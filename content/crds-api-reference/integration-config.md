# Integration Config

IntegrationConfig is used to configure settings of multi-tenancy for Multi Tenant Operator.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: IntegrationConfig
metadata:
  name: tenant-operator-config
  namespace: multi-tenant-operator
spec:
  components:
    console: true
    showback: true
    ingress:
      IngressClassName: 'nginx'
      Keycloak:
        Host: tenant-operator-keycloak.apps.mycluster-ams.abcdef.cloud
        TLSSecretName: tenant-operator-tls
      Console:
        Host: tenant-operator-console.apps.mycluster-ams.abcdef.cloud
        TLSSecretName: tenant-operator-tls
      Gateway:
        Host: tenant-operator-gateway.apps.mycluster-ams.abcdef.cloud
        TLSSecretName: tenant-operator-tls
  accessControl:
    rbac:
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
    namespaceAccessPolicy:
      deny:
        privilegedNamespaces:
          users:
            - system:serviceaccount:openshift-argocd:argocd-application-controller
            - adam@stakater.com
          groups:
            - cluster-admins
    privileged:
      namespaces:
        - ^default$
        - ^openshift.*
        - ^kube.*
      serviceAccounts:
        - ^system:serviceaccount:openshift.*
        - ^system:serviceaccount:kube.*
      users:
        - ''
      groups:
        - cluster-admins
  metadata:
    groups:
      labels:
        role: customer-reader
      annotations: 
        openshift.io/node-selector: node-role.kubernetes.io/worker=
    namespaces:
      labels:
        stakater.com/workload-monitoring: "true"
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
    sandboxes:
      labels:
        stakater.com/kind: sandbox
      annotations:
        openshift.io/node-selector: node-role.kubernetes.io/worker=
  integrations:
    keycloak:
      realm: mto
      address: https://keycloak.apps.prod.abcdefghi.kubeapp.cloud/
      clientName: mto-console
    argocd:
      clusterResourceWhitelist:
        - group: tronador.stakater.com
          kind: EnvironmentProvisioner
      namespaceResourceBlacklist:
        - group: '' # all groups
          kind: ResourceQuota
      namespace: openshift-operators
    vault:
      enabled: true
      authMethod: kubernetes      #enum: {kubernetes:default, Token}
      accessInfo: 
        accessorPath: oidc/
        address: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
        roleName: mto
        secretRef:       
          name: ''
          namespace: ''
      config: 
        ssoClient: vault
```

Following are the different components that can be used to configure multi-tenancy in a cluster via Multi Tenant Operator.

## Components

```yaml
  components:
    console: true
    showback: true
    ingress:
      IngressClassName: nginx
      Keycloak:
        Host: tenant-operator-keycloak.apps.mycluster-ams.abcdef.cloud
        TLSSecretName: tenant-operator-tls
      Console:
        Host: tenant-operator-console.apps.mycluster-ams.abcdef.cloud
        TLSSecretName: tenant-operator-tls
      Gateway:
        Host: tenant-operator-gateway.apps.mycluster-ams.abcdef.cloud
        TLSSecretName: tenant-operator-tls
```

- `components.console:` Enables or disables the console GUI for MTO.
- `components.showback:` Enables or disables the showback feature on the console.
- `components.ingress:` Configures the ingress settings for various components:
    - `ingressClassName:` Ingress class to be used for the ingress.
    - `console:` Settings for the console's ingress.
        - `host:` hostname for the console's ingress.
        - `tlsSecretName:` Name of the secret containing the TLS certificate and key for the console's ingress.
    - `gateway:` Settings for the gateway's ingress.
        - `host:` hostname for the gateway's ingress.
        - `tlsSecretName:` Name of the secret containing the TLS certificate and key for the gateway's ingress.
    - `keycloak:` Settings for the Keycloak's ingress.
        - `host:` hostname for the Keycloak's ingress.
        - `tlsSecretName:` Name of the secret containing the TLS certificate and key for the Keycloak's ingress.

Here's an example of how to generate the secrets required to configure MTO:

**TLS Secret for Ingress:**  

Create a TLS secret containing your SSL/TLS certificate and key for secure communication. This secret will be used for the Console, Gateway, and Keycloak ingresses.

```bash
kubectl -n multi-tenant-operator create secret tls <tls-secret-name> --key=<path-to-key.pem> --cert=<path-to-cert.pem>
```

Integration config will be managing the following resources required for console GUI:

- `MTO Postgresql` resources.
- `MTO Prometheus` resources.
- `MTO Opencost` resources.
- `MTO Console, Gateway, Keycloak` resources.
- `Showback` cronjob.

Details on console GUI and showback can be found [here](../explanation/console.md)

## Access Control

```yaml
accessControl:
  rbac:
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
  namespaceAccessPolicy:
    deny:
      privilegedNamespaces:
        users:
          - system:serviceaccount:openshift-argocd:argocd-application-controller
          - adam@stakater.com
          groups:
            - cluster-admins
    privileged:
      namespaces:
        - ^default$
        - ^openshift.*
        - ^kube.*
      serviceAccounts:
        - ^system:serviceaccount:openshift.*
        - ^system:serviceaccount:kube.*
      users:
        - ''
      groups:
        - cluster-admins
```

### RBAC

RBAC is used to configure the roles that will be applied to each Tenant namespace. The field allows optional custom roles, that are then used to create RoleBindings for namespaces that match a labelSelector.

#### TenantRoles

TenantRoles are required within the IntegrationConfig, as they are used for defining what roles will be applied to each Tenant namespace. The field allows optional custom roles, that are then used to create RoleBindings for namespaces that match a labelSelector.

> ⚠️ If you do not configure roles in any way, then the default OpenShift roles of `owner`, `edit`, and `view` will apply to Tenant members. Their details can be found [here](../reference-guides/custom-roles.md)

```yaml
rbac:
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

##### Default

This field contains roles that will be used to create default roleBindings for each namespace that belongs to tenants. These roleBindings are only created for a namespace if that namespace isn't already matched by the `custom` field below it. Therefore, it is required to have at least one role mentioned within each of its three subfields: `owner`, `editor`, and `viewer`. These 3 subfields also correspond to the member fields of the [Tenant CR](./tenant.md#tenant)

##### Custom

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

### Namespace Access Policy

Namespace Access Policy is used to configure the namespaces that are allowed to be created by tenants. It also allows the configuration of namespaces that are ignored by MTO.

```yaml
namespaceAccessPolicy:
  deny:
    privilegedNamespaces:
      groups:
        - cluster-admins
      users:
        - system:serviceaccount:openshift-argocd:argocd-application-controller
        - adam@stakater.com
  privileged:
    namespaces:
      - ^default$
      - ^openshift.*
      - ^kube.*
    serviceAccounts:
      - ^system:serviceaccount:openshift.*
      - ^system:serviceaccount:kube.*
    users:
      - ''
    groups:
      - cluster-admins
```

#### Deny

`namespaceAccessPolicy.Deny:` Can be used to restrict privileged *users/groups* CRUD operation over managed namespaces.

#### Privileged

##### Namespaces

`privileged.namespaces:` Contains the list of `namespaces` ignored by MTO. MTO will not manage the `namespaces` in this list. Treatment for privileged namespaces does not involve further integrations or finalizers processing as with normal namespaces. Values in this list are regex patterns.

For example:

- To ignore the `default` namespace, we can specify `^default$`
- To ignore all namespaces starting with the `openshift-` prefix, we can specify `^openshift-.*`.
- To ignore any namespace containing `stakater` in its name, we can specify `^stakater.`. (A constant word given as a regex pattern will match any namespace containing that word.)

##### ServiceAccounts

`privileged.serviceAccounts:` Contains the list of `ServiceAccounts` ignored by MTO. MTO will not manage the `ServiceAccounts` in this list. Values in this list are regex patterns. For example, to ignore all `ServiceAccounts` starting with the `system:serviceaccount:openshift-` prefix, we can use `^system:serviceaccount:openshift-.*`; and to ignore a specific service account like `system:serviceaccount:builder` service account we can use `^system:serviceaccount:builder$.`

!!! note
    `stakater`, `stakater.` and `stakater.*` will have the same effect. To check out the combinations, go to [Regex101](https://regex101.com/), select Golang, and type your expected regex and test string.  

##### Users

`privileged.users:` Contains the list of `users` ignored by MTO. MTO will not manage the `users` in this list. Values in this list are regex patterns.

##### Groups

`privileged.groups:` Contains names of the groups that are allowed to perform CRUD operations on namespaces present on the cluster. Users in the specified group(s) will be able to perform these operations without MTO getting in their way. MTO does not interfere even with the deletion of privilegedNamespaces.

!!! note
    User `kube:admin` is bypassed by default to perform operations as a cluster admin, this includes operations on all the namespaces.

> ⚠️ If you want to use a more complex regex pattern (for the `privileged.namespaces` or `privileged.serviceAccounts` field), it is recommended that you test the regex pattern first -  either locally or using a platform such as <https://regex101.com/>.

## Metadata

```yaml
metadata:
  groups:
    labels:
      role: customer-reader
    annotations: {}
  namespaces:
    labels:
      stakater.com/workload-monitoring: "true"
    annotations:
      openshift.io/node-selector: node-role.kubernetes.io/worker=
  sandboxes:
    labels:
      stakater.com/kind: sandbox
    annotations: {}
```

### Namespaces, group and sandbox

We can use the `metadata.namespaces`, `metadata.group` and `metadata.sandbox` fields to automatically add `labels` and `annotations` to the **Namespaces** and **Groups** managed via MTO.

If we want to add default *labels/annotations* to sandbox namespaces of tenants than we just simply add them in `metadata.namespaces.labels`/`metadata.namespaces.annotations` respectively.

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

## Integrations

Integrations are used to configure the integrations that MTO has with other tools. Currently, MTO supports the following integrations:

```yaml
integrations:
  keycloak:
    realm: mto
    address: https://keycloak.apps.prod.abcdefghi.kubeapp.cloud/
    clientName: mto-console
  argocd:
    clusterResourceWhitelist:
      - group: tronador.stakater.com
        kind: EnvironmentProvisioner
    namespaceResourceBlacklist:
      - group: '' # all groups
        kind: ResourceQuota
    namespace: openshift-operators
  vault:
    enabled: true
    authMethod: kubernetes      #enum: {kubernetes:default, Token}
    accessInfo: 
      accessorPath: oidc/
      address: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
      roleName: mto
      secretRef:       
        name: ''
        namespace: ''
    config: 
      ssoClient: vault
```

### Keycloak

[Keycloak](https://www.keycloak.org/) is an open-source Identity and Access Management solution aimed at modern applications and services. It makes it easy to secure applications and services with little to no code.

If a `Keycloak` instance is already set up within your cluster, configure it for MTO by enabling the following configuration:

```yaml
keycloak:
  realm: mto
  address: https://keycloak.apps.prod.abcdefghi.kubeapp.cloud/
  clientName: mto-console
```

- `keycloak.realm:` The realm in Keycloak where the client is configured.
- `keycloak.address:` The address of the Keycloak instance.
- `keycloak.clientName:` The name of the client in Keycloak.

For more details around enabling Keycloak in MTO, visit [here](../how-to-guides/integrating-external-keycloak.md)

### ArgoCD

[ArgoCD](https://argoproj.github.io/argo-cd/) is a declarative, GitOps continuous delivery tool for Kubernetes. It follows the GitOps pattern of using Git repositories as the source of truth for defining the desired application state. ArgoCD uses Kubernetes manifests and configures the applications on the cluster.

If `argocd` is configured on a cluster, then ArgoCD configuration can be enabled.

```yaml
argocd:
  enabled: bool
  clusterResourceWhitelist:
    - group: tronador.stakater.com
      kind: EnvironmentProvisioner
  namespaceResourceBlacklist:
    - group: '' # all groups
      kind: ResourceQuota
  namespace: openshift-operators
```

- `argocd.clusterResourceWhitelist` allows ArgoCD to sync the listed cluster scoped resources from your GitOps repo.
- `argocd.namespaceResourceBlacklist` prevents ArgoCD from syncing the listed resources from your GitOps repo.
- `argocd.namespace` is an optional field used to specify the namespace where ArgoCD Applications and AppProjects are deployed. The field should be populated when you want to create an ArgoCD AppProject for each tenant.

### Vault

[Vault](https://www.vaultproject.io/) is used to secure, store and tightly control access to tokens, passwords, certificates, encryption keys for protecting secrets and other sensitive data using a UI, CLI, or HTTP API.

If `vault` is configured on a cluster, then Vault configuration can be enabled.

```yaml
vault:
  enabled: true
  authMethod: kubernetes      #enum: {kubernetes:default, token}
  accessInfo: 
    accessorPath: oidc/
    address: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
    roleName: mto
    secretRef:
      name: ''
      namespace: ''
  config: 
    ssoClient: vault
```

If enabled, then admins have to specify the `authMethod` to be used for authentication. MTO supports two authentication methods:

- `kubernetes`: This is the default authentication method. It uses the Kubernetes authentication method to authenticate with Vault.
- `token`: This method uses a Vault token to authenticate with Vault.

#### AuthMethod - Kubernetes

If `authMethod` is set to `kubernetes`, then admins have to specify the following fields:

- `accessorPath:` Accessor Path within Vault to fetch SSO accessorID
- `address:` Valid Vault address reachable within cluster.
- `roleName:` Vault's Kubernetes authentication role
- `sso.clientName:` SSO client name.

#### AuthMethod - Token

If `authMethod` is set to `token`, then admins have to specify the following fields:

- `accessorPath:` Accessor Path within Vault to fetch SSO accessorID
- `address:` Valid Vault address reachable within cluster.
- `secretRef:` Secret containing Vault token.
    - `name:` Name of the secret containing Vault token.
    - `namespace:` Namespace of the secret containing Vault token.

For more details around enabling Kubernetes auth in Vault, visit [here](https://developer.hashicorp.com/vault/docs/auth/kubernetes)

The role created within Vault for Kubernetes authentication should have the following permissions:

```hcl
path "secret/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "sys/mounts" {
  capabilities = ["read", "list"]
}
path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "managed-addons/*" {
  capabilities = ["read", "list"]
}
path "auth/kubernetes/role/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "sys/auth" {
  capabilities = ["read", "list"]
}
path "sys/policies/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "identity/group" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "identity/group-alias" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
path "identity/group/name/*" {
  capabilities = ["read", "list"]
}
path "identity/group/id/*" {
  capabilities = ["create", "read", "update", "patch", "delete", "list"]
}
```

### Custom Pricing Model

You can modify IntegrationConfig to customise the default pricing model. Here is what you need at `IntegrationConfig.spec.components`:

```yaml
components:
    console: true # should be enabled
    showback: true # should be enabled
    # add below and override any default value
    # you can also remove the ones you do not need
    customPricingModel:
        CPU: "0.031611"
        spotCPU: "0.006655"
        RAM: "0.004237"
        spotRAM: "0.000892"
        GPU: "0.95"
        storage: "0.00005479452"
        zoneNetworkEgress: "0.01"
        regionNetworkEgress: "0.01"
        internetNetworkEgress: "0.12"
```

After modifying your default IntegrationConfig in `multi-tenant-operator` namespace, a configmap named `opencost-custom-pricing` will be updated. You will be able to see updated pricing info in `mto-console`.
