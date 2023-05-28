# Deleting a Tenant

## Retaining tenant namespaces and AppProject when a tenant is being deleted

Bill now wants to delete tenant `bluesky` and wants to retain all namespaces and AppProject of the tenant. To retain the namespaces Bill will set `spec.onDelete.cleanNamespaces`, and `spec.onDelete.cleanAppProjects` to `false`.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  quota: small
  sandboxConfig:
    enabled: true
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod
  onDelete:
    cleanNamespaces: false
    cleanAppProject: false
```

With the above configuration all tenant namespaces and AppProject will not be deleted when tenant `bluesky` is deleted. By default, the value of `spec.onDelete.cleanNamespaces` is also `false` and `spec.onDelete.cleanAppProject` is `true`
