# Webhooks

Multi Tenant Operator enforces most of its tenancy rules at admission time rather than after the fact. A `Tenant` that restricts storage classes does not clean up offending PersistentVolumeClaims later, it stops them being created. All of MTO's webhooks are validating; none mutate.

There are two sets. A fixed set is installed with the operator and always present. A second set is registered and removed at runtime by the tenant controller, depending on which features your tenants actually use.

## Static webhooks

These live in the `tenant.operator.validation.kb.io` ValidatingWebhookConfiguration and are always active when the webhook Deployment is running.

| Webhook | Resource | Operations | Failure policy |
| --- | --- | --- | --- |
| `vtenant.kb.io` | `tenants` (v1beta3) | CREATE, UPDATE | Fail |
| `vquota.kb.io` | `quotas` (v1beta1) | DELETE | Fail |
| `vintegrationconfig.kb.io` | `integrationconfigs` (v1beta1) | CREATE, UPDATE | Fail |
| `vnamespace.kb.io` | `namespaces` | CREATE, UPDATE, DELETE | Ignore |
| `vrolebinding.kb.io` | `rolebindings` | CREATE, UPDATE, DELETE | Ignore |

The split in failure policy is deliberate. MTO's own resources fail closed, so a webhook outage cannot let a tenant misconfiguration through. The webhooks on core Kubernetes resources fail open, so an outage degrades tenant isolation rather than blocking all namespace and RBAC activity cluster-wide.

!!! warning
    Because `vnamespace.kb.io` and `vrolebinding.kb.io` use `failurePolicy: Ignore`, a webhook Deployment that is down means namespace and RoleBinding operations proceed unchecked. Monitor the webhook pods as a security control, not just an availability one.

### What each enforces

**Tenant** rejects a tenant whose `spec.quota` is missing or names a `Quota` that does not exist, and rejects one claiming a namespace that already exists and is owned by a different tenant. The error names the conflicting tenant. The free tier also caps the cluster at two tenants.

**Quota** blocks deletion while any `Tenant` still references the quota, listing the referencing tenants so you know what to change first.

**IntegrationConfig** requires the default tenant roles to be present and complete, so owner, editor, and viewer must each be set. It also validates integration blocks when they are enabled: Vault needs an address, accessor path, and Kubernetes auth role name, and SSO needs a client name and a secret reference with both name and namespace.

**Namespace** and **RoleBinding** keep tenant boundaries intact for resources MTO does not own, preventing a namespace from being moved between tenants or a RoleBinding from granting access across a tenant boundary.

## Dynamic webhooks

The remaining checks only make sense for tenants that opted into the corresponding feature. Registering them unconditionally would put MTO in the admission path for every Pod and Ingress in the cluster, so the tenant controller instead creates each ValidatingWebhookConfiguration only while at least one tenant uses the feature, and deletes it when the last one stops.

| Webhook | Registered when a tenant sets | Intercepts |
| --- | --- | --- |
| `tenant-storage` | `spec.storageClasses` | `persistentvolumeclaims` |
| `tenant-ingress-classname` | `spec.ingressClasses` | `ingresses` |
| `tenant-ingress-hostname` | `spec.hostValidationConfig` with a valid regex | `ingresses` |
| `tenant-route-hostname` | `spec.hostValidationConfig` with a valid regex | `routes` (OpenShift) |
| `tenant-pod-priority` | `spec.podPriorityClasses` | workload resources |
| `tenant-pod-service-account` | `spec.serviceAccounts.denied` | workload resources |
| `tenant-pod-image-registry` | `spec.imageRegistries` | workload resources |

The three workload webhooks all intercept the same set: `pods`, then `deployments`, `replicasets`, `statefulsets`, and `daemonsets` in `apps`, and `jobs` and `cronjobs` in `batch`. Validating the controllers as well as the Pod means a rejected workload surfaces the error on the resource the user actually created, rather than only in a ReplicaSet event.

Two consequences follow from this design. Adding a restriction to a tenant may briefly register a new webhook before it takes effect, and removing the last tenant using a feature removes MTO from that resource's admission path entirely, which is the intended way to reduce blast radius.

!!! note
    `tenant-ingress-hostname` and `tenant-route-hostname` only register when the host validation regex is valid. An invalid regex means the webhook is silently not registered and hostnames are not enforced, so verify the tenant's status after configuring host validation. See [Restricting Hostname per Tenant](../guides/host-validation.md).

## Bypassing admission

Users in a group listed in `BYPASSED_GROUPS` skip these checks entirely. This exists so cluster administrators can repair a broken tenant without fighting the operator, and it is checked before any tenant logic runs.

!!! warning
    Membership of a bypassed group defeats every check on this page. See [Configuration](configuration.md) for how it is set and [Security Model](security-model.md) for how to reason about it.

## Enabling and certificates

The webhook Deployment starts when `ENABLE_WEBHOOKS` and `ENABLE_ADMISSION_WEBHOOKS` are both `"true"`. Serving certificates are supplied through `--webhook-cert-path`, `--webhook-cert-name`, and `--webhook-cert-key`. On Kubernetes these come from cert-manager into the `tenant-operator-webhook-server-cert` secret; on OpenShift, OLM generates and rotates them instead. A `NetworkPolicy` is provided to restrict ingress to the webhook port.

## Related pages

- [Configuration](configuration.md) for the variables and flags referenced above
- [RBAC](rbac.md) for the permissions that let the operator register webhooks
- [Security Model](security-model.md) for how admission fits the wider isolation model
