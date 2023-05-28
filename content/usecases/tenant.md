# Creating Tenant

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

Anna can now login to the cluster and check if she can create namespaces

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

## Assign multiple users as tenant owner

In the example above, Bill assigned the ownership of `bluesky` to `Anna`. If another user, e.g. `Anthony` needs to administer `bluesky`, than Bill can assign the ownership of tenant to that user as well:

```yaml
kubectl apply -f - << EOF
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

With the configuration above, Anthony can log-in to the cluster and execute

```bash
kubectl auth can-i create namespaces
yes
```

## Assigning Users Sandbox Namespace

Bill assigned the ownership of `bluesky` to `Anna` and `Anthony`. Now if the users want sandboxes to be made for them, they'll have to ask `Bill` to enable `sandbox` functionality.

To enable that, Bill will just set `enabled: true` within the `sandboxConfig` field

```yaml
kubectl apply -f - << EOF
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
  sandboxConfig:
    enabled: true
EOF
```

With the above configuration `Anna` and `Anthony` will now have new sandboxes created

```bash
kubectl get namespaces
NAME                             STATUS   AGE
bluesky-anna-aurora-sandbox      Active   5d5h
bluesky-anthony-aurora-sandbox   Active   5d5h
bluesky-john-aurora-sandbox      Active   5d5h
```

If Bill wants to make sure that only the sandbox owner can view his sandbox namespace, he can achieve this by setting `private: true` within the `sandboxConfig` filed.

## Creating Namespaces via Tenant Custom Resource

Bill now wants to create namespaces for `dev`, `build` and `production` environments for the tenant members. To create those namespaces Bill will just add those names within the `namespaces` field in the tenant CR. If Bill wants to append the tenant name as a prefix in namespace name, then he can use `namespaces.withTenantPrefix` field. Else he can use `namespaces.withoutTenantPrefix` for namespaces for which he does not need tenant name as a prefix.

```yaml
kubectl apply -f - << EOF
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
  namespaces:
    withTenantPrefix:
      - dev
      - build
    withoutTenantPrefix:
      - prod
EOF
```

With the above configuration tenant members will now see new namespaces have been created.

```bash
kubectl get namespaces
NAME             STATUS   AGE
bluesky-dev      Active   5d5h
bluesky-build    Active   5d5h
prod             Active   5d5h
```

## Distributing common labels and annotations to tenant namespaces via Tenant Custom Resource

Bill now wants to add labels/annotations to all the namespaces for a tenant. To create those labels/annotations Bill will just add them into `commonMetadata.labels`/`commonMetadata.annotations` field in the tenant CR.

```yaml
kubectl apply -f - << EOF
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
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod
  commonMetadata:
    labels:
      app.kubernetes.io/managed-by: tenant-operator
      app.kubernetes.io/part-of: tenant-alpha
    annotations:
      openshift.io/node-selector: node-role.kubernetes.io/infra=
EOF
```

With the above configuration all tenant namespaces will now contain the mentioned labels and annotations.

## Distributing specific labels and annotations to tenant namespaces via Tenant Custom Resource

Bill now wants to add labels/annotations to specific namespaces for a tenant. To create those labels/annotations Bill will just add them into `specificMetadata.labels`/`specificMetadata.annotations` and specific namespaces in `specificMetadata.namespaces` field in the tenant CR.

```yaml
kubectl apply -f - << EOF
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
  sandboxConfig:
    enabled: true
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod
  specificMetadata:
    - namespaces:
        - bluesky-anna-aurora-sandbox
      labels:
        app.kubernetes.io/is-sandbox: true
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
EOF
```

With the above configuration all tenant namespaces will now contain the mentioned labels and annotations.

## Retaining tenant namespaces and AppProject when a tenant is being deleted

Bill now wants to delete tenant `bluesky` and wants to retain all namespaces and AppProject of the tenant. To retain the namespaces Bill will set `spec.onDelete.cleanNamespaces`, and `spec.onDelete.cleanAppProjects` to `false`.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: bluesky
spec:
  owners:
    users:
    - anna@aurora.org
    - anthony@aurora.org
  quota: small
  sandboxConfig:
    enabled: true
  namespaces:
    withTenantPrefix:
      - dev
      - build
      - prod
  onDelete:
    cleanNamespaces: false
    cleanAppProject: false
```

With the above configuration all tenant namespaces and AppProject will not be deleted when tenant `bluesky` is deleted. By default, the value of `spec.onDelete.cleanNamespaces` is also `false` and `spec.onDelete.cleanAppProject` is `true`