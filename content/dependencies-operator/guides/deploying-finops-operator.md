# Deploying FinOps Operator

The FinOps Operator is the MTO-specific cost management platform. It provides cost allocation, chargeback, and showback capabilities integrated with the Multi-Tenant Operator ecosystem.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- A running OpenCost or Prometheus instance is recommended for cost data collection.

## Minimal Example

The following CR deploys the FinOps Operator with default settings:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: FinOpsOperator
metadata:
  name: finops-operator
spec:
  controllerManager:
    replicas: 1
    manager:
      resources:
        limits:
          cpu: 500m
          memory: 128Mi
  finops-gateway:
    replicas: 1
    service:
      type: ClusterIP
```

## Common Customizations

**Overriding the container images:**

```yaml
spec:
  controllerManager:
    manager:
      image:
        repository: my-registry.example.com/finops-operator
        tag: v0.1.14
  finops-gateway:
    container:
      image:
        repository: my-registry.example.com/finops-gateway
        tag: v0.1.14
```

**Scaling the gateway:**

```yaml
spec:
  finops-gateway:
    replicas: 2
    service:
      type: ClusterIP
```

**Setting a custom cluster domain:**

```yaml
spec:
  kubernetesClusterDomain: custom.cluster.local
```

## Verification

Confirm the FinOps Operator is running:

```bash
kubectl get pods -l app.kubernetes.io/name=finops-operator
```

## Further Reading

This is a Stakater internal chart. For questions about configuration options, contact Stakater support or refer to your organization's internal documentation.
