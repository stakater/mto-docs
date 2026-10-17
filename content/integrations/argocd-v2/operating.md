# Operating

## Drift protection

`sync.mode` defaults to `strict`: a managed `AppProject` cannot be hand-edited or deleted — Template Operator's admission webhook refuses both. Under the looser `revert`, a hand-deleted `AppProject` wedges in `Terminating` forever while its `TemplateInstance` still reports healthy, so `strict` is the right default.

`argocd proj role create-token` and `delete-token` still work: ArgoCD writes tokens into `spec.roles[].jwtTokens`, which the chart exempts from enforcement. A later re-render drops that spec copy (roles are applied as one list), but the token stays valid — ArgoCD checks project tokens against `status.jwtTokensByRole`, which Template Operator does not touch.

## Fleet health

One object answers for every tenant. This prints nothing when all is well, and one line per unhealthy tenant with the real error:

```bash
kubectl get templateinstances.templates.v2.stakater.com mto-argocd-parent \
  -n multi-tenant-operator -o json \
  | jq -r '.status.outputs as $o | $o.ready | keys[] as $k
      | select(($o.ready[$k]|fromjson|join("")) != "True")
      | "\($k): \($o.errors[$k]|fromjson|join(" | "))"'
```

The `errors` field collects every failing condition's message, whichever stage broke — parameter resolution, rendering or apply — because the `Ready` condition only ever summarises ("Template rendering failed").

!!! tip
    Use the fully-qualified `templateinstances.templates.v2.stakater.com`. On OpenShift a bare `kubectl get templateinstance` returns OpenShift's own kind with an empty status — indistinguishable from "not reconciling".

## When a tenant has no project

- The tenant has not opted in (`scaffolding.mode` is `OnAnnotation`/`OnLabel` and the annotation/label is missing or not exactly `"true"`).
- `rbac.serviceAccount` does not match Template Operator's identity, so the parent cannot list `Tenant`s — check `mto-argocd-parent`'s `Ready` condition ([Installation](installation.md#verify)).
- The tenant has a malformed override annotation: only that tenant's child fails; the fleet health query above names it.

## What deletes an AppProject

Template Operator owns every object a child renders. When the parent stops rendering a tenant's child — the tenant opts out, `scaffolding.mode` narrows, the `Tenant` is deleted, or `helm uninstall` runs — the child and its `AppProject` are removed, **unless** the `AppProject` is marked to be kept.

With `onDeletePurgeAppProject: false` (the default) the chart marks each `AppProject` `templates.v2.stakater.com/deletion-policy: Orphan`. Template Operator 0.0.7+ honours the mark and *releases* the project (the object stays, without the finalizer/labels, and ArgoCD keeps using it).

| Trigger | 0.0.7+, purge off (default) | purge on | 0.0.6 and earlier |
|:---|:---|:---|:---|
| opt-in removed / `Tenant` deleted / `scaffolding.mode` narrowed / `helm uninstall` | released | deleted | deleted |

!!! warning
    On Template Operator **0.0.6 and earlier**, `onDeletePurgeAppProject: false` has no effect — the `AppProject` is **deleted** in every case above. Use 0.0.7+ to keep projects.

"Purge on" is `onDeletePurgeAppProject: true`, or the `on-delete-purge` annotation on one `Tenant`.

These do **not** delete an `AppProject`: a malformed override annotation (only that child fails), a tenant losing all its namespaces (it keeps the project), or the parent failing to render (Template Operator keeps the last rendered set, so a broken `IntegrationConfig` cannot wipe the fleet).

## Uninstalling

A plain `helm uninstall` is safe:

```bash
helm uninstall mto-extension-argocd -n multi-tenant-operator
```

The chart's RBAC is kept on uninstall (`helm.sh/resource-policy: keep`, and `Prune=false,Delete=false` for an ArgoCD-managed release), so Template Operator keeps the permissions its finalizers need while it reaps the children. What then happens to the `AppProject`s depends on the version and purge, as above. The `NOTES.txt` that `helm install` prints has the commands to remove the kept RBAC afterwards.

Reinstalling immediately fails with an ownership-metadata error — wait for `Template/mto-argocd-parent` to disappear first.
