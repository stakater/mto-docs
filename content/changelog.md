# Changelog

## v0.8.x

### v0.8.3

- fix: Reconcile namespaces when the group spec for tenants is changed, so new rolebindings can be created for them

### v0.8.1

- fix: Updated release pipelines

### v0.8.0

- feat: Allow custom roles for each tenant via label selector, more details in [custom roles document](./usecases/custom-roles.md)
    - Roles mapping is a required field in [MTO's IntegrationConfig](./integration-config.md). By default, it will always be filled with OpenShift's admin/edit/view roles
    - Ensure that mentioned roles exist within the cluster
    - Remove coupling with OpenShift's built-in admin/edit/view roles
- feat: Removed coupling of ResourceSupervisor and Tenant resources
    - Added list of namespaces to hibernate within the ResourceSupervisor resource
    - Ensured that the same namespace cannot be added to two different Resource Supervisors
    - Moved ResourceSupervisor into a separate pod
    - Improved logs
- fix: Remove bug from tenant's common and specific metadata
- fix: Add missing field to Tenant's conversion webhook
- fix: Fix panic in ResourceSupervisor sleep functionality due to sending on closed channel
- chore: Update dependencies

## v0.7.x

### v0.7.4

- maintain: Automate certification of new MTO releases on RedHat's Operator Hub

### v0.7.3

- feat: Updated Tenant CR to provide Tenant level AppProject permissions

### v0.7.2

- feat: Add support to map secrets/configmaps from one namespace to other namespaces using TI. Secrets/configmaps will only be mapped if their namespaces belong to same Tenant

### v0.7.1

- feat: Add option to keep AppProjects created by Multi Tenant Operator in case Tenant is deleted. By default, AppProjects get deleted
- fix: Status now updates after namespaces are created
- maintain: Changes to Helm chart's default behaviour

### v0.7.0

- feat: Add support to map secrets/configmaps from one namespace to other namespaces using TGI. Resources can be mapped from one Tenant's namespaces to some other Tenant's namespaces
- feat: Allow creation of sandboxes that are private to the user
- feat: Allow creation of namespaces without tenant prefix from within tenant spec
- fix: Webhook changes will now be updated without manual intervention
- maintain: Updated Tenant CR version from v1beta1 to v1beta2. Conversion webhook is added to facilitate transition to new version
    - see [Tenant spec](./customresources.md#_2-tenant) for updated spec
- enhance: Better automated testing

## v0.6.x

### v0.6.1

- fix: Update MTO service-account name in environment variable

### v0.6.0

- feat: Add support to ArgoCD AppProjects created by Tenant Controller to have their sync disabled when relevant namespaces are hibernating
- feat: Add validation webhook for ResourceSupervisor
- fix: Delete ResourceSupervisor when hibernation is removed from tenant CR
- fix: CRQ and limit range not updating when quota changes
- fix: ArgoCD AppProjects created by Tenant Controller not updating when Tenant label is added to an existing namespace
- fix: Namespace workflow for TGI
- fix: ResourceSupervisor deletion workflow
- fix: Update RHSSO user filter for Vault integration
- fix: Update regex of namespace names in tenant CRD
- enhance: Optimize TGI and TI performance under load
- maintain: Bump Operator-SDK and Dependencies version

## v0.5.x

### v0.5.4

- fix: Update Helm dependency to v3.8.2

### v0.5.3

- fix: Add support for parameters in Helm chartRepository in templates

### v0.5.2

- fix: Add service name prefix for webhooks

### v0.5.1

- fix: ResourceSupervisor CR no longer requires a field for the Tenant name

### v0.5.0

- feat: Add support for tenant namespaces off-boarding. For more details check out [onDelete](./usecases/tenant.md#retaining-tenant-namespaces-when-a-tenant-is-being-deleted)
- feat: Add tenant webhook for spec validation

- fix: TemplateGroupInstance now cleans up leftover Template resources from namespaces that are no longer part of TGI namespace selector
- fix: Fixed hibernation sync issue

- enhance: Update tenant spec for applying common/specific namespace labels/annotations. For more details check out [commonMetadata & SpecificMetadata](./usecases/tenant.md#distributing-common-labels-and-annotations-to-tenant-namespaces-via-tenant-custom-resource)
- enhance: Add support for multi-pod architecture for Operator-Hub

- chore: Remove conversion webhook for Quota and Tenant

## v0.4.x

### v0.4.7

- feat: Add hibernation of StatefulSets and Deployments based on a timer
- feat: [New custom resource](./customresources.md#_6-resourcesupervisor) that handles hibernation

### v0.4.6

- fix: Revert v0.4.4

### v0.4.5

- feat: Add support for applying labels/annotation on specific namespaces

### v0.4.4

- fix: Update `privilegedNamespaces` regex

### v0.4.3

- fix: IntegrationConfig will now be synced in all pods

### v0.4.2

- feat: Added support to distribute common labels and annotations to tenant namespaces

### v0.4.1

- fix: Update dependencies to latest version

### v0.4.0

- feat: Controllers are now separated into individual pods

## v0.3.x

### v0.3.33

- fix: Optimize namespace reconciliation

### v0.3.33

- fix: Revert v0.3.29 change till webhook network issue isn't resolved

### v0.3.33

- fix: Execute webhook and controller of matching custom resource in same pod

### v0.3.30

- feat: Namespace controller will now trigger TemplateGroupInstance when a new matching namespace is created

### v0.3.29

- feat: Controllers are now separated into individual pods

### v0.3.28

- fix: Enhancement of TemplateGroupInstance Namespace event listener

### v0.3.27

- feat: TemplateGroupInstance will create resources instantly whenever a Namespace with matching labels is created

### v0.3.26

- fix: Update reconciliation frequency of TemplateGroupInstance

### v0.3.25

- feat: TemplateGroupInstance will now directly create template resources instead of creating TemplateInstances

#### Migrating from pervious version

- To migrate to Tenant-Operator:v0.3.25 perform the following steps
    - Downscale Tenant-Operator deployment by setting the replicas count to 0
    - Delete TemplateInstances created by TemplateGroupInstance (Naming convention of TemplateInstance created by TemplateGroupInstance is `group-{Template.Name}`)
    - Update version of Tenant-Operator to v0.3.25 and set the replicas count to 2. After Tenant-Operator pods are up TemplateGroupInstance will create the missing resources

### v0.3.24

- feat: Add feature to allow ArgoCD to sync specific cluster scoped custom resources, configurable via Integration Config. More details in [relevant docs](./integration-config.md#argocd)

### v0.3.23

- feat: Added concurrent reconcilers for template instance controller

### v0.3.22

- feat: Added validation webhook to prevent Tenant owners from creating RoleBindings with kind 'Group' or 'User'
- fix: Removed redundant logs for namespace webhook
- fix: Added missing check for users in a tenant owner's groups in namespace validation webhook
- fix: General enhancements and improvements

> ⚠️ Known Issues

- `caBundle` field in validation webhooks is not being populated for newly added webhooks. A temporary fix is to edit the validation webhook configuration manifest without the `caBundle` field added in any webhook, so OpenShift can add it to all fields simultaneously
    - Edit the `ValidatingWebhookConfiguration` `stakater-tenant-operator-validating-webhook-configuration` by removing all the `caBundle` fields of all webhooks
    - Save the manifest
    - Verify that all `caBundle` fields have been populated
    - Restart Tenant-Operator pods

### v0.3.21

- feat: Added ClusterRole manager rules extension

### v0.3.20

- fix: Fixed the recreation of underlying template resources, if resources were deleted

### v0.3.19

- feat: Namespace webhook FailurePolicy is now set to Ignore instead of Fail
- fix: Fixed config not being updated in namespace webhook when Integration Config is updated
- fix: Fixed a crash that occurred in case of ArgoCD in Integration Config was not set during deletion of Tenant resource

> ⚠️ ApiVersion `v1alpha1` of Tenant and Quota custom resources has been deprecated and is scheduled to be removed in the future. The following links contain the updated structure of both resources
>
> - [Quota v1beta1](./customresources.md#_1-quota)
> - [Tenant v1beta1](./customresources.md#_2-tenant)

### v0.3.18

- fix: Add ArgoCD namespace to destination namespaces for App Projects

### v0.3.17

- fix: Cluster administrator's permission will now have higher precedence on privileged namespaces

### v0.3.16

- fix: Add groups mentioned in Tenant CR to ArgoCD App Project manifests' RBAC

### v0.3.15

- feat: Add validation webhook for TemplateInstance & TemplateGroupInstance to prevent their creation in case the Template they reference does not exist

### v0.3.14

- feat: Added Validation Webhook for Quota to prevent its deletion when a reference to it exists in any Tenant
- feat: Added Validation Webhook for Template to prevent its deletion when a reference to it exists in any Tenant, TemplateGroupInstance or TemplateInstance
- fix: Fixed a crash that occurred in case Integration Config was not found

### v0.3.13

- feat: Multi Tenant Operator will now consider all namespaces to be managed if any default Integration Config is not found

### v0.3.12

- fix: General enhancements and improvements

### v0.3.11

- fix: Fix Quota's conversion webhook converting the wrong LimitRange field

### v0.3.10

- fix: Fix Quota's LimitRange to its intended design by being an optional field

### v0.3.9

- feat: Add ability to prevent certain resources from syncing via ArgoCD

### v0.3.8

- feat: Add default annotation to OpenShift Projects that show description about the Project

### v0.3.7

- fix: Fix a typo in Multi Tenant Operator's Helm release

### v0.3.6

- fix: Fix ArgoCD's `destinationNamespaces` created by Multi Tenant Operator

### v0.3.5

- fix: Change sandbox creation from 1 for each group to 1 for each user in a group

### v0.3.4

- feat: Support creation of sandboxes for each group

### v0.3.3

- feat: Add ability to create namespaces from a list of namespace prefixes listed in the Tenant CR

### v0.3.2

- refactor: Restructure Quota CR, more details in [relevant docs](./customresources.md#_1-quota)
- feat: Add support for adding LimitRanges in Quota
- feat: Add conversion webhook to convert existing v1alpha1 versions of quota to v1beta1

### v0.3.1

- feat: Add ability to create ArgoCD AppProjects per tenant, more details in [relevant docs](./usecases/argocd.md)

### v0.3.0

- feat: Add support to add groups in addition to users as tenant members

## v0.2.x

### v0.2.33

- refactor: Restructure Tenant spec, more details in [relevant docs](./customresources.md#_2-tenant)
- feat: Add conversion webhook to convert existing v1alpha1 versions of tenant to v1beta1

### v0.2.32

- refactor: Restructure integration config spec, more details in [relevant docs](./integration-config.md)
- feat: Allow users to input custom regex in certain fields inside of integration config, more details in [relevant docs](./integration-config.md#openshift)

### v0.2.31

- feat: Add limit range for `kube-RBAC-proxy`
