# Why MTO

Sharing a Kubernetes cluster is easy. Sharing it *safely*, at scale, without a platform team becoming the bottleneck for every namespace, role binding and quota change — that is the hard part. Multi-Tenant Operator exists to make that part routine.

## What Kubernetes does not model

Picture a platform serving thirty development teams. Each one needs namespaces, users and groups with different permissions, quota, network boundaries, required labels and annotations, standard platform configuration, secrets, GitOps access, cost visibility, development environments and a handful of integrations. The platform team has to work out how all of that relates to a team, and keep it consistent for as long as the team exists.

Kubernetes understands each of those resources individually. What it has no native concept of is the sentence that ties them together:

> This is Tenant A. These users belong to it, these namespaces belong to it, these resources are available to it — and the platform services around the cluster must respect the same boundary.

A namespace is an isolation boundary, not an organization, a department or a customer. MTO adds the abstraction that is missing: a `Tenant` that owns many namespaces and carries the membership, access rules, resource allocation, policies, templates, cost attribution and external integrations that belong to one organizational unit.

## The two ways teams usually solve it

**A cluster per team.** Isolation by duplication. It works, and then the bill arrives: every cluster needs its own control plane, ingress, monitoring, logging, policy engine, upgrade cycle and on-call rotation. Costs and operational load grow linearly with the number of teams, and the platform team spends its time on cluster fleet management instead of the platform.

**Namespaces, managed by hand.** Cheaper, but the governance lives in tickets and tribal knowledge. Someone creates the namespace, someone remembers the labels, someone else wires the role bindings, and the quota is set once and never revisited. Nothing is enforced, so the environment drifts from the day it is created — and nobody can answer "what does this team actually cost us?"

MTO takes the second path and removes what makes it fragile: it turns the tenant boundary into a declarative Kubernetes object and enforces it continuously.

## What changes

Onboarding a team becomes one merge request, not a runbook. A `Tenant` resource declares who is in the team, what they may consume, which namespaces they own and which standards those namespaces carry. MTO reconciles the rest — namespaces, RBAC, quotas, network isolation, templated resources — and keeps reconciling, so drift is corrected rather than discovered later.

The platform team's job shifts from executing requests to **defining guardrails**. Tenants self-serve inside them; the admission webhook rejects anything outside them at write time.

## The business argument

**Fewer clusters to run.** One governed cluster can safely host many teams, so you pay for one control plane, one monitoring stack and one upgrade cycle instead of many.

**Onboarding stops being a project.** A new team is a Tenant definition in Git, reviewed like any other change and applied by whatever GitOps tool you already use. No ticket queue, no snowflake namespaces.

**Cost becomes attributable.** Because the tenant — not the namespace — is the unit of ownership, it is also the unit of cost. Showback reports what each tenant and namespace consumed and what it was priced at, which is what turns "the cluster is expensive" into a conversation with a specific team.

**Idle spend is removable.** Development, test and demo environments are idle most of the week. Hibernation puts them to sleep on a schedule and wakes them on demand, so you stop paying for capacity nobody is using — and showback lets you prove the effect.

**Standards are enforced, not documented.** Templates push required resources — network policies, secrets, config, Helm-based application scaffolding — into every tenant namespace and keep them in sync. New namespaces are compliant with your baseline by construction.

**Governance follows the tenant out of Kubernetes.** Extensions project the same tenant boundary into the tools around the cluster — an ArgoCD AppProject scoped to the tenant's repositories and namespaces, Vault roles and policies scoped to its secrets. One definition, one boundary, instead of four systems you have to keep in sync by hand.

**Both audiences get an interface.** Administrators get a console for tenants, quotas, costs and capacity; tenant users get a self-service view of what they own. Both read and write the same Kubernetes objects, so there is no second source of truth.

## What MTO does not do

Honesty is more useful than a longer list:

- **It is namespace-based multi-tenancy, not control-plane-per-tenant.** Tenants who hold cluster credentials share the API server and the nodes. If a tenant needs its own API server or its own CRDs, that is a different isolation architecture — though MTO still governs whatever remains shared beneath it, and where tenants reach the platform through a product rather than through `kubectl`, the constraint does not apply at all. See [Deployment Models](deployment-models.md).
- **It does not replace your CI, GitOps or policy engine.** It defines and enforces the tenant boundary, and integrates with the tools you already run.
- **It is not a hosted service.** MTO runs in your cluster, on your infrastructure, under your control.

## Next

- [How MTO Works](how-it-works.md) — the reconciliation path, end to end
- [Key Capabilities](key-features.md) — what each capability area includes
- [Deployment Models](deployment-models.md) — where MTO fits alongside virtual and dedicated clusters
- [Use Cases](use-cases.md) — the shapes this takes in practice
- [Create a Tenant](../guides/create-tenant.md) — try it
