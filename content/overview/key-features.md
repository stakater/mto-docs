# Key Capabilities

MTO groups into six capability areas. Each one is driven by the same `Tenant` definition, which is what keeps them consistent with each other.

| Capability | The question it answers |
|---|---|
| [Multi-Tenancy](#multi-tenancy) | How do I safely share Kubernetes? |
| [Templates](#templates) | How do I standardize environments? |
| [FinOps](#finops) | Who is consuming what, and what does it cost? |
| [Hibernation](#hibernation) | Why pay for idle environments? |
| [Extensions](#extensions) | What about the tools surrounding Kubernetes? |
| [Console](#console) | How do operators and tenants actually use all this? |

## Multi-Tenancy

### Tenants as the unit of ownership

A `Tenant` names the people, the namespaces, the quota and the standards that belong to one team, department or customer. Everything else in MTO reads from it, so access, cost and lifecycle all agree on the same boundary.

More details on [Tenant](../concepts/tenant.md).

### Access control without hand-written RBAC

RBAC is one of the most error-prone parts of Kubernetes. MTO binds ClusterRoles to the tenant's namespaces for owners, editors and viewers, keeps those bindings current as membership changes, and lets you swap in custom roles when the defaults do not fit. Existing Kubernetes and OpenShift groups — including groups synced from an external identity provider — can be used directly as tenant membership.

More details on [Custom Roles](../guides/custom-roles.md) and [Extending Default Roles](../guides/extend-default-roles.md).

### Namespace management and self-service

Tenants declare the namespaces they own, with or without the tenant name as a prefix. Sandboxes give every member of a tenant their own namespace, preloaded with the tenant's templates and drawing from the tenant's quota — a personal development environment that costs nothing extra to govern.

More details on [Creating Namespaces](../guides/create-namespaces.md) and [Sandboxes](../guides/create-sandbox.md).

### Quota at the tenant scope

Quota is defined once for the tenant and shared across all of its namespaces, so teams can self-serve namespaces without being able to exceed the budget you allocated. On OpenShift this is enforced with a `ClusterResourceQuota`; on other distributions MTO aggregates per-namespace quota at admission.

More details on [Quota](../concepts/quota.md).

### Guardrails enforced at admission

Beyond quota, the admission webhook enforces the boundaries a platform team actually cares about: which storage classes, ingress classes, pod priority classes and image registries a tenant may use, which service accounts are denied, and which hostnames a tenant may claim. Each of these is off by default and grants no extra permissions until you enable it.

More details on [Storage Classes](../guides/storage-classes.md), [Image Registries](../guides/image-registries.md), [Pod Priority Classes](../guides/pod-priority-classes.md), [Service Accounts](../guides/service-accounts.md) and [Host Validation](../guides/host-validation.md).

### Network and node isolation

Tenant namespaces can be isolated from each other on the network, and workloads can be pinned to a specific node pool so noisy or sensitive tenants do not share hardware.

More details on [Disabling Intra-Tenant Networking](../guides/disable-intra-tenant-networking.md) and [Restricting Node Pools](../guides/restrict-nodepool-per-tenant.md).

### Standard metadata everywhere

Labels and annotations can be applied cluster-wide, per tenant, or per namespace, with templated values such as the tenant's name or user. That is what makes downstream tooling — cost attribution, network policy, monitoring — able to find things reliably.

More details on [Assigning Metadata](../guides/assign-metadata.md) and [Templated Metadata Values](../guides/templated-metadata-values.md).

## Templates

### Reusable, enforceable environments

A template describes what a namespace should contain: Kubernetes manifests, Helm charts, or references to existing resources. Templates are parameterized, so one definition serves many namespaces, and they can be *enforced* — applied to every namespace of one tenant or of all tenants — which turns a documented baseline into a guaranteed one.

Common uses:

* Network policies for tenant isolation
* Development tooling in every namespace
* Pre-populated databases with test data
* Image pull secrets and other credentials injected at namespace creation

### Cross-namespace resource distribution

Secrets and ConfigMaps can be cloned from one namespace into others selected by label. A `TemplateGroupInstance` distributes them across matching namespaces — including across tenants when that is intended — while a `TemplateInstance` stays inside a single tenant.

More details in the [Template Operator documentation](https://docs.stakater.com/template-operator/).

## FinOps

### Showback

MTO samples resource usage per namespace, aggregates it per tenant, prices it, and stores the history. The result answers the question that ends most "the cluster is too expensive" discussions: *which team consumed what, and what did it cost?* Because the tenant is the unit of ownership, the report needs no separate tagging scheme to be correct. Organizations that charge back internal departments or external customers can bill from actual consumption rather than estimates.

More details on [Showback](../console/showback.md).

### Cost and usage analysis

Usage is broken down over time and across tenants and namespaces, so you can see trends rather than a single snapshot — which environments grew, which requests are far above actual use, and where reservations are being paid for but not consumed.

### Capacity planning

Capacity planning looks at the cluster from the supply side: what the nodes provide, what is already committed, and what remains. Node filtering lets you scope the view to a specific pool, so a team asking for more capacity gets an answer grounded in what the cluster actually has rather than a guess.

More details on [Capacity Planning](../console/capacity-planning.md).

## Hibernation

Non-production environments are idle most of the week, and idle environments still cost money. MTO puts Deployments and StatefulSets to sleep and restores their previous replica counts on wake, in two modes:

* **Scheduled** — a sleep and wake cron pair, typically nights and weekends.
* **Instant** — put an environment to sleep now, and leave it asleep until someone wakes it.

Hibernation is driven by a `ClusterResourceSupervisor` resource, provided by the Hibernation Operator. It targets namespaces by label selector, and because MTO stamps `stakater.com/tenant: <tenant-name>` on every namespace it manages, one selector covers a whole tenant. A supervisor can also name the tenant's ArgoCD AppProjects, so the tenant's Applications sleep alongside its workloads instead of syncing them back up.

The effect shows up directly in showback. What it is worth depends on the infrastructure underneath: with a cluster autoscaler, freed requests allow nodes to be removed and the bill falls; on fixed capacity it releases headroom for other workloads and defers the next purchase. Hibernation scales workloads — PersistentVolumeClaims and their storage cost are untouched.

More details on [Hibernating a Tenant](../guides/hibernate-tenant.md) and the [Hibernation console](../console/hibernation.md).

## Extensions

The tenant boundary does not stop at the Kubernetes API. Extensions project the same tenant definition into the tools around the cluster, so you maintain one boundary instead of several.

### ArgoCD

MTO provisions an `AppProject` per tenant, scoped to the repositories the tenant may deploy from and the namespaces it may deploy into, with cluster-resource allow-lists and namespace-resource deny-lists. Tenant users get GitOps self-service without an administrator hand-editing ArgoCD RBAC.

More details on [ArgoCD Multi-Tenancy](../integrations/argocd.md).

### HashiCorp Vault

MTO extends the tenant's permission model into Vault, creating the paths, roles and policies for the tenant. Tenant users manage their own secrets without anyone else gaining access to their paths.

More details on [Vault Multi-Tenancy](../integrations/vault/vault.md).

### Developer workspaces and collaboration

DevWorkspace gives tenant users cloud development environments inside their own namespaces. Mattermost creates a team and a set of channels per tenant, and removes users from it when they leave the tenant.

More details on [DevWorkspace](../integrations/devworkspace.md) and [Mattermost](../integrations/mattermost.md).

More details on [Extensions](../concepts/extensions.md).

## Console

The MTO Console is the interface for both audiences over the same objects.

Administrators see every tenant, its namespaces, quota consumption, cost breakdown, templates, hibernation schedules and cluster capacity in one place. Tenant users see the subset they own, and can act on it — create namespaces, inspect quota headroom, instantiate templates, wake a hibernated environment.

Everything the console shows is read from the same Kubernetes resources you manage in Git, so a change made in the UI is visible through the API and vice versa. There is no second source of truth to reconcile.

More details on [Console](../console/overview.md).

## Underneath all of it

**Everything as code.** MTO is configured entirely through custom resources, so tenants, quotas, templates and schedules live in Git and go through review like any other change. GitOps tooling applies them; MTO reconciles them.

**No cluster sprawl.** One governed cluster hosting many teams means one control plane, one monitoring stack and one upgrade cycle to operate — instead of multiplying that work by the number of teams.

**A native experience.** Tenants use ordinary `kubectl`, ordinary namespaces and ordinary Kubernetes resources. MTO adds no proxy, no custom binary and no extra management layer between users and the API.

## Next

* [How MTO Works](how-it-works.md) — how these fit together at runtime
* [Use Cases](use-cases.md) — the shapes this takes in practice
* [Create a Tenant](../guides/create-tenant.md) — start with one object
