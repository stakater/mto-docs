# Extending Admin ClusterRole

Bill as the cluster admin want to add additional rules for admin ClusterRole.

Bill can extend the `admin` role for MTO using the aggregation label for admin ClusterRole. Bill will create a new ClusterRole with all the permissions he needs to extend for MTO and add the aggregation label on the newly created ClusterRole.

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: extend-admin-role
  labels:
    rbac.authorization.k8s.io/aggregate-to-admin: 'true'
rules:
  - verbs:
      - create
      - update
      - patch
      - delete
    apiGroups:
      - user.openshift.io
    resources:
      - groups
```

> Note: You can learn more about `aggregated-cluster-roles` [here](https://kubernetes.io/docs/reference/access-authn-authz/rbac/#aggregated-clusterroles)

## What’s next

See how Bill can [hibernate unused namespaces at night](../tutorials/tenant/tenant-hibernation.md)
