# Limiting PersistentVolume for Tenant

Bill, as a cluster admin, wants to restrict the amount of storage a Tenant can use. For that he'll add the `requests.storage` field to `quota.spec.resourcequota.hard`. If Bill wants to restrict tenant `bluesky` to use only `50Gi` of storage, he'll first create a quota with `requests.storage` field set to `50Gi`.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
  name: medium
spec:
  resourcequota:
    hard:
      requests.cpu: '5'
      requests.memory: '10Gi'
      requests.storage: '50Gi'
```

Once the quota is created, Bill will create the tenant and set the quota field to the one he created.

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
  quota: medium
  sandbox: true
EOF
```

Now, the combined storage used by all tenant namespaces will not exceed `50Gi`.

## Adding StorageClass Restrictions for Tenant

Now, Bill, as a cluster admin, wants to make sure that no Tenant can provision more than a fixed amount of storage from a StorageClass. Bill can restrict that using `<storage-class-name>.storageclass.storage.k8s.io/requests.storage` field in `quota.spec.resourcequota.hard` field. If Bill wants to restrict tenant `sigma` to use only `20Gi` of storage from storage class `stakater`, he'll first create a StorageClass `stakater` and then create the relevant Quota with `stakater.storageclass.storage.k8s.io/requests.storage` field set to `20Gi`.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
  name: small
spec:
  resourcequota:
    hard:
      requests.cpu: '2'
      requests.memory: '4Gi'
      stakater.storageclass.storage.k8s.io/requests.storage: '20Gi'
```

Once the quota is created, Bill will create the tenant and set the quota field to the one he created.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: sigma
spec:
  owners:
    users:
    - haseeb@aurora.org
  quota: small
  sandbox: true
EOF
```

Now, the combined storage provisioned from StorageClass `stakater` used by all tenant namespaces will not exceed `20Gi`.

> The `20Gi` limit will only be applied to StorageClass `stakater`. If a tenant member creates a PVC with some other StorageClass, he will not be restricted.

!!! tip
    More details about `Resource Quota` can be found [here](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
