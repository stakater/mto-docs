---
head:
  - - meta
    - name: keywords
      content: Kubernetes multi-tenancy, multi-tenant Kubernetes, Kubernetes tenant management, namespace management, Kubernetes RBAC, Kubernetes cost showback, workload hibernation, OpenShift multi-tenancy
---

# Multi-Tenant Operator

**Turn Kubernetes into a self-service multi-tenant platform.**

MTO enables platform teams to securely serve multiple teams, departments or customers from Kubernetes, while providing centralized access control, resource management, cost visibility, workload hibernation, standardized environments and integrations with the surrounding platform ecosystem.

Platform administrators define the guardrails. Tenants get self-service within those boundaries.

## What MTO provides

| Capability | Customer problem | What MTO provides |
|---|---|---|
| **Multi-Tenancy** | How do I safely share Kubernetes? | Tenants, namespaces, RBAC, quotas, isolation and self-service |
| **Templates** | How do I standardize environments? | Reusable and enforceable Kubernetes/Helm-based templates |
| **FinOps** | Who is consuming what, and what does it cost? | Tenant/namespace showback, usage and capacity insights |
| **Hibernation** | Why pay for idle environments? | Scheduled and manual workload sleep and wake |
| **Extensions** | What about the tools surrounding Kubernetes? | Extend tenant boundaries into ArgoCD, Vault and other platform services |
| **Console** | How do operators and tenants actually use all this? | A centralized visual experience for tenants, namespaces, costs, quotas, templates and hibernation |

## The idea in one object

Everything above hangs off a single Kubernetes resource: the **Tenant**.

You declare who is in the tenant, what it may consume, which namespaces it owns and what standards those namespaces carry. MTO then continuously reconciles the rest — namespaces, RBAC bindings, quotas, network isolation, templated resources, and the tenant's matching identities in ArgoCD and Vault.

```yaml
apiVersion: tenantoperator.stakater.com/v1beta3
kind: Tenant
metadata:
  name: bluesky
spec:
  quota: small
  accessControl:
    owners:
      users:
        - anna@aurora.org
  namespaces:
    withTenantPrefix:
      - dev
      - staging
    sandboxes:
      enabled: true
```

Because the tenant — not the namespace — is the unit of ownership, it is also the unit of *cost*, of *identity* and of *lifecycle*. That is what makes showback, hibernation and the ecosystem integrations fall out of the same definition instead of being four separate tools you have to keep in sync.

See [How MTO Works](overview/how-it-works.md) for the full reconciliation path.

## Where to go next

### Evaluating MTO

- [How MTO Works](overview/how-it-works.md) — the moving parts, end to end
- [Why MTO](overview/why-mto.md) — the business argument
- [Key Capabilities](overview/key-features.md) — capability by capability
- [Use Cases](overview/use-cases.md) — the shapes this takes in practice

### Running MTO

- [Installation](getting-started/installation/overview.md) — install on OpenShift, Kubernetes, AKS or EKS
- [Create a Tenant](multi-tenancy/guides/create-tenant.md) — your first tenant
- [Console](console/overview.md) — the UI for administrators and tenant users
- [Architecture](overview/architecture.md) — components and controllers
