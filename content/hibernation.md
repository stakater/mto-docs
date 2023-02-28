# Hibernating Namespaces

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
