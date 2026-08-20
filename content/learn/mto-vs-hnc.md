# MTO vs Hierarchical Namespace Controller (HNC)

## Introduction

The Hierarchical Namespace Controller (HNC) is a Kubernetes SIG Multi-Tenancy project that lets namespaces have parents, and propagates policy objects down the resulting tree.

It comes up in multi-tenancy searches because keeping policy consistent across a group of related namespaces is a real multi-tenancy problem. HNC solves that problem well. It is not a tenant model, and the difference matters when you are choosing a foundation for a platform.

---

## TL;DR

| Aspect | MTO | HNC |
|--------|-----|----------|
| Category | Tenant operating model | Namespace organization |
| Core abstraction | `Tenant` | Namespace hierarchy and child namespaces |
| Membership model | Owners, editors, viewers from IdP groups | None; propagates RBAC objects |
| Quota | At the tenant scope | Propagated objects, no tenant budget |
| Admission guardrails | Included | Not included |
| Cost attribution | Included | Not included |
| Lifecycle | Onboarding to offboarding | Namespace creation and deletion |
| Licence | Commercial | Open source, Kubernetes SIG |

---

## What is HNC?

HNC introduces a parent-child relationship between namespaces. A namespace can be declared the child of another, and HNC creates **child namespaces** beneath a parent on request.

Its central capability is **propagation**: configured object types — typically RBAC roles and bindings, network policies, resource quotas, secrets and config maps — are copied from a parent namespace to all of its descendants and kept in sync.

### Key Characteristics

- Namespace parent-child hierarchy
- Child-namespace creation delegated to namespace owners
- Policy object propagation down the tree
- Hierarchical RBAC, so access granted at a parent applies to descendants
- Open source, from Kubernetes SIG Multi-Tenancy

### Best For

- Keeping policy consistent across groups of related namespaces
- Delegating namespace creation without granting cluster-level permissions
- Teams that want a lightweight, Kubernetes-native building block
- Platforms whose tenancy model already exists and needs a propagation mechanism

---

## Core Architectural Difference

HNC organizes **namespaces**. MTO models **tenants**.

That sounds like a distinction without a difference until you list what a tenant carries that a namespace tree does not: membership tied to identity provider groups, a resource allocation defined once for the whole tenant, guardrails on what may be used, standard environments, a cost figure, a lifecycle, and a meaning in ArgoCD and the secrets platform.

HNC gives you a mechanism for making namespaces consistent. It does not give you the object that says *this is Tenant A, these people belong to it, this is its budget, and this is what its environments must look like* — so that object stays in your head, or in a spreadsheet.

The practical consequence: with HNC you still write the RBAC, still decide the quota for each branch, still apply the metadata, still attribute the cost. HNC makes sure whatever you wrote reaches the descendants.

---

## Detailed Comparison

### Grouping namespaces

HNC groups by hierarchy, which is expressive: a tenant can have a branch per environment, and policy can differ at each level. MTO groups by tenant ownership, a flat relationship — namespaces belong to a tenant, with metadata applied cluster-wide, per tenant or per namespace.

For deeply nested organizational structures, the HNC model is genuinely more expressive. For most platforms, the flat tenant relationship is what the organization actually looks like.

### Access control

HNC propagates RBAC objects down the tree, so a role binding at the parent applies to descendants. You write the role bindings.

MTO derives access from tenant membership: owners, editors and viewers, bound from users or existing groups, kept current as membership changes. Custom roles can replace the defaults where they do not fit.

### Resource allocation

HNC can propagate `ResourceQuota` objects, and provides hierarchical quota so the total for a branch can be capped.

MTO defines quota once at the tenant scope and shares it across all of the tenant's namespaces — on OpenShift through `ClusterResourceQuota`, elsewhere by aggregating at admission. Both address the "self-service namespaces must not multiply the budget" problem; MTO ties it to the tenant rather than to a branch of a namespace tree.

### Guardrails

MTO enforces at admission which storage classes, ingress classes, priority classes, image registries, service accounts and hostnames a tenant may use, each off by default.

HNC does not do admission policy of this kind; you would pair it with a policy engine.

### Standardization

Both distribute resources: HNC by propagating objects from a parent namespace, MTO by rendering templates — manifests, Helm charts or references to existing resources — into tenant namespaces and reconciling them.

Propagation in HNC is simpler and copies what already exists. MTO's templates are parameterized, so one definition serves many namespaces with different values.

### Cost, hibernation, integrations, console

Outside the scope of HNC entirely. It is a focused component, not a platform.

---

## What you assemble instead

HNC is one component of a platform, and an honest comparison counts the rest. Alongside it you would source a policy engine for admission guardrails, a templating mechanism for standardization, a cost stack with the labelling convention it depends on, something to sleep idle environments, GitOps and secrets tenancy maintained by hand, and an interface for tenant users. [What you assemble instead](kubernetes-multi-tenancy-tools.md#what-you-assemble-instead) sets out the trade capability by capability.

---

## How to Decide

### Choose HNC when

- You need policy consistency across related namespaces and nothing more
- Your organizational structure is genuinely hierarchical and you want to model it that way
- You want a small, open-source, Kubernetes-native building block
- A tenancy model already exists elsewhere in your platform

### Choose MTO when

- You need the tenant itself modelled, not only its namespaces
- Access should follow identity provider group membership without hand-written RBAC
- You need admission guardrails, cost attribution, hibernation or platform integrations
- You want tenant users to have a self-service interface
- You would otherwise be assembling HNC plus a policy engine plus cost tooling plus templating

---

## Using Them Together

They are not mutually exclusive, and both are namespace-based, so there is no isolation conflict. In practice most platforms pick one to own namespace policy, because two controllers propagating and reconciling objects into the same namespaces is a source of surprise rather than resilience.

If you already run HNC and are adding MTO, decide explicitly which one owns metadata and policy distribution rather than letting both do it.

---

## Key Takeaways

- HNC organizes namespaces; MTO models tenants. They are different categories.
- Propagation in HNC is a genuinely useful mechanism, and a mechanism is not a tenancy model.
- With HNC you still write the RBAC, set the quota and attribute the cost yourself.
- HNC is the better fit for deeply hierarchical organizational structures; MTO for the flat team-owns-namespaces shape most platforms actually have.
- If the requirement is governance, accountability and lifecycle rather than propagation, HNC is not the tool being asked for.

---

## Frequently Asked Questions (FAQ)

### Is HNC a multi-tenancy solution?

It is a multi-tenancy building block. It solves namespace organization and policy propagation, not tenant ownership, allocation, cost or lifecycle.

### Can HNC replace a tenant operator?

Not on its own. You would add a policy engine for admission guardrails, cost tooling for attribution, and a templating mechanism — and you would still be maintaining the tenant model outside the cluster.

### Does HNC support quota per tenant?

It supports hierarchical quota over a branch of the namespace tree, which achieves a similar outcome if that branch corresponds to a tenant. There is no tenant object for it to attach to.

### Is HNC still actively developed?

It is a Kubernetes SIG Multi-Tenancy project. As with any upstream project, check its current status in the repository before committing a platform to it.

### Can I use MTO and HNC together?

Technically yes, but decide which one owns namespace metadata and policy distribution. Two controllers reconciling the same objects is a maintenance problem.

---

## Keywords

MTO vs HNC
Hierarchical Namespace Controller
Kubernetes namespace hierarchy
child namespaces Kubernetes
HNC multi-tenancy
Kubernetes SIG multi-tenancy
