# TemplateInstance

Namespace scoped resource:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateInstance
metadata:
  name: networkpolicy
  namespace: build
spec:
  template: networkpolicy
  sync: true
parameters:
  - name: CIDR_IP
    value: "172.17.0.0/16"
```

TemplateInstance are used to keep track of resources created from Templates, which are being instantiated inside a Namespace.
Generally, a TemplateInstance is created from a Template and then the TemplateInstances will not be updated when the Template changes later on. To change this behavior, it is possible to set `spec.sync: true` in a TemplateInstance. Setting this option, means to keep this TemplateInstance in sync with the underlying template (similar to Helm upgrade).
