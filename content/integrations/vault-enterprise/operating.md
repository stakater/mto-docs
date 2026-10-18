# Operating

Day-2 for a platform administrator: how to read health, what to check when a workload cannot log in, what deletion does, and how to uninstall safely.

## Health

A child `TemplateInstance` being `Ready` means its VCO resources were **applied**, not that VCO could write them to Vault. Each child's `status.outputs` carries two fields per VCO kind, keyed by object name:

| Field | Meaning |
|:---|:---|
| `<kind>Succeeded` | `["True"]` once VCO has written the object at least once; `[]` means never — the one unambiguous failure |
| `<kind>LastError` | the message of the most recent failed reconcile, **ever** — it stays after the object recovers |

!!! warning "VCO status cannot say 'healthy now'"
    VCO sets `ReconcileSuccessful` and `ReconcileFailed` side by side and both timestamps freeze after the first write, so there is no live health bit. The `.eso` TemplateInstance's `ExternalSecret` outputs are the signal that tracks the data path now; and see [Monitoring](#monitoring).

## Troubleshooting

**A workload cannot log in.** In order:

- Its ServiceAccount is not annotated, or has a rejected annotation — look for a `vault-config-<sa>.error` `ConfigMap` in the workload namespace.
- Its namespace is not labelled `stakater.com/tenant: <tenant>`, so the parent does not see it.
- The tenant was skipped (name not a DNS label, longer than 63 chars, or equal to the shared-namespace name) — check the skipped-tenants `ConfigMap` in `configNamespace`.

**Nothing reconciles for any tenant.** The parent cannot read its inputs — almost always `templateOperator` not matching Template Operator v2's real identity, or a missing CRD/version mismatch. Read the parent `TemplateInstance`'s conditions in `configNamespace`.

**An object shows `<kind>Succeeded: []`.** VCO could not write it; read `<kind>LastError` for the cause (often a Vault permission or a Community-Edition cluster).

## Deletion

VCO has **no deletion policy**: when a CR is deleted, VCO deletes the object in Vault. For a `Namespace` CR that deletes the tenant's Vault namespace and every secret in it, which Vault cannot restore.

The protection is the VCO login's Vault policy: **do not grant `delete` on `sys/namespaces/*` or the tenants' `sys/mounts/*`** (the production `examples/vco-admin-policy.hcl` does not). the delete then fails, the data stays, and the CR sits in `Terminating` with the VCO finalizer until a person decides. To really delete a tenant, a Vault admin deletes the namespace, then removes the finalizer.

A tenant's Vault namespace and KV mount are rendered by the **parent**, so they live as long as the `Tenant` — deleting a tenant's last namespace removes its grants but keeps its secrets, and labelling a namespace again brings the grants back. A cross-tenant share lives in the shared namespace, so deleting a tenant never deletes it.

## Monitoring

`tenantValues.monitoring.enabled=true` gives each tenant a `PrometheusRule` with one alert, `VaultExternalSecretSyncFailed`: an `ExternalSecret` in one of the tenant's namespaces has `Ready=False` for 5 minutes. It needs the ESO metrics scraped. There is no alert on the VCO objects — their status cannot carry one (see [Health](#health)).

## Uninstalling

Order matters. Delete the parent `TemplateInstance` first, wait until every VCO CR is gone, and only then uninstall the release:

```bash
kubectl -n vault-config delete templateinstances.templates.v2.stakater.com \
  mto-extension-vault-enterprise-parent --wait
kubectl -n vault-config get namespaces.redhatcop.redhat.io,policies.redhatcop.redhat.io   # wait for "No resources"
helm uninstall mto-extension-vault-enterprise-bootstrap -n vault-config
```

A plain `helm uninstall` first would delete the RBAC and the VCO login ServiceAccount in the same step as the parent, leaving every CR stuck in `Terminating`. With the delete-denying Vault policy, the data-bearing CRs stay `Terminating` in either order — that is the intended protection, not a failure. Use the full resource name: on OpenShift the short name is OpenShift's own `template.openshift.io` kind.

---

**Previous:** [Security](security.md) · **Next:** [Reference](reference.md)
