# Configuration

Multi Tenant Operator is configured in two places. Cluster-wide tenancy behavior, such as default tenant roles and integrations, lives in the [IntegrationConfig](../concepts/integration-config.md) custom resource. How the operator itself runs, which controllers start, on which platform, and how its endpoints are exposed, is configured through the environment variables and flags on this page.

## Deployment layout

MTO does not run as a single process. Each controller ships as its own Deployment running the same operator image, with an environment variable selecting which controller that pod starts. A controller can therefore be scaled or restarted without disturbing the others.

| Deployment | Enabled by | Responsibility |
| --- | --- | --- |
| `tenant-controller` | `TENANT_CONTROLLER` | Reconciles `Tenant` resources and registers the dynamic admission webhooks |
| `namespace-controller` | `NAMESPACE_CONTROLLER` | Reconciles namespaces into their owning tenants |
| `quota-intconfig-controller` | `QUOTA_INTEGRATIONCONFIG_CONTROLLER` | Reconciles `Quota` and `IntegrationConfig` |
| `pilot-controller` | `PILOT_CONTROLLER` | Provisions the Console, Gateway, and their dependencies |
| `db-controller` | `DATABASE_CONTROLLER` | Manages the database backing the Console |
| `extensions-argocd-controller` | `EXTENSIONS_ARGOCD_CONTROLLER` | Reconciles the ArgoCD `Extension` integration |
| `webhook` | `ENABLE_WEBHOOKS`, `ENABLE_ADMISSION_WEBHOOKS` | Serves the validating admission webhooks |

Set a variable to `"true"` to start that controller. `ENABLE_ALL_CONTROLLERS` starts everything in one process and `ENABLE_ALL_CORE_CONTROLLERS` starts the core set, both of which suit local development rather than production.

## Environment variables

### Platform and identity

| Variable | Values | Description |
| --- | --- | --- |
| `PLATFORM_TYPE` | `OpenShift`, `Kubernetes` | Required. The operator refuses to start on any other value, since this decides whether OpenShift-only resources such as `Route` and `ClusterResourceQuota` are reconciled. |
| `OPERATOR_NAMESPACE` | namespace name | Namespace the operator runs in. |
| `OPERATOR_NAME_PREFIX` | string | Prefix applied to resources the operator generates. |
| `SERVICE_ACCOUNT_NAME` | string | ServiceAccount the webhook runs as. |
| `LEADER_ELECTION_ID` | string | Lease name used when `--leader-elect` is set. Each controller Deployment uses a distinct value so they do not contend for one lease. |

### Admission behavior

| Variable | Values | Description |
| --- | --- | --- |
| `ENABLE_WEBHOOKS` | `"true"` | Starts the webhook server. |
| `ENABLE_ADMISSION_WEBHOOKS` | `"true"` | Registers the admission webhook handlers. |
| `BYPASSED_GROUPS` | comma-separated group names | Groups whose members skip tenant admission checks entirely. |
| `DEBUG_WEBHOOKS` | `"true"` | Verbose webhook logging. Development only. |
| `EXPERIMENTAL_NAMESPACE_WEBHOOK_V2` | `"true"` | Opts into the rewritten namespace webhook. Off by default. |

!!! warning
    `BYPASSED_GROUPS` is an authorization bypass, not a logging or convenience setting. Any user in a listed group can create and modify tenant-owned resources with none of the tenant checks applying. Keep it to genuine cluster administrator groups, and see [Security Model](security-model.md).

### Console and dependencies

The `pilot-controller` reads the images it should deploy from its own environment, which is how a disconnected or mirrored registry is configured:

`MTO_CONSOLE_IMAGE`, `MTO_GATEWAY_IMAGE`, `MTO_POSTGRESQL_IMAGE`, `MTO_SHOWBACK_IMAGE`, `OPENCOST_IMAGE`, `PROMETHEUS_IMAGE`, and `KUBE_STATE_METRICS_IMAGE`.

`ENABLE_CONSOLE` turns the Console on, and `TENANT_API` enables the Tenants API that backs the [kubectl plugin](../cli/overview.md). `DB_OPERATION_TIMEOUT` bounds database calls, and `LOCAL_ENV` switches to local development defaults.

## Command-line flags

| Flag | Default | Description |
| --- | --- | --- |
| `--metrics-bind-address` | `0` | Metrics listen address. `0` disables the endpoint. See [Metrics](metrics.md). |
| `--metrics-secure` | `true` | Serve metrics over https with authentication. |
| `--metrics-cert-path` | none | Directory holding the metrics serving certificate. |
| `--metrics-cert-name` | `tls.crt` | Certificate filename within that directory. |
| `--metrics-cert-key` | `tls.key` | Key filename within that directory. |
| `--health-probe-bind-address` | `:8081` | Probe address, serving `/healthz` and `/readyz`. |
| `--leader-elect` | `false` | Enable leader election. Set on the shipped Deployments. |
| `--tenant-api-port` | `8080` | Port the Tenants API binds to. |
| `--webhook-cert-path` | none | Directory holding the webhook serving certificate. |
| `--webhook-cert-name` | `tls.crt` | Certificate filename within that directory. |
| `--webhook-cert-key` | `tls.key` | Key filename within that directory. |

## Helm values

The chart exposes each controller as its own block, so replicas, resources, pod security context, and image can be set per controller: `tenantController`, `namespaceController`, `quotaIntconfigController`, `pilotController`, `dbController`, `extensionsArgocdController`, and `webhook`.

```yaml
tenantController:
  replicas: 1
  manager:
    resources:
      limits:
        cpu: 500m
        memory: 512Mi

webhook:
  replicas: 2
```

Service types and ports are configured through `tenantMetricsService`, `webhookService`, `quotaIntconfigWebhookService`, `pilotMetricsService`, and `api`. `imagePullSecrets` and `kubernetesClusterDomain` apply chart-wide.

## Related pages

- [IntegrationConfig](../concepts/integration-config.md) for cluster-wide tenancy settings
- [RBAC](rbac.md) for the permissions each component holds
- [Webhooks](webhooks.md) for what admission enforces
