# ADR-0003-a: OpenBao CRD Design

- **Status:** Draft
- **Date:** 2026-04-22
- **Scope:** Schema of `security.tenantoperator.stakater.com/v1alpha1, Kind=OpenBao`
- **Informed by:** [ADR-0001: Tenancy model](../adr/0001-tenancy-mode.md)

This document is the source of truth for the CRD shape. Controllers and tests follow it; when the schema and controllers disagree, this document wins.

## Terminology

The word "namespace" is overloaded. In this doc:

- **k8s namespace** (or **k8s `ns`**) = Kubernetes namespace (e.g. `acme-api`).
- **`bao` namespace** (or **`bao` `ns`**) = OpenBao namespace (e.g. `acme/`, addressed via `X-Vault-Namespace`).

Schema field names keep their literal values (`tenancy.mode: namespace`, `rbac.roleScope: namespace`, template var `{{ .namespace }}`). Those values are defined below — see the field reference for what each refers to.

---

## Full CR

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBao
metadata:
  name: cluster-default
  namespace: mto-system
spec:
  # ─── SERVER ──────────────────────────────────────────────────────────
  server:
    url: https://bao.example.com:8200
    tokenSecretRef:
      name: openbao-credentials
      key: token
    # caBundleSecretRef: { name: openbao-ca, key: ca.crt }
    # insecureSkipVerify: false

  # ─── TENANCY (ADR-0001) ──────────────────────────────────────────────
  tenancy:
    # namespace (default): 1 Tenant = 1 bao namespace. Hard isolation.
    # path      (opt-in):  one global mount, ACL-gated, legacy model.
    mode: namespace

    defaults:
      env: prod

  # ─── AUTH MANAGEMENT ─────────────────────────────────────────────────
  authManagement:
    kubernetes: ensure        # ensure | off
    oidc: off                 # ensure | off  (off when sso.mode=disabled)

  # ─── SSO ─────────────────────────────────────────────────────────────
  sso:
    mode: disabled            # secret | inline | disabled

    # secretRef:  { name: sso-openbao-config }        # when mode=secret
    # inline:                                         # when mode=inline
    #   issuer: https://dex.example.com
    #   clientId: openbao
    #   ...

    # Required unless mode=disabled.
    roleResolution:
      claim: groups
      patterns:
        - { role: owner,  match: "tenant-{{ .tenant }}-owners"  }
        - { role: editor, match: "tenant-{{ .tenant }}-editors" }
        - { role: viewer, match: "tenant-{{ .tenant }}-viewers" }
      tieBreakStrategy: highest   # highest | lowest | deny
      fallback: deny              # owner | editor | viewer | deny

  # ─── LAYOUT (optional) ───────────────────────────────────────────────
  # Every name the operator materializes — KV paths, transit keys, PKI
  # mount paths, PKI role names — lives in this one block. Engine
  # entries below hold only non-name config.
  #
  # When omitted, the operator uses mode-appropriate defaults (below).
  # Override only for migrations from existing Vault setups or to match
  # external consumers that read from fixed paths.
  #
  # Defaults (two modes: namespace | path):
  #   kv:
  #     namespace → "secret/{{ .env }}/{{ .namespace }}/{{ .name }}"
  #     path      → "secret/tenants/{{ .tenant }}/{{ .env }}/{{ .namespace }}/{{ .name }}"
  #   transitKey:              (per-k8s-ns key)
  #     namespace → "{{ .namespace }}-{{ .env }}"
  #     path      → "{{ .namespace }}-{{ .env }}"
  #     Note: transit keys share one global mount in path mode. The
  #     default assumes `{{ .namespace }}` (nsFull) is unique across
  #     tenants — true when tenants use `withTenantPrefix`. Tenants
  #     using `withoutTenantPrefix` must either guarantee unique
  #     k8s ns names or override with `{{ .tenant }}-{{ .namespace }}-{{ .env }}`.
  #     The operator detects collisions at reconcile time and fails
  #     the Tenant with reason=TransitKeyCollision.
  #   transitKeyShared:        (intra-tenant shared key)
  #     both      → "{{ .tenant }}-shared-{{ .env }}"
  #   pkiMount:
  #     namespace → "pki"
  #     path      → "pki-{{ .tenant }}"
  #   pkiRole:                 (per-k8s-ns role)
  #     both      → "{{ .namespace }}-{{ .env }}"
  #   pkiRoleShared:           (intra-tenant shared role)
  #     both      → "{{ .tenant }}-shared-{{ .env }}"
  #
  # Template variables (all operator-supplied; do not substitute yourself):
  #   {{ .tenant }}    — MTO tenant name
  #   {{ .env }}       — tenancy.defaults.env or mto.secrets/env annotation
  #   {{ .namespace }} — k8s namespace (full name, per nsFull), not bao ns
  #   {{ .name }}      — secret key name (KV only)
  #
  # The `_shared` KV path segment sits at the same level as
  # {{ .namespace }} and is not expressed via this template — the
  # operator injects it directly. See "Intra-tenant sharing" below.
  #
  # layout:
  #   templates:
  #     kv:                "secret/{{ .env }}/{{ .namespace }}/{{ .name }}"
  #     transitKey:        "{{ .namespace }}-{{ .env }}"
  #     transitKeyShared:  "{{ .tenant }}-shared-{{ .env }}"
  #     pkiMount:          "pki"
  #     pkiRole:           "{{ .namespace }}-{{ .env }}"
  #     pkiRoleShared:     "{{ .tenant }}-shared-{{ .env }}"

  # ─── TENANT ROLE MAPPING (MTO role → policy tier) ────────────────────
  # Used for both humans (after sso.roleResolution) and workloads (direct).
  # IdP group patterns live in sso.roleResolution.patterns, not here.
  tenantRoleMapping:
    owner:
      policyTier: admin        # admin | editor | viewer | none
    editor:
      policyTier: editor
    viewer:
      policyTier: viewer

    # Optional: replace default capability set per tier.
    policyOverrides:
      admin:  { capabilities: [create, read, update, delete, list] }
      editor: { capabilities: [create, read, update, list] }
      viewer: { capabilities: [read, list] }

  # ─── RBAC (workloads via kubernetes-auth) ────────────────────────────
  rbac:
    roleScope: namespace         # namespace | app  (k8s ns granularity)
    defaultCapability: editor    # admin | editor | viewer | none
    token:
      ttl: 1h
      maxTTL: 4h
      renewable: true

  # ─── ENGINES (per-tenant) ────────────────────────────────────────────
  # Each entry is materialized per Tenant. In namespace mode, inside the
  # Tenant's bao ns. In path mode, as one global mount with per-tenant
  # separation in path/key naming. See "Per-tenant realization" below.
  #
  # Cross-tenant engines do NOT live here. Shared KV and shared Transit
  # are auto-created by the operator when an OpenBaoShare is admitted.
  # Shared PKI is declared in `sharedEngines` below — see "Shared
  # realization" for why the split.
  engines:

    - name: kv
      type: kv-v2
      layoutRef: kv
      enabled: true
      strategy:
        mount:
          path: secret               # namespace mode: <tenant>/secret/
                                     # path mode: single global secret/ mount
          manage: adopt              # off | adopt | ensure
      policies:
        presets: [admin, editor, viewer]
      projection:
        mode: external-secrets       # external-secrets | csi | none
        secretStore:
          scope: namespace           # namespace | cluster  (k8s ns placement)
          name: openbao

    - name: transit
      type: transit
      layoutRef: transitKey
      enabled: false                  # opt-in
      strategy:
        mount: { path: transit, manage: adopt }
      policies: { presets: [admin] }
      transit:
        # Operator creates one key per k8s ns (name from layoutRef template),
        # plus one `<tenant>-shared-<env>` key per tenant with >=2 namespaces
        # (see Intra-tenant sharing).
        keyType: aes256-gcm96         # aes256-gcm96 | chacha20-poly1305 | ed25519 | rsa-2048 | rsa-4096 | ecdsa-p256 | ...
      # No projection — transit is API-only.

    - name: pki
      type: pki
      layoutRef: pkiMount
      enabled: false                  # opt-in
      strategy:
        mount: { path: pki, manage: ensure }
      policies: { presets: [admin, viewer] }
      pki:
        maxLeaseTTL: 8760h            # 1y
        intermediate: true            # this PKI is an intermediate CA, signed by a root CA outside this CR

        # Role names come from spec.layout.templates.pkiRole and
        # .pkiRoleShared. Only non-name config lives here.
        perNamespaceRole:             # materialized once per k8s ns in the tenant
          allowedDomains: ["{{ .namespace }}.svc.cluster.local"]
          allowSubdomains: true
          maxTTL: 720h                # 30d

        intraTenantSharedRole:        # materialized once per tenant with >=2 k8s ns (optional)
          allowedDomains: ["*.{{ .tenant }}.svc.cluster.local"]
          allowSubdomains: true
          maxTTL: 720h

  # ─── SHARED ENGINES (PKI only) ───────────────────────────────────────
  # Only PKI needs a mount-level declaration for cross-tenant use. A PKI
  # mount is one CA, with its own validity, issuer chain, and role
  # catalogue — all mount-level properties owned by the platform team,
  # not by any one share.
  #
  # Shared KV and shared Transit are NOT listed here. The operator
  # creates them implicitly on first OpenBaoShare of the matching type.
  # See "Shared realization" below for the full rationale.
  sharedEngines:

    - name: pki-shared
      type: pki
      strategy:
        mount: { path: pki-shared, manage: ensure }
      pki:
        maxLeaseTTL: 8760h
        intermediate: true
        roles:
          - name: dev
            allowedDomains: ["*.svc.cluster.local"]
            allowSubdomains: true
            maxTTL: 720h

  # ─── SCAFFOLDING ─────────────────────────────────────────────────────
  scaffolding:
    mode: on-annotation          # none | on-annotation
    annotations:
      enable: "mto.secrets/enable"
      keys:   "mto.secrets/keys"
      env:    "mto.secrets/env"

  # ─── SHARING ─────────────────────────────────────────────────────────
  # Cross-tenant sharing (OpenBaoShare) realization. Only read in
  # tenancy.mode=namespace — in path mode, sharing is first-class via
  # path globs and needs no extra plumbing.
  sharing:
    # The operator realizes cross-namespace access via OpenBao's
    # identity-group feature (unsafe_cross_namespace_identity=true).
    # Two-token alternatives are rejected — see
    # docs/design/multi-tenant-namespace-layout.md#cross-namespace-sharing.
    allowCrossNamespaceIdentity: false   # must be true to admit any OpenBaoShare

  # ─── SAFETY ──────────────────────────────────────────────────────────
  # See docs/design/revocation.md for how these flags combine.
  safety:
    # Allow reversible destructive actions on revocation:
    #   - kv-v2 soft-delete under revoked share paths
    #   - transit key rotation when a reader is revoked
    #   - cascade-delete of a tenant's bao namespace (namespace mode)
    allowDeletes: false

    # Allow irreversible destructive actions:
    #   - kv/destroy (permanent version removal)
    #   - kv/metadata delete (permanent destroy of all versions)
    # Ignored unless allowDeletes is also true.
    allowDestroy: false

    # Revoke in-flight tokens when their policies are detached. When
    # false, existing tokens continue to work until their own TTL
    # expires — up to rbac.token.maxTTL after revocation.
    revokeExistingTokens: true
```

---

## Minimal CR (defaults applied)

```yaml
apiVersion: security.tenantoperator.stakater.com/v1alpha1
kind: OpenBao
metadata:
  name: cluster-default
  namespace: mto-system
spec:
  server:
    url: https://bao.example.com:8200
    tokenSecretRef: { name: openbao-credentials, key: token }

  engines:
    - name: kv
      type: kv-v2
      strategy:
        mount: { path: secret }
```

Defaults applied:

| Field | Default |
|---|---|
| `tenancy.mode` | `namespace` |
| `tenancy.defaults.env` | `prod` |
| `authManagement.kubernetes` | `ensure` |
| `authManagement.oidc` | `off` |
| `sso.mode` | `disabled` |
| `tenantRoleMapping.owner.policyTier / editor.policyTier / viewer.policyTier` | `admin` / `editor` / `viewer` |
| `rbac.roleScope` | `namespace` |
| `rbac.defaultCapability` | `editor` |
| `rbac.token.ttl` / `maxTTL` | `1h` / `4h` |
| `engines[].strategy.mount.manage` | `adopt` |
| `engines[].projection.mode` (kv-v2 only) | `external-secrets` |
| `engines[].projection.secretStore.scope` | `namespace` |
| `sharedEngines[].strategy.mount.manage` | `ensure` |
| `scaffolding.mode` | `on-annotation` |
| `safety.allowDeletes` | `false` |

---

## Field reference

### `spec.server` — connection to OpenBao

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string (URI) | yes | OpenBao server base URL. |
| `tokenSecretRef` | `SecretKeySelector` | yes | Secret holding the operator's `Bao` token. |
| `caBundleSecretRef` | `SecretKeySelector` | no | CA bundle for TLS verification. |
| `insecureSkipVerify` | `bool` | no | Skip TLS verification. Dev only. |

### `spec.tenancy` — isolation model (ADR-0001)

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `mode` | `enum` `namespace \| path` | no | `namespace` | Isolation model. `namespace` = 1 Tenant = 1 `bao` `ns`. `path` = legacy, one global mount. See ADR-0001. |
| `defaults.env` | string | no | `prod` | Fallback environment token used in layout templates when no per-namespace override is set. The per-namespace annotation (`scaffolding.annotations.env`, default `mto.secrets/env`) is authoritative whenever it is present on the k8s namespace — a single Tenant can therefore span multiple envs (e.g. `dev` + `prod`) by annotating each k8s namespace differently. |

### `spec.authManagement`

| Field | Type | Default | Description |
|---|---|---|---|
| `kubernetes` | `enum` `ensure \| off` | `ensure` | Whether the operator manages Kubernetes auth mounts. |
| `oidc` | `enum` `ensure \| off` | `off` | Whether the operator manages OIDC auth. Keep `off` when `sso.mode=disabled`. |

### `spec.sso`

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | `enum` `secret \| inline \| disabled` | `disabled` | SSO source. |
| `secretRef.name` | string | — | Required when `mode=secret`. |
| `inline` | `map[string]string` | — | Required when `mode=inline`. Opaque bag; shape defined by the operator. |
| `roleResolution` | object | — | Required unless `mode=disabled`. |

#### `spec.sso.roleResolution`

| Field | Type | Default | Description |
|---|---|---|---|
| `claim` | string | — | OIDC claim to inspect, e.g. `groups`. |
| `patterns[]` | list | — | Template-aware group `matchers`. |
| `patterns[].role` | `enum` `owner \| editor \| viewer` | — | MTO role assigned when matched. |
| `patterns[].match` | string | — | Template, e.g. `tenant-{{ .tenant }}-owners`. |
| `tieBreakStrategy` | `enum` `highest \| lowest \| deny` | `highest` | Applied when a user matches multiple patterns. |
| `fallback` | `enum` `owner \| editor \| viewer \| deny` | `deny` | Applied when no pattern matches. |

### `spec.layout` (optional)

Named path templates shared across engines. **Optional** — when omitted, the operator uses mode-appropriate defaults. Override only for migrations from existing Vault setups or to match external consumers that read from fixed paths.

Defaults by mode. When `spec.layout` is omitted (or a specific key is omitted), the operator substitutes the value below:

| Key | `tenancy.mode=namespace` | `tenancy.mode=path` |
|---|---|---|
| `kv` | `secret/{{ .env }}/{{ .namespace }}/{{ .name }}` | `secret/tenants/{{ .tenant }}/{{ .env }}/{{ .namespace }}/{{ .name }}` |
| `transitKey` | `{{ .namespace }}-{{ .env }}` | `{{ .namespace }}-{{ .env }}` |
| `transitKeyShared` | `{{ .tenant }}-shared-{{ .env }}` | `{{ .tenant }}-shared-{{ .env }}` |
| `pkiMount` | `pki` | `pki-{{ .tenant }}` |
| `pkiRole` | `{{ .namespace }}-{{ .env }}` | `{{ .namespace }}-{{ .env }}` |
| `pkiRoleShared` | `{{ .tenant }}-shared-{{ .env }}` | `{{ .tenant }}-shared-{{ .env }}` |

Template variables (all operator-supplied; never hard-coded by the user):

- `{{ .tenant }}` — MTO tenant name.
- `{{ .env }}` — environment from `tenancy.defaults.env` or the scaffolding annotation override.
- `{{ .namespace }}` — **k8s namespace** (full name per `nsFull`), not `bao` `ns`.
- `{{ .name }}` — secret name (KV only).

Operator validates user-provided templates:

- `path` mode: `kv` must contain `{{ .tenant }}` (tenant data lives under a shared KV mount; the prefix prevents cross-tenant collision).
- `namespace` mode: `{{ .tenant }}` in `kv` is redundant (`bao` `ns` is the boundary) but not rejected.
- All modes: `{{ .namespace }}` and `{{ .name }}` must appear in `kv` where path-per-secret is expected.

Collision safety (`path` mode only):

- `transitKey` defaults to `{{ .namespace }}-{{ .env }}`, which is unique across tenants when every tenant uses `withTenantPrefix` (`nsFull` already includes the tenant).
- When a tenant uses `withoutTenantPrefix`, two tenants can declare k8s namespaces with the same short name, and the default template renders the same transit key name. The operator detects this at Tenant reconcile time and fails with `TenantsReconciled=False, reason=TransitKeyCollision`. Fix by overriding `spec.layout.templates.transitKey` to `{{ .tenant }}-{{ .namespace }}-{{ .env }}`.
- `pkiRole` defaults to `{{ .namespace }}-{{ .env }}` but collision is structurally impossible because PKI mounts are per-tenant (`pki-<tenant>/` in path mode, `<tenant>/pki/` in namespace mode). No override needed.

### `spec.tenantRoleMapping`

Maps each MTO tenant role to an OpenBao policy tier. Used for both humans (after `sso.roleResolution` extracts the role from IdP groups) and workloads (direct, no SSO in the path). IdP group patterns live in `sso.roleResolution.patterns`, not here.

| Field | Type | Default | Description |
|---|---|---|---|
| `owner.policyTier` | `enum` `admin \| editor \| viewer \| none` | `admin` | Policy tier for tenant owners. `none` = no policy attached. |
| `editor.policyTier` | `enum` | `editor` | Policy tier for tenant editors. |
| `viewer.policyTier` | `enum` | `viewer` | Policy tier for tenant viewers. |

#### `spec.tenantRoleMapping.policyOverrides`

Optional. Replaces the default capability set for each tier. If `<role>.policyTier=none`, the override for that tier is ignored.

| Field | Type | Description |
|---|---|---|
| `admin.capabilities` | `[]` of `create\|read\|update\|delete\|list` | Full verb set for the admin tier. |
| `editor.capabilities` | same | Full verb set for the editor tier. |
| `viewer.capabilities` | same | Full verb set for the viewer tier. |

### `spec.rbac`

| Field | Type | Default | Description |
|---|---|---|---|
| `roleScope` | `enum` `namespace \| app` | `namespace` | k8s-auth role granularity. `namespace` = one role per k8s `ns`; `app` = one role per app SA. |
| `defaultCapability` | `enum` `admin \| editor \| viewer \| none` | `editor` | Default tier for workloads. `none` skips k8s-auth scaffolding. |
| `token.ttl` | duration | `1h` | Workload token TTL. |
| `token.maxTTL` | duration | `4h` | Workload token max TTL. |
| `token.renewable` | `bool` | — | Whether workload tokens are renewable. |

### `spec.engines[]`

Per-tenant engines. Each entry is materialized per Tenant. Cross-tenant engines do not live here — see `spec.sharedEngines[]` below and the realization section at the end of this document.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | string | yes | — | Logical engine name, e.g. `kv`. Referenced by `OpenBaoShare.engineRef`. |
| `type` | `enum` `kv-v2 \| transit \| pki` | yes | — | Engine type. Determines which engine-specific block (`transit`, `pki`) is read. |
| `layoutRef` | string | no | per `type` (`kv` / `transitKey` / `pkiMount`) | Key into `spec.layout.templates`. Only needed when the user overrides the template for this engine. |
| `enabled` | `bool` | no | `true` | Disable without removing. |
| `strategy.mount.path` | string | yes | — | Mount path, e.g. `secret`. |
| `strategy.mount.manage` | `enum` `off \| adopt \| ensure` | no | `adopt` | How aggressively the operator manages the mount. |
| `policies.presets` | list of `admin\|editor\|viewer\|none` | yes | — | Policy tiers to materialize on each Tenant's `bao` `ns` / per-tenant paths. |
| `projection.mode` | `enum` `external-secrets \| csi \| none` | no (kv-v2 only) | `external-secrets` | How secrets reach pods. Only read when `type=kv-v2`; must be absent on `transit`/`pki` entries. |
| `projection.secretStore.scope` | `enum` `namespace \| cluster` | conditional | `namespace` | ESO `SecretStore` placement in k8s. `namespace` = one per k8s `ns`; `cluster` = single `ClusterSecretStore`. Required when `projection.mode=external-secrets`. |
| `projection.secretStore.name` | string | conditional | — | Name of the generated SecretStore. |

In `tenancy.mode=namespace`, the operator sets `spec.provider.vault.namespace` (the `bao` `ns`) on every generated `SecretStore` automatically; no CRD knob is exposed.

#### `spec.engines[].transit` (when `type=transit`)

Encryption-as-a-service. No secret data stored; clients call `encrypt`/`decrypt` against named keys.

| Field | Type | Required | Description |
|---|---|---|---|
| `keyType` | `enum` (OpenBao key types) | no | Default `aes256-gcm96`. Common: `aes256-gcm96`, `chacha20-poly1305`, `ed25519`, `rsa-2048`, `rsa-4096`, `ecdsa-p256`. |

Key materialization is implicit: the operator creates one key per k8s namespace using the resolved `transitKey` template, plus one `<tenant>-shared-<env>` key per tenant with ≥2 namespaces. See [Intra-tenant sharing](#intra-tenant-sharing).

#### `spec.engines[].pki` (when `type=pki`)

Per-tenant certificate authority. Role names come from `spec.layout.templates.pkiRole` and `spec.layout.templates.pkiRoleShared`. Only non-name config lives in this block.

| Field | Type | Required | Description |
|---|---|---|---|
| `maxLeaseTTL` | duration | yes | Upper bound on issued cert lifetime for this mount. |
| `intermediate` | `bool` | no | If `true`, this PKI is an intermediate CA. The root CA / CSR signing happens outside this CR. |
| `perNamespaceRole` | object | yes | Config for the role materialized once per k8s namespace (name from `layout.templates.pkiRole`). |
| `perNamespaceRole.allowedDomains` | `[]string` (template) | yes | Allowed SAN domains; may reference `{{ .tenant }}`, `{{ .namespace }}`, `{{ .env }}`. |
| `perNamespaceRole.allowSubdomains` | `bool` | no | Allow subdomains of `allowedDomains`. |
| `perNamespaceRole.maxTTL` | duration | yes | Upper bound on issued cert lifetime for this role. |
| `intraTenantSharedRole` | object | no | Config for the role materialized once per tenant with ≥2 k8s namespaces (name from `layout.templates.pkiRoleShared`). Omit to skip intra-tenant PKI sharing. See [Intra-tenant sharing](#intra-tenant-sharing). |
| `intraTenantSharedRole.allowedDomains` | `[]string` (template) | yes | Allowed SAN domains; may reference `{{ .tenant }}`, `{{ .env }}` (no `{{ .namespace }}` — there is no single k8s `ns` context for a shared role). |
| `intraTenantSharedRole.allowSubdomains` | `bool` | no | Allow subdomains of `allowedDomains`. |
| `intraTenantSharedRole.maxTTL` | duration | yes | Upper bound on issued cert lifetime for this role. |

CEL rules:

- `type=transit` → `transit` required, `pki` and `projection` must be absent.
- `type=pki` → `pki` required, `transit` and `projection` must be absent.
- `type=kv-v2` → both `transit` and `pki` must be absent; `projection` is used.
- `pki.intraTenantSharedRole.allowedDomains[*]` must not contain `{{ .namespace }}` — no single-ns context is available when the role is materialized.

### `spec.sharedEngines[]` — shared PKI engines

Cross-tenant PKI mounts. Declared here (not on `OpenBaoShare`) because a PKI mount is one CA — `maxLeaseTTL`, `intermediate`, issuer chain, and the `roles[]` catalogue are mount-level properties with a single correct value owned by the platform team.

Shared KV and shared Transit are not declared — the operator creates them implicitly when the first `OpenBaoShare` of the matching type is admitted. See [Shared realization](#shared-realization) for why.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | string | yes | — | Logical name, referenced by `OpenBaoShare.engineRef`. Convention: `pki-shared`, or `pki-shared-<purpose>` when multiple shared `CAs` coexist. |
| `type` | `enum` `pki` | yes | — | Only `pki` is valid in `sharedEngines[]`. |
| `strategy.mount.path` | string | yes | — | Mount path, e.g. `pki-shared`. |
| `strategy.mount.manage` | `enum` `off \| adopt \| ensure` | no | `ensure` | Shared mounts default to `ensure` — the operator is authoritative. |
| `pki.maxLeaseTTL` | duration | yes | — | Mount-level cert lifetime cap. |
| `pki.intermediate` | `bool` | no | — | `true` = intermediate CA; root signing happens outside this CR. |
| `pki.roles[]` | list | yes | — | Role catalogue. `OpenBaoShare.spec.pki.roles` picks names from this list — shares do not define new roles. |
| `pki.roles[].name` | string | yes | — | Role name. **No template variables** — there is no tenant context for a shared CA. |
| `pki.roles[].allowedDomains` | `[]string` | yes | — | Allowed SAN domains. No template variables. |
| `pki.roles[].allowSubdomains` | `bool` | no | — | Allow subdomains of `allowedDomains`. |
| `pki.roles[].maxTTL` | duration | yes | — | Per-role lifetime cap. |

Fields deliberately absent from `sharedEngines[]`:

- `policies.presets` — there is no tenant whose roles receive these tiers. Policy attachment is done per share by `OpenBaoShare`.
- `projection` — PKI is API-only and has no kv-v2 projection path.
- `layoutRef` — path templates assume a tenant context; shared `CAs` have none.
- `enabled` — entries in `sharedEngines[]` are opt-in by virtue of being listed; omit the entry to not realize a shared CA.

### `spec.scaffolding`

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | `enum` `none \| on-annotation` | `on-annotation` | Whether to auto-create K8s resources for annotated apps. |
| `annotations.enable` | string | `mto.secrets/enable` | Enables scaffolding for a workload. |
| `annotations.keys` | string | `mto.secrets/keys` | Comma-separated list of secret keys to project. |
| `annotations.env` | string | `mto.secrets/env` | Per-k8s-namespace env annotation. Authoritative when set — `tenancy.defaults.env` only applies to k8s namespaces without this annotation. Enables one Tenant to span multiple envs. |

### `spec.sharing`

Only read in `tenancy.mode=namespace`. Governs how the operator realizes `OpenBaoShare` CRs across bao-namespace boundaries.

| Field | Type | Default | Description |
|---|---|---|---|
| `allowCrossNamespaceIdentity` | `bool` | `false` | Must be `true` for any `OpenBaoShare` to be admitted. Enables OpenBao's `unsafe_cross_namespace_identity` — acknowledging the known risks documented in [multi-tenant-namespace-layout.md](./multi-tenant-namespace-layout.md#cross-namespace-sharing). |

### `spec.safety`

Gates the destructive actions the operator is allowed to take. See [revocation.md](./revocation.md) for how these combine on each revocation trigger.

| Field | Type | Default | Description |
|---|---|---|---|
| `allowDeletes` | `bool` | `false` | Allow reversible destructive actions: `delete` capability in generated policies, kv-v2 soft-delete on revoked share paths, transit key rotation on reader revocation, and cascade-delete of a tenant's `bao` namespace in `namespace` mode. |
| `allowDestroy` | `bool` | `false` | Allow irreversible destructive actions: `kv/destroy` and `kv/metadata` delete. Ignored unless `allowDeletes` is also `true`. |
| `revokeExistingTokens` | `bool` | `true` | Revoke in-flight tokens when their policies are detached on revocation. When `false`, existing tokens remain valid until their own TTL expires (up to `rbac.token.maxTTL`). |

---

## Intra-tenant sharing

When a tenant has two or more k8s namespaces, its workloads often need common data (database connection strings, internal API tokens, a shared signing key). The operator provisions this implicitly — there is no CR to author.

### Trigger

`len(tenant.spec.namespaces.withTenantPrefix) + len(tenant.spec.namespaces.withoutTenantPrefix) >= 2`.

Single-namespace tenants still get the shared policy generated (harmless — grants access to paths and keys that don't exist).

### Resources created

| Resource | Where (namespace mode) | Where (path mode) | Gated by |
|---|---|---|---|
| KV reserved `subtree` | `<tenant>/kv/data/<env>/_shared/` | `kv/data/tenants/<tenant>/<env>/_shared/` | KV engine enabled |
| Transit shared key | `<tenant>/transit/keys/<tenant>-shared-<env>` | `transit/keys/<tenant>-shared-<env>` | `engines[type=transit].enabled=true` |
| PKI shared role | `<tenant>/pki/roles/<tenant>-shared-<env>` | `pki-<tenant>/roles/<tenant>-shared-<env>` | `engines[type=pki].enabled=true` **and** `engines[type=pki].pki.intraTenantSharedRole` present |
| Policy | `<tenant>/sys/policies/acl/<tenant>-shared-editor` | `sys/policies/acl/<tenant>-shared-editor` | always |

Naming comes from `spec.layout.templates` (`transitKeyShared`, `pkiRoleShared`). The shared transit key is always created when transit is enabled; the shared PKI role is only created when `engines[type=pki].pki.intraTenantSharedRole` is present — omit it to skip intra-tenant PKI sharing while keeping per-ns PKI.

### Policy attachment

`<tenant>-shared-editor` is attached to **every** k8s auth role of the tenant. Both apps in `team-a` can read and write intra-tenant shared resources — ownership is at the tenant level, not the workload level.

Teams that want stricter write control should use per-k8s-ns paths and gate writes via tenant RBAC at the SSO layer.

### `_shared` is reserved

`_shared` sits at the same path level as `{{ .namespace }}` but is **not** a k8s namespace and does not flow through `spec.layout.templates.kv`. The controller rejects tenants whose k8s namespaces short-name to `_shared`.

See layout details in [multi-tenant-namespace-layout.md](./multi-tenant-namespace-layout.md#intra-tenant-sharing) and [multi-tenant-path-layout.md](./multi-tenant-path-layout.md#intra-tenant-sharing).

---

## Per-tenant realization and shared realization

The operator materializes physical OpenBao mounts from `spec.engines[]` (per-tenant) and `spec.sharedEngines[]` (shared PKI). Shared KV and shared Transit are not declared — they are created on demand.

### Per-tenant realization (`spec.engines[]`)

| `engines[].type` | `tenancy.mode=namespace` (default) | `tenancy.mode=path` |
|---|---|---|
| `kv-v2` | One `kv/` mount inside each Tenant's `bao` `ns` | One global `kv/` mount; per-tenant separation by `tenants/<tenant>/` path prefix |
| `transit` | One `transit/` mount per Tenant `bao` `ns` | One global `transit/` mount; per-tenant key naming (`<tenant>-<ns>-<env>`) |
| `pki` | One `pki/` mount per Tenant `bao` `ns` | One `pki-<tenant>/` mount per Tenant |

### Shared realization

Shared realization splits by engine type. KV and Transit are implicit; PKI is declarative.

#### Shared KV and shared Transit — no declaration needed

The operator creates these the first time an `OpenBaoShare` of the matching type is admitted.

| Engine type | `tenancy.mode=namespace` | `tenancy.mode=path` |
|---|---|---|
| kv-v2 | One `kv/` mount in the `shared/` `bao` `ns`. Data at `kv/data/<env>/from-<W>/to-<R>/*` and `kv/data/<env>/all/*`. | No new mount. Share data lives at `secret/data/shared/<env>/…` inside the existing global `kv/` mount. |
| transit | One `transit/` mount in the `shared/` `bao` `ns`. Keys named `from-<W>-to-<R>-<env>` and `shared-all-<env>`. | No new mount. Share keys named the same way inside the existing global `transit/` mount. |

Why these are not declared in `sharedEngines[]`:

- **Mount config is trivial.** Path and type are the only mount-level settings. There is no CA identity, no validity, no role catalogue to own.
- **The operator reserves share paths unconditionally.** `secret/data/shared/*` and `transit/keys/{from-*, shared-*, to-*}` are off-limits to tenant writes regardless of any declaration. A declaration would add nothing the operator cannot already enforce.
- **`OpenBaoShare.engineRef` resolves by convention.** When a share's engine type is `kv-v2` or `transit`, `engineRef` resolves to the per-type shared mount; an explicit entry is not needed for name lookup.

Why these are not moved onto `OpenBaoShare`:

- **Writer-tenant CRs do not create mounts.** `OpenBaoShare` grants access inside an existing mount; letting it create the mount would let any writer tenant provision OpenBao infrastructure.
- **Per-share config already lives on the share.** `kv.keys[]`, `transit.keyName`, `transit.keyType`, and `{writerOps, readers}` are all share-level fields. Adding mount-level config on top would duplicate ownership and raise conflict-resolution questions when two shares disagree.

#### Shared PKI — declared in `sharedEngines[]`

Always its own mount in both modes. One `OpenBao` CR can declare several (e.g. `pki-shared`, `pki-shared-partners`).

| `tenancy.mode=namespace` | `tenancy.mode=path` |
|---|---|
| One mount (path from `sharedEngines[].strategy.mount.path`) in the `shared/` `bao` `ns` | One top-level mount at the same path |

Why PKI is declared (and not inferred like KV/Transit):

- **A PKI mount is one CA.** `maxLeaseTTL`, `intermediate`, and the issuer chain are mount-level properties with a single correct value. Two mounts cannot share them; two `OpenBaoShare` CRs cannot jointly own them.
- **The role catalogue is mount-level.** `pki.roles[]` defines which cert profiles exist on the mount. `OpenBaoShare.spec.pki.roles` picks names from that catalogue — shares do not define new roles.
- **Single owner = platform team.** The team that owns the `OpenBao` CR owns shared `CAs`. Putting CA config on `OpenBaoShare` would scatter it across writer-tenant-owned CRs with no defined conflict resolution.

### Minimal CR for each mode

**Namespace mode, per-tenant `kv` only (most common):**

```yaml
engines:
  - name: kv
    type: kv-v2
    strategy: { mount: { path: secret } }
```

**Namespace mode with a shared CA:**

```yaml
engines:
  - name: kv
    type: kv-v2
    strategy: { mount: { path: secret } }

sharedEngines:
  - name: pki-shared
    type: pki
    strategy: { mount: { path: pki-shared } }
    pki:
      maxLeaseTTL: 8760h
      intermediate: true
      roles:
        - name: dev
          allowedDomains: ["*.svc.cluster.local"]
          maxTTL: 720h
```

Shared KV and shared Transit need no entry — they appear when an `OpenBaoShare` of the matching type is admitted.

**Path mode:**

Same CR as above. The operator reads `tenancy.mode=path` and realizes the per-tenant `kv` as one global mount with per-tenant path prefixes, and the shared CA as a top-level `pki-shared/` mount.

## Companion CRD: `OpenBaoShare`

Cross-tenant sharing — directional (team-a → team-b) and broadcast (platform → all) — is modeled in a separate CRD, `OpenBaoShare`, so that writer teams can self-service shares without touching this platform-owned CR. See [ADR-0003-b: OpenBaoShare CRD](./0003-b-openbaoshare-crd.md) for the full schema.

Why separate:

- `OpenBao` defines engines, mounts, and policy tiers. One per cluster, platform-owned. Shared PKI mounts live here in `sharedEngines[]` alongside per-tenant engines; shared KV and Transit mounts are created on demand by the operator.
- `OpenBaoShare` references an engine by name and opens a named share within it. Many per cluster, writer-tenant-owned. Grants access; never configures the mount.

---

## Status

```yaml
status:
  observedGeneration: 7
  conditions:
    - type: Ready
      status: "True"
      reason: AllComponentsReady
      observedGeneration: 7
    - type: AuthConfigured
      status: "True"
      reason: KubernetesAuthMounted
      observedGeneration: 7
    - type: TenantsReconciled
      status: "True"
      reason: AllTenantsApplied
      observedGeneration: 7
  engines:
    - name: kv
      mounted: true
      path: secret
      lastReconciled: "2026-04-23T10:15:00Z"
    - name: pki-shared
      mounted: true
      path: pki-shared
      lastReconciled: "2026-04-23T10:15:01Z"
  tenants:
    - name: team-a
      ready: true
      baoNamespace: team-a/       # namespace mode only
      namespacesApplied: 2
      lastReconciled: "2026-04-23T10:15:02Z"
    - name: team-b
      ready: false
      reason: PolicyUpsertFailed
      lastReconciled: "2026-04-23T10:14:57Z"
```

- `observedGeneration` — top-level and per-condition; clients use it to tell whether `status` reflects the current `spec`.
- `Ready` — computed from `AuthConfigured` and `TenantsReconciled`. Not owned by a single controller.
- `AuthConfigured` — owned by the ClusterAuth controller.
- `TenantsReconciled` — owned by the Tenant controller.
- `engines[]` — one entry per `spec.engines[]` and `spec.sharedEngines[]`; reports mount state.
- `tenants[]` — one entry per MTO `Tenant` the operator has seen; `ready=false` entries carry `reason`.

Mutations go through `utils.RecomputeReadyInPlace` / `SetCond` ([internal/utils/status.go](../../internal/utils/status.go)).

---

## Validation summary

| Validation | Enforced by |
|---|---|
| `sso.secretRef` required when `sso.mode=secret` | Existing CEL on `SSOSpec` |
| `sso.inline` required when `sso.mode=inline` | Existing CEL on `SSOSpec` |
| `sso.roleResolution` must be absent when `sso.mode=disabled` | Existing CEL on `SSOSpec` |
| `projection.secretStore` required when `projection.mode=external-secrets` | CEL on `EngineProjection` |
| `projection.secretStore` must be absent otherwise | CEL on `EngineProjection` |
| `engines[].projection` must be absent when `type != kv-v2` | CEL on `EngineSpec` |
| `engines[].transit` required when `type=transit`, absent otherwise | CEL on `EngineSpec` |
| `engines[].pki` required when `type=pki`, absent otherwise | CEL on `EngineSpec` |
| `engines` has at least 1 item | `MinItems=1` on `OpenBaoSpec.Engines` |
| `sharedEngines[].type` must be `pki` | `Enum` on `SharedEngineSpec.Type` |
| `sharedEngines[].pki` required | CEL on `SharedEngineSpec` |
| `sharedEngines[].pki.roles[].name` / `allowedDomains` must not contain `{{` | CEL — no template vars in shared PKI |
| `sharedEngines[].name` unique across `engines[]` and `sharedEngines[]` | CEL on `OpenBaoSpec` |

---

## Differences from the previous design

Changes from the old shape (prior to ADR-0001 integration):

| # | Change | Driver |
|---|---|---|
| 1 | `tenancy.mode` default `path` → `namespace` | ADR-0001 decision |
| 4 | CEL rules on `TenancySpec` | Fail fast on misconfigured namespace-mode CRs |
| 5 | `engines[].strategy.scope` removed; `engines[]` is per-tenant only | Remove per-field semantics that changed with scope |
| 6 | Cross-tenant PKI moved to top-level `sharedEngines[]` | PKI mount = one CA; platform-owned, single-writer config |
| 7 | Cross-tenant KV and Transit no longer declared; auto-created on first `OpenBaoShare` | Mount config for KV/Transit is trivial and fully inferable |
| 8 | `engines[].projection` scoped to `type=kv-v2` only | transit/pki have no projection path; remove dead config |
| 9 | Layout template examples drop `tenants/{{ .tenant }}/` prefix | ADR rationale — short names inside tenant's `bao` `ns` |
| 10 | `authManagement.oidc` default `ensure` → `off` | Consistency with `sso.mode=disabled` default |
| 11 | Operator auto-sets `X-Vault-Namespace` on generated SecretStores in namespace mode | ADR Costs; not a user knob |

## Explicitly out of scope

- `tenancy.hierarchy: flat | env` — Alternative C is not in the accepted ADR.
- `tenancy.crossNamespaceReaders` — ADR flags cross-tenant aggregation as a known namespace-mode limitation, not a feature.
- `injection.secretStore.setVaultNamespace` — operator behavior, not user-tunable.
