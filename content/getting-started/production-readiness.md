# Production Readiness

The installation guides get MTO running with defaults chosen for a first look: bundled dependencies, a shared admin login, and a cluster the operator is allowed to trust. Before a cluster carrying real tenants depends on it, work through this list. Each item says what to change and links to the page that explains it.

## Run the dependencies yourself

The Console and showback rest on PostgreSQL and Prometheus. In `Managed` mode the [MTO Dependencies Operator](https://github.com/stakater/mto-dependencies-operator) provisions both inside the operator namespace as a single instance with 8Gi of storage, and they are only updated when a new MTO release ships a new bundled chart. That is fine for evaluation. In production the database and the metrics store should be yours: patched, backed up, sized and made highly available on your own schedule, by the team that already runs those services.

- **Point MTO at your own PostgreSQL.** Set `components.postgres.mode` to `External` and reference a secret holding either a `dsn` or the individual `host`, `port`, `username`, `password`, `database` and `sslmode` fields. Use `sslmode=require` or stricter. See [PostgreSQL](../concepts/integration-config.md#postgresql).
- **Point MTO at your own Prometheus.** Set `components.prometheus.mode` to `External` with `external.serverURL`. Showback samples usage from this Prometheus, so its retention bounds how far back cost data can be recomputed. See [Prometheus](../concepts/integration-config.md#prometheus).
- **Back up the database.** PostgreSQL holds the Console cache and the showback history that outlives Prometheus retention. Losing it does not affect tenancy enforcement, but it does lose cost history. See [Cost Analysis](../console/showback.md).
- **Own the upgrade cadence.** With `External` mode, MTO upgrades no longer touch PostgreSQL or Prometheus. Track the upstream security advisories and upgrade on your own schedule.
- **Leave OpenCost in `Managed` mode.** Showback depends on the OpenCost API, so MTO pins the OpenCost version it ships with and upgrades it in step with its own releases. Running your own OpenCost puts that compatibility on you. See [OpenCost](../concepts/integration-config.md#opencost).
- **Dex can go either way.** If you already run Dex, point MTO at it with `External` mode. Otherwise keep the bundled one and connect it to your identity provider, as described in the next section. See [Dex](../concepts/integration-config.md#dex).

```yaml
spec:
  components:
    postgres:
      mode: External
      external:
        secretRef:
          name: mto-postgres
          namespace: multi-tenant-operator
    prometheus:
      mode: External
      external:
        serverURL: https://prometheus.monitoring.svc:9090
```

## Remove the default admin login

MTO ships a local Dex user, `mto`, with password `mto`, so the Console can be reached before an identity provider is connected. The install guides add its email, `mto@stakater.com`, to the privileged users so it can see everything. A well-known account with a well-known password that can see every tenant has no place on a production cluster.

- **Connect Dex to your identity provider.** Create a `Connector` for your OIDC, SAML or LDAP provider so people sign in with their organisation accounts. See the [DexConfigOperator connector guides](https://docs.stakater.com/dco/latest/).
- **Grant administrator access to real people.** Add your platform administrators, preferably as a group, under `spec.accessControl.privileged` in the `IntegrationConfig`, and confirm one of them can sign in and see the IntegrationConfig page before the next step. See [Console Configuration](../console/configuration.md#administrators).
- **Delete the `mto` local user.** The default account is a `LocalUser` resource in the operator namespace. Find it and delete it together with the credentials secret it references. When the last `LocalUser` is gone, DexConfigOperator removes the local password login from Dex entirely.

```bash
kubectl get localusers.auth.stakater.com -n multi-tenant-operator
kubectl delete localuser <name> -n multi-tenant-operator
kubectl delete secret <credentials-secret> -n multi-tenant-operator
```

- **Remove `mto@stakater.com` from the privileged users.** Edit `spec.accessControl.privileged.users` in the `IntegrationConfig` so the list holds only your own administrators.
- **Optionally keep a break-glass account.** If you want a local login that survives an identity provider outage, create your own `LocalUser` with a non-default name, a strong bcrypt-hashed password, and a stored procedure for who may use it. See [Managing Local Users](https://docs.stakater.com/dco/latest/).

## Review who bypasses tenancy

Two settings let a user act with no tenant checks at all. Review both as you would review cluster-admin bindings.

- **`BYPASSED_GROUPS`** on the webhook skips admission checks entirely for its members. Keep it to genuine cluster administrator groups. On Helm it is `webhook.manager.env.bypassedGroups`. See [Admission bypass](../reference/security-model.md#admission-bypass).
- **`privileged.groups` and `privileged.users`** in the `IntegrationConfig` are ignored by MTO for namespace operations and are Console administrators. Prefer groups over individual users, and use `namespaceAccessPolicy.deny` to keep even privileged principals out of tenant namespaces where that is the policy. See [Privileged](../concepts/integration-config.md#privileged).
- **Privileged namespace and ServiceAccount patterns** are regular expressions. Make sure they cover the platform namespaces your distribution needs, such as `^openshift.*` and `^kube.*`, and nothing broader. On OpenShift include `^system:serviceaccount:openshift-infra.*` or pods will fail to schedule. See [Troubleshooting](../troubleshooting.md#pod-creation-error).
- **Treat the operator namespace like `kube-system`.** The operator ServiceAccount can grant any permission in the cluster. Restrict who can exec into its pods or edit its Deployments. See [Trust in the operator](../reference/security-model.md#trust-in-the-operator).

## Keep the webhooks available

The webhooks on namespaces and RoleBindings fail open. While the webhook Deployment is unavailable, a tenant user could move a namespace between tenants or grant access across a boundary. Webhook availability is therefore a security control, not only an uptime concern.

- **Run at least two webhook replicas.** On Helm set `webhook.replicas: 2`. See [Helm values](../reference/configuration.md#helm-values).
- **Set resource requests and limits per controller.** Each controller is its own Deployment and accepts its own `resources` block. Size them from observed usage on a staging cluster rather than leaving them unset.
- **Keep leader election on.** The shipped Deployments set `--leader-elect`. Do not remove it when customising manifests.
- **Alert on webhook pod availability.** See the warning in [Webhooks](../reference/webhooks.md#static-webhooks).

## Control upgrades

- **OpenShift.** Subscribe to the `stable` channel with `installPlanApproval: Manual`, so a new version installs only when you approve it. See [Installing via OperatorHub UI](installation/openshift.md#installing-via-operatorhub-ui).
- **Helm.** Pin the chart version in your `helm upgrade` command or GitOps source rather than tracking the latest tag.
- **Read the release notes first.** Some releases change behaviour that needs preparation, such as the move to Dex or the shared ingress hostname. See [Release Notes](../release-notes.md).
- **Upgrade a non-production cluster first.** The tenant definitions are the same resources everywhere, so a staging cluster running the same `Tenant`, `Quota` and `IntegrationConfig` manifests is a faithful rehearsal.
- **Know the recovery path.** A stuck OLM upgrade can require uninstalling and reinstalling the operator. Tenant resources survive that, since CRDs are kept. See [OperatorHub Upgrade Error](../troubleshooting.md#operatorhub-upgrade-error).

## Monitor the operator

- **Enable the metrics endpoint.** It is off by default. Set `--metrics-bind-address` and keep `--metrics-secure=true`. See [Metrics](../reference/metrics.md).
- **Fix the shipped ServiceMonitor.** It sets `insecureSkipVerify: true`. Replace it with `caFile`, `certFile` and `keyFile` pointing at the metrics certificates. See [ServiceMonitor](../reference/metrics.md#servicemonitor).
- **Alert on reconcile errors.** `multi_tenant_operator_reconcile_error` is set while a resource is failing to reconcile. Alert on its presence rather than aggregating over its `errors` label. See [MTO metrics](../reference/metrics.md#mto-metrics).
- **Scrape every controller.** Each controller Deployment has its own metrics Service.

## Secure the Console endpoints

- **Use a real certificate for the shared host.** Set `components.ingress.host` and `tlsSecretName` to a certificate that covers the host, issued by a CA your users trust. See [Ingress](../concepts/integration-config.md#ingress).
- **Set `trustedRootCert` for a private certificate authority.** If your certificates chain to an internal root, provide it so the Gateway, Dex and FinOps Gateway trust each other. See [Dashboard](../console/dashboard.md).
- **Update external OIDC clients.** In consolidated mode the Dex issuer is `https://<host>/dex`. Anything that trusts MTO's Dex, such as Grafana or Vault, needs that issuer.

## Set the isolation defaults

MTO does not isolate the network or the nodes unless asked. Decide these once, at the cluster level, before tenants arrive.

- **Network.** `tenantPolicies.network.disableIntraTenantNetworking`, `disableNodePortServices` and `disableHostPorts` are all off by default. See [Network](../concepts/integration-config.md#network) and [Disable intra-tenant networking](../guides/disable-intra-tenant-networking.md).
- **Nodes.** Tenant workloads share nodes and a kernel unless you pin tenants to node pools. See [Restricting Tenant Workloads to Specific Nodes](../guides/restrict-nodepool-per-tenant.md).
- **Tenant roles.** Confirm the default owner, editor and viewer ClusterRoles match your policy before the first tenant is created, since RoleBindings are created from them. See [RBAC](../concepts/integration-config.md#rbac).
- **What MTO does not do.** Read the gaps before promising them to tenants. See [What MTO does not do](../reference/security-model.md#what-mto-does-not-do).

## Licensing and configuration as code

- **Install the Enterprise license.** The free tier caps a cluster at two tenants. Create the `license` ConfigMap in the operator namespace. See [Enterprise License Configuration](installation/kubernetes.md#enterprise-license-configuration).
- **Keep tenancy in Git.** `Tenant`, `Quota`, `IntegrationConfig` and `Extensions` are ordinary resources. Manage them through GitOps so the cluster can be rebuilt from the repository and every change is reviewed. See [Deployment Models](../overview/deployment-models.md#dedicated-clusters).
- **Set retention before you need it.** `spec.namespaces.onDeletePurgeNamespaces` on each `Tenant` and `argoCD.onDeletePurgeAppProject` on its `Extensions` decide what a tenant deletion takes with it. Decide the policy now rather than during an incident. See [Uninstalling MTO](uninstalling.md#decide-what-to-keep).

## Related pages

- [Security Model](../reference/security-model.md) for what the isolation rests on
- [Configuration](../reference/configuration.md) for the variables, flags and Helm values named here
- [IntegrationConfig](../concepts/integration-config.md) for the cluster-wide settings
