# Installation

For a platform administrator: a Vault admin sets up the login VCO uses once, then you install the bootstrap chart once. There is no per-tenant installation step.

## Requirements

| | |
|:---|:---|
| Vault | **Community Edition** 2.x (tested on 2.1.1). On Vault Enterprise, use the [Vault Enterprise](../vault-enterprise/overview.md) extension. |
| One cluster per Vault | Each tenant's auth mount is configured for this cluster's API and CA. A second cluster that writes the same tenant's auth config would let its workloads log in as this cluster's. |
| [`vault-config-operator`](https://github.com/redhat-cop/vault-config-operator) (VCO) | **v1.0.3 or later**, with drift detection on and a short sync period — see [below](#install-vault-config-operator). |
| [Template Operator v2](../../template-operator-v2/concepts/overview.md) (`templates.v2.stakater.com`) | **Required**, 0.0.5 or later (the extension's tests run 0.0.7) — the extension is configuration for it and does nothing without it. |
| Kubernetes | **1.30 or later**, for the `ValidatingAdmissionPolicy` objects the bootstrap chart installs ([Security](security.md#the-admission-policies)). |
| [Multi-Tenant Operator](../../getting-started/installation/overview.md) | the `Tenant` CRD. MTO labels each tenant namespace `stakater.com/tenant: <tenant>`; that label is what the charts key on. |
| [External Secrets Operator](https://external-secrets.io/) | only if `parent.eso` is enabled (the default) — see [Delivery and login](delivery-and-login.md). |

## Install Template Operator v2

The simplest route is to let MTO deploy it: set `components.templateOperatorV2.mode: Managed` in the `IntegrationConfig`. MTO then runs it in `multi-tenant-operator` as the ServiceAccount `tenant-operator-template-operator-v2` — the value used for `templateOperator` below. To install it yourself from its chart instead, release it as `template-operator-v2` in `stakater-template-operator`; it then runs as the ServiceAccount `template-operator-v2`. The bootstrap chart's default, `template-operator-template-operator-v2`, matches neither, so always set `templateOperator`.

To see which ServiceAccount your Template Operator v2 runs as:

```bash
kubectl get pods -A -o custom-columns='NAMESPACE:.metadata.namespace,SERVICEACCOUNT:.spec.serviceAccountName' \
  | grep template-operator
```

## Install `vault-config-operator`

The extension renders VCO custom resources, so VCO must be running on the cluster — **v1.0.3 or later**. Install it from OperatorHub or with its Helm chart, following the operator's own README, with these environment variables on the operator:

```yaml
env:
  - name: ENABLE_DRIFT_DETECTION
    value: "true"
  - name: SYNC_PERIOD_SECONDS
    value: "300"        # minutes, not the VCO default of 10 hours
  - name: CACHE_VAULT_TOKEN
    value: "true"
```

- **Drift detection and a short sync period** put back a policy that someone changed by hand in Vault. On Community Edition the policy is the only wall between tenants, so a policy widened by hand must not stay wide for hours.
- **`CACHE_VAULT_TOKEN`** makes VCO reuse and renew one Vault token. Without it, VCO logs in again on every reconcile, and with drift detection that piles up live tokens in Vault.

## Set up the Vault login for VCO

VCO logs in to Vault with the Kubernetes auth method as the ServiceAccount the bootstrap chart creates. Before the chart can do anything, a Vault admin sets up that login:

```bash
curl -fsSLO https://raw.githubusercontent.com/stakater/mto-extension-vault-community/main/charts/examples/vco-admin-policy.hcl

vault auth enable kubernetes
vault write auth/kubernetes/config kubernetes_host=https://kubernetes.default.svc:443
vault policy write vco-admin vco-admin-policy.hcl
vault write auth/kubernetes/role/vco-admin \
  bound_service_account_names=vco-admin \
  bound_service_account_namespaces=vault-config \
  token_policies=vco-admin token_ttl=1h
```

[`vco-admin-policy.hcl`](https://github.com/stakater/mto-extension-vault-community/blob/main/charts/examples/vco-admin-policy.hcl) is the production policy. It limits VCO **by name and by mount type**:

- policies only in the extension's three name families, `kv.`, `share.` and `sso.`;
- roles only on the extension's mounts, and never on the VCO login mount `auth/kubernetes`;
- KV mounts **without `delete`**, so deleting a tenant keeps its secrets — see [Operating → deletion](operating.md#deletion);
- the type of every mount fixed, so VCO cannot mount another kind of engine.

`kubernetes_host` without `token_reviewer_jwt` means Vault reviews tokens with its own ServiceAccount (bound to `system:auth-delegator`, as the HashiCorp chart does by default), so no reviewer credential is stored.

!!! warning "The VCO token is still close to root"
    Vault Community has no namespace to contain what a `kv.*` policy grants, so the VCO policy limits the *names* it can write, not what those policies *contain*. Treat the VCO identity as a Vault admin: nobody but VCO may create tokens for the ServiceAccount `vault-config/vco-admin` or exec into the VCO pod. What VCO is *asked* to write is checked by the [admission policies](security.md#the-admission-policies).

!!! note "The first segment of the VCO login mount is a reserved tenant name"
    Every tenant's auth mounts start with the tenant's name, and Vault refuses an auth mount nested under another. With VCO logging in at `auth/kubernetes`, a tenant named `kubernetes` is skipped.

!!! note "Other mount paths"
    The policy names the default mounts: the workload mount `kubernetes/workloads` and the SSO mount `oidc/sso`. If you change `kubernetesAuth.path`/`.name` or the SSO mount, change the policy with them: replace every `kubernetes/workloads` with `<kubernetesAuth.path>/<kubernetesAuth.name>` and every `oidc/sso` with the SSO mount's `<path>/<name>`. Change nothing else. Until you do, VCO is denied every tenant's auth mounts.

## Install the bootstrap chart

```bash
helm upgrade --install mto-extension-vault-community-bootstrap \
  oci://ghcr.io/stakater/charts/mto-extension-vault-community-bootstrap \
  --namespace vault-config --create-namespace \
  --set parent.vaultServer=https://vault.example.com:8200 \
  --set templateOperator.serviceAccountName=tenant-operator-template-operator-v2 \
  --set templateOperator.namespace=multi-tenant-operator
```

!!! warning "The ServiceAccount must be your Template Operator v2's"
    The RBAC the chart installs binds to `templateOperator`. If it names an account that is not the one Template Operator v2 runs as, `helm install` still succeeds but nothing reconciles — the parent cannot list `Tenant`s. The values above are for an MTO-managed Template Operator v2.

!!! warning "List your own mounts before the first install"
    Every tenant's mounts start with its name, so a tenant named like a mount your platform already has (`secret`, `pki`, …) cannot get its own. The parent skips tenant names in `parent.reservedPaths`, which has common defaults. It cannot read Vault's mount tables, so add every other secrets or auth mount prefix your Vault has.

Key bootstrap values — full list in [Reference](reference.md):

| Value | Default | Meaning |
|:---|:---|:---|
| `configNamespace` | `vault-config` | holds every Template, TemplateInstance and VCO CR; install the chart here |
| `parent.vaultServer` | `http://vault.vault.svc.cluster.local:8200` | the Vault address workloads and ESO use |
| `parent.reservedPaths` | `secret`, `kv`, `pki`, `transit`, … | your platform's own mount prefixes; tenants with these names are skipped |
| `parent.eso` | `enabled` | `"enabled"` / `"disabled"` — a string, not a boolean |
| `tenantValues` | `{}` | any other tenant-chart value, install-wide (CA bundle, monitoring, SSO, …) |

There is no `vco.namespace`: Community Edition has one namespace, and VCO logs in to it.

## Verify

```bash
kubectl -n vault-config get templateinstances.templates.v2.stakater.com \
  -o custom-columns='NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status'
```

A row for the parent, and one or two per tenant that has a labelled namespace (`mto-extension-vault-community-<tenant>`, plus `….eso` with ESO on), all with `READY=True`. Then confirm the mounts exist in Vault: `vault secrets list` shows `<tenant>/kv/` for every tenant, and `shared/kv/`.

A tenant that is missing may have been skipped — see [Operating → troubleshooting](operating.md#troubleshooting).

!!! tip
    Always use the fully-qualified `templateinstances.templates.v2.stakater.com`. On OpenShift a bare `kubectl get templateinstance` returns OpenShift's own kind with an empty status — indistinguishable from "nothing is reconciling".

## Check Vault itself

The charts call no Vault API themselves, so these checks are yours. Run them once after the install, and again after any change to Vault made outside the extension:

```bash
# Vault is Community Edition: the version has no +ent suffix.
vault status -format=json | jq -r .version
# The VCO policy is the production one, unchanged.
diff <(vault policy read vco-admin) vco-admin-policy.hcl
# Every tenant token carries the default policy, so an edit to it reaches every tenant.
vault policy read default
```

Compare the `default` policy with the one in a fresh Vault of the same version (`vault server -dev`).

---

**Previous:** [Overview](overview.md) · **Next:** [Giving an application a secret](giving-an-application-a-secret.md)
