# Resource Supervisor

Supports hibernation of `deployments` and `statefulsets` for given namespaces via names and/or label selectors.
If provided, it will update [AppProject](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/#creating-projects) instance with [SyncWindow](https://argo-cd.readthedocs.io/en/stable/user-guide/sync_windows/) to deny sync to selected namespaces.

Following namespaces will be ignored:

- with annotation `"hibernation.stakater.com/exclude": "true"`
- whose name match with priviledged namespaces' regex specified in [IntegrationConfig](./integration-config.md)
- namespace where MTO is installed

## Supported modes

### Hibernation with cron schedule

Applications will sleep and wakup at provided cron schedule

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: rs-example1
spec:
  argocd:
    appProjects: []
    namespace: ""
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
    - bluesky-dev
  schedule:
    sleepSchedule: "10 * * * *" # sleep each hour at min 10
    wakeSchedule: "50 * * * *" # wakeup each hour at min 50
```

### Sleep

Applications will sleep instantly, and will wakeup when resource supervisor is deleted

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: rs-example2
spec:
  argocd:
    appProjects: []
    namespace: ""
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
    - bluesky-dev
  schedule: {}
```

### Sleep at given cron schedule

Applications will sleep at provided cron schedule, and will wakeup when resource supervisor is deleted

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: rs-example3
spec:
  argocd:
    appProjects: []
    namespace: ""
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
    - bluesky-dev
  schedule:
    sleepSchedule: "0 0 1 2 2025" # sleep on 1st February 2025
```

## More examples

### Example 1

labelSelector's `matchLabels` and `matchExpressions` is `AND` operation. Here is an example with it:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: rs-example4
spec:
  argocd:
    appProjects: []
    namespace: ""
  namespaces:
    labelSelector:
      matchLabels:
        stakater.com/current-tenant: bluesky
        stakater.com/kind: dev
      matchExpressions:
       - { key: "private-sandbox", operator: In , values: ["true"] }
    names:
    - bluesky-staging
  schedule:
    sleepSchedule: ""
```

It will sleep `bluesky-staging` namespace, and all those which have the specified labels.

### Example 2

If you provide Argo CD AppProject in spec, it will create syncWindow with `deny` policy

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: rs-example4
spec:
  argocd:
    appProjects:
      - dev-apps
      - dev-apps2
    namespace: "customer-argocd-projects"
  namespaces:
    labelSelector:
      matchLabels: {}
      matchExpressions: {}
    names:
    - bluesky-staging
    - bluesky-dev
  schedule:
    sleepSchedule: ""
```

It will sleep given namespaces, and create `deny` syncWindow on provided AppProjects
