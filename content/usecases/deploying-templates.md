# Distributing Resources in Namespaces

Multi Tenant Operator has three Custom Resources which can cover this usecase using the `Template` CR, depending upon the conditions and preference.

1. TemplateGroupInstance
2. TemplateInstance
3. Tenant

Stakater Team, however, encourages the use of `TemplateGroupInstance` to distribute resources in multiple namespaces as it is optimized for better performance.

## Deploying Template to Namespaces via TemplateGroupInstances

Bill, the cluster admin, wants to deploy a docker pull secret in namespaces where certain labels exists.

First, Bill creates a template:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: docker-secret
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

Once the template has been created, Bill makes a `TemplateGroupInstance` referring to the `Template` he wants to deploy with `MatchLabels`:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: docker-secret-group-instance
spec:
  template: docker-pull-secret
  selector:
    matchLabels:
      kind: build
  sync: true
```

Afterwards, Bill can see that secrets have been successfully created in all label matching namespaces.

```bash
kubectl get secret docker-secret -n bluesky-anna-aurora-sandbox
NAME             STATE    AGE
docker-secret    Active   3m

kubectl get secret docker-secret -n alpha-dave-aurora-sandbox
NAME             STATE    AGE
docker-secret    Active   2m
```

`TemplateGroupInstance` can also target specific tenants or all tenant namespaces under a single yaml definition.

### TemplateGroupInstance for multiple Tenants

It can be done by using the `matchExpressions` field, dividing the tenant label in key and values. 

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: docker-secret-group-instance
spec:
  template: docker-pull-secret
  selector:
    matchExpressions:
    - key: stakater.com/tenant
      operator: In
      values:
        - alpha
        - beta
  sync: true
```

### TemplateGroupInstance for all Tenants

This can also be done by using the `matchExpressions` field, using just the tenant label key `stakater.com/tenant`.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: docker-secret-group-instance
spec:
  template: docker-pull-secret
  selector:
    matchExpressions:
    - key: stakater.com/tenant
      operator: Exists
  sync: true
```

## Deploying Template to Namespaces via Tenant

Bill is a cluster admin who wants to deploy a docker-pull-secret in Anna's tenant namespaces where certain labels exists.

First, Bill creates a template:

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

Once the template has been created, Bill edits Anna's tenant and populates the `namespacetemplate` field:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
  editors:
    users:
    - john@aurora.org
  quota: small
  sandboxConfig:
    enabled: true
  templateInstances:
  - spec:
      template: docker-pull-secret
    selector:
      matchLabels:
        kind: build
```

Multi Tenant Operator will deploy `TemplateInstances` mentioned in `templateInstances` field, `TemplateInstances` will only be applied in those `namespaces` which belong to Anna's `tenant` and have the matching label of `kind: build`.

So now Anna adds label `kind: build` to her existing namespace `bluesky-anna-aurora-sandbox`, and after adding the label she see's that the secret has been created.

```bash
kubectl get secret docker-secret -n bluesky-anna-aurora-sandbox
NAME                  STATE    AGE
docker-pull-secret    Active   3m
```

## Deploying Template to a Namespace via TemplateInstance

Anna wants to deploy a docker pull secret in her namespace.

First Anna asks Bill, the cluster admin, to create a template of the secret for her:

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

Once the template has been created, Anna creates a `TemplateInstance` in her namespace referring to the `Template` she wants to deploy:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateInstance
metadata:
  name: docker-pull-secret-instance
  namespace: bluesky-anna-aurora-sandbox
spec:
  template: docker-pull-secret
  sync: true
```

Once this is created, Anna can see that the secret has been successfully applied.

```bash
kubectl get secret docker-secret -n bluesky-anna-aurora-sandbox
NAME                  STATE    AGE
docker-pull-secret    Active   3m
```

## Passing Parameters to Template via TemplateInstance, TemplateGroupInstance or Tenant

Anna wants to deploy a LimitRange resource to certain namespaces.

First Anna asks Bill, the cluster admin, to create template with parameters for LimitRange for her:

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

Afterwards, Anna creates a `TemplateInstance` in her namespace referring to the `Template` she wants to deploy:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateInstance
metadata:
  name: namespace-parameterized-restrictions-instance
  namespace: bluesky-anna-aurora-sandbox
spec:
  template: namespace-parameterized-restrictions
  sync: true
parameters:
  - name: DEFAULT_CPU_LIMIT
    value: "1.5"
  - name: DEFAULT_CPU_REQUESTS
    value: "1"
```

If she wants to distribute the same Template over multiple namespaces, she can use `TemplateGroupInstance`.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: namespace-parameterized-restrictions-tgi
spec:
  template: namespace-parameterized-restrictions
  sync: true
  selector:
    matchExpressions:
    - key: stakater.com/tenant
      operator: In
      values:
        - alpha
        - beta
parameters:
  - name: DEFAULT_CPU_LIMIT
    value: "1.5"
  - name: DEFAULT_CPU_REQUESTS
    value: "1"
```

Or she can use her tenant to cover only the tenant namespaces.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
  editors:
    users:
    - john@aurora.org
  quota: small
  sandboxConfig:
    enabled: true
  templateInstances:
  - spec:
      template: namespace-parameterized-restrictions
      sync: true
    parameters:
      - name: DEFAULT_CPU_LIMIT
        value: "1.5"
      - name: DEFAULT_CPU_REQUESTS
        value: "1"
    selector:
      matchLabels:
        kind: build
```
