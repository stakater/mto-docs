# Use Cases

The first step in deciding how to share a cluster is being honest about who the tenants are. Two shapes cover most of it — teams inside one organization, and customers of a product — and they need different things from the boundary. MTO supports both with the same `Tenant` object; what changes is how much of the cluster the tenant is allowed to see.

## Multi-team tenancy

Several teams inside one organization share a cluster. Each runs one or more workloads, which often talk to workloads owned by other teams or in other clusters. Team members interact with Kubernetes directly through `kubectl`, or indirectly through a GitOps controller or release automation.

There is usually some trust between teams — but trust is not a control. Without enforced boundaries, one team's misconfigured deployment consumes the capacity another team was promised, and no one can say afterwards which team caused it.

**What MTO does here:**

* Each team is a Tenant. Its members come from your existing identity provider groups, so joining or leaving the team changes cluster access automatically.
* The team owns a fixed set of namespaces — typically `dev`, `staging`, `prod` prefixed with the tenant name — and can create more within the quota it was given.
* Sandboxes give each developer a personal namespace inside the team's boundary, instead of a shared "scratch" namespace nobody dares to clean up.
* Network isolation and node-pool restrictions keep teams out of each other's way at runtime.
* Showback attributes cluster cost to the team that incurred it, which is what makes capacity conversations concrete.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: payments
spec:
  quota: medium
  accessControl:
    owners:
      groups:
        - payments-leads
    editors:
      groups:
        - payments-developers
  namespaces:
    withTenantPrefix:
      - dev
      - staging
      - prod
    sandboxes:
      enabled: true
```

## Multi-customer tenancy

A vendor runs many instances of the same workload — one per customer. This is often called SaaS tenancy, though the pattern is not exclusive to SaaS: managed service providers and internal service teams hit the same shape.

Customers usually have no access to the cluster at all. Kubernetes is an implementation detail, used by the vendor to run the workloads. What matters is that one customer's instance cannot affect the others, and that the cost of serving each customer is known.

**What MTO does here:**

* Each customer is a Tenant, created by the same automation that handles their commercial onboarding — a Tenant definition committed to Git, applied by your GitOps tool.
* Quota per customer prevents one instance from starving the rest, and maps cleanly onto whatever plan the customer bought.
* Templates guarantee that every customer environment is provisioned identically: the same network policies, the same secrets, the same baseline resources. New customers are compliant with your standard by construction, not by checklist.
* Showback prices each customer's consumption, which turns cost-to-serve from an estimate into a number — and supports billing based on actual usage.
* Offboarding is a deletion: remove the Tenant and, if configured, its namespaces and external identities go with it.

## Patterns that show up in both

**Non-production environments that cost money while nobody uses them.** Development, test, demo and staging environments are idle most of the week. Hibernation sleeps them on a schedule and wakes them on demand, and showback shows the difference it made.

**Onboarding that used to be a project.** Whether the new arrival is a team or a customer, it is one Tenant definition reviewed like any other merge request — instead of a ticket, a runbook, and someone remembering the labels.

**Governance beyond Kubernetes.** The tenant boundary extends into ArgoCD and Vault, so a team or customer gets scoped GitOps and scoped secrets from the same definition rather than three systems configured by hand.

**A shared cluster instead of a fleet.** Both shapes are, at bottom, a decision not to run one cluster per tenant — and the reason that decision is usually the right one is the operational cost of the alternative. See [Why MTO](why-mto.md).

## Where MTO is not the right answer

If a tenant is genuinely untrusted and needs its own API server — hostile workloads, or a hard regulatory boundary between tenants — namespace-based multi-tenancy is not the tool. MTO is built for teams, departments and customers inside one organization's trust boundary.

## Next

* [Key Capabilities](key-features.md) — what each capability area includes
* [How MTO Works](how-it-works.md) — the reconciliation path, end to end
* [Create a Tenant](../multi-tenancy/guides/create-tenant.md) — start with one object
