# Real extensions

Stakater's ArgoCD and Vault Enterprise extensions both use the parent and child pattern from the [tutorial](tutorial.md), but each made different choices. This page walks through those choices, with excerpts from the charts.

| | ArgoCD | Vault Enterprise |
|---|---|---|
| Per tenant | One ArgoCD `AppProject` | A Vault namespace, with secrets engines, login roles and policies: two dozen or more `vault-config-operator` CRs |
| Downstream controller | ArgoCD | [`vault-config-operator`](https://github.com/redhat-cop/vault-config-operator) (VCO), which writes the CRs to Vault |
| Child written as | An inline gotemplate | A published Helm chart |
| Charts | One | Two: a bootstrap chart installed once, and a tenant chart that template-operator-v2 pulls |
| Who gets it | Tenants that opt in (`OnAnnotation` by default) | Every tenant with a valid name |
| Parent reads | Tenants, Namespaces, the IntegrationConfig | Tenants, Namespaces |
| Child reads | Nothing: everything comes from the parent | ServiceAccounts and Deployments in the tenant's namespaces |

## ArgoCD

The ArgoCD extension gives every opted-in tenant an `AppProject`, scoped to that tenant's namespaces, with owner, edit and view roles. It replaces an earlier Go controller in MTO, and its whole mechanism is three template-operator-v2 objects plus RBAC.

```text
Tenant ───────────┐
Namespace ────────┼──▶ parent TemplateInstance ──▶ one child per tenant ──▶ one AppProject per tenant
IntegrationConfig ┘
```

### Three inputs, three watches

The parent TemplateInstance reads two cluster-wide lists and one object. That is three watches however many tenants there are. A namespace event that affects one tenant rewrites only that tenant's child.

```yaml
parameters:
  - name: tenants
    valueFrom:
      objectFieldRef:
        apiVersion: tenantoperator.stakater.com/v1beta3
        kind: Tenant
        jsonPath: .items
  - name: namespaces
    valueFrom:
      objectFieldRef:
        apiVersion: v1
        kind: Namespace
        jsonPath: .items
  # A GET, read shallowly at .spec. NEVER give it a defaultValue: masking a
  # failed read yields an empty privileged list, which puts privileged
  # namespaces into every tenant's destinations.
  - name: integrationConfig
    valueFrom:
      objectFieldRef:
        apiVersion: tenantoperator.stakater.com/v1beta1
        kind: IntegrationConfig
        name: tenant-operator-config
        namespace: multi-tenant-operator
        jsonPath: .spec
```

From the IntegrationConfig it reads only `accessControl.privileged`. Privileged namespaces are kept out of every tenant's destinations, and privileged groups are added to every role. If the field is absent or `null`, the parent refuses to render. See [Fail closed](design-rules.md#fail-closed).

### The parent does the cluster-wide work

The parent makes three passes. The first picks the opted-in tenants. The second buckets namespaces by tenant in a single pass over the Namespace list, dropping privileged namespaces. The third emits one child per tenant:

```yaml
{{- range $ns := .parameters.namespaces }}
{{- $owner := dig $nsLabel "" (default dict (index $ns.metadata "labels")) }}
{{- if and $owner (hasKey $taken $owner) (or $allowCP (ne $ns.metadata.name $argoNs)) }}
{{- $isPriv := false }}
{{- range $p := $privNs }}{{- if mustRegexMatch $p $ns.metadata.name }}{{- $isPriv = true }}{{- end }}{{- end }}
{{- if not $isPriv }}{{- $_ := set $byTenant $owner (append (get $byTenant $owner | default list) $ns.metadata.name) }}{{- end }}
{{- end }}
{{- end }}
```

The privileged-namespace check runs here, not in the child, because only the parent sees the IntegrationConfig. Everything a tenant controls is passed down as raw text.

### Per-tenant overrides, parsed in the child

A Tenant can override chart defaults with annotations: source repositories, resource allow and deny lists, sync windows, and whether its `AppProject` is deleted with it. The parent copies each annotation into a child parameter verbatim. An absent annotation inherits the chart default, and an explicit `"[]"` overrides it with an empty list:

```yaml
{{- $wlJson := $defaultWl }}{{- if hasKey $annos $aWl }}{{- $wlJson = index $annos $aWl }}{{- end }}
```

The child decodes each one with `mustFromJson`, checks its shape field by field, and fails for that one tenant if anything is wrong. A near-miss on the purge annotation is refused rather than read as "retain":

```yaml
{{- if not (has .parameters.onDeletePurge (list "true" "false")) }}
{{- fail (printf "on-delete-purge must be exactly \"true\" or \"false\", got %q" .parameters.onDeletePurge) }}
{{- end }}
```

### Deletion: orphan by default

Deleting an `AppProject` strands every Application that uses it. So unless purge is on, the child annotates the project to be released instead of deleted:

```yaml
metadata:
  name: {{ $t | quote }}
  namespace: {{ $argoNs | quote }}
  {{- if not $purge }}
  annotations:
    templates.v2.stakater.com/deletion-policy: Orphan
  {{- end }}
```

### Least-privilege RBAC

The chart grants template-operator-v2 cluster-wide read on Tenants, Namespaces and `AppProject`s, but writes to `AppProject`s only through a RoleBinding in the ArgoCD namespace. `list` and `watch` stay cluster-wide, because teardown lists each rendered kind across the cluster. The verbs used for cleanup are granted unconditionally. Only `create` follows the scaffolding setting, so that turning the extension off still lets template-operator-v2 remove what it owns:

```yaml
rules:
  - apiGroups: ["argoproj.io"]
    resources: ["appprojects"]
    verbs: ["get", "update", "patch", "delete"]
  {{- if ne .Values.scaffolding.mode "Never" }}
  - apiGroups: ["argoproj.io"]
    resources: ["appprojects"]
    verbs: ["create"]
  {{- end }}
```

Every RBAC object carries both `helm.sh/resource-policy: keep` and `argocd.argoproj.io/sync-options: Prune=false,Delete=false`, so neither `helm uninstall` nor an ArgoCD prune can delete it before teardown is finished.

### Sync and the fields ArgoCD writes

The Templates use `sync: strict`. Two fields are exempt: `metadata.finalizers`, which template-operator-v2 manages itself, and `spec.roles[*].jwtTokens`, where ArgoCD writes project tokens. Without the second exemption, `argocd proj role create-token` is refused by template-operator-v2's webhook. A template guard refuses `strict` without both exemptions at install time.

### How it is tested

| Layer | Catches |
|---|---|
| `helm lint` | Chart structure |
| Render tests, through template-operator-v2's function map | Wrong `AppProject` content. Fixtures are discovered, not listed, so adding a file adds a test. Property tests check invariants over random clusters, and a scale test renders 1,000 tenants over about 8,000 namespaces. |
| An equivalence test | Every difference from the Go controller it replaces is deliberate and listed |
| Admission tests with `envtest` | Template CRs the API server would reject |
| End-to-end on kind | What template-operator-v2 and ArgoCD actually do, including paths MTO's own webhooks make untestable on a real cluster, such as a privileged namespace labelled for a tenant |

## Vault Enterprise

The Vault Enterprise extension gives every tenant its own Vault Enterprise namespace, configured through `vault-config-operator` CRs. It renders configuration only; VCO writes it to Vault.

It is split into two charts:

| Chart | Installed | Role |
|---|---|---|
| Bootstrap | Once per cluster, by hand | The parent: watches Tenants, renders each tenant's Vault namespace and KV mount, and emits the child TemplateInstances. Also creates the ServiceAccount VCO logs in with. |
| Tenant | Never by hand | The child: a published Helm chart that template-operator-v2 pulls and renders once per tenant. |

```text
Tenant CRs ──► parent TemplateInstance
                 per Tenant               Namespace <tenant>, SecretEngineMount <tenant>-kv
                 per Tenant with a        TemplateInstance ...-<tenant>      → core slice
                 labelled namespace       TemplateInstance ...-<tenant>.eso  → eso slice

core slice    auth mount, a Policy and a login role per annotated ServiceAccount,
              SSO roles, and a vault-config-<sa> ConfigMap for each workload
eso slice     SecretStore and ExternalSecret objects for each workload
```

### A Helm chart as the child

With two dozen or more CRs per tenant and real logic in each, the child is a full Helm chart. The child Template points at the published chart and passes the per-tenant values through `valuesTemplate`. The backticks stop Helm from rendering template-operator-v2's actions when the bootstrap chart is installed:

```yaml
spec:
  parameters:
    - name: tenant
      required: true
    - name: knownTenants
      value: ""
    - name: serviceAccounts
    - name: deployments
  helm:
    chart:
      repository:
        url: {{ $.Values.tenantChart.registry | quote }}
        name: {{ $.Values.tenantChart.name | quote }}
        version: {{ $.Values.tenantChart.version | quote }}
    releaseName: {{ $.Values.tenantChart.releaseName | quote }}
    version: v4
    valuesTemplate: |
      component: {{ $slice.component }}
      tenant: {{ `{{ .parameters.tenant | quote }}` }}
      knownTenants: {{ `{{ .parameters.knownTenants | quote }}` }}
      serviceAccounts: {{ `{{ .parameters.serviceAccounts | toJson }}` }}
      deployments: {{ `{{ .parameters.deployments | toJson }}` }}
      {{- $installWide | nindent 6 }}
```

Two consequences follow from template-operator-v2 pulling the *published* tenant chart:

- **Values reach the tenant chart only through the bootstrap.** Editing the tenant chart's `values.yaml` has no effect on a cluster. The bootstrap exposes `tenantValues` for install-wide settings, and fails the render if one of them collides with a value it sets itself.
- **Versions must match.** The bootstrap pins `tenantChart.version`, and a check keeps it equal to the tenant chart's own version.

### The child reads the tenant's namespaces

Unlike ArgoCD, the child reads the cluster too. It lists ServiceAccounts and Deployments, scoped by `namespaceSelector` to the tenant's labelled namespaces, and grants Vault access to each ServiceAccount that asks for it with annotations:

```yaml
- name: serviceAccounts
  valueFrom:
    objectFieldRef:
      apiVersion: v1
      kind: ServiceAccount
      jsonPath: .items
      namespaceSelector:
        matchLabels:
          stakater.com/tenant: {{ $name | quote }}
```

A child whose `namespaceSelector` matches no namespace fails parameter validation. So the parent emits children only for tenants that have at least one labelled namespace. It counts them in one pass over the Namespace list.

### Data belongs to the parent

A tenant's Vault namespace and KV mount hold its secrets, so they are rendered by the **parent**, for every valid Tenant, not by the child:

```yaml
{{- range $name := $tenants }}
---
apiVersion: redhatcop.redhat.io/v1alpha1
kind: Namespace
metadata: { name: {{ $name | quote }}, namespace: {{ $cfgNs }} }
spec:
  authentication:
    {{ $auth }}
  name: {{ $name | quote }}
```

A child exists only while its tenant has a labelled namespace. If the Vault namespace lived in the child, deleting a tenant's last namespace would delete its Vault namespace and every secret in it. In the parent, the data lives as long as the `Tenant` resource. Deleting the last namespace removes the grants and keeps the secrets, and labelling a namespace again brings the grants back.

VCO has no deletion policy: deleting a `Namespace` CR deletes the Vault namespace. So there is a second line of defence in Vault itself. The policy VCO logs in with denies `delete` on namespaces and mounts. A deleted CR then stays in `Terminating`, and nothing is lost until an administrator decides.

### Skipping, not failing

The `Tenant` CRD does not restrict names, but a Vault namespace, a label value and the extension's dot-joined object names all do. The parent skips a tenant whose name is not a DNS label, is longer than 63 characters, or equals the shared namespace's name. It lists every skip and the reason in a ConfigMap, instead of failing the render for everyone:

```yaml
{{- range $t := (default list .parameters.tenants) }}
{{- $n := toString $t.metadata.name }}
{{- if not (regexMatch "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$" $n) }}
{{- $_ := set $skipped $n "the name is not a DNS label (lowercase letters, digits and hyphens, no dots): nothing is rendered for this tenant" }}
{{- else if gt (len $n) 63 }}
...
```

### Errors reported where they happen

Inside a tenant, a wrongly configured ServiceAccount does not fail the render either. It gets a ConfigMap `vault-config-<sa>.error` that says what is wrong, and nothing else, so one namespace's mistake does not stop the tenant's other namespaces. An unknown `vault.stakater.com/` annotation is reported as an error, not ignored.

### Slices, so one missing CRD cannot break everything

The tenant chart renders in two slices, `core` and `eso`, each from its own child Template and TemplateInstance. If the External Secrets Operator's CRDs are missing, only the `.eso` TemplateInstance fails, and the core Vault wiring applies regardless.

### Honest health

A `Ready` child means its CRs were applied, not that VCO wrote them to Vault. The child Templates read the status VCO writes back through `outputs`, two fields per kind: whether the object has ever reconciled successfully, and the last error ever seen. The status cannot say more than that: VCO sets its success and failure conditions side by side, and their timestamps freeze after the first write. The extension's docs state that limit rather than implying a live health signal.

### How it is tested

- **Render tests** with fixtures and a golden render. Each guard has a check that fails when the guard is removed.
- **CRD validation** of every rendered CR against a vendored copy of the VCO CRDs, through the API server's admission pipeline.
- **End-to-end** on a kind lab with Vault Enterprise, VCO, Dex and Keycloak. Every assertion is made in Vault, logged in as the workload's own ServiceAccount, and every denial is paired with a matching allowed request.

## What to take from them

| Question | ArgoCD's answer | Vault Enterprise's answer |
|---|---|---|
| How much per tenant? | One object, so an inline gotemplate | Dozens, so a published chart |
| What does the child need to read? | Nothing beyond what the parent passes | The tenant's ServiceAccounts and Deployments |
| What must survive deletion? | The `AppProject`, orphaned by default | The data, owned by the parent and protected in Vault |
| What can a tenant break? | Only its own child, through its own annotations | Only its own ServiceAccount's access, reported in an error ConfigMap |

Start from the tutorial's chart, then follow whichever of these is closer to your tool.
