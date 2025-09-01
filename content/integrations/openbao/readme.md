# MTO OpenBao Extension

> **Purpose:** A single source of truth for deploying, operating, and extending the **MTO OpenBao Extension (OBX)**. It serves both **platform engineers** (how to install/use) and **developers** (how it works under the hood).

---

## 1) What is it?

The OpenBao Extension (OBX) integrates **OpenBao** (Vault‑compatible) with **MTO Tenants** to deliver:

* Per‑tenant **KV v2** secret isolation (and optional **Transit** / **PKI** prefixes).
* **Kubernetes auth** for workloads (ServiceAccounts) and **OIDC/JWT** for humans (via SSO extension, e.g., Dex/Keycloak/Entra).
* Optional app‑level auto‑scaffolding via **External Secrets Operator (ESO)** or **CSI Secrets Store**.

> OBX **does not** install or operate the Bao cluster; it wires Bao to your MTO tenants.

---

## 2) Audience

* **Platform engineers:** Install/configure, define policies, enable tenants/app teams, troubleshoot.
* **Developers of OBX:** Understand controllers, Day‑0/1/2 flows, CRDs, idempotency and tests.

---

## 3) Architecture

```mermaid
graph TD
  subgraph Cluster
    MTO["MTO Core"];
    OBX["OpenBao Extension"];
    SSO["SSO Extension<br/>(Dex/Keycloak)"];
    ESO["External Secrets Operator"];
  end
  BAO["OpenBao"];
  WORK["Workloads"];

  MTO -->|Tenant CR| OBX;
  SSO -->|"issuer + client + groupsClaim"| OBX;
  OBX -->|"auth/kubernetes + auth/oidc + policies/roles"| BAO;
  ESO -->|"SecretStore / ExternalSecret"| BAO;
  BAO -->|"tokens / kv"| WORK;
```

---

## 4) Scope & Boundaries

* **OBX manages (on Bao):** `auth/kubernetes`, `auth/oidc|jwt`, tenant policies, roles, identity groups & aliases, and optional SecretStore/ESO objects in Kubernetes.
* **SSO extension manages:** Your IdP (Dex/Keycloak/Entra) & publishes an SSO **contract** (issuer, groupsClaim, `openbao` clientID/secret, group patterns) via CR **status** or a labeled **Secret**.
* **Out of scope:** Operating Bao (HA, storage, unseal, backup/restore, DR).

---

## 5) Prerequisites

1. **OpenBao** reachable (`https://bao.example.com:8200`) and a **scoped management token** (least privilege; see Appendix A policy).
2. **SSO extension** installed and configured; publishes **issuer**, **groupsClaim**, and `openbao` client.
3. **External Secrets Operator** (if using ESO mode), or **CSI Secrets Store** if using CSI.
4. **Network/TLS**: Pods allowed to egress to Bao; trust chain available.

---

## 6) Path Schema & Conventions

* **KV v2 path template:** `secret/tenants/<tenant>/<env>/<namespace>/<app>/<name>`
* **Default environment:** `prod` (configurable).
* **Granularity modes:**
  * `namespace` (default, simplest): one role per tenant namespace.
  * `app` (optional, tighter): one role per app SA.
* **Opt‑in scaffolding**: annotate Deployments/SS/CronJobs to auto‑generate ExternalSecrets.

---

## 7) Install (Platform Engineer)

### 7.1 Create namespace & install controller

```bash
kubectl create ns mto-system || true
helm upgrade --install mto-openbao-extension \
  oci://<your-registry>/mto-openbao-extension \
  -n mto-system \
  -f values.yaml
```

### 7.2 Provide Bao credentials (scoped)

```bash
kubectl -n mto-system create secret generic openbao-credentials \
  --from-literal=token=<BAO_OPERATOR_TOKEN>
```

### 7.3 Create OpenBaoIntegration CR

```yaml
# OpenBaoIntegration: wires your MTO tenants to an existing OpenBao (Vault-compatible) cluster.
# - Ensures Bao auth backends for workloads (Kubernetes) and humans (OIDC/JWT).
# - Sets up per-tenant policies/roles and (optionally) External Secrets Operator objects.
# - KV (secrets) enabled by default; other engines (Transit/PKI/Database) are sketched but off.
apiVersion: security.mto.stakater.com/v1alpha1
kind: OpenBaoIntegration
metadata:
  name: cluster-default                 # One per cluster (typical). Keep in mto-system.
  namespace: mto-system

spec:
  # --- How the operator connects to your OpenBao endpoint(s) ---
  connection:
    # Single endpoint for now; keep this lean. (Future: endpoints[] if needed.)
    url: https://bao.example.com:8200

    # Bao operator token (least-privilege policy). Secret MUST be in the same namespace as this CR.
    tokenSecretRef:
      name: openbao-credentials         # kubectl -n mto-system create secret generic openbao-credentials --from-literal=token=...
      key: token

    # OPTIONAL: provide a custom CA if Bao uses a private CA.
    # caBundleSecretRef:
    #   name: bao-ca
    #   key: ca.crt

    # OPTIONAL: dev-only. Don’t disable TLS verification in production.
    # insecureSkipVerify: false

  # --- What parts of Bao auth the operator should manage (on Bao’s side) ---
  manageAuth:
    kubernetes: Ensure                  # Off | Ensure  → mount/configure auth/kubernetes for workload SAs
    oidc: Ensure                        # Off | Ensure  → mount/configure auth/oidc (or jwt) for human users

  # --- Where OIDC settings come from (your SSO extension publishes this contract) ---
  sso:
    source: FromClusterSSO              # FromClusterSSO | FromBindingSecret | Inline
    ref:
      name: default                     # Name of ClusterSSO (or Secret if using FromBindingSecret)
    # inline:                            # Fallback if you don’t use the SSO extension (not recommended)
    #   issuer: https://dex.mto.svc.cluster.local
    #   clientID: vault-openbao
    #   clientSecretRef: { name: sso-openbao-client, namespace: mto-system, key: clientSecret }
    #   groupsClaim: groups

  # --- Tenancy model + defaults used in path templates, roles, etc. ---
  tenancy:
    mode: path                          # path | namespace (path = works on OSS; namespace for enterprise builds later)
    defaults:
      env: prod                         # Default environment if apps don’t specify mto.secrets/env

  # --- Naming & path templates (reused by engines below) ---
  layout:
    templates:
      # KV v2 path schema: tenant → env → namespace → app → name
      kv: "secret/tenants/{{ .tenant }}/{{ .env }}/{{ .namespace }}/{{ .app }}/{{ .name }}"

      # Transit key naming (used if Transit engine is enabled)
      transitKey: "ten-{{ .tenant }}-{{ .namespace }}-{{ .app }}"

      # Per-tenant PKI mount path (used if PKI engine is enabled)
      pkiMount: "pki/tenants/{{ .tenant }}"

  # --- RBAC granularity for workload access (Kubernetes auth roles) ---
  rbac:
    granularity: namespace              # namespace (default, simpler) | app (tighter; more roles)
    tokenTTL: 1h                        # SA-issued Bao tokens TTL
    tokenMaxTTL: 4h

  # --- Engines define which Bao capabilities to expose. KV is on; others are examples (off). ---
  engines:
    # 1) KV (secrets) — enabled by default
    - name: kv
      type: kv-v2
      enabled: true

      # Mount strategy: using a shared cluster mount "secret" (works everywhere). No destructive ops.
      strategy:
        scope: cluster                  # cluster = one shared mount (secret); tenant = per-tenant mount
        mount:
          path: secret                  # i.e., /v1/secret (kv v2)
          manage: Adopt                 # Off | Adopt | Ensure → Adopt uses if present; Ensure creates if missing

      # Policy presets:
      # - admin: RW under the tenant path (create/update/patch/delete/read/list on data; read/list/delete on metadata)
      # - viewer: RO under the tenant path (read/list on data+metadata)
      policies:
        presets: [admin, viewer]
        # extras: []                    # (Optional) Additional HCL rules if you need finer control

      # How apps get secrets:
      injection:
        mode: external-secrets          # external-secrets | csi | none
        secretStore:
          perNamespace: true            # Create one SecretStore per tenant namespace
          nameTemplate: "openbao"       # SecretStore name (kept simple for predictability)

      # Use the kv template declared in layout.templates.kv
      layoutRef: kv

    # 2) Transit (envelope encryption, signing) — OPTIONAL (disabled)
    - name: transit
      type: transit
      enabled: false

      strategy:
        scope: cluster
        mount:
          path: transit
          manage: Adopt

      transit:
        autoCreateKeyPerApp: true       # Create a key per app automatically on Day-1
        keyNameTemplate: "{{ .layout.transitKey }}"
        keyConfig:
          type: aes256-gcm96
          convergent_encryption: false

      policies:
        presets: [admin]                # Typically admins control encrypt/decrypt; app tokens may get sign/verify if needed

      injection:
        mode: none                      # Transit is usually consumed directly via Bao API from app code

    # 3) PKI (per-tenant CA/issuer) — OPTIONAL (disabled)
    - name: pki
      type: pki
      enabled: false

      strategy:
        scope: tenant                   # Each tenant gets its own PKI mount/CA (nice isolation)
        mount:
          pathTemplate: "{{ .layout.pkiMount }}"
          manage: Ensure

      pki:
        maxLeaseTTL: 8760h              # 1 year CA TTL
        intermediate: true              # Act as intermediate signed by your platform root (external to this operator)
        roles:
          - nameTemplate: "{{ .tenant }}-svc"
            allowed_domains:
              - "{{ .namespace }}.svc.cluster.local"
            allow_subdomains: true
            max_ttl: 720h

      # Optional glue to cert-manager so apps can request certs via a native K8s Issuer
      injection:
        certManager:
          enabled: true
          issuerKind: Issuer            # Issuer | ClusterIssuer
          nameTemplate: "{{ .tenant }}-pki"
          authRoleNameTemplate: "ten-{{ .tenant }}-pki"

    # 4) Database (dynamic DB users) — OPTIONAL (disabled)
    #    Example shows how to declare a shared "database" mount and per-tenant roles.
    - name: database
      type: database
      enabled: false

      strategy:
        scope: cluster
        mount:
          path: database
          manage: Adopt

      database:
        connections:
          - name: "pg-main"
            plugin_name: "postgresql-database-plugin"
            # DSN for the root/admin DB connection lives in a Secret you manage
            dsnSecretRef:
              name: db-root-dsn
              namespace: mto-system
              key: dsn
            tenantRoles:
              - nameTemplate: "{{ .tenant }}-app-ro"
                creation_statements: |
                  CREATE ROLE "{{name}}" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';
                  GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{{name}}";
                default_ttl: "1h"
                max_ttl: "4h"

      injection:
        mode: none                      # Apps fetch short-lived DB creds at runtime via Bao API

  # --- App-level scaffolding: only create ExternalSecrets when apps opt in via annotations ---
  scaffolding:
    mode: OnAnnotation                  # None | OnAnnotation
    annotations:
      enable: "mto.secrets/enable"      # "true" to enable for the workload
      keys:   "mto.secrets/keys"        # comma-separated logical keys (e.g., "db,api,license")
      env:    "mto.secrets/env"         # optional: override env per workload (defaults.tenancy.env otherwise)

  # --- Safety guardrails: avoid destructive operations in production by default ---
  safety:
    destructiveOps: false               # If true, allows explicit delete flows (normally off)
```

> Tenant namespaces are typically created/selected by the **Tenant CR** in MTO. OBX detects them automatically.

---

## 8) Using it (Platform Engineer & App Teams)

### 8.1 Annotate an app to consume secrets (ESO mode)

```yaml
metadata:
  annotations:
    mto.secrets/enable: "true"
    mto.secrets/keys:   "db,api,license"
    mto.secrets/env:    "prod"    # optional, overrides defaultEnv
```

OBX creates **ExternalSecret** objects per key which project Bao values into K8s Secrets (ESO sync).

### 8.2 Write secrets to Bao (humans via OIDC or CI bots)

```
secret/tenants/acme/prod/acme-payments/api/db
  ├─ username=...
  └─ password=...

secret/tenants/acme/prod/acme-payments/api/api
  └─ value=...
```

### 8.3 Consume in Pods

```yaml
envFrom:
  - secretRef: { name: api-db }
  - secretRef: { name: api-api }
```

> **Alternative:** Use CSI Secrets Store (`injection.mode: csi`) or call Bao directly with Kubernetes auth tokens.

---

## 9) Lifecycle — Day‑0 / Day‑1 / Day‑2

### 9.1 By Auth Backend × Scope

#### Kubernetes Auth (workloads)

* **Day‑0 (cluster):** OBX ensures `auth/kubernetes` mounted+configured (kube host & CA).
* **Day‑1 (tenant/ns/app):**

  * Policies `<tenant>-admin`/`-viewer` and namespace/app‑scoped variants.
  * Roles bound to SAs: `ten-<tenant>-ns-<ns>-rw` (namespace granularity) or per‑app roles.
  * Per‑namespace **SecretStore** for ESO.
  * On app annotation, **ExternalSecrets** are created per key.
* **Day‑2 (ops):** rotate CA/endpoint, adjust TTLs, reconcile drift, GC ExternalSecrets on opt‑out (no Bao data deletion by default).

#### Matrix

| Scope         | Day-0 (once/cluster)                                                                    | Day-1 (per tenant / ns / app)                                                                                                                                                                                                                                                                                                                   | Day-2 (ops)                                                                                                                                                      |
| ------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cluster**   | Ensure `auth/kubernetes` is mounted & configured (`kubernetes_host`, CA). Never delete. | —                                                                                                                                                                                                                                                                                                                                               | Re-sync CA/endpoint if the cluster rotates; alert on drift; optional canary reconcile.                                                                           |
| **Tenant**    | —                                                                                       | Create **policies**:<br>• `<ten>-admin` (RW under `secret/tenants/<ten>/*`)<br>• `<ten>-viewer` (RO under same)<br>Optionally ensure `transit/` & `pki/` mount prefixes for `<ten>` when enabled.                                                                                                                                               | Rotate policy templates if schema changes (no breaking deletes).                                                                                                 |
| **Namespace** | —                                                                                       | Create **roles** bound to SAs in the tenant namespace(s).<br>Role: `ten-<ten>-ns-<ns>-rw` → policy `<ten>-ns-<ns>-rw` (RW under `.../<ns>/*`).<br>Create **SecretStore** (ESO) in each tenant ns pointing to Bao with the role above.                                                                                                           | Bump TTLs, rotate role names on namespace rename, reconcile SA bindings; re-issue SecretStore on cert changes.                                                   |
| **App**       | —                                                                                       | **Opt-in** via annotations on Deployments/StatefulSets/CronJobs:<br>`mto.secrets/enable: "true"`<br>`mto.secrets/keys: "db,api,license"`<br>`mto.secrets/env: "prod\|staging\|dev"`<br>Operator generates `ExternalSecret`(s) per key mapping to the path schema. If `granularity=app`, also create an app-specific role bound to the app’s SA. | Rolling rotation of projected K8s Secrets (ESO refresh interval); handle app SA changes; GC `ExternalSecret`s on annotation removal (with a soft-delete window). |

#### OIDC/JWT Auth (humans)

* **Day‑0 (cluster):** OBX reads SSO contract → ensures `auth/oidc` (or `auth/jwt`) with `issuer`, `clientID/secret`, `groupsClaim`, `redirectURIs`.
* **Day‑1 (tenant):** Create **identity groups** `<tenant>-admins/viewers` and **group‑aliases** mapping IdP groups to these, then attach policies.
* **Day‑2 (ops):** react to client secret/JWKS rotations; support group rename migrations with grace windows.

#### Matrix

| Scope         | Day-0 (once/cluster)                                                                                                                                                        | Day-1 (per tenant / ns / app)                                                                                                                                                                                                                                                                              | Day-2 (ops)                                                                                                       |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Cluster**   | Ensure `auth/oidc` (or `auth/jwt`) mounted & configured from **SSO contract**:<br>`issuer`, `clientID`, `clientSecret`, `groupsClaim`, `redirectURIs`. Never delete mounts. | —                                                                                                                                                                                                                                                                                                          | React to SSO rotations (client secret/issuer/JWKS); reconcile safely; pause on invalid JWKS to avoid auth outage. |
| **Tenant**    | —                                                                                                                                                                           | Create **identity groups** in Bao: `<ten>-admins`, `<ten>-viewers`.<br>Create **group-aliases** mapping IdP group strings (from SSO patterns, e.g., `tenant-<ten>-admins`) **onto** those identity groups on the `oidc` mount.<br>Attach **policies** (`<ten>-admin` / `<ten>-viewer`) to identity groups. | Handle IdP group rename/migration (keep old alias for grace period); reconcile alias mount accessor changes.      |
| **Namespace** | —                                                                                                                                                                           | (No extra objects; humans inherit tenant policies.) Optional finer split: `<ten>-ns-<ns>-admins/viewers` for very large tenants.                                                                                                                                                                           | Update aliases if namespace-scoped human roles are used.                                                          |
| **App**       | —                                                                                                                                                                           | (Usually nothing.) If you run “app operators” needing human OIDC tokens, bind additional RO policies if needed.                                                                                                                                                                                            | N/A                                                                                                               |

### 9.2 Status reporting

Minimal and greppable:

```yaml
Tenant.status.integrations.openbao:
  ready: true
  kvPathPrefix: "secret/tenants/<tenant>/"
  auth:
    kubernetes:
      roles: ["ten-<tenant>-ns-<ns>-rw"]
    oidc:
      groups:
        admin: "tenant-<tenant>-admins"
        viewer: "tenant-<tenant>-viewers"
  layout: "secret/tenants/{{ .tenant }}/{{ .env }}/{{ .namespace }}/{{ .app }}/{{ .name }}"
  lastSyncTime: <RFC3339>
```

---

## 10) Operations & Security (Platform Engineer)

* **Least privilege:** use an OBX token with policy in Appendix A. Never use root.
* **No destructive defaults:** OBX creates/patches; it does not delete auth mounts nor secret data.
* **NetworkPolicies:** restrict egress to Bao from only needed namespaces.
* **KMS/etcd encryption:** enable if using ESO to encrypt K8s Secrets at rest.
* **Observability:** Prometheus metrics

  * `openbao_reconcile_seconds{kind=...,result=...}`
  * `openbao_api_requests_total{path=...,status=...}`
  * `openbao_secretstore_status{namespace=...,ready=0|1}`

### Troubleshooting

| Symptom                  | Cause                               | Fix                                                            |
| ------------------------ | ----------------------------------- | -------------------------------------------------------------- |
| SecretStore not Ready    | Bad Bao URL/CA/token                | Verify CA chain & token; check OBX logs.                       |
| OIDC login error         | Issuer/redirect mismatch            | Verify SSO contract & Bao `auth/oidc` config.                  |
| Pod `permission denied`  | SA not bound / policy path mismatch | Inspect role/policy; confirm namespace/app mode.               |
| Secrets not created      | Missing annotations/keys            | Add annotations or switch to `injection.mode: csi`/direct API. |
| Drift after SSO rotation | Client secret changed               | OBX reconciles if SecretRef used; otherwise reapply CR.        |

---

## 11) Developer Guide (How it Works)

### 11.1 Controllers (reconcilers)

* **ClusterAuthReconciler**

  * Inputs: `OpenBaoIntegration`, SSO contract (ClusterSSO/Secret)
  * Ensures: `auth/kubernetes`, `auth/oidc|jwt` config; emits clusterAuth ready status
  * Non‑destructive: never deletes mounts
* **TenantBaoReconciler**

  * Inputs: `Tenant` CR, `OpenBaoIntegration`
  * Ensures per‑tenant policies, identity groups, group‑aliases
  * For each tenant namespace: K8s auth roles + SecretStore (ESO mode)
* **AppSecretReconciler**

  * Watches: Deployments/StatefulSets/CronJobs in tenant namespaces
  * On `mto.secrets/enable: "true"`: generate/update ExternalSecrets per `mto.secrets/keys`

### 11.2 Watches & scale hygiene

* Watch **only** namespaces selected by the Tenant CR.
* Filter on relevant annotations/labels to reduce churn.
* Use **idempotent** upserts; tolerate out‑of‑order events.

### 11.3 Drift & deletion policy

* **Auth mounts:** create/patch only; never delete automatically.
* **Policies/Roles/Groups:** patch on drift; deletion behind a feature flag with safeguard (rare).
* **ExternalSecrets:** GC on annotation removal (soft‑delete window recommended).

### 11.4 Templates (renderers)

* **Policy HCL — namespace RW:**

```hcl
path "secret/data/tenants/{{tenant}}/{{env}}/{{namespace}}/*" {
  capabilities = ["create","update","patch","delete","read","list"]
}
path "secret/metadata/tenants/{{tenant}}/{{env}}/{{namespace}}/*" {
  capabilities = ["read","list","delete"]
}
```

* **Role JSON — namespace RW:**

```json
{
  "bound_service_account_names": ["*"],
  "bound_service_account_namespaces": ["{{namespace}}"],
  "policies": ["ten-{{tenant}}-ns-{{namespace}}-rw"],
  "token_ttl": "1h",
  "token_max_ttl": "4h"
}
```

* **OIDC config & role (human-default):**

```json
{
  "oidc_discovery_url": "https://dex.mto.svc.cluster.local",
  "oidc_client_id": "vault-openbao",
  "oidc_client_secret": "<from Secret>",
  "default_role": "human-default",
  "bound_issuer": "https://dex.mto.svc.cluster.local"
}
```

```json
{
  "user_claim": "email",
  "groups_claim": "groups",
  "allowed_redirect_uris": [
    "https://bao.example.com/ui/vault/auth/oidc/oidc/callback",
    "https://bao.example.com/v1/auth/oidc/oidc/callback"
  ]
}
```

### 11.5 CRD (spec) highlights

* `manageAuth.kubernetes|oidc: Off|Ensure`
* `sso.source: FromClusterSSO|FromBindingSecret|Inline`
* `layout.pathTemplate` & `defaultEnv`
* `rbac.granularity: namespace|app`
* `injection.mode: external-secrets|csi|none`
* `scaffolding.mode: None|OnAnnotation`

### 11.6 Testing strategy (TDD/e2e)

* **Unit:** golden tests for renderers (HCL/JSON) with fixtures across tenant/ns/app/env.
* **Envtest:** controller-runtime fake API server; verify SecretStore/ExternalSecrets creation on annotations.
* **Kind e2e:** spin Bao (dev), ESO, Dex (from SSO), apply OBX + Tenant; assert SA login, OIDC login, KV access.
* **Fault injection:** rotate Dex client secret & Kubernetes CA; assert non‑destructive reconcile.

### 11.7 Performance notes

* Avoid listing across all namespaces; restrict informers to tenant‑selected namespaces.
* Batch Bao API calls where safe; exponental backoff on 429/5xx.
* Metrics for reconcile duration and Bao API latency; feature flag for sampling rate.

---

## 12) Configuration Reference (Full)

See `spec` block in §7.3; all fields documented inline. Consider publishing an **OpenAPI schema** with descriptions to enable validation and UX hints.

---

## 13) Appendices

### Appendix A — OBX Bao Policy (least privilege)

```hcl
path "sys/auth"            { capabilities = ["read", "list", "update"] }
path "sys/auth/*"          { capabilities = ["read", "list", "update"] }
path "sys/policies/acl/*"  { capabilities = ["create", "read", "update", "list"] }
path "auth/*/role/*"       { capabilities = ["create", "read", "update", "list"] }
path "identity/group"      { capabilities = ["create", "read", "update", "list"] }
path "identity/group/*"    { capabilities = ["create", "read", "update", "list"] }
path "identity/group-alias"   { capabilities = ["create", "read", "update", "list"] }
path "identity/group-alias/*" { capabilities = ["create", "read", "update", "list"] }
path "secret/*"            { capabilities = ["read", "list"] }
path "secret/data/tenants/*"     { capabilities = ["create","update","patch","delete","read","list"] }
path "secret/metadata/tenants/*" { capabilities = ["read","list","delete"] }
```

### Appendix B — Annotations cheat‑sheet

```yaml
metadata:
  annotations:
    mto.secrets/enable: "true"
    mto.secrets/keys:   "db,api,license"
    mto.secrets/env:    "prod"
```

### Appendix C — Example ExternalSecret (generated)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-db
  namespace: acme-payments
spec:
  refreshInterval: 5m
  secretStoreRef: { name: openbao, kind: SecretStore }
  target: { name: api-db }
  data:
    - secretKey: username
      remoteRef:
        key: secret/tenants/acme/prod/acme-payments/api/db
        property: username
    - secretKey: password
      remoteRef:
        key: secret/tenants/acme/prod/acme-payments/api/db
        property: password
```

### Appendix D — App‑level RBAC (optional, tighter)

```hcl
path "secret/data/tenants/{{tenant}}/{{env}}/{{namespace}}/{{app}}/*" {
  capabilities = ["create","update","patch","delete","read","list"]
}
path "secret/metadata/tenants/{{tenant}}/{{env}}/{{namespace}}/{{app}}/*" {
  capabilities = ["read","list","delete"]
}
```

### Appendix E — CSI Secrets Store (outline)

* Switch `injection.mode: csi`.
* OBX renders a `SecretProviderClass` per annotated app/keys.
* Pods mount volume:

```yaml
volumes:
- name: bao-secrets
  csi:
    driver: secrets-store.csi.k8s.io
    readOnly: true
    volumeAttributes:
      secretProviderClass: <generated-name>
```

---

**Done.** One guide for both roles. Install it, annotate apps, and if you’re hacking on OBX, you’ve got the internals too.
