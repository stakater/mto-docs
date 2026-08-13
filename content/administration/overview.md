# Administration

MTO installs as one product, not as five independent operators you assemble. Multi-Tenancy, Templates, FinOps, Hibernation and Extensions share one installation, one cluster-wide configuration object and one supporting stack — which is convenient to run, and changes what a platform administrator is responsible for compared with deploying any of those components on its own.

This section covers the responsibilities that come from hosting them together.

## One configuration object

Cluster-wide policy lives in a single `IntegrationConfig`, not in per-component settings:

- `spec.accessControl` — the roles that map to tenant owners, editors and viewers, the namespace access policy, and privileged namespaces and service accounts.
- `spec.components` — whether the Console, its ingress and the FinOps stack are provisioned at all.
- `spec.metadata` — the labels and annotations every managed namespace, group and sandbox carries.
- `spec.integrations` — where ArgoCD and Vault are, and the policies MTO creates in them.
- `spec.tenantPolicies` — cluster-wide defaults such as network isolation.

A change here affects every tenant. It belongs in Git and in review like any other cluster-wide policy.

See [Configuration](configuration.md) and [Integration Config](../multi-tenancy/concepts/integration-config.md).

## One supporting stack

MTO's Pilot controller provisions and manages the components the Console and FinOps depend on — Console, Gateway, Dex, PostgreSQL, Prometheus, `kube-state-metrics`, OpenCost and the FinOps Operator and Gateway. Running them is therefore an MTO responsibility rather than a separate integration project, but the implications are yours to plan for:

- **Storage.** PostgreSQL is a StatefulSet and holds cost history, so it needs a storage class that survives node loss, and it belongs in your backup scope.
- **Retention.** Cost history is stored in PostgreSQL and outlives Prometheus retention. Prometheus sizing therefore affects sampling, not how far back reports go.
- **Ingress and TLS.** The Console, Gateway, Dex and FinOps Gateway are exposed through ingress you configure, with hostnames and TLS secrets you supply.
- **Identity.** Dex is the identity broker for the Console. It replaces the previously bundled Keycloak, and is configured through the IntegrationConfig.

See [Dashboard](../console/dashboard.md) for the component and ingress settings.

## One admission webhook

The webhook that enforces tenant guardrails is cluster-wide and sits in the write path of workload creation. Two consequences follow: its availability matters to tenants who are not doing anything with MTO at the time, and the privileged namespaces and service accounts you exempt in the IntegrationConfig are the escape hatch for cluster components that must not be subject to it.

See [Webhooks](webhooks.md) and [Security Model](security-model.md).

## Operator permissions

MTO manages namespaces, RBAC, quota and resources inside tenant namespaces, so its own ClusterRole is broad by necessity. When a tenant needs to manage a resource type MTO does not know about, the manager role is extended deliberately rather than by granting tenants cluster-level access.

See [RBAC](rbac.md) and [Extending Default Roles](../multi-tenancy/guides/extend-default-roles.md).

## Standalone deployments

FinOps and Hibernation can also be deployed on their own, without the rest of MTO. Their administration differs in that case — different installation, different configuration surface, and no shared IntegrationConfig — and is documented with those products rather than here.

## In this section

- [Configuration](configuration.md) — the settings a cluster administrator controls
- [RBAC](rbac.md) — the roles MTO defines and the permissions it needs
- [Security Model](security-model.md) — what the boundary guarantees, and what it does not
- [Metrics](metrics.md) — what MTO exposes about itself
- [Webhooks](webhooks.md) — the admission checks and their failure behaviour
- [Troubleshooting](troubleshooting.md) — common problems and how to diagnose them
