# Create Sandbox Namespaces for Tenant Users

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

## Create Private Sandboxes

Bill assigned the ownership of `bluesky` to `Anna` and `Anthony`. Now if the users want sandboxes to be made for them, they'll have to ask `Bill` to enable `sandbox` functionality. The Users also want to make sure that the sandboxes that are created for them are also only visible to the user they belong to. To enable that, Bill will just set `enabled: true` and `private: true` within the `sandboxConfig` field

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
    private: true
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

However, from the perspective of `Anna`, only their sandbox will be visible

```bash
kubectl get namespaces
NAME                             STATUS   AGE
bluesky-anna-aurora-sandbox      Active   5d5h
```

## Set metadata on sandbox namespaces

If you want to have a common metadata on all sandboxes, you can add `sandboxMetadata` to Tenant like below:

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
  editors:
    users:
    - john@aurora.org
    groups:
    - alpha
  quota: small
  sandboxConfig:
    enabled: true
    private: true
  sandboxMetadata:
    labels:
      app.kubernetes.io/part-of: che.eclipse.org
    annotations:
      che.eclipse.org/username: "{{ TENANT.USERNAME }}" # templated placeholder
```

Note: In above Tenant, we have used a templated annotation value `"{{ TENANT.USERNAME }}"`. It will resolve to user of the respective sandbox namespace. For more info on it, see [here](../../reference-guides/templated-metadata-values.md)
