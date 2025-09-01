# MTO OpenBao Extension

> **Goal:** Enable each MTO Tenant to use OpenBao (HashiCorp Vault–compatible) for secrets, crypto, and PKI with minimal setup. Workloads use **Kubernetes auth**; humans use **OIDC** (via your SSO extension such as Dex). The extension is **integrational**: it wires Bao to your cluster and tenants; it does **not** operate the Bao cluster itself.

---

## Who is this for?

Platform engineers running **MTO** who want: per‑tenant secret isolation, developer self‑service with **External Secrets Operator (ESO)** or **CSI Secrets Store**, and audited human access via **OIDC**.

---

## What you get

* Per‑tenant **KV v2** path prefixes (and optional **Transit/PKI** prefixes).
* Bao **policies** and **roles** enforcing least privilege by tenant/namespace/app.
* Two auth backends wired for you:
  * **Kubernetes** (workloads via ServiceAccounts).
  * **OIDC/JWT** (humans via SSO; Dex/Keycloak/Entra).
* Optional app‑level scaffolding: annotate Deployments to auto‑create **ExternalSecrets**.
* Minimal, greppable **Tenant.status** updates (ready, paths, roles, groups).

---

## Before you begin (prerequisites)

### 1) A reachable OpenBao instance

* Bao URL (e.g., `https://bao.example.com:8200`) with a **scoped management token**.
* Storage/HA, unseal, backups are **out of scope** for this extension.

**Recommended Bao policy for the operator token** (least privilege):

```hcl
# Manage specific auth mounts (create/patch but not delete)
path "sys/auth"            { capabilities = ["read", "list", "update"] }
path "sys/auth/*"          { capabilities = ["read", "list", "update"] }

# Manage policies used by tenants
path "sys/policies/acl/*"  { capabilities = ["create", "read", "update", "list"] }

# Manage roles for kubernetes & oidc mounts
path "auth/*/role/*"       { capabilities = ["create", "read", "update", "list"] }

# Identity groups & aliases for OIDC groups → Bao policies
path "identity/group"      { capabilities = ["create", "read", "update", "list"] }
path "identity/group/*"    { capabilities = ["create", "read", "update", "list"] }
path "identity/group-alias"   { capabilities = ["create", "read", "update", "list"] }
path "identity/group-alias/*" { capabilities = ["create", "read", "update", "list"] }

# Tenant KV paths only (no blanket secret powers)
path "secret/*"            { capabilities = ["read", "list"] }
path "secret/data/tenants/*"     { capabilities = ["create","update","patch","delete","read","list"] }
path "secret/metadata/tenants/*" { capabilities = ["read","list","delete"] }
```

### 2) SSO extension installed (Dex or other)

* Install **MTO SSO extension** and configure your IdP. It will publish one of:
  * **ClusterSSO** status with `issuer`, `groupsClaim`, `clients.openbao.clientID/SecretRef`, and tenant **groupPatterns**; or
  * A labeled **Secret** containing the above ("service binding" style).

### 3) (Optional) External Secrets Operator (ESO)

* If using ESO, have the CRDs/controller installed.

### 4) Kubernetes version & namespaces

* Kubernetes ≥ 1.25 (RBAC, SA tokens). Ensure your **tenant namespaces** exist or are managed by MTO.

### 5) Network / TLS

* Pods that will contact Bao must be allowed by **NetworkPolicies**.
* Bao must present a CA chain trusted by those pods (or pass CA via SecretStore spec).

---

## Quick start (TL;DR)

1. **Install the extension** (Helm or Kustomize; replace placeholders):

```bash
# Namespace for operators
kubectl create ns mto-system || true

# Helm (example)
helm upgrade --install mto-openbao-extension \
  oci://<your-registry>/mto-openbao-extension \
  -n mto-system \
  -f values.yaml
```

2. **Provide the Bao token** (scoped policy above):

```bash
kubectl -n mto-system create secret generic openbao-credentials \
  --from-literal=token=<BAO_OPERATOR_TOKEN>
```

3. **Create the integration CR** (minimal):

```yaml
apiVersion: security.mto.stakater.com/v1alpha1
kind: OpenBaoIntegration
metadata:
  name: cluster-default
  namespace: mto-system
spec:
  baseURL: https://bao.example.com:8200
  credentialsRef:
    name: openbao-credentials
  manageAuth:
    kubernetes: Ensure
    oidc: Ensure
  sso:
    source: FromClusterSSO
    ref:
      name: default
  layout:
    pathTemplate: "secret/tenants/{{ .tenant }}/{{ .env }}/{{ .namespace }}/{{ .app }}/{{ .name }}"
    defaultEnv: "prod"
  rbac:
    granularity: namespace   # or: app
  injection:
    mode: external-secrets
    secretStore:
      perNamespace: true
      nameTemplate: "openbao"
  scaffolding:
    mode: OnAnnotation
    annotations:
      enable: "mto.secrets/enable"
      keys: "mto.secrets/keys"
      env: "mto.secrets/env"
```

4. **Create or label tenant namespaces** (done by MTO Tenant CR). Ensure your tenant CR selects these namespaces.

5. **Annotate an app to consume secrets** (ESO path wiring auto‑generated):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: acme-payments
  annotations:
    mto.secrets/enable: "true"
    mto.secrets/keys: "db,api"
    mto.secrets/env: "prod"
spec:
  template:
    spec:
      serviceAccountName: api-sa
      containers:
        - name: api
          image: your/image
          envFrom:
            - secretRef: { name: api-db }    # created by ESO
            - secretRef: { name: api-api }   # created by ESO
```

6. **Put the actual secret values in Bao** (from CI or humans with OIDC):

```
# Example path schema
secret/tenants/acme/prod/acme-payments/api/db
  └─ username=…
  └─ password=…

secret/tenants/acme/prod/acme-payments/api/api
  └─ value=…
```

ESO will sync them into `api-db` and `api-api` Kubernetes Secrets.

---

## Architecture (at a glance)

```mermaid
graph TD
  subgraph Cluster
    MTO[MTO Core]
    OBX[OpenBao Extension]
    SSO[SSO Extension (Dex/Keycloak)]
    ESO[External Secrets Operator]
  end
  BAO[(OpenBao)]

  MTO -->|Tenant CR| OBX
  SSO -->|issuer + client + groupsClaim| OBX
  OBX -->|auth/kubernetes + auth/oidc + policies/roles| BAO
  ESO -->|SecretStore/ExternalSecret| BAO
  BAO -->|tokens/kv| Workloads
```

---

## How it works (Day‑0 / Day‑1 / Day‑2)

### Day‑0 (cluster bootstrap)

1. OBX (the extension) ensures Bao **auth/kubernetes** mounted & configured.
2. OBX reads SSO contract → ensures Bao **auth/oidc** (issuer, client, groups claim, role).
3. No destructive changes: mounts are created/patched, **not** deleted.

### Day‑1 (tenant onboarding)

1. For each Tenant selected namespace, OBX creates:

   * **Policies**: `<tenant>-admin`, `<tenant>-viewer`, and namespace/app scoped variants.
   * **Kubernetes auth Roles** bound to SAs in that namespace.
   * **SecretStore** (ESO) in that namespace pointing at Bao.
2. For human access, OBX creates **identity groups** and **group‑aliases** mapping IdP group names → Bao policies.
3. If **scaffolding OnAnnotation**: when apps are annotated, OBX generates **ExternalSecrets** for listed keys.

### Day‑2 (operations)

* React to SSO rotations (client secret/JWKS); patch `auth/oidc` config.
* Rotate Kubernetes CA/endpoint on cluster changes.
* Metrics: reconcile duration, Bao API latency, error codes, SecretStore health.
* Garbage‑collect ExternalSecrets on opt‑out (no Bao data deletion by default).

---

## Configuration reference (spec fields)

```yaml
spec:
  baseURL: <string>                # Bao URL
  credentialsRef:                  # Secret with .data.token
    name: openbao-credentials
    namespace: mto-system

  manageAuth:                      # What the operator manages on Bao
    kubernetes: Off|Ensure         # default: Ensure
    oidc:       Off|Ensure         # default: Ensure

  sso:
    source: FromClusterSSO|FromBindingSecret|Inline
    ref:                           # name of ClusterSSO or Secret
      name: default
    inline:                        # fallback if source=Inline
      issuer: https://dex...
      clientID: vault-openbao
      clientSecretRef:
        name: sso-openbao-client
        namespace: mto-system
      groupsClaim: groups

  layout:
    pathTemplate: "secret/tenants/{{ .tenant }}/{{ .env }}/{{ .namespace }}/{{ .app }}/{{ .name }}"
    defaultEnv: prod

  rbac:
    granularity: namespace|app     # default: namespace
    tokenTTL: 1h
    tokenMaxTTL: 4h

  injection:
    mode: external-secrets|csi|none
    secretStore:
      perNamespace: true           # create one SecretStore per tenant ns
      nameTemplate: openbao

  scaffolding:
    mode: None|OnAnnotation        # default: OnAnnotation
    annotations:
      enable: mto.secrets/enable
      keys:   mto.secrets/keys
      env:    mto.secrets/env
```

---

## Usage patterns

### A) With External Secrets Operator (recommended)

* Pros: cached K8s Secret (resilience to Bao hiccups), simple Pod consumption.
* Cons: secrets at rest in etcd (encrypted at rest recommended).

**Per‑namespace SecretStore** is created by OBX. You only **annotate apps** and **write values** in Bao.

### B) With CSI Secrets Store (no Secret at rest)

* Pros: mounts directly in Pod volumes; no Secret in etcd.
* Cons: online dependency on Bao at Pod start; different consumption model.
* OBX can provision **SecretProviderClass** templates per app/keys when `injection.mode: csi`.

### C) Direct Bao API (advanced)

* Apps call Bao with short‑lived tokens via Kubernetes auth. No ESO/CSI objects needed. You manage code‑level fetch/renew.

---

## Human access via OIDC

* Your SSO extension publishes the **issuer**, **openbao client**, and **groupsClaim**.
* OBX configures Bao `auth/oidc`, creates **identity groups** `<tenant>-admins/viewers`, and maps IdP group names via **group‑aliases**.
* Result: humans sign in to Bao UI/CLI, get policies for their tenant paths.

---

## Observability

* Controller exposes Prometheus metrics:

  * `openbao_reconcile_seconds{kind=...,result=...}`
  * `openbao_api_requests_total{path=...,status=...}`
  * `openbao_secretstore_status{namespace=...,ready=0|1}`
* Optional: emit K8s Events on auth mount/role/policy changes.

---

## Security notes

* **Operator token**: use the least‑privilege Bao policy shown above. **Do not** use root.
* **No destructive defaults**: mounts/policies are created/updated, never deleted automatically.
* **NetworkPolicies**: restrict egress to Bao endpoint from only allowed namespaces.
* **KMS/etcd encryption**: if using ESO, enable Kubernetes secrets encryption at rest.

---

## Troubleshooting

| Symptom                    | Likely cause                      | Fix                                                                       |
| -------------------------- | --------------------------------- | ------------------------------------------------------------------------- |
| `SecretStore` not Ready    | Wrong Bao URL/CA or token         | Check CA chain; rotate token; see controller logs.                        |
| OIDC login fails           | SSO issuer/redirect URIs mismatch | Verify SSO contract; update `auth/oidc/config`; confirm redirect URIs.    |
| App Secrets not created    | Missing annotations or keys       | Add `mto.secrets/enable: "true"` and list keys; confirm ESO is installed. |
| `permission denied` in Pod | SA not bound to correct Bao role  | Ensure namespace/app role exists; check policy path schema; re‑annotate.  |
| Drift after SSO rotation   | Client secret changed             | OBX reconciles automatically if using SecretRef; otherwise re‑apply CR.   |

---

## FAQ

* **Do I need Bao namespaces?** No. The extension isolates by **path + policy**. If your Bao build supports namespaces, you can nest everything in per‑tenant namespaces later.
* **Can I restrict to app‑level policies?** Yes: set `rbac.granularity: app`.
* **Will the operator delete my data?** No. ExternalSecrets may be GC’d on opt‑out; Bao data is left intact by default.
* **Do I have to use ESO?** No. You can choose `csi` or direct Bao API.

---

## Uninstall / cleanup

1. Remove or scale down the controller:

```bash
helm uninstall mto-openbao-extension -n mto-system
```

2. (Optional) Manually remove Bao objects if desired (policies, roles, groups). The extension does not auto‑delete them.

---

## Appendix A — Path schema & examples

**Template:** `secret/tenants/<tenant>/<env>/<namespace>/<app>/<name>`

**Example (tenant `acme`):**

```
secret/tenants/acme/prod/acme-payments/api/db       # username/password
secret/tenants/acme/prod/acme-payments/api/api      # value
secret/tenants/acme/staging/acme-web/fe/oauth       # client_id/secret
```

---

## Appendix B — Annotations cheat‑sheet

```yaml
metadata:
  annotations:
    mto.secrets/enable: "true"
    mto.secrets/keys:   "db,api,license"
    mto.secrets/env:    "prod"   # optional; defaults to spec.layout.defaultEnv
```

---

## Appendix C — Example ExternalSecret (generated)

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

---

## Appendix D — Example RBAC granularity (app‑level policy)

```hcl
# RW only for a single app path
path "secret/data/tenants/{{tenant}}/{{env}}/{{namespace}}/{{app}}/*" {
  capabilities = ["create","update","patch","delete","read","list"]
}
path "secret/metadata/tenants/{{tenant}}/{{env}}/{{namespace}}/{{app}}/*" {
  capabilities = ["read","list","delete"]
}
```

---

**You’re set.** Create your Tenant, annotate apps, and start writing secrets to OpenBao. The extension handles the wiring; you control the data.
