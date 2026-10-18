# Security

The extension's defaults are least privilege. This page explains the ones that matter and the things that can look correct while being unsafe.

## The ArgoCD namespace is never a tenant destination

An Application in the control-plane namespace may reference *any* `AppProject`, and the application controller that syncs it is cluster-admin — so a tenant able to deploy there could create Applications, AppProjects or repository/cluster Secrets for every project, which is ArgoCD admin. The `AppProject` does not need the ArgoCD namespace as a destination: it lives there whatever `destinations` says.

`argocd.allowControlPlaneDestination: true` restores the legacy shape (the ArgoCD namespace as a destination). It is unsafe and exists for migration only.

## Roles are least privilege

With `roles.profile: leastPrivilege` (the default):

| Role | `applications` | `applicationsets` | `exec` |
|:---|:---|:---|:---|
| owner | `*` | `*` | off (`create` with `roles.exec.enabled`) |
| edit | `get`, `sync`, `update`, `update/*`, `action/*` | `get` | off |
| view | `get` | `get` | off |

Edit cannot create, delete or override Applications. ArgoCD's web terminal runs as the `argocd-server` ServiceAccount — outside the tenant's own RBAC and audit trail — so `exec` is off unless you enable it (owner only). `roles.profile: extensionsCompatible` restores the legacy broad `*`/`get` shape, for migration only; consider also setting `application.sync.requireOverridePrivilegeForRevisionSync` in ArgoCD (3.2+).

## Cluster-scoped kinds are cluster-wide

A cluster-scoped kind on the allow-list is granted for **every** object of that kind in the cluster, and the controller that syncs it is cluster-admin. With `{group: "", kind: Namespace}`, a tenant can change or delete any namespace — another tenant's, or `kube-system` — and can move a namespace into its own destinations by setting its `stakater.com/tenant` label.

Since ArgoCD 3.3 an entry can take a `name` (a glob). Older ArgoCD drops the field on apply, turning the entry back into "every object of this kind", so the chart refuses a `name` unless `argocd.allowClusterResourceNames: true` confirms 3.3+. Use exact names; a prefix glob is not tenant-safe (`{{ tenant }}-*` for `acme` also matches `acme-corp-prod`). See [Reference](reference.md#cluster-scoped-kinds).

## Per-tenant overrides are as trusted as the Tenant

A `Tenant` can override its repositories and resource lists by annotation ([Reference](reference.md#per-tenant-overrides)). Those values are shape-checked but not value-checked, so whoever can annotate a `Tenant` can widen that tenant's access up to what the annotations allow. Keep `Tenant` write access with the platform, and treat anyone who can annotate a `Tenant` as trusted with its ArgoCD access.

## Template authors share these permissions

The extension runs on Template Operator, which renders **every** `Template` on the cluster with one ServiceAccount — the one this chart grants `AppProject` write in the ArgoCD namespace. A `Template` can target any namespace, so **anyone who can create a `Template` and a `TemplateInstance` can use that grant**, not only this chart.

MTO's tenant roles do not include Templates by default, so tenants cannot do this out of the box. It becomes reachable the moment anyone is bound to Template Operator's own `template-editor`/`templateinstance-editor` roles, or an equivalent. If you grant those, confine Template Operator's writes with a `ValidatingAdmissionPolicy` that only allows a rendered object when its owning `TemplateInstance` is in a namespace you trust. Template Operator stamps `templates.v2.stakater.com/instance-namespace` on every object it renders and overwrites any value a template sets, so the policy can trust it and a template cannot spoof it.

### Confining Template Operator's writes

Set `is-operator` to your Template Operator identity, and list the namespaces that hold extensions (e.g. `multi-tenant-operator`) in the `validations` expression. Verified on Template Operator 0.0.8: cross-namespace and cluster-scoped writes from a `TemplateInstance` not on the allow-list are denied, while own-namespace and allow-listed writes pass and teardown is unaffected.

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
    - name: is-operator
      expression: 'request.userInfo.username == "system:serviceaccount:multi-tenant-operator:tenant-operator-template-operator-v2"'
    - name: is-rendered-object
      expression: '(object != null && "templates.v2.stakater.com/instance-namespace" in object.metadata.?labels.orValue({})) || (oldObject != null && "templates.v2.stakater.com/instance-namespace" in oldObject.metadata.?labels.orValue({}))'
  validations:
    - expression: 'variables.owner in ["multi-tenant-operator"] || (has(variables.obj.metadata.namespace) && variables.obj.metadata.namespace == variables.owner)'
      messageExpression: '"template-operator-v2: a TemplateInstance in namespace " + variables.owner + " may only write objects in its own namespace"'
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata: { name: template-operator-v2-write-scope }
spec:
  policyName: template-operator-v2-write-scope
  validationActions: [Deny]
```

## Before production

Four ways to end up with something that looks correct and isn't:

- **Seed the resource lists.** `clusterResourceWhitelist` and `namespaceResourceBlacklist` are chart values; if you forget them every tenant's project silently loses both lists.
- **Set `sourceRepos`.** A project with none permits no repository — see [Giving a tenant an AppProject](giving-a-tenant-an-appproject.md).
- **List real groups and users.** `roles[].groups` gets the MTO-generated group first, but MTO only creates it when the tenant-operator runs with `PLATFORM_TYPE=Openshift`. A tenant whose owners are only that group gets a project granting access to nobody.

### Match users the way your login provides them

The chart adds the tenant's users to `roles[].groups`, e.g. `alice@acme.example`. ArgoCD compares that with the login token's user ID and the claims named in `argocd-rbac-cm` `scopes` (default `[groups]`). Behind Dex the user ID is an opaque value, not an email, so with the default the user entries grant nothing. Add the claim that carries the user name the `Tenant` uses — usually `email`:

```yaml
# argocd-rbac-cm, in the ArgoCD namespace
data:
  scopes: '[groups, email]'
```

ArgoCD reloads it without a restart. Only include a claim users cannot change themselves in the identity provider, and note the setting is global (email entries in `policy.csv` start to match too, and a user in a project role can create tokens for that role).

---

**Previous:** [Identity and sync impersonation](identity-and-impersonation.md) · **Next:** [Operating](operating.md)
