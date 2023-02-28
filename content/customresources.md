# Custom Resources

Multi Tenant Operator defines the following 5 Custom Resources:

[[toc]]

## 1. Quota

Cluster scoped resource:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: Quota
metadata:
  name: medium
  annotations:
    quota.tenantoperator.stakater.com/is-default: "false"
spec:
  resourcequota:
    hard:
      requests.cpu: '5'
      limits.cpu: '10'
      requests.memory: '5Gi'
      limits.memory: '10Gi'
      configmaps: "10"
      persistentvolumeclaims: "4"
      replicationcontrollers: "20"
      secrets: "10"
      services: "10"
      services.loadbalancers: "2"
  limitrange:
    limits:
      - type: "Pod"
        max:
          cpu: "2"
          memory: "1Gi"
        min:
          cpu: "200m"
          memory: "100Mi"
      - type: "Container"
        max:
          cpu: "2"
          memory: "1Gi"
        min:
          cpu: "100m"
          memory: "50Mi"
        default:
          cpu: "300m"
          memory: "200Mi"
        defaultRequest:
          cpu: "200m"
          memory: "100Mi"
        maxLimitRequestRatio:
          cpu: "10"
```

When several tenants share a single cluster with a fixed number of resources, there is a concern that one tenant could use more than its fair share of resources. Quota is a wrapper around OpenShift `ClusterResourceQuota` and `LimitRange` which provides administrators to limit resource consumption per `Tenant`.
For more details [Quota.Spec](https://kubernetes.io/docs/concepts/policy/resource-quotas/) , [LimitRange.Spec](https://kubernetes.io/docs/concepts/policy/limit-range/)

## 2. Tenant

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
      - haseeb@stakater.com
    groups: # optional
      - alpha
  editors: # optional
    users: # optional
      - hanzala@stakater.com
  viewers: # optional
    users: # optional
      - jose@stakater.com
  quota: medium # required
  sandboxConfig: # optional
    enabled: true # optional
    private: true # optional
  onDelete: # optional
    cleanNamespaces: true # optional
    cleanAppProject: false # optional
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
        stakater.com/user: haseeb
      labels: # optional
        stakater.com/sandbox: true
      namespaces: # optional
        - alpha-haseeb-stakater-sandbox
  templateInstances: # optional
  - spec: # optional
      template: networkpolicy # required
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
    * For more details, check out [their definitions](./tenant-roles.md).

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

* Tenant automatically deploys `template` resource mentioned in `templateInstances` to matching tenant namespaces.
    * `Template` resources are created in those `namespaces` which belong to a `tenant` and contain `matching labels`.
    * `Template` resources are created in all `namespaces` of a `tenant` if `selector` field is empty.

> ⚠️ If same label or annotation key is being applied using different methods provided, then the highest precedence will be given to `specificMetadata` followed by `commonMetadata` and in the end would be the ones applied from `openshift.project.labels`/`openshift.project.annotations` in `IntegrationConfig`

## 3. Template

Cluster scoped resource:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: redis
resources:
  helm:
    releaseName: redis
    chart:
      repository:
        name: redis
        repoUrl: https://charts.bitnami.com/bitnami
    values: |
      redisPort: 6379
---
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: networkpolicy
parameters:
  - name: CIDR_IP
    value: "172.17.0.0/16"
resources:
  manifests:
    - kind: NetworkPolicy
      apiVersion: networking.k8s.io/v1
      metadata:
        name: deny-cross-ns-traffic
      spec:
        podSelector:
          matchLabels:
            role: db
        policyTypes:
        - Ingress
        - Egress
        ingress:
        - from:
          - ipBlock:
              cidr: "${{CIDR_IP}}"
              except:
              - 172.17.1.0/24
          - namespaceSelector:
              matchLabels:
                project: myproject
          - podSelector:
              matchLabels:
                role: frontend
          ports:
          - protocol: TCP
            port: 6379
        egress:
        - to:
          - ipBlock:
              cidr: 10.0.0.0/24
          ports:
          - protocol: TCP
            port: 5978
---
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Template
metadata:
  name: resource-mapping
resources:
  resourceMappings:
    secrets:
      - name: secret-s1
        namespace: namespace-n1
    configMaps:
      - name: configmap-c1
        namespace: namespace-n2
```

Templates are used to initialize Namespaces, share common resources across namespaces, and map secrets/configmaps from one namespace to other namespaces.

* They either contain one or more Kubernetes manifests, a reference to secrets/configmaps, or a Helm chart.
* They are being tracked by TemplateInstances in each Namespace they are applied to.
* They can contain pre-defined parameters such as ${namespace}/${tenant} or user-defined ${MY_PARAMETER} that can be specified within an TemplateInstance.

Also you can define custom variables in `Template` and `TemplateInstance` . The parameters defined in `TemplateInstance` are overwritten the values defined in `Template` .

Manifest Templates: The easiest option to define a Template is by specifying an array of Kubernetes manifests which should be applied when the Template is being instantiated.

Helm Chart Templates: Instead of manifests, a Template can specify a Helm chart that will be installed (using Helm template) when the Template is being instantiated.

Resource Mapping Templates: A template can be used to map secrets and configmaps from one tenant's namespace to another tenant's namespace, or within a tenant's namespace.

### Mandatory and Optional Templates

 Templates can either be mandatory or optional. By default, all Templates are optional. Cluster Admins can make Templates mandatory by adding them to the `spec.templateInstances` array within the Tenant configuration. All Templates listed in `spec.templateInstances` will always be instantiated within every `Namespace` that is created for the respective Tenant.

## 4. TemplateInstance

Namespace scoped resource:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateInstance
metadata:
  name: redis-instance
  namespace: build
spec:
  template: redis
  sync: false
```

TemplateInstance are used to keep track of resources created from Templates, which are being instantiated inside a Namespace.
Generally, a TemplateInstance is created from a Template and then the TemplateInstances will not be updated when the Template changes later on. To change this behavior, it is possible to set `spec.sync: true` in a TemplateInstance. Setting this option, means to keep this TemplateInstance in sync with the underlying template (similar to Helm upgrade).

## 5. TemplateGroupInstance

Cluster scoped resource:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: TemplateGroupInstance
metadata:
  name: redis-instance
spec:
  template: redis
  selector:
    matchLabels:
      app: redis
  sync: true
```

TemplateGroupInstance distributes a template across multiple namespaces which are selected by labelSelector.

## 6. ResourceSupervisor

Cluster scoped resource:

```yaml
apiVersion: tenantoperator.stakater.com/v1beta1
kind: ResourceSupervisor
metadata:
  name: tenant-sample
spec:
 argocd:
   appProjects:
     - tenant-sample
  hibernation:
    sleepSchedule: 23 * * * *
    wakeSchedule: 26 * * * *
  namespaces:
    - stage
    - dev
status:
  currentStatus: running
  nextReconcileTime: '2022-07-07T11:23:00Z'
```

The `ResourceSupervisor` is a resource created by MTO in case the [Hibernation](./hibernation.md) feature is enabled. The Resource manages the sleep/wake schedule of the namespaces owned by the tenant, and manages the previous state of any sleeping application. Currently, only StatefulSets and Deployments are put to sleep. Additionally, ArgoCD AppProjects that belong to the tenant have a `deny` SyncWindow added to them.

The `ResourceSupervisor` can be created both via the `Tenant` or manually. For more details, check some of its [use cases](./usecases/hibernation.md)

## Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    stakater.com/tenant: blue-sky
  name: build
```

* Namespace should have label `stakater.com/tenant` which contains the name of tenant to which it belongs to. The labels and annotations specified in the operator config,  `ocp.labels.project` and `ocp.annotations.project` are inserted in the namespace by the controller.

## Notes

* `tenant.spec.users.owner`: Can only create *Namespaces* with required *tenant label* and can delete *Projects*. To edit *Namespace* use `GitOps/ArgoCD`
