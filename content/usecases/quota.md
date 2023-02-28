# Enforcing Resources Quotas

Using Multi Tenant Operator, the cluster-admin can set and enforce resource quotas and limit ranges for tenants.

## Assigning Resource Quotas

Bill is a cluster admin who will first creates a resource quota where he sets the maximum resource limits that Anna's tenant will have.
Here `limitrange` is an optional field, cluster admin can skip it if not needed.

The annotation `quota.tenantoperator.stakater.com/is-default: "true"` sets the quota as default quota.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
  annotations:
    quota.tenantoperator.stakater.com/is-default: "false"
  name: small
spec:
  resourcequota:
    hard:
      requests.cpu: '5'
      requests.memory: '5Gi'
      configmaps: "10"
      secrets: "10"
      services: "10"
      services.loadbalancers: "2"
  limitrange:
    limits:
      - type: "Pod"
        max:
          cpu: "2"
          memory: "1Gi"
        min:
          cpu: "200m"
          memory: "100Mi"
EOF
```

For more details please refer to [Quotas](../customresources.md#_1-quota).

```bash
kubectl get quota small
NAME       STATE    AGE
small      Active   3m
```

Bill then proceeds to create a tenant for Anna, while also linking the newly created `quota`.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@stakater.com
  quota: small
  sandbox: false
EOF
```

When no quota is mentioned in the `quota` field of Tenant CR, MTO looks for quota with the following annotation `quota.tenantoperator.stakater.com/is-default: "true"` and links that quota with the tenant.

Now that the quota is linked with Anna's tenant, Anna can create any resource within the values of resource quota and limit range.

```bash
kubectl -n bluesky-production create deployment nginx --image nginx:latest --replicas 4
```

Once the resource quota assigned to the tenant has been reached, Anna cannot create further resources.

```bash
kubectl create pods bluesky-training
Error from server (Cannot exceed Namespace quota: please, reach out to the system administrators)
```

## What’s next

See how Bill can create [tenants](./tenant.md)
