# FAQs

## Q. Error received while performing Create, Update or Delete action on namespace `"Cannot CREATE namespace test-john without label stakater.com/tenant"`

**A.** Error occurs when a user is trying to perform create, update, delete action on a namespace without the required `stakater.com/tenant` label. This label is used by the operator to see that authorized users can perform that action on the namespace. Just add the label with the tenant name so that MTO knows which tenant the namespace belongs to, and who is authorized to perform create/update/delete operations. For more details please refer to [Namespace use-case](./usecases/namespace.md).

## Q. How do I deploy cluster-scoped resource via the ArgoCD integration?

**A.** Multi-Tenant Operator's ArgoCD Integration allows configuration of which cluster-scoped resources can be deployed, both globally and on a per tenant basis. For a global whitelist that applies to all tenants, you can add both resource `group` and  `kind` to the [IntegrationConfig's](./integration-config.md#argocd) `spec.argocd.clusterResourceWhitelist` field. Alternatively, you can set this up on a tenant level by configuring the same details within a [Tenant's](./customresources.md#2-tenant) `spec.argocd.appProject.clusterResourceWhitelist` field. For more details, check out the [ArgoCD integration use cases](./usecases/argocd.md#allow-argocd-to-sync-certain-cluster-wide-resources)
