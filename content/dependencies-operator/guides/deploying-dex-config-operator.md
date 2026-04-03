# Deploying Dex Config Operator

The Dex Config Operator dynamically manages Dex connectors and OAuth client configurations. It automates the lifecycle of identity provider integrations that would otherwise require manual Dex configuration updates.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- A running Dex instance in the cluster. Deploy Dex first using the [Deploying Dex](deploying-dex.md) guide.

## Minimal Example

The following CR deploys the Dex Config Operator with default settings:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: DexConfigOperator
metadata:
  name: dex-config-operator
spec:
  controllerManager:
    replicas: 1
    manager:
      resources:
        limits:
          cpu: 500m
          memory: 128Mi
```

## Common Customizations

**Setting a custom cluster domain:**

```yaml
spec:
  kubernetesClusterDomain: custom.cluster.local
```

**Overriding the container image:**

```yaml
spec:
  controllerManager:
    manager:
      image:
        repository: my-registry.example.com/dex-config-operator
        tag: v1.2.0
```

**Adjusting resource allocations:**

```yaml
spec:
  controllerManager:
    manager:
      resources:
        requests:
          cpu: 100m
          memory: 64Mi
        limits:
          cpu: "1"
          memory: 256Mi
```

## Verification

Confirm the Dex Config Operator is running:

```bash
kubectl get pods -l app.kubernetes.io/name=dex-config-operator
```

## Further Reading

This is a Stakater internal chart. For questions about configuration options, contact Stakater support or refer to your organization's internal documentation.
