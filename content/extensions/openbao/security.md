# Security

## The trust boundary is the namespace label

The extension finds a tenant's namespaces by the `stakater.com/tenant` label, and renders a policy and login role for every annotated ServiceAccount in them. So anyone who can set `stakater.com/tenant: X` on a namespace can give their own ServiceAccounts tenant X's OpenBao access.

Keep the label under the platform's control: only MTO and cluster admins may set or change it, and tenant users must not hold `patch`/`update` on `namespaces` at cluster scope. MTO's own namespace handling relies on the same label.

Inside a tenant, the ServiceAccount annotations decide which app gets which access — anyone who can annotate a ServiceAccount in a tenant namespace can request that tenant's access for it, up to `admin`. Treat "who can annotate ServiceAccounts in a tenant namespace" as part of the tenant's own trust boundary.

## How access is scoped

- A workload is confined to **one namespace and one application path** — the login role is bound to the ServiceAccount, and the policy is scoped to `kv/data/<env>/<namespace>/<app>/`. Two workloads in one namespace cannot read each other's secrets.
- Engines grant nothing on their own: an engine annotation without a `tier` grants nothing, and a ServiceAccount with no `bao.stakater.com/*` annotation renders nothing.
- A key on the wrong object (a grant on a Deployment, a request on a ServiceAccount) is reported as an error beside the workload, not silently ignored.
- Sharing and cross-tenant trust are opt-in on **both** sides and directional — exporting grants nothing until the peer imports; trusting a peer's certificates does not accept it inbound.
- People signing in through OIDC get their tier **across the tenant**; a workload is confined to its namespace. Keep that difference in mind when granting `admin`.

## How the extension scopes Template Operator v2

The extension renders through Template Operator v2, which applies objects with its own ServiceAccount. The chart grants that account the permissions this integration needs to manage the resources it renders — the OpenBao Config Operator CRs, the per-workload ConfigMaps and the ExternalSecrets.

Keep one administrative rule: **authoring a Template Operator v2 `Template` is a privileged operation** — anyone who can create `Template`s and `TemplateInstance`s drives the operator with those permissions. MTO's tenant roles do not grant that, and it should not be granted to tenants. Template Operator v2's own security model (the operator applies with its ServiceAccount, scoped by RBAC) is the reference for how those permissions are bounded.

---

**Previous:** [Delivery and login](delivery-and-login.md) · **Next:** [Operating](operating.md)
