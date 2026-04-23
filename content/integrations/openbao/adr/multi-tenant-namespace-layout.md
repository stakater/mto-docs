# Multi-Tenant OpenBao — Model A: Namespace-Per-Tenant

Layout using OpenBao's native **namespace** feature to give each tenant
its own isolated namespace with its own mounts, policies, and auth methods.

For the alternative single-namespace-with-path-prefix model, see
[multi-tenant-path-layout.md](multi-tenant-path-layout.md).

## Model summary

- Each tenant gets its own OpenBao namespace (`team-a/`, `team-b/`, ...).
- A dedicated `shared/` namespace holds cross-tenant resources.
- Per-tenant mounts: each tenant has its own `kv/`, `transit/`, `pki/`, and
  `auth/kubernetes/` — scoped to its namespace.
- Policies are namespace-local.

**Strengths:** hard isolation, admin delegation per tenant, clean blast-radius
boundaries, no path-prefix bookkeeping.
**Weaknesses:** cross-tenant sharing requires extra machinery (multiple tokens
or the `unsafe_cross_namespace_identity` flag), operator must manage per-ns
auth mounts, some `sys/*` operations are root-only.

## Requirements

- **OpenBao 2.3.0 or newer** — namespaces shipped in 2.3.0 (June 2025).
  Current stable: 2.5.3.
- Tenant controller must be able to operate in the root namespace to create
  sub-namespaces and provision per-tenant mounts.

## Scenario

Same scenario as the path-layout doc, for direct comparison:

- **team-a** has 2 namespaces: `team-a-api`, `team-a-web`
- **team-b** has 2 namespaces: `team-b-api`, `team-b-worker`
- **team-c** has 1 namespace: `team-c-api`
- **team-a → team-b** directional share (team-a writes, team-b reads)
- **team-b → team-c** directional share
- **broadcast shared** readable by all three tenants
- **team-a ↔ team-b** mutual mTLS via a shared CA

## Full tree

```text
(root namespace)                                   ← only admins operate here
│
├── sys/                                           ← root-only: audit, seal, quotas, license
├── sys/namespaces/                                ← create/list/delete tenant namespaces
│   ├── shared
│   ├── team-a
│   ├── team-b
│   └── team-c
│
│
├─ namespace: shared/                              ← cross-tenant resources live here
│   │
│   ├── sys/policies/acl/
│   │   ├── shared-all-reader
│   │   ├── share-team-a-to-team-b-writer
│   │   ├── share-team-a-to-team-b-reader
│   │   ├── share-team-a-to-all-writer
│   │   ├── share-team-a-to-all-reader
│   │   └── ...
│   │
│   ├── kv/                                        ← KV v2 mount in shared ns
│   │   └── data/dev/
│   │       ├── all/                               ← broadcast: every tenant reads
│   │       │   ├── corp-ca-bundle
│   │       │   └── smtp-relay-password
│   │       ├── from-team-a/
│   │       │   ├── to-team-b/
│   │       │   │   └── webhook-signing-key
│   │       │   └── to-all/
│   │       │       └── team-a-public-config
│   │       └── from-team-b/
│   │           └── to-team-c/
│   │               └── metrics-push-key
│   │
│   ├── transit/                                   ← shared transit mount
│   │   └── keys/
│   │       ├── shared-all-dev
│   │       ├── from-team-a-to-team-b-dev
│   │       └── from-team-b-to-team-c-dev
│   │
│   ├── pki-shared/                                ← shared CA for mutual mTLS
│   │   ├── roles/dev
│   │   ├── issue/dev
│   │   └── cert/ca, ca_chain
│   │
│   └── identity/groups/                           ← cross-ns bridge (see Cross-namespace sharing)
│       ├── share-team-a-to-team-b-reader         (members: team-a entities; policy here)
│       ├── share-team-b-to-team-c-reader
│       └── shared-all-reader                      (members: all tenant entities)
│
│
├─ namespace: team-a/                              ← team-a's isolated tenant space
│   │
│   ├── sys/policies/acl/
│   │   ├── team-a-api-editor
│   │   ├── team-a-web-editor
│   │   └── team-a-shared-editor
│   │
│   ├── kv/                                        ← team-a's own KV mount
│   │   └── data/dev/
│   │       ├── _shared/                           ← intra-tenant (api + web)
│   │       │   ├── db-connection-string
│   │       │   └── internal-api-token
│   │       ├── team-a-api/
│   │       │   ├── stripe-secret-key
│   │       │   └── jwt-signing-key
│   │       └── team-a-web/
│   │           ├── session-cookie-key
│   │           └── recaptcha-secret
│   │
│   ├── transit/
│   │   └── keys/
│   │       ├── team-a-api-dev
│   │       ├── team-a-web-dev
│   │       └── team-a-shared-dev
│   │
│   ├── pki/                                       ← team-a's private CA
│   │   ├── roles/{team-a-api-dev, team-a-web-dev, team-a-shared-dev}
│   │   ├── issue/{team-a-api-dev, team-a-web-dev, team-a-shared-dev}
│   │   └── cert/ca, ca_chain
│   │
│   └── auth/kubernetes/                           ← team-a's own k8s auth mount
│       ├── config
│       └── role/
│           ├── team-a-api                         ← SA default@team-a-api
│           └── team-a-web
│
│
├─ namespace: team-b/
│   ├── sys/policies/acl/
│   │   ├── team-b-api-editor
│   │   ├── team-b-worker-editor
│   │   └── team-b-shared-editor
│   ├── kv/data/dev/
│   │   ├── _shared/
│   │   ├── team-b-api/
│   │   └── team-b-worker/
│   ├── transit/keys/
│   │   ├── team-b-api-dev
│   │   ├── team-b-worker-dev
│   │   └── team-b-shared-dev
│   ├── pki/
│   │   ├── roles/{team-b-api-dev, team-b-worker-dev, team-b-shared-dev}
│   │   ├── issue/...
│   │   └── cert/ca
│   └── auth/kubernetes/
│       └── role/{team-b-api, team-b-worker}
│
│
└─ namespace: team-c/
    ├── sys/policies/acl/
    │   ├── team-c-api-editor
    │   └── team-c-shared-editor
    ├── kv/data/dev/
    │   ├── _shared/
    │   └── team-c-api/
    ├── transit/keys/
    │   ├── team-c-api-dev
    │   └── team-c-shared-dev
    ├── pki/
    │   └── roles/issue/{team-c-api-dev, team-c-shared-dev}
    └── auth/kubernetes/
        └── role/team-c-api
```

## Engine count

Each tenant namespace gets its own mounts; the `shared/` namespace has its own set. For **N tenants**:

| Kind | Count | Formula |
|---|---|---|
| Secret engines (`kv` + transit + `pki` per tenant, + 3 in `shared/`) | `3N + 3` | 3 per tenant + 3 shared |
| Secret engines, KV only | `N + 1` | 1 per tenant + 1 in `shared/` |
| K8s auth mounts | `N` | 1 per tenant. The `shared/` namespace has no auth mount — cross-namespace access is realized via identity groups, not a dedicated auth method. |

Example — 3 tenants, all three engine types enabled:

```text
secret engines: 3 * 3 + 3 = 12
  (team-a/{kv,transit,pki}, team-b/{kv,transit,pki}, team-c/{kv,transit,pki},
   shared/{kv,transit,pki-shared})
auth mounts:    3
  (team-a, team-b, team-c)
```

`transit` and `pki` are opt-in per the main CRD ([openbaoextension-crd.md](./openbaoextension-crd.md)); a minimal deployment with only KV is `N + 1` secret engines.

## Addressing

Every operation inside a namespace carries the namespace either as a path
prefix or an `X-Vault-Namespace` header:

```bash
# Path-prefix form
bao kv get team-a/kv/dev/team-a-api/stripe-secret-key

curl -H "X-Vault-Token: $TOKEN" \
  https://openbao/v1/team-a/kv/data/dev/team-a-api/stripe-secret-key

# Header form (equivalent)
BAO_NAMESPACE=team-a/ bao kv get kv/dev/team-a-api/stripe-secret-key

curl -H "X-Vault-Token: $TOKEN" -H "X-Vault-Namespace: team-a/" \
  https://openbao/v1/kv/data/dev/team-a-api/stripe-secret-key
```

Because the namespace provides tenant scope, paths **no longer carry
`tenants/<tenant>/` segments** — the namespace itself is the scope.

## Policies (namespace-local)

**Key rule:** every policy lives **inside** one namespace and can only
grant access to paths **within that same namespace**. The namespace a
policy lives in is determined by which namespace it is created in
(`sys/policies/acl/<name>` inside that namespace), not by the policy's
content.

Consequences:

- Policy paths are written **relative to the namespace** — they do not
  include a namespace prefix. A policy in `team-a/` that allows access to
  KV secrets writes `path "kv/data/..."`, not `path "team-a/kv/data/..."`.
- A token issued in namespace `A` only evaluates policies attached to
  auth roles in namespace `A`. Those policies cannot grant access to
  paths in namespace `B`, even if they name `B`'s paths literally — the
  path lookup is scoped to `A`.
- To give a workload access to resources in two namespaces, you need
  either two tokens (one per namespace) or cross-namespace identity
  (see [Cross-namespace sharing](#cross-namespace-sharing)).

### Example 1 — policy inside `team-a/`

Created via `sys/policies/acl/team-a-api-editor` while the client is in
namespace `team-a/`. Grants access to KV, transit, and PKI mounts that
live inside `team-a/`:

```hcl
# team-a-api-editor — lives in namespace team-a/
path "kv/data/dev/team-a-api/*"       { capabilities = ["create","read","update"] }
path "kv/metadata/dev/team-a-api/*"   { capabilities = ["list","read"] }
path "transit/encrypt/team-a-api-dev" { capabilities = ["update"] }
path "transit/decrypt/team-a-api-dev" { capabilities = ["update"] }
path "pki/issue/team-a-api-dev"       { capabilities = ["create","update"] }
```

Attached to a k8s auth role also inside `team-a/`. A token from that
role can read `kv/data/dev/team-a-api/...` **only within `team-a/`** —
the same path inside `team-b/` or `shared/` is a separate resource and
this token cannot reach it.

### Example 2 — policy inside `shared/`

Created via `sys/policies/acl/share-team-a-to-team-b-writer` while the
client is in namespace `shared/`. Grants write access to paths that
live inside the `shared/` namespace:

```hcl
# share-team-a-to-team-b-writer — lives in namespace shared/
path "kv/data/dev/from-team-a/to-team-b/*"       { capabilities = ["create","read","update"] }
path "kv/metadata/dev/from-team-a/to-team-b/*"   { capabilities = ["list","read"] }
path "transit/encrypt/from-team-a-to-team-b-dev" { capabilities = ["update"] }
```

This policy is useless on its own — it needs to be attached to an auth
role that issues tokens operating in `shared/`. A team-a workload
authenticated into `team-a/` will not automatically get this policy; see
the next section for how to bridge that gap.

## Intra-tenant sharing

When a tenant has two or more k8s namespaces (`team-a-api` and
`team-a-web`), the operator creates a set of shared resources inside
the tenant's `bao` namespace so that both workloads can read and write
common data without any cross-namespace plumbing. All of it lives in
`team-a/`, attached to every workload role in the tenant.

### What the operator creates

Triggered when `len(tenant.spec.namespaces.*) >= 2`:

| Resource | Path | Gated by |
|---|---|---|
| KV reserved `subtree` | `team-a/kv/data/<env>/_shared/` | KV engine enabled (always) |
| Transit shared key | `team-a/transit/keys/<tenant>-shared-<env>` | `engines[name=transit].enabled=true` |
| PKI shared role | `team-a/pki/roles/<tenant>-shared-<env>` | `engines[name=pki].enabled=true` |
| Policy | `team-a/sys/policies/acl/<tenant>-shared-editor` | always (if any of the above exist) |

`_shared` is an operator-reserved path segment at the same level as
`<nsFull>` — it is **not** a k8s namespace and does not flow through
`spec.layout.templates.kv`'s `{{ .namespace }}` variable. The
controller rejects tenants whose k8s namespaces short-name to
`_shared`.

Single-namespace tenants still get the policy generated (harmless,
grants access to resources that don't exist). No separate CRD knob —
this is implicit behavior, parallel to how `_shared` is already
treated for KV.

### Policy shape (inside `team-a/`)

```hcl
# team-a-shared-editor — lives in namespace team-a/
path "kv/data/dev/_shared/*"            { capabilities = ["create","read","update"] }
path "kv/metadata/dev/_shared/*"        { capabilities = ["list","read"] }
path "transit/encrypt/team-a-shared-dev" { capabilities = ["update"] }
path "transit/decrypt/team-a-shared-dev" { capabilities = ["update"] }
path "pki/issue/team-a-shared-dev"       { capabilities = ["create","update"] }
```

Attached to **every** k8s auth role in `team-a/` (`team-a-api`,
`team-a-web`). Both workloads can read and write intra-tenant shared
resources; ownership is at the tenant level, not the workload level.

### Why both apps are writers

Intra-tenant shared data belongs to the tenant as a whole, not to any
one k8s namespace inside it. There is no "owner k8s-ns" for `_shared`,
so there is no natural way to split write from read across workloads
of the same tenant. Teams that want stricter control should use
per-k8s-ns paths (`team-a-api/`, `team-a-web/`) and grant one-way
access via tenant RBAC at the SSO layer.

## Cross-namespace sharing

The operator realizes all cross-namespace access via a single mechanism:
OpenBao identity groups with `unsafe_cross_namespace_identity=true`.
Two-token alternatives are rejected — see "Rejected alternatives" below.

### How it works

An entity authenticated in `team-a/` is made a member of an identity
group that **lives in `shared/`** and carries the `share-*-reader`
(or writer) policy. With `unsafe_cross_namespace_identity=true`, a
group in namespace X can include entities from namespace Y and still
attach policies from X. The entity's single token therefore evaluates:

- policies attached to the auth role in `team-a/` (tenant-local), and
- policies attached via its group membership in `shared/` (cross-tenant),

on every request — so tenant-local and shared access use one login
and one token.

The operator creates one identity group in `shared/` per
`OpenBaoShare` it admits; the group carries the share's policy and its
member list is the union of entities authenticated in the reader
tenants' `bao` namespaces.

Enabled per-cluster via `OpenBao.spec.sharing.allowCrossNamespaceIdentity=true`.
Without that flag set, the operator rejects every `OpenBaoShare` with
`Ready=False, reason=CrossNamespaceIdentityDisabled`.

### Known risks

OpenBao labels this feature "**unsafe**" because it weakens the
isolation that namespaces are designed to provide.

- Tracking: [GH-1432](https://github.com/openbao/openbao/issues/1432),
  [GH-2321](https://github.com/openbao/openbao/issues/2321)
- A CVE ([CVE-2026-40264](https://github.com/openbao/openbao/security))
  landed on cross-namespace token renewal — the subsystem has had real
  isolation bugs.

The `allowCrossNamespaceIdentity` flag exists so enabling this is an
explicit, auditable decision.

### Rejected alternatives

- **Two logins.** Workload authenticates separately to `team-a/` and
  `shared/`, gets two tokens, selects per call. Doubles auth overhead
  and complicates every SDK, agent, and CSI integration.
- **Shared auth mount in `shared/`.** Workloads authenticate into
  `shared/` via a dedicated k8s-auth mount. Same outcome as two logins:
  two tokens per workload.

Both are strictly worse than the identity-group path for the same
isolation outcome — an attacker who can abuse cross-namespace policies
can abuse them under two-token just as readily, they just need to
compromise one of the two tokens.

## System-path restrictions

A number of `sys/*` endpoints are root-namespace-only and **cannot** be used
inside a tenant namespace. From the OpenBao docs:

- audit, seal, `rekey`, quotas, replication, generate-root, license, and others

Practical consequences:

- Audit config is global (one audit sink for the whole cluster).
- Seal/unseal is global.
- Per-tenant quota enforcement at the namespace level is supported;
  cluster-wide quotas are root-only.

See the full list:
<https://openbao.org/docs/concepts/namespaces/>

## KV v2 capability semantics

KV v2 splits delete into four distinct operations. When the design enables
tenant delete rights (the CRD `spec.safety.allowDeletes` gate), the policy
must grant the specific operation, not just add `delete` on `data/*`.

| Operation | Path | Capability |
|---|---|---|
| Soft-delete latest version | `kv/data/<path>` | `delete` |
| Soft-delete specific versions | `kv/delete/<path>` | `update` |
| `Undelete` versions | `kv/undelete/<path>` | `update` |
| Permanent destroy specific versions | `kv/destroy/<path>` | `update` |
| Permanent destroy all versions + metadata | `kv/metadata/<path>` | `delete` |

**Note:** `list` capability only works on `kv/metadata/<path>`, **not** on
`kv/data/<path>`. Stanzas in this doc omit `list` from `data/*` for this
reason.

Source: <https://openbao.org/docs/secrets/kv/kv-v2/>

## PKI CA endpoints are unauthenticated

In every `pki/` and `pki-<tenant>/` mount (inside any namespace), these
endpoints are on OpenBao's unauthenticated-paths list and do **not**
require a policy grant:

- `pki/cert/ca`
- `pki/ca/pem`
- `pki/ca_chain`
- `pki/crl`, `pki/crl/pem`

Any client can fetch CA bundles and CRLs without a token. Do not add
policies that grant `read` on these paths — they are redundant. Cross-
namespace CA trust (e.g. team-a verifying certs issued by team-b's CA)
works out of the box: the verifying client fetches
`team-b/pki/cert/ca` unauthenticated, just like any TLS trust bundle.

`pki/crl/rotate` and issuer-management endpoints remain authenticated and
require a policy grant.

## Reserved names

These names are reserved for the layout and **must not collide with
tenant-generated names**:

| Name | Purpose |
|---|---|
| `shared` | OpenBao namespace for cross-tenant resources |
| `_shared` (under `<ns>/kv/data/<env>/`) | Intra-tenant shared KV path |
| `all` (under `shared/kv/data/<env>/`) | Broadcast read tree |
| `from-<tenant>` / `to-<tenant>` (under `shared/kv/data/<env>/`) | Directional shares |

Additionally, OpenBao itself reserves the following namespace names and
will reject them at creation: `.`, `..`, `root`, `sys`, `audit`, `auth`,
`cubbyhole`, `identity`.

The controller must reject tenant names that collide with reserved values,
and must reject `nsFull` values that would collide with `_shared`, `all`,
`from-*`, or `to-*`. K8s namespace names follow RFC 1123 (no underscores),
so `_shared` is safe against real K8s namespaces, but `all`, `from-x`,
`to-x` are valid K8s names and need explicit guard-rails.

Source: <https://openbao.org/docs/concepts/namespaces/>

## Naming conventions

| Pattern | Meaning |
|---|---|
| `team-a/` | OpenBao namespace for tenant `team-a` |
| `shared/` | OpenBao namespace for cross-tenant resources |
| `<ns>/kv/data/dev/<nsFull>/` | Private per-K8s-namespace path |
| `<ns>/kv/data/dev/_shared/` | Shared across K8s namespaces of one tenant |
| `shared/kv/data/dev/all/` | Readable by every tenant |
| `shared/kv/data/dev/from-<W>/to-<R>/` | Directional cross-tenant share |
| `<nsFull>-<env>` | Per-k8s-ns transit key / PKI role (namespace-local) |
| `<tenant>-shared-<env>` | Intra-tenant shared transit key / PKI role |
| `shared-all-<env>` | Broadcast transit key (in `shared/`) |
| `from-<W>-to-<R>-<env>` | Directional cross-tenant transit key (in `shared/`) |

### Auth role naming

Roles live inside the tenant's `bao` namespace, so the `bao` path already
carries the tenant scope. The role name itself is the k8s namespace
name as declared in `Tenant.spec.namespaces.*` (`<nsFull>` per
[internal/utils/namespace_util.go](../../internal/utils/namespace_util.go)):

| Auth role path | Example (withTenantPrefix) | Example (withoutTenantPrefix) |
|---|---|---|
| `<ns>/auth/kubernetes/role/<nsFull>` | `team-a/auth/kubernetes/role/team-a-api` | `team-a/auth/kubernetes/role/api` |

The tenant prefix appears in the role name only because it's part of
the k8s namespace name — not because the role needs to disambiguate
across tenants (the `bao` namespace does that).

Contrast with Model B, where the flat auth mount forces
`<tenant>-<nsFull>` to disambiguate (`team-a-team-a-api`).

## Operator changes required (`mto-extension-openbao`)

Today the controller ([tenant_controller.go](../../internal/controller/tenant/tenant_controller.go))
assumes a single root namespace — it talks to `secret/` (KV) and
`auth/kubernetes/` at root.

Moving to Model A requires the controller to:

1. Create an OpenBao namespace per Tenant via `sys/namespaces/<tenant>`.
2. Mount KV, transit, PKI **inside** each tenant namespace.
3. Enable `auth/kubernetes` inside each tenant namespace with its own k8s
   config.
4. Write per-namespace policies.
5. Reconcile the `shared/` namespace for cross-tenant grants as a separate
   step.
6. Handle cross-namespace token requests — every `Bao` client call must carry
   the correct `X-Vault-Namespace` header.

This is a substantive change, not a path rewrite. The CRD's
`spec.tenancyMode: namespace` field (`scaffolded` per
[CLAUDE.md](../../CLAUDE.md)) is where this plugs in.

## When to choose Model A vs Model B

| Criterion | Model A (namespace-per-tenant) | Model B (path-per-tenant) |
|---|---|---|
| Isolation | Hard boundary per namespace | Path-glob enforcement only |
| Admin delegation | Per-tenant admins possible | Central admin only |
| Cross-tenant sharing | Two tokens or `unsafe_cross_namespace_identity` | First-class, single policy attach |
| Operator complexity | High — per-ns mounts and auth | Low — single mount set |
| Blast radius on misconfig | Contained to one namespace | Whole tenancy tree |
| Minimum OpenBao version | 2.3.0 | Any |
| Matches regulatory multi-tenancy | ✅ | Weaker |

**Pick Model A** when isolation is a hard requirement (compliance, multi-customer SaaS, distinct tenant admins).

**Pick Model B** when sharing is frequent, central admin is fine, and operator simplicity matters more than strict isolation.

## References

- OpenBao namespaces concept: <https://openbao.org/docs/concepts/namespaces/>
- `bao namespace` CLI: <https://openbao.org/docs/commands/namespace/>
- `sys/namespaces` API: <https://openbao.org/api-docs/system/namespaces/>
- Landing PR: <https://github.com/openbao/openbao/pull/1165>
- CHANGELOG 2.3.0 entry:
  <https://github.com/openbao/openbao/blob/main/CHANGELOG.md>
