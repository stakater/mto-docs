# Migrating from the IntegrationConfig integration

The older Vault integration is configured through `IntegrationConfig.spec.integrations.vault` and reconciled by MTO itself (see [the older page](../vault/vault.md)). This extension replaces it. Both keep each tenant's secrets in a KV v2 mount at `<tenant>/kv`, so the secrets can stay where they are. The access model around them changes: per-application policies instead of one read policy per tenant, and SSO roles instead of identity groups.

!!! danger "Never set `enabled: false` on the old integration"
    Setting `integrations.vault.enabled: false` makes MTO unmount every tenant's `<tenant>/kv` engine, which **deletes the secrets in it** — the same secrets the extension serves. To turn the old integration off, delete the `vault` block from the `IntegrationConfig`; that leaves Vault as it stands.

## What changes

| | Old (`IntegrationConfig`) | This extension |
|:---|:---|:---|
| Configured in | `IntegrationConfig.spec.integrations.vault` | bootstrap chart values |
| Who reconciles | MTO's controller | Template Operator v2 and VCO, from the charts |
| Tenant's KV mount | `<tenant>/kv` | `<tenant>/kv` — the same mount |
| Workload opt-in | label `stakater.com/vault-access: "true"` on a ServiceAccount | annotations `vault.stakater.com/kv` and `vault.stakater.com/role` on a ServiceAccount |
| Workload access | `<tenant>-read` on the whole mount | one policy per app, on its own prefix, at the role it asks for |
| Workload login | `auth/kubernetes`, role `<namespace>-<tenant>-mto` | `auth/<tenant>/kubernetes/workloads`, role `kv.<tenant>.<namespace>.<sa>` |
| People | identity groups from the `Tenant`'s `accessControl` groups; Owners admin, Viewers read, Editors nothing | an OIDC mount per tenant; roles `admin`, `editor`, `viewer`, `audit-read`, each bound to an IdP group by pattern |
| Common path | one `commonSecretsPath`, shared by every tenant | directional shares in `shared/kv`, opt-in on both sides |
| Custom policies | the `policies` block | none — tenants never administer Vault; platform-wide access is a policy a Vault admin writes |
| Delivery | — | Kubernetes `Secret`s through External Secrets |
| Turning off or deleting | `enabled: false` deletes every tenant's secrets | access ends; the mount and its secrets stay until a Vault admin purges them |

## Before you start

!!! warning "Rehearse it first"
    The extension's test suite proves a fresh install. It does not run this migration. Rehearse it on a copy of your Vault before you run it in production, and take a backup of Vault's storage (with integrated storage, `vault operator raft snapshot save`).

- **Check every tenant's name.** The extension skips a tenant whose name is not a DNS label of at most 29 characters, or is reserved ([Security → what the extension validates](security.md#what-the-extension-validates)). A skipped tenant keeps its old access but gets no new access.
- **Reserve the old mounts.** Add your `commonSecretsPath` (default `common-shared-secrets`) and every other mount your Vault has to `parent.reservedPaths`.
- **Plan the IdP groups.** The old integration took group names from each `Tenant`. The extension binds each role to a group named by a pattern that holds the tenant's name, such as `{tenant}-owner-group`. If your groups do not follow such a pattern, create groups that do.

## 1. Install the extension next to the old integration

Follow [Installation](installation.md). The parent renders a mount CR for every tenant's `<tenant>/kv`. VCO finds the mount already in place and keeps it with its secrets: it creates a mount only when none exists at the path, and otherwise only tunes its config. Check both:

```bash
kubectl -n vault-config get templateinstances.templates.v2.stakater.com \
  mto-extension-vault-community-parent -o jsonpath='{.status.outputs.enginesSucceeded}'
vault kv list acme/kv          # the old secrets are still there
```

The old access keeps working while you move workloads and people.

## 2. Move each workload

The old layout is free-form (`acme/kv/db-creds`). The extension grants each app only its own prefix, `<tenant>/kv/data/<env>/<namespace>/<app>/`. For each app:

1. Annotate its ServiceAccount. `viewer` gives the read-only access it had before:

    ```yaml
    metadata:
      annotations:
        vault.stakater.com/kv: "true"
        vault.stakater.com/role: viewer
    ```

1. Copy each secret the app reads to its new path. A Vault admin, or a tenant Owner signed in through the old OIDC login, can do it:

    ```bash
    vault kv get -format=json -mount=acme/kv db-creds | jq .data.data \
      | vault kv put -mount=acme/kv dev/acme-shop/checkout/db-creds -
    ```

1. Point the app at the new values: mount the `vault-config-<serviceaccount>` `ConfigMap` ([Giving an application a secret](giving-an-application-a-secret.md)), or annotate the Deployment for delivery ([Delivery and login](delivery-and-login.md)).
1. Remove the `stakater.com/vault-access` label from the ServiceAccount.

## 3. Move people

Turn on [human SSO](delivery-and-login.md#human-sso) and map your groups to roles. For groups named like the old example's `acme-owner-group` and `acme-viewer-group`:

```yaml
tenantValues:
  sso:
    roles: [admin, viewer]
    tenantRoleMapping:
      admin:  { pattern: "{tenant}-owner-group" }
      viewer: { pattern: "{tenant}-viewer-group" }
```

Add each tenant's redirect URI to the IdP client ([redirect URIs are per tenant](delivery-and-login.md#redirect-uris-are-per-tenant)). Members then sign in on their tenant's own mount: `vault login -method=oidc -path=<tenant>/oidc/sso role=sso.<tenant>.<role>`.

## 4. Turn off the old integration

When no workload uses a `-mto` role and no person needs the old login:

1. Delete the `vault` block from the `IntegrationConfig`. **Do not set `enabled: false`.**
1. A Vault admin deletes what the old integration left. Until then, the old `<tenant>-admin` policy still lets a tenant's Owners manage `sys/mounts/<tenant>/*` — including disabling the mount — which the extension never grants:

    ```bash
    vault policy delete acme-admin
    vault policy delete acme-read
    vault list auth/kubernetes/role                       # the old roles end in -mto
    vault delete auth/kubernetes/role/acme-shop-acme-mto
    vault list identity/group/name                        # the old identity groups
    ```

    Delete the old identity groups and their aliases, any custom policies from the `policies` block, and the Vault role and policy MTO logged in with (`accessInfo.roleName`). **Do not disable `<tenant>/kv`** — the extension uses it.

1. Disable the `commonSecretsPath` mount once nothing reads it. Move a secret that one tenant gives another to a [cross-tenant share](secrets-and-sharing.md#sharing-between-tenants).
1. Delete the old secret paths in each `<tenant>/kv` once every app reads from its new path.

## Deliberate differences from the old integration

- **Workloads get least privilege.** Each app reaches its own prefix at its own role, not the whole tenant mount.
- **Editors get access.** The `editor` role is a real role, from its own group.
- **No path shared by every tenant.** Sharing is directional and both sides opt in.
- **No custom tenant policies.** On Community Edition the policy is the only wall between tenants, so only the extension writes tenant policies.
- **Data outlives the tenant.** Deleting a tenant, or the extension, never deletes secrets; a Vault admin purges them ([Operating → deletion](operating.md#deletion)).

---

**Previous:** [Reference](reference.md)
