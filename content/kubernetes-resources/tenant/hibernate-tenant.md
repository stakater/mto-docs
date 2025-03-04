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

## Resource Supervisor

Adding a Hibernation Schedule to a Tenant creates an accompanying ResourceSupervisor Custom Resource.

When the sleep timer is activated, the Resource Supervisor puts your applications to sleep and store their previous state. When the wake timer is activated, it uses the stored state to bring them back to running state.

Enabling ArgoCD support for Tenants will also hibernate applications in the tenants' `appProjects`.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: sigma-tenant
spec:
  argocd:
    appProjects:
      - sigma-tenant
    namespace: openshift-gitops
  schedule:
    sleepSchedule: 42 * * * *
    wakeSchedule: 45 * * * *

  namespaces:
    labelSelector:
      matchLabels:
        stakater.com/current-tenant: sigma
      matchExpressions: {}
    names:
    - tenant-ns1
    - tenant-ns2
```

> Currently, Hibernation is available only for `StatefulSets` and `Deployments`.

### Manual creation of ResourceSupervisor

Hibernation can also be applied by creating a ResourceSupervisor resource manually.
The ResourceSupervisor definition will contain the hibernation cron schedule, the names of the namespaces to be hibernated, and the names of the ArgoCD AppProjects whose ArgoCD Applications have to be hibernated (as per the given schedule).

This method can be used to hibernate:

- Some specific namespaces and AppProjects in a tenant
- A set of namespaces and AppProjects belonging to different tenants
- Namespaces and AppProjects belonging to a tenant that the cluster admin is not a member of
- Non-tenant namespaces and ArgoCD AppProjects

As an example, the following ResourceSupervisor could be created manually, to apply hibernation explicitly to the 'ns1' and 'ns2' namespaces, and to the 'sample-app-project' AppProject.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: hibernator
spec:
  argocd:
    appProjects:
      - sample-app-project
    namespace: openshift-gitops
  schedule:
    sleepSchedule: 42 * * * *
    wakeSchedule: 45 * * * *

  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
    - ns1
    - ns2
```

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

Bill can verify this behaviour by checking the newly created ResourceSupervisor resource at run time:

```bash
oc get ResourceSupervisor -A
NAME           AGE
sigma          5m
```

The ResourceSupervisor will look like this at 'running' time (as per the schedule):

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  finalizers:
  - tenantoperator.stakater.com/resourcesupervisor
  generation: 1
  name: sigma
  ownerReferences:
  - apiVersion: tenantoperator.stakater.com/v1beta3
    blockOwnerDeletion: true
    controller: true
    kind: Tenant
    name: sigma
spec:
  argocd:
    appProjects: []
    namespace: ""
  namespaces:
    names:
    - stage
    - build
    - dev
  schedule:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
status:
  currentStatus: running
  nextReconcileTime: "2024-06-10T20:00:00Z"
```

The ResourceSupervisor will look like this at 'sleeping' time (as per the schedule):

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: example
spec:
  argocd:
    appProjects: []
    namespace: ''
  schedule:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
      - build
      - stage
      - dev
status:
  currentStatus: sleeping
  nextReconcileTime: '2024-06-11T08:00:00Z'
  sleepingNamespaces:
  - Namespace: build
    sleepingApplications:
    - kind: Deployment
      name: Example
      replicas: 3
  - Namespace: stage
    sleepingApplications:
    - kind: Deployment
      name: Example
      replicas: 3
```

Bill wants to prevent the `build` namespace from going to sleep, so he can add the `hibernation.stakater.com/exclude: 'true'` annotation to it. The ResourceSupervisor will now look like this after reconciling:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: example
spec:
  argocd:
    appProjects: []
    namespace: ''
  schedule:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
      - stage
      - dev
status:
  currentStatus: sleeping
  nextReconcileTime: '2024-07-12T08:00:00Z'
  sleepingNamespaces:
  - Namespace: build
    sleepingApplications:
    - kind: Deployment
      name: example
      replicas: 3
```

## Hibernating namespaces and/or ArgoCD Applications with ResourceSupervisor

Bill, the cluster administrator, wants to hibernate a collection of namespaces and AppProjects belonging to multiple different tenants. He can do so by creating a ResourceSupervisor manually, specifying the hibernation schedule in its spec, the namespaces and ArgoCD Applications that need to be hibernated as per the mentioned schedule.
Bill can also use the same method to hibernate some namespaces and ArgoCD Applications that do not belong to any tenant on his cluster.

The example given below will hibernate the ArgoCD Applications in the 'test-app-project' AppProject; and it will also hibernate the 'ns2' and 'ns4' namespaces.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: test-resource-supervisor
spec:
  argocd:
    appProjects:
      - test-app-project
    namespace: argocd-ns
  schedule:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
      - ns2
      - ns4
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

For more info see [here](../../crds-api-reference/resource-supervisor.md)
