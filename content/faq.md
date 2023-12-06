# FAQs

## Namespace Admission Webhook

### Q. Error received while performing Create, Update or Delete action on Namespace

```terminal
Cannot CREATE namespace test-john without label stakater.com/tenant
```

**Answer.** Error occurs when a user is trying to perform create, update, delete action on a namespace without the required `stakater.com/tenant` label. This label is used by the operator to see that authorized users can perform that action on the namespace. Just add the label with the tenant name so that MTO knows which tenant the namespace belongs to, and who is authorized to perform create/update/delete operations. For more details please refer to [Namespace use-case](./tutorials/tenant/creating-namespaces.md).

### Q. Error received while performing Create, Update or Delete action on OpenShift Project

```terminal
Cannot CREATE namespace testing without label stakater.com/tenant. User: system:serviceaccount:openshift-apiserver:openshift-apiserver-sa
```

**Answer.** This error occurs because we don't allow Tenant members to do operations on OpenShift Project, whenever an operation is done on a project, `openshift-apiserver-sa` tries to do the same request onto a namespace. That's why the user sees `openshift-apiserver-sa` Service Account instead of its own user in the error message.

The fix is to try the same operation on the namespace manifest instead.

### Q. Error received while doing "kubectl apply -f namespace.yaml"

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

**Answer.** Multi-Tenant Operator's ArgoCD Integration allows configuration of which cluster-scoped resources can be deployed, both globally and on a per-tenant basis. For a global allow-list that applies to all tenants, you can add both resource `group` and  `kind` to the [IntegrationConfig's](./how-to-guides/integration-config.md#argocd) `spec.argocd.clusterResourceWhitelist` field. Alternatively, you can set this up on a tenant level by configuring the same details within a [Tenant's](./how-to-guides/tenant.md) `spec.argocd.appProject.clusterResourceWhitelist` field. For more details, check out the [ArgoCD integration use cases](./tutorials/argocd/enabling-multi-tenancy-argocd.md#allow-argocd-to-sync-certain-cluster-wide-resources)

## Q. InvalidSpecError: application repo \<repo\> is not permitted in project \<project\>

**A.** The above error can occur if the ArgoCD Application is syncing from a source that is not allowed the referenced AppProject. To solve this, verify that you have referred to the correct project in the given ArgoCD Application, and that the repoURL used for the Application's source is valid. If the error still appears, you can add the URL to the relevant Tenant's `spec.argocd.sourceRepos` array.

## Q. Why are there `mto-showback-*` pods failing in my cluster?

**A.** The `mto-showback-*` pods are used to calculate the cost of the resources used by each tenant. These pods are created by the Multi-Tenant Operator and are scheduled to run every 10 minutes. If the pods are failing, it is likely that the operator's necessary to calculate cost are not present in the cluster. To solve this, you can navigate to `Operators` -> `Installed Operators` in the OpenShift console and check if the MTO-OpenCost and MTO-Prometheus operators are installed. If they are in a pending state, you can manually approve them to install them in the cluster.
