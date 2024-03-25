# Creating Namespaces through Tenant Custom Resource

Bill, tasked with structuring namespaces for different environments within a tenant, utilizes the Tenant Custom Resource (CR) to streamline this process efficiently. Here's how Bill can orchestrate the creation of `dev`, `build`, and `production` environments for the tenant members directly through the Tenant CR.


### Strategy for Namespace Creation

To facilitate the environment setup, Bill decides to categorize the namespaces based on their association with the tenant's name. He opts to use the `namespaces.withTenantPrefix` field for namespaces that should carry the tenant name as a prefix, enhancing clarity and organization. For namespaces that do not require a tenant name prefix, Bill employs the `namespaces.withoutTenantPrefix` field.

Here's how Bill configures the Tenant CR to create these namespaces:

```yaml
kubectl apply -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
        - anthony@aurora.org
    editors:
      users:
        - john@aurora.org
      groups:
        - alpha
  namespaces:
    withTenantPrefix:
      - dev
      - build
    withoutTenantPrefix:
      - prod
EOF
```

This configuration ensures the creation of the desired namespaces, directly correlating them with the bluesky tenant.

Upon applying the above configuration, Bill and the tenant members observe the creation of the following namespaces:

```bash
kubectl get namespaces
NAME             STATUS   AGE
bluesky-dev      Active   5m
bluesky-build    Active   5m
prod             Active   5m
```

Anna, as a tenant owner, gains the capability to further customize or create new namespaces within her tenant's scope. For example, creating a bluesky-production namespace with the necessary tenant label:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bluesky-production
  labels:
    stakater.com/tenant: bluesky
```

> ⚠️ It's crucial for Anna to include the tenant label `tenantoperator.stakater.com/tenant: bluesky` to ensure the namespace is recognized as part of the bluesky tenant. Failure to do so, or if Anna is not associated with the bluesky tenant, will result in Multi Tenant Operator (MTO) denying the namespace creation.

Following the creation, the MTO dynamically assigns roles to Anna and other tenant members according to their designated user types, ensuring proper access control and operational capabilities within these namespaces.

### Incorporating Existing Namespaces into the Tenant via ArgoCD

For teams practicing GitOps, existing namespaces can be seamlessly integrated into the [Tenant](../../how-to-guides/tenant.md) structure by appending the tenant label to the namespace's manifest within the GitOps repository. This approach allows for efficient, automated management of namespace affiliations and access controls, ensuring a cohesive tenant ecosystem.

#### Add Existing Namespaces to Tenant via GitOps

Using GitOps as your preferred development workflow, you can add existing namespaces for your tenants by including the tenant label.

To add an existing namespace to your tenant via GitOps:

1. Migrate the namespace resource to the GitOps-monitored repository
1. Amend the namespace manifest to include the tenant label: tenantoperator.stakater.com/tenant: <TENANT_NAME>.
1. Synchronize the GitOps repository with the cluster to propagate the changes
1. Validate that the tenant users now have appropriate access to the integrated namespace



### Removing Namespaces via GitOps

To disassociate or remove namespaces from the cluster through GitOps, the namespace configuration should be eliminated from the GitOps repository. Additionally, detaching the namespace from any ArgoCD-managed applications by removing the `app.kubernetes.io/instance` label ensures a clean removal without residual dependencies.

Synchronizing the repository post-removal finalizes the deletion process, effectively managing the lifecycle of namespaces within a tenant-operated Kubernetes environment.
