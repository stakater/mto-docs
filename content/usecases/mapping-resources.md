# Mapping Resources across Tenant Namespaces via TGI

Bill is a cluster admin who wants to map a `docker-pull-secret`, present in a `build` namespace, in tenant namespaces where certain labels exists.

First, Bill creates a template:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: docker-pull-secret
resources:
  resourceMappings:
    secrets:
      - name: docker-pull-secret
        namespace: build
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

Afterwards, Bill can see that secrets has been successfully mapped in all matching namespaces.

```bash
kubectl get secret docker-pull-secret -n bluesky-anna-aurora-sandbox
NAME             STATE    AGE
docker-pull-secret    Active   3m

kubectl get secret docker-pull-secret -n alpha-haseeb-aurora-sandbox
NAME             STATE    AGE
docker-pull-secret    Active   3m
```

## Mapping Resources within Tenant Namespaces via TI

Anna is a tenant owner who wants to map a `docker-pull-secret`, present in `bluseky-build` namespace, to `bluesky-anna-aurora-sandbox` namespace.

First, Bill creates a template:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: docker-pull-secret
resources:
  resourceMappings:
    secrets:
      - name: docker-pull-secret
        namespace: bluesky-build
```

Once the template has been created, Anna creates a `TemplateInstance` in `bluesky-anna-aurora-sandbox` namespace, referring to the `Template`.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateInstance
metadata:
  name: docker-secret-instance
  namespace: bluesky-anna-aurora-sandbox
spec:
  template: docker-pull-secret
  sync: true
```

Afterwards, Bill can see that secrets has been successfully mapped in all matching namespaces.

```bash
kubectl get secret docker-pull-secret -n bluesky-anna-aurora-sandbox
NAME             STATE    AGE
docker-pull-secret    Active   3m
```
