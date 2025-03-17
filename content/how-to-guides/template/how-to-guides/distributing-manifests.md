# Distributing Resources in Namespaces

Multi Tenant Operator has two Custom Resources which can cover this need using the [`Template` CR](../../template/template.md), depending upon the conditions and preference.

1. TemplateGroupInstance
1. TemplateInstance

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

Once the template has been created, Bill makes a `TemplateGroupInstance` referring to the `Template` he wants to deploy with `template` field, and the namespaces where resources are needed, using `selector` field:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: docker-secret-group-instance
spec:
  template: docker-pull-secret
  selector:
    matchExpressions:
    - key: kind
      operator: In
      values:
        - build
  sync: true
```

Afterward, Bill can see that secrets have been successfully created in all label matching namespaces.

```bash
kubectl get secret docker-secret -n bluesky-anna-aurora-sandbox
NAME             STATE    AGE
docker-secret    Active   3m

kubectl get secret docker-secret -n alpha-dave-aurora-sandbox
NAME             STATE    AGE
docker-secret    Active   2m
```

`TemplateGroupInstance` can also target specific tenants or all tenant namespaces under a single YAML definition.
