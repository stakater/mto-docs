# Multi-Tenant OpenBao — Model B: Path-Per-Tenant

Path, policy, and sharing layout for multi-tenant OpenBao across KV v2, Transit, and PKI engines, using a **single OpenBao namespace** and separating tenants by path prefix.

For the alternative isolated-namespace-per-tenant model, see [multi-tenant-namespace-layout.md](multi-tenant-namespace-layout.md).

## Model summary

- Single root OpenBao namespace for everything.
- Tenants separated by path prefix: `tenants/<tenant>/<env>/<nsFull>/...`.
- One KV mount, one transit mount, per-tenant PKI mounts.
- One Kubernetes auth mount with per-namespace roles.
- Cross-tenant sharing is first-class via dedicated `shared/` paths.

**Strengths:** simple, central management, ergonomic sharing.
**Weaknesses:** weaker isolation — all tenants share the same mounts, policies are enforced by path `globbing` rather than hard namespace boundaries.

## Scenario

- **team-a** has 2 namespaces: `team-a-api`, `team-a-web`
- **team-b** has 2 namespaces: `team-b-api`, `team-b-worker`
- **team-c** has 1 namespace: `team-c-api`
- **team-a → team-b** directional share (team-a writes, team-b reads)
- **team-b → team-c** directional share
- **broadcast shared** readable by all three tenants
- **team-a ↔ team-b** mutual mTLS via a shared CA

## Full tree

```
openbao/                                                           ← OpenBao namespace
│
├── kv/                                                            ← KV v2 mount
│   │
│   ├── config                                                     (mount config)
│   │
│   └── data/
│       │
│       ├── tenants/
│       │   │
│       │   ├── team-a/
│       │   │   └── dev/
│       │   │       │
│       │   │       ├── _shared/                                   ← intra-tenant (api + web)
│       │   │       │   ├── db-connection-string
│       │   │       │   └── internal-api-token
│       │   │       │
│       │   │       ├── team-a-api/                                ← private to team-a-api
│       │   │       │   ├── stripe-secret-key
│       │   │       │   ├── jwt-signing-key
│       │   │       │   └── redis-password
│       │   │       │
│       │   │       └── team-a-web/                                ← private to team-a-web
│       │   │           ├── session-cookie-key
│       │   │           └── recaptcha-secret
│       │   │
│       │   ├── team-b/
│       │   │   └── dev/
│       │   │       ├── _shared/
│       │   │       │   └── kafka-sasl-password
│       │   │       ├── team-b-api/
│       │   │       │   ├── postgres-password
│       │   │       │   └── oauth-client-secret
│       │   │       └── team-b-worker/
│       │   │           ├── rabbitmq-password
│       │   │           └── s3-access-key
│       │   │
│       │   └── team-c/
│       │       └── dev/
│       │           ├── _shared/
│       │           │   └── datadog-api-key
│       │           └── team-c-api/
│       │               ├── github-webhook-secret
│       │               └── slack-bot-token
│       │
│       └── shared/
│           └── dev/
│               │
│               ├── all/                                           ← broadcast: every tenant reads
│               │   ├── corp-ca-bundle
│               │   ├── smtp-relay-password
│               │   └── artifactory-read-token
│               │
│               ├── from-team-a/
│               │   └── to-team-b/                                 ← team-a writes, team-b reads
│               │       ├── webhook-signing-key
│               │       └── event-bus-token
│               │
│               └── from-team-b/
│                   └── to-team-c/                                 ← team-b writes, team-c reads
│                       └── metrics-push-key
│
├── transit/                                                       ← Transit mount
│   │
│   ├── config/keys                                                (mount config)
│   │
│   └── keys/
│       │
│       ├── team-a-api-dev                                         ← private to team-a-api
│       ├── team-a-web-dev                                         ← private to team-a-web
│       ├── team-a-shared-dev                                      ← intra-tenant (team-a ns)
│       │
│       ├── team-b-api-dev
│       ├── team-b-worker-dev
│       ├── team-b-shared-dev
│       │
│       ├── team-c-api-dev
│       ├── team-c-shared-dev
│       │
│       ├── shared-all-dev                                         ← broadcast encrypt+decrypt
│       │
│       ├── from-team-a-to-team-b-dev                              ← team-a encrypts, team-b decrypts
│       └── from-team-b-to-team-c-dev
│
│   (operations per key — not separate paths, just endpoints:)
│   transit/encrypt/<key>
│   transit/decrypt/<key>
│   transit/sign/<key>          (asymmetric keys only)
│   transit/verify/<key>
│   transit/rewrap/<key>
│   transit/datakey/plaintext/<key>
│
├── pki-team-a/                                                    ← team-a's private CA
│   ├── config/ca, config/urls, config/crl
│   ├── root/generate/internal                                     (one-time, CA bootstrap)
│   ├── roles/
│   │   ├── team-a-api-dev
│   │   ├── team-a-web-dev
│   │   └── team-a-shared-dev                                      ← intra-tenant role
│   ├── issue/team-a-api-dev                                       ← call to issue cert
│   ├── issue/team-a-web-dev
│   ├── issue/team-a-shared-dev
│   ├── sign/<role>, sign-verbatim/<role>
│   ├── cert/ca                                                    ← unauthenticated read (CA bundle)
│   ├── ca_chain                                                   ← unauthenticated read
│   └── crl, crl/rotate                                            ← crl unauthenticated; rotate = admin
│
├── pki-team-b/                                                    ← team-b's private CA
│   ├── roles/{team-b-api-dev, team-b-worker-dev, team-b-shared-dev}
│   ├── issue/{team-b-api-dev, team-b-worker-dev, team-b-shared-dev}
│   ├── cert/ca                                                    ← unauthenticated read
│   └── ca_chain
│
├── pki-team-c/
│   ├── roles/{team-c-api-dev, team-c-shared-dev}
│   ├── issue/{team-c-api-dev, team-c-shared-dev}
│   ├── cert/ca
│   └── ca_chain
│
├── pki-shared/                                                    ← shared CA for cross-tenant mTLS
│   ├── roles/dev                                                  (broad role, all tenants issue)
│   ├── issue/dev
│   ├── cert/ca
│   └── ca_chain
│
└── auth/
    └── kubernetes/                                                (auth mount — see CLAUDE.md)
        ├── config
        └── role/
            ├── team-a-team-a-api                                  ← SA default@team-a-api → policies
            ├── team-a-team-a-web
            ├── team-b-team-b-api
            ├── team-b-team-b-worker
            └── team-c-team-c-api
```

## Engine count

KV and transit are singletons; PKI cannot share a mount, so there is one per tenant plus the shared CA. For **N tenants**:

| Kind | Count | Formula |
|---|---|---|
| Secret engines (`kv` + transit + per-tenant `pki` + pki-shared) | `N + 3` | 1 `kv` + 1 transit + N pki-`<tenant>` + 1 pki-shared |
| Secret engines, KV only | `1` | single `kv` mount, regardless of tenant count |
| K8s auth mounts | `1` | single mount, per-tenant roles inside |

Example — 3 tenants, all three engine types enabled:

```text
secret engines: 3 + 3 = 6
  (kv, transit, pki-team-a, pki-team-b, pki-team-c, pki-shared)
auth mounts:    1
  (auth/kubernetes with roles team-a-*, team-b-*, team-c-*)
```

`transit` and `pki` are opt-in per the main CRD ([openbaoextension-crd.md](./openbaoextension-crd.md)); a minimal KV-only deployment is a single secret engine regardless of tenant count.

## Addressing

All resources live in the **root namespace**, so clients need no namespace
header or prefix. Paths start directly from the mount:

```bash
# KV v2 — read a tenant-local secret
bao kv get kv/dev/tenants/team-a/dev/team-a-api/stripe-secret-key

curl -H "X-Vault-Token: $TOKEN" \
  https://openbao/v1/kv/data/tenants/team-a/dev/team-a-api/stripe-secret-key

# KV v2 — read a cross-tenant shared secret
bao kv get kv/shared/dev/from-team-a/to-team-b/webhook-signing-key

# Transit — encrypt with a per-namespace key
curl -H "X-Vault-Token: $TOKEN" \
  -d '{"plaintext":"aGVsbG8="}' \
  https://openbao/v1/transit/encrypt/team-a-api-dev

# PKI — issue a cert under the tenant's CA
curl -H "X-Vault-Token: $TOKEN" \
  -d '{"common_name":"api.team-a.svc"}' \
  https://openbao/v1/pki-team-a/issue/team-a-api-dev
```

Tenant identity is carried in the **path**, not the namespace header. Access
control is enforced by matching the path against the policies attached to
the token's auth role (e.g. `team-a-team-a-api` role → policies that glob
`kv/data/tenants/team-a/dev/team-a-api/*`).

Workloads use one token to reach both tenant-local and shared resources —
the same policy set covers both.

## Policy inventory

One policy per `(tenant, namespace)` plus a few cross-cutting ones.

```
sys/policies/acl/
│
├── team-a-team-a-api-editor           ← attached to role team-a-team-a-api
├── team-a-team-a-web-editor
├── team-b-team-b-api-editor
├── team-b-team-b-worker-editor
├── team-c-team-c-api-editor
│
├── team-a-shared-editor               ← intra-tenant stanza, attached to both team-a roles
├── team-b-shared-editor
├── team-c-shared-editor
│
├── shared-all-reader                  ← attached to every tenant role
│
├── share-team-a-to-team-b-writer      ← attached to team-a roles
├── share-team-a-to-team-b-reader      ← attached to team-b roles
├── share-team-b-to-team-c-writer      ← attached to team-b roles
├── share-team-b-to-team-c-reader      ← attached to team-c roles
│
└── pki-shared-issuer                  ← attached to team-a + team-b roles (mutual mTLS)

(No pki-trust-* policies: pki/cert/ca and pki/ca_chain are on OpenBao's
 unauthenticated-paths list, so CA bundles are fetched without a token.)
```

## Example: full policy set attached to `team-a-team-a-api` role

Role `auth/kubernetes/role/team-a-team-a-api` has `token_policies`:

```
team-a-team-a-api-editor
team-a-shared-editor
shared-all-reader
share-team-a-to-team-b-writer
pki-shared-issuer
```

### `team-a-team-a-api-editor`

```hcl
path "kv/data/tenants/team-a/dev/team-a-api/*"     { capabilities = ["create","read","update"] }
path "kv/metadata/tenants/team-a/dev/team-a-api/*" { capabilities = ["list","read"] }
path "transit/encrypt/team-a-api-dev"              { capabilities = ["update"] }
path "transit/decrypt/team-a-api-dev"              { capabilities = ["update"] }
path "pki-team-a/issue/team-a-api-dev"             { capabilities = ["create","update"] }
```

### `team-a-shared-editor`

Intra-tenant shared resources. See [Intra-tenant sharing](#intra-tenant-sharing) below for when and how the operator creates the key/role this policy grants access to.

```hcl
path "kv/data/tenants/team-a/dev/_shared/*"        { capabilities = ["create","read","update"] }
path "kv/metadata/tenants/team-a/dev/_shared/*"    { capabilities = ["list","read"] }
path "transit/encrypt/team-a-shared-dev"           { capabilities = ["update"] }
path "transit/decrypt/team-a-shared-dev"           { capabilities = ["update"] }
path "pki-team-a/issue/team-a-shared-dev"          { capabilities = ["create","update"] }
```

### `shared-all-reader`

```hcl
path "kv/data/shared/dev/all/*"                    { capabilities = ["read"] }
path "kv/metadata/shared/dev/all/*"                { capabilities = ["list","read"] }
path "transit/encrypt/shared-all-dev"              { capabilities = ["update"] }
path "transit/decrypt/shared-all-dev"              { capabilities = ["update"] }
```

### `share-team-a-to-team-b-writer`

```hcl
path "kv/data/shared/dev/from-team-a/to-team-b/*"     { capabilities = ["create","read","update"] }
path "kv/metadata/shared/dev/from-team-a/to-team-b/*" { capabilities = ["list","read"] }
path "transit/encrypt/from-team-a-to-team-b-dev"      { capabilities = ["update"] }
```

### `pki-shared-issuer`

```hcl
path "pki-shared/issue/dev" { capabilities = ["create","update"] }
```

> **Note:** `pki-shared/cert/ca` and `pki-shared/ca_chain` are on OpenBao's
> unauthenticated-paths list and do **not** require a policy grant. Any
> client can fetch CA bundles and CRLs without a token. No `pki-trust-*`
> policies are needed for cross-tenant trust — readers simply fetch the
> other tenant's `pki-<tenant>/cert/ca` directly.

## Mirror policies

### `share-team-a-to-team-b-reader` (attached to team-b roles)

```hcl
path "kv/data/shared/dev/from-team-a/to-team-b/*"     { capabilities = ["read"] }
path "kv/metadata/shared/dev/from-team-a/to-team-b/*" { capabilities = ["list","read"] }
path "transit/decrypt/from-team-a-to-team-b-dev"      { capabilities = ["update"] }
```

## Intra-tenant sharing

When a tenant has two or more k8s namespaces (`team-a-api` and `team-a-web`), the operator creates a set of shared resources so both workloads can read and write common data. Everything lives inside the per-tenant path prefix; no cross-tenant paths are involved.

### What the operator creates

Triggered when `len(tenant.spec.namespaces.*) >= 2`:

| Resource | Path | Gated by |
|---|---|---|
| KV reserved `subtree` | `kv/data/tenants/<tenant>/<env>/_shared/` | KV engine enabled (always) |
| Transit shared key | `transit/keys/<tenant>-shared-<env>` | `engines[name=transit].enabled=true` |
| PKI shared role | `pki-<tenant>/roles/<tenant>-shared-<env>` | `engines[name=pki].enabled=true` |
| Policy | `sys/policies/acl/<tenant>-shared-editor` | always (if any of the above exist) |

`_shared` is an operator-reserved path segment at the same level as `<nsFull>` under `tenants/<tenant>/<env>/`. It is **not** a k8s namespace and does not flow through `spec.layout.templates.kv`'s `{{ .namespace }}` variable. The controller rejects tenants whose k8s namespaces short-name to `_shared`.

Single-namespace tenants still get the policy generated (harmless, grants access to resources that don't exist). No separate CRD knob — implicit behavior parallel to how `_shared` is already treated for KV.

### Policy shape

Already shown above in the [Example full policy set](#example-full-policy-set-attached-to-team-a-team-a-api-role). Attached to **every** k8s auth role of the tenant (`team-a-team-a-api`, `team-a-team-a-web`). Both workloads can read and write intra-tenant shared resources; ownership is at the tenant level, not the workload level.

### Why both apps are writers

Intra-tenant shared data belongs to the tenant as a whole, not to any one k8s namespace inside it. There is no "owner k8s-ns" for `_shared`, so there is no natural way to split write from read across workloads of the same tenant. Teams that want stricter control should use per-k8s-ns paths (`team-a-api/`, `team-a-web/`) and grant one-way access via tenant RBAC at the SSO layer.

## Auth role naming

The k8s auth mount is a single global mount shared across every tenant, so role names must carry the tenant prefix to disambiguate:

| Auth role path | Example (withTenantPrefix) | Example (withoutTenantPrefix) |
|---|---|---|
| `auth/kubernetes/role/<tenant>-<nsFull>` | `auth/kubernetes/role/team-a-team-a-api` | `auth/kubernetes/role/team-a-api` |

`<nsFull>` is the k8s namespace name as declared in `Tenant.spec.namespaces.*` (per [internal/utils/namespace_util.go](../../internal/utils/namespace_util.go)). The `<tenant>-<nsFull>` doubling happens only when the k8s namespace name already includes the tenant prefix; the role name itself is just tenant + `nsFull` joined by `-`.

Contrast with Model A, where the `bao` namespace scopes the auth mount and the role name is just `<nsFull>`.

## Access matrix

| Resource | team-a-api | team-a-web | team-b-api | team-b-worker | team-c-api |
|---|---|---|---|---|---|
| `kv/.../team-a-api/*` | `rw` | — | — | — | — |
| `kv/.../team-a/_shared/*` | `rw` | `rw` | — | — | — |
| `kv/.../shared/all/*` | r | r | r | r | r |
| `kv/.../from-team-a/to-team-b/*` | `rw` | `rw` | r | r | — |
| `kv/.../from-team-b/to-team-c/*` | — | — | `rw` | `rw` | r |
| `transit/encrypt/team-a-api-dev` | ✅ | — | — | — | — |
| `transit/encrypt/from-team-a-to-team-b-dev` | ✅ | ✅ | — | — | — |
| `transit/decrypt/from-team-a-to-team-b-dev` | — | — | ✅ | ✅ | — |
| `pki-team-a/issue/...` | ✅ (own role) | ✅ (own role) | — | — | — |
| `pki-shared/issue/dev` | ✅ | ✅ | ✅ | ✅ | — |

> `pki-<x>/cert/ca` and `pki-<x>/ca_chain` are unauthenticated — every
> tenant (and any other client) can fetch them without a policy grant.

## Naming conventions

| Pattern | Meaning |
|---|---|
| `tenants/<tenant>/<env>/<nsFull>/` | Private to one K8s namespace |
| `tenants/<tenant>/<env>/_shared/` | Shared across namespaces of one tenant |
| `shared/<env>/all/` | Readable by every tenant |
| `shared/<env>/from-<W>/to-<R>/` | Directional: W writes, R reads |
| `<tenant>-<nsFull>-<env>` (transit key / `pki` role) | Per-namespace resource |
| `<tenant>-shared-<env>` | Per-tenant intra-tenant resource |
| `shared-all-<env>` | Broadcast resource |
| `from-<W>-to-<R>-<env>` | Directional cross-tenant resource |
| `pki-<tenant>/` | Per-tenant CA mount |
| `pki-shared/` | Shared CA mount for mutual mTLS |

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
`kv/data/<path>`. Stanzas above omit `list` from `data/*` for this reason.

Source: <https://openbao.org/docs/secrets/kv/kv-v2/>

## Reserved path segments

These segments are reserved for the layout and **must not collide with
tenant-generated names**:

| Segment | Purpose |
|---|---|
| `tenants/` | Top-level partition for tenant-owned data |
| `shared/` | Top-level partition for cross-tenant data |
| `_shared` (under `tenants/<tenant>/<env>/`) | Intra-tenant shared path |
| `all` (under `shared/<env>/`) | Broadcast read tree |
| `from-<tenant>` / `to-<tenant>` (under `shared/<env>/`) | Directional shares |

The controller must reject any `nsFull` value that would collide with
`_shared`, `all`, `from-*`, or `to-*`. K8s namespace names follow RFC 1123
(no underscores), so `_shared` is safe against real K8s namespaces, but
`all`, `from-x`, `to-x` are valid K8s names and need explicit guard-rails
in the controller.

## Engine-specific sharing mechanics

| Aspect | KV | Transit | PKI |
|---|---|---|---|
| What's shared | Path data | Operation on a named key | Issuance role + CA trust |
| Symmetric vs asymmetric | Symmetric only (read/write) | Asymmetric possible (encrypt-only / decrypt-only / sign-only) | Asymmetric by design (issuer vs verifier) |
| "Read" equivalent | `read` on `data/*` | `update` on `decrypt/<name>` | `read` on `cert/ca` (to verify) |
| "Write" equivalent | `create/update` on `data/*` | `update` on `encrypt/<name>` | `create/update` on `issue/<role>` |
| Naming convention reuse | `from-X/to-Y/` as path | `from-X-to-Y` as key name | `pki-shared` mount, or `cert/ca` reads across mounts |
