# Reference

The full, commented reference is the charts' own docs ([`charts/README.md`](https://github.com/stakater/mto-extension-vault-enterprise/blob/main/charts/README.md) and each `values.yaml`). This page covers what you reach for most.

## Bootstrap chart values

| Value | Default | Meaning |
|:---|:---|:---|
| `configNamespace` | `vault-config` | holds every Template, TemplateInstance and VCO CR; install the chart here |
| `templateOperator.serviceAccountName` / `.namespace` | `template-operator-v2` / `stakater-template-operator` | Template Operator v2's identity — set to match your install ([Installation](installation.md)) |
| `vco.authPath` / `vco.role` / `vco.serviceAccount` | `kubernetes` / `vco-admin` / `vco-admin` | how VCO logs in; must match the Vault bootstrap |
| `vco.namespace` | `""` (root) | the Vault namespace VCO logs in to, and the parent of every tenant namespace |
| `kubernetesAuth.path` / `.name` | `kubernetes` / `workloads` | the workload auth mount inside each tenant namespace (`kubernetes/workloads`) |
| `parent.env` | `dev` | the `<env>` segment of KV paths |
| `parent.vaultServer` | — | the Vault address in ConfigMaps and SecretStores |
| `parent.eso` | `enabled` | `"enabled"` / `"disabled"` — a string, not a boolean |
| `parent.token` | `{}` | workload token `type` / `ttl` / `maxTTL`, **integer seconds** |
| `parent.sso.enabled` / `.issuerUrl` | `false` / `""` | human SSO ([Delivery and login](delivery-and-login.md#human-sso)); `enabled=true` needs `issuerUrl` |
| `tenantChart.registry` / `.version` | `oci://ghcr.io/stakater/public/charts` / chart version | where Template Operator v2 pulls the tenant chart |
| `tenantValues` | `{}` | any other tenant-chart value, install-wide — see below |
| `sync.mode` | `revert` | drift protection for everything rendered |

`tenantValues` is the only way to set a tenant-chart value on a cluster (Template Operator v2 pulls the **published** tenant chart, so editing its `values.yaml` locally has no effect). Common keys: `vaultCABundle`, `monitoring.enabled`, `sso.oidc.clientId`, `sso.roles`, `sso.tenantGroupTemplate`. A key the bootstrap already sets is refused, naming the value to use instead.

## Workload annotations (on a ServiceAccount)

| Annotation | Value | Effect |
|:---|:---|:---|
| `vault.stakater.com/kv` | `"true"` | the app's own KV prefix |
| `vault.stakater.com/role` | `viewer` \| `editor` \| `admin` \| `audit-read` | required with `kv`; how much access |
| `vault.stakater.com/app` | name | the app that owns the prefix (default: the ServiceAccount name) |
| `vault.stakater.com/kv-subscribe-ns` | CSV of namespaces | read the `_shared/` prefix of those sibling namespaces |
| `vault.stakater.com/kv-export-tenant` | CSV of tenants | write `from-<own>/to-<peer>/` in the shared namespace |
| `vault.stakater.com/kv-import-tenant` | CSV of tenants | read `from-<peer>/to-<own>/` in the shared namespace |

## Delivery annotations (on a Deployment, ESO enabled)

| Annotation | Value | Reads |
|:---|:---|:---|
| `vault.stakater.com/kv-secret.<name>` | `<leaf>[#<key>]` | the app's own `<leaf>` |
| `vault.stakater.com/kv-subscribe.<name>` | `<writer-ns>/<leaf>[#<key>]` | a subscribed `_shared/` leaf |
| `vault.stakater.com/kv-import.<name>` | `<peer>/<leaf>[#<key>]` | an imported cross-tenant leaf |

Each renders an `ExternalSecret` and `Secret` named `<serviceaccount>-<name>`. The Deployment's `serviceAccountName` must be an annotated ServiceAccount that grants the path.

## Not supported yet

Transit (encryption) and PKI (certificates) engines, and cert-manager integration. For those, see the [OpenBao extension](../openbao/overview.md), which covers transit and PKI.

## One release per cluster

Install the bootstrap chart once per cluster, into `configNamespace`. The parent reads the one cluster-wide `IntegrationConfig` and the object names are fixed, so a second release collides. A tenant's Vault namespace and KV mount are rendered by the parent and live as long as the `Tenant`.

---

**Previous:** [Operating](operating.md)
