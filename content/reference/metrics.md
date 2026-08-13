# Metrics

Multi Tenant Operator exposes Prometheus metrics through the [controller-runtime](https://book.kubebuilder.io/reference/metrics) framework: the standard controller and Go runtime metrics, plus a set of MTO-specific gauges under the `multi_tenant_operator` subsystem.

## Endpoint

The metrics server is disabled by default (`--metrics-bind-address=0`). Enabling it binds the endpoint at `/metrics`, and `--metrics-secure` decides how it is served:

- With `--metrics-secure=true`, the default, metrics are served over https. Requests are authenticated and authorized against the Kubernetes API, so a scraper must present a token belonging to a principal bound to the `metrics-reader` ClusterRole.
- With `--metrics-secure=false`, metrics are served over plain http with no authentication. Use this only where the endpoint is otherwise isolated.

Serving certificates come from `--metrics-cert-path`, `--metrics-cert-name`, and `--metrics-cert-key`. See [Configuration](configuration.md) for the full flag list and [RBAC](rbac.md) for the `metrics-reader` and `metrics-auth-role` definitions.

Each controller Deployment has its own metrics service, so a complete picture means scraping all of them rather than one.

## MTO metrics

All are gauges under the `multi_tenant_operator` subsystem.

| Metric | Labels | Description |
| --- | --- | --- |
| `multi_tenant_operator_resources_deployed_total` | `kind`, `name`, `namespace` | Total resources deployed by the operator for a given resource |
| `multi_tenant_operator_resources_deployed` | `kind`, `name`, `namespace`, `type` | Resources deployed, split by `type` (`manifest` or `resource_mappings`) |
| `multi_tenant_operator_reconcile_error` | `kind`, `name`, `namespace`, `state`, `errors` | Set when a resource is in error. `state` is the reconciliation stage, `CreateOrUpdate` or `Remove`, and `errors` carries the message |
| `multi_tenant_operator_reconcile_count` | `kind`, `name` | Reconcile count for a resource |
| `multi_tenant_operator_reconcile_seconds` | `kind`, `name` | Duration of the last reconcile, in seconds |

!!! note
    `reconcile_error` carries the error text in a label. Error messages vary, so each distinct message creates a new time series. Watch label cardinality if a resource is failing repeatedly with changing errors, and prefer alerting on the presence of the metric rather than aggregating across its `errors` label.

Because these are gauges rather than counters, `rate()` does not apply. `multi_tenant_operator_reconcile_seconds` reports the most recent duration, not a cumulative total.

## ServiceMonitor

A Prometheus Operator `ServiceMonitor` named `controller-manager-metrics-monitor` is provided:

- **scheme:** https, **port:** `https`, **path:** `/metrics`
- **auth:** bearer token from `/var/run/secrets/kubernetes.io/serviceaccount/token`
- **selector:** matches the `control-plane` label across the controller services, covering `controller-manager`, `controller-manager-tenant`, `controller-manager-webhook`, `controller-manager-quota-intconfig`, and `controller-manager-pilot`

!!! warning
    The shipped ServiceMonitor sets `insecureSkipVerify: true`, which disables certificate verification between Prometheus and the metrics endpoint. For production, replace it with `caFile`, `certFile`, and `keyFile` pointing at the metrics certificates.

## Useful queries

```promql
# Resources currently reporting a reconcile error, by kind
count by (kind) (multi_tenant_operator_reconcile_error > 0)

# Slowest reconciles
topk(10, multi_tenant_operator_reconcile_seconds)

# Total resources deployed for a tenant's namespace
sum by (namespace) (multi_tenant_operator_resources_deployed_total)
```

## Related pages

- [Configuration](configuration.md) for the metrics flags
- [RBAC](rbac.md) for the roles a scraper needs
- [Security Model](security-model.md) for how the endpoint is protected
