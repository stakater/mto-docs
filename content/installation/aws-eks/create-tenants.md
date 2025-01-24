# Create tenants on EKS Cluster using MTO

This document provides detailed insights on creating MTO Tenants on EKS cluster.

## Prerequisites

MTO must be installed on EKS cluster. [MTO EKS installation guide](./mto-installation.md) provides a detailed walk-through of MTO installation on EKS.

## Users Interaction with the Cluster

We will use two types of users to interact with the cluster, IAM users created via AWS Console and SSO Users.

### IAM Users

We have created a user named `test-benzema-mto` in AWS Console, with ARN `arn:aws:iam::<account>:user/test-benzema-mto`.
This user has a policy attached to be able to get cluster info

```json
{
    "Statement": [
        {
            "Action": "eks:DescribeCluster",
            "Effect": "Allow",
            "Resource": "*"
        }
    ],
    "Version": "2012-10-17"
}
```

We have mapped this user in `aws-auth` configmap in `kube-system` namespace.

```yaml
  mapUsers:
    - groups:
      - iam-devteam
      userarn: arn:aws:iam::<account>:user/test-benzema-mto
      username: test-benzema-mto
```

Using this [AWS guide](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html), we will ask the user to update its kubeconfig and try to access the cluster.

Since we haven't attached any RBAC with this user at the moment, trying to access anything in the cluster would throw an error

```terminal
$ kubectl get svc

Error from server (Forbidden): services is forbidden: User "test-benzema-mto" cannot list resource "services" in API group "" in the namespace "default"
```

### SSO Users

For SSO Users, we will map a role `arn:aws:iam::<account>:role/aws-reserved/sso.amazonaws.com/eu-north-1/AWSReservedSSO_PowerUserAccess_b0ad9936c75e5bcc`, that is attached by default with Users on SSO login to the AWS console and `awscli`, in `aws-auth` configmap in `kube-system` namespace.

```yaml
  mapRoles:
    - groups:
      - sso-devteam
      rolearn: arn:aws:iam::<account>:role/AWSReservedSSO_PowerUserAccess_b0ad9936c75e5bcc
      username: sso-devteam:{{SessionName}}
```

Since this user also doesn't have attached RBAC, trying to access anything in the cluster would throw an error

```terminal
$ kubectl get svc

Error from server (Forbidden): services is forbidden: User "sso-devteam:random-user-stakater.com" cannot list resource "services" in API group "" in the namespace "default"
```

### Setting up Tenant for Users

Now, we will set tenants for the above-mentioned users.

We will start by creating a `Quota CR` with some resource limits

```yaml
kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
  name: small
spec:
  limitrange:
    limits:
    - max:
        cpu: 800m
      min:
        cpu: 200m
      type: Container
  resourcequota:
    hard:
      configmaps: "10"
      memory: "8Gi"
EOF
```

Now, we will mention this `Quota` in two `Tenant` CRs

```yaml
kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-iam
spec:
  namespaces:
    withTenantPrefix:
    - dev
    - build
  accessControl:
    owners:
      groups:
      - iam-devteam
  quota: small
EOF
```

```yaml
kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-sso
spec:
  namespaces:
    withTenantPrefix:
    - dev
    - build
  accessControl:
    owners:
      groups:
    - sso-devteam
  quota: small
EOF
```

Notice that the only difference in both tenant specs are the groups.

### Accessing Tenant Namespaces

After the creation of `Tenant` CRs, now users can access namespaces in their respective tenants and preform create, update, delete functions.

Listing the namespaces by cluster admin will show us the recently created tenant namespaces

```bash
$ kubectl get namespaces

NAME                    STATUS   AGE
cert-manager            Active   8d
default                 Active   9d
kube-node-lease         Active   9d
kube-public             Active   9d
kube-system             Active   9d
multi-tenant-operator   Active   8d
random                  Active   8d
tenant-iam-build        Active   5s
tenant-iam-dev          Active   5s
tenant-sso-build        Active   5s
tenant-sso-dev          Active   5s
```

### IAM Users on Tenant Namespaces

We will now try to deploy a pod from user `test-benzema-mto` in its tenant namespace `tenant-iam-dev`

```bash
$ kubectl run nginx --image nginx -n tenant-iam-dev

pod/nginx created
```

And if we try the same operation in the other tenant with the same user, it will fail

```bash
$ kubectl run nginx --image nginx -n tenant-sso-dev

Error from server (Forbidden): pods is forbidden: User "test-benzema-mto" cannot create resource "pods" in API group "" in the namespace "tenant-sso-dev"
```

To be noted, `test-benzema-mto` can not list namespaces

```bash
$ kubectl get namespaces

Error from server (Forbidden): namespaces is forbidden: User "test-benzema-mto" cannot list resource "namespaces" in API group "" at the cluster scope
```

### SSO Users on Tenant Namespaces

We will repeat the above operations for our SSO user `sso-devteam:random-user-stakater.com` as well

```bash
$ kubectl run nginx --image nginx -n tenant-sso-dev

pod/nginx created
```

Trying to do operations outside the scope of its own tenant will result in errors

```bash
$ kubectl run nginx --image nginx -n tenant-iam-dev

Error from server (Forbidden): pods is forbidden: User "sso-devteam:random-user-stakater.com" cannot create resource "pods" in API group "" in the namespace "tenant-iam-dev"
```

To be noted, `sso-devteam:random-user-stakater.com` can not list namespaces

```bash
$ kubectl get namespaces

Error from server (Forbidden): namespaces is forbidden: User "sso-devteam:random-user-stakater.com" cannot list resource "namespaces" in API group "" at the cluster scope
```

## Using MTO Console

### Prerequisites

- Ensure that MTO Console is enabled by running the following command

  ```bash
  kubectl get integrationconfig tenant-operator-config -o=jsonpath='{.spec.components}' -n multi-tenant-operator
  ```

  Console should be set to true

  ```json
  {"console":true,"showback":true}
  ```

  If console is set to false then [enable the MTO Console](./mto-installation.md#enable-mto-console) before proceeding to next step

- **A Keycloak user with same username as AWS IAM user** should be created. Follow our [Setting Up User Access in Keycloak for MTO Console](../../how-to-guides/keycloak.md) guide to create a Keycloak user.

### MTO Console Login

Use the following command to get URL of MTO Console

```bash
kubectl get routes -n multi-tenant-operator
```

Output

```bash
NAME                             HOST/PORT              PATH     SERVICES                    PORT    TERMINATION     WILDCARD
tenant-operator-console-ncm2k    console.<SUBDOMAIN>      /      tenant-operator-console     http    edge/Redirect   None
tenant-operator-gateway-6kbxz    gateway.<SUBDOMAIN>      /      tenant-operator-gateway     http    edge/Redirect   None
tenant-operator-keycloak-mt6sl   keycloak.<SUBDOMAIN>     /      tenant-operator-keycloak    <all>   edge/Redirect   None
```

Open the URL and Login with the Keycloak user credentials.

![MTO Console Login Page](../../images/mto-console-login.png)

Dashboard will open after the successful login. Now you can navigate different tenants and namespaces using MTO Console

![MTO Console Dashboard](../../images/mto-console-dasboard.png)
