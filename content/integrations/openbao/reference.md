# Reference

## The annotation grammar

The keys follow one grammar, so you can work out a name instead of looking it up:

- `bao.stakater.com/<engine>` — turn an engine on: `kv`, `transit`, `pki`.
- `bao.stakater.com/<engine>-<verb>-<scope>` — a sharing **grant**, always on the ServiceAccount. `export` and `import` cross a tenant boundary, `subscribe` stays inside one tenant. Values are comma-separated lists.
- `bao.stakater.com/<engine>-<request>.<name>` — a delivery **request**, always on the Deployment. `<name>` becomes the Kubernetes `Secret`.
- `tier` and `app` carry no engine: they qualify the identity itself.

Grants go on the ServiceAccount, because that is the identity OpenBao authenticates. Requests go on the Deployment, because that is the workload receiving the secret. A key on the wrong object is reported as an error beside the workload rather than ignored.

### On the ServiceAccount

| Annotation | Engine | What it does |
|:---|:---|:---|
| `bao.stakater.com/tier` | all | **Required alongside any engine.** `audit-read`, `viewer`, `editor` or `admin`. |
| `bao.stakater.com/kv` | KV | `"true"` — read and write this application's own secrets path. |
| `bao.stakater.com/transit` | Transit | `"true"` — use the application, namespace and tenant encryption keys. |
| `bao.stakater.com/pki` | PKI | `"true"` — issue certificates directly from OpenBao. |
| `bao.stakater.com/app` | KV, Transit | Optional. Names the application that owns these secrets; defaults to the ServiceAccount name. |
| `bao.stakater.com/kv-subscribe-ns` | KV | Read the shared folders of other namespaces in the same tenant. |
| `bao.stakater.com/kv-export-tenant` | KV | Share secrets out to other tenants. |
| `bao.stakater.com/kv-import-tenant` | KV | Read secrets other tenants shared in. |
| `bao.stakater.com/transit-export-tenant` | Transit | Share an encryption key out to other tenants. |
| `bao.stakater.com/transit-import-tenant` | Transit | Use an encryption key another tenant shared in. |
| `bao.stakater.com/pki-allow-tenant` | PKI | Accept these tenants as inbound mTLS clients. Implies trusting their CA. |
| `bao.stakater.com/pki-trust-tenant` | PKI | Trust these tenants' server certificates when calling them, without accepting them inbound. |

### On the Deployment

Each creates a Kubernetes `Secret` named `<serviceaccount>-<name>`:

| Annotation | Reads from | Needs, on the ServiceAccount |
|:---|:---|:---|
| `bao.stakater.com/kv-secret.<name>` | this application's own path | `kv` |
| `bao.stakater.com/kv-subscribe.<name>` | a sibling namespace's shared folder | `kv-subscribe-ns` |
| `bao.stakater.com/kv-import.<name>` | another tenant's shared space | `kv-import-tenant` |

Values take the form `<leaf>[#<field>]` — with a field, only that field is copied into the `Secret`; without one, every field becomes a key. The subscribe and import forms are prefixed with the source: `team-a-api/postgres` and `team-a/creds`.

## Install values

Everything under `parent` is passed to every tenant; values outside it cover the cluster's own setup. See [Installation](installation.md).

| Value | Default | Meaning |
|:---|:---|:---|
| `parent.baoServer` | — | the OpenBao address workloads and ESO use |
| `parent.env` | `dev` | the `<env>` segment of every secret path |
| `parent.eso` | `enabled` | deliver secrets as Kubernetes `Secret`s |
| `parent.certManager.enabled` | `false` | a cert-manager `Issuer` per namespace |
| `parent.sso.enabled` / `.issuerUrl` | `false` / `""` | human login through OIDC |
| `parent.pki.roles` | — | the certificate roles tenants issue from (install-wide) |
| `platformPki` | — | the CA that signs each tenant's intermediate CA |
| `safety` | — | what deletion does |

What each tier may do is fixed by the extension and is not a value.

## See also

- **OpenBao Config Operator** — the operator that applies this configuration to OpenBao.
- [Tenant](../../concepts/tenant.md) — the resource this extension reads.
- [Vault Enterprise](../vault-enterprise/overview.md) — the equivalent for HashiCorp Vault Enterprise (KV, sharing, SSO; no transit/PKI yet).

---

**Previous:** [Operating](operating.md)
