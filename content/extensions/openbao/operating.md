# Operating

Day-2 for a platform administrator: check what was created, diagnose a workload that cannot log in, and understand what deletion does.

## Checking what was created

For tenant `team-a`, the resources the extension renders:

```bash
kubectl -n openbao-config-operator-system get \
  obns,obse,obam,obkac,obkar,obp,obtk,obpkic,obpkir \
  -l templates.v2.stakater.com/instance=openbao-config-mto-team-a
```

One read covers the health of every tenant at once:

```bash
kubectl -n openbao-config-operator-system \
  get templateinstances.templates.v2.stakater.com openbao-config-mto-parent \
  -o jsonpath='{.status.outputs.tiReady}' | jq .
```

Anything other than `True` for a tenant means its configuration did not reach OpenBao. The neighbouring `tiRendered` and `tiApplied` fields say whether it failed to render or was refused on apply.

!!! tip
    Always use the fully-qualified `templateinstances.templates.v2.stakater.com`. On OpenShift a bare `kubectl get templateinstance` returns OpenShift's own kind with an empty status — indistinguishable from "nothing is reconciling".

## Troubleshooting

**A workload cannot log in.** In order:

- The ServiceAccount needs **both** an engine annotation and `bao.stakater.com/tier` — an engine on its own grants nothing.
- Annotation values are strings — `"true"` must be quoted, or Kubernetes rejects it as a boolean.
- The `bao-config-<serviceaccount>` `ConfigMap` appears only once the ServiceAccount is annotated. If it is missing, the annotation has not been picked up.
- Grants go on the ServiceAccount and secret requests on the Deployment. A key on the wrong object is reported as an error beside the workload, not ignored.

**A whole tenant is missing.** Check its `Tenant` lists a namespace under `withTenantPrefix` or `withoutTenantPrefix` — a tenant listing none is skipped, silently — and that its namespaces carry `stakater.com/tenant=<tenant-name>`.

## What deletion does

Deleting a resource does not destroy the data behind it, by default.

| What is deleted | What happens |
|:---|:---|
| An engine, an OpenBao namespace or an auth mount | **Retained.** The OpenBao object and everything under it survives; re-creating an identical resource adopts it back. |
| A policy, login role, group or alias | **Deleted,** so the access it granted is revoked. |

The practical consequence: **deleting an MTO `Tenant` does not destroy its OpenBao data.** Its secrets, encryption keys and certificate authority are retained while its policies and login roles are removed, so access closes but the data is recoverable by re-creating the tenant.

!!! warning
    To remove a tenant's data for real, delete the tenant and then, with an OpenBao administrator token, delete its OpenBao namespace — `bao namespace delete <tenant>` cascades through everything inside it.

Removing an annotation from a ServiceAccount revokes what it granted, so access follows the workload definition rather than lingering in OpenBao.

---

**Previous:** [Security](security.md) · **Next:** [Reference](reference.md)
