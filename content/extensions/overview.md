# Extensions

**What about the tools surrounding Kubernetes?**

A tenant boundary that stops at the Kubernetes API is only half a boundary. The team that owns `bluesky-dev` also needs an ArgoCD project scoped to its namespaces, a Vault path only it can read, and a workspace it can develop in. Configured by hand, those drift away from the Tenant the moment membership changes — and then the cluster says one thing while ArgoCD and Vault say another.

Extensions project the same Tenant definition into the tools around the cluster, so you maintain one boundary instead of several.

## What it covers

| System | What MTO provides |
|---|---|
| ArgoCD | An `AppProject` per tenant — the repositories it may deploy from, the namespaces it may deploy into, and cluster-resource allow-lists |
| HashiCorp Vault | A path, a role and policies per tenant, bound to the tenant's owners, editors and viewers |
| DevWorkspace | Sandbox namespaces stamped with the labels and annotations that make them cloud development environments |
| Mattermost | A team and channels per tenant, with membership following tenant membership |

## Four mechanisms, not one

MTO extends into surrounding systems in four different ways, and which one applies determines *where* you configure it — per tenant, cluster-wide, through namespace metadata, or by labelling the Tenant for a companion operator.

Only the first of those uses the `Extensions` custom resource, whose spec today carries ArgoCD configuration and nothing else. Vault, for example, is configured in the IntegrationConfig, not on `Extensions`.

[Extensions concepts](concepts/extensions.md) sets out all four with the configuration for each.

## Why it matters

Access to a cluster is rarely the whole of what a team needs. If granting it means a ticket to the GitOps team and another to the secrets team, the self-service story ends at the namespace. Extensions are what make onboarding a tenant a single change rather than a sequence of them — and offboarding one just as short.

## Concepts

- [Extensions](concepts/extensions.md) — the four mechanisms and where each is configured

## Guides

- [ArgoCD Multi-Tenancy](guides/argocd.md)
- [Vault Multi-Tenancy](guides/vault.md)
- [DevWorkspace](guides/devworkspace.md)
- [Mattermost](guides/mattermost.md)
