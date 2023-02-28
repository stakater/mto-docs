# Propagate Secrets from Parent to Descendant namespaces

Secrets like `registry` credentials often need to exist in multiple Namespaces, so that Pods within different namespaces can have access to those credentials in form of secrets.

Manually creating secrets within different namespaces could lead to challenges, such as:

- Will have to create secret either manually or via GitOps each time there is a new descendant namespace that needs the secret
- If we update the parent secret, will have to update the secret in all descendant namespaces
- This could be time-consuming, and a small mistake while creating or updating the secret could lead to unnecessary debugging

MTO will copy a Secret called `regcred` which exists in the `default` or any other Namespace to new Namespaces when they are created.
It will also push updates to the copied Secrets and keep the propagated secrets always sync and updated with parent namespaces.

---

With the help of Multi-Tenant Operator's Template feature we can make this secret distribution experience easy.
We will first create a Template which will have reference of the registry secret.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: registry-secret
resources:
  resourceMappings:
    secrets:
      - name: registry
        namespace: default
```

Now using this Template we can propagate registry secret to different namespaces that has some common set of labels.
By using this label approach we don't have to maintain list of namespaces where we would like this secret to be created.
For example, will just add one label `kind: registry` and all namespaces with this label will get this secret.

For propagating it on different namespaces dynamically will have to create another resource called `TemplateGroupInstance`.
`TemplateGroupInstance` will have `Template` and `matchLabel` mapping as shown below:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: registry-secret-group-instance
spec:
  template: registry-secret
  selector:
    matchLabels:
      kind: registry
  sync: true
```

Afterwards, you will be able to see those secrets would be been mapped in all matching namespaces.
And, any time there is any new namespace created with these set of labels, will get these secrets too.

```bash
kubectl get secret registry-secret -n example-ns-1
NAME             STATE    AGE
registry-secret    Active   3m

kubectl get secret registry-secret -n example-ns-2
NAME             STATE    AGE
registry-secret    Active   3m
```
