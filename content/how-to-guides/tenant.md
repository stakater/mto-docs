# Tenant

Cluster scoped resource:

The smallest valid Tenant definition is given below (with just one field in its spec):

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: alpha
spec:
  quota: small
```

Here is a more detailed Tenant definition, explained below:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta2
kind: Tenant
metadata:
  name: alpha
spec:
  owners: # optional
    users: # optional
      - dave@stakater.com
    groups: # optional
      - alpha
  editors: # optional
    users: # optional
      - jack@stakater.com
  viewers: # optional
    users: # optional
      - james@stakater.com
  quota: medium # required
  sandboxConfig: # optional
    enabled: true # optional
    private: true # optional
  onDelete: # optional
    cleanNamespaces: false # optional
    cleanAppProject: true # optional
  argocd: # optional
    sourceRepos: # required
      - https://github.com/stakater/gitops-config
    appProject: # optional
      clusterResourceWhitelist: # optional
        - group: tronador.stakater.com
          kind: Environment
      namespaceResourceBlacklist: # optional
        - group: ""
          kind: ConfigMap
  hibernation: # optional
    sleepSchedule: 23 * * * * # required
    wakeSchedule: 26 * * * * # required
  namespaces: # optional
    withTenantPrefix: # optional
      - dev
      - build
    withoutTenantPrefix: # optional
      - preview
  commonMetadata: # optional
    labels: # optional
      stakater.com/team: alpha
    annotations: # optional
      openshift.io/node-selector: node-role.kubernetes.io/infra=
  specificMetadata: # optional
    - annotations: # optional
        stakater.com/user: dave
      labels: # optional
        stakater.com/sandbox: true
      namespaces: # optional
        - alpha-dave-stakater-sandbox
  sandboxMetadata: # optional
    labels: # optional
      app.kubernetes.io/part-of: che.eclipse.org
    annotations: # optional
      che.eclipse.org/username: "{{ TENANT.USERNAME }}" # templatized placeholder
  templateInstances: # optional
  - spec: # optional
      template: networkpolicy # required
      sync: true  # optional
      parameters: # optional
        - name: CIDR_IP
          value: "172.17.0.0/16"
    selector: # optional
      matchLabels: # optional
        policy: network-restriction
```

* Tenant has 3 kinds of `Members`. Each member type should have different roles assigned to them. These roles are gotten from the [IntegrationConfig's TenantRoles field](integration-config.md#tenantroles). You can customize these roles to your liking, but by default the following configuration applies:
    * `Owners:` Users who will be owners of a tenant. They will have OpenShift admin-role assigned to their users, with additional access to create namespaces as well.
    * `Editors:` Users who will be editors of a tenant. They will have OpenShift edit-role assigned to their users.
    * `Viewers:` Users who will be viewers of a tenant. They will have OpenShift view-role assigned to their users.

* `Users` can be linked to the tenant by specifying there username in `owners.users`, `editors.users` and `viewers.users` respectively.

* `Groups` can be linked to the tenant by specifying the group name in `owners.groups`, `editors.groups` and `viewers.groups` respectively.

* Tenant will have a `Quota` to limit resource consumption.

* `sandboxConfig` is used to configure the tenant user sandbox feature
    * Setting `enabled` to *true* will create *sandbox namespaces* for owners and editors.
    * Sandbox will follow the following naming convention **{TenantName}**-**{UserName}**-*sandbox*.
    * In case of groups, the sandbox namespaces will be created for each member of the group.
    * Setting `private` to *true* will make those sandboxes be only visible to the user they belong to. By default, sandbox namespaces are visible to all tenant members

* `onDelete` is used to tell Multi Tenant Operator what to do when a Tenant is deleted.
    * `cleanNamespaces` if the value is set to **true** *MTO* deletes all *tenant namespaces* when a `Tenant` is deleted. Default value is **false**.
    * `cleanAppProject` will keep the generated ArgoCD AppProject if the value is set to **false**. By default, the value is **true**.

* `argocd` is required if you want to create an ArgoCD AppProject for the tenant.
    * `sourceRepos` contain a list of repositories that point to your GitOps.
    * `appProject` is used to set the `clusterResourceWhitelist` and `namespaceResourceBlacklist` resources. If these are also applied via `IntegrationConfig` then those applied via Tenant CR will have higher precedence for given Tenant.

* `hibernation` can be used to create a schedule during which the namespaces belonging to the tenant will be put to sleep. The values of the `sleepSchedule` and `wakeSchedule` fields must be a string in a cron format.

* Namespaces can also be created via tenant CR by *specifying names* in `namespaces`.
    * Multi Tenant Operator will append *tenant name* prefix while creating namespaces if the list of namespaces is under the `withTenantPrefix` field, so the format will be **{TenantName}**-**{Name}**.
    * Namespaces listed under the `withoutTenantPrefix` will be created with the given name. Writing down namespaces here that already exist within the cluster are not allowed.
    * `stakater.com/kind: {Name}` label will also be added to the namespaces.

* `commonMetadata` can be used to distribute common labels and annotations among tenant namespaces.
    * `labels` distributes provided labels among all tenant namespaces
    * `annotations` distributes provided annotations among all tenant namespaces

* `specificMetadata` can be used to distribute specific labels and annotations among specific tenant namespaces.
    * `labels` distributes given labels among specific tenant namespaces
    * `annotations` distributes given annotations among specific tenant namespaces
    * `namespaces` consists a list of specific tenant namespaces across which the labels and annotations will be distributed

* `sandboxMetadata` can be used to distribute specific labels and annotations among all tenant sandbox namespaces.
    * `labels` distributes given labels among tenant sandbox namespaces
    * `annotations` distributes given annotations among tenant sandbox namespaces. In annotations, we also support a username template `{{ TENANT.USERNAME }}`, it can be used if you want to access tenant username value in annotation i.e. `username: {{ TENANT.USERNAME }}`. This template can be used for sandboxMetadata labels as well, given that username is valid for a label value.

* Tenant automatically deploys `template` resource mentioned in `templateInstances` to matching tenant namespaces.
    * `Template` resources are created in those `namespaces` which belong to a `tenant` and contain `matching labels`.
    * `Template` resources are created in all `namespaces` of a `tenant` if `selector` field is empty.

> ⚠️ If same label or annotation key is being applied using different methods provided, then the highest precedence will be given to `specificMetadata` followed by `commonMetadata` and in the end would be the ones applied from `openshift.project.labels`/`openshift.project.annotations` in `IntegrationConfig`
