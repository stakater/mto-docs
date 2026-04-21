# ADR-0001: Tenancy model and Tenant → OpenBao namespace mapping

- **Status:** Accepted
- **Date:** 2026-04-21
- **Decision:** Default `namespace` mode with 1 Tenant = 1 OpenBao namespace; `path` mode available as an opt-in.

## Context

The operator provisions OpenBao resources for each MTO `Tenant`. A Tenant has one or more Kubernetes namespaces. Two design questions need answers.

**Q1. How is tenant isolation modelled on the OpenBao side?** Two candidates:

- **Path-prefix (current implementation)** — one global KV mount `secret/` and one global `kubernetes/` auth mount. Every tenant's data is separated by path segments (`secret/data/tenants/<tenant>/<env>/<ns>/*`) and by naming conventions on policies/roles (`<tenant>-<ns>-editor`).
- **OpenBao namespace per tenant** — each tenant gets its own `sys/namespaces/<tenant>/`, containing its own KV mount, k8s auth backend, policies, and roles. Clients set the `X-Vault-Namespace` header.

**Q2. Given namespace mode, what is the Tenant → OpenBao namespace mapping?** Two candidates:

- **1 Tenant = 1 OpenBao namespace** — the tenant's OpenBao namespace holds all of the tenant's k8s namespaces as paths and Kubernetes-auth roles inside it.
- **1 k8s namespace = 1 OpenBao namespace** — M OpenBao namespaces per Tenant, one per k8s namespace.

## Decision

1. **Q1 → Default `namespace` mode.** Each Tenant is isolated via its own OpenBao namespace under the default. `path` mode remains available as an opt-in (`spec.tenancy.mode: path`) for deployments that need it — see Opt-in modes below.
1. **Q2 → 1 Tenant = 1 OpenBao namespace.** Per-k8s-namespace separation stays as policies and Kubernetes-auth roles inside the tenant's OpenBao namespace. The M-ns-per-tenant alternative is rejected.

## Rationale

### Q1: Why `namespace` over `path`

| Aspect | `path` | `namespace` |
|---|---|---|
| Isolation | Soft — ACL path rules | Hard — cross-namespace access returns 404 (structural, not ACL-gated) |
| Blast radius of a policy typo | Cross-tenant read possible | Structurally impossible |
| Tenant-scoped admin tokens | No | Yes |
| Policy / role naming | Must encode tenant in name | Short names, re-usable |
| Client config | Full path, no header | `X-Vault-Namespace` header required |
| Marginal bootstrap cost per tenant | 0 new calls (reuses global mounts) | 4 one-time API calls |
| Operational familiarity | Vault-OSS idiomatic | OpenBao-native (equivalent to Vault Enterprise namespaces) |

The structural-isolation row is load-bearing: a secrets platform cannot rely on ACL correctness as its only tenant boundary. The namespace-mode costs (4 bootstrap calls per tenant, namespace-header plumbing in clients) are one-time or mechanical; the path-mode isolation weakness is a standing risk that grows with every policy edit.

### Q2: Why 1 Tenant = 1 OpenBao namespace (not 1-per-k8s-ns)

| Aspect | 1 Tenant = 1 OpenBao ns | 1 k8s-ns = 1 OpenBao ns |
|---|---|---|
| Trust-boundary alignment | Matches MTO's Tenant | Splits one team across many OpenBao namespaces |
| Bootstrap cost per tenant | 4 API calls | 4 × M calls (M = k8s-ns per tenant) |
| k8s-ns rename/move | Policy & role rename inside tenant ns | Destructive OpenBao-ns migration |
| Same-tenant cross-ns sharing | One policy attached to multiple roles | Requires cross-namespace plumbing |
| Isolation gain between same-tenant workloads | N/A (same team) | None — same team, same policies |

MTO's trust boundary is the Tenant. All k8s namespaces under a single Tenant share the same team and policies, so splitting them into M OpenBao namespaces buys no isolation but couples two independent lifecycles (k8s-ns rename ⇒ OpenBao-ns migration) and multiplies bootstrap cost M×.

## Consequences

Beyond the tradeoffs already captured in Rationale, picking `namespace` mode brings the following gains and costs into effect:

### Gains

- **Audit log segmentation.** Every audit entry carries the namespace, so per-tenant audit review is a filter (`namespace=acme/`) rather than grepping request paths.
- **Identity scoped per tenant.** Entities, groups, and aliases live inside the tenant's namespace. IdP group → policy mappings for SSO can use un-prefixed group names and are owned per tenant.
- **Per-tenant mount tuning.** `sys/mounts/<path>/tune` (e.g., `default_lease_ttl`, `max_lease_ttl`, audit-exempt paths) scopes to the tenant's mount, verified against OpenBao v2.5.2.

### Costs

- **Per-tenant k8s-auth config.** Each tenant namespace needs its own `auth/kubernetes/config` write, even though the values (`kubernetes_host`, `kubernetes_ca_cert`, token-reviewer JWT) are identical across all tenants in one cluster. Cost: N config writes at bootstrap and N objects to keep in sync on CA rotation or JWT refresh.
- **Clients must set `X-Vault-Namespace`.** VSO, OpenBao Agent, CSI driver integrations gain a namespace-header requirement.
- **Cascade delete.** Deleting an OpenBao namespace removes all its mounts, policies, and data. The operator respects `spec.safety.allowDeletes` as the safety gate.

## Opt-in modes

### Path-prefix (`spec.tenancy.mode: path`)

Path-prefix mode offers no structural protection against cross-tenant policy bugs — tenant isolation depends entirely on ACL correctness, and a malformed path rule (e.g., `path "secret/data/tenants/*"`) leaks across tenants with no secondary boundary. That isolation weakness is why `namespace` is the default.

It remains available for deployments where:

- Operators are Vault-OSS-idiomatic and want the familiar single-mount model.
- Debugging and observability benefit from a single global mount, auth method, and audit stream (no namespace context to set).
- Cross-tenant aggregation policies are needed (e.g., a central observability or backup service reading from every tenant) — trivial in path mode as a single policy, non-trivial in namespace mode (requires a root-ns entity with cross-namespace policies).

## Rejected alternatives

### 1 Tenant = M OpenBao namespaces (one per k8s namespace)

Example: `acme/app1/`, `acme/app2/`, `globex/app1/`. Rejected because:

- MTO treats the Tenant as the trust boundary, not the k8s ns.
- 5× bootstrap cost for no isolation gain between same-team workloads.
- Couples k8s-ns rename/move to OpenBao-ns migration — messy.
