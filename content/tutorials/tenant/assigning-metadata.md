# Assigning metadata

## Assigning Common/Specific Metadata

### Distributing common labels and annotations to tenant namespaces via Tenant Custom Resource

Bill now wants to add labels/annotations to all the namespaces for a tenant. To create those labels/annotations Bill will just add them into `commonMetadata.labels`/`commonMetadata.annotations` field in the tenant CR.

```yaml
kubectl apply -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  editors:
    users:
    - john@aurora.org
    groups:
    - alpha
  quota: small
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod
  commonMetadata:
    labels:
      app.kubernetes.io/managed-by: tenant-operator
      app.kubernetes.io/part-of: tenant-alpha
    annotations:
      openshift.io/node-selector: node-role.kubernetes.io/infra=
EOF
```

With the above configuration all tenant namespaces will now contain the mentioned labels and annotations.

### Distributing specific labels and annotations to tenant namespaces via Tenant Custom Resource

Bill now wants to add labels/annotations to specific namespaces for a tenant. To create those labels/annotations Bill will just add them into `specificMetadata.labels`/`specificMetadata.annotations` and specific namespaces in `specificMetadata.namespaces` field in the tenant CR.

```yaml
kubectl apply -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  editors:
    users:
    - john@aurora.org
    groups:
    - alpha
  quota: small
  sandboxConfig:
    enabled: true
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod
  specificMetadata:
    - namespaces:
        - bluesky-anna-aurora-sandbox
      labels:
        app.kubernetes.io/is-sandbox: true
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
EOF
```

With the above configuration all tenant namespaces will now contain the mentioned labels and annotations.

## Assigning metadata to all sandboxes

Bill can choose to apply metadata to sandbox namespaces only by using `sandboxMetadata` property of Tenant CR like below:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  editors:
    users:
    - john@aurora.org
    groups:
    - alpha
  quota: small
  sandboxConfig:
    enabled: true
    private: true
  sandboxMetadata: # metadata for all sandbox namespaces
    labels:
      app.kubernetes.io/part-of: che.eclipse.org
    annotations:
      che.eclipse.org/username: "{{ TENANT.USERNAME }}" # templated placeholder
```

We are using a templated annotation here. See more on supported templated values for labels and annotations for specific MTO CRs [here](../../reference-guides/templated-metadata-values.md)
