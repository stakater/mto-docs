# Delivery and login

Two ways people and workloads reach the secrets: External Secrets delivers them to workloads as Kubernetes `Secret`s, and human SSO lets tenant members sign in to Vault.

## Delivering secrets with External Secrets

With `parent.eso` enabled (the default), a workload gets its secret as an ordinary Kubernetes `Secret` — no Vault code in the app. Annotate the Deployment; its `serviceAccountName` must be a ServiceAccount already annotated for Vault access ([Giving an application a secret](giving-an-application-a-secret.md)).

| Annotation | Value | Reads |
|:---|:---|:---|
| `vault.stakater.com/kv-secret.<name>` | `<leaf>[#<key>]` | the app's own `<leaf>`; with `#<key>` only that key, else every key of the leaf |
| `vault.stakater.com/kv-subscribe.<name>` | `<writer-ns>/<leaf>[#<key>]` | a `_shared/` leaf of the app's own namespace, or of a subscribed one |
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

Each annotation renders an `ExternalSecret` and a `Secret` named `<serviceaccount>-<name>` (here `checkout-db`, `checkout-token`), which the pod consumes with `envFrom`/`secretKeyRef` as usual. Every annotated ServiceAccount has a `SecretStore` `<serviceaccount>-vault` that logs in as that ServiceAccount at `<tenant>/kubernetes/workloads` and reads `<tenant>/kv`; an import reads through `<serviceaccount>.share-<peer>-vault` on `shared/kv`.

A Deployment whose ServiceAccount does not grant the path gets a `vault-config-<deployment>.deploy-error` `ConfigMap` explaining why. So does one that asks for a secret while ESO is disabled install-wide. Two Deployments that ask for the same secret through one ServiceAccount share one `ExternalSecret`; two that ask for different secrets under the same name are both refused.

### Rolling pods when a secret changes

ESO reads Vault again every `parent.externalSecretRefreshInterval` (default `1h`) and updates the `Secret`. A container reads environment variables only at start, so to roll the Deployment when the `Secret` changes, add [Reloader](https://github.com/stakater/reloader)'s own annotation to it — the extension renders nothing for this:

```yaml
metadata:
  annotations:
    vault.stakater.com/kv-secret.db: "db-creds#password"
    secret.reloader.stakater.com/reload: "checkout-db"
```

!!! tip
    ESO logs in to Vault on every refresh, so a short interval across many workloads is a burst of logins. Keep the interval as long as your rotation allows.

## Human SSO

With `parent.sso.enabled=true`, each tenant gets its own OIDC auth mount `auth/<tenant>/oidc/sso` and one Vault role per entry of `sso.roles`, named `sso.<tenant>.<role>` and bound to exactly the identity-provider group `<tenant>-<role>s` (configurable with `sso.tenantGroupTemplate`). A member gets exactly the role their group grants — the same roles as workloads (`viewer`, `editor`, `admin`, `audit-read`) — across the tenant's whole `<tenant>/kv` mount, and nothing else.

```yaml
parent:
  sso:
    enabled: true
    issuerUrl: https://idp.example.com
    allowedRedirectUris:
      - http://localhost:8250/oidc/callback            # the vault CLI, the same for every tenant
      - https://vault.example.com/ui/vault/auth/{tenant}/oidc/sso/oidc/callback
tenantValues:
  sso:
    oidc:
      clientId: vault
      clientSecretRef: { name: vault-oidc-client-secret, key: client-secret }
```

All tenants share one identity-provider client, `tenantValues.sso.oidc.clientId` (default `vault`); set it to the ID of Vault's client in your IdP. It is also the audience every role accepts. `parent.sso.issuerUrl` is the issuer Vault talks to (Dex's, when Keycloak sits behind Dex). The client secret is a `Secret` in `configNamespace`, named by `sso.oidc.clientSecretRef`.

A member signs in on the tenant's mount:

```bash
vault login -method=oidc -path=acme/oidc/sso role=sso.acme.editor
```

### Redirect URIs are per tenant

Vault Community has no namespaces, so each tenant's mount has its own UI callback: `https://<vault>/ui/vault/auth/<tenant>/oidc/sso/oidc/callback`. Write it once in `parent.sso.allowedRedirectUris` with `{tenant}`, and each tenant's roles get their own.

The IdP client must allow the same URIs: one per tenant, or a wildcard where the IdP supports one. Keycloak accepts `https://<vault>/ui/vault/auth/*`. Dex has no wildcard, so its client lists every tenant's URI.

### Group patterns

`sso.tenantGroupTemplate` (default `{tenant}-{role}s`) and a per-role `sso.tenantRoleMapping.<role>.pattern` name the group that gets each role. The install fails when a pattern:

- does not hold `{tenant}` exactly once — one group would get that role in every tenant. Give platform-wide access with a Vault admin policy instead;
- can give the same group to two tenants, or to two roles of one tenant. With the default pattern, roles `audit-read` and `read` would: tenant `x` as `audit-read` and tenant `x-audit` as `read` both bind `x-audit-reads`. Put a character a tenant name cannot hold between `{tenant}` and the rest (`{tenant}.{role}`), or rename the role.

There is no fallback role: `sso.tenantRoleMapping.fallback` must stay `deny`, because a role without a group binding would give any valid token from the IdP that tenant's access.

A login refused for the group is not a 403 — Vault answers "does not match any associated bound claim values", so a user outside the tenant's groups cannot sign in to that tenant. A person removed from a group cannot log in again; a token already issued lives until its TTL (`ssoToken.ttl`, default `15m`).

---

**Previous:** [Secrets and sharing](secrets-and-sharing.md) · **Next:** [Security](security.md)
