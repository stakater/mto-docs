# API Reference

## Tenant Operator

<!-- markdownlint-disable -->

### Packages
- [tenantoperator.stakater.com/v1alpha1](#tenantoperatorstakatercomv1alpha1)
- [tenantoperator.stakater.com/v1beta1](#tenantoperatorstakatercomv1beta1)
- [tenantoperator.stakater.com/v1beta3](#tenantoperatorstakatercomv1beta3)


### tenantoperator.stakater.com/v1alpha1

Package v1alpha1 contains API Schema definitions for the tenantoperator v1alpha1 API group

#### Resource Types
- [Extensions](#extensions)
- [IntegrationConfig](#integrationconfig)



##### AppProjectConfig



AppProject contains details about argocd AppProjects



_Appears in:_
- [ArgoCDConfig](#argocdconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `sourceRepos` _string array_ | SourceRepos contains list of repository URLs which can be used for deployment |  |  |
| `namespaceResourceBlacklist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | NamespaceResourceBlacklist contains list of blacklisted namespace level resources |  |  |
| `clusterResourceWhitelist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | ClusterResourceWhitelist contains list of whitelisted cluster level resources |  |  |


##### ArgoCD







_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespace` _Namespace_ | Namespace should contain the name of the namespace in which to deploy ArgoCD AppProjects |  | Required: \{\} <br /> |
| `namespaceResourceBlacklist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | NamespaceResourceBlacklist contains list of blacklisted namespace level resources |  |  |
| `clusterResourceWhitelist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | ClusterResourceWhitelist contains list of whitelisted cluster level resources |  |  |


##### ArgoCDConfig



ArgoCDConfig contains details about source repositories and AppProjects



_Appears in:_
- [ExtensionsSpec](#extensionsspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `appProject` _[AppProjectConfig](#appprojectconfig)_ | AppProject contains details about argocd AppProjects |  |  |
| `onDeletePurgeAppProject` _boolean_ | OnDeletePurgeAppProject is used to enable or disable the AppProject purge feature |  | Optional: \{\} <br /> |


##### ArgoCDConfigStatus



ArgoCDStatus defines the observed state of the ArgoCD extension



_Appears in:_
- [ExtensionsStatus](#extensionsstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `appProjectState` _boolean_ |  |  |  |
| `argoNamespace` _string_ |  |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ |  |  |  |


##### Endpoint



Endpoint is used to connect to an application



_Appears in:_
- [ManagedApp](#managedapp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `url` _string_ |  |  |  |
| `secretReference` _[SecretReference](#secretreference)_ |  |  |  |


##### Extensions



Extensions is the Schema for the extensions API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1alpha1` | | |
| `kind` _string_ | `Extensions` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[ExtensionsSpec](#extensionsspec)_ |  |  |  |
| `status` _[ExtensionsStatus](#extensionsstatus)_ |  |  |  |


##### ExtensionsSpec



ExtensionsSpec defines the desired state of Extensions



_Appears in:_
- [Extensions](#extensions)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tenantName` _string_ | TenantName is the name of the tenant to which the extension belongs |  | Required: \{\} <br /> |
| `argoCD` _[ArgoCDConfig](#argocdconfig)_ | ArgoCDConfig defines ArgoCD configurations for the tenant |  |  |


##### ExtensionsStatus



ExtensionsStatus defines the observed state of Extensions



_Appears in:_
- [Extensions](#extensions)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `argocd` _[ArgoCDConfigStatus](#argocdconfigstatus)_ |  |  |  |


##### Ingress







_Appears in:_
- [IngressConfig](#ingressconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host specifies the hostname for the ingress |  |  |
| `tlsSecretName` _string_ | TLSSecretName is the name of the secret containing the TLS certificate |  | Optional: \{\} <br /> |


##### IngressConfig







_Appears in:_
- [Provision](#provision)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `keycloak` _[Ingress](#ingress)_ |  |  |  |
| `console` _[Ingress](#ingress)_ |  |  |  |
| `gateway` _[Ingress](#ingress)_ |  |  |  |
| `ingressClassName` _string_ | ingressClassName is the ingress class name |  | Optional: \{\} <br /> |


##### IntegrationConfig



IntegrationConfig is the Schema for the integrationConfigs API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1alpha1` | | |
| `kind` _string_ | `IntegrationConfig` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[IntegrationConfigSpec](#integrationconfigspec)_ |  |  |  |
| `status` _[IntegrationConfigStatus](#integrationconfigstatus)_ |  |  |  |


##### IntegrationConfigSpec



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


##### IntegrationConfigStatus



IntegrationConfigStatus defines the observed state of IntegrationConfig



_Appears in:_
- [IntegrationConfig](#integrationconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `roleBindingsToDelete` _object (keys:string, values:string array)_ | RoleBindingsToDelete contains all of the rolebindings that have been whenever the roles cache config map gets updated |  |  |


##### ManagedApp



ManagedApp is the config for a managed application.



_Appears in:_
- [ManagedNexus](#managednexus)
- [ManagedRHSSO](#managedrhsso)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ |  | false |  |
| `endpoint` _[Endpoint](#endpoint)_ |  |  |  |
| `sso` _[SSO](#sso)_ |  |  |  |


##### ManagedNexus



ManagedNexus is the config for Nexus.



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ManagedApp` _[ManagedApp](#managedapp)_ |  |  |  |


##### ManagedRHSSO



ManagedRHSSO is the config for RedHat Single Sign-On.



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ManagedApp` _[ManagedApp](#managedapp)_ |  |  |  |
| `realm` _string_ |  |  |  |


##### ManagedVault



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


##### MatchNamespaceLabel







_Appears in:_
- [TenantRoles](#tenantroles)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labelSelector` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#labelselector-v1-meta)_ | LabelSelector is the label selector that will be used to find namespaces to apply roles to |  |  |
| `UserRoles` _[UserRoles](#userroles)_ | Custom roles applied to the namespaces selected by the label selector |  | Required: \{\} <br /> |


##### Metadata







_Appears in:_
- [OpenshiftConfig](#openshiftconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labels` _object (keys:string, values:string)_ |  |  |  |
| `annotations` _object (keys:string, values:string)_ |  |  |  |


##### NamespaceAccessPolicy



NamespaceAccessPolicy contains access and deny policies for namespaces



_Appears in:_
- [OpenshiftConfig](#openshiftconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deny` _[Policy](#policy)_ |  |  |  |


##### OpenshiftConfig



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


##### Policy



Policy contains policies relating to privilegedNamespaces



_Appears in:_
- [NamespaceAccessPolicy](#namespaceaccesspolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `privilegedNamespaces` _[PrivilegedNamespaces](#privilegednamespaces)_ |  |  |  |


##### PolicyMembers







_Appears in:_
- [PrivilegedNamespaces](#privilegednamespaces)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


##### PrivilegedNamespaces



PrivilegedNamespaces contains groups/users



_Appears in:_
- [Policy](#policy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


##### Provision







_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `console` _boolean_ | Console is used to enable/disable the mto-console | true | Optional: \{\} <br /> |
| `showback` _boolean_ | Showback is used to enable/disable the showback feature | true | Optional: \{\} <br /> |
| `ingress` _[IngressConfig](#ingressconfig)_ | the following are used to configure the ingress for the provisioned services |  |  |
| `trustedRootCert` _string_ | TrustedRootCert is the name of the secret containing the trusted root CA certificate<br />This certificate is used for SSL/TLS communication with other services |  | Optional: \{\} <br /> |


##### SSO



SSO contains details for single sign on



_Appears in:_
- [ManagedApp](#managedapp)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clientName` _string_ |  |  |  |
| `accessorID` _string_ |  |  |  |


##### SecretReference



SecretReference contains details of a secret



_Appears in:_
- [Endpoint](#endpoint)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |
| `namespace` _string_ |  |  |  |


##### TenantRoles



TenantRoles is used to configure custom RBAC rules for tenants



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `default` _[UserRoles](#userroles)_ | DefaultRoles contains the default roles that will be applied to each tenant. Required field. | \{ editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]] \} |  |
| `custom` _[MatchNamespaceLabel](#matchnamespacelabel) array_ | CustomRoles is an optional Label selector method to apply roles to specific namespaces.<br />These roles will override the existing Default Roles |  |  |


##### UserRoles



UserRoles is the list of roles applied to owners/editors/viewers



_Appears in:_
- [MatchNamespaceLabel](#matchnamespacelabel)
- [TenantRoles](#tenantroles)



##### VaultSSO







_Appears in:_
- [ManagedVault](#managedvault)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clientName` _string_ |  |  |  |



### tenantoperator.stakater.com/v1beta1

Package v1beta1 contains API Schema definitions for the tenantoperator v1beta1 API group

#### Resource Types
- [IntegrationConfig](#integrationconfig)
- [Quota](#quota)



##### AccessControl



AccessControl defines the access control settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `rbac` _[RBAC](#rbac)_ |  | \{ tenantRoles:map[default:map[editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]]]] \} |  |
| `namespaceAccessPolicy` _[NamespaceAccessPolicy](#namespaceaccesspolicy)_ |  |  |  |
| `privileged` _[Privileged](#privileged)_ |  |  |  |


##### ArgoCDIntegration



ArgoCD defines the ArgoCD integration settings



_Appears in:_
- [Integrations](#integrations)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `clusterResourceWhitelist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | ClusterResourceWhitelist contains list of whitelisted cluster level resources |  |  |
| `namespaceResourceBlacklist` _[GroupKind](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#groupkind-v1-meta) array_ | NamespaceResourceWhitelist contains list of whitelisted namespace level resources |  |  |
| `namespace` _Namespace_ | Namespace should contain the name of the namespace in which to deploy ArgoCD AppProjects |  | Required: \{\} <br /> |


##### Components



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




##### Custom







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


##### Deny



Deny defines the deny settings for namespace access policy



_Appears in:_
- [NamespaceAccessPolicy](#namespaceaccesspolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `privilegedNamespaces` _[PrivilegedNamespaces](#privilegednamespaces)_ |  |  |  |


##### DependencyMode

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


##### DexComponentConfig







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Prometheus Helm chart values when mode is Managed |  |  |
| `external` _[DexExternalConfig](#dexexternalconfig)_ | External defines information required when using an externally managed Dex deployment |  |  |


##### DexConfigOperatorConfig







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Prometheus Helm chart values |  |  |


##### DexExternalConfig







_Appears in:_
- [DexComponentConfig](#dexcomponentconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `issuer` _string_ | Issuer is the URL of the Dex issuer, used for OIDC discovery |  |  |


##### ExternalServerConfig



ExternalServerConfig stores references to an external Prometheus deployment



_Appears in:_
- [OpenCostComponentConfig](#opencostcomponentconfig)
- [PrometheusComponentConfig](#prometheuscomponentconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `serverURL` _string_ | ServerURL is the base URL that the operator should use for query API access |  |  |


##### FinOpsOperator



FinOpsOperator defines the configuration for FinOps Operator components
See https://docs.stakater.com/finops-operator/latest for more details



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the FinOps Operator Helm chart values when mode is Managed |  | Optional: \{\} <br /> |




##### Ingress







_Appears in:_
- [IngressConfig](#ingressconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `host` _string_ | Host specifies the hostname for the ingress (legacy per-component mode). |  |  |
| `tlsSecretName` _string_ | TLSSecretName is the name of the secret containing the TLS certificate. |  | Optional: \{\} <br /> |
| `path` _string_ | Path is the path prefix under the shared host in consolidated mode.<br />Defaults: Console "/", Gateway "/gateway", Dex "/dex", FinOps "/finops". |  | Optional: \{\} <br /> |


##### IngressConfig







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


##### IntegrationConfig



IntegrationConfig is the Schema for the integrationconfigs API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1beta1` | | |
| `kind` _string_ | `IntegrationConfig` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[IntegrationConfigSpec](#integrationconfigspec)_ |  |  |  |
| `status` _[IntegrationConfigStatus](#integrationconfigstatus)_ |  |  |  |


##### IntegrationConfigSpec



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


##### IntegrationConfigStatus



IntegrationConfigStatus defines the observed state of IntegrationConfig



_Appears in:_
- [IntegrationConfig](#integrationconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `roleBindingsToDelete` _object (keys:string, values:string array)_ |  |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Status conditions |  |  |


##### Integrations



Integrations defines the integration settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `argocd` _[ArgoCDIntegration](#argocdintegration)_ |  |  |  |
| `vault` _[VaultIntegration](#vaultintegration)_ |  |  |  |




##### MatchNamespaceLabel







_Appears in:_
- [TenantRoles](#tenantroles)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labelSelector` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#labelselector-v1-meta)_ | LabelSelector is the label selector that will be used to find namespaces to apply roles to |  |  |
| `UserRoles` _[UserRoles](#userroles)_ | Custom roles applied to the namespaces selected by the label selector |  |  |


##### Metadata



Metadata defines the metadata settings for IntegrationConfig



_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `groups` _[MetadataType](#metadatatype)_ | Groups contains labels and annotations applied to the groups |  |  |
| `namespaces` _[MetadataType](#metadatatype)_ | Namespaces contains labels and annotations applied to the namespaces |  |  |
| `sandboxes` _[MetadataType](#metadatatype)_ | Sandboxes contains labels and annotations applied to the sandbox |  |  |


##### MetadataType







_Appears in:_
- [Metadata](#metadata)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `labels` _object (keys:string, values:string)_ |  |  |  |
| `annotations` _object (keys:string, values:string)_ |  |  |  |


##### NamespaceAccessPolicy



NamespaceAccessPolicy defines the namespace access policy settings



_Appears in:_
- [AccessControl](#accesscontrol)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `deny` _[Deny](#deny)_ |  |  |  |




##### OpenCostComponentConfig



OpenCostComponentConfig describes how OpenCost is configured for showback features



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the OpenCost Helm chart values when mode is Managed |  |  |
| `external` _[ExternalServerConfig](#externalserverconfig)_ | External defines information required when using an externally managed OpenCost deployment |  |  |


##### PolicyRule



PolicyRule defines the policy rule



_Appears in:_
- [VaultPolicy](#vaultpolicy)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `path` _string_ | Path is the path to the resource |  |  |
| `capabilities` _string array_ | Capabilities is the list of capabilities |  |  |


##### PostgresComponentConfig



PostgresComponentConfig describes how Postgres is configured for application persistence



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Postgres Helm chart values when mode is Managed |  |  |
| `external` _[PostgresExternalConfig](#postgresexternalconfig)_ | External defines information required when using an externally managed Postgres instance |  |  |


##### PostgresExternalConfig



PostgresExternalConfig stores references to an external Postgres instance



_Appears in:_
- [PostgresComponentConfig](#postgrescomponentconfig)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `secretRef` _[SecretRef](#secretref)_ | SecretRef references a secret containing a DSN or discrete connection details |  |  |


##### Privileged



Privileged defines the privileged settings for IntegrationConfig



_Appears in:_
- [AccessControl](#accesscontrol)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `namespaces` _string array_ |  |  |  |
| `serviceAccounts` _string array_ |  |  |  |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


##### PrivilegedNamespaces



PrivilegedNamespaces defines the list of privileged namespaces and associated users/groups



_Appears in:_
- [Deny](#deny)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `users` _string array_ |  |  |  |
| `groups` _string array_ |  |  |  |


##### PrometheusComponentConfig



PrometheusComponentConfig describes how Prometheus is configured for tenant operations



_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `mode` _[DependencyMode](#dependencymode)_ |  | Managed | Enum: [Managed External] <br /> |
| `values` _[RawExtension](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#rawextension-runtime-pkg)_ | Values allows customization of the Prometheus Helm chart values when mode is Managed |  |  |
| `external` _[ExternalServerConfig](#externalserverconfig)_ | External defines information required when using an externally managed Prometheus |  |  |


##### Quota



Quota is the Schema for the quotas API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1beta1` | | |
| `kind` _string_ | `Quota` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[QuotaSpec](#quotaspec)_ |  |  |  |
| `status` _[QuotaStatus](#quotastatus)_ |  |  |  |


##### QuotaSpec







_Appears in:_
- [Quota](#quota)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resourcequota` _[ResourceQuotaSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#resourcequotaspec-v1-core)_ | ResourceQuota defines the allocated ResourceQuota for the tenant |  |  |
| `limitrange` _[LimitRangeSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#limitrangespec-v1-core)_ | LimitRange defines the allocated LimitRange for the namespace inside tenant |  | Optional: \{\} <br /> |


##### QuotaStatus



QuotaStatus defines the observed state of Quota



_Appears in:_
- [Quota](#quota)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `TenantQuotaStatus` _[TenantQuotaStatus](#tenantquotastatus)_ |  |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Status conditions for quota |  |  |


##### RBAC



RBAC defines the RBAC settings for IntegrationConfig



_Appears in:_
- [AccessControl](#accesscontrol)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tenantRoles` _[TenantRoles](#tenantroles)_ | TenantRoles sets the default Owner/Editor/Viewer and/or custom roles for each tenant | \{ default:map[editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]]] \} |  |




##### SecretRef



SecretReference defines the reference to a secret



_Appears in:_
- [PostgresExternalConfig](#postgresexternalconfig)
- [ShowbackOpts](#showbackopts)
- [VaultAccessInfo](#vaultaccessinfo)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |
| `namespace` _string_ |  |  |  |


##### ShowbackOpts







_Appears in:_
- [Components](#components)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `custom` _[Custom](#custom)_ | Custom is used to define custom pricing for opencost. If not provided, the default pricing will be used.<br />Custom field is deprecated and will be removed in a future release. Please use the spec.components.finopsOperator.priceBook field instead to configure custom pricing for OpenCost. |  | Optional: \{\} <br /> |
| `cloudPricingSecretRef` _[SecretRef](#secretref)_ | CloudPricingSecretRef is the reference to the secret containing the opeconst config for AWS/Azure.<br />This field is deprecated and will be removed in a future release. Please use the spec.components.opencost.cloudIntegrationSecret field instead to configure the cloud integration for OpenCost. |  | Optional: \{\} <br /> |
| `retentionPeriod` _string_ | RetentionPeriod defines the retention period of prometheus server<br />This field is deprecated and will be removed in a future release. Please use the spec.components.prometheus.retention field instead to configure the retention period for Prometheus. | 7d |  |


##### TenantPolicies







_Appears in:_
- [IntegrationConfigSpec](#integrationconfigspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `network` _[TenantPoliciesNetwork](#tenantpoliciesnetwork)_ |  |  |  |


##### TenantPoliciesNetwork







_Appears in:_
- [TenantPolicies](#tenantpolicies)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `disableIntraTenantNetworking` _boolean_ |  |  |  |
| `disableNodePortServices` _boolean_ |  |  |  |
| `disableHostPorts` _boolean_ |  |  |  |


##### TenantQuotaStatus







_Appears in:_
- [QuotaStatus](#quotastatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `tenants` _object (keys:string, values:[TenantResourceStatus](#tenantresourcestatus))_ |  |  |  |


##### TenantResourceStatus







_Appears in:_
- [TenantQuotaStatus](#tenantquotastatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `status` _[ResourceQuotaStatus](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#resourcequotastatus-v1-core)_ |  |  |  |


##### TenantRoles







_Appears in:_
- [RBAC](#rbac)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `default` _[UserRoles](#userroles)_ | DefaultRoles contains the default roles that will be applied to each tenant. Required field. | \{ editor:map[clusterRoles:[edit]] owner:map[clusterRoles:[admin]] viewer:map[clusterRoles:[view]] \} |  |
| `custom` _[MatchNamespaceLabel](#matchnamespacelabel) array_ | CustomRoles is an optional Label selector method to apply roles to specific namespaces.<br />These roles will override the existing Default Roles |  |  |


##### UserRoles







_Appears in:_
- [MatchNamespaceLabel](#matchnamespacelabel)
- [TenantRoles](#tenantroles)



##### VaultAccessInfo



VaultAccessInfo defines the access information for Vault



_Appears in:_
- [VaultIntegration](#vaultintegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `accessorPath` _string_ |  |  |  |
| `address` _string_ |  |  |  |
| `roleName` _string_ |  |  |  |
| `secretRef` _[SecretRef](#secretref)_ |  |  |  |


##### VaultConfig



VaultConfig defines the Vault configuration



_Appears in:_
- [VaultIntegration](#vaultintegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ssoClient` _string_ |  |  |  |
| `commonSecretsPath` _string_ | CommonSecretsPath defines a secrets path in Vault which is shared by all tenants |  | Optional: \{\} <br /> |


##### VaultIntegration



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


##### VaultPolicy



VaultPolicy defines the Vault policy details



_Appears in:_
- [VaultIntegration](#vaultintegration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the name of the policy |  |  |
| `rules` _[PolicyRule](#policyrule) array_ | Rules is the policy rules |  |  |
| `tenantRoles` _string array_ | TenantRoles is the list of tenant roles to apply the policy to |  |  |



### tenantoperator.stakater.com/v1beta3

Package v1beta3 contains API Schema definitions for the tenantoperator v1beta3 API group

#### Resource Types
- [Tenant](#tenant)



##### AccessControl







_Appears in:_
- [TenantSpec](#tenantspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `owners` _Members_ | owners represents the list of owners |  |  |
| `editors` _Members_ | editors represents the list of editors |  |  |
| `viewers` _Members_ | viewers represents the list of viewers |  |  |


##### HostValidationConfig







_Appears in:_
- [TenantSpec](#tenantspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `denyWildcards` _boolean_ | DenyWildcards indicates whether wildcard host names are allowed or not<br />If true, wildcard host names are not allowed<br />If false, wildcard host names are allowed | false | Optional: \{\} <br />Type: boolean <br /> |
| `allowedRegex` _string_ | AllowedRegex is a regular expression that defines the allowed host names<br />If specified, host names must match this regex to be allowed |  | Optional: \{\} <br />Type: string <br /> |
| `allowed` _string array_ | Allowed is a list of allowed host names<br />If specified, host names must be in this list to be allowed |  | Optional: \{\} <br />Type: array <br /> |


##### IngressClassEntry







_Appears in:_
- [IngressClassStatus](#ingressclassstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


##### IngressClassStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[IngressClassEntry](#ingressclassentry) array_ |  |  |  |


##### Metadata







_Appears in:_
- [Namespaces](#namespaces)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `common` _[Metadata](#metadata)_ | commonmetadata applies given labels and annotations |  |  |
| `sandbox` _[Metadata](#metadata)_ | sandboxmetadata applies given labels and annotation across sandbox namespaces |  |  |
| `specific` _MetadataOnNamespaces array_ | specificmetadata applies given labels and annotation across specific namespaces |  |  |


##### Namespaces







_Appears in:_
- [TenantSpec](#tenantspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `sandboxes` _[Sandboxes](#sandboxes)_ | sandboxes is used to enable or disable the sandbox feature |  |  |
| `withoutTenantPrefix` _Namespace array_ | WithoutTenantPrefix will create new namespaces mentioned in it |  |  |
| `withTenantPrefix` _Namespace array_ | WithTenantPrefix will create new namespaces mentioned in it and add a prefix of the tenant name to them |  |  |
| `onDeletePurgeNamespaces` _boolean_ | ondeletepurgenamespaces is used to enable or disable the namespace purge feature | false |  |
| `metadata` _[Metadata](#metadata)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |


##### NamespacesStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `commonStatus` _[Metadata](#metadata)_ | CommonStatus stores the previous state of labels and annotation applied across all tenant namespaces, if mentioned in spec |  |  |
| `sandboxStatus` _[Metadata](#metadata)_ | SandboxStatus stores the previous state of labels and annotation applied across all sandbox namespaces, if mentioned in spec |  |  |
| `specificStatus` _MetadataOnNamespaces array_ | SpecificStatus stores the previous state of labels and annotations applied across specific tenant namespaces, if mentioned in spec |  |  |


##### PodPriorityClassEntry







_Appears in:_
- [PodPriorityClassStatus](#podpriorityclassstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


##### PodPriorityClassStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[PodPriorityClassEntry](#podpriorityclassentry) array_ |  |  |  |


##### QuotaEntry







_Appears in:_
- [QuotaStatus](#quotastatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


##### QuotaStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[QuotaEntry](#quotaentry) array_ |  |  |  |


##### Sandboxes







_Appears in:_
- [Namespaces](#namespaces)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `enabled` _boolean_ | enabled is used to enable or disable the sandbox feature |  |  |
| `private` _boolean_ | private is used to enable or disable the private sandbox feature |  |  |


##### StorageClassEntry







_Appears in:_
- [StorageStatus](#storagestatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  |  |


##### StorageStatus







_Appears in:_
- [TenantStatus](#tenantstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `available` _[StorageClassEntry](#storageclassentry) array_ |  |  |  |


##### Tenant



Tenant is the Schema for the tenants API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `tenantoperator.stakater.com/v1beta3` | | |
| `kind` _string_ | `Tenant` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[TenantSpec](#tenantspec)_ |  |  |  |
| `status` _[TenantStatus](#tenantstatus)_ |  |  |  |


##### TenantSpec



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


##### TenantStatus



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

## Template Operator

<!-- markdownlint-disable -->

### Packages
- [templates.stakater.com/v1alpha1](#templatesstakatercomv1alpha1)


### templates.stakater.com/v1alpha1

Package v1alpha1 contains API Schema definitions for the templates.stakater.com v1alpha1 API group

#### Resource Types
- [ClusterTemplateInstance](#clustertemplateinstance)
- [Template](#template)
- [TemplateInstance](#templateinstance)


##### ClusterTemplateInstance



ClusterTemplateInstance is the Schema for the clustertemplateinstances API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `templates.stakater.com/v1alpha1` | | |
| `kind` _string_ | `ClusterTemplateInstance` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[ClusterTemplateInstanceSpec](#clustertemplateinstancespec)_ |  |  |  |
| `status` _[ClusterTemplateInstanceStatus](#clustertemplateinstancestatus)_ |  |  |  |


##### ClusterTemplateInstanceSpec



ClusterTemplateInstanceSpec defines the desired state of ClusterTemplateInstance



_Appears in:_
- [ClusterTemplateInstance](#clustertemplateinstance)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `template` _string_ | Template is used to tell what to deploy in matched namespaces |  |  |
| `selector` _[LabelSelector](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#labelselector-v1-meta)_ | Selector is used to filter namespaces where template needs to be deployed |  |  |
| `sync` _boolean_ | Sync is used to keep deployed instance and template in sync |  |  |
| `parameters` _[TemplateInstanceParameter](#templateinstanceparameter) array_ | Parameters hold the values of the defined parameters in the template |  | Optional: \{\} <br /> |


##### TemplateInstanceParameter







_Appears in:_
- [ClusterTemplateInstanceSpec](#clustertemplateinstancespec)
- [TemplateInstanceSpec](#templateinstancespec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the name of the parameter to set |  |  |
| `value` _string_ | Value is the value of the parameter to set |  |  |


##### ClusterTemplateInstanceStatus



ClusterTemplateInstanceStatus defines the observed state of ClusterTemplateInstance



_Appears in:_
- [ClusterTemplateInstance](#clustertemplateinstance)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Status conditions |  | Optional: \{\} <br /> |
| `deployedNamespaces` _object (keys:string, values:[DeployedNamespaceState](#deployednamespacestate))_ | DeployedNamespaces is a list of namespaces where template has been deployed along with its state. |  | Optional: \{\} <br /> |
| `mappedSecrets` _object (keys:string, values:map[string]MappedResourcesState)_ | MappedSecrets is a list of secrets which have been mapped along with its state. |  | Optional: \{\} <br /> |
| `mappedConfigmaps` _object (keys:string, values:map[string]MappedResourcesState)_ | MappedConfigmaps is a list of configmaps which have been mapped along with its state. |  | Optional: \{\} <br /> |
| `templateManifestsHash` _string_ | TemplateManifestsHash is used to ignore false-positive template.manifests update events |  | Optional: \{\} <br /> |
| `templateResourceMappingHash` _string_ | TemplateResourceMappingHash is used to ignore false-positive template.resourceMappings update events |  | Optional: \{\} <br /> |
| `namespaceCount` _integer_ | NamespaceCount tells the number of namespaces CTI matches |  | Optional: \{\} <br /> |


##### Template



Template is the Schema for the templates API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `templates.stakater.com/v1alpha1` | | |
| `kind` _string_ | `Template` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `resources` _[TemplateResources](#templateresources)_ |  |  | Optional: \{\} <br /> |
| `spec` _[TemplateSpec](#templatespec)_ |  |  |  |
| `status` _[TemplateStatus](#templatestatus)_ |  |  | Optional: \{\} <br /> |
| `parameters` _[TemplateParameter](#templateparameter) array_ | Parameters can be used to replace certain parts of the template. A parameter is referenced<br />by this format: $\{NAME\}, to parse the value as an expression write $\{\{NAME\}\} instead. Besides the<br />parameters defined here, the following predefined parameters can be used:<br />- $\{NAMESPACE\}: the namespace where the template instance was created<br />- $\{TENANT\}: the tenant name of the tenant that owns the namespace (if any) |  | Optional: \{\} <br /> |


##### TemplateResources



TemplateResources defines a templates resources



_Appears in:_
- [Template](#template)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `manifests` _[EmbeddedResource](#embeddedresource) array_ | manifest represents kubernetes resources that will be deployed into the target namespace |  | Optional: \{\} <br /> |
| `helm` _[HelmConfiguration](#helmconfiguration)_ | helm defines the configuration for a helm deployment |  | Optional: \{\} <br /> |
| `resourceMappings` _[ResourceMapping](#resourcemapping)_ | ResourceMappings defines the secrets/configmaps which will be mapped into the target namespaces |  | Optional: \{\} <br /> |
| `gotemplate` _string_ | gotemplate is a Go template with Sprig functions support which will be rendered to generate Kubernetes resources. |  | Optional: \{\} <br /> |


##### EmbeddedResource



EmbeddedResource holds a kubernetes resource



_Appears in:_
- [TemplateResources](#templateresources)



##### HelmConfiguration



HelmConfiguration holds the helm configuration



_Appears in:_
- [TemplateResources](#templateresources)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `releaseName` _string_ | The helm release name. If omitted the template name will be used |  | Optional: \{\} <br /> |
| `setValues` _[HelmSetValue](#helmsetvalue) array_ | Values in the form of name=value that will be passed to the helm command during<br />helm template |  | Optional: \{\} <br /> |
| `values` _string_ | The additional helm values to use. Expected block string |  | Optional: \{\} <br /> |
| `chart` _[HelmChart](#helmchart)_ | Tells us where to find the helm chart to deploy |  |  |


##### HelmSetValue



HelmSetValue defines a name=value pair that will be passed to helm template



_Appears in:_
- [HelmConfiguration](#helmconfiguration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | The path of the value to set |  |  |
| `value` _string_ | The value to set |  |  |
| `forceString` _boolean_ | ForceString specifies if the parameter `--set` or `--set-string` should be used |  | Optional: \{\} <br /> |


##### HelmChart



HelmChart holds the information needed to find a chart to deploy



_Appears in:_
- [HelmConfiguration](#helmconfiguration)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `repository` _[HelmChartRepository](#helmchartrepository)_ | Load helm chart from a repository |  | Optional: \{\} <br /> |


##### HelmChartRepository



HelmChartRepository defines a helm repository where TO can load a chart from



_Appears in:_
- [HelmChart](#helmchart)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name of the chart to deploy |  |  |
| `version` _string_ | Version is the version of the chart to deploy |  | Optional: \{\} <br /> |
| `repoUrl` _string_ | The repo url to use |  | Optional: \{\} <br /> |
| `username` _[HelmSecretRef](#helmsecretref)_ | The username to use for the selected repository |  | Optional: \{\} <br /> |
| `password` _[HelmSecretRef](#helmsecretref)_ | The password to use for the selected repository |  | Optional: \{\} <br /> |


##### HelmSecretRef



HelmSecretRef holds a secret reference to a secret



_Appears in:_
- [HelmChartRepository](#helmchartrepository)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `key` _string_ |  |  |  |
| `name` _string_ |  |  |  |
| `namespace` _string_ |  |  | Optional: \{\} <br /> |


##### ResourceMapping







_Appears in:_
- [TemplateResources](#templateresources)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `secrets` _[Resource](#resource) array_ | Secrets consist of secrets which will be mapped to matching namespaces |  | Optional: \{\} <br /> |
| `configMaps` _[Resource](#resource) array_ | ConfigMaps consist of configMaps which will be mapped to matching namespaces |  | Optional: \{\} <br /> |


##### Resource







_Appears in:_
- [ResourceMapping](#resourcemapping)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the name of the resource |  | Required: \{\} <br /> |
| `namespace` _string_ | Namespace is the namespace where the resource lives |  | Required: \{\} <br /> |


##### TemplateSpec







_Appears in:_
- [Template](#template)



##### TemplateStatus







_Appears in:_
- [Template](#template)



##### TemplateParameter







_Appears in:_
- [Template](#template)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ | Name is the name of the parameter |  |  |
| `value` _string_ | Value is the default value of the parameter |  | Optional: \{\} <br /> |
| `required` _boolean_ | If required is true, the template instance must<br />define this parameter, otherwise the deployment will fail. |  | Optional: \{\} <br /> |
| `validation` _string_ | Validation takes a regular expression as value to<br />verify the provided value does match expected values. |  | Optional: \{\} <br /> |


##### TemplateInstance



TemplateInstance is the Schema for the templatesinstance API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `templates.stakater.com/v1alpha1` | | |
| `kind` _string_ | `TemplateInstance` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[TemplateInstanceSpec](#templateinstancespec)_ |  |  |  |
| `status` _[TemplateInstanceStatus](#templateinstancestatus)_ |  |  | Optional: \{\} <br /> |


##### TemplateInstanceSpec



TemplateInstanceSpec holds the expected cluster status of the template instance



_Appears in:_
- [TemplateInstance](#templateinstance)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `template` _string_ | The template to instantiate. This is an immutable field |  |  |
| `sync` _boolean_ | If true the template instance will keep the deployed resources in sync with the template. |  | Optional: \{\} <br /> |
| `parameters` _[TemplateInstanceParameter](#templateinstanceparameter) array_ | Parameters hold the values of the defined parameters in the template |  | Optional: \{\} <br /> |


##### TemplateInstanceStatus



TemplateInstanceStatus describes the current status of the template instance in the cluster



_Appears in:_
- [TemplateInstance](#templateinstance)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `status` _[InstanceDeploymentStatus](#instancedeploymentstatus)_ | Status holds the template instances status |  |  |
| `message` _string_ | A human readable message indicating details about why the namespace is in this condition. |  | Optional: \{\} <br /> |
| `reason` _string_ | A brief CamelCase message indicating details about why the namespace is in this state. |  | Optional: \{\} <br /> |
| `templateHash` _string_ | TemplateHash is used to ignore false-positive template update events |  | Optional: \{\} <br /> |
| `templateManifests` _string_ | TemplateManifests are the manifests that were rendered before |  | Optional: \{\} <br /> |
| `mappedSecrets` _object (keys:string, values:[MappedResourcesState](#mappedresourcesstate))_ | MappedSecrets is a list of secrets which have been mapped along with its state. |  | Optional: \{\} <br /> |
| `mappedConfigmaps` _object (keys:string, values:[MappedResourcesState](#mappedresourcesstate))_ | MappedConfigmaps is a list of configmaps which have been mapped along with its state. |  | Optional: \{\} <br /> |
| `observedAt` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | LastAppliedAt indicates when the template was last applied |  | Optional: \{\} <br /> |


##### InstanceDeploymentStatus

_Underlying type:_ _string_

InstanceDeploymentStatus describes the status of template instance deployment as {"Deployed", "Failed", ""}



_Appears in:_
- [DeployedNamespaceState](#deployednamespacestate)
- [MappedResourcesState](#mappedresourcesstate)
- [TemplateInstanceStatus](#templateinstancestatus)

| Field | Description |
| --- | --- |
| `Deployed` | InstanceDeploymentStatusDeployed describes a succeeded instance deployment<br /> |
| `Failed` | InstanceDeploymentStatusFailed describes a failed instance deployment<br /> |
| `` | InstanceDeploymentStatusPending describes a not yet deployed instance<br /> |


##### DeployedNamespaceState







_Appears in:_
- [ClusterTemplateInstanceStatus](#clustertemplateinstancestatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `templateManifests` _string_ | TemplateManifests are the manifests that were rendered before |  | Optional: \{\} <br /> |
| `status` _[InstanceDeploymentStatus](#instancedeploymentstatus)_ |  |  |  |


##### MappedResourcesState







_Appears in:_
- [ClusterTemplateInstanceStatus](#clustertemplateinstancestatus)
- [TemplateInstanceStatus](#templateinstancestatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `reason` _string_ | Reason of resource mapping if failed |  | Optional: \{\} <br /> |
| `status` _[InstanceDeploymentStatus](#instancedeploymentstatus)_ |  |  |  |

## FinOps

<!-- markdownlint-disable -->

### Packages
- [finops.stakater.com/v1alpha1](#finopsstakatercomv1alpha1)


### finops.stakater.com/v1alpha1

Package v1alpha1 contains API Schema definitions for the finops v1alpha1 API group.

#### Resource Types
- [CostJob](#costjob)
- [FinOpsProvider](#finopsprovider)
- [Offering](#offering)
- [PriceBook](#pricebook)
- [Subscription](#subscription)



##### AWSOptions



AWSOptions defines AWS-specific options.



_Appears in:_
- [FinOpsProviderSpec](#finopsproviderspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `cloudIntegrationSecret` _string_ | CloudIntegrationSecret is the Azure Subscription ID. |  | Optional: \{\} <br /> |
| `pricingModelSource` _string_ | PricingModelSource indicates how the pricing model is provided to OpenCost.<br />e.g., "Pricebook" if derived from PriceBook CRs. |  | Optional: \{\} <br /> |


##### AzureOptions



AzureOptions defines Azure-specific options.



_Appears in:_
- [FinOpsProviderSpec](#finopsproviderspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `cloudIntegrationSecret` _string_ | CloudIntegrationSecret is the Azure Subscription ID. |  | Optional: \{\} <br /> |
| `pricingModelSource` _string_ | PricingModelSource indicates how the pricing model is provided to OpenCost.<br />e.g., "Pricebook" if derived from PriceBook CRs. |  | Optional: \{\} <br /> |


##### Compatibility



Compatibility defines compatibility requirements for subscriptions bound to this offering



_Appears in:_
- [OfferingSpec](#offeringspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `requiredOfferings` _[ObjectReference](#objectreference) array_ | RequiredOfferings lists offerings that must be covered by an active subscription in<br />the same family (the connected tree sharing a root ancestor) for a subscription to<br />this offering to activate. Coverage spans the whole family EXCEPT the subscription's<br />own subtree: ancestors, siblings, uncles, and cousins all count; the subscription's<br />own children and descendants do not. A root subscription's subtree is the entire<br />family, so a requirement-bearing root can never be covered. |  | Optional: \{\} <br /> |


##### CostBucket







_Appears in:_
- [SubscriptionStatus](#subscriptionstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `granularity` _string_ | Granularity is the time granularity of this bucket (e.g., hour, day, month). |  | Enum: [hour day month] <br /> |
| `start` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | Start is the start time of the bucket (inclusive). |  |  |
| `endExclusive` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | EndExclusive is the end time of the bucket (exclusive). |  |  |
| `current` _integer_ | Current is the current accumulated spend for the period in micro-currency units. |  | Optional: \{\} <br /> |
| `projected` _integer_ | Projected is the projected spend for the full period cycle in micro-currency units. |  | Optional: \{\} <br /> |
| `breakdown` _[CostMetric](#costmetric) array_ | Breakdown contains the cost breakdown by component. |  | Optional: \{\} <br /> |


##### CostJob



CostJob is the Schema for the costjobs API.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `finops.stakater.com/v1alpha1` | | |
| `kind` _string_ | `CostJob` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[CostJobSpec](#costjobspec)_ |  |  |  |
| `status` _[CostJobStatus](#costjobstatus)_ |  |  |  |




##### CostJobSpec



CostJobSpec defines the desired state of CostJob.



_Appears in:_
- [CostJob](#costjob)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `type` _[CostJobType](#costjobtype)_ | Type of the cost collection job, e.g., "ResourceCostCollection" | ResourceCostCollection | Enum: [ResourceCostCollection SubscriptionChargeCollection] <br />Optional: \{\} <br /> |
| `databaseInitTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | DatabaseInitTimeout is the timeout for database initialization | 2m | Optional: \{\} <br /> |
| `kubernetesOperationTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | KubernetesOperationTimeout is the timeout for Kubernetes API operations | 1m | Optional: \{\} <br /> |
| `openCostFetchTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | OpenCostFetchTimeout is the timeout for fetching data from OpenCost | 2m | Optional: \{\} <br /> |
| `databaseInsertTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | DatabaseInsertTimeout is the timeout for database insert operations | 3m | Optional: \{\} <br /> |
| `databaseViewsRefreshTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | DatabaseViewsRefreshTimeout is retained for API compatibility and has no<br />effect. The cost ingestion job no longer refreshes any database view: the<br />mv_provider_allocations_summary materialized view it used to rebuild on<br />every run had no readers and was dropped in migration 14.<br />Deprecated: no-op. Setting this value changes nothing. |  | Optional: \{\} <br /> |
| `statusUpdateTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | StatusUpdateTimeout is the timeout for status update operations | 1m | Optional: \{\} <br /> |
| `httpClientTimeout` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ | HTTPClientTimeout is the timeout for HTTP client requests | 90s | Optional: \{\} <br /> |
| `interval` _[Duration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#duration-v1-meta)_ |  | 24h |  |
| `resources` _[ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#resourcerequirements-v1-core)_ | Resources overrides compute resources for the generated CronJob's loader container.<br />Setting this replaces the whole block, so a partial value does not inherit the<br />template defaults for the keys it omits. Unset means the operator defaults apply. |  | Optional: \{\} <br /> |


##### CostJobStatus



CostJobStatus defines the observed state of CostJob



_Appears in:_
- [CostJob](#costjob)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `lastExecutionTime` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | Last execution time |  |  |
| `lastSuccessfulExecutionTime` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | Last successful execution time |  |  |
| `lastExecutionStatus` _string_ | Status of the last execution |  | Enum: [Success Failed Error Pending] <br /> |
| `executionHistory` _[ExecutionRecord](#executionrecord) array_ | History of the last 10 executions |  |  |


##### CostJobType

_Underlying type:_ _string_



_Validation:_
- Enum: [ResourceCostCollection SubscriptionChargeCollection]

_Appears in:_
- [CostJobSpec](#costjobspec)

| Field | Description |
| --- | --- |
| `ResourceCostCollection` |  |
| `SubscriptionChargeCollection` |  |


##### CostMetric







_Appears in:_
- [CostBucket](#costbucket)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[MeterName](#metername)_ | Name is the name of the cost metric (e.g., "cpuHour", "pvGbHour"). |  | Enum: [subscription cpuHour gpuHour ramGbHour pvGbHour networkGb] <br />Required: \{\} <br /> |
| `current` _integer_ | Current is the current accumulated value in micro-currency units. |  | Optional: \{\} <br /> |
| `projected` _integer_ | Projected is the projected value in micro-currency units. |  | Optional: \{\} <br /> |


##### ExecutionRecord



ExecutionRecord represents a single execution attempt



_Appears in:_
- [CostJobStatus](#costjobstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `executionTime` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | The time when this execution started |  |  |
| `status` _string_ | Status of the execution (Success, Failed, Error) |  | Enum: [Success Failed Error] <br /> |
| `duration` _string_ | Duration of the execution |  |  |
| `error` _string_ | Error message if the execution failed |  |  |


##### FinOpsProvider



FinOpsProvider is the Schema for the finopsproviders API.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `finops.stakater.com/v1alpha1` | | |
| `kind` _string_ | `FinOpsProvider` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[FinOpsProviderSpec](#finopsproviderspec)_ |  |  |  |
| `status` _[FinOpsProviderStatus](#finopsproviderstatus)_ |  |  |  |


##### FinOpsProviderSpec



ProviderOptions holds provider-specific configuration options.
Exactly one of AWS, GCP, Azure, or OnPrem must be set.
These validations operate on the Go field names (AWS, GCP, Azure, OnPrem).
Se https://opencost.io/docs/configuration/ for possible options
todo: +kubebuilder:validation:XValidation:rule="has(self.Aws) || has(self.Gcp) || has(self.Azure) || has(self.OnPrem)", message="At least one provider option (awsoptions, gcpoptions, azureoptions, onpremoptions) must be set"
todo: +kubebuilder:validation:XValidation:rule="(has(self.Aws) ? 1 : 0) + (has(self.Gcp) ? 1 : 0) + (has(self.Azure) ? 1 : 0) + (has(self.OnPrem) ? 1 : 0) == 1", message="Exactly one provider option (awsoptions, gcpoptions, azureoptions, onpremoptions) must be set"



_Appears in:_
- [FinOpsProvider](#finopsprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `awsoptions` _[AWSOptions](#awsoptions)_ | AWS specific options. |  | Optional: \{\} <br /> |
| `gcpoptions` _[GCPOptions](#gcpoptions)_ | GCP specific options. |  | Optional: \{\} <br /> |
| `azureoptions` _[AzureOptions](#azureoptions)_ | Azure specific options. |  | Optional: \{\} <br /> |
| `onpremoptions` _[OnPremOptions](#onpremoptions)_ | OnPrem specific options. |  | Optional: \{\} <br /> |


##### FinOpsProviderStatus



FinOpsProviderStatus defines the observed state of FinOpsProvider.



_Appears in:_
- [FinOpsProvider](#finopsprovider)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `observedGeneration` _integer_ | ObservedGeneration reflects the generation of the most recently observed spec. |  | Optional: \{\} <br /> |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Conditions represent the latest available observations of the FinOpsProvider's state. |  | Optional: \{\} <br /> |
| `lastSyncTime` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | LastSyncTime is the timestamp of the last successful sync of OpenCost configuration. |  | Optional: \{\} <br /> |


##### GCPOptions



GCPOptions defines GCP-specific options.



_Appears in:_
- [FinOpsProviderSpec](#finopsproviderspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `cloudIntegrationSecret` _string_ | CloudIntegrationSecret is the Azure Subscription ID. |  | Optional: \{\} <br /> |
| `pricingModelSource` _string_ | PricingModelSource indicates how the pricing model is provided to OpenCost.<br />e.g., "Pricebook" if derived from PriceBook CRs. |  | Optional: \{\} <br /> |




##### Lifecycle



Lifecycle defines lifecycle behavior for subscriptions



_Appears in:_
- [OfferingSpec](#offeringspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `onParentDeactivate` _[ParentDeactivateAction](#parentdeactivateaction)_ | OnParentDeactivate toggles whether subscriptions to this offering should be deactivated when their parent subscription is deactivated<br />- Deactivate: this subscription also deactivates.<br />- Orphan: this subscription stays active independently, while retaining the parent reference for traceability. | Deactivate | Enum: [Deactivate Orphan] <br /> |
| `allowOverride` _boolean_ | AllowOverride allows the subscription to override the lifecycle settings |  | Optional: \{\} <br /> |


##### Margins



Margins defines pricing adjustments. AbsoluteMicros and FactorMilli are
mutually exclusive — pick one mode per meter. Both must be non-negative: a
negative margin would drive the per-unit price (and thus the usage charge)
below zero, which usage meters don't support. Express a discount with a
factorMilli below 1000 (e.g. 980 = 0.98x), not a negative absoluteMicros.



_Appears in:_
- [Meter](#meter)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `absoluteMicros` _integer_ | AbsoluteMicros is an additive margin in micro-currency units (10^-6 of the currency)<br />1,000,000 micros = 1.00 currency unit<br />Example: 0.02 cents = 0.0002 currency units = 200 micros |  | Optional: \{\} <br /> |
| `factorMilli` _integer_ | FactorMilli is a multiplicative factor in milli-units<br />1000 = 1.000x, 1020 = 1.020x (adds 2%), 980 = 0.980x (discount 2%) |  | Optional: \{\} <br /> |


##### Meter



Meter defines pricing adjustments for a specific meter



_Appears in:_
- [Pricing](#pricing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[MeterName](#metername)_ | Name is the name of the meter along with unit (e.g., "cpuHour", "ramGbHour"). |  | Enum: [subscription cpuHour gpuHour ramGbHour pvGbHour networkGb] <br />Required: \{\} <br /> |
| `margins` _[Margins](#margins)_ | Margins adjusts the price derived from raw usage for this meter.<br />You can specify either:<br />- absoluteMicros: an additive margin in micro-currency units (10^-6 of the currency), or<br />- factorMilli: a multiplicative factor in milli-units (1000 = 1.000x, 1020 = 1.020x). |  | Optional: \{\} <br /> |


##### MeterName

_Underlying type:_ _string_

MeterName defines the name of a usage meter for pricing adjustments

_Validation:_
- Enum: [subscription cpuHour gpuHour ramGbHour pvGbHour networkGb]

_Appears in:_
- [CostMetric](#costmetric)
- [Meter](#meter)
- [ResolvedMeter](#resolvedmeter)

| Field | Description |
| --- | --- |
| `subscription` |  |
| `cpuHour` |  |
| `gpuHour` |  |
| `ramGbHour` |  |
| `pvGbHour` |  |
| `networkGb` | MeterNetworkGB bills total data transferred (transfer + receive) per GiB.<br />No time dimension — the rate is per-GB, not per-GB-hour — hence no "Hour".<br /> |


##### ObjectReference







_Appears in:_
- [Compatibility](#compatibility)
- [SubscriptionParent](#subscriptionparent)
- [SubscriptionSpec](#subscriptionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _string_ |  |  | Required: \{\} <br /> |
| `namespace` _string_ | Namespace of the referenced object. Must be set explicitly — references are<br />never resolved against the referrer's namespace, so the same reference always<br />means the same object no matter where it is authored. MinLength guards against<br />an empty string, which +required alone would accept. |  | MinLength: 1 <br />Required: \{\} <br /> |


##### Offering



Offering describes a cost driving entity
It owns the rules for how the base cost for that entity is collected and calculated





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `finops.stakater.com/v1alpha1` | | |
| `kind` _string_ | `Offering` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[OfferingSpec](#offeringspec)_ |  |  |  |
| `status` _[OfferingStatus](#offeringstatus)_ |  |  |  |


##### OfferingSpec



OfferingSpec defines the desired state of Offering.



_Appears in:_
- [Offering](#offering)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `pricing` _[Pricing](#pricing)_ | Pricing specifies how the price for this offering is calculated |  | Required: \{\} <br /> |
| `compatibility` _[Compatibility](#compatibility)_ | Compatibility can be used for ensuring that any subscription created for this offering<br />has the required offerings in its parents or siblings |  | Optional: \{\} <br /> |
| `lifecycle` _[Lifecycle](#lifecycle)_ | Lifecycle defines how subscriptions to this offering behave during certain lifecycle events |  | Optional: \{\} <br /> |


##### OfferingStatus



OfferingStatus defines the observed state of Offering.



_Appears in:_
- [Offering](#offering)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resolvedPricing` _[ResolvedPricing](#resolvedpricing)_ | ResolvedPricing contains the effective pricing derived from the offering spec |  | Optional: \{\} <br /> |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Conditions represent the latest available observations of the Offering's state |  | Optional: \{\} <br /> |
| `ready` _[ConditionStatus](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#conditionstatus-v1-meta)_ | Ready indicates whether the offering is ready to be subscribed to (i.e., all required offerings are present and no circular dependencies detected) |  |  |


##### OnPremOptions



OnPremOptions defines On-Premise specific options.



_Appears in:_
- [FinOpsProviderSpec](#finopsproviderspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `pricingModelSource` _string_ | PricingModelSource indicates how the pricing model is provided to OpenCost.<br />e.g., "Pricebook" if derived from PriceBook CRs. |  | Optional: \{\} <br /> |


##### ParentDeactivateAction

_Underlying type:_ _string_

ParentDeactivateAction defines the behavior when a parent subscription is deactivated.

_Validation:_
- Enum: [Deactivate Orphan]

_Appears in:_
- [Lifecycle](#lifecycle)
- [SubscriptionLifecycle](#subscriptionlifecycle)

| Field | Description |
| --- | --- |
| `Deactivate` |  |
| `Orphan` |  |


##### PriceBook



PriceBook is the Schema for the pricebooks API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `finops.stakater.com/v1alpha1` | | |
| `kind` _string_ | `PriceBook` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[PriceBookSpec](#pricebookspec)_ |  |  |  |
| `status` _[PriceBookStatus](#pricebookstatus)_ |  |  |  |


##### PriceBookSpec



PriceBookSpec defines the desired state of PriceBook



_Appears in:_
- [PriceBook](#pricebook)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `currency` _string_ | The base currency for financial reporting and calculations (e.g., EUR, USD). |  | Pattern: `^[A-Z]\{3\}$` <br />Required: \{\} <br /> |
| `valuationMode` _string_ | The mode of valuation - either 'currency' for direct monetary rates or 'percent' for weighted scoring. |  | Enum: [currency percent] <br />Required: \{\} <br /> |
| `rates` _[PriceRates](#pricerates)_ | Rates used for valuation in 'currency' mode. Defines cost per unit of resource. Required if valuationMode is 'currency'. |  | Optional: \{\} <br /> |


##### PriceBookStatus



PriceBookStatus defines the observed state of PriceBook



_Appears in:_
- [PriceBook](#pricebook)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `active` _boolean_ | Active indicates whether this PriceBook instance is currently designated as the active one<br />used for pricing calculations. This field is managed by the operator. |  | Optional: \{\} <br /> |
| `ready` _[ConditionStatus](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#conditionstatus-v1-meta)_ | Ready indicates whether this PriceBook's rates are valid and it is usable<br />for pricing resolution. Managed by the operator. |  | Optional: \{\} <br /> |
| `observedGeneration` _integer_ | ObservedGeneration reflects the generation of the most recently observed spec. |  | Optional: \{\} <br /> |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Conditions represent the latest available observations of the PriceBook's state. |  | Optional: \{\} <br /> |
| `activePricing` _object (keys:string, values:string)_ | ActivePricing mirrors the OpenCost custom-pricing document (default.json)<br />this PriceBook has applied to OpenCost. Populated only on the active, ready<br />PriceBook (the one driving OpenCost); nil on every other PriceBook.<br />Managed by the operator. |  | Optional: \{\} <br /> |


##### PriceRates



PriceRates defines the cost rates for different resources. Each rate is a
non-negative decimal string (e.g. "0.031"); empty means "unset". The pattern
`^([0-9]+(\.[0-9]+)?)?$` rejects malformed values at admission while allowing
empty.



_Appears in:_
- [PriceBookSpec](#pricebookspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `cpuHour` _string_ | Cost per vCPU-hour (e.g., 0.031). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |
| `spotCPUHour` _string_ | Cost per vCPU-hour (e.g., 0.031). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |
| `ramGbHour` _string_ | Cost per GB-hour of RAM (e.g., 0.004). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |
| `spotRAMGbHour` _string_ | Cost per GB-hour of spotRAM (e.g., 0.004). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |
| `pvGbHour` _string_ | Cost per GB-hour of Persistent Volume (e.g., 0.00012). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |
| `gpuHour` _string_ | Cost per GPU-hour (e.g., 1.8). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |
| `networkGiB` _string_ | Cost per GiB of network data transferred (e.g., 0.09). |  | Pattern: `^([0-9]+(\.[0-9]+)?)?$` <br />Optional: \{\} <br /> |


##### Pricing



Pricing defines pricing rules for the offering



_Appears in:_
- [OfferingSpec](#offeringspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resourcePricing` _[Meter](#meter) array_ | ResourcePricing defines per-meter pricing adjustments applied to raw usage.<br />Each meter can optionally define:<br />- includedUsage: an amount of usage included for free per subscription (same unit as the meter)<br />- margins: either an absolute add-on (in micro-currency) or a multiplicative factor (in milli-units) |  | Optional: \{\} <br /> |
| `subscriptionFee` _[SubscriptionFee](#subscriptionfee)_ | SubscriptionFee defines the recurring fee charged for the subscription being active,<br />independent of resource usage |  | Optional: \{\} <br /> |


##### ResolvedIncludedUsage



ResolvedIncludedUsage contains the resolved included usage with its unit of measurement



_Appears in:_
- [ResolvedMeter](#resolvedmeter)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `value` _integer_ | Value is the amount of free usage included per subscription |  |  |
| `unit` _string_ | Unit is the unit of measurement (e.g., "GbHour", "CoreHour") |  |  |


##### ResolvedMeter



ResolvedMeter contains the effective per-unit price for a specific meter



_Appears in:_
- [ResolvedPricing](#resolvedpricing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `name` _[MeterName](#metername)_ | Name is the meter name (e.g., "cpuHour", "ramGbHour") |  | Enum: [subscription cpuHour gpuHour ramGbHour pvGbHour networkGb] <br />Required: \{\} <br /> |
| `unitPriceMicros` _integer_ | UnitPriceMicros is the effective per-unit price in micro-currency units (10^-6) |  |  |
| `includedUsage` _[ResolvedIncludedUsage](#resolvedincludedusage)_ | IncludedUsage is the free usage included per subscription for this meter |  | Optional: \{\} <br /> |


##### ResolvedPricing



ResolvedPricing contains the effective pricing that consumers see.
It is derived from the offering spec and stamped on status during reconciliation.



_Appears in:_
- [OfferingStatus](#offeringstatus)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resolvedAt` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | ResolvedAt is the timestamp when pricing was last resolved |  |  |
| `meters` _[ResolvedMeter](#resolvedmeter) array_ | Meters contains per-meter resolved unit prices after margins are applied.<br />Empty when no resource pricing is configured. |  |  |
| `subscriptionFee` _[SubscriptionFee](#subscriptionfee)_ | SubscriptionFee contains the resolved subscription fee, if configured |  | Optional: \{\} <br /> |


##### Subscription



Subscription is the Schema for the subscriptions API.





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `finops.stakater.com/v1alpha1` | | |
| `kind` _string_ | `Subscription` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[SubscriptionSpec](#subscriptionspec)_ |  |  |  |
| `status` _[SubscriptionStatus](#subscriptionstatus)_ |  |  |  |


##### SubscriptionFee



SubscriptionFee defines the recurring fee charged for the subscription being active,
independent of resource usage.

Billing model:
- The fee accrues over time in discrete "ticks" of length `period`.
- Each tick contributes `priceMicros` to the total.
- Ticks are aligned according to `tickAlignment`.

Tick alignment:
  - ActivatedAt: ticks start at status.activatedAt (tick boundaries are: activatedAt + N*period).
    Best for per-subscription billing cycles (common for add-ons).
  - HourBoundary / DayBoundary / MonthBoundary: ticks align to wall-clock boundaries.
    Best for synchronized billing windows across subscriptions (common for reporting).

Charging rule (deterministic per time window):
For a time bucket [start, endExclusive), the subscription fee charged in that bucket is:

	ticks(t) = number of full tick boundaries strictly before time t
	feeInBucket = priceMicros * (ticks(endExclusive) - ticks(start))

This ensures exports are idempotent: the same [start, endExclusive) always yields the same fee.

Minimum commitment (minPeriods):
  - minPeriods defines the minimum number of periods to bill once the subscription becomes active.
  - If the subscription deactivates before minPeriods have elapsed, the remaining periods are billed
    as an adjustment at deactivation time, so the total billed periods is at least minPeriods.

All monetary values are expressed in micro-currency units (10^-6 of the currency).



_Appears in:_
- [Pricing](#pricing)
- [ResolvedPricing](#resolvedpricing)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `period` _string_ | Period is the tick interval. Its interpretation depends on tickAlignment:<br />  - ActivatedAt: a Go duration string (e.g., "1h", "30m", "24h").<br />  - HourBoundary: an integer number of hours (e.g., "1", "2").<br />  - DayBoundary: an integer number of days (e.g., "1", "7").<br />  - MonthBoundary: an integer number of months (e.g., "1", "3", "12"). |  |  |
| `tickAlignment` _[TickAlignment](#tickalignment)_ | TickAlignment defines where tick boundaries occur.<br />ActivatedAt: ticks start at status.activatedAt (tick boundaries are: activatedAt + N*period).<br />Best for per-subscription billing cycles (common for add-ons).<br />HourBoundary / DayBoundary / MonthBoundary: ticks align to wall-clock boundaries.<br />Best for synchronized billing windows across subscriptions (common for reporting).<br />For boundary-aligned modes, the first tick after activation covers a partial period<br />and is prorated: charge = priceMicros * actualDuration / periodDuration.<br />For MonthBoundary, the period duration denominator is a fixed 365.25/12 days (30.4375 days). |  | Enum: [ActivatedAt HourBoundary DayBoundary MonthBoundary] <br /> |
| `minPeriods` _integer_ | MinPeriods is the minimum number of full tick periods before deletion is allowed.<br />The collection job keeps the subscription finalizer until at least minPeriods ticks<br />have elapsed since activation. The subscription continues accruing charges normally<br />until the finalizer is removed. |  | Minimum: 1 <br />Optional: \{\} <br /> |
| `priceMicros` _integer_ | PriceMicros is the price per tick, in micro-currency units |  | Minimum: 1 <br />Required: \{\} <br /> |


##### SubscriptionLifecycle







_Appears in:_
- [SubscriptionSpec](#subscriptionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `onParentDeactivate` _[ParentDeactivateAction](#parentdeactivateaction)_ | OnParentDeactivate controls what happens when the parent subscription deactivates:<br />- Deactivate: this subscription also deactivates.<br />- Orphan: this subscription stays active independently, while retaining the parent reference for traceability.<br />Orphan only detaches the parent lifecycle link; compatibility requirements are still enforced.<br />An orphan whose required offering was covered only by the now-deactivated parent (and by no<br />active sibling) is still deactivated, because keeping it active would violate the requirement. | Deactivate | Enum: [Deactivate Orphan] <br /> |
| `targetRef` _[TargetReference](#targetreference)_ | TargetRef ties the lifecycle of the subscription to a target resource.<br />The subscription will not activate until the target status is Ready.<br />When the target is deleted, the subscription will be deactivated. |  | Optional: \{\} <br /> |


##### SubscriptionParent







_Appears in:_
- [SubscriptionSpec](#subscriptionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `subscriptionRef` _[ObjectReference](#objectreference)_ | SubscriptionRef is a reference to the parent subscription. |  | Required: \{\} <br /> |


##### SubscriptionSpec



SubscriptionSpec defines the desired state of Subscription.
A Subscription creates a binding to an Offering, starting the clock and instantiating the offering.
Effectively it starts consuming the cost-driving entity from a billing perspective.

offeringRef and parent are immutable: both determine what the subscription is
billed for and which subscriptions provide its compatibility coverage, and a
subscription's activation is a billing epoch that cannot be re-pointed.



_Appears in:_
- [Subscription](#subscription)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `offeringRef` _[ObjectReference](#objectreference)_ | OfferingRef is the reference to the Offering which is being subscribed to. |  | Required: \{\} <br /> |
| `parent` _[SubscriptionParent](#subscriptionparent)_ | Parent is an optional reference to a parent subscription for traceability.<br />For example, a storage subscription attached to a VM would reference the VM subscription. |  | Optional: \{\} <br /> |
| `usageSources` _[UsageSource](#usagesource) array_ | UsageSources defines from where the data for the resource usage of this subscription comes. |  | Optional: \{\} <br /> |
| `lifecycle` _[SubscriptionLifecycle](#subscriptionlifecycle)_ | Lifecycle allows overriding lifecycle behavior if the Offering permits it.<br />If both parent and targetRef are set:<br />- activation requires BOTH (parent active AND target Ready)<br />- deactivation happens if EITHER stops applying, except parent deactivation is ignored when onParentDeactivate=Orphan<br />Note: onParentDeactivate=Orphan only governs the parent lifecycle link. It does not<br />exempt the subscription from its offering's compatibility requirements: if the deactivating<br />parent was the only active provider of a required offering, the subscription is still<br />deactivated for the coverage gap. |  | Optional: \{\} <br /> |


##### SubscriptionStatus



SubscriptionStatus defines the observed state of Subscription.
Non-active subscriptions are ignored by scrape jobs.
A subscription becomes active when:
- parent.SubscriptionRef is set and the parent is active, and/or
- targetRef is set and the target is Ready.
Unset references are ignored. If neither reference is set, the subscription activates after spec validation.



_Appears in:_
- [Subscription](#subscription)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `ready` _[ConditionStatus](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#conditionstatus-v1-meta)_ | Ready indicates whether the subscription is active and ready. |  |  |
| `activatedAt` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | ActivatedAt is the time when the subscription became active. |  | Optional: \{\} <br /> |
| `deactivatedAt` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | DeactivatedAt is the time when the subscription was deactivated. |  | Optional: \{\} <br /> |
| `compatibilityRoot` _string_ | CompatibilityRoot is the metadata.uid of this subscription's root ancestor,<br />resolved once by the controller. It identifies the connected family used<br />for compatibility coverage. |  | Optional: \{\} <br /> |
| `costs` _[CostBucket](#costbucket) array_ | Costs contains rolling cost summaries for the current hour, day, and month.<br />When populated, contains exactly 3 entries — one per granularity.	// +optional |  |  |
| `conditions` _[Condition](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#condition-v1-meta) array_ | Conditions represent the latest available observations of the Subscription's state. |  | Optional: \{\} <br /> |


##### TargetReference







_Appears in:_
- [SubscriptionLifecycle](#subscriptionlifecycle)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | APIVersion is the API version of the target resource. |  |  |
| `kind` _string_ | Kind is the kind of the target resource. |  |  |
| `namespace` _string_ | Namespace is the namespace of the target resource. |  | Optional: \{\} <br /> |
| `name` _string_ | Name is the name of the target resource. |  |  |


##### TickAlignment

_Underlying type:_ _string_

TickAlignment defines where tick boundaries occur for subscription fee billing.

_Validation:_
- Enum: [ActivatedAt HourBoundary DayBoundary MonthBoundary]

_Appears in:_
- [SubscriptionFee](#subscriptionfee)

| Field | Description |
| --- | --- |
| `ActivatedAt` | ActivatedAt: ticks start at status.activatedAt (tick boundaries are: activatedAt + N*period).<br />Best for per-subscription billing cycles (common for add-ons).<br /> |
| `HourBoundary` | HourBoundary ticks align to wall-clock hour boundaries (e.g., 1:00, 2:00, etc.).<br /> |
| `DayBoundary` | DayBoundary ticks align to wall-clock day boundaries (e.g., 1 calender day).<br /> |
| `MonthBoundary` | MonthBoundary ticks align to wall-clock month boundaries (e.g., 1st of each month).<br /> |


##### UsageSource







_Appears in:_
- [SubscriptionSpec](#subscriptionspec)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `resourceType` _string_ | ResourceType is the type of resource to track (e.g., Deployment, StatefulSet, Pod). |  | Enum: [Deployment StatefulSet Pod DaemonSet Job CronJob ReplicaSet] <br /> |
| `name` _string_ | Name is the name of the specific resource instance. |  | Optional: \{\} <br /> |
| `namespace` _string_ | Namespace is the namespace of the resource. |  | Optional: \{\} <br /> |

## Hibernation Operator

<!-- markdownlint-disable -->

### Packages
- [hibernation.stakater.com/v1beta1](#hibernationstakatercomv1beta1)


### hibernation.stakater.com/v1beta1


#### Resource Types
- [ClusterResourceSupervisor](#clusterresourcesupervisor)
- [ResourceSupervisor](#resourcesupervisor)



##### ClusterResourceSupervisor



ClusterResourceSupervisor is the Schema for the resourcesupervisors API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `hibernation.stakater.com/v1beta1` | | |
| `kind` _string_ | `ClusterResourceSupervisor` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[ClusterResourceSupervisorSpec](#clusterresourcesupervisorspec)_ |  |  |  |
| `status` _[ClusterResourceSupervisorStatus](#clusterresourcesupervisorstatus)_ |  |  |  |




##### ClusterResourceSupervisorSpec



ClusterResourceSupervisorSpec defines the desired state of ClusterResourceSupervisor



_Appears in:_
- [ClusterResourceSupervisor](#clusterresourcesupervisor)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `schedule` _Hibernation_ |  |  | Required: \{\} <br /> |
| `namespaces` _Namespaces_ | Namespaces is a list of namespaces to which the schedule will be applied |  | Optional: \{\} <br /> |
| `argocd` _ArgoCDHibernation_ | ArgoCD contains details about ArgoCD to which the schedule will be applied |  |  |


##### ClusterResourceSupervisorStatus



ClusterResourceSupervisorStatus defines the observed state of ClusterResourceSupervisor



_Appears in:_
- [ClusterResourceSupervisor](#clusterresourcesupervisor)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `nextReconcileTime` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | NextReconcileTime contains the next time at which the namespace resources will sleep or wake up |  |  |
| `currentStatus` _[Status](#status)_ | CurrentStatus shows the state the tenant's resources |  | Enum: [sleeping running error] <br /> |
| `sleepingNamespaces` _SleepingNamespace array_ | SleepingResources contains the previous states for each of the deployments currently scaled down |  |  |
| `watchedNamespaces` _string array_ | WatchedNamespaces contains the list of namespaces that are being watched by the ClusterResourceSupervisor |  |  |
| `ignoreNamespaces` _string array_ | IgnoreNamespaces contains the list of namespaces that are being ignored by the ClusterResourceSupervisor |  |  |


##### ResourceSupervisor



ResourceSupervisor is the Schema for the resourcesupervisors API





| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `apiVersion` _string_ | `hibernation.stakater.com/v1beta1` | | |
| `kind` _string_ | `ResourceSupervisor` | | |
| `metadata` _[ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#objectmeta-v1-meta)_ | Refer to Kubernetes API documentation for fields of `metadata`. |  |  |
| `spec` _[ResourceSupervisorSpec](#resourcesupervisorspec)_ |  |  |  |
| `status` _[ResourceSupervisorStatus](#resourcesupervisorstatus)_ |  |  |  |




##### ResourceSupervisorSpec



ResourceSupervisorSpec defines the desired state of ResourceSupervisor API



_Appears in:_
- [ResourceSupervisor](#resourcesupervisor)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `schedule` _Hibernation_ |  |  | Required: \{\} <br /> |


##### ResourceSupervisorStatus



ResourceSupervisorStatus defines the observed state of ResourceSupervisor



_Appears in:_
- [ResourceSupervisor](#resourcesupervisor)

| Field | Description | Default | Validation |
| --- | --- | --- | --- |
| `nextReconcileTime` _[Time](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.30/#time-v1-meta)_ | NextReconcileTime contains the next time at which the namespace resources will sleep or wake up |  |  |
| `currentStatus` _[Status](#status)_ | CurrentStatus shows the state the tenant's resources |  | Enum: [sleeping running error] <br /> |


##### Status

_Underlying type:_ _string_



_Validation:_
- Enum: [sleeping running error]

_Appears in:_
- [ClusterResourceSupervisorStatus](#clusterresourcesupervisorstatus)
- [ResourceSupervisorStatus](#resourcesupervisorstatus)
