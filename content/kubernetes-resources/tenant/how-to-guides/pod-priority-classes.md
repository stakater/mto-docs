# Pod Priority Classes

## Restricting allowed Pod PriorityClasses for tenant workloads

Use the `podPriorityClasses.allowed` field in the `Tenant` CR to restrict which priority classes tenant workloads may use. This ensures that only approved priority classes are used so cluster QoS and scheduling policies remain predictable.

```yaml title="Tenant"
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-sample
spec:
  # other fields
  podPriorityClasses:
    allowed:
      - high-priority
```

### Notes

The operator will validate the `priorityClassName` field on workloads and controllers (Pods, Deployments, StatefulSets, ReplicaSets, Jobs, CronJobs, Daemonsets). The empty string (`""`) is treated as a valid `priorityClass` name — include `""` in `allowed` if you want to permit resources that omit a priority class.

### Example

Allowed Pod (uses `high-priority`):

```yaml title="Allowed Pod"
apiVersion: v1
kind: Pod
metadata:
  name: pod-allowed-pri
spec:
  priorityClassName: high-priority
  containers:
    - name: app
      image: nginx:1.23
```

Denied Pod (uses a non-allowed priority class):

```yaml title="Denied Pod"
apiVersion: v1
kind: Pod
metadata:
  name: pod-denied-pri
spec:
  priorityClassName: low-priority
  containers:
    - name: app
      image: nginx:1.23
```

### Behavior

- The first Pod will be accepted because `high-priority` is in `podPriorityClasses.allowed`.
- The second Pod will be rejected by the operator if `low-priority` is not present in the allow-list.

### Demo

![Pod Priority Classes Demo](../../../images/pod-priority.gif)
