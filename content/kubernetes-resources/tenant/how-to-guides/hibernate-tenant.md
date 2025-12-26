# Hibernate a Tenant

Implementing hibernation for tenants' namespaces efficiently manages cluster resources by temporarily reducing workload activities during off-peak hours. This guide demonstrates how to configure hibernation schedules for tenant namespaces, leveraging Tenant and ResourceSupervisor for precise control.

## Configuring Hibernation for Tenant Namespaces

You can manage workloads in your cluster with MTO by implementing a hibernation schedule for your tenants.
Hibernation downsizes the running `Deployments` and `StatefulSets` in a tenant’s namespace according to a defined cron schedule. You can set a hibernation schedule for your tenants by adding the ‘spec.hibernation’ field to the tenant's respective Custom Resource.

```yaml
hibernation:
  sleepSchedule: 23 * * * *
  wakeSchedule: 26 * * * *
```

`spec.hibernation.sleepSchedule` accepts a cron expression indicating the time to put the workloads in your tenant’s namespaces to sleep.

`spec.hibernation.wakeSchedule` accepts a cron expression indicating the time to wake the workloads in your tenant’s namespaces up.

!!! note
    Both sleep and wake schedules must be specified for your tenant's hibernation schedule to be valid.

Additionally, adding the `hibernation.stakater.com/exclude: 'true'` annotation to a namespace excludes it from hibernating.

!!! note
    This is only true for hibernation applied via the Tenant Custom Resource, and does not apply for hibernation done by manually creating a ResourceSupervisor (details about that below).

## Freeing up unused resources with hibernation

## Hibernating a tenant

Bill is a cluster administrator who wants to free up unused cluster resources at nighttime, in an effort to reduce costs (when the cluster isn't being used).

First, Bill creates a tenant with the `hibernation` schedules mentioned in the spec, or adds the hibernation field to an existing tenant:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: sigma
spec:
  hibernation:
    sleepSchedule: "0 20 * * 1-5"  # Sleep at 8 PM on weekdays
    wakeSchedule: "0 8 * * 1-5"    # Wake at 8 AM on weekdays
  accessControl:
    owners:
      users:
        - user@example.com
  quota: medium
  namespaces:
    withoutTenantPrefix:
      - dev
      - stage
      - build
```

The schedules above will put all the `Deployments` and `StatefulSets` within the tenant's namespaces to sleep, by reducing their pod count to 0 at 8 PM every weekday. At 8 AM on weekdays, the namespaces will then wake up by restoring their applications' previous pod counts.

## Hibernating namespaces and/or ArgoCD Applications with ClusterResourceSupervisor

Bill, the cluster administrator, wants to hibernate a collection of namespaces and AppProjects belonging to multiple different tenants. He can do so by creating a ClusterResourceSupervisor manually, specifying the hibernation schedule in its spec, the namespaces and ArgoCD Applications that need to be hibernated as per the mentioned schedule.
Bill can also use the same method to hibernate some namespaces and ArgoCD Applications that do not belong to any tenant on his cluster.

The example given below will hibernate the ArgoCD Applications in the 'test-app-project' AppProject; and it will also hibernate the 'ns2' and 'ns4' namespaces.

```yaml
status:
  currentStatus: sleeping
  nextReconcileTime: '2022-10-13T08:00:00Z'
  sleepingNamespaces:
  - Namespace: build
    sleepingApplications:
    - kind: Deployment
      name: test-deployment
      replicas: 3
    - kind: Deployment
      name: test-deployment
      replicas: 3
```
