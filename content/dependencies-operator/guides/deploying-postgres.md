# Deploying PostgreSQL

PostgreSQL is deployed using the Bitnami PostgreSQL Helm chart, providing a production-ready database for MTO ecosystem components such as Dex or custom tenant workloads.

## Prerequisites

- The MTO Dependencies Operator is running in your cluster (bundled with MTO).
- Create a Kubernetes Secret containing database credentials before applying the CR if you want to use `auth.existingSecret`.

## Minimal Example

The following CR deploys a standalone PostgreSQL instance:

```yaml
apiVersion: dependencies.tenantoperator.stakater.com/v1alpha1
kind: Postgres
metadata:
  name: postgres
spec:
  architecture: standalone
  auth:
    username: mtoadmin
    password: changeme
    database: mto
  primary:
    persistence:
      size: 8Gi
```

!!! note
    For production deployments, use `auth.existingSecret` instead of inline credentials. Create a Secret with keys `postgres-password` and `password` before applying the CR.

## Common Customizations

**Using an existing Secret for credentials:**

```yaml
spec:
  auth:
    existingSecret: postgres-credentials
    database: mto
```

**Enabling replication with read replicas:**

```yaml
spec:
  architecture: replication
  readReplicas:
    replicaCount: 2
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
```

**Increasing storage and setting resource limits:**

```yaml
spec:
  primary:
    persistence:
      size: 50Gi
    resources:
      requests:
        cpu: 500m
        memory: 512Mi
      limits:
        cpu: "1"
        memory: 1Gi
```

## Verification

Confirm PostgreSQL is running:

```bash
kubectl get pods -l app.kubernetes.io/name=postgresql
```

## Further Reading

- [Bitnami PostgreSQL chart documentation](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)
