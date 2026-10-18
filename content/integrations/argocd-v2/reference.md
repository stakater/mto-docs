# Reference

The full, commented reference is the chart's [`values.yaml`](https://github.com/stakater/mto-extension-argocd/blob/main/charts/mto-extension-argocd/values.yaml). This page covers the values and overrides you reach for most.

## Chart values

| Value | Default | |
|:---|:---|:---|
| `argocd.namespace` | — | **Required.** Where `AppProject`s are created |
| `rbac.serviceAccount.name` / `.namespace` | `template-operator-v2` / `stakater-template-operator` | Template Operator's identity. Set to match your install — see [Installation](installation.md#install-the-extension) |
| `scaffolding.mode` | `OnAnnotation` | `Always`, `OnLabel`, `OnAnnotation`, `Never` |
| `argocd.sourceRepos.pattern` | `[]` | Per-tenant repo patterns, one `sourceRepos` entry each; `{{ tenant }}` is expanded |
| `argocd.clusterResourceWhitelist` | `[]` | Cluster-scoped kinds tenants may manage — read [Cluster-scoped kinds](#cluster-scoped-kinds) first |
| `argocd.namespaceResourceBlacklist` | `[]` | Namespaced kinds they may not |
| `sync.mode` | `strict` | Drift protection — see [Operating](operating.md#drift-protection) |
| `onDeletePurgeAppProject` | `false` | Keep (`false`) or delete (`true`) the `AppProject` on teardown |
| `argocd.allowControlPlaneDestination` | `false` | The legacy, unsafe shape — see [Security](security.md) |
| `argocd.allowClusterResourceNames` | `false` | Allow a `name` on `clusterResourceWhitelist` entries. Set only on ArgoCD 3.3+ |
| `roles.profile` | `leastPrivilege` | Or `extensionsCompatible`, the legacy shape |
| `roles.exec.enabled` / `roles.clusters.enabled` | `false` | Owner-only web terminal, cluster writes |
| `argocd.sourceNamespaces.enabled` / `.pattern` | `false` / `{{ tenant }}-argocd` | [Applications in tenant namespaces](applications.md) |
| `argocd.impersonation.enabled` / `.serviceAccount` | `false` / `argocd-deployer` | [Sync impersonation](identity-and-impersonation.md#sync-impersonation) |
| `identity.mode` / `identity.groupPattern` | `accessControl` / `tenant-{{ tenant }}-{{ tier }}` | [Groups named by pattern](identity-and-impersonation.md#groups-named-by-pattern) |
| `argocd.syncWindows` | `[]` | [Sync windows](https://argo-cd.readthedocs.io/en/stable/user-guide/sync_windows/) on every project |
| `argocd.orphanedResources` | `off` | `warn` or `monitor` to flag resources no Application manages |

## Per-tenant overrides

Six settings can be overridden per tenant, as annotations under `argocd.tenantoperator.stakater.com/`:

| Annotation | Overrides | Format |
|:---|:---|:---|
| `source-repos` | `argocd.sourceRepos.pattern` | JSON array of strings |
| `cluster-resource-whitelist` | `argocd.clusterResourceWhitelist` | JSON array of `{group, kind, name?}` |
| `namespace-resource-blacklist` | `argocd.namespaceResourceBlacklist` | JSON array of `{group, kind}` |
| `on-delete-purge` | `onDeletePurgeAppProject` | `"true"` or `"false"` |
| `sync-windows` | `argocd.syncWindows` | JSON array of window objects |
| `orphaned-resources` | `argocd.orphanedResources` | `off`, `warn` or `monitor` |

An **absent** annotation inherits the chart default. An explicit `[]` **overrides with empty** — a different thing — which is why the value is passed to the child verbatim rather than parsed by the parent; malformed JSON fails that tenant's child alone and never falls back to the default. Override values are shape-checked, not value-checked — see [Security](security.md#per-tenant-overrides-are-as-trusted-as-the-tenant).

## Cluster-scoped kinds

A cluster-scoped kind on the allow-list is granted for every object of that kind in the cluster. Prefer exact `name`s (ArgoCD 3.3+, with `argocd.allowClusterResourceNames: true`) over globs, and read [Security → Cluster-scoped kinds are cluster-wide](security.md#cluster-scoped-kinds-are-cluster-wide) before allowing any.

## The opt-in annotation value

`scaffolding.mode: OnAnnotation`/`OnLabel` includes a tenant only when `argocd.tenantoperator.stakater.com/enabled` is exactly `"true"`. `"True"`, `"yes"`, `"1"` and `"on"` all read as opted out, deliberately.

---

**Previous:** [Operating](operating.md) · **Next:** [Migrating](migrating.md)
