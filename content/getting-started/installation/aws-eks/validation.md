# MTO Validation Guide

In this guide, we will set up **two tenants**—**Logistics** and **Retail**—for an imaginary e-commerce company, each with one user.

- **Falcon** will be the user assigned to the **Logistics** tenant.  
- **Bear** will be the user assigned to the **Retail** tenant.

## 1. Create & Configure AWS IAM Users & Groups

### 1.1. Create a user

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

### 1.2. Attach cluster access policy to user

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

### 1.3. Generate access key for the user

Executing the following command will provide the Access Key Id and Access Secret Key Id that can be used to log in later

```bash
aws iam create-access-key --user-name "falcon@nordmart.com"
```

### 1.4. Grant user access to Kubernetes via ConfigMap

Use the following command to map this user in `aws-auth` ConfigMap in `kube-system` namespace.

```bash
eksctl create iamidentitymapping --cluster "<CLUSTER_NAME>" \
                                 --region "<AWS_REGION>" \
                                 --arn "<USER_ARN>" \
                                 --username "falcon@nordmart.com" \
                                 --no-duplicate-arns
```

Repeat the same steps to create another user `bear@nordmart.com` for retail tenant.

## 2. Create MTO Quota

As cluster admin create a `Quota CR` with some resource limits:

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

## 3. Create MTO Tenants

As cluster admin create 2 tenants `logistics` and `retail` with one user each:

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

## 4. List namespaces as cluster admin

Listing the namespaces as cluster admin will show following namespaces:

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

## 5. Validate Falcon permissions

### 5.1. Switch to falcon

Set the following environment variables from the access keys generated in [previous steps](#13-generate-access-key-for-the-user)

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

### 5.2. Check CLI permissions

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

### 5.3. Validate Console permissions

Navigate to MTO Console URL and Log In with the user credentials.

![MTO Console Login Page](../../images/mto-console-login.png)

Dashboard will open after the successful login. Now you can navigate different tenants and namespaces using MTO Console

![MTO Console Dashboard](../../images/mto-console-bear-dashboard.png)

## 6. Validate Bear permissions

### 6.1. Switch to bear

Set the following environment variables from the access keys generated in [previous steps](#13-generate-access-key-for-the-user)

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

### 6.2. Check CLI permissions

We will repeat the above operations for our retail user `bear@nordmart.com` as well

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

### 6.3. Validate Console permissions

Navigate to MTO Console URL and Log In with the user credentials.

![MTO Console Login Page](../../images/mto-console-login.png)

Dashboard will open after the successful login. Now you can navigate different tenants and namespaces using MTO Console

![MTO Console Dashboard](../../images/mto-console-bear-dashboard.png)
