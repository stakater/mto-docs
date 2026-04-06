# Deploying OpenCost

OpenCost provides real-time Kubernetes cost monitoring and FinOps visibility, helping teams understand and optimize their cloud spending.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- A running Prometheus instance is required. OpenCost queries Prometheus for resource usage data.

## Minimal Example

The following CR deploys OpenCost with the UI enabled, pointing to an in-cluster Prometheus:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: OpenCost
metadata:
  name: opencost
spec:
  opencost:
    exporter:
      defaultClusterId: my-cluster
    prometheus:
      internal:
        enabled: true
        serviceName: prometheus-server
        namespaceName: default
    ui:
      enabled: true
```

## Common Customizations

**Using an external Prometheus instance:**

```yaml
spec:
  opencost:
    prometheus:
      external:
        enabled: true
        url: https://prometheus.monitoring.svc:9090
```

**Configuring custom pricing for on-prem clusters:**

```yaml
spec:
  opencost:
    customPricing:
      enabled: true
      costModel:
        CPU: "0.03"
        RAM: "0.004"
        storage: "0.0005"
```

**Scaling the exporter:**

```yaml
spec:
  opencost:
    exporter:
      replicas: 2
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 500m
          memory: 256Mi
```

## Verification

Confirm OpenCost is running:

```bash
kubectl get pods -l app.kubernetes.io/name=opencost
```

## Further Reading

- [OpenCost Helm chart documentation](https://github.com/opencost/opencost-helm-chart)
- [OpenCost official documentation](https://www.opencost.io/docs/)
