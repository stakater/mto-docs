<!-- markdownlint-disable -->
# API Reference

## Packages
- [tenantoperator.stakater.com/v1alpha1](#tenantoperatorstakatercomv1alpha1)
- [tenantoperator.stakater.com/v1beta1](#tenantoperatorstakatercomv1beta1)
- [tenantoperator.stakater.com/v1beta3](#tenantoperatorstakatercomv1beta3)


## tenantoperator.stakater.com/v1alpha1

Package v1alpha1 contains API Schema definitions for the tenantoperator v1alpha1 API group

### Resource Types
- [Extensions](#extensions)
- [IntegrationConfig](#integrationconfig)



#### AppProjectConfig



AppProject contains details about argocd AppProjects



_Appears in:_
- [ArgoCDConfig](#argocdconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `sourceRepos` _string array_ | SourceRepos contains list of repository URLs which can be used for deployment |  |  |
| `namespaceResourceBlacklist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | NamespaceResourceBlacklist contains list of blacklisted namespace level resources |  |  |
| `clusterResourceWhitelist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | ClusterResourceWhitelist contains list of whitelisted cluster level resources |  |  |


#### ArgoCD







_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespace` _Namespace_ | Namespace should contain the name of the namespace in which to deploy ArgoCD AppProjects |  | Required: \{\} <br /> |
| `namespaceResourceBlacklist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | NamespaceResourceBlacklist contains list of blacklisted namespace level resources |  |  |
| `clusterResourceWhitelist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | ClusterResourceWhitelist contains list of whitelisted cluster level resources |  |  |


#### ArgoCDConfig



ArgoCDConfig contains details about source repositories and AppProjects



_Appears in:_
- [ExtensionsSpec](#extensionsspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `appProject` _[AppProjectConfig](#appprojectconfig)_ | AppProject contains details about argocd AppProjects |  |  |
| `onDeletePurgeAppProject` _boolean_ | OnDeletePurgeAppProject is used to enable or disable the AppProject purge feature |  | Optional: \{\} <br /> |


#### ArgoCDConfigStatus



ArgoCDStatus defines the observed state of the ArgoCD extension



_Appears in:_
- [ExtensionsStatus](#extensionsstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `appProjectState` _boolean_ |  |  |  |
| `argoNamespace` _string_ |  |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ |  |  |  |


#### Endpoint



Endpoint is used to connect to an application



_Appears in:_
- [ManagedApp](#managedapp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `url` _string_ |  |  |  |
| `secretReference` _[SecretReference](#secretreference)_ |  |  |  |


#### Extensions



Extensions is the Schema for the extensions API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1alpha1` | | |
| `kind` _string_ | `Extensions` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[ExtensionsSpec](#extensionsspec)_ |  |  |  |
| `status` _[ExtensionsStatus](#extensionsstatus)_ |  |  |  |


#### ExtensionsSpec



ExtensionsSpec defines the desired state of Extensions



_Appears in:_
- [Extensions](#extensions)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tenantName` _string_ | TenantName is the name of the tenant to which the extension belongs |  | Required: \{\} <br /> |
| `argoCD` _[ArgoCDConfig](#argocdconfig)_ | ArgoCDConfig defines ArgoCD configurations for the tenant |  |  |


#### ExtensionsStatus



ExtensionsStatus defines the observed state of Extensions



_Appears in:_
- [Extensions](#extensions)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `argocd` _[ArgoCDConfigStatus](#argocdconfigstatus)_ |  |  |  |


#### Ingress







_Appears in:_
- [IngressConfig](#ingressconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host specifies the hostname for the ingress |  |  |
| `tlsSecretName` _string_ | TLSSecretName is the name of the secret containing the TLS certificate |  | Optional: \{\} <br /> |


#### IngressConfig







_Appears in:_
- [Provision](#provision)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keycloak` _[Ingress](#ingress)_ |  |  |  |
| `console` _[Ingress](#ingress)_ |  |  |  |
| `gateway` _[Ingress](#ingress)_ |  |  |  |
| `ingressClassName` _string_ | ingressClassName is the ingress class name |  | Optional: \{\} <br /> |


#### IntegrationConfig



IntegrationConfig is the Schema for the integrationConfigs API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1alpha1` | | |
| `kind` _string_ | `IntegrationConfig` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[IntegrationConfigSpec](#integrationconfigspec)_ |  |  |  |
| `status` _[IntegrationConfigStatus](#integrationconfigstatus)_ |  |  |  |


#### IntegrationConfigSpec



IntegrationConfigSpec defines the desired state of IntegrationConfig



_Appears in:_
- [IntegrationConfig](#integrationconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `openshift` _[OpenshiftConfig](#openshiftconfig)_ | Openshift is the config containing labels and annotations |  |  |
| `tenantRoles` _[TenantRoles](#tenantroles)_ | TenantRoles sets the default Owner/Editor/Viewer and/or custom roles for each tenant | \{ default:map[editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]]] \} |  |
| `nexus` _[ManagedNexus](#managednexus)_ | Nexus is the config for managed Nexus. |  |  |
| `rhsso` _[ManagedRHSSO](#managedrhsso)_ | Nexus is the config for managed RHSSO. |  |  |
| `vault` _[ManagedVault](#managedvault)_ | Nexus is the config for managed Vault. |  |  |
| `argocd` _[ArgoCD](#argocd)_ | ArgoCD contains details about argocd Applications and AppProjects |  |  |
| `provision` _[Provision](#provision)_ | Provision is used to enable/disable the provision feature such as mto-console and showback | \{ console:true showback:true \} |  |


#### IntegrationConfigStatus



IntegrationConfigStatus defines the observed state of IntegrationConfig



_Appears in:_
- [IntegrationConfig](#integrationconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `roleBindingsToDelete` _object (keys:string, values:string array)_ | RoleBindingsToDelete contains all of the rolebindings that have been whenever the roles cache config map gets updated |  |  |


#### ManagedApp



ManagedApp is the config for a managed application.



_Appears in:_
- [ManagedNexus](#managednexus)
- [ManagedRHSSO](#managedrhsso)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ |  | false |  |
| `endpoint` _[Endpoint](#endpoint)_ |  |  |  |
| `sso` _[SSO](#sso)_ |  |  |  |


#### ManagedNexus



ManagedNexus is the config for Nexus.



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ManagedApp` _[ManagedApp](#managedapp)_ |  |  |  |


#### ManagedRHSSO



ManagedRHSSO is the config for RedHat Single Sign-On.



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ManagedApp` _[ManagedApp](#managedapp)_ |  |  |  |
| `realm` _string_ |  |  |  |


#### ManagedVault



ManagedVault is the config for Vault.



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ |  | false |  |
| `address` _string_ |  |  |  |
| `accessorPath` _string_ |  |  |  |
| `roleName` _string_ |  |  |  |
| `sso` _[VaultSSO](#vaultsso)_ |  |  |  |


#### MatchNamespaceLabel







_Appears in:_
- [TenantRoles](#tenantroles)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labelSelector` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#labelselector-v1-meta)_ | LabelSelector is the label selector that will be used to find namespaces to apply roles to |  |  |
| `UserRoles` _[UserRoles](#userroles)_ | Custom roles applied to the namespaces selected by the label selector |  | Required: \{\} <br /> |


#### Metadata







_Appears in:_
- [OpenshiftConfig](#openshiftconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labels` _object (keys:string, values:string)_ |  |  |  |
| `annotations` _object (keys:string, values:string)_ |  |  |  |


#### NamespaceAccessPolicy



NamespaceAccessPolicy contains access and deny policies for namespaces



_Appears in:_
- [OpenshiftConfig](#openshiftconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deny` _[Policy](#policy)_ |  |  |  |


#### OpenshiftConfig



OpenshiftConfig is the config containing labels and annotations



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `project` _[Metadata](#metadata)_ | Project contains labels and annotations applied to the namespace |  |  |
| `group` _[Metadata](#metadata)_ | Group contains labels and annotations applied to the group |  |  |
| `sandbox` _[Metadata](#metadata)_ | Sandbox contains labels and annotations applied to the sandbox |  |  |
| `privilegedNamespaces` _string array_ | PrivilegedNamespaces contains list of privileged namespaces regex |  |  |
| `privilegedServiceAccounts` _string array_ | PrivilegedServiceAccounts contains list of privileged serviceAccounts regex |  |  |
| `namespaceAccessPolicy` _[NamespaceAccessPolicy](#namespaceaccesspolicy)_ | NamespaceAccessPolicy contains groups/users which are denied access over managed namespaces |  |  |
| `clusterAdminGroups` _string array_ | ClusterAdminGroups contains groups which are admins of tenants |  |  |


#### Policy



Policy contains policies relating to privilegedNamespaces



_Appears in:_
- [NamespaceAccessPolicy](#namespaceaccesspolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `privilegedNamespaces` _[PrivilegedNamespaces](#privilegednamespaces)_ |  |  |  |


#### PolicyMembers







_Appears in:_
- [PrivilegedNamespaces](#privilegednamespaces)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


#### PrivilegedNamespaces



PrivilegedNamespaces contains groups/users



_Appears in:_
- [Policy](#policy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


#### Provision







_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `console` _boolean_ | Console is used to enable/disable the mto-console | true | Optional: \{\} <br /> |
| `showback` _boolean_ | Showback is used to enable/disable the showback feature | true | Optional: \{\} <br /> |
| `ingress` _[IngressConfig](#ingressconfig)_ | the following are used to configure the ingress for the provisioned services |  |  |
| `trustedRootCert` _string_ | TrustedRootCert is the name of the secret containing the trusted root CA certificate<br />This certificate is used for SSL/TLS communication with other services |  | Optional: \{\} <br /> |


#### SSO



SSO contains details for single sign on



_Appears in:_
- [ManagedApp](#managedapp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clientName` _string_ |  |  |  |
| `accessorID` _string_ |  |  |  |


#### SecretReference



SecretReference contains details of a secret



_Appears in:_
- [Endpoint](#endpoint)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |
| `namespace` _string_ |  |  |  |


#### TenantRoles



TenantRoles is used to configure custom RBAC rules for tenants



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `default` _[UserRoles](#userroles)_ | DefaultRoles contains the default roles that will be applied to each tenant. Required field. | \{ editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]] \} |  |
| `custom` _[MatchNamespaceLabel](#matchnamespacelabel) array_ | CustomRoles is an optional Label selector method to apply roles to specific namespaces.<br />These roles will override the existing Default Roles |  |  |


#### UserRoles



UserRoles is the list of roles applied to owners/editors/viewers



_Appears in:_
- [MatchNamespaceLabel](#matchnamespacelabel)
- [TenantRoles](#tenantroles)



#### VaultSSO







_Appears in:_
- [ManagedVault](#managedvault)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clientName` _string_ |  |  |  |



## tenantoperator.stakater.com/v1beta1

Package v1beta1 contains API Schema definitions for the tenantoperator v1beta1 API group

### Resource Types
- [IntegrationConfig](#integrationconfig)
- [Quota](#quota)



#### AccessControl



AccessControl defines the access control settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `rbac` _[RBAC](#rbac)_ |  | \{ tenantRoles:map[default:map[editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]]]] \} |  |
| `namespaceAccessPolicy` _[NamespaceAccessPolicy](#namespaceaccesspolicy)_ |  |  |  |
| `privileged` _[Privileged](#privileged)_ |  |  |  |


#### ArgoCDIntegration



ArgoCD defines the ArgoCD integration settings



_Appears in:_
- [Integrations](#integrations)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clusterResourceWhitelist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | ClusterResourceWhitelist contains list of whitelisted cluster level resources |  |  |
| `namespaceResourceBlacklist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | NamespaceResourceWhitelist contains list of whitelisted namespace level resources |  |  |
| `namespace` _Namespace_ | Namespace should contain the name of the namespace in which to deploy ArgoCD AppProjects |  | Required: \{\} <br /> |


#### Components



Components defines the components settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `console` _boolean_ |  | false |  |
| `showback` _boolean_ |  | false |  |
| `showbackOpts` _[ShowbackOpts](#showbackopts)_ | ShowbackOpts is used to configure the showback for the Component<br />ShowbackOpts is deprecated and will be removed in a future release. See docs.stakater.com/mto/latest for more details on the replacement for showback configuration. |  |  |
| `ingress` _[IngressConfig](#ingressconfig)_ | the following are used to configure the ingress for the Component's services |  |  |
| `prometheus` _[PrometheusComponentConfig](#prometheuscomponentconfig)_ | Defines configuration for prometheus component |  | Optional: \{\} <br /> |
| `opencost` _[OpenCostComponentConfig](#opencostcomponentconfig)_ | Defines configuration for opencost component |  | Optional: \{\} <br /> |
| `postgres` _[PostgresComponentConfig](#postgrescomponentconfig)_ | Defines configuration for postgres component |  | Optional: \{\} <br /> |
| `dex` _[DexComponentConfig](#dexcomponentconfig)_ | Defines configuration for dex component |  | Optional: \{\} <br /> |
| `finopsOperator` _[FinOpsOperator](#finopsoperator)_ | Defines configuration for finops operator component |  | Optional: \{\} <br /> |
| `dexConfigOperator` _[DexConfigOperatorConfig](#dexconfigoperatorconfig)_ | Defines configuration for dex config operator component |  | Optional: \{\} <br /> |




#### Custom







_Appears in:_
- [ShowbackOpts](#showbackopts)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `CPU` _string_ |  |  |  |
| `spotCPU` _string_ |  |  |  |
| `RAM` _string_ |  |  |  |
| `spotRAM` _string_ |  |  |  |
| `GPU` _string_ |  |  |  |
| `storage` _string_ |  |  |  |
| `zoneNetworkEgress` _string_ |  |  |  |
| `regionNetworkEgress` _string_ |  |  |  |
| `internetNetworkEgress` _string_ |  |  |  |
| `provider` _string_ |  |  |  |
| `description` _string_ |  |  |  |
| `projectId` _string_ |  |  |  |
| `awsSpotDataBucket` _string_ |  |  |  |
| `awsSpotDataRegion` _string_ |  |  |  |
| `awsSpotDataPrefix` _string_ |  |  |  |
| `spotLabel` _string_ |  |  |  |
| `spotLabelValue` _string_ |  |  |  |


#### Deny



Deny defines the deny settings for namespace access policy



_Appears in:_
- [NamespaceAccessPolicy](#namespaceaccesspolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `privilegedNamespaces` _[PrivilegedNamespaces](#privilegednamespaces)_ |  |  |  |


#### DependencyMode

_Underlying type:_ _string_

DependencyMode describes how a dependency is provided

_Validation:_
- Enum: [Managed External]

_Appears in:_
- [DexComponentConfig](#dexcomponentconfig)
- [OpenCostComponentConfig](#opencostcomponentconfig)
- [PostgresComponentConfig](#postgrescomponentconfig)
- [PrometheusComponentConfig](#prometheuscomponentconfig)

| Field | Description |
| --- | --- |
| `Managed` | DependencyModeManaged indicates the operator should provision and manage the dependency<br /> |
| `External` | DependencyModeExternal indicates the dependency is supplied by the user<br /> |


#### DexComponentConfig







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Prometheus Helm chart values when mode is Managed |  |  |
| `external` _[DexExternalConfig](#dexexternalconfig)_ | External defines information required when using an externally managed Dex deployment |  |  |


#### DexConfigOperatorConfig







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Prometheus Helm chart values |  |  |


#### DexExternalConfig







_Appears in:_
- [DexComponentConfig](#dexcomponentconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `issuer` _string_ | Issuer is the URL of the Dex issuer, used for OIDC discovery |  |  |


#### ExternalServerConfig



ExternalServerConfig stores references to an external Prometheus deployment



_Appears in:_
- [OpenCostComponentConfig](#opencostcomponentconfig)
- [PrometheusComponentConfig](#prometheuscomponentconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `serverURL` _string_ | ServerURL is the base URL that the operator should use for query API access |  |  |


#### FinOpsOperator



FinOpsOperator defines the configuration for FinOps Operator components
See https://docs.stakater.com/finops-operator/latest for more details



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the FinOps Operator Helm chart values when mode is Managed |  | Optional: \{\} <br /> |




#### Ingress







_Appears in:_
- [IngressConfig](#ingressconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host specifies the hostname for the ingress (legacy per-component mode). |  |  |
| `tlsSecretName` _string_ | TLSSecretName is the name of the secret containing the TLS certificate. |  | Optional: \{\} <br /> |
| `path` _string_ | Path is the path prefix under the shared host in consolidated mode.<br />Defaults: Console "/", Gateway "/gateway", Dex "/dex", FinOps "/finops". |  | Optional: \{\} <br /> |


#### IngressConfig







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host, when set, enables consolidated mode: all components are served under<br />this single shared hostname via distinct path prefixes. When empty, the<br />per-component Console/Gateway/Dex/FinOpsGateway hosts are used (legacy). |  | Optional: \{\} <br /> |
| `tlsSecretName` _string_ | TLSSecretName is the TLS secret for the shared host (consolidated mode). |  | Optional: \{\} <br /> |
| `console` _[Ingress](#ingress)_ |  |  |  |
| `gateway` _[Ingress](#ingress)_ |  |  |  |
| `dex` _[Ingress](#ingress)_ |  |  |  |
| `finopsGateway` _[Ingress](#ingress)_ |  |  |  |
| `ingressClassName` _string_ | ingressClassName is the ingress class name |  | Optional: \{\} <br /> |


#### IntegrationConfig



IntegrationConfig is the Schema for the integrationconfigs API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1beta1` | | |
| `kind` _string_ | `IntegrationConfig` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[IntegrationConfigSpec](#integrationconfigspec)_ |  |  |  |
| `status` _[IntegrationConfigStatus](#integrationconfigstatus)_ |  |  |  |


#### IntegrationConfigSpec



IntegrationConfigSpec defines the desired state of IntegrationConfig



_Appears in:_
- [IntegrationConfig](#integrationconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `accessControl` _[AccessControl](#accesscontrol)_ |  | \{ rbac:map[tenantRoles:map[default:map[editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]]]]] \} |  |
| `components` _[Components](#components)_ |  |  |  |
| `metadata` _[Metadata](#metadata)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `integrations` _[Integrations](#integrations)_ |  |  |  |
| `tenantPolicies` _[TenantPolicies](#tenantpolicies)_ |  |  |  |


#### IntegrationConfigStatus



IntegrationConfigStatus defines the observed state of IntegrationConfig



_Appears in:_
- [IntegrationConfig](#integrationconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `roleBindingsToDelete` _object (keys:string, values:string array)_ |  |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Status conditions |  |  |


#### Integrations



Integrations defines the integration settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `argocd` _[ArgoCDIntegration](#argocdintegration)_ |  |  |  |
| `vault` _[VaultIntegration](#vaultintegration)_ |  |  |  |




#### MatchNamespaceLabel







_Appears in:_
- [TenantRoles](#tenantroles)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labelSelector` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#labelselector-v1-meta)_ | LabelSelector is the label selector that will be used to find namespaces to apply roles to |  |  |
| `UserRoles` _[UserRoles](#userroles)_ | Custom roles applied to the namespaces selected by the label selector |  |  |


#### Metadata



Metadata defines the metadata settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `groups` _[MetadataType](#metadatatype)_ | Groups contains labels and annotations applied to the groups |  |  |
| `namespaces` _[MetadataType](#metadatatype)_ | Namespaces contains labels and annotations applied to the namespaces |  |  |
| `sandboxes` _[MetadataType](#metadatatype)_ | Sandboxes contains labels and annotations applied to the sandbox |  |  |


#### MetadataType







_Appears in:_
- [Metadata](#metadata)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labels` _object (keys:string, values:string)_ |  |  |  |
| `annotations` _object (keys:string, values:string)_ |  |  |  |


#### NamespaceAccessPolicy



NamespaceAccessPolicy defines the namespace access policy settings



_Appears in:_
- [AccessControl](#accesscontrol)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deny` _[Deny](#deny)_ |  |  |  |




#### OpenCostComponentConfig



OpenCostComponentConfig describes how OpenCost is configured for showback features



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the OpenCost Helm chart values when mode is Managed |  |  |
| `external` _[ExternalServerConfig](#externalserverconfig)_ | External defines information required when using an externally managed OpenCost deployment |  |  |


#### PolicyRule



PolicyRule defines the policy rule



_Appears in:_
- [VaultPolicy](#vaultpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `path` _string_ | Path is the path to the resource |  |  |
| `capabilities` _string array_ | Capabilities is the list of capabilities |  |  |


#### PostgresComponentConfig



PostgresComponentConfig describes how Postgres is configured for application persistence



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Postgres Helm chart values when mode is Managed |  |  |
| `external` _[PostgresExternalConfig](#postgresexternalconfig)_ | External defines information required when using an externally managed Postgres instance |  |  |


#### PostgresExternalConfig



PostgresExternalConfig stores references to an external Postgres instance



_Appears in:_
- [PostgresComponentConfig](#postgrescomponentconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `secretRef` _[SecretRef](#secretref)_ | SecretRef references a secret containing a DSN or discrete connection details |  |  |


#### Privileged



Privileged defines the privileged settings for IntegrationConfig



_Appears in:_
- [AccessControl](#accesscontrol)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespaces` _string array_ |  |  |  |
| `serviceAccounts` _string array_ |  |  |  |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


#### PrivilegedNamespaces



PrivilegedNamespaces defines the list of privileged namespaces and associated users/groups



_Appears in:_
- [Deny](#deny)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


#### PrometheusComponentConfig



PrometheusComponentConfig describes how Prometheus is configured for tenant operations



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Prometheus Helm chart values when mode is Managed |  |  |
| `external` _[ExternalServerConfig](#externalserverconfig)_ | External defines information required when using an externally managed Prometheus |  |  |


#### Quota



Quota is the Schema for the quotas API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1beta1` | | |
| `kind` _string_ | `Quota` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[QuotaSpec](#quotaspec)_ |  |  |  |
| `status` _[QuotaStatus](#quotastatus)_ |  |  |  |


#### QuotaSpec







_Appears in:_
- [Quota](#quota)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resourcequota` _[ResourceQuotaSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#resourcequotaspec-v1-core)_ | ResourceQuota defines the allocated ResourceQuota for the tenant |  |  |
| `limitrange` _[LimitRangeSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#limitrangespec-v1-core)_ | LimitRange defines the allocated LimitRange for the namespace inside tenant |  | Optional: \{\} <br /> |


#### QuotaStatus



QuotaStatus defines the observed state of Quota



_Appears in:_
- [Quota](#quota)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `TenantQuotaStatus` _[TenantQuotaStatus](#tenantquotastatus)_ |  |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Status conditions for quota |  |  |


#### RBAC



RBAC defines the RBAC settings for IntegrationConfig



_Appears in:_
- [AccessControl](#accesscontrol)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tenantRoles` _[TenantRoles](#tenantroles)_ | TenantRoles sets the default Owner/Editor/Viewer and/or custom roles for each tenant | \{ default:map[editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]]] \} |  |




#### SecretRef



SecretReference defines the reference to a secret



_Appears in:_
- [PostgresExternalConfig](#postgresexternalconfig)
- [ShowbackOpts](#showbackopts)
- [VaultAccessInfo](#vaultaccessinfo)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |
| `namespace` _string_ |  |  |  |


#### ShowbackOpts







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `custom` _[Custom](#custom)_ | Custom is used to define custom pricing for opencost. If not provided, the default pricing will be used.<br />Custom field is deprecated and will be removed in a future release. Please use the spec.components.finopsOperator.priceBook field instead to configure custom pricing for OpenCost. |  | Optional: \{\} <br /> |
| `cloudPricingSecretRef` _[SecretRef](#secretref)_ | CloudPricingSecretRef is the reference to the secret containing the opeconst config for AWS/Azure.<br />This field is deprecated and will be removed in a future release. Please use the spec.components.opencost.cloudIntegrationSecret field instead to configure the cloud integration for OpenCost. |  | Optional: \{\} <br /> |
| `retentionPeriod` _string_ | RetentionPeriod defines the retention period of prometheus server<br />This field is deprecated and will be removed in a future release. Please use the spec.components.prometheus.retention field instead to configure the retention period for Prometheus. | 7d |  |


#### TenantPolicies







_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `network` _[TenantPoliciesNetwork](#tenantpoliciesnetwork)_ |  |  |  |


#### TenantPoliciesNetwork







_Appears in:_
- [TenantPolicies](#tenantpolicies)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `disableIntraTenantNetworking` _boolean_ |  |  |  |
| `disableNodePortServices` _boolean_ |  |  |  |
| `disableHostPorts` _boolean_ |  |  |  |


#### TenantQuotaStatus







_Appears in:_
- [QuotaStatus](#quotastatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tenants` _object (keys:string, values:[TenantResourceStatus](#tenantresourcestatus))_ |  |  |  |


#### TenantResourceStatus







_Appears in:_
- [TenantQuotaStatus](#tenantquotastatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `status` _[ResourceQuotaStatus](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#resourcequotastatus-v1-core)_ |  |  |  |


#### TenantRoles







_Appears in:_
- [RBAC](#rbac)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `default` _[UserRoles](#userroles)_ | DefaultRoles contains the default roles that will be applied to each tenant. Required field. | \{ editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]] \} |  |
| `custom` _[MatchNamespaceLabel](#matchnamespacelabel) array_ | CustomRoles is an optional Label selector method to apply roles to specific namespaces.<br />These roles will override the existing Default Roles |  |  |


#### UserRoles







_Appears in:_
- [MatchNamespaceLabel](#matchnamespacelabel)
- [TenantRoles](#tenantroles)



#### VaultAccessInfo



VaultAccessInfo defines the access information for Vault



_Appears in:_
- [VaultIntegration](#vaultintegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `accessorPath` _string_ |  |  |  |
| `address` _string_ |  |  |  |
| `roleName` _string_ |  |  |  |
| `secretRef` _[SecretRef](#secretref)_ |  |  |  |


#### VaultConfig



VaultConfig defines the Vault configuration



_Appears in:_
- [VaultIntegration](#vaultintegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ssoClient` _string_ |  |  |  |
| `commonSecretsPath` _string_ | CommonSecretsPath defines a secrets path in Vault which is shared by all tenants |  | Optional: \{\} <br /> |


#### VaultIntegration



Vault defines the Vault integration settings



_Appears in:_
- [Integrations](#integrations)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ |  | false |  |
| `authMethod` _string_ | AuthMethod defines the authentication method for Vault, Possible values are: "kubernetes", "token" | kubernetes | Enum: [kubernetes token] <br /> |
| `accessInfo` _[VaultAccessInfo](#vaultaccessinfo)_ | AccessInfo defines the access information for Vault |  |  |
| `config` _[VaultConfig](#vaultconfig)_ | Config defines the Vault configuration |  |  |
| `policies` _[VaultPolicy](#vaultpolicy) array_ | Policies defines custom Vault policies |  | Optional: \{\} <br /> |


#### VaultPolicy



VaultPolicy defines the Vault policy details



_Appears in:_
- [VaultIntegration](#vaultintegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the name of the policy |  |  |
| `rules` _[PolicyRule](#policyrule) array_ | Rules is the policy rules |  |  |
| `tenantRoles` _string array_ | TenantRoles is the list of tenant roles to apply the policy to |  |  |



## tenantoperator.stakater.com/v1beta3

Package v1beta3 contains API Schema definitions for the tenantoperator v1beta3 API group

### Resource Types
- [Tenant](#tenant)



#### AccessControl







_Appears in:_
- [TenantSpec](#tenantspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `owners` _Members_ | owners represents the list of owners |  |  |
| `editors` _Members_ | editors represents the list of editors |  |  |
| `viewers` _Members_ | viewers represents the list of viewers |  |  |


#### HostValidationConfig







_Appears in:_
- [TenantSpec](#tenantspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `denyWildcards` _boolean_ | DenyWildcards indicates whether wildcard host names are allowed or not<br />If true, wildcard host names are not allowed<br />If false, wildcard host names are allowed | false | Optional: \{\} <br />Type: boolean <br /> |
| `allowedRegex` _string_ | AllowedRegex is a regular expression that defines the allowed host names<br />If specified, host names must match this regex to be allowed |  | Optional: \{\} <br />Type: string <br /> |
| `allowed` _string array_ | Allowed is a list of allowed host names<br />If specified, host names must be in this list to be allowed |  | Optional: \{\} <br />Type: array <br /> |


#### IngressClassEntry







_Appears in:_
- [IngressClassStatus](#ingressclassstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


#### IngressClassStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[IngressClassEntry](#ingressclassentry) array_ |  |  |  |


#### Metadata







_Appears in:_
- [Namespaces](#namespaces)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `common` _[Metadata](#metadata)_ | commonmetadata applies given labels and annotations |  |  |
| `sandbox` _[Metadata](#metadata)_ | sandboxmetadata applies given labels and annotation across sandbox namespaces |  |  |
| `specific` _MetadataOnNamespaces array_ | specificmetadata applies given labels and annotation across specific namespaces |  |  |


#### Namespaces







_Appears in:_
- [TenantSpec](#tenantspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `sandboxes` _[Sandboxes](#sandboxes)_ | sandboxes is used to enable or disable the sandbox feature |  |  |
| `withoutTenantPrefix` _Namespace array_ | WithoutTenantPrefix will create new namespaces mentioned in it |  |  |
| `withTenantPrefix` _Namespace array_ | WithTenantPrefix will create new namespaces mentioned in it and add a prefix of the tenant name to them |  |  |
| `onDeletePurgeNamespaces` _boolean_ | ondeletepurgenamespaces is used to enable or disable the namespace purge feature | false |  |
| `metadata` _[Metadata](#metadata)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |


#### NamespacesStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `commonStatus` _[Metadata](#metadata)_ | CommonStatus stores the previous state of labels and annotation applied across all tenant namespaces, if mentioned in spec |  |  |
| `sandboxStatus` _[Metadata](#metadata)_ | SandboxStatus stores the previous state of labels and annotation applied across all sandbox namespaces, if mentioned in spec |  |  |
| `specificStatus` _MetadataOnNamespaces array_ | SpecificStatus stores the previous state of labels and annotations applied across specific tenant namespaces, if mentioned in spec |  |  |


#### PodPriorityClassEntry







_Appears in:_
- [PodPriorityClassStatus](#podpriorityclassstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


#### PodPriorityClassStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[PodPriorityClassEntry](#podpriorityclassentry) array_ |  |  |  |


#### QuotaEntry







_Appears in:_
- [QuotaStatus](#quotastatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


#### QuotaStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[QuotaEntry](#quotaentry) array_ |  |  |  |


#### Sandboxes







_Appears in:_
- [Namespaces](#namespaces)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | enabled is used to enable or disable the sandbox feature |  |  |
| `private` _boolean_ | private is used to enable or disable the private sandbox feature |  |  |


#### StorageClassEntry







_Appears in:_
- [StorageStatus](#storagestatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


#### StorageStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[StorageClassEntry](#storageclassentry) array_ |  |  |  |


#### Tenant



Tenant is the Schema for the tenants API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1beta3` | | |
| `kind` _string_ | `Tenant` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[TenantSpec](#tenantspec)_ |  |  |  |
| `status` _[TenantStatus](#tenantstatus)_ |  |  |  |


#### TenantSpec



TenantSpec defines the desired state of Tenant



_Appears in:_
- [Tenant](#tenant)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `quota` _string_ | Quota field is used to link relevant Tenant Operator Quota CR |  | Required: \{\} <br /> |
| `accessControl` _[AccessControl](#accesscontrol)_ | AccessControl defines the list of admins, editors and viewers |  |  |
| `namespaces` _[Namespaces](#namespaces)_ | namespaces defines namespaces and their metadata |  |  |
| `desc` _string_ | Desc can contains description about the tenant |  |  |
| `hostValidationConfig` _[HostValidationConfig](#hostvalidationconfig)_ | HostValidationConfig defines the allowed ingress and route host names for the tenant |  | Optional: \{\} <br /> |


#### TenantStatus



TenantStatus defines the observed state of Tenant



_Appears in:_
- [Tenant](#tenant)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespaces` _[NamespacesStatus](#namespacesstatus)_ | namespacesStatus stores the previous state of namespaces, if mentioned in spec |  |  |
| `sandboxState` _boolean_ | SandboxState stores the previous state of sandbox field, if mentioned in spec |  |  |
| `deployedSandboxes` _object (keys:string, values:string)_ | DeployedSandboxes has the map for created sandbox environments so they can be synced with spec |  |  |
| `deployedNamespaces` _string array_ | DeployedNamespaces has the string for created namespaces so they can be synced with spec |  |  |
| `storageClasses` _[StorageStatus](#storagestatus)_ | StorageClasses is the status for currently available StorageClasses for the tenant |  |  |
| `ingressClasses` _[IngressClassStatus](#ingressclassstatus)_ | IngressClasses is the status for currently available IngressClasses for the tenant |  |  |
| `podPriorityClasses` _[PodPriorityClassStatus](#podpriorityclassstatus)_ | PodPriorityClasses is the status for currently available PodPriorityClasses for the tenant |  |  |
| `quota` _[QuotaStatus](#quotastatus)_ | Quota is the status for the tenant's Quota |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Status conditions for tenant |  |  |


