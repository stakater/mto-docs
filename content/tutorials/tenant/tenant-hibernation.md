# Hibernating a Tenant

Implementing hibernation for tenants' namespaces efficiently manages cluster resources by temporarily reducing workload activities during off-peak hours. This guide demonstrates how to configure hibernation schedules for tenant namespaces, leveraging Tenant and ResourceSupervisor for precise control.

## Configuring Hibernation for Tenant Namespaces

You can manage workloads in your cluster with MTO by implementing a hibernation schedule for your tenants.
Hibernation downsizes the running Deployments and StatefulSets in a tenant’s namespace according to a defined cron schedule. You can set a hibernation schedule for your tenants by adding the ‘spec.hibernation’ field to the tenant's respective Custom Resource.

```yaml
hibernation:
  sleepSchedule: 23 * * * *
  wakeSchedule: 26 * * * *
```

`spec.hibernation.sleepSchedule` accepts a cron expression indicating the time to put the workloads in your tenant’s namespaces to sleep.

`spec.hibernation.wakeSchedule` accepts a cron expression indicating the time to wake the workloads in your tenant’s namespaces up.

!!! note
    Both sleep and wake schedules must be specified for your Hibernation schedule to be valid.

Additionally, adding the `hibernation.stakater.com/exclude: 'true'` annotation to a namespace excludes it from hibernating.

!!! note
    This is only true for hibernation applied via the Tenant Custom Resource, and does not apply for hibernation done by manually creating a ResourceSupervisor (details about that below).

!!! note
    This will not wake up an already sleeping namespace before the wake schedule.

## Resource Supervisor

Adding a Hibernation Schedule to a Tenant creates an accompanying ResourceSupervisor Custom Resource.
The Resource Supervisor stores the Hibernation schedules and manages the current and previous states of all the applications, whether they are sleeping or awake.

When the sleep timer is activated, the Resource Supervisor controller stores the details of your applications (including the number of replicas, configurations, etc.) in the applications' namespaces and then puts your applications to sleep. When the wake timer is activated, the controller wakes up the applications using their stored details.

Enabling ArgoCD support for Tenants will also hibernate applications in the tenants' `appProjects`.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: sigma
spec:
  argocd:
    appProjects:
      - sigma
    namespace: openshift-gitops
  hibernation:
    sleepSchedule: 42 * * * *
    wakeSchedule: 45 * * * *
  namespaces:
    - tenant-ns1
    - tenant-ns2
```

> Currently, Hibernation is available only for StatefulSets and Deployments.

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
  hibernation:
    sleepSchedule: 42 * * * *
    wakeSchedule: 45 * * * *
  namespaces:
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
  name: example
spec:
  argocd:
    appProjects: []
    namespace: ''
  hibernation:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    - build
    - stage
    - dev
status:
  currentStatus: running
  nextReconcileTime: '2022-10-12T20:00:00Z'
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
  hibernation:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    - build
    - stage
    - dev
status:
  currentStatus: sleeping
  nextReconcileTime: '2022-10-13T08:00:00Z'
  sleepingApplications:
    - Namespace: build
      kind: Deployment
      name: example
      replicas: 3
    - Namespace: stage
      kind: Deployment
      name: example
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
  hibernation:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    - stage
    - dev
status:
  currentStatus: sleeping
  nextReconcileTime: '2022-10-13T08:00:00Z'
  sleepingApplications:
    - Namespace: stage
      kind: Deployment
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
  hibernation:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  namespaces:
    - ns2
    - ns4
status:
  currentStatus: sleeping
  nextReconcileTime: '2022-10-13T08:00:00Z'
  sleepingApplications:
    - Namespace: ns2
      kind: Deployment
      name: test-deployment
      replicas: 3
```
