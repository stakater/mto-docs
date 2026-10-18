# Delivery and login

Two ways people and workloads reach the secrets: External Secrets delivers them to workloads as Kubernetes `Secret`s, and human SSO lets tenant members sign in to the Vault UI.

## Delivering secrets with External Secrets

With `parent.eso` enabled (the default), a workload gets its secret as an ordinary Kubernetes `Secret` — no Vault code in the app. Annotate the Deployment; its `serviceAccountName` must be a ServiceAccount already annotated for Vault access ([Giving an application a secret](giving-an-application-a-secret.md)).

| Annotation | Value | Reads |
|:---|:---|:---|
| `vault.stakater.com/kv-secret.<name>` | `<leaf>[#<key>]` | the app's own `<leaf>` |
| `vault.stakater.com/kv-subscribe.<name>` | `<writer-ns>/<leaf>[#<key>]` | a subscribed `_shared/` leaf |
| `vault.stakater.com/kv-import.<name>` | `<peer>/<leaf>[#<key>]` | an imported cross-tenant leaf |

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  namespace: acme-shop
  annotations:
    vault.stakater.com/kv-secret.db: db-creds          # whole leaf -> Secret
    vault.stakater.com/kv-secret.token: api#token       # one key of a leaf
spec:
  template:
    spec:
      serviceAccountName: checkout
```

Each annotation renders an `ExternalSecret` and a `Secret` named `<serviceaccount>-<name>` (here `checkout-db`, `checkout-token`), which the pod consumes with `envFrom`/`secretKeyRef` as usual. A Deployment whose ServiceAccount does not grant the path gets a `vault-config-<deployment>.deploy-error` `ConfigMap` explaining why.

!!! tip
    A rotated value in Vault flows to the `Secret` on the next ESO refresh. Pair it with [Reloader](https://github.com/stakater/reloader) to roll the pods automatically.

## Human SSO

`parent.sso.enabled=true` with `parent.sso.issuerUrl` gives each tenant an OIDC mount `oidc/sso` and one Vault role per entry of `sso.roles`, bound to the identity-provider group `<tenant>-<role>s` (configurable with `sso.tenantGroupTemplate`). A member logs in to the tenant's Vault namespace and gets exactly the role their group grants — the same roles as workloads (`viewer`, `editor`, `admin`, `audit-read`):

```bash
VAULT_NAMESPACE=<vco.namespace>/acme \
  vault login -method=oidc -path=oidc/sso role=sso.acme.editor
```

All tenants share one identity-provider client, `tenantValues.sso.oidc.clientId` (default `vault`); set it to the ID of Vault's client in your IdP. `parent.sso.issuerUrl` is the issuer Vault talks to (Dex's, when Keycloak sits behind Dex). The client secret is a `Secret` `vault-oidc-client-secret` (key `client-secret`) in `configNamespace`.

A login refused for the group is not a 403 — Vault answers "does not match any associated bound claim values", so a user outside the tenant's groups simply cannot sign in to that namespace.

---

**Previous:** [Secrets and sharing](secrets-and-sharing.md) · **Next:** [Security](security.md)
