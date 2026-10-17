# Design rules

The [tutorial](tutorial.md) extension works. This page is about making one that is safe to run against every tenant on a production cluster.

Every rule here comes from building Stakater's ArgoCD and Vault Enterprise extensions. Most started as a bug that hit every tenant at once, or failed silently.

## Know your blast radius

An extension has two failure domains, and each rule below keeps a failure in the smaller one.

| A failure in | Affects | So |
|---|---|---|
| A child | One tenant | It is visible on that tenant's TemplateInstance, and every other tenant carries on. |
| The parent | Every tenant at once | Make it as hard to break as you can. |
| A chart value | Every tenant at once, after install | Refuse a bad value at `helm install`, not later on the cluster. |

There is a worse case than a failed render: **a render that succeeds with the wrong output.** template-operator-v2 deletes whatever a render no longer contains. If a typo makes the parent emit no children, every child is deleted, and with them every object they rendered, for every tenant. Most of the rules below come back to this.

## Template authors share your permissions

Everything your chart grants goes to template-operator-v2's ServiceAccount, and template-operator-v2 renders *every* Template on the cluster with that ServiceAccount. A Template can write into any namespace, not only its own. `targetNamespaces` limits where a TemplateInstance may be created, not where the objects it renders land. So anyone who can create a Template and a TemplateInstance, in any namespace, can use every permission any extension has granted.

That is a cross-tenant path when tenants can create Templates. MTO's tenant roles do not include them, but template-operator-v2 ships `template-operator-v2-template-editor-role` and `template-operator-v2-templateinstance-editor-role` so that teams can use it themselves. The [tutorial](tutorial.md#step-9-stop-other-templates-borrowing-your-permissions) shows a tenant owner with only those two roles writing a ConfigMap into another tenant's namespace through `tenant-info`'s grant. With the ArgoCD extension's grant, the same Template could write an `AppProject` that allows every destination: cluster-admin through ArgoCD.

Narrowing your RBAC does not fix this, because every Template uses the same ServiceAccount. An admission policy does. template-operator-v2 labels each object it renders with the namespace of the TemplateInstance that owns it (`templates.v2.stakater.com/instance-namespace`), and overwrites any value a template sets. So the cluster can require that a TemplateInstance writes only inside its own namespace, unless that namespace is one you trust to hold extensions:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: template-operator-v2-write-scope
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["*"]
        apiVersions: ["*"]
        resources: ["*"]
        operations: ["CREATE", "UPDATE", "DELETE"]
  variables:
    - name: obj
      expression: 'request.operation == "DELETE" ? oldObject : object'
    - name: owner
      expression: 'variables.obj.metadata.?labels[?"templates.v2.stakater.com/instance-namespace"].orValue("")'
  matchConditions:
    - name: is-template-operator-v2
      expression: 'request.userInfo.username == "system:serviceaccount:<namespace>:<template-operator-v2 ServiceAccount>"'
    - name: is-rendered-object
      expression: '(object != null && "templates.v2.stakater.com/instance-namespace" in object.metadata.?labels.orValue({})) || (oldObject != null && "templates.v2.stakater.com/instance-namespace" in oldObject.metadata.?labels.orValue({}))'
  validations:
    - expression: 'variables.owner in ["multi-tenant-operator", "<other extension namespaces>"] || (has(variables.obj.metadata.namespace) && variables.obj.metadata.namespace == variables.owner)'
      messageExpression: '"template-operator-v2: a TemplateInstance in namespace " + variables.owner + " may only write objects in its own namespace"'
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: template-operator-v2-write-scope
spec:
  policyName: template-operator-v2-write-scope
  validationActions: [Deny]
```

Tested on template-operator-v2 0.0.8:

| TemplateInstance in | Renders into | Result |
|---|---|---|
| a namespace on the list | another namespace, or a cluster-scoped object | allowed |
| any namespace | its own namespace | allowed |
| a namespace not on the list | another namespace | refused, and the TemplateInstance reports the message |
| a namespace not on the list | a cluster-scoped object | refused |
| any namespace | an object labelled as if another namespace owned it | refused: template-operator-v2 replaces the label |

Teardown is not affected, because deleting an object is checked against the label it already carries.

The policy is a cluster-wide rule, not part of any one extension, so the platform team owns it and adds each extension's namespace to the list. In your chart's documentation:

- **Say which permissions you grant template-operator-v2, and where.** A cluster-wide write grant is shared with every Template author until the policy is in place.
- **Do not grant the template-operator-v2 editor roles to tenants** unless the policy is in place.
- **Treat who can create Templates in your extension's namespace as part of your trust boundary.** Anyone who can is trusted with everything the extension can do.

## Write the parent so it cannot fail

Every tenant flows through the parent's single render.

**Read optional keys with `index`.** From template-operator-v2 0.0.8, a field read of a missing key fails the render. `$t.metadata.annotations` on a Tenant without annotations takes the whole parent down. `index` returns nothing for a missing key; `default dict` turns that into an empty map:

```yaml
{{- $annotations := default dict (index $t.metadata "annotations") }}
```

**Default each level in turn.** `dig` looks like a shortcut, but it fails on an explicit `null`, and Tenants do arrive with `spec: null` or `accessControl: null`. The ArgoCD extension tested every shape. Only this form survives all of them:

```yaml
{{- $spec := default dict (index $t "spec") }}
{{- $ac := default dict (index $spec "accessControl") }}
{{- $owners := default dict (index $ac "owners") }}
{{- $groups := default list (index $owners "groups") }}
```

**Pass per-tenant input down as raw text.** If a tenant's annotation holds JSON, the parent copies the string into the child's parameter and the child decodes it. Malformed JSON then fails one child instead of the parent.

**Decide present-or-absent with `hasKey`, not `default`.** `default` treats `""` as unset. An author who writes an empty annotation clearly meant to override something, so that should fail loudly, not quietly fall back to the chart default:

```yaml
{{- $value := $chartDefault }}
{{- if hasKey $annotations $key }}{{- $value = index $annotations $key }}{{- end }}
```

**Make one pass over large lists.** A loop over namespaces inside a loop over tenants costs tenants × namespaces steps, and the parent re-renders on every Namespace event in the cluster. At 300 tenants and 3,000 namespaces, the ArgoCD extension measured 1.9 seconds per render with nested loops. Bucket namespaces by tenant in one pass instead.

**Never let a tenant's name collide with yours.** Name children under a prefix the parent's own name cannot take. If children were named `<extension>-<tenant>`, a Tenant called `parent` would produce `<extension>-parent`, the parent TemplateInstance itself. template-operator-v2 would overwrite the parent with that child, the parent would stop ranging over tenants, and every other child would be deleted. Use `<extension>-tenant-<tenant>`.

## Validate in the child

The child is where a tenant's input gets checked, because a failure there stays with that tenant.

- **Decode with `mustFromJson`.** Plain `fromJson` hides the error and returns an error map, which renders into a live object.
- **Check the shape, not only the syntax.** `[{"group":{}}]` is valid JSON. Rendered with `quote`, it becomes the string `"map[]"` and applies cleanly to the live object. Check each value's kind (`kindIs "string"`, `kindIs "slice"`, `kindIs "map"`) and `fail` if it is wrong.
- **Accept exactly the values you mean.** For a boolean, accept `"true"` and `"false"` and fail on anything else. `True`, `yes`, `1` and `on` all look affirmative. Treating them as "no" silently does the opposite of what the author meant.
- **Say what is wrong.** The `fail` message appears in the tenant's TemplateInstance status. Name the annotation and the bad value.

## Fail closed

When an input decides who can reach what, a missing value must stop the render, not fall back to something permissive.

The ArgoCD extension reads the IntegrationConfig's privileged namespaces and keeps them out of every tenant's `AppProject`. An early version read them with a default, along these lines:

```yaml
{{- $privNs := dig "accessControl" "privileged" "namespaces" list $ic }}
```

When the field is absent, that yields an empty list. An empty list filters nothing, so privileged namespaces went into every tenant's destinations. The version that ships refuses instead:

```yaml
{{- $priv := default dict (index (default dict (index $ic "accessControl")) "privileged") }}
{{- if or (not (hasKey $priv "namespaces")) (kindIs "invalid" (index $priv "namespaces")) }}
{{- fail "IntegrationConfig .spec.accessControl.privileged.namespaces is absent or null; refusing to render. Set it explicitly, to [] if the cluster has none." }}
{{- end }}
```

The same reasoning gives three more rules:

- **No `defaultValue` on a security-relevant `valueFrom`.** A default masks a failed read, and the failure mode is cross-tenant access.
- **Reject an empty regular expression.** `""` is a valid pattern that matches everything, so one stray entry in a deny list removes every tenant's access, or, in an allow list, grants everything.
- **Use `mustRegexMatch`** on patterns that come from configuration. The plain form turns an invalid pattern into "no match", which disables the filter for every tenant.

## Validate chart values twice

A chart value applies to every tenant, so check it at `helm install`, before anything renders. Check it twice:

1. In `values.schema.json`, for the user's benefit.
1. In a template guard that calls `fail`. The schema can be skipped (`helm install --skip-schema-validation`), and some tools that render charts through the Helm SDK never apply it.

Values that most need a guard:

- **True-or-false values.** In a Go template, the string `"false"` is true. A toggle set to `"false"` turns the feature on. Check with `kindIs "bool"`.
- **Enumerations.** The ArgoCD extension's `scaffolding.mode` decides which tenants get a child. A typo matches no branch, every tenant fails the filter, no children are emitted, and every `AppProject` is deleted. Check it against the list of valid values.
- **Keys you look up.** An empty annotation key never matches anything, so the opt-in or the override it names is silently ignored.
- **Placeholders.** If a value supports `{{ tenant }}`, reject any other placeholder syntax (`{{ .tenant }}`, `${tenant}`, `%s`). Otherwise it ships verbatim into every tenant's objects.
- **`sync.mode: strict`** without `metadata.finalizers` in `ignoreFields`. Teardown then deadlocks.

```yaml
{{- define "my-extension.validate" -}}
{{- if not (has .Values.scaffolding.mode (list "Always" "OnLabel" "OnAnnotation" "Never")) -}}
{{- fail (printf "scaffolding.mode must be one of Always, OnLabel, OnAnnotation, Never; got %q. Any other value emits no children, and every tenant's objects are deleted." .Values.scaffolding.mode) -}}
{{- end -}}
{{- end -}}
```

## Opting tenants in

Choose how a tenant gets the extension. The ArgoCD extension offers four modes, and the same set works for most extensions:

| Mode | A tenant gets the extension when |
|---|---|
| `OnAnnotation` (default) | it has the opt-in annotation set to exactly `"true"` |
| `OnLabel` | it has the opt-in label set to exactly `"true"` |
| `Always` | it exists |
| `Never` | never. Existing objects are removed, as below. |

Default to opt-in. On a cluster that already has these objects managed some other way, an opt-in extension changes nothing until someone asks it to.

Narrowing the filter removes objects. If a tenant stops matching, its child is no longer emitted, so template-operator-v2 deletes it and everything it rendered. Document that next to the setting, and see [Deletion](#deletion).

## Decide who controls each input

An extension turns cluster state into access in another system. For each input, write down who can change it.

- **The `Tenant` resource** is normally edited only by platform administrators. Overrides read from Tenant annotations are as trusted as the Tenant.
- **The `stakater.com/tenant` label on a namespace** says which tenant owns it. If the extension grants access to whatever is labelled for a tenant, then anyone who can set that label can claim the tenant's access. Keep namespace labelling under the platform's control. Tenant users must not hold `patch` or `update` on Namespaces at cluster scope. MTO needs the same rule for its own isolation.
- **Objects inside tenant namespaces**, such as ServiceAccount annotations, can be written by the tenant's own users. An extension that reads them, as Vault Enterprise does, must treat them as untrusted input and cap what they can request.

## Names

Names you compose from tenant data must be unambiguous.

- **Join name parts with a character the parts cannot contain.** With hyphens, namespace `t-web` plus ServiceAccount `api-x` and namespace `t-web-api` plus ServiceAccount `x` both give `t-web-api-x`. The Vault Enterprise extension joins with dots (`kv.<tenant>.<namespace>.<serviceaccount>`), because none of the parts may contain one.
- **Give each family of names its own prefix and part count**, so that a name from one family can never equal a name from another.
- **Quote every value derived from a tenant name.** `1234` is a valid tenant name and a YAML number.
- **Check tenant names that become identifiers elsewhere.** The `Tenant` CRD does not restrict names to what your tool accepts. Vault Enterprise skips a tenant whose name is not a DNS label, and lists each skipped tenant and the reason in a ConfigMap, instead of failing the parent.

## Deletion

template-operator-v2 deletes an object as soon as no render contains it. That happens when a tenant opts out, when a filter narrows, when the parent's TemplateInstance is deleted, and when a bug produces an empty render. Decide, per kind, whether that is acceptable.

| If deleting the object | Then |
|---|---|
| loses nothing; it is recreated identically | Let template-operator-v2 delete it. |
| breaks people who depend on it, but loses no data | Annotate it `templates.v2.stakater.com/deletion-policy: Orphan`, so it is released instead of deleted. Consider making that a per-tenant choice. |
| destroys data, such as a Vault namespace and its secrets | Do not rely on Kubernetes alone. Also protect it in the tool itself. |

The ArgoCD extension orphans `AppProject`s by default, because deleting one strands every Application that uses it. Purging is an opt-in value that a tenant can override.

The Vault Enterprise extension goes further. A tenant's Vault namespace and its secrets are rendered by the **parent**, for every valid Tenant, so they live as long as the `Tenant` resource rather than as long as its namespaces. On top of that, the production Vault policy that `vault-config-operator` logs in with denies `delete` on namespaces and mounts. A deleted CR then stays in `Terminating` and the data stays in Vault until an administrator decides.

## Uninstall in the right order

```bash
kubectl -n <namespace> delete templateinstances.templates.v2.stakater.com <parent> --wait
kubectl -n <namespace> wait templateinstances.templates.v2.stakater.com \
  -l templates.v2.stakater.com/instance=<parent> --for=delete --timeout=5m
helm uninstall <release> -n <namespace>
kubectl delete <the RBAC kept by the chart>
```

Deleting the parent TemplateInstance deletes its children, and they delete their objects. That takes time, and it needs the RBAC. So:

- **Mark the RBAC `helm.sh/resource-policy: keep`.** If ArgoCD manages the chart, also mark it `argocd.argoproj.io/sync-options: Prune=false,Delete=false`. Otherwise `helm uninstall`, or an ArgoCD prune, removes the RBAC in the same step as the parent. template-operator-v2 is then forbidden from removing its finalizers, and everything stays in `Terminating`.
- **Keep reap permissions separate from create.** If a "disable" value removes all the RBAC, template-operator-v2 can no longer delete what it already owns. Gate `create` on the value; keep `get`, `update`, `patch` and `delete` unconditional.
- **Keep anything a downstream controller needs to clean up.** The Vault Enterprise chart creates the ServiceAccount that `vault-config-operator` logs in with. If that ServiceAccount goes before the CRs, `vault-config-operator` fails every delete and every CR stays in `Terminating`.

## Report health honestly

A child that is `Ready` means its objects were **applied**. It does not mean your tool accepted them.

- **Read the tool's own status back through `outputs`**, so the TemplateInstance shows what happened downstream.
- **Know what that status can say.** The status `vault-config-operator` writes cannot tell you whether an object is healthy now. It sets `ReconcileSuccessful` and `ReconcileFailed` side by side, and their timestamps stop moving after the first write. Vault Enterprise's outputs therefore say "has succeeded at least once" and "last error ever", and its docs say exactly that.
- **Aggregate in the parent.** A `fromAll` output over the child TemplateInstances gives one object that answers whether every tenant is reconciled, and why not.

## Test it

Test at four levels. Each catches failures the level above it cannot.

| Level | Needs | Catches |
|---|---|---|
| `helm lint` and the chart-value guards | nothing | Chart structure, and bad values refused at install |
| Render tests | Go, no cluster | Wrong output for a given set of Tenants, and parent failures |
| Admission tests | `envtest` and template-operator-v2's CRDs | Templates the API server would reject: schema and CEL rules |
| End-to-end | a kind cluster with template-operator-v2 | What template-operator-v2 and your tool actually do |

### Render tests

Render tests are where most bugs are caught, and they are fast. Run your gotemplate files through the **same function set template-operator-v2 uses, not through Helm.** Helm adds functions such as `toYaml`, `include` and `.Files`, and replaces `toJson` and `fromJson` with its own versions. A gotemplate can pass under Helm and fail on the cluster.

template-operator-v2 0.0.8 renders with Sprig's text functions minus `env`, `expandenv` and `getHostByName`, and with `missingkey=error`. This engine reproduces that:

```go
package render

import (
    "bytes"
    "errors"
    "io"
    "os"
    "text/template"

    "github.com/Masterminds/sprig/v3"
    "gopkg.in/yaml.v3"
)

func funcs() template.FuncMap {
    f := sprig.TxtFuncMap()
    delete(f, "env")
    delete(f, "expandenv")
    delete(f, "getHostByName")
    return f
}

// Render executes one gotemplate file against a parameter set.
func Render(path string, params map[string]any) ([]map[string]any, error) {
    src, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    t, err := template.New("template").Funcs(funcs()).Option("missingkey=error").Parse(string(src))
    if err != nil {
        return nil, err
    }
    var out bytes.Buffer
    if err := t.Execute(&out, map[string]any{"parameters": params}); err != nil {
        return nil, err
    }
    var docs []map[string]any
    dec := yaml.NewDecoder(&out)
    for {
        var d map[string]any
        if err := dec.Decode(&d); errors.Is(err, io.EOF) {
            return docs, nil
        } else if err != nil {
            return nil, err
        }
        if len(d) > 0 {
            docs = append(docs, d)
        }
    }
}
```

Then table-drive the parent with the shapes Tenants really take. This is the tutorial's parent under test:

```go
func TestParent(t *testing.T) {
    optIn := map[string]any{"tenant-info.example.com/enabled": "true"}
    cases := []struct {
        name       string
        tenants    []any
        namespaces []any
        children   []string
    }{
        {"no tenants", nil, nil, nil},
        {"not opted in", []any{tenant("acme", nil)}, []any{namespace("acme-dev", "acme")}, nil},
        {"near-miss opt-in", []any{tenant("acme", map[string]any{"tenant-info.example.com/enabled": "True"})}, nil, nil},
        {"opted in", []any{tenant("acme", optIn), tenant("globex", nil)},
            []any{namespace("acme-dev", "acme"), namespace("globex-dev", "globex")},
            []string{"tenant-info-tenant-acme"}},
        {"no namespaces", []any{tenant("initech", optIn)}, nil, []string{"tenant-info-tenant-initech"}},
        {"tenant named parent", []any{tenant("parent", optIn)}, nil, []string{"tenant-info-tenant-parent"}},
    }
    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            docs, err := Render("../../files/parent.tpl", parentParams(tc.tenants, tc.namespaces))
            if err != nil {
                t.Fatalf("parent failed, which fails every tenant: %v", err)
            }
            var got []string
            for _, d := range docs {
                got = append(got, d["metadata"].(map[string]any)["name"].(string))
            }
            if strings.Join(got, ",") != strings.Join(tc.children, ",") {
                t.Fatalf("children = %v, want %v", got, tc.children)
            }
        })
    }
}
```

`tenant`, `namespace` and `parentParams` are small helpers that build the maps a LIST returns. `parentParams` adds the parent's other parameters with the chart's default values. Feed each rendered child's parameters into the child gotemplate in the same way, and assert on the objects it renders and on the errors it should raise.

A test that cannot fail proves nothing. Break each guard on purpose and check that its test goes red. For example, change one `index $t.metadata "annotations"` in the parent to `$t.metadata.annotations`, and the "not opted in" case fails with `map has no entry for key "annotations"`, the same error the cluster gives.

The ArgoCD extension adds three more kinds of render test:

- **Golden files**: one fixture per scenario (a cluster's Tenants, Namespaces and IntegrationConfig, plus chart values), rendered and compared with a checked-in result.
- **Property tests**: invariants over randomly generated clusters, such as "no tenant's destinations ever include another tenant's namespace".
- **A scale test**: 1,000 tenants over about 8,000 namespaces must render within 10 seconds, which catches an accidentally quadratic loop.

### Admission and end-to-end tests

**Admission tests** start a real API server with `envtest`, install template-operator-v2's CRDs, and apply the Templates your chart renders. They catch what `helm lint` cannot: a field the CRD schema rejects, or a CEL rule on `outputs` or parameters. Vendor the CRDs at the template-operator-v2 version you support, and refresh them when you upgrade.

**End-to-end tests** run the [tutorial's lab](tutorial.md#step-1-create-a-cluster) in CI, with your tool installed, and assert on what the tool does, not only on what was rendered. A useful order:

1. Install the chart, then create tenants and namespaces.
1. Assert on the tool's view. For example, log in to Vault as the workload's ServiceAccount and read its secret, or check that ArgoCD accepts the `AppProject`.
1. Assert that one tenant cannot reach another tenant's objects. Pair every denial with a matching allowed request, so that a wrongly configured test cannot pass by being refused for the wrong reason.
1. Opt a tenant out, and check that what should go goes and what should stay stays.
1. Uninstall in the documented order, every run.

## Before you ship

- [ ] The parent survives Tenants with no annotations, no labels, `spec: null` and `accessControl: null`.
- [ ] No per-tenant input is parsed in the parent.
- [ ] Every security-relevant input fails closed when it is absent, `null` or empty.
- [ ] Every chart value that affects all tenants is checked by a template guard, not only by the schema.
- [ ] Child names cannot collide with the parent's.
- [ ] RBAC grants list and watch at cluster scope on every rendered kind, and survives `helm uninstall`.
- [ ] Your docs list every permission the chart grants template-operator-v2, and the cluster has the write-scope policy, with your namespace on its list.
- [ ] `sync: strict`, with `metadata.finalizers` and any field your tool writes in `ignoreFields`.
- [ ] Every kind has a deletion decision: delete, orphan, or protected in the tool.
- [ ] Health is read back from the tool's own status, and documented for what it can and cannot say.
- [ ] The uninstall order is documented and tested.
- [ ] The template-operator-v2 version you tested against is pinned and written down.
