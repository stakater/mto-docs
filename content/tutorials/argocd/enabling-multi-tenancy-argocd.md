# Enabling Multi-Tenancy in ArgoCD

## ArgoCD integration in Multi Tenant Operator

With Multi Tenant Operator (MTO), cluster admins can configure multi tenancy in their cluster. Now with ArgoCD integration, multi tenancy can be configured in ArgoCD applications and AppProjects.

MTO (if configured to) will create AppProjects for each tenant. The AppProject will allow tenants to create ArgoCD Applications that can be synced to namespaces owned by those tenants. Cluster admins will also be able to blacklist certain namespaces resources if they want, and allow certain cluster scoped resources as well (see the `NamespaceResourceBlacklist` and `ClusterResourceWhitelist` sections in [Integration Config docs](./integration-config.md) and [Tenant Custom Resource docs](./customresources.md)).

Note that ArgoCD integration in MTO is completely optional.

## Default ArgoCD configuration

We have set a default ArgoCD configuration in Multi Tenant Operator that fulfils the following use cases:

- Tenants are able to see only their ArgoCD applications in the ArgoCD frontend
- Tenant 'Owners' and 'Editors' will have full access to their ArgoCD applications
- Tenants in the 'Viewers' group will have read-only access to their ArgoCD applications
- Tenants can sync all namespace-scoped resources, except those that are blacklisted in the spec
- Tenants can only sync cluster-scoped resources that are whitelisted in the spec
- Tenant 'Owners' can configure their own GitOps source repos at a tenant level
- Cluster admins can prevent specific resources from syncing via ArgoCD
- Cluster admins have full access to all ArgoCD applications and AppProjects
- Since ArgoCD integration is on a per-tenant level, namespace-scoped applications are only synced to Tenant's namespaces

Detailed use cases showing how to create AppProjects are mentioned in [use cases for ArgoCD](./usecases/argocd.md).
