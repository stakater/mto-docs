# Operating

Day-2 for a platform administrator: how to read health, what to check when a workload cannot log in, what deletion does and how to purge, and how to upgrade and uninstall safely.

## Health

A `TemplateInstance` being `Ready` means its VCO resources were **applied**, not that VCO could write them to Vault. Each `TemplateInstance`'s `status.outputs` carries two fields per VCO kind, keyed by object name:

| Field | Meaning |
|:---|:---|
| `<output>Succeeded` | `["True"]` once VCO has written the object at least once; `[]` means never — the one unambiguous failure |
| `<output>LastError` | the message of the most recent failed reconcile, **ever** — it stays after the object recovers |

The parent reports each tenant's KV mount (`engines…`). Each tenant's child reports its auth mounts and their configs, its login roles, its policies and its SSO roles (`authMounts…`, `k8sAuthConfigs…`, `k8sAuthRoles…`, `policies…`, `oidcConfigs…`, `oidcRoles…`).

```bash
kubectl -n vault-config get templateinstances.templates.v2.stakater.com \
  mto-extension-vault-community-parent -o jsonpath='{.status.outputs.enginesLastError}'
```

!!! warning "VCO status cannot say 'healthy now'"
    VCO sets `ReconcileSuccessful` and `ReconcileFailed` side by side and both freeze after their first write, so there is no live health bit. The signal that tracks the data path now is on each tenant's `.eso` TemplateInstance: `externalSecretSync` gives every `ExternalSecret`'s `Ready` status and reason, and `secretStores` every `SecretStore`'s. A failed store fails every `ExternalSecret` that uses it, so the two tell "one workload" from "this login". See also [Monitoring](#monitoring).

## Troubleshooting

**A workload cannot log in.** In order:

- Its ServiceAccount is not annotated, or has a rejected annotation — look for a `vault-config-<sa>.error` `ConfigMap` in the workload namespace.
- Its namespace is not labelled `stakater.com/tenant: <tenant>`, so the parent does not see it.
- The tenant was skipped — its name is not a DNS label, is longer than 29 characters, or is reserved. Check the `ConfigMap` `mto-extension-vault-community-skipped-tenants` in `configNamespace`, which gives the reason.
- The app logs in on the wrong mount: on Community Edition the mount carries the tenant's name, `<tenant>/kubernetes/workloads`. Use `VAULT_K8S_MOUNT` from the app's `ConfigMap`.

**Nothing reconciles for any tenant.** The parent cannot read its inputs — almost always `templateOperator` not matching Template Operator v2's real identity, or a missing CRD or version mismatch. Read the parent `TemplateInstance`'s conditions in `configNamespace`.

**An object shows `<output>Succeeded: []`.** VCO could not write it; read `<output>LastError` for the cause, often a Vault permission.

**A tenant's mount fails with "path is already in use".** The tenant is named like a mount your platform already has, which `parent.reservedPaths` does not list. Its KV mount fails on the parent's `enginesLastError`, its auth mount on its child's `authMountsLastError`, and no other tenant is affected. Add the name to `parent.reservedPaths`, and rename or delete the tenant.

## Deletion

Access ends at once; data stays until a Vault admin purges it.

| Event | What goes | What stays |
|:---|:---|:---|
| Annotation removed | the policy, role and `ConfigMap`; a token issued before loses access at once (Vault reads a token's policies by name) | the app's secrets |
| Role lowered | the policy is rewritten in place; an issued token follows at once | secrets |
| Tenant's last labelled namespace deleted | its child TemplateInstances: every grant, and **its auth mounts — which revokes every token issued through them**, share tokens included | `<tenant>/kv` and its secrets |
| Tenant deleted | as above; the `<tenant>-kv` CR stays `Terminating`, because the production VCO policy may not disable a KV mount | the mount, its secrets, and the shares in `shared/kv` |
| Tenant recreated with the same name | — | the retained secrets come back: **purge before reusing a name** |

VCO has no deletion policy: when a CR is deleted, VCO deletes the object in Vault. The protection for data is the VCO Vault policy, which denies `delete` on the KV mounts. The delete fails, the secrets stay, and the mount CR waits in `Terminating` with the VCO finalizer until a person decides. Until then, VCO retries the delete, and each retry adds a 403 to the VCO log and to Vault's audit log.

### Purging a deleted tenant

A Vault admin, in this order:

1. Check that the mount CR is already `Terminating` — the tenant is deleted. **Never disable a mount whose CR is live**: VCO re-creates it, empty, within one sync period.
1. Disable the mount, which deletes its secrets: `vault secrets disable <tenant>/kv`.
1. Remove the CR's finalizer:

    ```bash
    kubectl -n vault-config patch secretenginemounts.redhatcop.redhat.io <tenant>-kv \
      --type merge -p '{"metadata":{"finalizers":null}}'
    ```

1. Before the name is reused: delete `from-<tenant>/` and `to-<tenant>/` in `shared/kv/`, and remove the peers' `kv-export-tenant` and `kv-import-tenant` entries that name it.

## Monitoring

`tenantValues.monitoring.enabled=true` gives each tenant a `PrometheusRule` `mto-extension-vault-community-<tenant>` in `monitoring.prometheusNamespace`, with one alert, `VaultExternalSecretSyncFailed`: an `ExternalSecret` in one of the tenant's namespaces has `Ready=False` for 5 minutes. It needs the Prometheus Operator CRDs and the ESO metrics scraped. There is no alert on the VCO objects — their status cannot carry one (see [Health](#health)).

## Upgrading

A null value, or a key commented out, takes the chart default (`admission.enabled` on, `parent.eso` enabled). That holds for a values file and for `--set`, but **not on `helm upgrade --reuse-values`**: Helm then keeps the release's old value, and the chart never sees the null. To go back to a default, set the value itself (`--set parent.eso=enabled`, `--set admission.enabled=true`), or upgrade with all your values and without `--reuse-values`.

The schema refuses a key the charts do not read, and a value of the wrong type, so a misspelled key fails the upgrade instead of being ignored.

## Uninstalling

Order matters. Delete the parent `TemplateInstance` first, wait until every VCO CR is gone, and only then uninstall the release.

```bash
kubectl -n vault-config delete templateinstances.templates.v2.stakater.com \
  mto-extension-vault-community-parent --wait --timeout=5m
kubectl -n vault-config get secretenginemounts.redhatcop.redhat.io,authenginemounts.redhatcop.redhat.io,kubernetesauthengineconfigs.redhatcop.redhat.io,kubernetesauthengineroles.redhatcop.redhat.io,policies.redhatcop.redhat.io,jwtoidcauthengineconfigs.redhatcop.redhat.io,jwtoidcauthengineroles.redhatcop.redhat.io
```

Under the production policy, the KV mount CRs (`<tenant>-kv` and `shared-kv`) stay `Terminating`. For each one, decide what happens to its secrets:

- **Keep them:** remove only the CR's finalizer (step 3 of [Purging a deleted tenant](#purging-a-deleted-tenant)). The mount and its secrets stay in Vault.
- **Delete them:** [purge](#purging-a-deleted-tenant) the mount.

When no VCO CR is left, uninstall the release:

```bash
helm uninstall mto-extension-vault-community-bootstrap -n vault-config
```

A plain `helm uninstall` first would delete the RBAC and the VCO login ServiceAccount in the same step as the parent, and every CR would then wait `Terminating` for a login that no longer exists. Use the full resource name: on OpenShift the short name is OpenShift's own `template.openshift.io` kind.

---

**Previous:** [Security](security.md) · **Next:** [Reference](reference.md)
