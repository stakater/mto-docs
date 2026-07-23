# Restricting Service Accounts per Tenant

## Denying use of specific service accounts inside a tenant

Use the `serviceAccounts.denied` field in the `Tenant` CR to block pods and controllers from using particular service accounts inside tenant namespaces.

```yaml title="Tenant"
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-sample
spec:
  # other fields
  serviceAccounts:
    denied:
      - service-user-1
      - service-user-2
```

### Notes

- The operator watches these fields on resources that create pods (Pods, Deployments, StatefulSets, ReplicaSets, Jobs, CronJobs, Daemonsets).
- If a pod does not specify a service account (or specifies an empty string), it is treated as the `default` service account. To block pods that rely on the default service account, add `default` to the `denied` list.

This mechanism prevents tenants from running workloads under service accounts you consider untrusted or that have excessive privileges.

### Example

Allowed Pod (uses a permitted service account):

```yaml title="Allowed Pod"
apiVersion: v1
kind: Pod
metadata:
  name: allowed-sa
spec:
  serviceAccountName: safe-sa
  containers:
    - name: app
      image: nginx:1.23
```

Denied Pod (uses a service account that is on the deny-list):

```yaml title="Denied Pod"
apiVersion: v1
kind: Pod
metadata:
  name: denied-sa
spec:
  serviceAccountName: service-user-1
  containers:
    - name: app
      image: nginx:1.23
```

### Behavior

- The first Pod will be accepted when `safe-sa` is not listed in `serviceAccounts.denied`.
- The second Pod will be rejected or blocked by the operator if `service-user-1` appears in `serviceAccounts.denied`.

### Demo

![Service Account Validation](../../../images/service-account-validation.gif)
