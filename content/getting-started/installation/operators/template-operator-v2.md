# Installation

Template Operator v2 ships with MTO but is off by default. Turn it on in the IntegrationConfig and MTO deploys and manages it. There is no separate chart or operator to install.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  components:
    templateOperatorV2:
      mode: Managed   # default Disabled
      values: {}      # optional Template Operator v2 chart values
```

`values` takes the operator's own Helm chart values, for example `rbac.additionalRules` to let it read the kinds your templates reference. Setting `mode` back to `Disabled` removes it. See [IntegrationConfig](../../../concepts/integration-config.md#template-operator-v2) for every option.

To install MTO itself, see [Installing MTO](../overview.md).

## Verify

Check that Template Operator v2's CRDs are present:

```bash
kubectl get crd templates.templates.v2.stakater.com templateinstances.templates.v2.stakater.com
```

And that its controller is running in MTO's namespace:

```bash
kubectl get pods -n multi-tenant-operator | grep template-operator-v2
```
