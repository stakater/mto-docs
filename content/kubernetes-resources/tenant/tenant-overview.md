# Tenant

A minimal Tenant definition requires only a quota field, essential for limiting resource consumption:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: alpha
spec:
  quota: small
```

For a more comprehensive setup, a detailed Tenant definition includes various configurations:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: tenant-sample
spec:
  quota: small
  accessControl:
    owners:
      users:
        - kubeadmin
      groups:
        - admin-group
    editors:
      users:
        - devuser1
        - devuser2
      groups:
        - dev-group
    viewers:
      users:
        - viewuser
      groups:
        - view-group
  hibernation:
  # UTC time
    sleepSchedule: "20 * * * *"
    wakeSchedule: "40 * * * *"        
  namespaces:
    sandboxes:
      enabled: true
      private: true
    withoutTenantPrefix:
      - analytics
      - marketing
    withTenantPrefix:
      - dev
      - staging
    onDeletePurgeNamespaces: true
    metadata:
      common:
        labels:
          common-label: common-value
        annotations:
          common-annotation: common-value
      sandbox:
        labels:
          sandbox-label: sandbox-value
        annotations:
          sandbox-annotation: sandbox-value
      specific:
        - namespaces:
            - tenant-sample-dev
          labels:
            specific-label: specific-dev-value
          annotations:
            specific-annotation: specific-dev-value
  desc: "This is a sample tenant setup for the v1beta3 version."
  storageClasses:
    allowed:
      - staging
      - dev
  ingressClasses:
    allowed:
      - nginx
      - trafeik
  serviceAccounts:
    denied:
      - service-user-1
      - service-user-2

```

## Access Control

Structured access control is critical for managing roles and permissions within a tenant effectively. It divides users into three categories, each with customizable privileges. This design enables precise role-based access management.  

These roles are obtained from [IntegrationConfig's TenantRoles field](../integration-config.md#tenantroles).
  
* `Owners`: Have full administrative rights, including resource management and namespace creation. Their roles are crucial for high-level management tasks.
* `Editors`: Granted permissions to modify resources, enabling them to support day-to-day operations without full administrative access.
* `Viewers`: Provide read-only access, suitable for oversight and auditing without the ability to alter resources.

Users and groups are linked to these roles by specifying their usernames or group names in the respective fields under `owners`, `editors`, and `viewers`.

## Quota

The `quota` field sets the resource limits for the tenant, such as CPU and memory usage, to prevent any single tenant from consuming a disproportionate amount of resources. This mechanism ensures efficient resource allocation and fosters fair usage practices across all tenants.  

For more information on quotas, please refer [here](../quota.md).

## Namespaces

Controls the creation and management of namespaces within the tenant:

* `sandboxes`:
    * When enabled, sandbox namespaces are created with the following naming convention - **{TenantName}**-**{UserName}**-*sandbox*.
    * In case of groups, the sandbox namespaces will be created for each member of the group.
    * Setting `private` to *true* will make the sandboxes visible only to the user they belong to. By default, sandbox namespaces are visible to all tenant members.

* `withoutTenantPrefix`: Lists the namespaces to be created without automatically prefixing them with the tenant name, useful for shared or common resources.
* `withTenantPrefix`: Namespaces listed here will be prefixed with the tenant name, ensuring easy identification and isolation.
* `onDeletePurgeNamespaces`: Determines whether namespaces associated with the tenant should be deleted upon the tenant's deletion, enabling clean up and resource freeing.
* `metadata`: Configures metadata like labels and annotations that are applied to namespaces managed by the tenant:
    * `common`: Applies specified labels and annotations across all namespaces within the tenant, ensuring consistent metadata for resources and workloads.
    * `sandbox`: Special metadata for sandbox namespaces, which can include templated annotations or labels for dynamic information.
        * We also support the use of a templating mechanism within annotations, specifically allowing the inclusion of the tenant's username through the placeholder `{{ TENANT.USERNAME }}`. This template can be utilized to dynamically insert the tenant's username value into annotations, for example, as `username: {{ TENANT.USERNAME }}`.
    * `specific`: Allows applying unique labels and annotations to specified tenant namespaces, enabling custom configurations for particular workloads or environments.

## Hibernation

`hibernation` allows for the scheduling of inactive periods for namespaces associated with the tenant, effectively putting them into a "sleep" mode. This capability is designed to conserve resources during known periods of inactivity.

* Configuration for this feature involves two key fields, `sleepSchedule` and `wakeSchedule`, both of which accept strings formatted according to cron syntax.
* These schedules dictate when the namespaces will automatically transition into and out of hibernation, aligning resource usage with actual operational needs.

## Description

`desc` provides a human-readable description of the tenant, aiding in documentation and at-a-glance understanding of the tenant's purpose and configuration.

> ⚠️ If same label or annotation key is being applied using different methods provided, then the highest precedence will be given to `namespaces.metadata.specific` followed by `namespaces.metadata.common` and in the end would be the ones applied from `openshift.project.labels`/`openshift.project.annotations` in `IntegrationConfig`

## Storage

```yaml
storageClasses:
  allowed:
    - staging-fast
    - shared
```

* `allowed` can be used to limit a tenant to only being able to create PersistentVolumeClaims for StorageClasses in the list. If `storageClass` is not specified for a PersistentVolumeClaim, the default StorageClass (if set) will be evaluated as any other class name. If the default StorageClass is not set, the evaluation will be deferred until a default StorageClass is set. `""` is evaluated as any other class name, so if you are using it to manually bind to PersistentVolumes while using StorageClass filtering you need to add  an empty string `""` to the tenants allow-list or it will get filtered.

## Ingress

!!! note
    This field is applicable only for Kubernetes. For more information, refer to the [Ingress Sharding Guide](../tenant/how-to-guides/ingress-sharding.md).

* `allowed` restricts a tenant to creating Ingress resources only with the specified IngressClasses. The empty string `""` is treated like any other IngressClass name. If you use it while filtering IngressClasses, you must include `""` in the tenant's allow-list, or it will be filtered out. If no IngressClass is specified for an Ingress resource, it will be treated as `""`.

```yaml
ingressClasses:
  allowed:
  - nginx
  - traefik
```

## Service Accounts

* `denied` restricts the tenant from using the specified service accounts in pods, deployments, and other resources. The empty string `""` or no service account name is provided then it is treated as `default` service account name. `default` must be added to denied list if you want to block pods / pod controllers with default or empty service account

The creation of following resources will be blocked if a denied service account is provided:

* Pods
* Deployments
* StatefulSets
* ReplicaSets
* Jobs
* CronJobs
* Daemonsets

```yaml
serviceAccounts:
  denied:
    - service-user-1
    - service-user-2
```
