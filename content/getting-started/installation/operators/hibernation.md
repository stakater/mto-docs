# Installation

The Hibernation Operator ships with MTO. Installing MTO installs it too, so there is nothing to enable in the IntegrationConfig and no separate chart or operator to install.

- **OLM (OpenShift):** the MTO bundle declares the Hibernation Operator as a dependency, so OLM installs it alongside MTO.
- **Helm:** the MTO chart carries the Hibernation Operator as a chart dependency and deploys it into MTO's namespace.

To install MTO itself, see [Installing MTO](../overview.md).

## Verify

Check that the Hibernation Operator's CRDs are present:

```bash
kubectl get crd resourcesupervisors.hibernation.stakater.com clusterresourcesupervisors.hibernation.stakater.com
```

And that its controller is running in MTO's namespace:

```bash
kubectl get pods -n multi-tenant-operator | grep hibernation
```

Once both are in place, you can [hibernate a tenant](../../../guides/hibernate-tenant.md) or create a `ResourceSupervisor` directly.
