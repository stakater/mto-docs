# Installation

Under MTO, the FinOps Operator is part of showback. MTO deploys it when showback is enabled in the IntegrationConfig, and removes it when showback is turned off. There is no separate chart or operator to install.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  components:
    showback: true
    finopsOperator:
      values: {}   # optional FinOps Operator chart values
```

MTO connects the operator to the PostgreSQL and OpenCost it already runs for showback, so those need no setup of their own. Rates go in `finopsOperator.values.priceBook.rates`. See [IntegrationConfig](../../../concepts/integration-config.md#finops-operator) for every option.

To install MTO itself, see [Installing MTO](../overview.md).

## Verify

Check that the FinOps Operator's CRDs are present:

```bash
kubectl get crd finopsproviders.finops.stakater.com pricebooks.finops.stakater.com costjobs.finops.stakater.com offerings.finops.stakater.com subscriptions.finops.stakater.com
```

And that its controller is running in MTO's namespace:

```bash
kubectl get pods -n multi-tenant-operator | grep finops
```
