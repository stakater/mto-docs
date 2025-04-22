# Quota

Underlying implementation of Quota CR in OpenShift differs from rest of the Kubernetes distributions. In OpenShift, MTO relies on [ClusterResourceQuota CR](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/schedule_and_quota_apis/clusterresourcequota-quota-openshift-io-v1) to do the calculations and link with the tenant. However, in other distributions, MTO creates underlying [ResourceQuota CRs](https://kubernetes.io/docs/concepts/policy/resource-quotas/) in every Tenant namespace which are aggregated at the time of resource admission for calculations.

!!! note
    Quota CR in Kubernetes in a preview feature, which can malfunction to allow more resources than the allowed count in its spec when the webhook is under load. Feel free to contact [Stakater Support](https://support.stakater.com/) if you have questions.

Using Multi Tenant Operator, the cluster-admin can set and enforce cluster resource quotas and limit ranges for tenants.

## Assigning Resource Quotas

Bill is a cluster admin who will first create `Quota` CR where he sets the maximum resource limits that Anna's tenant will have.
Here `limitrange` is an optional field, cluster admin can skip it if not needed.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
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

For more details please refer to [Quotas](./quota.md).

```bash
kubectl get quota small
NAME       STATE    AGE
small      Active   3m
```

Bill then proceeds to create a tenant for Anna, while also linking the newly created `Quota`.

```yaml
kubectl create -f - << EOF
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
        - anthony@aurora.org
  namespaces:
    sandboxes:
      enabled: true
EOF
```

Now that the quota is linked with Anna's tenant, Anna can create any resource within the values of resource quota and limit range.

```bash
kubectl -n bluesky-production create deployment nginx --image nginx:latest --replicas 4
```

Once the resource quota assigned to the tenant has been reached, Anna cannot create further resources.

```bash
kubectl create pods bluesky-training
Error from server (Cannot exceed Namespace quota: please, reach out to the system administrators)
```

## Limiting PersistentVolume for Tenant

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
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
        - anthony@aurora.org
  namespaces:
    sandboxes:
      enabled: true
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
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
        - anthony@aurora.org
  namespaces:
    sandboxes:
      enabled: true
EOF
```

Now, the combined storage provisioned from StorageClass `stakater` used by all tenant namespaces will not exceed `20Gi`.

> The `20Gi` limit will only be applied to StorageClass `stakater`. If a tenant member creates a PVC with some other StorageClass, he will not be restricted.

!!! tip
    More details about `Resource Quota` can be found [here](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
