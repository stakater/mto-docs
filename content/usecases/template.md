# Creating Templates

Anna wants to create a Template that she can use to initialize or share common resources across namespaces (e.g. PullSecrets).

Anna can either create a template using `Custom Resource Manifests`

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: docker-pull-secret
resources:
  manifests:
    - kind: Secret
      apiVersion: v1
      metadata:
        name: docker-pull-secret
      data:
        .dockercfg: eyAKICAiaHR0cHM6IC8vaW5kZXguZG9ja2VyLmlvL3YxLyI6IHsgImF1dGgiOiAiYzNSaGEyRjBaWEk2VjI5M1YyaGhkRUZIY21WaGRGQmhjM04zYjNKayJ9Cn0K
      type: kubernetes.io/dockercfg
```

Or by using `Helm Charts`

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: redis
resources:
  helm:
    releaseName: redis
    chart:
      repository:
        name: redis
        repoUrl: https://charts.bitnami.com/bitnami
    values: |
      redisPort: 6379
```

Or by using `Resource Mapping`

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: resource-mapping
resources:
  resourceMappings:
    secrets:
      - name: docker-secret
        namespace: bluesky-build
    configMaps:
      - name: tronador-configMap
        namespace: stakater-tronador
```

**Note:** Resource mapping can be used via TGI to map resources within tenant namespaces or to some other tenant's namespace. If used with TI, the resources will only be mapped if namespaces belong to same tenant.

## Using Templates with Default Parameters

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: namespace-parameterized-restrictions
parameters:
  # Name of the parameter
  - name: DEFAULT_CPU_LIMIT
    # The default value of the parameter
    value: "1"
  - name: DEFAULT_CPU_REQUESTS
    value: "0.5"
    # If a parameter is required the template instance will need to set it
    # required: true
    # Make sure only values are entered for this parameter
    validation: "^[0-9]*\\.?[0-9]+$"
resources:
  manifests:
    - apiVersion: v1
      kind: LimitRange
      metadata:
        name: namespace-limit-range-${namespace}
      spec:
        limits:
          - default:
              cpu: "${{DEFAULT_CPU_LIMIT}}"
            defaultRequest:
              cpu: "${{DEFAULT_CPU_REQUESTS}}"
            type: Container
```

Parameters can be used with both `manifests` and `helm charts`

## What’s next

See how Anna can deploy a [template in a namespace](./deploying-templates.md)
