# Enabling DevWorkspace for Tenant's sandbox in OpenShift

## DevWorkspaces metadata via Multi Tenant Operator

DevWorkspaces require specific metadata on a namespace for it to work in it. With Multi Tenant Operator (MTO), you can create sandbox namespaces for users of a Tenant, and then add the required metadata automatically on all sandboxes.

## Required metadata for enabling DevWorkspace on sandbox

```yaml
  labels:
    app.kubernetes.io/part-of: che.eclipse.org
    app.kubernetes.io/component: workspaces-namespace
  annotations:
    che.eclipse.org/username: <username>
```

## Automate sandbox metadata for all Tenant users via Tenant CR

With Multi Tenant Operator (MTO), you can set `sandboxMetadata` like below to automate metadata for all sandboxes:

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
    viewers:
      users:
        - john@acme.org
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

It will create sandbox namespaces and also apply the `sandboxMetadata` for owners and editors. Notice the template `{{ TENANT.USERNAME }}`, it will resolve the username as value of the corresponding annotation. For more info on templated value, see [here](../../reference-guides/templated-metadata-values.md)

## Automate sandbox metadata for all Tenant users via IntegrationConfig CR

You can also automate the metadata on all sandbox namespaces by using IntegrationConfig, notice `metadata.sandboxes`:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  accessControl:
    namespaceAccessPolicy:
      deny:
        privilegedNamespaces: {}
    privileged:
      namespaces:
      - ^default$
      - ^openshift-*
      - ^kube-*
      serviceAccounts:
      - ^system:serviceaccount:openshift-*
      - ^system:serviceaccount:kube-*
      - ^system:serviceaccount:stakater-actions-runner-controller:actions-runner-controller-runner-deployment$
    rbac:
      tenantRoles:
        default:
          editor:
            clusterRoles:
            - edit
          owner:
            clusterRoles:
            - admin
          viewer:
            clusterRoles:
            - view
  components:
    console: false
    ingress:
      console: {}
      gateway: {}
      keycloak: {}
    showback: false
  integrations:
    vault:
      accessInfo:
        accessorPath: ""
        address: ""
        roleName: ""
        secretRef:
          name: ""
          namespace: ""
      authMethod: kubernetes
      config:
        ssoClient: ""
      enabled: false
  metadata:
    groups: {}
    namespaces: {}
    sandboxes:
      labels:
        app.kubernetes.io/part-of: che.eclipse.org
        app.kubernetes.io/component: workspaces-namespace
      annotations:
        che.eclipse.org/username: "{{ TENANT.USERNAME }}"
```

 For more info on templated value `"{{ TENANT.USERNAME }}"`, see [here](../../reference-guides/templated-metadata-values.md)
