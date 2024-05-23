# Assigning Metadata in Tenant Custom Resources

In the v1beta3 version of the Tenant Custom Resource (CR), metadata assignment has been refined to offer granular control over labels and annotations across different namespaces associated with a tenant. This functionality enables precise and flexible management of metadata, catering to both general and specific needs.

## Distributing Common Labels and Annotations

To apply common labels and annotations across all namespaces within a tenant, the `namespaces.metadata.common` field in the Tenant CR is utilized. This approach ensures that essential metadata is uniformly present across all namespaces, supporting consistent identification, management, and policy enforcement.

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
    withTenantPrefix:
      - dev
      - build
      - prod
    metadata:
      common:
        labels:
          app.kubernetes.io/managed-by: tenant-operator
          app.kubernetes.io/part-of: tenant-alpha
        annotations:
          openshift.io/node-selector: node-role.kubernetes.io/infra=
EOF

```

By configuring the `namespaces.metadata.common` field as shown, all namespaces within the tenant will inherit the specified labels and annotations.

## Distributing Specific Labels and Annotations

For scenarios requiring targeted application of labels and annotations to specific namespaces, the Tenant CR's `namespaces.metadata.specific` field is designed. This feature enables the assignment of unique metadata to designated namespaces, accommodating specialized configurations and requirements.

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
    withTenantPrefix:
      - dev
      - build
      - prod
    metadata:
      specific:
        - namespaces:
            - bluesky-dev
          labels:
            app.kubernetes.io/is-sandbox: "true"
          annotations:
            openshift.io/node-selector: node-role.kubernetes.io/worker=
EOF
```

This configuration directs the specific labels and annotations solely to the enumerated namespaces, enabling distinct settings for particular environments.

## Assigning Metadata to Sandbox Namespaces

To specifically address *sandbox namespaces* within the tenant, the `namespaces.metadata.sandbox` property of the Tenant CR is employed. This section allows for the distinct management of sandbox namespaces, enhancing security and differentiation in development or testing environments.

```yaml
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
          che.eclipse.org/username: "{{ TENANT.USERNAME }}" # templated placeholder
```

This setup ensures that all sandbox namespaces receive the designated metadata, with support for templated values, such as **{{ TENANT.USERNAME }}**, allowing dynamic customization based on the tenant or user context.

These enhancements in metadata management within the `v1beta3` version of the Tenant CR provide comprehensive and flexible tools for labeling and annotating namespaces, supporting a wide range of organizational, security, and operational objectives.
