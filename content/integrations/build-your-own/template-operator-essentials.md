# Template Operator essentials

An extension is **configuration for Template Operator v2** — a parent `Template` + `TemplateInstance` that render your tenant objects. This page orients you to the parts you use and links the canonical reference; it does not repeat it. Read the [Template Operator v2 docs](../../template-operator-v2/concepts/overview.md) for the full behaviour.

Both kinds live in the `templates.v2.stakater.com` group at `v2alpha1`. Use the full resource names with `kubectl` — `templates.templates.v2.stakater.com` and `templateinstances.templates.v2.stakater.com` — because on OpenShift the short `templateinstance` resolves to OpenShift's own `template.openshift.io` kind.

## What an extension uses, and where it's documented

| You need | For | Reference |
|---|---|---|
| `Template` / `TemplateInstance`, provider–consumer split | the two objects your chart installs | [Overview](../../template-operator-v2/concepts/overview.md) |
| `gotemplate` engine — `missingkey=error`, Sprig-not-Helm, `mustFromJson` | writing the render safely | [Gotemplate](../../template-operator-v2/concepts/gotemplate.md) |
| `parameters` and `objectFieldRef` (GET vs LIST, `namespaceSelector`) | reading `Tenant`s, `Namespace`s, the `IntegrationConfig` | [Parameters](../../template-operator-v2/concepts/parameters.md) |
| `outputs` (`from` / `fromAll`) | surfacing per-tenant health on status | [Outputs](../../template-operator-v2/concepts/outputs.md) |
| `sync` modes and `ignoreFields` | drift protection on what you render | [Sync](../../template-operator-v2/concepts/sync.md) |
| `targetNamespaces` | where an instance may be created | [Target namespaces](../../template-operator-v2/concepts/target-namespaces.md) |
| what happens to rendered objects, orphan/`deletion-policy` | teardown behaviour | [Lifecycle](../../template-operator-v2/concepts/lifecycle.md) |
| the security model and the operator-ServiceAccount boundary | scoping RBAC | [Security](../../template-operator-v2/concepts/security.md) |

And the patterns an extension is built on, each a worked guide:

- The fan-out: one instance renders into many namespaces — [Rendering to many namespaces](../../template-operator-v2/guides/rendering-to-many-namespaces.md).
- Composition: a parent that renders child `TemplateInstance`s, one per tenant — [Composing TemplateInstances](../../template-operator-v2/guides/composing-templateinstances.md).
- Testing your gotemplates the way the operator renders them — [Testing Templates](../../template-operator-v2/guides/testing-templates.md).

## Extension-specific notes

A few things matter when you are *building* the chart rather than using the operator:

- **Keep an extension's `Template`s and `TemplateInstance`s in one namespace** (the operator namespace). Then the default `targetNamespaces` already allows them and you never set it.
- **Parameters travel as strings.** A parent passes a list or map to a child as a JSON string (`{{ $v | toJson | quote }}`) and the child decodes it with `mustFromJson`; a comma-joined empty list becomes `""`, which the operator rejects as unset. See [Parameters](../../template-operator-v2/concepts/parameters.md).
- **RBAC your chart must grant the operator's ServiceAccount:** `get/list/watch` on every kind the parent reads; `create/update/patch/delete` on every kind the children render; and **`list`/`watch` at cluster scope on every rendered kind** — on teardown the operator lists each rendered kind cluster-wide, so a namespaced-only Role leaves instances stuck `Terminating`. Grant least privilege, scoped to the namespaces you actually write to (the operator applies with its own ServiceAccount — see [Security](../../template-operator-v2/concepts/security.md)). Ship the RBAC in the chart (a RoleBinding cannot be rendered in the same pass as its Role), and keep it on uninstall — [Uninstall in the right order](design-rules.md#uninstall-in-the-right-order).

## Installing Template Operator v2

From MTO 1.10, MTO deploys it for you — set `components.templateOperatorV2.mode: Managed` in the `IntegrationConfig`, and it runs in MTO's namespace as `tenant-operator-template-operator-v2`. To install it standalone, use its own chart (`oci://ghcr.io/stakater/public/charts/template-operator-v2`); the ServiceAccount is then `template-operator-v2` in `stakater-template-operator`. Either way, make the ServiceAccount a chart value and look the name up rather than assuming it:

```bash
kubectl -n multi-tenant-operator get deployment template-operator-v2-controller-manager \
  -o jsonpath='{.spec.template.spec.serviceAccountName}{"\n"}'
```

!!! warning
    Install only from MTO or the published chart — their sync-enforcement webhook is scoped to operator-managed objects by a label filter. A build of the webhook without that filter intercepts every write in the cluster and can deadlock it during install.
