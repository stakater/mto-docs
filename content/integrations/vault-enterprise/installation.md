# Installation

For a platform administrator: a Vault admin sets up the login VCO uses once, then you install the bootstrap chart once. There is no per-tenant installation step.

## Requirements

| | |
|:---|:---|
| Vault | **Enterprise** (tested on 2.1.1). Tenant isolation is one Vault *namespace* per tenant, and namespaces exist only in Enterprise. On Community Edition every tenant's objects land in root and collide. |
| [`vault-config-operator`](https://github.com/redhat-cop/vault-config-operator) (VCO) | **v1.0.3 or later** — the first release with `spec.authentication.targetNamespace` and the `Namespace` fix the charts rely on. |
| [Template Operator v2](../../template-operator-v2/concepts/overview.md) (`templates.v2.stakater.com`) | **Required** — the extension is configuration for it and does nothing without it. `0.0.8` recommended. |
| [Multi-Tenant Operator](../../getting-started/installation/overview.md) | the `Tenant` CRD. MTO labels each tenant namespace `stakater.com/tenant: <tenant>`; that label is what the charts key on. |
| [External Secrets Operator](https://external-secrets.io/) | only if `parent.eso` is enabled (the default) — see [Delivery and login](delivery-and-login.md). |

## Install Template Operator v2

The simplest route is to let MTO deploy it: set `components.templateOperatorV2.mode: Managed` in the `IntegrationConfig`. MTO then runs it in `multi-tenant-operator` as the ServiceAccount `tenant-operator-template-operator-v2` — the value used for `templateOperator` below. To install it yourself from its chart instead, it runs as `template-operator-v2` in `stakater-template-operator`.

## Install `vault-config-operator`

The extension renders [`vault-config-operator`](https://github.com/redhat-cop/vault-config-operator) (VCO) custom resources, so VCO must be running on the cluster — **v1.0.3 or later** (see [Requirements](#requirements)). Install it from OperatorHub or with its Helm chart, following the operator's own README. The Vault bootstrap below then sets up the Kubernetes-auth login VCO uses.

VCO logs in to Vault with the Kubernetes auth method **once**, in `vco.namespace` (empty = root), as the ServiceAccount the bootstrap chart creates. Before the chart can do anything, a Vault admin sets up that login:

```bash
vault auth enable kubernetes
vault write auth/kubernetes/config kubernetes_host=https://kubernetes.default.svc:443
vault policy write vco-admin examples/vco-admin-policy.hcl
vault write auth/kubernetes/role/vco-admin \
  bound_service_account_names=vco-admin \
  bound_service_account_namespaces=vault-config \
  token_policies=vco-admin token_ttl=1h
```

`examples/vco-admin-policy.hcl` (in the repo) is the production policy — it **denies delete** on the data-bearing paths, which is the protection described in [Operating → deletion](operating.md#deletion). `kubernetes_host` without `token_reviewer_jwt` means Vault reviews tokens with its own ServiceAccount (bound to `system:auth-delegator`, as the HashiCorp chart does by default), so no reviewer credential is stored.

!!! note "The policy grants child namespaces with a `+`"
    The policy lives in the login namespace and reaches a tenant namespace by prefixing paths with a `+` segment (e.g. `+/sys/policy/*`). That follows from how Vault matches a policy path against the full request path including the namespace.

## Install the bootstrap chart

```bash
helm upgrade --install mto-extension-vault-enterprise-bootstrap \
  oci://ghcr.io/stakater/public/charts/mto-extension-vault-enterprise-bootstrap \
  --namespace vault-config --create-namespace \
  --set parent.vaultServer=https://vault.example.com:8200 \
  --set templateOperator.serviceAccountName=tenant-operator-template-operator-v2 \
  --set templateOperator.namespace=multi-tenant-operator
```

!!! warning "The ServiceAccount must be your Template Operator v2's"
    The RBAC the chart installs binds to `templateOperator`. If it names an account that is not the one Template Operator v2 runs as, `helm install` still succeeds but nothing reconciles — the parent cannot list `Tenant`s. The values above are for an MTO-managed Template Operator v2; a standalone install uses `template-operator-v2` in `stakater-template-operator`.

Key bootstrap values — full list in [Reference](reference.md):

| Value | Default | Meaning |
|:---|:---|:---|
| `configNamespace` | `vault-config` | holds every Template, TemplateInstance and VCO CR; install the chart here |
| `vco.namespace` | `""` (root) | the Vault namespace VCO logs in to, and the parent of every tenant namespace |
| `parent.vaultServer` | — | the Vault address workloads and ESO use |
| `parent.eso` | `enabled` | `"enabled"` / `"disabled"` — a string, not a boolean |
| `tenantValues` | `{}` | any other tenant-chart value, install-wide (CA bundle, monitoring, SSO, …) |

## Verify

```bash
kubectl -n vault-config get templateinstances.templates.v2.stakater.com \
  -o custom-columns='NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status'
```

A row per tenant (plus the parent) with `READY=True`. Then confirm the Vault namespaces exist (`vault namespace list`), one per tenant.

!!! tip
    Always use the fully-qualified `templateinstances.templates.v2.stakater.com`. On OpenShift a bare `kubectl get templateinstance` returns OpenShift's own kind with an empty status — indistinguishable from "nothing is reconciling".

---

**Previous:** [Overview](overview.md) · **Next:** [Giving an application a secret](giving-an-application-a-secret.md)
