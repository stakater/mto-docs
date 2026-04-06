# Deploying Prometheus

Prometheus provides metrics collection, storage, and alerting for your Kubernetes cluster. It is deployed using the Prometheus community Helm chart.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- If you plan to use persistent storage, ensure a default StorageClass is available or specify one explicitly.

## Minimal Example

The following CR deploys Prometheus with default settings:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: Prometheus
metadata:
  name: prometheus
spec:
  server:
    retention: 15d
    persistentVolume:
      size: 8Gi
```

## Common Customizations

**Disabling sub-components you don't need:**

```yaml
spec:
  alertmanager:
    enabled: false
  prometheus-node-exporter:
    enabled: false
  kube-state-metrics:
    enabled: false
```

**Increasing retention and storage:**

```yaml
spec:
  server:
    retention: 30d
    persistentVolume:
      size: 50Gi
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: "1"
        memory: 2Gi
```

**Adding custom scrape configurations:**

```yaml
spec:
  serverFiles:
    prometheus.yml:
      scrape_configs:
        - job_name: my-app
          static_configs:
            - targets:
                - my-app.default.svc:8080
```

## Verification

Confirm Prometheus is running:

```bash
kubectl get pods -l app.kubernetes.io/name=prometheus
```

## Further Reading

- [Prometheus community chart documentation](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus)
