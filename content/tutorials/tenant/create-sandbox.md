# Create Sandbox Namespaces for Tenant Users

Sandbox namespaces offer a personal development and testing space for users within a tenant. This guide covers how to enable and configure sandbox namespaces for tenant users, along with setting privacy and applying metadata specifically for these sandboxes.

## Enabling Sandbox Namespaces

Bill has assigned the ownership of the tenant bluesky to Anna and Anthony. To provide them with their sandbox namespaces, he must enable the sandbox functionality in the tenant's configuration.

To enable sandbox namespaces, Bill updates the Tenant Custom Resource (CR) with sandboxes.enabled: true:

```yaml
kubectl apply -f - << EOF
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
    editors:
      users:
        - john@aurora.org
      groups:
        - alpha
  namespaces:
    sandboxes:
      enabled: true
EOF
```

This configuration automatically generates sandbox namespaces for Anna, Anthony, and even John (as an editor) with the naming convention `<tenantName>-<userName>-sandbox`.

```bash
kubectl get namespaces
NAME                             STATUS   AGE
bluesky-anna-aurora-sandbox      Active   5d5h
bluesky-anthony-aurora-sandbox   Active   5d5h
bluesky-john-aurora-sandbox      Active   5d5h
```

### Creating Private Sandboxes

To address privacy concerns where users require their sandbox namespaces to be visible only to themselves, Bill can set the `sandboxes.private: true` in the Tenant CR:

```yaml
kubectl apply -f - << EOF
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
    editors:
      users:
        - john@aurora.org
      groups:
        - alpha
  namespaces:
    sandboxes:
      enabled: true
      private: true
EOF
```

With `private: true`, each sandbox namespace is accessible and visible only to its designated user, enhancing privacy and security.

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

## Applying Metadata to Sandbox Namespaces

For uniformity or to apply specific policies, Bill might need to add common metadata, such as labels or annotations, to all sandbox namespaces. This is achievable through the `namespaces.metadata.sandbox` configuration:

```yaml
kubectl apply -f - << EOF
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
    editors:
      users:
        - john@aurora.org
      groups:
        - alpha
  namespaces:
    sandboxes:
      enabled: true
      private: true
    metadata:
      sandbox:
        labels:
          app.kubernetes.io/part-of: che.eclipse.org
        annotations:
          che.eclipse.org/username: "{{ TENANT.USERNAME }}"
EOF
```

The templated annotation "{{ TENANT.USERNAME }}" dynamically inserts the username of the sandbox owner, personalizing the sandbox environment. This capability is particularly useful for integrating with other systems or applications that might utilize this metadata for configuration or access control.

Through the examples demonstrated, Bill can efficiently manage sandbox namespaces for tenant users, ensuring they have the necessary resources for development and testing while maintaining privacy and organizational policies.
