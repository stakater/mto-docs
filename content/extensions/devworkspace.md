# DevWorkspace

[DevWorkspaces](https://github.com/devfile/devworkspace-operator) — the workspace engine behind [Eclipse Che](https://www.eclipse.org/che/) and OpenShift Dev Spaces — only run in a namespace that carries specific `che.eclipse.org` metadata. Multi Tenant Operator (MTO) can stamp that metadata onto every sandbox namespace it creates, so each tenant user lands in a workspace-ready sandbox with no manual step.

## The metadata a sandbox needs

```yaml
labels:
  app.kubernetes.io/part-of: che.eclipse.org
  app.kubernetes.io/component: workspaces-namespace
annotations:
  che.eclipse.org/username: <username>
```

The two labels mark the namespace as a Che workspaces namespace; the annotation names the user it belongs to.

## Apply it to every sandbox

Set `spec.namespaces.metadata.sandbox` on the `Tenant`. MTO creates a sandbox namespace for each owner and editor and applies this metadata to all of them:

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
        - anna@acme.org
    editors:
      users:
        - erik@acme.org
  namespaces:
    sandboxes:
      enabled: true
      private: false
    metadata:
      sandbox:
        labels:
          app.kubernetes.io/part-of: che.eclipse.org
          app.kubernetes.io/component: workspaces-namespace
        annotations:
          che.eclipse.org/username: "{{ TENANT.USERNAME }}"
```

`{{ TENANT.USERNAME }}` resolves to the username of the owner or editor each sandbox belongs to, so every sandbox receives its own `che.eclipse.org/username`. See [Templated Metadata Values](../guides/templated-metadata-values.md).

!!! note "Legacy: setting it on IntegrationConfig"
    The same metadata can be applied to every sandbox cluster-wide through `spec.metadata.sandboxes` on the `IntegrationConfig` (note the plural key). Prefer the `Tenant` above; reach for this only on an existing `IntegrationConfig`-based setup.

    ```yaml
    apiVersion: tenantoperator.stakater.com/v1beta1
    kind: IntegrationConfig
    metadata:
      name: tenant-operator-config
      namespace: multi-tenant-operator
    spec:
      metadata:
        sandboxes:
          labels:
            app.kubernetes.io/part-of: che.eclipse.org
            app.kubernetes.io/component: workspaces-namespace
          annotations:
            che.eclipse.org/username: "{{ TENANT.USERNAME }}"
    ```
