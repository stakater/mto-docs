# Secrets and sharing

Each application has its own KV prefix. Sharing is opt-in: within a tenant through a `_shared/` space, and between tenants through directional export/import.

## The KV layout

Inside the tenant's `kv/` mount:

```text
kv/data/<env>/<namespace>/<app>/...          an app's own secrets
kv/data/<env>/_shared/from-<namespace>/...   written by that namespace's editor/admin apps,
                                             read by every app there and by subscribers
```

`<env>` is `parent.env` (default `dev`). In the Vault UI, tenant `acme` with namespace `acme-shop` shows one folder per namespace plus `_shared/`.

## Sharing within a tenant

An editor or admin app writes to its namespace's `_shared/from-<namespace>/` space automatically. Another app reads it by subscribing, with an annotation on its ServiceAccount:

```yaml
metadata:
  annotations:
    vault.stakater.com/kv: "true"
    vault.stakater.com/role: viewer
    vault.stakater.com/kv-subscribe-ns: acme-tools    # CSV of writer namespaces
```

`acme-tools`'s apps can then read `acme-shop`'s shared space (and any other namespace they subscribe to), read-only. A namespace always shares with the tenant's other namespaces; the subscription is how a reader opts in.

## Sharing between tenants

Cross-tenant sharing is directional and opt-in on both sides. The writer exports to a peer; the reader imports from a peer. The data lives in a shared Vault namespace, not in either tenant's.

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

`acme` writes to `from-acme/to-team-b/` and `team-b` reads it. A peer named in an export/import must actually exist (have a labelled namespace), or the entry is skipped. Because the share lives in the shared namespace, deleting a tenant never deletes it — see [Operating → deletion](operating.md#deletion).

## Names

The extension names each policy and role by joining parts with dots — `kv.<tenant>.<namespace>.<serviceaccount>` for an app, and distinct families for shares and SSO. None of the parts may contain a dot (tenant names are checked), so two different sets of parts can never collide. You do not write these names; they are shown here so you recognise them in Vault.

---

**Previous:** [Giving an application a secret](giving-an-application-a-secret.md) · **Next:** [Delivery and login](delivery-and-login.md)
