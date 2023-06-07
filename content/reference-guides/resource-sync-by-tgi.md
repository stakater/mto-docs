# Sync Resources Deployed by TemplateGroupInstance

The TemplateGroupInstance CR provides two types of resource sync for the resources mentioned in Template

For the given example, let's consider we want to apply the following template

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

    - apiVersion: v1
      kind: ServiceAccount
      metadata:
        name: example-automated-thing
      secrets:
        - name: example-automated-thing-token-zyxwv
```

And the following TemplateGroupInstance is used to deploy these resources to namespaces having label `kind: build`

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: docker-secret-group-instance
spec:
  template: docker-secret
  selector:
    matchLabels:
      kind: build
  sync: true
```

As we can see, in our TGI, we have a field `spec.sync` which is set to `true`. This will update the resources on two conditions:

- The Template CR is updated
- The TemplateGroupInstance CR is reconciled/updated

- If, for any reason, the underlying resource gets updated or deleted, `TemplateGroupInstance` CR will try to revert it back to the state mentioned in the `Template` CR.

!!! note
    
    If the updated field of the deployed manifest is not mentioned in the Template, it will not get reverted. 

    For example, if `secrets` field is not mentioned in ServiceAcoount in the above Template, it will not get reverted if changed

## Ignore Resources Updates on Resources

If the resources mentioned in `Template` CR conflict with another controller/operator, and you want TemplateGroupInstance to not actively revert the resource updates, you can add the following label to the conflicting resource `multi-tenant-operator/ignore-resource-updates: ""`.

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

    - apiVersion: v1
      kind: ServiceAccount
      metadata:
        name: example-automated-thing
        labels:
          multi-tenant-operator/ignore-resource-updates: ""
      secrets:
        - name: example-automated-thing-token-zyxwv
```

!!! note
    
    However, this label will not stop Multi Tenant Operator from updating the resource on following conditions:

    - Template gets updated
    - TemplateGroupInstance gets updated
    - Resource gets deleted

If you dont want to sync the resources in any case, you can disable sync via `sync: false` in `TemplateGroupInstance` spec.