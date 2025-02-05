# Multi Tenant Operator in Microsoft Azure Kubernetes Service

This document covers how to link Multi Tenant Operator with an [AKS (Azure Kubernetes Service)](https://azure.microsoft.com/en-us/products/kubernetes-service/) cluster.

## Prerequisites

- Make sure Azure CLI version 2.0.61 or later is installed and configured. If you need to install or upgrade, see [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli). To find the version, run:
`az --version`
- You need kubectl as well, with a minimum version of 1.18.3. If you need to install, see [Install kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl).
- To install MTO, you need Helm CLI as well. Visit [Installing Helm](https://helm.sh/docs/intro/install/) to get Helm CLI
- You need to have a user in [Azure Portal](https://portal.azure.com/signin/index/), which we will use as the administrator for creating clusters, users and groups with enough permissions for the respective tasks

## Create an Admin Group

Start by creating an admin group which will later be used as the administrator of our AKS cluster. Log in to [Azure Portal](https://portal.azure.com/signin/index/) from CLI:

```terminal
az login
```

```terminal
$ az ad signed-in-user show

{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
  "businessPhones": [],
  "displayName": "test-admin-user",
  "givenName": null,
  "id": "<user-id>",
  "jobTitle": null,
  "mail": null,
  "mobilePhone": null,
  "officeLocation": null,
  "preferredLanguage": null,
  "surname": null,
  "userPrincipalName": "<upn>"
}
```

The user-id will be used later to add our user in the admin group for MTO.

Create a group called `mto-admins`:

```terminal
az ad group create --display-name mto-admins --mail-nickname mto-admins
```

Using the above user-id, link user to the newly created group:

```terminal
az ad group member add --group mto-admins --member-id <user-id>
```

Use this command to get admin-group-id, this will later be used while provisioning the cluster:

```terminal
$ az ad group show --group mto-admins

{
  **********
  "description": null,
  "displayName": "mto-admins",
  "expirationDateTime": null,
  "groupTypes": [],
  "id": "<admin-group-id>",
  "isAssignableToRole": null,
  **********
}
```

## Create an AKS Cluster

Create a Resource Group by using the `az group create` command in your preferred Azure location:

```terminal
az group create --name myResourceGroup --location westus2
```

Create a small cluster:

```terminal
az aks create --resource-group myResourceGroup --name myAKSCluster --node-count 1 --vm-set-type VirtualMachineScaleSets --enable-cluster-autoscaler --min-count 1 --max-count 3 --enable-aad --aad-admin-group-object-ids <admin-group-id>
```

### Create test groups in `Entra ID`

First, store the ID of your AKS cluster in a variable named AKS_ID:

```terminal
AKS_ID=$(az aks show --resource-group myResourceGroup --name myAKSCluster --query id -o tsv)
```

Create your first test group named `appdev` using group command and assign its ID to `APPDEV_ID` variable:

```terminal
APPDEV_ID=$(az ad group create --display-name appdev --mail-nickname appdev --query id -o tsv)
```

Allow the `appdev` group to interact with the AKS cluster using kubectl by assigning them the Azure Kubernetes Service Cluster User Role:

```terminal
az role assignment create --assignee $APPDEV_ID --role "Azure Kubernetes Service Cluster User Role" --scope $AKS_ID
```

Create your second test group named `opssre` using the command and assign its ID to the `OPSSRE_ID` variable:

```terminal
OPSSRE_ID=$(az ad group create --display-name opssre --mail-nickname opssre --query id -o tsv)
```

Allow the `opssre` group to interact with the AKS cluster using kubectl by assigning them the Azure Kubernetes Service Cluster User Role:

```terminal
az role assignment create --assignee $OPSSRE_ID --role "Azure Kubernetes Service Cluster User Role" --scope $AKS_ID
```

### Create test users in `Entra ID`

Set User Principal Name (UPN) and password for your users. The UPN must include the verified domain name of your tenant, for example `user@company.com`.

Following command reads the UPN for the `appdev` group and stores it in the `AAD_DEV_UPN` variable:

```terminal
echo "Please enter the UPN for application developers: " && read AAD_DEV_UPN
```

For this scope of this blog, we will assume that the entered UPN was `aksdev@company.com`.

Following command reads the password for your user and stores it in the `AAD_DEV_PW` variable:

```terminal
echo "Please enter the secure password for application developers: " && read AAD_DEV_PW
```

Create the user `AKS Dev` using the previously created variables:

```terminal
AKSDEV_ID=$(az ad user create --display-name "AKS Dev" --user-principal-name $AAD_DEV_UPN --password $AAD_DEV_PW --query id -o tsv)
```

Add this user to the `appdev` group that was previously created:

```terminal
az ad group member add --group appdev --member-id $AKSDEV_ID
```

Repeat the steps for `OPS SRE` user.

The following command reads the UPN for your user and stores it in the `AAD_SRE_UPN` variable:

```terminal
echo "Please enter the UPN for SREs: " && read AAD_SRE_UPN
```

For this scope of this blog, we will assume that the entered UPN was `opssre@company.com`.

The following command reads the password for your user and stores it in the `AAD_SRE_PW` variable:

```terminal
echo "Please enter the secure password for SREs: " && read AAD_SRE_PW
```

Create the user `AKS SRE` using above variables

```terminal
AKSSRE_ID=$(az ad user create --display-name "AKS SRE" --user-principal-name $AAD_SRE_UPN --password $AAD_SRE_PW --query id -o tsv)
```

Add this user to the `opssre` group that was previously created:

```terminal
az ad group member add --group opssre --member-id $AKSSRE_ID
```

## Installing Cert Manager and MTO

In this section, we will install Multi Tenant Operator (MTO) for tenancy between different users and groups. MTO has several webhooks which need certificates. For automated handling of certs, we will install Cert Manager as a prerequisite.

Start by logging in to Azure from CLI by running the following command:

```terminal
kubectl get pods
```

Executing the command will take you to a browser window where you can log in from your test-admin-user.

Running `kubectl auth whoami` will show you the user info:

```terminal
$ kubectl auth whoami

ATTRIBUTE    VALUE
Username     test-admin-user
Groups       [<mto-admins-id> system:authenticated]
Extra: oid   [<oid>]
```

You will notice that the `mto-admins` group ID is attached with our test-admin-user user. This user will be used for all the cluster admin level operations.

### Install Cert Manager

Install Cert Manager in the cluster for automated handling of operator webhook certs:

```terminal
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.yaml
```

Let's wait for the pods to be up:

```terminal
$ kubectl get pods -n cert-manager --watch

NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-7fb948f468-wgcbx              1/1     Running   0          7m18s
cert-manager-cainjector-75c5fc965c-wxtkp   1/1     Running   0          7m18s
cert-manager-webhook-757c9d4bb7-wd9g8      1/1     Running   0          7m18s
```

### Install MTO using Helm

Helm will be used to install MTO as it is the only available way of installing it on Kubernetes Clusters.

Use helm install command to install MTO helm chart. Here, `bypassedGroups` has to be set as `system:masters` as it is used by `masterclient` of AKS and `<mto-admins-id>`as it is used by test-admin-user:

```terminal
helm install tenant-operator oci://ghcr.io/stakater/public/charts/multi-tenant-operator --version 0.12.62 --namespace multi-tenant-operator --create-namespace --set bypassedGroups='system:masters\,<mto-admins-id>'
```

Wait for the pods to come to a running state:

```terminal
$ kubectl get pods -n multi-tenant-operator --watch

NAME                                                              READY   STATUS    RESTARTS   AGE
tenant-operator-namespace-controller-768f9459c4-758kb             2/2     Running   0          2m
tenant-operator-pilot-controller-7c96f6589c-d979f                 2/2     Running   0          2m
tenant-operator-resourcesupervisor-controller-566f59d57b-xbkws    2/2     Running   0          2m
tenant-operator-template-quota-intconfig-controller-7fc99462dz6   2/2     Running   0          2m
tenant-operator-templategroupinstance-controller-75cf68c872pljv   2/2     Running   0          2m
tenant-operator-templateinstance-controller-d996b6fd-cx2dz        2/2     Running   0          2m
tenant-operator-tenant-controller-57fb885c84-7ps92                2/2     Running   0          2m
tenant-operator-webhook-5f8f675549-jv9n8                          2/2     Running   0          2m
```

### Setting up Tenant for Users

Start by getting IDs for `opssre` and `appdev` groups by running `az ad group show` command:

```terminal
$ az ad group show --group appdev

{
  ***********
  "displayName": "opssre",
  "expirationDateTime": null,
  "groupTypes": [],
  "id": "<opssre-group-id>",
  "isAssignableToRole": null,
  ************
}
```

```terminal
$ az ad group show --group appdev

{
  ***********
  "displayName": "appdev",
  "expirationDateTime": null,
  "groupTypes": [],
  "id": "<appdev-group-id>",
  "isAssignableToRole": null,
  ************
}
```

Create a `Quota CR` with some resource limits:

```terminal
$ kubectl apply -f - <<EOF
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
EOF
```

Now, mention this `Quota` in two `Tenant` CRs, with `opssre` and `appdev` group IDs in the groups section of spec:

```terminal
$ kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-a
spec:
  namespaces:
    withTenantPrefix:
    - dev
    - build
  accessControl:
    owners:
      groups:
    - <opssre-group-id>
  quota: small
EOF
```

```terminal
$ kubectl apply -f - <<EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-b
spec:
  namespaces:
    withTenantPrefix:
    - dev
    - build
  accessControl:
    owners:
      groups:
    - <appdev-group-id>
  quota: small
EOF
```

Notice that the only difference in both tenant specs are the groups.

Check if the tenant namespaces have been created:

```terminal
$ kubectl get namespaces

NAME                    STATUS   AGE
cert-manager            Active   4h26m
default                 Active   5h25m
kube-node-lease         Active   5h25m
kube-public             Active   5h25m
kube-system             Active   5h25m
multi-tenant-operator   Active   3h55m
tenant-a-build          Active   10m
tenant-a-dev            Active   10m
tenant-b-build          Active   10m
tenant-b-dev            Active   10m
```

Notice that MTO has created two namespaces under each tenant.

## Users Interaction with the Cluster

### AppDev group

AppDev is one of the previously created groups, its scope is limited to Tenant A namespaces as we mentioned its group ID in Tenant A. Start by clearing token of test-admin-user:

```terminal
kubelogin remove-tokens
```

Use the `aksdev` user from `appdev` group to log in to the cluster:

```terminal
kubectl get pods
```

This will take you to device login page. After entering the correct code, it will redirect you to Microsoft Login page, here you will enter the email and password of `aksdev` user created at the start of the article.

After successful log in, it will show you the output of your kubectl command:

```terminal
Error from server (Forbidden): pods is forbidden: User "aksdev@company.com" cannot list resource "pods" in API group "" in the namespace "default"
```  

This user does not have access to default namespace.

Now try accessing the resources in its tenant namespaces which are under Tenant A:

```terminal
$ kubectl get pods -n tenant-a-dev

No resources found in tenant-a-dev namespace.
```

Create an `nginx` pod in the same namespace

```terminal
$ kubectl run nginx --image=nginx -n tenant-a-dev

pod/nginx created
```

Now try the same operation in other namespace of Tenant B:

```terminal
$ kubectl run nginx --image=nginx -n tenant-b-dev

Error from server (Forbidden): pods is forbidden: User "aksdev@company.com" cannot create resource "pods" in API group "" in the namespace "tenant-b-dev"
```

This operation fails with an error showing strict controls in their Tenants.

### OpsSre group

OpsSre is the second group created at the start of this article, its scope is limited to Tenant B namespaces as we mentioned its group ID in Tenant B.

Start by clearing token of `appdev` user:

```terminal
kubelogin remove-tokens
```

Use the `opssre` user from `opssre` group to log in to the cluster:

```terminal
kubectl get pods
```

This will take you to device login page. After entering the correct code, it will redirect you to Microsoft Login page, here you will enter the email and password of `opssre` user created at the start of the article.

After successful log in, it will show you the output of your kubectl command:

```terminal
Error from server (Forbidden): pods is forbidden: User "opssre@company.com" cannot list resource "pods" in API group "" in the namespace "default"
```

This user does not have access to default namespace

Now try accessing the resources in its tenant namespaces which are under Tenant B:

```terminal
$ kubectl get pods -n tenant-b-dev

No resources found in tenant-b-dev namespace.
```

Create an `nginx` pod in the same namespace:

```terminal
$ kubectl run nginx --image=nginx -n tenant-b-dev

pod/nginx created
```

Now try the same operation in other namespace of Tenant A:

```terminal
$ kubectl run nginx --image=nginx -n tenant-a-dev

Error from server (Forbidden): pods is forbidden: User "opssre@company.com" cannot create resource "pods" in API group "" in the namespace "tenant-a-dev"
```

This operation fails with an error showing strict controls in their Tenants.

## Cleanup Resources

Cleanup the users, groups, AKS Cluster and Resource Group created for this blog.
Run the following set of commands to remove resources created in above sections:

```terminal
# Delete the Azure AD user accounts for aksdev and akssre.

$ az ad user delete --id $AKSDEV_ID
$ az ad user delete --id $AKSSRE_ID

# Delete the Azure AD groups for `appdev`,`opssre` and `mto-admins`. This also deletes the Azure role assignments.

$ az ad group delete --group appdev
$ az ad group delete --group opssre
$ az ad group delete --group mto-admins

# Delete the Resource Group which will also delete the underlying AKS test cluster and related resources

$ az group delete --name myResourceGroup
```
