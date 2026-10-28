# Choosing which tenants get a resource

By default, every managed data source and dashboard goes to every tenant. `spec.scaffolding.mode` decides whether annotations are consulted:

| Mode | Behaviour |
|:---|:---|
| `OnAnnotation` (default) | Annotations on the resource select tenants. |
| `Always` | Annotations are ignored; everything syncs to every tenant. |

Under `OnAnnotation`:

| Annotation on the resource | Effect |
|:---|:---|
| `mto.grafana/tenant: "bluesky,arsenal"` | Sync only to the listed tenants. Comma- or space-separated, case-insensitive. |
| `mto.grafana/disabled: "true"` | Skip this resource entirely. |
| *(neither)* | Sync to every tenant. |

```yaml
apiVersion: grafana.integreatly.org/v1beta1
kind: GrafanaDashboard
metadata:
  name: loki-dashboard
  namespace: telemetry
  annotations:
    mto.grafana/tenant: "bluesky,arsenal"
```

Three details worth knowing:

- `disabled` is checked **before** `tenant`, so a resource carrying both is skipped whatever it lists.
- An **empty** `mto.grafana/tenant` value matches no tenants at all — a quiet way to disable a resource by accident. Use `mto.grafana/disabled` when that is what you mean.
- Both keys can be renamed through `spec.scaffolding.annotations`: its `tenant` entry overrides the tenant key, and its `enable` entry overrides the disabled key.

!!! warning
    The `Never` and `OnLabel` modes are accepted by the schema but are not implemented, and currently behave like `Always` — everything syncs to every tenant. Do not set `Never` expecting it to stop syncing; disable individual resources with `mto.grafana/disabled` instead.

---

**Previous:** [Tenant access and roles](tenant-access-and-roles.md) · **Next:** [Operating](operating.md)
