# Capsule Alternatives

## Introduction

Capsule is a well-regarded open-source tenancy operator, and teams evaluating it usually want to know what else exists before committing.

The honest answer is that the alternatives fall into two groups, and only one of them is really an alternative. Some tools do the same job — namespace-based tenant governance. Others isolate control planes, which is a different job that is often mistaken for the same one.

---

## TL;DR

| Alternative | Same job as Capsule? | Licence | Notes |
|--------|-----|----------|----------|
| Multi-Tenant Operator (MTO) | Yes, and more | Commercial | Adds cost, hibernation, templates, integrations, console |
| Hierarchical Namespace Controller (HNC) | Partly | Open source | Propagates policy; no tenant model |
| vCluster | No | Open source | Virtual clusters — isolation, not governance |
| vCluster Platform (Loft) | No | Commercial | Platform over virtual clusters |
| Kamaji | No | Open source | Hosted control planes |
| Build it yourself | Yes | — | Common, and usually underestimated |

---

## What Capsule does

Capsule adds a `Tenant` custom resource to Kubernetes, groups namespaces under it, and enforces the tenant's policies on those namespaces — quota, network policy, admission constraints and access. A proxy component gives tenant users a view of cluster-scoped resources filtered to what their tenant owns.

It is focused, open source, and a CNCF Sandbox project. Teams look for alternatives usually for one of three reasons: they need capabilities beyond tenant governance, they want commercial support, or they are on OpenShift and want native handling of its constructs.

---

## Genuine alternatives

### Multi-Tenant Operator (MTO)

The closest direct comparison. Same layer, same abstraction, wider scope.

MTO is a commercial platform from Stakater built on a single `Tenant` definition that drives six capability areas: **multi-tenancy**, **templates**, **FinOps**, **hibernation**, **extensions** into the surrounding ecosystem, and a **console** for both administrators and tenant users. Tenancy is the foundation the other five stand on, not the extent of the product.

Its tenancy pillar — a `Tenant` owning namespaces, RBAC derived from identity provider groups, quota at the tenant scope, admission guardrails and network isolation — is where Capsule is a genuine alternative. The other five are where the comparison stops being like for like:

- **Standardization** — templates rendered into tenant namespaces and reconciled continuously, optionally enforced across every namespace of one tenant or all tenants
- **Cost attribution** — consumption sampled per namespace, aggregated to the tenant, priced with provider pricing on public cloud, and stored so periods can be compared
- **Hibernation** — idle workloads scaled down on a schedule or on demand, targeted by label so one schedule covers a whole tenant
- **Beyond Kubernetes** — an ArgoCD `AppProject` per tenant, and a path with policies and login roles per tenant in OpenBao or Vault
- **Console** — a permission-aware interface over the same objects for administrators and tenant users
- **OpenShift** — native `ClusterResourceQuota` enforcement

The trade is licensing: MTO is a commercial product with vendor support, where Capsule is open source. See [MTO vs Capsule](mto-vs-capsule.md) for the detailed comparison.

### Hierarchical Namespace Controller (HNC)

A partial alternative. HNC organizes namespaces into a hierarchy and propagates policy objects down it, which covers Capsule's policy-consistency ground.

It has no tenant abstraction — no membership, no allocation at the tenant scope, no lifecycle — so if what you valued in Capsule was the `Tenant` object, HNC is a step sideways rather than across. See [MTO vs HNC](mto-vs-hnc.md).

### Building it yourself

The most common alternative, and the one whose cost is most often underestimated. The primitives are all in Kubernetes; the work is in reconciliation, admission control, identity integration, cost attribution and keeping it correct across upgrades.

Worth doing if tenancy is your differentiator. Rarely worth it otherwise. See [How to Implement Kubernetes Multi-Tenancy](kubernetes-multi-tenancy-implementation.md) for what the list actually contains.

---

## Not really alternatives

These appear on every list of Capsule alternatives and address a different layer.

**vCluster** gives each tenant a virtual control plane with its own API server and CRDs. That is stronger isolation than Capsule provides — and it provides no tenant governance at all. Teams frequently run both.

**vCluster Platform (Loft)** is the commercial platform around virtual clusters: self-service provisioning, templates, sleep mode. Closer to a platform comparison, still built on a different primitive.

**Kamaji** and **HyperShift** run tenant control planes as workloads on a management cluster, giving each tenant a real cluster. Again: isolation, not governance — and Kamaji comes from Clastix, the same organization as Capsule, precisely because the two address different layers.

If you evaluate one of these against Capsule feature by feature you will conclude they are incomparable, which is correct. See [Deployment Models](../overview/deployment-models.md).

---

## Choosing

1. **Is your requirement governance or isolation?** Governance keeps you in Capsule's category — MTO, HNC, or building it. Isolation moves you to virtual clusters or hosted control planes.
1. **Do you need cost attributed to tenants?** Capsule and HNC do not address it; MTO does.
1. **Do standards need enforcing, not documenting?** Templates reconciled continuously are the difference between a baseline that holds and one that decays.
1. **Does the boundary need to reach ArgoCD and secrets management?** If yes, check whether the tool projects the tenant into them or leaves it to you.
1. **Is open-source licensing a requirement?** If it is, that shortens the list to Capsule, HNC or your own code.
1. **Are you on OpenShift?** Native handling of OpenShift constructs is worth checking specifically.

---

## Key Takeaways

- Most "Capsule alternatives" lists mix governance tools with isolation tools. Only the governance tools are alternatives.
- MTO is the closest comparison and the widest in scope; the trade is commercial licensing.
- HNC covers policy propagation but has no tenant abstraction.
- vCluster, Loft, Kamaji and HyperShift isolate control planes and leave governance unsolved.
- Building it yourself is viable and consistently underestimated.

---

## Frequently Asked Questions (FAQ)

### What is the best alternative to Capsule?

For the same job with wider scope, MTO. For an open-source policy-propagation building block, HNC. For stronger isolation rather than governance, a virtual cluster or hosted control plane — a different decision.

### Is there an open-source alternative to Capsule with cost visibility?

Not as a single project. You would pair a governance tool with separate cost tooling and maintain the labelling that tooling depends on.

### Is vCluster a Capsule alternative?

No. vCluster isolates control planes; Capsule governs tenancy within a cluster. They are frequently used together.

### Why would I move from Capsule to MTO?

Usually for cost attribution, standardization, hibernation, GitOps and secrets tenancy, a console for tenant users, native OpenShift support, or vendor support — rather than for core tenant governance, where the two are close.

### Can I migrate from Capsule to MTO?

Both express tenancy as custom resources over namespaces, so the concepts map. Running both at once is not advisable, since both claim namespace ownership and enforce policy through admission control.

---

## Keywords

Capsule alternatives
alternative to Capsule Kubernetes
Capsule vs MTO
open source Kubernetes multi-tenancy
Kubernetes tenant operator alternatives
namespace multi-tenancy tools
