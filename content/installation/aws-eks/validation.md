# MTO Validation Guide

This document provides detailed insights on creating MTO Tenants on EKS cluster. In this tutorial we will setup 2 tenants named logistics and retail for an imaginary ecommerce company.

## Create & Configure IAM Users

### 1. Create a User

Create a user with username `falcon@nordmart.com`

```sh
$ aws iam create-user --user-name falcon@nordmart.com

Output:
{
    "User": {
        "Path": "/",
        "UserName": "falcon@nordmart.com",
        "UserId": "AIDAZFWZTAEJ7ILHDKLLD",
        "Arn": "arn:aws:iam::630742778131:user/falcon@nordmart.com",
        "CreateDate": "2025-02-03T13:09:51Z"
    }
}
```

We have created an IAM user named `falcon@nordmart.com`, with ARN `arn:aws:iam::630742778131:user/falcon@nordmart.com`.

### 2. Attach cluster access policy

Create a AWS JSON policy file. This policy will allow the user to access the cluster.

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

Attach a policy to user by running the following command

```bash
aws iam put-user-policy --user-name falcon@nordmart.com --policy-document file://policy.json --policy-name ClusterAccess
```

### 3. Generating Access Keys

Executing the following command will provide the Access Key Id and Access Secret Key Id that can be used to log in later

```bash
aws iam create-access-key --user-name "falcon@nordmart.com"
```

### 4. Grant IAM users access to Kubernetes with a `ConfigMap`

Use the following command to map this user in `aws-auth` configmap in `kube-system` namespace.

```bash
eksctl create iamidentitymapping --cluster "<CLUSTER_NAME>" \
                                 --region "<AWS_REGION>" \
                                 --arn "<USER_ARN>" \
                                 --username "falcon@nordmart.com" \
                                 --no-duplicate-arns
```

Repeat the same steps to create another user `bear@nordmart.com` for retail tenant.

## Setting up Tenants

Now, we will create tenants for above created users.

### 1. Create a Quota

We will start by creating a `Quota CR` with some resource limits

```sh
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

### 2. Create Tenants

Now, we will create 2 tenants `logistics` and `retail` with one user each

```sh
kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: logistics
spec:
  namespaces:
    withTenantPrefix:
    - dev
    - build
  accessControl:
    owners:
      users:
      - falcon@nordmart.com
  quota: small
EOF
```

```sh
kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: retail
spec:
  namespaces:
    withTenantPrefix:
    - dev
    - build
  accessControl:
    owners:
      users:
      - bear@nordmart.com
  quota: small
EOF
```

Notice that the only difference in both tenant specs are the users.

After the creation of `Tenant` CRs, now users can access namespaces in their respective tenants and preform create, update, delete functions.

Listing the namespaces by cluster admin will show us the recently created tenant namespaces

```sh
$ kubectl get namespaces

NAME                    STATUS   AGE
cert-manager            Active   8d
default                 Active   9d
kube-node-lease         Active   9d
kube-public             Active   9d
kube-system             Active   9d
multi-tenant-operator   Active   8d
random                  Active   8d
logistics-dev           Active   5s
logistics-build         Active   5s
retail-dev              Active   5s
retail-build            Active   5s
```

## Switching to different User in EKS Cluster

Set the following environment variables from the access keys generated in [previous steps](#3-generating-access-keys)

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional)

Execute the following command to update the kube context

```sh
aws configure set region $AWS_REGION
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY

aws eks update-kubeconfig --name <EKS_CLUSTER_NAME> --region $AWS_REGION
```

## Validation

### Logistics User on Tenant Namespaces

We will now try to deploy a pod from user `falcon@nordmart.com` in its tenant namespace `logistics-dev`

```bash
$ kubectl run nginx --image nginx -n logistics-dev

pod/nginx created
```

And if we try the same operation in the other tenant with the same user, it will fail

```bash
$ kubectl run nginx --image nginx -n retail-dev

Error from server (Forbidden): pods is forbidden: User "falcon@nordmart.com" cannot create resource "pods" in API group "" in the namespace "retail-dev"
```

To be noted, `falcon@nordmart.com` can not list namespaces

```bash
$ kubectl get namespaces

Error from server (Forbidden): namespaces is forbidden: User "falcon@nordmart.com" cannot list resource "namespaces" in API group "" at the cluster scope
```

### Retail User on Tenant Namespaces

We will repeat the above operations for our SSO user `bear@nordmart.com` as well

```bash
$ kubectl run nginx --image nginx -n retail-dev

pod/nginx created
```

Trying to do operations outside the scope of its own tenant will result in errors

```bash
$ kubectl run nginx --image nginx -n retail-dev

Error from server (Forbidden): pods is forbidden: User "bear@nordmart.com" cannot create resource "pods" in API group "" in the namespace "retail-dev"
```

To be noted, `bear@nordmart.com` can not list namespaces

```bash
$ kubectl get namespaces

Error from server (Forbidden): namespaces is forbidden: User "bear@nordmart.com" cannot list resource "namespaces" in API group "" at the cluster scope
```

## Using MTO Console

### Prerequisites

- Ensure that MTO Console is enabled by running the following command

  ```bash
  $ kubectl get integrationconfig tenant-operator-config -o=jsonpath='{.spec.components}' -n multi-tenant-operator

  {"console":true,"showback":true}
  ```

  If console is set to false then [enable the MTO Console](./installation.md#enable-mto-console) before proceeding to next step

- **A Keycloak user with same username as AWS IAM user** should be created. Follow our [Setting Up User Access in Keycloak for MTO Console](../../console/configuration.md#setting-up-user-access-in-keycloak-for-mto-console) guide to create a Keycloak user.

### MTO Console Log In

List the ingresses to access the URL of MTO Console

```bash
kubectl get ingress -n multi-tenant-operator

NAME                       CLASS   HOSTS                                  ADDRESS                                                                          PORTS     AGE
tenant-operator-console    nginx   console.iinhdnh6.demo.kubeapp.cloud    ae51c179026a94c90952fc50d5d91b52-a4446376b6415dcb.elb.eu-north-1.amazonaws.com   80, 443   23m
tenant-operator-gateway    nginx   gateway.iinhdnh6.demo.kubeapp.cloud    ae51c179026a94c90952fc50d5d91b52-a4446376b6415dcb.elb.eu-north-1.amazonaws.com   80, 443   23m
tenant-operator-keycloak   nginx   keycloak.iinhdnh6.demo.kubeapp.cloud   ae51c179026a94c90952fc50d5d91b52-a4446376b6415dcb.elb.eu-north-1.amazonaws.com   80, 443   24m

```

Open the URL and Log In with the Keycloak user credentials.

![MTO Console Login Page](../../images/mto-console-login.png)

Dashboard will open after the successful login. Now you can navigate different tenants and namespaces using MTO Console

![MTO Console Dashboard](../../images/mto-console-dasboard.png)
