# Troubleshooting Guide

## OperatorHub Upgrade Error

### Operator is stuck in upgrade if upgrade approval is set to Automatic

#### Problem

If operator upgrade is set to Automatic Approval on OperatorHub, there may be scenarios where it gets blocked.

#### Resolution

!!! information
        If upgrade approval is set to manual, and you want to skip upgrade of a specific version, then delete the InstallPlan created for that specific version. Operator Lifecycle Manager (OLM) will create the latest available InstallPlan which can be approved then.

As OLM does not allow to upgrade or downgrade from a version stuck because of error, the only possible fix is to uninstall the operator from the cluster.
When the operator is uninstalled it removes all of its resources i.e., ClusterRoles, ClusterRoleBindings, and Deployments etc., except Custom Resource Definitions (CRDs), so none of the Custom Resources (CRs), Tenants, Templates etc., will be removed from the cluster.
If any CRD has a conversion webhook defined then that webhook should be removed before installing the stable version of the operator. This can be achieved via removing the `.spec.conversion` block from the CRD schema.

As an example, if you have installed v0.8.0 of Multi Tenant Operator on your cluster, then it'll stuck in an error `error validating existing CRs against new CRD's schema for "integrationconfigs.tenantoperator.stakater.com": error validating custom resource against new schema for IntegrationConfig multi-tenant-operator/tenant-operator-config: [].spec.tenantRoles: Required value`. To resolve this issue, you'll first uninstall the MTO from the cluster. Once you uninstall the MTO, check Tenant CRD which will have a conversion block, which needs to be removed. After removing the conversion block from the Tenant CRD, install the latest available version of MTO from OperatorHub.

## Permission Issues

### Vault user permissions are not updated if the user is added to a Tenant, and the user does not exist in RHSSO

#### Problem

If a user is added to tenant resource, and the user does not exist in RHSSO, then RHSSO is not updated with the user's Vault permission.

#### Reproduction steps

1. Add a new user to Tenant CR
1. Attempt to log in to Vault with the added user
1. Vault denies that the user exists, and signs the user up via RHSSO. User is now created on RHSSO (you may check for the user on RHSSO).

#### Resolution

If the user does not exist in RHSSO, then MTO does not create the tenant access for Vault in RHSSO.

The user now needs to go to Vault, and sign up using OIDC. Then the user needs to wait for MTO to reconcile the updated tenant (reconciliation period is currently 1 hour). After reconciliation, MTO will add relevant access for the user in RHSSO.

If the user needs to be added immediately and it is not feasible to wait for next MTO reconciliation, then: add a label or annotation to the user, or restart the Tenant controller pod to force immediate reconciliation.

## Pod Creation Error

### Q. Errors in ReplicaSet Events about pods not being able to schedule on OpenShift because SCC annotation is not found

```terminal
unable to find annotation openshift.io/sa.scc.uid-range
```

**Answer.** OpenShift recently updated its process of handling SCC, and it's now managed by annotations like `openshift.io/sa.scc.uid-range` on the namespaces. Absence  of them wont let pods schedule. The fix for the above error is to make sure ServiceAccount `system:serviceaccount:openshift-infra.` regex is always mentioned in `Privileged.serviceAccounts` section of `IntegrationConfig`. This regex will allow operations from all `ServiceAccounts` present in `openshift-infra` namespace. More info at [Privileged Service Accounts](./kubernetes-resources/integration-config.md#privileged)

## Namespace Admission Webhook

### Q. Error received while performing Create, Update or Delete action on Namespace

```terminal
Cannot CREATE namespace test-john without label stakater.com/tenant
```

**Answer.** Error occurs when a user is trying to perform create, update, delete action on a namespace without the required `stakater.com/tenant` label. This label is used by the operator to see that authorized users can perform that action on the namespace. Just add the label with the tenant name so that MTO knows which tenant the namespace belongs to, and who is authorized to perform create/update/delete operations. For more details please refer to [Namespace use-case](./kubernetes-resources/tenant/how-to-guides/create-namespaces.md).

### Q. Error received while performing Create, Update or Delete action on OpenShift Project

```terminal
Cannot CREATE namespace testing without label stakater.com/tenant. User: system:serviceaccount:openshift-apiserver:openshift-apiserver-sa
```

**Answer.** This error occurs because we don't allow Tenant members to do operations on OpenShift Project, whenever an operation is done on a project, `openshift-apiserver-sa` tries to do the same request onto a namespace. That's why the user sees `openshift-apiserver-sa` Service Account instead of its own user in the error message.

The fix is to try the same operation on the namespace manifest instead.

### Q. Error received while doing `kubectl apply -f namespace.yaml`

```terminal
Error from server (Forbidden): error when retrieving current configuration of:
Resource: "/v1, Resource=namespaces", GroupVersionKind: "/v1, Kind=Namespace"
Name: "ns1", Namespace: ""
from server for: "namespace.yaml": namespaces "ns1" is forbidden: User "muneeb" cannot get resource "namespaces" in API group "" in the namespace "ns1"
```

**Answer.** Tenant members will not be able to use `kubectl apply` because `apply` first gets all the instances of that resource, in this case namespaces, and then does the required operation on the selected resource. To maintain tenancy, tenant members do not the access to get or list all the namespaces.

The fix is to create namespaces with `kubectl create` instead.

## MTO - ArgoCD Integration

### Q. How do I deploy cluster-scoped resource via the ArgoCD integration?

**Answer.** Multi-Tenant Operator's ArgoCD Integration allows configuration of which cluster-scoped resources can be deployed, both globally and on a per-tenant basis. For a global allow-list that applies to all tenants, you can add both resource `group` and  `kind` to the [IntegrationConfig's](./kubernetes-resources/integration-config.md#argocd) `spec.integrations.argocd.clusterResourceWhitelist` field. Alternatively, you can set this up on a tenant level by configuring the same details within a [Tenant's](./kubernetes-resources/tenant/tenant-overview.md) `spec.integrations.argocd.appProject.clusterResourceWhitelist` field. For more details, check out the [ArgoCD integration use cases](./integrations/argocd.md#allowing-argocd-to-sync-certain-cluster-wide-resources)

### Q. InvalidSpecError: application repo \<repo\> is not permitted in project \<project\>

**Answer.** The above error can occur if the ArgoCD Application is syncing from a source that is not allowed the referenced AppProject. To solve this, verify that you have referred to the correct project in the given ArgoCD Application, and that the repoURL used for the Application's source is valid. If the error still appears, you can add the URL to the relevant Tenant's `spec.integrations.argocd.sourceRepos` array.

## MTO - OpenCost

### Q. Why are there `mto-showback-*` pods failing in my cluster?

**Answer.** The `mto-showback-*` pods are used to calculate the cost of the resources used by each tenant. These pods are created by the Multi-Tenant Operator and are scheduled to run every 10 minutes. If the pods are failing, it is likely that the operator's necessary to calculate cost are not present in the cluster. To solve this, you can navigate to `Operators` -> `Installed Operators` in the OpenShift console and check if the MTO-OpenCost and MTO-Prometheus operators are installed. If they are in a pending state, you can manually approve them to install them in the cluster.
