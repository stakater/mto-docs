# Hibernation

**Why pay for idle environments?**

A development or staging environment is idle for most of the week — nights, weekends, and every hour nobody is testing. The workloads keep running, the requests keep reserving capacity, and the bill keeps arriving. Scaling those environments down by hand does not survive contact with a real team.

Hibernation puts Deployments and StatefulSets to sleep and restores their previous replica counts on wake, either on a schedule or on demand.

## Two modes

- **Scheduled** — a sleep and wake cron pair, typically nights and weekends. The environment goes down and comes back without anyone remembering to do it.
- **Instant** — put an environment to sleep now, and leave it asleep until someone wakes it. Useful for an environment between projects.

## How it works

Hibernation is delivered by the **Hibernation Operator**, installed alongside MTO, and driven by a `ClusterResourceSupervisor` resource. It targets namespaces by label selector — and because MTO stamps `stakater.com/tenant: <tenant-name>` on every namespace it manages, one selector covers a whole tenant, including namespaces created after the supervisor was written.

A supervisor can also name the tenant's ArgoCD AppProjects, so the tenant's Applications sleep alongside its workloads instead of syncing them straight back up.

!!! note
    Before MTO v1.7, hibernation was configured with a `spec.hibernation` block on the `Tenant`. That field has been removed; use a `ClusterResourceSupervisor` instead.

## What it does not touch

Hibernation scales workloads; it does not delete them. Namespaces, quota, RBAC, PersistentVolumeClaims and configuration all survive a sleep, and a woken environment is the one you left — at the replica counts it had before.

## Where the saving shows up

Directly in [FinOps](../finops/overview.md). A non-production tenant asleep at nights and weekends is visible as a lower cost, which is what turns hibernation from a good idea into a number you can put in front of a budget holder.

## Guides

- [Hibernate a Tenant](guides/hibernate-tenant.md) — schedule a tenant's namespaces

## In the Console

- [Hibernation](../console/hibernation.md) — sleep, hibernate and wake from the UI
