# Installation

Template Operator ships with MTO. Installing MTO installs it too, so there is nothing to enable in the IntegrationConfig and no separate chart or operator to install.

- **OLM (OpenShift):** the MTO bundle declares Template Operator as a dependency, so OLM installs it alongside MTO.
- **Helm:** the MTO chart carries Template Operator as a chart dependency and deploys it into MTO's namespace.

To install MTO itself, see [Installing MTO](../overview.md).

## Verify

Check that Template Operator's CRDs are present:

```bash
kubectl get crd templates.templates.stakater.com templateinstances.templates.stakater.com clustertemplateinstances.templates.stakater.com
```

And that its controller is running in MTO's namespace:

```bash
kubectl get pods -n multi-tenant-operator | grep template
```
