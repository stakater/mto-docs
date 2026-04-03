# Deploying Kube State Metrics

Kube State Metrics generates metrics about the state of Kubernetes objects (deployments, pods, nodes, etc.) and exposes them for Prometheus to scrape.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- A running Prometheus instance to scrape the exported metrics.

## Minimal Example

The following CR deploys Kube State Metrics with default collectors:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: KubeStateMetrics
metadata:
  name: kube-state-metrics
spec:
  replicas: 1
```

## Common Customizations

**Enabling a Prometheus ServiceMonitor:**

```yaml
spec:
  prometheus:
    monitor:
      enabled: true
```

**Limiting collectors to specific resource types:**

```yaml
spec:
  collectors:
    - pods
    - deployments
    - nodes
    - namespaces
    - statefulsets
```

**Setting resource limits:**

```yaml
spec:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 250m
      memory: 256Mi
```

## Verification

Confirm Kube State Metrics is running:

```bash
kubectl get pods -l app.kubernetes.io/name=kube-state-metrics
```

## Further Reading

- [Kube State Metrics chart documentation](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-state-metrics)
