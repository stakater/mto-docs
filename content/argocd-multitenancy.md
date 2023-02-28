# ArgoCD Multi-tenancy

ArgoCD is a declarative GitOps tool built to deploy applications to Kubernetes. While the continuous delivery (CD) space is seen by some as crowded these days, ArgoCD does bring some interesting capabilities to the table. Unlike other tools, ArgoCD is lightweight and easy to configure.

## Why ArgoCD?

Application definitions, configurations, and environments should be declarative and version controlled. Application deployment and lifecycle management should be automated, auditable, and easy to understand.

## ArgoCD integration in Multi Tenant Operator

With Multi Tenant Operator (MTO), cluster admins can configure multi tenancy in their cluster. Now with ArgoCD integration, multi tenancy can be configured in ArgoCD applications and AppProjects.

MTO (if configured to) will create AppProjects for each tenant. The AppProject will allow tenants to create ArgoCD Applications that can be synced to namespaces owned by those tenants. Cluster admins will also be able to blacklist certain namespaces resources if they want, and allow certain cluster scoped resources as well (see the `NamespaceResourceBlacklist` and `ClusterResourceWhitelist` sections in [Integration Config docs](./integration-config.md) and [Tenant Custom Resource docs](./customresources.md)).

Note that ArgoCD integration in MTO is completely optional.

## Default ArgoCD configuration

We have set a default ArgoCD configuration in Multi Tenant Operator that fulfils the following use cases:

- Tenants are able to see only their ArgoCD applications in the ArgoCD frontend
- Tenant 'Owners' and 'Editors' will have full access to their ArgoCD applications
- Tenants in the 'Viewers' group will have read-only access to their ArgoCD applications
- Tenants can only sync whitelisted cluster-scoped and namespaced resources via their applications
- Tenant 'Owners' can configure their own GitOps source repos at a tenant level
- Cluster admins can prevent specific resources from syncing via ArgoCD
- Cluster admins have full access to all ArgoCD applications and AppProjects

Detailed use cases showing how to create AppProjects are mentioned in [use cases for ArgoCD](./usecases/argocd.md).
