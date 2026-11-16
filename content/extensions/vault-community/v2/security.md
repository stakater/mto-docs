# Security

On Vault Enterprise a namespace around each tenant contains whatever a policy inside it grants. Vault Community has no namespaces: every tenant's mounts, policies and roles live side by side, and **the policy is the only wall between tenants**. So the extension never lets that wall be written by hand, and checks it twice.

## The scope check

Every policy and role the charts render passes a scope check, or the render fails:

- each policy is one-line `path "…" { capabilities = [...] }` stanzas, with no `sudo` and no `+`;
- every path is inside the tenant's own mount, `<tenant>/kv/{data,metadata,delete,undelete,destroy}/<env>/`, or its named shares in `shared/kv/`;
- the tenant's name is closed by `/` before any wildcard, so tenant `acme` can never match `acme-corp`;
- nothing is under `sys/`, `auth/`, `identity/` or `cubbyhole/`;
- a role binds only its own policy, its tenant's mount, its ServiceAccount, and its namespace by name **and** tenant label.

No role, `admin` included, can write a policy, a mount, an auth role or a mount's config. Tenants own their secrets; the platform owns Vault.

## The admission policies

The render check covers what the charts render. The bootstrap chart applies the same check at the Kubernetes API server, to every `redhatcop.redhat.io` object in `configNamespace`, whoever writes it — the charts, Template Operator, or a person. It installs four `ValidatingAdmissionPolicy` objects, each with failure policy `Fail`:

| Policy | Refuses |
|:---|:---|
| `mto-extension-vault-community-vco-kinds` | a VCO CR of a kind the extension does not render (VCO has about 80); any `spec.connection`, which would send the VCO login to another address; any `spec.authentication` other than the one the installation sets, or one with a Vault namespace |
| `mto-extension-vault-community-vco-origin` | an object Template Operator renders for a `TemplateInstance` outside `configNamespace` — a Template in a tenant namespace cannot write VCO CRs here |
| `mto-extension-vault-community-vco-scope` | a policy, role or mount outside its tenant's scope (the scope check above), a mount of another shape or at a reserved name, an OIDC config for another issuer |
| `mto-extension-vault-community-vco-cluster` | a Kubernetes auth config for another API server, or another CA than this cluster's `kube-root-ca.crt` |

A deletion is not refused: the VCO finalizer updates pass. `admission.enabled` exists only for clusters older than Kubernetes 1.30. **Turning it off removes the wall** between tenants.

## The VCO identity in Vault

The VCO policy limits the names it can write and the types of mount it can create, but not what a `kv.*` policy contains: Vault Community has no namespace to hold that in. The VCO token is therefore close to root, and the admission policies are what bound what VCO is asked to write. Protect the VCO identity like that of a Vault admin:

- nobody but VCO may create tokens for the ServiceAccount `vault-config/vco-admin`, or exec into the VCO pod;
- the VCO login role binds `vault-config` only;
- only Template Operator and Vault admins may write to `configNamespace`. The admission policies hold for any writer, but a writer there can still delete the extension's objects — which revokes tenants' access, never their data.

## The trust boundary is the namespace label

**The `stakater.com/tenant` label on a namespace is what grants a tenant's Vault access.** The parent finds a tenant's namespaces by that label, and the tenant chart renders a policy and login role for every annotated ServiceAccount in them. So anyone who can set `stakater.com/tenant: X` on a namespace can give their own ServiceAccounts tenant X's Vault access.

Keep the label under the platform's control: only MTO and cluster admins may set or change it, and tenant users must not hold `patch`/`update` on `namespaces` at cluster scope. MTO's own namespace handling relies on the same label, so this is a rule MTO already needs.

Each login role binds its namespace by **name and tenant label**. Kubernetes does not reserve namespace names per tenant, so a namespace that another tenant creates later with a deleted namespace's name gets nothing.

Inside a tenant, the ServiceAccount annotations decide which app gets which access — anyone who can annotate a ServiceAccount in a tenant namespace can request that tenant's access for it, up to `admin`. Treat "who can annotate ServiceAccounts in a tenant namespace" as part of the tenant's own trust boundary.

## What the extension validates

- A ServiceAccount carrying no `vault.stakater.com/` annotation renders nothing.
- An unknown `vault.stakater.com/` annotation is an **error**, not ignored — the app gets a `vault-config-<sa>.error` `ConfigMap` and no access. `transit` and `pki` are rejected too (this extension does not support them).
- A cross-tenant export/import names a peer that must exist, or the entry renders nothing until it does.
- Tenant names are checked: a DNS label of at most 29 characters, not the shared name (`shared`), and not a reserved path — `sys`, `auth`, `identity`, `cubbyhole`, `agent-registry`, `token`, the first segment of the VCO login mount, and every entry of `parent.reservedPaths`. A tenant that fails is skipped and listed, with the reason, in the `ConfigMap` `mto-extension-vault-community-skipped-tenants` — it never breaks the other tenants.

## How the extension scopes Template Operator v2

The extension renders through Template Operator v2, which applies objects with its own ServiceAccount. The bootstrap grants that account the permissions this integration needs to manage the resources it renders — the `vault-config-operator` CRs, the per-workload ConfigMaps and the ExternalSecrets.

Keep one administrative rule: **authoring a Template Operator v2 `Template` is a privileged operation** — anyone who can create `Template`s and `TemplateInstance`s drives the operator with those permissions. MTO's tenant roles do not grant that, and it should not be granted to tenants. The `vco-origin` admission policy stops a Template outside `configNamespace` from writing VCO CRs, but a tenant's Template still runs with Template Operator's rights elsewhere.

## What Community Edition cannot isolate

Some things in Vault Community are shared by every tenant. The extension does not hide or emulate them:

| Shared by every tenant | Consequence | Per tenant on |
|:---|:---|:---|
| one root namespace | the policy is the only wall; a policy written by hand outside the extension can still cross tenants | Vault Enterprise, OpenBao |
| the VCO identity in Vault | close to root; admission bounds what VCO is asked, nothing bounds its token | Vault Enterprise, OpenBao |
| one audit log | per-tenant audit is a filter you run downstream, on `<tenant>/` and `auth/<tenant>/` | Vault Enterprise |
| one identity store | entities and groups are global, readable only by Vault admins | Vault Enterprise, OpenBao |
| one `default` policy | every tenant token carries it; an edit reaches every tenant | Vault Enterprise, OpenBao |
| quotas by source address only | no per-tenant fairness | Vault Enterprise (lease-count quotas) |
| no delegated administration | tenants never manage policies or mounts — by design here | Vault Enterprise, OpenBao |

---

**Previous:** [Delivery and login](delivery-and-login.md) · **Next:** [Operating](operating.md)
