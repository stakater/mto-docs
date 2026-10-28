# Migrating from the Extensions integration

The older ArgoCD integration is configured through the `Extensions` custom resource and `IntegrationConfig.spec.integrations.argocd`, reconciled by MTO's built-in `ExtensionsArgoCDReconciler` (see [the older page](../argocd.md)). This extension replaces both. It renders the same per-tenant `AppProject`, so a migration is a change of mechanism, not of outcome — and you can start from a compatibility shape that matches the old output, then move to the secure defaults.

## What changes

| | Old (`Extensions` + built-in reconciler) | This extension |
|:---|:---|:---|
| Per-tenant config | an `Extensions` CR per tenant | an opt-in annotation/label on the `Tenant` |
| Cluster-wide config | `IntegrationConfig.spec.integrations.argocd` | chart values |
| Who reconciles | MTO's Go controller | Template Operator, from the chart |
| Defaults | the ArgoCD namespace is a destination; broad roles | neither (least privilege) |

`integrations.argocd.{namespace, clusterResourceWhitelist, namespaceResourceBlacklist}` are no longer read by this extension; move those values into the chart (`argocd.namespace`, `argocd.clusterResourceWhitelist`, `argocd.namespaceResourceBlacklist`). `accessControl.privileged` in the `IntegrationConfig` is still read.

## Start from the compatibility shape

Two values make the rendered `AppProject` match the old controller's output, so you can cut over without changing what any tenant can do:

```yaml
argocd:
  allowControlPlaneDestination: true   # keep the ArgoCD namespace as a destination
roles:
  profile: extensionsCompatible        # the legacy broad role shape
```

Install with these, confirm each tenant's `AppProject` is equivalent, then remove the `Extensions` CRs and the `integrations.argocd` block.

## Then move to the secure defaults

Drop the two compatibility values and re-render. Each managed `AppProject` then changes:

- the **ArgoCD namespace leaves `destinations`** — Applications that deploy *into* the control-plane namespace stop syncing. Move them into tenant namespaces first (see [Applications in tenant namespaces](applications.md)), or migrate them deliberately.
- the **roles narrow** to least privilege (edit can no longer create/delete/override Applications; `exec` is off).

Do this as a deliberate, announced step — it is a real tightening of what tenants can do.

## Deliberate differences from the old output

Even in compatibility mode, a few differences are intentional (each is pinned by the extension's equivalence tests):

- **`spec.description`** is `Managed by mto-extension-argocd`.
- **`roles[].groups`** gains the tenant's **users** alongside its groups (a name listed twice appears once; ArgoCD rejects a duplicate). This is a fix — the generated group only resolves where ArgoCD is told which claim carries it (see [Security](security.md#match-users-the-way-your-login-provides-them)).
- **`roles[].policies`** are one line per project-scoped resource instead of one line with resource `*`. Same access; ArgoCD's API rejects `*` there, so the old single-line form actually broke every project write through ArgoCD (including `create-token` and the UI).
- **metadata** carries a `templates.v2.stakater.com/deletion-policy: Orphan` annotation when purge is off, and does not carry MTO's `multi-tenant-operator/predicate` label.

See [Security](security.md) for the defaults and [Operating](operating.md#what-deletes-an-appproject) for what teardown does.

---

**Previous:** [Reference](reference.md)
