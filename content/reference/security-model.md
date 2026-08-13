# Security Model

Multi Tenant Operator partitions a cluster between tenants that do not trust each other equally. This page describes what that isolation actually rests on, and where its limits are, so you can judge whether it matches your threat model.

## The isolation boundary

A tenant is a set of namespaces plus the people who may act in them. Two mechanisms hold that boundary, and they do different jobs:

- **RBAC decides who can act.** MTO binds ClusterRoles into each tenant's namespaces, so a tenant owner is an admin of their own namespaces and an ordinary user everywhere else. This is standard Kubernetes authorization, with the usual guarantees.
- **Admission decides what they can create.** Restrictions such as permitted storage classes, image registries, or ingress hostnames are not expressible in RBAC, so they are enforced by [validating webhooks](webhooks.md) at admission time.

The important consequence is that the two fail differently. RBAC is enforced by the API server and keeps working if MTO is down. Admission checks depend on MTO's webhook pods being reachable, and the webhooks on core resources are configured to fail open.

!!! warning
    `vnamespace.kb.io` and `vrolebinding.kb.io` use `failurePolicy: Ignore`. While the webhook Deployment is unavailable, namespace and RoleBinding operations are not checked, so a tenant user could move a namespace between tenants or grant access across a boundary. This trade is intentional, as failing closed would block namespace and RBAC activity cluster-wide, but it means webhook availability is a security control. Alert on it.

MTO's own resources fail closed, so a webhook outage cannot leave a `Tenant`, `Quota`, or `IntegrationConfig` in an invalid state.

## Trust in the operator

The operator provisions namespaces, RBAC, quotas, and workloads on users' behalf, which requires broad permissions. Its `manager-role` includes write access to `clusterroles`, `clusterrolebindings`, and `rolebindings`, and to `validatingwebhookconfigurations`.

Treat the operator's ServiceAccount as cluster-admin-equivalent. Anyone who can execute in an operator pod, modify its Deployment, or edit `manager-role` can grant themselves any permission in the cluster. In practice this means the operator namespace should be as tightly controlled as `kube-system`, and the Console and Gateway ServiceAccounts, which are separate and narrower, should not be conflated with it. See [RBAC](rbac.md) for the full permission set.

## Admission bypass

`BYPASSED_GROUPS` lists groups whose members skip tenant admission checks entirely. The check runs before any tenant logic, so a member of a bypassed group is unaffected by every restriction described on this page and in [Webhooks](webhooks.md).

This exists so administrators can repair a broken tenant without fighting the operator. It is the single highest-value setting to review, since adding a widely-held group to it silently disables tenant enforcement for a large part of your user base. Keep it to genuine cluster administrator groups, and review it as you would review cluster-admin bindings.

## Workload hardening

The operator, webhook, and controller Deployments run as non-root (`runAsNonRoot: true`) with privilege escalation disabled (`allowPrivilegeEscalation: false`) at the container level. Pod security context is exposed per controller through the Helm chart, so you can tighten it further to meet the [restricted Pod Security Standard](https://kubernetes.io/docs/concepts/security/pod-security-standards/#restricted) if your baseline requires it.

Running each controller as its own Deployment also limits blast radius: a crash loop or resource exhaustion in one controller does not stop the others.

## Transport and endpoints

- **Webhooks** are served over TLS. On Kubernetes the certificate comes from cert-manager into `tenant-operator-webhook-server-cert`; on OpenShift, OLM generates and rotates it. A `NetworkPolicy` restricts ingress to the webhook port.
- **Metrics** default to https with bearer-token authentication, authorized against the Kubernetes API through `tokenreviews` and `subjectaccessreviews`. Setting `--metrics-secure=false` removes authentication entirely. A `NetworkPolicy` restricts ingress to the metrics port. See [Metrics](metrics.md).
- **The Tenants API** backing the [kubectl plugin](../cli/overview.md) is reached through `services/proxy`, so access is mediated by the API server and subject to normal Kubernetes authentication.

!!! note
    The shipped Prometheus `ServiceMonitor` sets `insecureSkipVerify: true`. Metrics remain authenticated, but the scraper does not verify the endpoint's certificate. Replace it with explicit CA and client certificate paths for production.

## What MTO does not do

Being explicit about the gaps is more useful than a list of features:

- **No network isolation by default.** Tenants share the cluster network unless you apply NetworkPolicies. See [Disable intra-tenant networking](../guides/disable-intra-tenant-networking.md).
- **No node or kernel isolation.** Tenant workloads share nodes and a kernel. Where that is unacceptable, combine MTO with node isolation, and see [Restricting Tenant Workloads to Specific Nodes](../guides/restrict-nodepool-per-tenant.md).
- **No protection against a compromised control plane component.** The model assumes the API server, etcd, and the operator itself are trustworthy.
- **No retroactive enforcement.** Admission checks apply to new and updated objects. Tightening a tenant's restrictions does not remove resources that already violate them.

## Related pages

- [RBAC](rbac.md) for the exact permissions at each layer
- [Webhooks](webhooks.md) for what admission enforces and when it is registered
- [Configuration](configuration.md) for the settings referenced here
