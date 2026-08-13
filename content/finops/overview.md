# FinOps

**Who is consuming what, and what does it cost?**

Most Kubernetes cost conversations stall in the same place: the bill is one number, and nobody can say which team caused it. Splitting it usually depends on a labelling convention that someone has to apply and nobody fully applies, so attribution is only ever as good as the discipline behind it.

MTO does not depend on that discipline. A namespace exists because a tenant declared it, and every namespace MTO manages carries `stakater.com/tenant`. There is no unattributed remainder to argue about, and no second tagging scheme to maintain alongside the tenant model.

## What it covers

| Area | What it answers |
|---|---|
| Showback | What did each tenant and each namespace consume, and what did it cost? |
| Cost and usage analysis | How is that changing over time, and where are requests far above actual use? |
| Capacity planning | What do the nodes provide, what is already committed, and what is left? |

## How the number is produced

MTO measures rather than estimates from node count:

1. **Sampled** — Prometheus and `kube-state-metrics` record actual usage and requests per namespace over time.
1. **Aggregated** — usage is rolled up to the tenant, because the tenant is the unit of ownership.
1. **Priced** — OpenCost applies rates to the sampled usage. On public cloud, MTO can use provider pricing so the figures track what you are actually billed.
1. **Stored** — results are written to MTO's PostgreSQL instance, so history survives Prometheus retention and periods can be compared.

The FinOps stack — OpenCost, Prometheus, `kube-state-metrics`, the FinOps Operator and Gateway, and PostgreSQL — is provisioned by MTO's Pilot controller, so this works after installation rather than after a separate integration project.

## What it is used for

**Showback.** Give each team its own consumption, in money. That is usually enough to change behaviour on its own — teams reduce oversized requests once the number has their name on it.

**Chargeback.** Bill internal departments or external customers from measured consumption instead of an allocation formula. Because a customer is a tenant, cost-to-serve is a figure you read rather than model.

**Proving savings.** [Hibernation](../hibernation/overview.md)'s effect shows up here as a lower cost, not a claim.

## Enable it

Cost visibility is part of the console stack. In the IntegrationConfig:

```yaml
  components:
    console: true
    showback: true
```

See [Dashboard](../console/dashboard.md) for the full set of components and their ingress configuration.

## Guides

- [AWS Pricing](guides/aws-pricing.md) — use AWS standard or spot pricing
- [Azure Pricing](guides/azure-pricing.md) — use Azure standard or customer-specific pricing

## In the Console

- [Cost Analysis](../console/showback.md) — consumption by tenant and namespace
- [Capacity Planning](../console/capacity-planning.md) — the supply side
