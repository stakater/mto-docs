# Extending Manager ClusterRole

Bill as the cluster admin want to add additional rules for manager ClusterRole.

Bill can extend rules by adding additional RBAC rules at `managerRoleExtendedRules` in MTO Helm Charts

```yaml
managerRoleExtendedRules:
  - apiGroups:
    - user.openshift.io
    resources:
    - groups
    verbs:
    - create
    - delete
    - get
    - list
    - patch
    - update
    - watch
```

## What’s next

See how Bill can [hibernate unused namespaces at night](./hibernation.md)
