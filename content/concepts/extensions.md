# Extensions

A tenant boundary that stops at the Kubernetes API is only half a boundary. The team that owns `bluesky-dev` also needs an ArgoCD project scoped to its namespaces, a Vault path only it can read, and a workspace it can develop in — and if those are configured by hand, they drift away from the Tenant the moment membership changes.

Extensions are how MTO projects the same Tenant definition into the tools around the cluster.

## Every extension is optional

Nothing here is enabled by default, and nothing is all-or-nothing.

- **Cluster-wide integrations are inert until configured.** If `spec.integrations.argocd` is not set in the IntegrationConfig, MTO has no ArgoCD configuration and creates nothing there. The same holds for Vault and OpenBao.
- **Per-tenant extensions are created per tenant.** A tenant with no `Extensions` resource gets no `AppProject`, whatever other tenants are doing.

That matters when adopting MTO on a cluster already in production. If you have ArgoCD `AppProjects` you maintain in Git today, leave the integration unconfigured and MTO will not touch them — there is no reconcile to lose and no migration to perform. The same is true of Vault or OpenBao policies managed elsewhere.

You can then enable an extension for one tenant, see what it produces, and decide whether to move the rest. Adoption is incremental by construction rather than by exception.

## The four mechanisms

MTO extends into surrounding systems in four different ways. Which one applies depends on the system, and the distinction matters because it determines *where* you configure it.

| Mechanism | Configured in | Scope | Used by |
|---|---|---|---|
| Extensions CR | `Extensions` resource | One tenant | ArgoCD |
| IntegrationConfig integrations | `IntegrationConfig.spec.integrations` | Cluster-wide | ArgoCD, Vault |
| Namespace metadata automation | `Tenant` or `IntegrationConfig` metadata | Tenant or cluster-wide | DevWorkspace |
| Companion operator, triggered by label | Label on the `Tenant` | One tenant | Mattermost |

Only the first of these uses the `Extensions` custom resource. Today that resource carries ArgoCD configuration and nothing else — its spec has exactly two fields, `tenantName` and `argoCD`.

## Per-tenant extensions: the Extensions CR

Every `Extensions` resource is associated with one Tenant, and gives that tenant its own ArgoCD `AppProject`.

Before creating one, add the cluster-wide ArgoCD configuration to the IntegrationConfig, so MTO knows where ArgoCD runs:

```yaml
  integrations:
    argocd:
      clusterResourceWhitelist:
        - group: tronador.stakater.com
          kind: EnvironmentProvisioner
      namespaceResourceBlacklist:
        - group: ''
          kind: ResourceQuota
      namespace: openshift-operators
```

That allows the `EnvironmentProvisioner` CRD and blacklists `ResourceQuota` for every tenant. The `namespace` field is mandatory and must be the namespace where ArgoCD is deployed.

Then declare the extension for a tenant:

```yaml
apiVersion: tenantoperator.stakater.com/v1alpha1
kind: Extensions
metadata:
  name: extensions-sample
spec:
  tenantName: tenant-sample
  argoCD:
    onDeletePurgeAppProject: true
    appProject:
      sourceRepos:
        - "github.com/stakater/repo"
      clusterResourceWhitelist:
        - group: ""
          kind: "Pod"
      namespaceResourceBlacklist:
        - group: "v1"
          kind: "ConfigMap"
```

The fields:

- `tenantName`: the Tenant this extension belongs to.
- `argoCD.onDeletePurgeAppProject`: if `true`, the AppProject is deleted when the Extensions resource is deleted.
- `argoCD.appProject.sourceRepos`: the repositories this tenant may deploy from.
- `argoCD.appProject.clusterResourceWhitelist`: cluster-scoped resources the tenant's applications may manage.
- `argoCD.appProject.namespaceResourceBlacklist`: namespace-scoped resources the tenant's applications may not manage.

MTO reconciles this into an ArgoCD `AppProject` whose destinations are the tenant's namespaces. The tenant gets GitOps self-service; nobody hand-edits ArgoCD RBAC.

See [ArgoCD Multi-Tenancy](../integrations/argocd.md) for the full integration.

## Cluster-wide integrations: IntegrationConfig

Some systems are configured once for the whole cluster rather than per tenant, under `spec.integrations` in the IntegrationConfig. ArgoCD appears here as the cluster-level half of the mechanism above. **Vault lives here only** — there is no Vault field on the Extensions resource.

```yaml
  integrations:
    vault:
      enabled: true
      authMethod: kubernetes      # kubernetes (default) or token
      accessInfo:
        accessorPath: oidc/
        address: https://vault.apps.prod.abcdefghi.kubeapp.cloud/
        roleName: mto
        secretRef:
          name: ''
          namespace: ''
      config:
        ssoClient: vault
      policies:
        - name: CustomPolicy
          rules:
            - capabilities:
                - read
                - list
              path: testPath
          tenantRoles:
            - viewer
            - editor
```

With Vault enabled, MTO creates a path, a role and policies per tenant, and binds them to the tenant's owners, editors and viewers. The `policies` list lets you attach additional custom policies to specific tenant roles.

See [Vault Multi-Tenancy](../integrations/vault/vault.md) and [Integration Config](integration-config.md).

## Metadata automation: DevWorkspace

Some tools need nothing from MTO except that namespaces carry the right labels and annotations. There is no custom resource and no hook — MTO stamps the metadata, and the other operator takes it from there.

DevWorkspace works this way. It recognises a namespace as a developer workspace when it carries:

```yaml
labels:
  app.kubernetes.io/part-of: che.eclipse.org
  app.kubernetes.io/component: workspaces-namespace
annotations:
  che.eclipse.org/username: <username>
```

Setting that by hand on every sandbox does not scale, so MTO templates it. Cluster-wide, in the IntegrationConfig:

```yaml
  metadata:
    sandboxes:
      labels:
        app.kubernetes.io/part-of: che.eclipse.org
        app.kubernetes.io/component: workspaces-namespace
      annotations:
        che.eclipse.org/username: "{{ TENANT.USERNAME }}"
```

Every sandbox MTO creates then arrives ready to be a workspace, with the username substituted per user.

See [DevWorkspace](../integrations/devworkspace.md).

## Companion operators: Mattermost

The fourth mechanism is a separately installed operator that watches Tenants and acts on the ones that opt in with a label.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: sigma
  labels:
    stakater.com/mattermost: 'true'
```

With the `MTO-Mattermost-Integration-Operator` installed, that label makes it create and manage a Mattermost Team from the Tenant — members follow tenant membership, so someone leaving the tenant leaves the team.

See [Mattermost](../integrations/mattermost.md).

## Choosing where to configure

- The tool needs per-tenant configuration that differs between tenants → **Extensions CR** (ArgoCD today).
- The tool needs one connection and one policy set for the cluster → **IntegrationConfig `integrations`** (ArgoCD endpoint, Vault).
- The tool only needs namespaces to be labelled correctly → **metadata automation** (DevWorkspace).
- The tool has its own operator that watches Tenants → **label the Tenant** (Mattermost).

## Next

- [Integration Config](integration-config.md) — the cluster-wide configuration object
- [ArgoCD Multi-Tenancy](../integrations/argocd.md)
- [Vault Multi-Tenancy](../integrations/vault/vault.md)
- [DevWorkspace](../integrations/devworkspace.md)
- [Mattermost](../integrations/mattermost.md)
