# Template Operator essentials

This page covers the parts of template-operator-v2 an extension uses, and how they behave on template-operator-v2 0.0.8. It is a working reference, not the complete API.

Both kinds are namespaced and live in the `templates.v2.stakater.com` group, at version `v2alpha1`. Always use the full resource names, `templates.templates.v2.stakater.com` and `templateinstances.templates.v2.stakater.com`, with `kubectl`. On OpenShift the short name `templateinstance` resolves to OpenShift's own `template.openshift.io` kind.

## Template

A `Template` declares parameters and says how to render objects from them. On its own it does nothing; a `TemplateInstance` that references it does the rendering.

```yaml
apiVersion: templates.v2.stakater.com/v2alpha1
kind: Template
metadata:
  name: tenant-info-child
  namespace: multi-tenant-operator
spec:
  parameters:
    - name: tenant
      required: true          # the instance must supply it
      exposeInStatus: true    # show the resolved value in the instance's status
    - name: namespacesJson
      value: "[]"             # default, used when the instance does not set it
  sync:
    mode: strict
    ignoreFields: [metadata.finalizers]
  gotemplate: |
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: {{ .parameters.tenant | quote }}
    ...
  outputs:
    - name: directory
      from: {apiVersion: v1, kind: ConfigMap, name: "{.parameters.tenant}"}
      fields:
        - {name: namespaces, jsonPath: "{.data.namespaces}"}
```

| Field | What it does |
|---|---|
| `parameters[]` | The template's inputs: `name`, a default `value`, `required`, `exposeInStatus`, and an optional `type` (`string`, `number`, `bool`, `array`, `object`). |
| `gotemplate` | A Go template that renders to YAML, one or more documents. Exactly one of `gotemplate` and `helm` is set. |
| `helm` | Renders a published Helm chart instead. See [Rendering a Helm chart](#rendering-a-helm-chart). |
| `outputs[]` | Values read back from rendered objects into the instance's status. See [Status and outputs](#status-and-outputs). |
| `sync` | Drift protection for rendered objects. See [Sync modes](#sync-modes). |
| `targetNamespaces` | Which namespaces may hold an instance of this Template. If it is omitted, only the Template's own namespace may. Keep each extension's Templates and TemplateInstances in one namespace and you never need to set it. |

## TemplateInstance

A `TemplateInstance` references a Template and supplies its parameters. A parameter is either a literal `value` or a `valueFrom` that reads the cluster.

```yaml
apiVersion: templates.v2.stakater.com/v2alpha1
kind: TemplateInstance
metadata:
  name: tenant-info-parent
  namespace: multi-tenant-operator
spec:
  templateRef:
    name: tenant-info-parent
    namespace: multi-tenant-operator
  parameters:
    - name: optInAnnotation
      value: tenant-info.example.com/enabled
    - name: tenants
      valueFrom:
        objectFieldRef:
          apiVersion: tenantoperator.stakater.com/v1beta3
          kind: Tenant
          jsonPath: .items
```

### Reading the cluster with `objectFieldRef`

`objectFieldRef` is how an extension sees tenants. template-operator-v2 watches whatever it reads, and re-renders the instance when any of it changes.

| Form | What it reads | Example |
|---|---|---|
| `name` set (and `namespace` for a namespaced kind) | A GET of one object, then `jsonPath` over it | The `IntegrationConfig`, with `jsonPath: .spec` |
| No `name` | A LIST of every object of the kind, cluster-wide. `jsonPath: .items` gives the list. | Every `Tenant`, every `Namespace` |
| No `name`, plus `namespaceSelector` | A LIST limited to namespaces matching the selector | Every `ServiceAccount` in one tenant's namespaces |

A LIST always returns a list. A cluster with no Tenants gives an empty list, not an error, so a parent that ranges over it simply renders nothing.

`namespaceSelector` picks *where to look* for a namespaced kind. It does not filter Namespace objects, and it errors on a cluster-scoped kind. To find a tenant's namespaces, LIST every Namespace and filter on the `stakater.com/tenant` label in the gotemplate.

Read a GET shallowly and dig in the template. A deep `jsonPath` such as `.spec.accessControl.privileged` fails the whole instance when any segment is absent. Read `.spec` and walk down with `index` and `default dict`, as in [Write the parent so it cannot fail](design-rules.md#write-the-parent-so-it-cannot-fail).

`valueFrom` can also read a key with `configMapKeyRef` or `secretKeyRef`. `defaultValue` supplies a value when a `valueFrom` read fails. Do not give a security-relevant input a `defaultValue`: masking a failed read can widen access. See [Fail closed](design-rules.md#fail-closed).

### Parameter values are strings

A literal `value` is a string, number or boolean. A parent passes a list or a map to a child as a **JSON string**, and the child decodes it with `mustFromJson`:

```yaml
# in the parent's gotemplate
    - name: namespacesJson
      value: {{ $namespaces | toJson | quote }}
```

Do not join a list with commas. An empty list then becomes `""`, which template-operator-v2 treats as an unset parameter and rejects. A tenant with no namespaces is common enough that this matters.

## The gotemplate

A gotemplate is Go's [text/template](https://pkg.go.dev/text/template) with [Sprig](https://masterminds.github.io/sprig/) functions. It sees two values:

| Value | Holds |
|---|---|
| `.parameters` | Every resolved parameter, by name |
| `.instance` | The TemplateInstance's metadata: `name`, `namespace`, `labels` |

It is not Helm. Several functions people reach for out of habit do not exist:

| Not available | Use instead |
|---|---|
| `toYaml`, `fromYaml` | `toJson` and `mustFromJson`. JSON is valid YAML, so `toJson` output can go straight into a manifest. |
| `include`, `tpl`, `define`d helpers, `.Files` | Inline the logic, or move it into the parent and pass the result down as a parameter. |
| `fromJsonArray` | `mustFromJson`, which decodes arrays as well as objects. |
| `env`, `expandenv`, `getHostByName` | Removed from Sprig on purpose. Pass the value in as a parameter. |

Also note:

- **Missing keys are errors.** From 0.0.8, a field read of a missing key, such as `$t.metadata.annotations` on a Tenant without annotations, fails the render with `map has no entry for key`. `index $t.metadata "annotations"` returns nothing instead. Read every optional key with `index`.
- **`fromJson` swallows errors.** It returns an error map rather than failing, and that renders into a live object as garbage. Always use `mustFromJson`.
- **Use `mustRegexMatch` for patterns you did not write.** The plain `regexMatch` returns false on an invalid pattern, which quietly turns a filter off.
- **`fail` stops the render** with your message, which then appears in the instance's status. Use it to refuse bad input.

## What template-operator-v2 does with a render

For every rendered object, template-operator-v2:

1. Applies it.
1. Labels it with the instance that owns it (`templates.v2.stakater.com/instance`, and the instance's name, namespace and UID).
1. Adds the finalizer `templates.v2.stakater.com/template-instance-resource`.
1. Lists it under the instance's `status.renderedResources`.

Each render is the full desired state. On every reconcile, template-operator-v2 applies what the render contains and **deletes what it no longer contains**. When a parent stops emitting a tenant's child, the child is deleted, and so is everything the child rendered. Deleting a TemplateInstance deletes everything it rendered in the same way.

A render that fails does not delete anything. If the parent's gotemplate fails, template-operator-v2 marks the parent `Failed` and leaves the existing children and their objects in place.

### Keeping an object on deletion

An object annotated `templates.v2.stakater.com/deletion-policy: Orphan` is released instead of deleted. template-operator-v2 removes its labels and finalizer and leaves the object in the cluster. Use this for objects that people depend on and that cannot be recreated identically. See [Deletion](design-rules.md#deletion).

## Sync modes

`spec.sync.mode` decides what happens when someone edits a rendered object.

| Mode | Behaviour |
|---|---|
| `off` (default) | Objects are applied on each render. Edits in between persist until the next render. |
| `revert` | template-operator-v2 watches rendered objects and reverts edits. |
| `strict` | `revert`, plus an admission webhook that refuses updates and deletes of rendered objects from anyone but template-operator-v2. |

Under `revert`, deleting a rendered object by hand leaves it stuck in `Terminating`: the finalizer is never released, and the instance goes on reporting `Ready`. `strict` refuses the delete instead, which is why extensions use it.

Under `strict`, `ignoreFields` must include `metadata.finalizers`. template-operator-v2 manages its own finalizer through an update, and without the exemption its own webhook refuses it, so nothing can be torn down. Add any other field that another controller writes. For example, ArgoCD writes `spec.roles[*].jwtTokens` into an `AppProject` when a project token is created.

## Status and outputs

Each TemplateInstance reports a `phase` (`Ready` or `Failed`) and a set of conditions:

| Condition | False means |
|---|---|
| `TemplateResolved` | The referenced Template does not exist |
| `TargetNamespaceAllowed` | The Template's `targetNamespaces` does not allow this namespace |
| `ParametersValid` | A required parameter is missing, or a `valueFrom` read failed |
| `Rendered` | The gotemplate or chart failed. The message holds the template error or your `fail` text. |
| `Applied` | The API server rejected a rendered object, or template-operator-v2 lacks RBAC for it |
| `Synced` | Drift protection is not active |
| `OutputsResolved` | An output could not be read |
| `Ready` | Any of the above. Its message only summarises, so read the failing condition for the cause. |

`outputs` copies values from rendered objects into `status.outputs`, so the instance answers questions about what it produced:

- `from` reads one rendered object, named with a `jsonPath` template such as `"{.parameters.tenant}"`.
- `fromAll` reads every rendered object of a kind, keyed by `keyTemplate`.
- Each entry under `fields` names a `jsonPath` expression, and its result is stored under that field's name. Field names must be unique across all of a Template's outputs.
- An output may not read a `Secret`.

A parent can use `fromAll` over its own child TemplateInstances to give one place that shows every tenant's health. The [tutorial's parent](tutorial.md#the-parent-every-tenant) does this.

## RBAC

Out of the box, template-operator-v2's ServiceAccount can manage `templates` and `templateinstances` and read `namespaces`, and nothing else. An extension's chart grants it everything else:

- **get, list and watch** on every kind the parent reads (`tenants`, `integrationconfigs`, ...).
- **get, list, watch, create, update, patch and delete** on every kind the children render.
- **list and watch at cluster scope** on every rendered kind, even when every object lands in one namespace. On teardown, template-operator-v2 finds what it owns by listing each rendered kind across the cluster. With only a namespaced Role, the delete fails with `forbidden` and the instance stays in `Terminating`. Mutating verbs can stay namespaced.

The ServiceAccount's name depends on how template-operator-v2 was installed. See [Installing template-operator-v2](#installing-template-operator-v2). Make it a chart value.

Ship the RBAC in your chart, not through template-operator-v2: a RoleBinding cannot be rendered in the same pass as the Role it binds. And keep it on uninstall. See [Uninstall in the right order](design-rules.md#uninstall-in-the-right-order).

## Rendering a Helm chart

A Template can render a published chart instead of a gotemplate:

```yaml
spec:
  parameters:
    - name: tenant
      required: true
  helm:
    chart:
      repository:
        url: oci://ghcr.io/example/charts    # or an https chart repository
        name: my-tenant-chart
        version: "1.4.0"                     # an exact version
        auth:                                # optional, for a private registry
          secretRef:
            name: registry-credentials       # in the Template's namespace
    releaseName: my-tenant-chart
    valuesTemplate: |
      tenant: {{ .parameters.tenant | quote }}
```

- `valuesTemplate` is a gotemplate with the same context and functions as above. It renders YAML that is merged over the chart's own `values.yaml`.
- Objects without a namespace land in the TemplateInstance's namespace.
- template-operator-v2 pulls the **published** chart. Changing a chart in your Git checkout has no effect on a cluster until you publish a new version and the Template references it.
- Inside the chart you write ordinary Helm, with every Helm function available.

See [Vault Enterprise](real-extensions.md#vault-enterprise) for an extension built this way.

## Installing template-operator-v2

From MTO 1.10, MTO deploys template-operator-v2 for you. Set `components.templateOperatorV2.mode` to `Managed` in the [IntegrationConfig](../../concepts/integration-config.md):

```yaml
spec:
  components:
    templateOperatorV2:
      mode: Managed
```

MTO 1.10.1 then runs template-operator-v2 0.0.8 in MTO's namespace, under the ServiceAccount `tenant-operator-template-operator-v2`. Look the name up rather than assuming it:

```bash
kubectl -n multi-tenant-operator get deployment template-operator-v2-controller-manager \
  -o jsonpath='{.spec.template.spec.serviceAccountName}{"\n"}'
```

To install it yourself instead, use the public chart. It needs cert-manager, which issues its webhook certificate:

```bash
helm install template-operator-v2 oci://ghcr.io/stakater/public/charts/template-operator-v2 \
  --version 0.0.8 --namespace stakater-template-operator --create-namespace --wait
```

The ServiceAccount is then `template-operator-v2` in `stakater-template-operator`. On a cluster where MTO is running, create the `stakater-template-operator` namespace from a group listed in MTO's `bypassedGroups`: MTO refuses other namespaces that do not belong to a tenant.

!!! warning
    Install only from MTO or from the published chart. Their sync-enforcement webhook only matches objects that carry the `templates.v2.stakater.com/instance` label. A copy of the chart without that filter matches every update in the cluster. Because the webhook fails closed and is registered before the operator can answer, it can deadlock the cluster during install.
