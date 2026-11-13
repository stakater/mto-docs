# Reference

The full, commented reference is the charts' own docs ([`charts/README.md`](https://github.com/stakater/mto-extension-vault-community/blob/main/charts/README.md) and each `values.yaml`). This page covers what you reach for most.

## Bootstrap chart values

| Value | Default | Meaning |
|:---|:---|:---|
| `configNamespace` | `vault-config` | holds every Template, TemplateInstance and VCO CR; install the chart here |
| `templateOperator.serviceAccountName` / `.namespace` | `template-operator-template-operator-v2` / `stakater-template-operator` | Template Operator v2's identity — always set it to match your install; the default matches neither an MTO-managed nor a chart install ([Installation](installation.md#install-template-operator-v2)) |
| `vco.authPath` / `vco.role` / `vco.serviceAccount` | `kubernetes` / `vco-admin` / `vco-admin` | how VCO logs in; must match the Vault bootstrap. There is no `vco.namespace` |
| `kubernetesAuth.path` / `.name` | `kubernetes` / `workloads` | each tenant's workload auth mount, `auth/<tenant>/kubernetes/workloads`; change the VCO policy with it ([Installation](installation.md#set-up-the-vault-login-for-vco)) |
| `kubernetesAuth.tokenReviewerServiceAccount` | `""` | set only when Vault runs outside the cluster |
| `parent.env` | `dev` | the `<env>` segment of KV paths |
| `parent.vaultServer` | `http://vault.vault.svc.cluster.local:8200` | the Vault address in ConfigMaps and SecretStores |
| `parent.sharedTenantName` | `shared` | the prefix of the shared mount `shared/kv`; a reserved tenant name |
| `parent.reservedPaths` | `secret`, `kv`, `pki`, `transit`, `database`, `ssh`, `totp`, `oidc`, `jwt`, `userpass`, `approle`, `ldap` | your platform's own mount prefixes; tenants with these names are skipped |
| `parent.eso` | `enabled` | `"enabled"` / `"disabled"` — a string, not a boolean |
| `parent.externalSecretRefreshInterval` | `1h` | how often ESO reads Vault again |
| `parent.token` | `{}` | workload token `type` / `ttl` / `maxTTL`, **integer seconds**; unset sides take the tenant chart's defaults (`ttl` 3600, `maxTTL` 14400) |
| `parent.sso.enabled` / `.issuerUrl` | `false` / `""` | human SSO ([Delivery and login](delivery-and-login.md#human-sso)); `enabled=true` needs `issuerUrl` |
| `parent.sso.allowedRedirectUris` | the Vault CLI's `http://localhost:8250/oidc/callback` | redirect URIs; `{tenant}` stands for each tenant's name |
| `tenantChart.registry` / `.version` | `oci://ghcr.io/stakater/charts` / chart version | where Template Operator v2 pulls the tenant chart |
| `tenantChart.authSecretName` | `""` | a `Secret` in `configNamespace` with registry credentials |
| `tenantValues` | `{}` | any other tenant-chart value, install-wide — see below |
| `sync.mode` | `revert` | drift protection for everything rendered: `off`, `revert` or `strict` |
| `admission.enabled` | `true` | the admission policies; turn off only on a cluster older than Kubernetes 1.30 ([Security](security.md#the-admission-policies)) |

`tenantValues` is the only way to set a tenant-chart value on a cluster (Template Operator v2 pulls the **published** tenant chart, so editing its `values.yaml` locally has no effect). Common keys: `vaultCABundle`, `monitoring.enabled`, `monitoring.prometheusNamespace`, `sso.oidc.clientId`, `sso.oidc.clientSecretRef`, `sso.roles`, `sso.tenantGroupTemplate`, `sso.tenantRoleMapping`, `roleCaps`, `ssoToken.ttl` / `.maxTTL`. A key the bootstrap already sets is refused, naming the value to use instead.

## Workload annotations (on a ServiceAccount)

| Annotation | Value | Effect |
|:---|:---|:---|
| `vault.stakater.com/kv` | `"true"` | the app's own KV prefix |
| `vault.stakater.com/role` | `viewer` \| `editor` \| `admin` \| `audit-read` | required with `kv`; how much access |
| `vault.stakater.com/app` | name | the app that owns the prefix (default: the ServiceAccount name) |
| `vault.stakater.com/kv-subscribe-ns` | CSV of namespaces | read the `_shared/` prefix of those sibling namespaces |
| `vault.stakater.com/kv-export-tenant` | CSV of tenants | write `shared/kv/…/from-<own>/to-<peer>/` |
| `vault.stakater.com/kv-import-tenant` | CSV of tenants | read `shared/kv/…/from-<peer>/to-<own>/` |

## Delivery annotations (on a Deployment, ESO enabled)

| Annotation | Value | Reads |
|:---|:---|:---|
| `vault.stakater.com/kv-secret.<name>` | `<leaf>[#<key>]` | the app's own `<leaf>` |
| `vault.stakater.com/kv-subscribe.<name>` | `<writer-ns>/<leaf>[#<key>]` | a subscribed `_shared/` leaf |
| `vault.stakater.com/kv-import.<name>` | `<peer>/<leaf>[#<key>]` | an imported cross-tenant leaf |

Each renders an `ExternalSecret` and `Secret` named `<serviceaccount>-<name>`. The Deployment's `serviceAccountName` must be an annotated ServiceAccount that grants the path.

## The workload `ConfigMap`

`vault-config-<serviceaccount>`, in the workload's namespace. The keys are the Vault Enterprise extension's:

| Key | Value on Community Edition |
|:---|:---|
| `VAULT_ADDR` | `parent.vaultServer` |
| `VAULT_CACERT` | `/etc/vault/ca/ca.crt`, only with `tenantValues.vaultCABundle` set; mount the `ConfigMap` `vault-ca-bundle` there |
| `VAULT_NAMESPACE` | `""` — Community Edition has none |
| `VAULT_K8S_MOUNT` | `<tenant>/kubernetes/workloads` |
| `VAULT_K8S_ROLE` | `kv.<tenant>.<namespace>.<serviceaccount>` |
| `VAULT_KV_APP` | the app's name |
| `VAULT_KV_APP_PATH` | `<tenant>/kv/data/<env>/<namespace>/<app>/` |
| `VAULT_KV_APP_META_PATH` | `<tenant>/kv/metadata/<env>/<namespace>/<app>/` |
| `VAULT_KV_SHARED_OUT_PATH` | the namespace's `_shared/from-<namespace>/` path |
| `VAULT_FROM_<NS>_PATH` | one per subscription |
| `VAULT_OUT_<PEER>_NAMESPACE` / `_ROLE` / `_PATH` | one set per export; `_NAMESPACE` is `""` |
| `VAULT_IN_<PEER>_NAMESPACE` / `_ROLE` / `_PATH` | one set per import; `_NAMESPACE` is `""` |

## Vault paths per tenant

| Object | Path |
|:---|:---|
| KV v2 mount | `<tenant>/kv` |
| workload auth mount | `auth/<tenant>/kubernetes/workloads` |
| SSO auth mount | `auth/<tenant>/oidc/sso` |
| cross-tenant shares | `shared/kv/data/<env>/from-<tenant>/to-<peer>/` |

## Not supported yet

Transit (encryption) and PKI (certificates) engines, and cert-manager integration. A `transit` or `pki` annotation is rejected with an error `ConfigMap`. For those, use the **[OpenBao](../openbao/overview.md) extension**, which covers transit and PKI.

## One release per cluster, one cluster per Vault

Install the bootstrap chart once per cluster, into `configNamespace`. The parent reads the one cluster-wide `IntegrationConfig` and the object names are fixed, so a second release collides. Connect one cluster to each Vault: tenant mounts are named by tenant alone, so two clusters would write the same tenant's auth config. A tenant's KV mount is rendered by the parent and lives as long as the `Tenant`.

---

**Previous:** [Operating](operating.md) · **Next:** [Migrating](migrating.md)
