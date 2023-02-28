# Integration Config

IntegrationConfig is used to configure settings of multi-tenancy for Multi Tenant Operator.

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: stakater-tenant-operator
spec:
  tenantRoles:
    default:
      owner:
        clusterRoles:
          - admin
      editor:
        clusterRoles:
          - edit
      viewer:
        clusterRoles:
          - view
          - viewer
    custom:
    - labelSelector:
        matchExpressions:
        - key: stakater.com/kind
          operator: In
          values:
            - build
        matchLabels:
          stakater.com/kind: dev
      owner:
        clusterRoles:
          - custom-owner
      editor:
        clusterRoles:
          - custom-editor
      viewer:
        clusterRoles:
          - custom-viewer
          - custom-view
  openshift:
    project:
      labels:
        stakater.com/workload-monitoring: "true"
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
    group:
      labels:
        role: customer-reader
    sandbox:
      labels:
        stakater.com/kind: sandbox
    clusterAdminGroups:
      - cluster-admins
    privilegedNamespaces:
      - ^default$
      - ^openshift-*
      - ^kube-*
    privilegedServiceAccounts:
      - ^system:serviceaccount:openshift-*
      - ^system:serviceaccount:kube-*
    namespaceAccessPolicy:
      deny:
        privilegedNamespaces:
          users:
            - system:serviceaccount:openshift-argocd:argocd-application-controller
            - adam@stakater.com
          groups:
            - cluster-admins
  argocd:
    namespace: openshift-operators
    namespaceResourceBlacklist:
      - group: '' # all groups
        kind: ResourceQuota
    clusterResourceWhitelist:
      - group: tronador.stakater.com
        kind: EnvironmentProvisioner
  rhsso:
    enabled: true
    endpoint:
      url: https://iam-keycloak-auth.apps.prod.abcdefghi.kubeapp.cloud/
      secretReference:
        name: auth-secrets
        namespace: openshift-auth
  vault:
    enabled: true
    endpoint:
      url: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
      secretReference:
        name: vault-root-token
        namespace: vault
    sso:
      clientName: vault
      accessorID: <ACCESSOR_ID_TOKEN>
```

Following are the different components that can be used to configure multi-tenancy in a cluster via Multi Tenant Operator.

## TenantRoles

TenantRoles are required within the IntegrationConfig, as they are used for defining what roles will be applied to each Tenant namespace. The field allows optional custom roles, that are then used to create RoleBindings for namespaces that match a labelSelector.

> ⚠️ If you do not configure roles in any way, then the default OpenShift roles of `owner`, `edit`, and `view` will apply to Tenant members. Their details can be found [here](./tenant-roles.md)

```yaml
tenantRoles:
  default:
    owner:
      clusterRoles:
        - admin
    editor:
      clusterRoles:
        - edit
    viewer:
      clusterRoles:
        - view
        - viewer
  custom:
  - labelSelector:
      matchExpressions:
      - key: stakater.com/kind
        operator: In
        values:
          - build
      matchLabels:
        stakater.com/kind: dev
    owner:
      clusterRoles:
        - custom-owner
    editor:
      clusterRoles:
        - custom-editor
    viewer:
      clusterRoles:
        - custom-viewer
        - custom-view
```

### Default

This field contains roles that will be used to create default roleBindings for each namespace that belongs to tenants. These roleBindings are only created for a namespace if that namespaces isn't already matched by the `custom` field below it. Therefore, it is required to have at least one role mentioned within each of its three subfields: `owner`, `editor`, and `viewer`. These 3 subfields also correspond to the member fields of the [Tenant CR](./customresources.md#_2-tenant)

### Custom

An array of custom roles. Similar to the `default` field, you can mention roles within this field as well. However, the custom roles also require the use of a `labelSelector` for each iteration within the array. The roles mentioned here will only apply to the namespaces that are matched by the labelSelector. If a namespace is matched by 2 different labelSelectors, then both roles will apply to it. Additionally, roles can be skipped within the labelSelector. These missing roles are then inherited from the `default` roles field . For example, if the following custom roles arrangement is used:

```yaml
custom:
- labelSelector:
    matchExpressions:
    - key: stakater.com/kind
      operator: In
      values:
        - build
    matchLabels:
      stakater.com/kind: dev
  owner:
    clusterRoles:
      - custom-owner
```

Then the `editor` and `viewer` roles will be taken from the `default` roles field, as that is required to have at least one role mentioned.

## OpenShift

``` yaml
openshift:
  project:
    labels:
      stakater.com/workload-monitoring: "true"
    annotations:
      openshift.io/node-selector: node-role.kubernetes.io/worker=
  group:
    labels:
      role: customer-reader
  sandbox:
    labels:
      stakater.com/kind: sandbox
  clusterAdminGroups:
    - cluster-admins
  privilegedNamespaces:
    - ^default$
    - ^openshift-*
    - ^kube-*
  privilegedServiceAccounts:
    - ^system:serviceaccount:openshift-*
    - ^system:serviceaccount:kube-*
  namespaceAccessPolicy:
    deny:
      privilegedNamespaces:
        users:
          - system:serviceaccount:openshift-argocd:argocd-application-controller
          - adam@stakater.com
        groups:
          - cluster-admins
```

### Project, group and sandbox

We can use the `openshift.project`, `openshift.group` and `openshift.sandbox` fields to automatically add `labels` and `annotations` to  the **Projects** and **Groups** managed via MTO.

```yaml
  openshift:
    project:
      labels:
        stakater.com/workload-monitoring: "true"
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
    group:
      labels:
        role: customer-reader
    sandbox:
      labels:
        stakater.com/kind: sandbox
```

If we want to add default *labels/annotations* to sandbox namespaces of tenants than we just simply add them in `openshift.project.labels`/`openshift.project.annotations` respectively.

Whenever a project is made it will have the labels and annotations as mentioned above.

```yaml
kind: Project
apiVersion: project.openshift.io/v1
metadata:
  name: bluesky-build
  annotations:
    openshift.io/node-selector: node-role.kubernetes.io/worker=
  labels:
    workload-monitoring: 'true'
    stakater.com/tenant: bluesky
spec:
  finalizers:
    - kubernetes
status:
  phase: Active
```

```yaml
kind: Group
apiVersion: user.openshift.io/v1
metadata:
  name: bluesky-owner-group
  labels:
    role: customer-reader
users:
  - andrew@stakater.com
```

### Cluster Admin Groups

`clusterAdminGroups:` Contains names of the groups that are allowed to perform CRUD operations on namespaces present on the cluster. Users in the specified group(s) will be able to perform these operations without MTO getting in their way

### Privileged Namespaces

`privilegedNamespaces:` Contains the list of `namespaces` ignored by MTO. MTO will not manage the `namespaces` in this list. Values in this list are regex patterns.
For example:

- To ignore the `default` namespace, we can specify `^default$`
- To ignore all namespaces starting with the `openshift-` prefix, we can specify `^openshift-*`.
- To ignore any namespace containing `stakater` in its name, we can specify `stakater`. (A constant word given as a regex pattern will match any namespace containing that word.)

### Privileged ServiceAccounts

`privilegedServiceAccounts:` Contains the list of `ServiceAccounts` ignored by MTO. MTO will not manage the `ServiceAccounts` in this list. Values in this list are regex patterns. For example, to ignore all `ServiceAccounts` starting with the `system:serviceaccount:openshift-` prefix, we can use `^system:serviceaccount:openshift-*`; and to ignore the `system:serviceaccount:builder` service account we can use `^system:serviceaccount:builder$.`

### Namespace Access Policy

`namespaceAccessPolicy.Deny:` Can be used to restrict privileged *users/groups* CRUD operation over managed namespaces.

```yaml
namespaceAccessPolicy:
  deny:
    privilegedNamespaces:
      groups:
        - cluster-admins
      users:
        - system:serviceaccount:openshift-argocd:argocd-application-controller
        - adam@stakater.com
```

> ⚠️ If you want to use a more complex regex pattern (for the `openshift.privilegedNamespaces` or `openshift.privilegedServiceAccounts` field), it is recommended that you test the regex pattern first -  either locally or using a platform such as <https://regex101.com/>.

## ArgoCD

### Namespace

`argocd.namespace` is an optional field used to specify the namespace where ArgoCD Applications and AppProjects are deployed. The field should be populated when you want to create an ArgoCD AppProject for each tenant.

### NamespaceResourceBlacklist

```yaml
argocd:
  namespaceResourceBlacklist:
  - group: '' # all resource groups
    kind: ResourceQuota
  - group: ''
    kind: LimitRange
  - group: ''
    kind: NetworkPolicy
```

`argocd.namespaceResourceBlacklist` prevents ArgoCD from syncing the listed resources from your GitOps repo.

### ClusterResourceWhitelist

```yaml
argocd:
  clusterResourceWhitelist:
  - group: tronador.stakater.com
    kind: EnvironmentProvisioner
```

`argocd.clusterResourceWhitelist` allows ArgoCD to sync the listed cluster scoped resources from your GitOps repo.

## RHSSO (Red Hat Single Sign-On)

Red Hat Single Sign-On [RHSSO](https://access.redhat.com/products/red-hat-single-sign-on) is based on the Keycloak project and enables you to secure your web applications by providing Web single sign-on (SSO) capabilities based on popular standards such as SAML 2.0, OpenID Connect and OAuth 2.0.

If `RHSSO` is configured on a cluster, then RHSSO configuration can be enabled.

```yaml
rhsso:
  enabled: true
  endpoint:
    secretReference:
      name: auth-secrets
      namespace: openshift-auth
    url: https://iam-keycloak-auth.apps.prod.abcdefghi.kubeapp.cloud/
```

If enabled, than admins have to provide secret and URL of RHSSO.

- `secretReference.name:` Will contain the name of the secret.
- `secretReference.namespace:` Will contain the namespace of the secret.
- `url:` Will contain the URL of RHSSO.

## Vault

[Vault](https://www.vaultproject.io/) is used to secure, store and tightly control access to tokens, passwords, certificates, encryption keys for protecting secrets and other sensitive data using a UI, CLI, or HTTP API.

If `vault` is configured on a cluster, then Vault configuration can be enabled.

```yaml
Vault:
  enabled: true
  endpoint:
    secretReference:
      name: vault-root-token
      namespace: vault
    url: >-
      https://vault.apps.prod.abcdefghi.kubeapp.cloud/
  sso:
    accessorID: <ACCESSOR_ID_TOKEN>
    clientName: vault
```

If enabled, than admins have to provide secret, URL and SSO accessorID of Vault.

- `secretReference.name:` Will contain the name of the secret.
- `secretReference.namespace:` Will contain the namespace of the secret.
- `url:` Will contain the URL of Vault.
- `sso.accessorID:` Will contain the SSO accessorID.
- `sso.clientName:` Will contain the client name.

For more details please refer [use-cases](./usecases/integrationconfig.md)
