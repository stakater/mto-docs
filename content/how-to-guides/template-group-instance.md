# TemplateGroupInstance

Cluster scoped resource:

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
  - name: CIDR_IP
    value: "172.17.0.0/16"
```

TemplateGroupInstance distributes a template across multiple namespaces which are selected by labelSelector.
