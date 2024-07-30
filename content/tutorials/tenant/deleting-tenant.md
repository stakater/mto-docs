# Deleting a Tenant While Preserving Resources

When managing tenant lifecycles within Kubernetes, certain scenarios require the deletion of a tenant without removing associated namespaces or ArgoCD AppProjects. This ensures that resources and configurations tied to the tenant remain intact for archival or transition purposes.

## Configuration for Retaining Resources

Bill decides to decommission the bluesky tenant but needs to preserve all related namespaces for continuity. To achieve this, he adjusts the Tenant Custom Resource (CR) to prevent the automatic cleanup of these resources upon tenant deletion.

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
  namespaces:
    sandboxes:
      enabled: true
    withTenantPrefix:
      - dev
      - build
      - prod
    onDeletePurgeNamespaces: false
EOF
```

With the `onDeletePurgeNamespaces` fields set to false, Bill ensures that the deletion of the bluesky tenant does not trigger the removal of its namespaces. This setup is crucial for cases where the retention of environment setups and deployments is necessary post-tenant deletion.

### Default Behavior

It's important to note the default behavior of the Tenant Operator regarding resource cleanup:

Namespaces: By default, `onDeletePurgeNamespaces` is set to false, implying that namespaces are not automatically deleted with the tenant unless explicitly configured.

## Deleting the Tenant

Once the Tenant CR is configured as desired, Bill can proceed to delete the bluesky tenant:

```bash
kubectl delete tenant bluesky
```

This command removes the tenant resource from the cluster while leaving the specified namespaces untouched, adhering to the configured `onDeletePurgeNamespaces` policies. This approach provides flexibility in managing the lifecycle of tenant resources, catering to various operational strategies and compliance requirements.
