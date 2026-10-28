# Security

## The trust boundary is the namespace label

**The `stakater.com/tenant` label on a namespace is what grants a tenant's Vault access.** The parent finds a tenant's namespaces by that label, and the tenant chart renders a `Policy` and login role for every annotated ServiceAccount in them. So anyone who can set `stakater.com/tenant: X` on a namespace can give their own ServiceAccounts tenant X's Vault access.

Keep the label under the platform's control: only MTO and cluster admins may set or change it, and tenant users must not hold `patch`/`update` on `namespaces` at cluster scope. MTO's own namespace handling relies on the same label, so this is a rule MTO already needs.

Inside a tenant, the ServiceAccount annotations decide which app gets which access — anyone who can annotate a ServiceAccount in a tenant namespace can request that tenant's access for it, up to `admin`. Treat "who can annotate ServiceAccounts in a tenant namespace" as part of the tenant's own trust boundary.

## What the extension validates

- A ServiceAccount carrying no `vault.stakater.com/` annotation renders nothing.
- An unknown `vault.stakater.com/` annotation is an **error**, not ignored — the app gets a `vault-config-<sa>.error` `ConfigMap` and no access. `transit` and `pki` are rejected too (this extension does not support them).
- A cross-tenant export/import names a peer that must actually exist, or the entry is dropped.
- Tenant names are checked (DNS label, ≤63 chars, not the shared-namespace name); a tenant that fails is skipped and listed, with the reason, in a `ConfigMap` — it never breaks the other tenants.

## How the extension scopes Template Operator v2

The extension renders through Template Operator v2, which applies objects with its own ServiceAccount. The bootstrap grants that account the permissions this integration needs to manage the resources it renders — the `vault-config-operator` CRs, the per-workload ConfigMaps and the ExternalSecrets.

Keep one administrative rule: **authoring a Template Operator v2 `Template` is a privileged operation** — anyone who can create `Template`s and `TemplateInstance`s drives the operator with those permissions. MTO's tenant roles do not grant that, and it should not be granted to tenants. Template Operator v2's own security model (the operator applies with its ServiceAccount, scoped by RBAC) is the reference for how those permissions are bounded.

---

**Previous:** [Delivery and login](delivery-and-login.md) · **Next:** [Operating](operating.md)
