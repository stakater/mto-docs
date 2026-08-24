# Uninstalling MTO

Removing MTO is a few decisions followed by one removal step. Make the decisions first: two of them cannot be undone once the operator is gone.

## Decide what to keep

Deleting a `Tenant` can delete what the tenant owns, so set the retention you want on each tenant **before** removing the operator that would act on it:

- `spec.namespaces.onDeletePurgeNamespaces` on the `Tenant` — whether the tenant's namespaces are deleted along with it. It defaults to `false`, so namespaces survive unless you asked otherwise. See [Delete a Tenant](../guides/delete-tenant.md).
- `argoCD.onDeletePurgeAppProject` on the tenant's `Extensions` resource — whether its ArgoCD `AppProject` is deleted with it. See [Extensions](../concepts/extensions.md#per-tenant-extensions-the-extensions-cr).

## Disable the console and cost components

If you enabled the console or showback, turn them off before uninstalling, while the operator that manages them is still running.

The `IntegrationConfig` manages the resources behind the console GUI — PostgreSQL, Prometheus, OpenCost, the MTO Console and Gateway, Dex and DexConfigOperator, and the FinOps Operator and Gateway — so this step is what hands them back before MTO goes.

Edit the `IntegrationConfig` — by default `tenant-operator-config` — and set:

```yaml
spec:
  components:
    console: false
    showback: false
```

See [Integration Config](../concepts/integration-config.md).

## Remove the IntegrationConfig

Delete the `IntegrationConfig` from the cluster. On OpenShift you can do this from `Search` → `IntegrationConfig` → `tenant-operator-config` → `Delete`.

## Remove the operator

Uninstall the way you installed:

| How you installed | How to remove |
|---|---|
| OpenShift, via OperatorHub or OLM | [Uninstall via OperatorHub UI](installation/openshift.md#uninstall-via-operatorhub-ui) |
| Kubernetes, AKS or EKS, via Helm | [Uninstall via Helm CLI](installation/kubernetes.md#uninstall-via-helm-cli) |

## Optionally remove the custom resource definitions

Uninstalling the operator leaves MTO's CRDs and the resources built from them on the cluster. Removing the CRDs deletes every `Tenant`, `Quota`, `IntegrationConfig` and `Extensions` resource with them, and that cannot be undone — so do it only when you are certain the tenant definitions are no longer wanted.

## Notes

- For how to use MTO, see the [Tenant tutorial](../guides/create-tenant.md).
- For extending MTO's manager ClusterRole, see [Extending Default Roles](../guides/extend-default-roles.md).
