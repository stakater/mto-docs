# Extending the default access level for tenant members

Bill as the cluster admin wants to extend the default access for tenant members. As an admin of an OpenShift Cluster, Bill can extend the admin, edit, and view ClusterRole using aggregation. Bill will first create a ClusterRole with privileges to resources which Bill wants to extend. Bill will add the aggregation label to the newly created ClusterRole for extending the default ClusterRoles.

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
