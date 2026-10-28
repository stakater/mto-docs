# Installation

Done once per cluster, by a platform administrator, before any tenant gets an OpenBao namespace. There is no per-tenant installation step.

## Prerequisites

- An **OpenBao server** reachable from the cluster.
- [Template Operator v2](../../template-operator-v2/concepts/overview.md) (`templates.v2.stakater.com`) and the [**OpenBao Config Operator**](https://github.com/stakater/openbao-config-operator) — the extension renders objects for them and does nothing without them.
- [External Secrets Operator](https://external-secrets.io/), while secrets are delivered as Kubernetes `Secret`s (the default).
- [cert-manager](https://cert-manager.io/) to issue certificates through Kubernetes, and [trust-manager](https://cert-manager.io/docs/trust/trust-manager/) for trust between tenants.
- An OIDC identity provider, for human login.

MTO labels each tenant namespace `stakater.com/tenant=<tenant-name>`, and the extension uses that label to find them.

## Install Template Operator v2

The simplest route is to let MTO deploy it: set `components.templateOperatorV2.mode: Managed` in the `IntegrationConfig`. MTO then runs it in `multi-tenant-operator` as the ServiceAccount `tenant-operator-template-operator-v2`.

## Install the OpenBao Config Operator

The [OpenBao Config Operator](https://github.com/stakater/openbao-config-operator) applies to OpenBao the custom resources the extension renders. Install it once per cluster.

On plain Kubernetes, apply the release manifest (server-side, because the bundled CRDs are large):

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/stakater/openbao-config-operator/v0.0.6/dist/install.yaml
```

It runs in the `openbao-config-operator-system` namespace. On OpenShift, install it from its OLM catalog instead — a `CatalogSource` and a `Subscription`; see the operator's [deployment guide](https://github.com/stakater/openbao-config-operator/blob/main/DEPLOY.md).

The operator holds no OpenBao token: it authenticates with its own ServiceAccount through the one-time bootstrap in [Give the operator its own credentials](#give-the-operator-its-own-credentials) below.

## Enable the extension

The extension is installed once per cluster with Helm; it watches `Tenant` resources cluster-wide and renders one set of configuration per tenant, which the OpenBao Config Operator applies.

A tenant is picked up once its spec lists at least one namespace under `withTenantPrefix` or `withoutTenantPrefix`. The check reads those two fields and nothing else: sandboxes do not count, and neither do namespaces attached by label alone — a `Tenant` listing none is skipped, silently, even when labelled namespaces exist. Add one and it is picked up on the next render.

Everything under `parent` is passed to every tenant — this is where you point the cluster at your OpenBao server and choose which features are on:

```yaml
parent:
  baoServer: https://openbao.openbao.svc.cluster.local:8200
  env: dev                    # a segment in every secret path, so one server can hold several environments
  eso: enabled                # deliver secrets as Kubernetes Secrets
  certManager:
    enabled: false            # cert-manager Issuers per namespace
  sso:
    enabled: false            # human login through OIDC
    issuerUrl: ""
```

Values outside `parent` cover the cluster's own setup rather than the tenants': `platformPki` for the certificate authority that signs each tenant's CA, and `safety` for what deletion does. The certificate roles tenants issue from are install-wide too, under `parent.pki.roles`. What each tier may do is fixed by the extension and is not a value.

## Give the operator its own credentials

The OpenBao Config Operator authenticates to OpenBao with its own Kubernetes ServiceAccount and stores no token anywhere. This needs a one-time bootstrap per OpenBao server: an auth mount for the cluster, a policy covering what the operator manages, and a role binding that policy to the operator's ServiceAccount.

!!! warning
    Never give the operator OpenBao's root token. In production, set `baoServer` to an `https://` address, and set `baoCABundle` if OpenBao serves with a private CA.

## Verify

```bash
kubectl -n openbao-config-operator-system \
  get templateinstances.templates.v2.stakater.com openbao-config-mto-parent \
  -o jsonpath='{.status.outputs.tiReady}' | jq .
```

Anything other than `True` for a tenant means its configuration did not reach OpenBao — see [Operating](operating.md). Then confirm the OpenBao namespaces exist, one per tenant.

!!! tip
    Always use the fully-qualified `templateinstances.templates.v2.stakater.com`. On OpenShift a bare `kubectl get templateinstance` returns OpenShift's own kind with an empty status.

---

**Previous:** [Overview](overview.md) · **Next:** [Giving an application a secret](giving-an-application-a-secret.md)
