# Freeing up unused resources with hibernation

## Hibernating a tenant

Bill is a cluster administrator who wants to free up unused cluster resources at nighttime, in an effort to reduce costs during the night (when the cluster isn't being used).

First, Bill creates a tenant with the `hibernation` schedules mentioned in the spec, or adds the hibernation field to an existing tenant:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: sigma
spec:
  hibernation:
    sleepSchedule: 0 20 * * 1-5
    wakeSchedule: 0 8 * * 1-5
  owners:
    users:
      - user
  editors:
    users:
      - user1
  quota: medium
  namespaces:
    withoutTenantPrefix:
      - build
      - stage
      - dev
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
  finalizers:
    - tenantoperator.stakater.com/resourcesupervisor
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
  finalizers:
    - tenantoperator.stakater.com/resourcesupervisor
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

Bill, the cluster administrator, wants to hibernate a collection of namespaces and AppProjects belonging to multiple different tenants. He can do so by creating a ResourceSupervisor manually, and specifying in its spec the hibernation schedule, and the namespaces and ArgoCD Applications that need to be hibernated as per the mentioned schedule.
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
    namespace: test-ns
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
