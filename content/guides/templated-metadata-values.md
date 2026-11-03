# Templated metadata values

Some labels and annotations that MTO applies to managed namespaces need a value that differs per user or per tenant. Instead of a fixed string, you write a **templated value** — a placeholder that MTO replaces with real data when it reconciles the resource.

This page lists the templated values MTO supports today.

## Supported templated values

### `{{ TENANT.USERNAME }}`

Resolves to the username of the tenant member a namespace belongs to — one of the users listed under `owners` or `editors` in the [`Tenant`](../concepts/tenant.md). Use it where a per-user namespace needs a label or annotation carrying that user's name, as [DevWorkspace](../extensions/devworkspace.md) sandboxes do.

Set it in either of two places, depending on how widely it should apply. The key name differs between the two, and both are correct:

| Resource | Field | Applies to |
|:---|:---|:---|
| [`Tenant`](../concepts/tenant.md) | `spec.namespaces.metadata.sandbox.labels` / `.annotations` — singular `sandbox` | that tenant's sandboxes |
| [`IntegrationConfig`](../concepts/integration-config.md) | `spec.metadata.sandboxes.labels` / `.annotations` — plural `sandboxes` | every tenant's sandboxes, cluster-wide |

Example:

```yaml
annotations:
  che.eclipse.org/username: "{{ TENANT.USERNAME }}"   # the double quotes are required
```

The double quotes are not optional: unquoted, the leading `{{` is read as the start of a YAML flow mapping, so the value fails to parse.
