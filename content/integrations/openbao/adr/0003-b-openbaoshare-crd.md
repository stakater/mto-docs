# ADR-0003-b: OpenBaoShare CRD Design

- **Status:** Draft
- **Date:** 2026-04-23
- **Scope:** Schema of `security.tenantoperator.stakater.com/v1alpha1, Kind=OpenBaoShare`
- **Companion to:** [ADR-0003-a: OpenBao CRD](./0003-a-openbao-crd.md)
- **Grounded in:** [Model A — namespace layout](./multi-tenant-namespace-layout.md), [Model B — path layout](./multi-tenant-path-layout.md)

The `OpenBao` CRD defines the per-tenant isolation model. `OpenBaoShare` is the **only** way to open a gap in that isolation — a tenant (or the platform) declares it wants to share a resource with one or more other tenants, and the operator realizes that share in whichever model (A or B) the cluster is running.

## Why a separate CRD

| CRD | Owner | Purpose |
|---|---|---|
| `OpenBao` | Platform team | Cluster-wide config: server, tenancy mode, engines, default policies. One per cluster. |
| `OpenBaoShare` | Writer tenant team | Declares a single share: `from` tenant writes, `to` tenants read. Many per cluster. |

Keeping them separate means:

- Writer teams self-service shares without editing the platform CR.
- Platform RBAC on `OpenBao` stays tight; `OpenBaoShare` RBAC is per-tenant-namespace (Kubernetes RBAC gates which team can create a `OpenBaoShare` in which namespace).
- Share churn (new consumers, revocations, rotations) is independent of engine definitions.

Pile-up is prevented by one rule: `from.tenant` must match the tenant that owns the CR's k8s namespace. A team can only share **its own** data.

## Sharing patterns (from the layout docs)

The two layout docs define four concrete patterns. `OpenBaoShare` models all four:

| Pattern | Layout convention (Model B path) | Layout convention (Model A namespace) | `OpenBaoShare` shape |
|---|---|---|---|
| Directional KV | `shared/<env>/from-<W>/to-<R>/*` | `shared/kv/data/<env>/from-<W>/to-<R>/*` | `from.tenant: W`, `to.tenants: [R]`, `kv: {...}` |
| Broadcast KV | `shared/<env>/all/*` | `shared/kv/data/<env>/all/*` | `from.tenant: platform`, `to.mode: all`, `kv: {...}` |
| Directional Transit | key `from-<W>-to-<R>-<env>` | key `from-<W>-to-<R>-<env>` in `shared/transit/` | `from.tenant: W`, `to.tenants: [R]`, `transit: {...}` |
| Shared CA (mutual mTLS) | mount `pki-shared/` | mount `pki-shared/` in `shared/` `ns` | `from.tenant: platform`, `to.tenants: [W, R]`, `pki: {...}` |

The operator picks the right realization based on the `OpenBao` CR's `tenancy.mode`. The `OpenBaoShare` spec itself is mode-agnostic.

---

## Shape

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBaoShare
metadata:
  name: <share-name>
  namespace: <writer-tenant-k8s-ns>
spec:
  openBaoRef:                        # optional when a single OpenBao CR exists
    name: cluster-default
    namespace: mto-system
  engineRef: kv                      # name of engine in OpenBao.spec.engines

  from:
    tenant: <writer>

  to:
    mode: tenants                    # tenants | all
    tenants: [<reader-1>, <reader-2>]         # required when mode=tenants

  # Exactly ONE of kv / transit / pki, matching the referenced engine's type.

  kv:
    keys: [<secret-name>, ...]       # optional; omit to share the whole dir
    readers:
      workloads: ro                  # ro | none
      humans:
        owner:  ro                   # ro | none
        editor: ro
        viewer: none

  # transit:
  #   keyName: from-<W>-to-<R>-<env>       # operator auto-fills if omitted
  #   keyType: aes256-gcm96                # any OpenBao transit key type
  #   writerOps: [encrypt]                 # subset of encrypt|decrypt|sign|rewrap
  #   readers:
  #     workloads: [decrypt]               # subset of encrypt|decrypt|verify|rewrap
  #     humans:
  #       owner:  [decrypt]
  #       editor: [decrypt]
  #       viewer: []

  # pki:
  #   roles: [<role-name>, ...]            # PKI roles from the engine
  #   readers:
  #     workloads: [issue]                 # subset of issue|read
  #     humans:
  #       owner:  [issue, read]
  #       editor: [issue]
  #       viewer: [read]
```

`to.mode=all` is the broadcast case (maps to `shared/all/` or `shared-all-<env>`). `to.mode=tenants` is the directional case (maps to `from-<W>/to-<R>/` or `from-<W>-to-<R>-<env>`).

---

## Example — KV: team-a shares a webhook signing key with team-b

Directly matches [Model B §share-team-a-to-team-b](./multi-tenant-path-layout.md#example-full-policy-set-attached-to-team-a-team-a-api-role) and [Model A §Example 2](./multi-tenant-namespace-layout.md#example-2--policy-inside-shared).

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBaoShare
metadata:
  name: webhook-signing
  namespace: team-a                  # writer tenant's k8s ns
spec:
  engineRef: kv
  from:
    tenant: team-a
  to:
    mode: tenants
    tenants: [team-b]
  kv:
    keys: [webhook-signing-key, event-bus-token]     # optional; omit to share the whole directory
    readers:
      workloads: ro                  # ro | none
      humans:
        owner:  ro
        editor: ro
        viewer: none
```

What the operator does:

- **Model B (path):** writes data under `kv/data/shared/<env>/from-team-a/to-team-b/{webhook-signing-key,event-bus-token}`; attaches `share-team-a-to-team-b-writer` to team-a's auth roles and `share-team-a-to-team-b-reader` to team-b's.
- **Model A (namespace):** writes data under `shared/kv/data/<env>/from-team-a/to-team-b/...`; handles cross-namespace access per `OpenBao.spec.sharing.crossNamespaceStrategy` (two-token or identity-group — see [Model A §Cross-namespace sharing](./multi-tenant-namespace-layout.md#cross-namespace-sharing)).

## Example — KV broadcast: platform shares a corp CA bundle with everyone

Matches `shared/dev/all/corp-ca-bundle` from both layout docs.

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBaoShare
metadata:
  name: corp-ca-bundle
  namespace: mto-system
spec:
  engineRef: kv
  from:
    tenant: platform
  to:
    mode: all
  kv:
    keys: [corp-ca-bundle, smtp-relay-password, artifactory-read-token]
    readers:
      workloads: ro
      humans:
        owner:  ro
        editor: ro
        viewer: ro
```

Operator attaches `shared-all-reader` to every tenant role.

## Example — Transit: directional encrypt/decrypt pair

Matches the transit key `from-team-a-to-team-b-dev`.

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBaoShare
metadata:
  name: team-a-to-team-b-transit
  namespace: team-a
spec:
  engineRef: transit
  from:
    tenant: team-a
  to:
    mode: tenants
    tenants: [team-b]
  transit:
    keyName: from-team-a-to-team-b-dev
    keyType: aes256-gcm96
    writerOps: [encrypt]             # verbs granted to team-a
    readers:
      workloads: [decrypt]           # verbs granted to team-b workloads
      humans:
        owner:  [decrypt]
        editor: [decrypt]
        viewer: []
```

Asymmetric-by-policy: team-a can only encrypt, team-b can only decrypt, even though the key itself is symmetric. For asymmetric-by-key setups (e.g. `sign`/`verify`), set `keyType: ed25519` and populate `writerOps: [sign]`, `readers.workloads: [verify]`.

## Example — PKI: shared CA for mutual mTLS

Matches `pki-shared/` with role `dev`. Both tenants are "readers" in the sense that both issue leaf certs against the shared mount; `from.tenant` is the platform because neither `team-a` nor `team-b` owns the CA.

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBaoShare
metadata:
  name: shared-mtls-ca
  namespace: mto-system
spec:
  engineRef: pki-shared
  from:
    tenant: platform
  to:
    mode: tenants
    tenants: [team-a, team-b]
  pki:
    roles: [dev]                     # roles in pki-shared that consumers may use
    readers:
      workloads: [issue]             # issue | read
      humans:
        owner:  [issue, read]
        editor: [issue]
        viewer: [read]
```

`pki/cert/ca` and `pki/ca_chain` are unauthenticated on OpenBao ([path-layout §Mirror policies note](./multi-tenant-path-layout.md#mirror-policies)), so no policy grant is needed for CA trust — only for `issue`.

---

## Field reference

### Common

| Field | Type | Required | Description |
|---|---|---|---|
| `openBaoRef.name` | string | conditional | Required when multiple `OpenBao` CRs exist. |
| `openBaoRef.namespace` | string | no | k8s `ns` of the `OpenBao` CR. |
| `engineRef` | string | yes | Engine name inside the `OpenBao` CR. The engine's type determines which block (`kv`/`transit`/`pki`) is required. |
| `from.tenant` | string | yes | Writer tenant. Must own `metadata.namespace`. Use `platform` for platform-owned broadcasts. |
| `to.mode` | `enum` `tenants \| all` | yes | `tenants` = directional; `all` = broadcast. |
| `to.tenants` | `[]string` | conditional | Required when `to.mode=tenants`. **Exactly one** tenant, distinct from `from.tenant`. Multi-reader directional shares are not supported — create one `OpenBaoShare` per reader instead (see [Why single-reader directional](#why-single-reader-directional)). |

### `spec.kv` (engine type `kv-v2`)

| Field | Type | Required | Description |
|---|---|---|---|
| `keys` | `[]string` | no | Specific secret names to share. If omitted, the whole `from-W/to-R/` (or `all/`) directory is shared. |
| `readers.workloads` | `enum` `ro \| none` | no | Reader workloads' access. Default `ro`. |
| `readers.humans.{owner,editor,viewer}` | `enum` `ro \| none` | no | Reader humans' access per tenant role. Default `ro / ro / none`. |

### `spec.transit` (engine type `transit`)

| Field | Type | Required | Description |
|---|---|---|---|
| `keyName` | string | yes | Transit key to share. Created if absent. Naming convention: `from-<W>-to-<R>-<env>` for directional, `shared-all-<env>` for broadcast — operator auto-fills if omitted. |
| `keyType` | `enum` | no | Default `aes256-gcm96`. Use asymmetric types (`ed25519`, `rsa-*`, `ecdsa-*`) to enforce sign/verify splits. |
| `writerOps` | `[]verb` | no | Subset of `encrypt \| decrypt \| sign \| rewrap`. Default `[encrypt]` for symmetric, `[sign]` for asymmetric. |
| `readers.workloads` | `[]verb` | no | Subset of `encrypt \| decrypt \| verify \| rewrap`. Default `[decrypt]` for symmetric, `[verify]` for asymmetric. |
| `readers.humans.{owner,editor,viewer}` | `[]verb` | no | Per-role verb lists. |

### `spec.pki` (engine type `pki`)

| Field | Type | Required | Description |
|---|---|---|---|
| `roles` | `[]string` | yes | PKI role names (from the engine's `pki.roles[]`) that readers may use. |
| `readers.workloads` | `[]verb` | no | Subset of `issue \| read`. Default `[issue]`. |
| `readers.humans.{owner,editor,viewer}` | `[]verb` | no | Per-role verb lists. |

Note: `pki/cert/ca` and `pki/ca_chain` are on OpenBao's unauthenticated-paths list; no grant needed for CA trust.

### CEL / operator validation

- Exactly one of `kv`, `transit`, `pki` present; must match `engineRef`'s type.
- `from.tenant` must equal the Tenant owning `metadata.namespace`, or be `platform` when the CR lives in the operator namespace.
- `to.tenants` must not contain `from.tenant`.
- `to.mode=tenants` → `to.tenants.length == 1`. `to.mode=all` → `to.tenants` must be absent.
- Reserved segment guard: operator rejects a `OpenBaoShare` whose computed path would collide with `_shared`, `all`, `from-*`, or `to-*` naming (see [path-layout §Reserved path segments](./multi-tenant-path-layout.md#reserved-path-segments)).

### Why single-reader directional

The layout conventions in [Model A](./multi-tenant-namespace-layout.md) and [Model B](./multi-tenant-path-layout.md) name directional resources as `from-<W>/to-<R>/` (KV path) and `from-<W>-to-<R>-<env>` (transit key). `<R>` is one reader tenant — there is no defined naming for a two-reader share.

Three options were considered; one-share-per-reader is the chosen rule:

| Option | What it does | Why rejected |
|---|---|---|
| `to.tenants: [R1, R2]` with operator-level fan-out to N paths/keys | Operator writes the same data to `from-W/to-R1/*` **and** `from-W/to-R2/*` | Doubles writes on every update; no atomicity across readers; revoking R1 has to garbage-collect a copy |
| New naming `to-R1-R2/` | Single resource, policy attached to both | New convention for every N > 1 combination; path/key names grow `unboundedly` |
| **One share per reader** (accepted) | Writer authors N `OpenBaoShare` CRs | Zero new convention; revocation is per-CR; matches existing layout names |

For truly broadcast cases, use `to.mode=all` — one share, one resource, read by every tenant.

---

## How the operator realizes a share

### Model B (path)

- KV: writes/reads live at `kv/data/shared/<env>/from-<W>/to-<R>/*` (or `kv/data/shared/<env>/all/*`). Operator generates `share-<W>-to-<R>-writer` / `-reader` policies and attaches them to the appropriate auth roles.
- Transit: key materialized in the root transit mount. Policies grant `writerOps` on `transit/<verb>/<keyName>` to writer roles, `readers.workloads` verbs to reader roles.
- PKI: `pki-shared/` (or the engine named in `engineRef`) is already mounted by the `OpenBao` CR. Operator attaches an `issue`/`read` policy to reader roles.

### Model A (namespace)

- KV: writes/reads live in the `shared/` namespace at `kv/data/<env>/from-<W>/to-<R>/*`. Cross-namespace access is realized via OpenBao identity groups with `unsafe_cross_namespace_identity=true` — the entity authenticated in the reader's `bao` namespace is a member of a group in `shared/` that carries the `share-*-reader` policy. Requires `OpenBao.spec.sharing.allowCrossNamespaceIdentity=true`; without it the `OpenBaoShare` is rejected with `Ready=False, reason=CrossNamespaceIdentityDisabled`.
- Transit: key lives in `shared/transit/`. Same policy attachment as Model B, but inside `shared/`.
- PKI: `pki-shared/` lives in the `shared/` namespace.

Two-token / dual-login realizations are not supported — see [multi-tenant-namespace-layout.md#cross-namespace-sharing](./multi-tenant-namespace-layout.md#cross-namespace-sharing) for why.

---

## Status

```yaml
status:
  observedGeneration: 3
  conditions:
    - type: Ready
      status: "True"
      reason: ShareApplied
      observedGeneration: 3
    - type: OpenBaoResolved
      status: "True"
      observedGeneration: 3
    - type: WritersGranted
      status: "True"
      observedGeneration: 3
    - type: ReadersGranted
      status: "True"
      observedGeneration: 3
  resolvedOpenBao: mto-system/cluster-default
  resolvedEngine: kv
  resolvedModel: path                # path | namespace
  baoPath: "kv/data/shared/dev/from-team-a/to-team-b"
  grantedTenants: [team-b]
```

---

## Authorization model

- **Writer team** creates/updates/deletes the `OpenBaoShare` in their own k8s namespace.
- **Platform team** owns the `OpenBao` CR (engines, mounts, tenancy mode). Platform-wide broadcasts (`to.mode=all`) are created by the platform team in `mto-system`.
- **Reader tenants** never edit anything; access is driven by the writer's `OpenBaoShare`.
- Cluster admins can restrict `to.mode=all` via Kubernetes RBAC (e.g. only allow `OpenBaoShare` creation in `mto-system` for broadcasts) or via admission webhook (Kyverno/Gatekeeper).

---

## Revocation

When a reader is removed from `spec.to.tenants`, or the whole `OpenBaoShare` is deleted, the operator applies the following actions gated by `OpenBao.spec.safety.allowDeletes`. See [docs/design/revocation.md](./revocation.md) for the full model.

| `allowDeletes` | Policy detached from reader | KV data at share path | Transit key |
|---|---|---|---|
| `false` (default) | yes | left in place | not rotated |
| `true` | yes | deleted (soft-delete in kv-v2; destroy requires explicit `safety.allowDestroy`) | rotated to new version; old ciphertexts no longer decryptable under reader's policies |

"Policy detached" always happens regardless of `allowDeletes` — without it the revocation hasn't taken effect. The `allowDeletes` flag controls whether the operator also removes the *data* the reader could previously fetch.

## Relationship to the `OpenBao` CRD

- `OpenBaoShare` cannot create engines, mounts, or auth methods. The engine named by `engineRef` must exist in a `Ready` `OpenBao` CR.
- Deleting the `OpenBao` CR does not cascade-delete `OpenBaoShare`s; the operator marks them `Ready=False, reason=OpenBaoMissing`.
- `safety.allowDeletes` on the `OpenBao` CR governs whether the operator will revoke access and delete KV data when a reader is removed from `to.tenants`. When `false`, revocations log a warning and leave data in place.
