# Secrets and sharing

Each application has its own KV prefix. Sharing is opt-in: within a tenant through a `_shared/` space, and between tenants through directional export/import.

## The KV layout

Inside the tenant's `<tenant>/kv` mount:

```text
<tenant>/kv/data/<env>/<namespace>/<app>/...          an app's own secrets
<tenant>/kv/data/<env>/_shared/from-<namespace>/...   written by that namespace's editor/admin apps,
                                                      read by every app there and by subscribers
```

`<env>` is `parent.env` (default `dev`). In the Vault UI, open the `acme/kv` mount: tenant `acme` with namespace `acme-shop` shows one folder per namespace plus `_shared/`.

## Sharing within a tenant

An editor or admin app writes to its namespace's `_shared/from-<namespace>/` space automatically. Another app reads it by subscribing, with an annotation on its ServiceAccount:

```yaml
metadata:
  annotations:
    vault.stakater.com/kv: "true"
    vault.stakater.com/role: viewer
    vault.stakater.com/kv-subscribe-ns: acme-shop    # CSV of writer namespaces
```

Put on a ServiceAccount in `acme-tools`, this lets that app read `acme-shop`'s shared space (and that of any other namespace it subscribes to). A subscription is read-only on both the data and the metadata path, so a subscriber cannot change `max_versions` and destroy the writer's versions. A namespace outside the tenant cannot be subscribed to.

## Sharing between tenants

Cross-tenant sharing is directional and opt-in on both sides. The writer exports to a peer; the reader imports from a peer. The data lives in the shared mount `shared/kv`, in neither tenant's own mount.

```yaml
# a ServiceAccount in tenant acme — may write to team-b's inbox
metadata:
  annotations:
    vault.stakater.com/kv: "true"
    vault.stakater.com/role: editor
    vault.stakater.com/kv-export-tenant: team-b       # CSV of peer tenants
---
# a ServiceAccount in tenant team-b — may read what acme sent
metadata:
  annotations:
    vault.stakater.com/kv: "true"
    vault.stakater.com/role: viewer
    vault.stakater.com/kv-import-tenant: acme          # CSV of peer tenants
```

`acme` writes to `shared/kv/data/<env>/from-acme/to-team-b/` and `team-b` reads it. The share roles live on each tenant's own auth mount, so a share login uses `VAULT_K8S_MOUNT` like any other; the role and path for each peer are in the app's `ConfigMap` (`VAULT_OUT_<PEER>_ROLE`/`_PATH`, `VAULT_IN_<PEER>_ROLE`/`_PATH`). Offboarding a tenant disables its auth mount, which revokes its share tokens too.

A share to a tenant that does not exist yet renders nothing, and appears when that tenant does. Because the share lives in the shared mount, deleting a tenant never deletes it — see [Operating → deletion](operating.md#deletion).

## Names

The extension names each policy and role by joining parts with dots:

| Family | Name | For |
|:---|:---|:---|
| `kv.` | `kv.<tenant>.<namespace>.<serviceaccount>` | an app's own access |
| `share.` | `share.<tenant>.<namespace>.<serviceaccount>.out.<peer>` / `.in.<peer>` | an export or an import |
| `sso.` | `sso.<tenant>.<role>` | a human SSO role |

None of the parts may contain a dot (tenant names are checked), so two different sets of parts can never collide. Every name starts with the tenant, because on Community Edition all tenants' policies and roles share one Vault namespace. You do not write these names; they are shown here so you recognise them in Vault.

---

**Previous:** [Giving an application a secret](giving-an-application-a-secret.md) · **Next:** [Delivery and login](delivery-and-login.md)
