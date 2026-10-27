# Operating

## Validate the whole chain

One check confirms the stack, however you assembled it. Sign in as a member of one tenant, confirm you can see that tenant's logs, metrics and traces, then confirm a request for another tenant's data is refused.

## Checking what was created

```bash
kubectl get grafana -n mto-extension-grafana-system
kubectl describe grafana mto-extension-grafana -n mto-extension-grafana-system
```

The status is the first place to look:

- `status.phase` — the one-word summary: `Ready`, `Progressing`, `Failed`, or `Blocked` for a duplicate resource that has been refused.
- `status.tenantStatus` — totals for tenants seen, reconciled and failed, plus a per-tenant `details` list carrying each tenant's last sync time and last error.
- `status.conditions` — the Ready condition, whose reason narrows the phase down: `Success`, `Reconciling`, `WaitingForDependencies`, `PartialSuccess`, `Error` or `Blocked`.
- `status.aggregatedViews` — per-user view state, with phase `Active`, `PartialMirror` or `Failed`.
- `status.strayMirrorTenantOrgs` — tenant organisations that unexpectedly contain mirror content. Reported for visibility only; never deleted.

Inside Grafana, using the credentials from `<grafana-instance-name>-admin-credentials`:

```bash
SECRET=grafana-admin-credentials    # <grafana-instance-name>-admin-credentials
GF_USER=$(kubectl get secret "$SECRET" -n telemetry \
  -o jsonpath='{.data.GF_SECURITY_ADMIN_USER}' | base64 -d)
GF_PASS=$(kubectl get secret "$SECRET" -n telemetry \
  -o jsonpath='{.data.GF_SECURITY_ADMIN_PASSWORD}' | base64 -d)

curl -su "$GF_USER:$GF_PASS" http://grafana-service.telemetry.svc:3000/api/orgs
curl -su "$GF_USER:$GF_PASS" http://grafana-service.telemetry.svc:3000/api/v1/sso-settings/generic_oauth
```

The organisation list should hold one entry per tenant. In the SSO settings, `orgMapping` should carry `group:orgID:role` triples for each tenant, and `roleAttributePath` should contain only the cluster-admin expression — tenant patterns appearing there are what flattens per-organisation roles into one role everywhere.

## When something does not appear

| Symptom | What to check |
|:---|:---|
| A data source is missing from every organisation | `allowCrossNamespaceImport: true`; the resource is in `spec.server.namespace`; `jsonData` has an `httpHeaderName<N>` equal to `X-Scope-OrgID`; `spec.datasource.uid` is non-empty and unique; `DatasourceSynchronized=True` |
| A dashboard is missing from every organisation | `allowCrossNamespaceImport: true`; the namespace; a UID via `spec.customUID` or the JSON; a `GrafanaFolder` exists for any referenced folder; `DashboardSynchronized=True` |
| It appears in some organisations only | That is the annotations working — check `mto.grafana/tenant` and the scaffolding mode |
| Panels report the data source was not found | The dashboard's UID matches no managed data source and the type fallback could not resolve it, because more than one shares that type. Use the same base UID as the `GrafanaDatasource` |
| A user signs in but sees no tenant | Their groups match no rendered pattern. Compare the token's `groups` claim against the patterns; add the user to the right group, or change `pattern` to match your provider's naming |
| A user has the same role everywhere | Tenant patterns have reached `roleAttributePath`. Check the SSO settings above |
| Dashboard edits made in the UI keep reverting | Expected — the resource is the source of truth. Duplicate the dashboard to experiment, then move the change into the resource |

The reconcile cadence is `spec.resyncInterval`: 30 seconds by default, floored at 10 seconds, so most corrections land within one cycle. With aggregated views enabled the default tightens to 10 seconds, because new SSO users are only discovered by polling.

## What deletion does

- Deleting a `Tenant` deletes its Grafana organisation, and with it the dashboards and data sources inside.
- Deleting a `GrafanaDashboard` or `GrafanaDatasource` removes it from every tenant organisation on the next reconcile.
- Removing a tenant from a `mto.grafana/tenant` annotation removes the resource from that tenant only.

Content follows the definition rather than lingering in Grafana.

!!! warning
    Aggregated-view organisations are not deleted automatically when `aggregatedViews.enabled` is set back to `false`, or when the extension is removed. Grafana rejects deletion of an organisation while the auto-added admin is still a member, so these are left for administrators to remove. Mirrored content inside them stops being updated as soon as the feature is off.

Setting `spec.deletionPolicy` is currently accepted but has no effect — the field is reserved, and the behaviour above applies either way.

---

**Previous:** [Choosing which tenants get a resource](choosing-which-tenants.md) · **Next:** [Reference](reference.md)
