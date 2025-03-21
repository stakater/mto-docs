# Changing the default access level for tenant owners

This feature allows the cluster admins to change the default roles assigned to Tenant owner, editor, viewer groups.

For example, if Bill as the cluster admin wants to reduce the privileges that tenant owners have, so they cannot create or edit Roles or bind them. As an admin of an OpenShift cluster, Bill can do this by assigning the `edit` role to all tenant owners. This is easily achieved by modifying the [IntegrationConfig](../../integration-config.md):

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  accessControl:
    rbac:
      tenantRoles:
        default:
          owner:
            clusterRoles:
              - edit
          editor:
            clusterRoles:
              - edit
          viewer:
            clusterRoles:
              - view
```

Once all namespaces reconcile, the old `admin` RoleBindings should get replaced with the `edit` ones for each tenant owner.

## Giving specific permissions to some tenants

Bill now wants the owners of the tenants `bluesky` and `alpha` to have `admin` permissions over their namespaces. Custom roles feature will allow Bill to do this, by modifying the IntegrationConfig like this:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  accessControl:
    rbac:
      tenantRoles:
        default:
          owner:
            clusterRoles:
              - edit
          editor:
            clusterRoles:
              - edit
          viewer:
            clusterRoles:
              - view
        custom:
        - labelSelector:
            matchExpressions:
            - key: stakater.com/tenant
              operator: In
              values:
                - alpha
          owner:
            clusterRoles:
              - admin
        - labelSelector:
            matchExpressions:
            - key: stakater.com/tenant
              operator: In
              values:
                - bluesky
          owner:
            clusterRoles:
              - admin
```

New Bindings will be created for the Tenant owners of `bluesky` and `alpha`, corresponding to the `admin` Role. Bindings for editors and viewer will be inherited from the `default roles`. All other Tenant owners will have an `edit` Role bound to them within their namespaces
