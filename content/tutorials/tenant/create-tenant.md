# Creating a Tenant

Bill is a cluster admin who receives a new request from Aurora Solutions CTO asking for a new tenant for Anna's team.

Bill creates a new tenant called `bluesky` in the cluster:

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  editors:
    users:
    - john@aurora.org
    groups:
    - alpha
  quota: small
  sandbox: false
EOF
```

Bill checks if the new tenant is created:

```bash
kubectl get tenants.tenantoperator.stakater.com bluesky
NAME       STATE    AGE
bluesky    Active   3m
```

Anna can now log in to the cluster and check if she can create namespaces

```bash
kubectl auth can-i create namespaces
yes
```

However, cluster resources are not accessible to Anna

```bash
kubectl auth can-i get namespaces
no

kubectl auth can-i get persistentvolumes
no
```

Including the `Tenant` resource

```bash
kubectl auth can-i get tenants.tenantoperator.stakater.com
no
```
