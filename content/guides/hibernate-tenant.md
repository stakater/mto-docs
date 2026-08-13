# Hibernate a Tenant

Implementing hibernation for tenants' namespaces efficiently manages cluster resources by temporarily reducing workload activities during off-peak hours. This guide demonstrates how to configure hibernation schedules for tenant namespaces using a [ClusterResourceSupervisor](https://docs.stakater.com/hibernation-operator/latest/how-to-guides/create-cluster-resource-supervisor.html) from the [Hibernation Operator](https://docs.stakater.com/hibernation-operator).

!!! note
    The `spec.hibernation` field has been removed from the Tenant CR in MTO v1.7. Hibernation is now managed by creating a `ClusterResourceSupervisor` resource that targets tenant namespaces using label selectors.

## Prerequisites

- [Hibernation Operator](https://docs.stakater.com/hibernation-operator) must be installed on the cluster.

## Hibernating a Tenant's Namespaces

MTO automatically applies the label `stakater.com/tenant: <tenant-name>` to all namespaces managed by a tenant. You can use this label in a `ClusterResourceSupervisor` to hibernate all namespaces belonging to a specific tenant.

### Example: Hibernate all namespaces of a tenant

Bill is a cluster administrator who wants to free up unused cluster resources at nighttime, in an effort to reduce costs (when the cluster isn't being used).

Bill creates a `ClusterResourceSupervisor` that targets all namespaces belonging to the `sigma` tenant:

```yaml
apiVersion: hibernation.stakater.com/v1beta1
kind: ClusterResourceSupervisor
metadata:
  name: sigma-hibernation
spec:
  namespaces:
    labelSelector:
      matchLabels:
        stakater.com/tenant: sigma
  schedule:
    sleepSchedule: "0 20 * * 1-5"  # Sleep at 8 PM on weekdays
    wakeSchedule: "0 8 * * 1-5"    # Wake at 8 AM on weekdays
```

The schedules above will put all the `Deployments` and `StatefulSets` within the `sigma` tenant's namespaces to sleep, by reducing their pod count to 0 at 8 PM every weekday. At 8 AM on weekdays, the namespaces will then wake up by restoring their applications' previous pod counts.

### Example: Hibernate namespaces with ArgoCD AppProject integration

Bill, the cluster administrator, wants to hibernate a collection of namespaces and ArgoCD AppProjects belonging to a tenant. He can do so by creating a `ClusterResourceSupervisor` that combines a tenant label selector with ArgoCD AppProject targeting:

```yaml
apiVersion: hibernation.stakater.com/v1beta1
kind: ClusterResourceSupervisor
metadata:
  name: sigma-full-hibernation
spec:
  namespaces:
    labelSelector:
      matchLabels:
        stakater.com/tenant: sigma
  argocd:
    namespace: argocd
    appProjects:
      - sigma-app-project
  schedule:
    sleepSchedule: "0 20 * * 1-5"  # Sleep at 8 PM on weekdays
    wakeSchedule: "0 8 * * 1-5"    # Wake at 8 AM on weekdays
```

This will hibernate both the namespaces belonging to the `sigma` tenant and the ArgoCD Applications in the `sigma-app-project` AppProject.

For more details on `ClusterResourceSupervisor` configuration options, see the [Hibernation Operator documentation](https://docs.stakater.com/hibernation-operator/latest/how-to-guides/create-cluster-resource-supervisor.html).
