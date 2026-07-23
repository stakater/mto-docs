# MTO docs migration to the shared structure

## Goal

Move mto-docs to the uniform documentation structure defined in
[`structure.md`](../../../structure.md), the same layout the
`template-operator-docs` and `hibernation-operator-docs` repos migrated to
recently. Making MTO's sections uniform is the point of the restructure: it lets
[`merge.yaml`](../../../merge.yaml) land sub-operator docs into MTO's sections
1:1 (guides→Guides, reference→Reference, concepts→Concepts) instead of mapping
into legacy section names.

Old bookmarks and inbound links must keep working, so every relocated page gets
a redirect.

## Approach

Phased (Option A):

1. **Shared-theme dependency** — enable the redirects plugin in the shared theme,
   bump the submodule here.
2. **Structural PR** — move/rename existing pages (git mv, history preserved),
   rewrite nav, add the redirect map, update `merge.yaml`, land net-new pages as
   stubs so `mkdocs build --strict` stays green.
3. **Authoring PRs** — write real content for the net-new and split pages.

This ships the uniform structure fast (unblocking merge.yaml) without gating on
content authoring, and mirrors how the sub-operators were migrated (structure
commit first, then content).

## Decisions

- **Scope:** restructure *and* author new pages, phased as above.
- **Guides:** flat, no thematic sub-groups. Merged sub-operator content
  (Templates, Finops) forms its own sub-groups via merge.yaml.
- **Integrations:** all integration pages flat under a single Integrations
  section (argocd, vault, devworkspace, mattermost, aws/azure-pricing). No
  Required/Optional split, no separate Extensions section.
- **Resource pages** (Tenant, Quota, Extensions, IntegrationConfig): split per
  page — conceptual prose to Concepts, spec detail to Reference › API Reference.
  Not auto-generated; reuse existing content.
- **Redirects:** one entry per moved page (comprehensive). Split pages redirect
  to their Concepts page.
- **Console:** MTO-specific section kept as-is.

## Target nav

```yaml
nav:
  - Overview:
      - Introduction: index.md
      - overview/key-features.md
      - overview/use-cases.md
      - overview/benefits.md
  - Concepts:
      - concepts/architecture.md
      - concepts/terminology.md
      - concepts/tenant.md
      - concepts/quota.md
      - concepts/extensions.md
      - concepts/integration-config.md
  - Getting Started:
      - getting-started/quick-start.md
      - Installation:
          - getting-started/installation/overview.md
          - getting-started/installation/openshift.md
          - getting-started/installation/kubernetes.md
          - On AKS:
              - Preparation: getting-started/installation/azure-aks/preparation.md
              - Installation: getting-started/installation/azure-aks/installation.md
              - Validation: getting-started/installation/azure-aks/validation.md
          - On EKS:
              - Preparation: getting-started/installation/aws-eks/preparation.md
              - Installation: getting-started/installation/aws-eks/installation.md
              - Validation: getting-started/installation/aws-eks/validation.md
      - getting-started/uninstalling.md
  - Console:
      - console/overview.md
      - console/dashboard.md
      - console/tenants.md
      - console/namespaces.md
      - console/hibernation.md
      - console/showback.md
      - console/quotas.md
      - console/templates.md
      - console/template-instances.md
      - console/cluster-template-instances.md
      - console/capacity-planning.md
      - console/configuration.md
  - Guides:
      - guides/create-tenant.md
      - guides/create-namespaces.md
      - guides/create-sandbox.md
      - guides/assign-metadata.md
      - guides/hibernate-tenant.md
      - guides/restrict-nodepool-per-tenant.md
      - guides/disable-intra-tenant-networking.md
      - guides/ingress-sharding.md
      - guides/host-validation.md
      - guides/storage-classes.md
      - guides/pod-priority-classes.md
      - guides/service-accounts.md
      - guides/image-registries.md
      - guides/custom-roles.md
      - guides/extend-default-roles.md
      - guides/delete-tenant.md
      - guides/templated-metadata-values.md
  - Integrations:
      - integrations/argocd.md
      - Vault:
          - integrations/vault/vault.md
          - integrations/vault/vault-ic.md
          - integrations/vault/vault-kc-entraid.md
      - integrations/devworkspace.md
      - integrations/mattermost.md
      - integrations/azure-pricing.md
      - integrations/aws-pricing.md
  - Reference:
      - API Reference:
          - reference/api/tenant.md
          - reference/api/quota.md
          - reference/api/extensions.md
          - reference/api/integration-config.md
      - reference/configuration.md
      - reference/cli.md
      - reference/rbac.md
      - reference/metrics.md
      - reference/webhooks.md
      - reference/security-model.md
  - Troubleshooting: troubleshooting.md
  - Release Notes: release-notes.md
  - Pricing: pricing.md
  - EULA: eula.md
```

## File moves (git mv, history preserved)

| Old path | New path |
|---|---|
| `about/key-features.md` | `overview/key-features.md` |
| `about/use-cases.md` | `overview/use-cases.md` |
| `about/benefits.md` | `overview/benefits.md` |
| `architecture/architecture.md` | `concepts/architecture.md` |
| `architecture/concepts.md` | `concepts/terminology.md` |
| `kubernetes-resources/tenant/tenant-overview.md` | `concepts/tenant.md` (prose) + new `reference/api/tenant.md` (spec) |
| `kubernetes-resources/quota.md` | `concepts/quota.md` + new `reference/api/quota.md` |
| `kubernetes-resources/extensions.md` | `concepts/extensions.md` + new `reference/api/extensions.md` |
| `kubernetes-resources/integration-config.md` | `concepts/integration-config.md` + new `reference/api/integration-config.md` |
| `installation/overview.md` | `getting-started/installation/overview.md` |
| `installation/openshift.md` | `getting-started/installation/openshift.md` |
| `installation/kubernetes.md` | `getting-started/installation/kubernetes.md` |
| `installation/azure-aks/*` | `getting-started/installation/azure-aks/*` |
| `installation/aws-eks/*` | `getting-started/installation/aws-eks/*` |
| `installation/uninstalling.md` | `getting-started/uninstalling.md` |
| `cli/kubectl-plugin.md` | `reference/cli.md` |
| `kubernetes-resources/tenant/how-to-guides/*.md` (18) | `guides/*.md` |
| `changelog.md` | `release-notes.md` |
| `console/*`, `integrations/*`, `pricing.md`, `eula.md`, `troubleshooting.md`, `index.md` | unchanged |

For the 4 resource-page splits: the structural PR moves the whole page to
`concepts/` and lands `reference/api/*.md` as a stub. The actual prose/spec split
happens in the authoring phase, keeping the structural diff mechanical.

## New pages

Land as stubs (title + one-line intro + `<!-- TODO -->`) in the structural PR;
authored in phase 2.

| Page | Phase-2 source |
|---|---|
| `getting-started/quick-start.md` | condensed install + first tenant |
| `reference/configuration.md` | tenant-operator `helm-charts`, `config/manager` env |
| `reference/rbac.md` | tenant-operator `config/rbac/*` |
| `reference/metrics.md` | `config/network-policy/allow-metrics-traffic.yaml`, metrics config |
| `reference/webhooks.md` | `config/webhook/manifests.yaml`, `docs/validation-webhook.md` |
| `reference/security-model.md` | synthesized from RBAC + webhooks + isolation |
| `reference/api/{tenant,quota,extensions,integration-config}.md` | spec split from moved concept pages |

Source repo for authoring: `~/Documents/work/tenant-operator` (main / current
release branch).

## Redirects

Add the `mkdocs-redirects` plugin with a `redirect_maps` block to
[`theme_override/mkdocs.yml`](../../../theme_override/mkdocs.yml), one entry per
moved page (old path → new path). Every path in the File moves table gets a
redirect — including all 18 guides, the aws-eks/azure-aks installation
sub-pages, and the split resource pages (which redirect to their Concepts page).
The `redirect_maps` block is generated directly from the move table so no path
is missed. The plugin emits a small HTML redirect stub at each old URL using relative links,
so redirects work under mike's version prefix, the nginx image, and GH Pages PR
previews.

### Cross-repo dependency

The build installs Python deps only from `theme_common/requirements.txt`, and
`theme_common` is the shared-theme submodule
(`stakater/stakater-docs-mkdocs-theme`, currently v0.0.60). The plugin is not
installed today. Required:

1. Add `mkdocs-redirects>=1.2.1,<2.0.0` to the shared theme's `requirements.txt`
   (may already be done — the sub-operators depend on it; verify first).
2. Bump the `theme_common` submodule here to that commit.

A copy of the sub-operators' `shared-theme-redirects.md` note goes in MTO's
`docs/superpowers/`. Until the shared change lands: `pip install mkdocs-redirects`
locally, or comment out the plugin block to build without redirects.

## merge.yaml update

Point `into`/`under` at the new sections so sub-operator content lands 1:1:

- Template & Hibernation `guides/**` → `into: guides`, `under: Guides`.
- Template & Hibernation reference/api → `into: reference/api`, `under: Reference`
  (was `kubernetes-resources` / `API Reference`).
- Hibernation `integrations/**` → `into: integrations`, `under: Integrations`
  (was `under: Extensions` — the Extensions section no longer exists).

## Verification

- **Structural PR:** `mkdocs build --strict` = 0 warnings (with
  `pip install mkdocs-redirects` locally until the theme dep lands); every old URL
  resolves via a redirect stub; existing 34 unit tests pass; merge dry-run against
  live sub-operator branches still builds.
- **Authoring PRs:** author each new/split page; re-run `--strict`.

## Sequencing

1. Shared-theme dependency + submodule bump.
2. Structural PR (moves, nav, redirects, merge.yaml, stubs).
3. Authoring PRs (new pages + resource-page splits).
