# CR Reference

All Custom Resources belong to the API group `dependencies.tenantoperator.stakater.com/v1alpha1`. Each CR's `.spec` maps directly to the values of its underlying Helm chart.

## Dex

**Kind:** `Dex` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

OpenID Connect identity provider.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `replicaCount` | integer | `1` | Number of Dex replicas |
| `config.issuer` | string | — | The issuer URL for OIDC discovery |
| `config.storage` | object | — | Backend storage configuration (e.g. `kubernetes`, `sqlite3`) |
| `config.connectors` | list | `[]` | Upstream identity provider connectors |
| `config.staticClients` | list | `[]` | Pre-registered OAuth2 clients |
| `ingress.enabled` | boolean | `false` | Enable ingress for Dex |
| `service.type` | string | `ClusterIP` | Kubernetes service type |

For the full list of supported values, see the [Dex Helm chart documentation](https://github.com/dexidp/helm-charts).

## Postgres

**Kind:** `Postgres` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

Production-ready PostgreSQL database (Bitnami chart).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `architecture` | string | `standalone` | `standalone` or `replication` |
| `auth.username` | string | — | Database username |
| `auth.password` | string | — | Database password (use `auth.existingSecret` instead in production) |
| `auth.existingSecret` | string | — | Name of a Secret containing credentials |
| `auth.database` | string | — | Default database name |
| `primary.persistence.size` | string | `8Gi` | PVC size for primary storage |
| `primary.resources` | object | — | CPU/memory resource requests and limits |

For the full list of supported values, see the [Bitnami PostgreSQL chart documentation](https://github.com/bitnami/charts/tree/main/bitnami/postgresql).

## Prometheus

**Kind:** `Prometheus` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

Metrics collection, storage, and alerting.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `server.retention` | string | `15d` | How long to retain metrics data |
| `server.persistentVolume.size` | string | `8Gi` | PVC size for Prometheus server |
| `server.resources` | object | — | CPU/memory resource requests and limits |
| `alertmanager.enabled` | boolean | `true` | Enable Alertmanager |
| `prometheus-node-exporter.enabled` | boolean | `true` | Enable Node Exporter |
| `kube-state-metrics.enabled` | boolean | `true` | Enable bundled Kube State Metrics |

For the full list of supported values, see the [Prometheus community chart documentation](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus).

## KubeStateMetrics

**Kind:** `KubeStateMetrics` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

Exports Kubernetes object metrics for Prometheus.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `replicas` | integer | `1` | Number of replicas |
| `collectors` | list | 24 default collectors | List of Kubernetes object types to collect metrics for |
| `prometheus.monitor.enabled` | boolean | `false` | Create a Prometheus ServiceMonitor |
| `resources` | object | — | CPU/memory resource requests and limits |

For the full list of supported values, see the [Kube State Metrics chart documentation](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-state-metrics).

## OpenCost

**Kind:** `OpenCost` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

Kubernetes cost monitoring and FinOps visibility.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `opencost.exporter.defaultClusterId` | string | — | Cluster identifier for cost allocation |
| `opencost.exporter.replicas` | integer | `1` | Number of exporter replicas |
| `opencost.prometheus.internal.enabled` | boolean | — | Use an in-cluster Prometheus instance |
| `opencost.prometheus.external.url` | string | — | URL of an external Prometheus instance |
| `opencost.ui.enabled` | boolean | `true` | Enable the OpenCost web UI |
| `opencost.ui.uiPort` | integer | `9090` | Port for the UI service |
| `opencost.customPricing` | object | — | Custom pricing configuration for on-prem or unsupported clouds |

!!! note
    OpenCost requires a running Prometheus instance. Configure either `opencost.prometheus.internal` or `opencost.prometheus.external` to point to your Prometheus server.

For the full list of supported values, see the [OpenCost Helm chart documentation](https://github.com/opencost/opencost-helm-chart).

## DexConfigOperator

**Kind:** `DexConfigOperator` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

Dynamically manages Dex connectors and OAuth client configurations.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `controllerManager.replicas` | integer | `1` | Number of controller replicas |
| `controllerManager.manager.image.repository` | string | — | Container image repository |
| `controllerManager.manager.image.tag` | string | — | Container image tag |
| `controllerManager.manager.resources.limits.cpu` | string | `500m` | CPU limit |
| `controllerManager.manager.resources.limits.memory` | string | `128Mi` | Memory limit |
| `kubernetesClusterDomain` | string | `cluster.local` | Kubernetes cluster domain |

!!! note
    DexConfigOperator works in conjunction with Dex. Ensure a Dex instance is running before deploying this component.

This is a Stakater internal chart — no public upstream documentation is available.

## FinOpsOperator

**Kind:** `FinOpsOperator` | **API Version:** `dependencies.tenantoperator.stakater.com/v1alpha1`

MTO-specific cost management platform.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `controllerManager.replicas` | integer | `1` | Number of controller replicas |
| `controllerManager.manager.image.repository` | string | — | Container image repository |
| `controllerManager.manager.image.tag` | string | — | Container image tag |
| `controllerManager.manager.resources` | object | — | CPU/memory resource requests and limits |
| `finops-gateway.container.image.repository` | string | — | Gateway container image |
| `finops-gateway.replicas` | integer | `1` | Number of gateway replicas |
| `finops-gateway.service.type` | string | `ClusterIP` | Gateway service type |
| `kubernetesClusterDomain` | string | `cluster.local` | Kubernetes cluster domain |

This is a Stakater internal chart — no public upstream documentation is available.

## Common Patterns

All CRs pass their `.spec` values directly to the underlying Helm chart. This means all CRs support standard Helm values including:

- `resources` — CPU and memory requests/limits
- `nodeSelector` — Schedule pods on specific nodes
- `tolerations` — Tolerate specific node taints
- `affinity` — Advanced pod scheduling rules
- `podAnnotations` — Custom annotations on pods

These fields follow the standard Kubernetes conventions and can be set under `.spec` for any CR.
