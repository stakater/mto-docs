# Docs screenshots — automated capture

Live MTO Console screenshots for these docs, captured with
[browser-runner](https://github.com/stakater-ab/browser-runner) (design:
`browser-runner/docs/docs-screenshot-automation.md`).

**Phase 1 (this PR): side-by-side validation.** Flows write PNGs into `captured/`
(gitignored) using the **same file names** as the existing images under
`content/images/`, so each new image sits next to the one it replaces and can be
compared directly. Nothing under `content/images/` is touched.

**Phase 2 (next): switch the docs over.** The existing hand-taken images move to a
folder of their own (kept, not deleted, so we can always diff against them), and
pages stop hardcoding image paths — each `![…](../images/x.png)` becomes a
`{{ screenshot: x }}` directive that the build resolves to that run's capture. The
directive is what makes the swap verifiable: an unreplaced directive is visible
text and fails the build, whereas a plain path silently renders a stale file.
Design + rationale: `browser-runner/docs/docs-screenshot-automation.md`.

## Layout

```
screenshots/
  README.md          # this file: inventory + how to run
  flows/             # one browser-runner YAML per console docs page
    _seed.yaml       #   setup: creates the shared template (runs first)
    _teardown.yaml   #   cleanup: deletes every docs-* object (runs last)
    _verify-clean.yaml #  optional: asserts the env has no leftovers (fatal)
  captured/          # capture output (gitignored) — compare against content/images/
  .env.example       # every variable, with which flow uses it and why
  capture.sh         # runs all flows (or one) via docker
```

## Running

Copy `.env.example` to `.env` (gitignored), fill in the portal URL and
credentials, then:

```sh
./screenshots/capture.sh            # _seed, all capture flows, _teardown
./screenshots/capture.sh tenants    # just flows/tenants.yaml
./screenshots/capture.sh _seed      # setup only
./screenshots/capture.sh _teardown  # cleanup only (safe to run any time)
```

A full run is **setup → capture → teardown**, all three as flows — no manual
steps, nothing outside the runner:

| Flow | Role |
|---|---|
| `_seed.yaml` | Creates `docs-seed-template` (parameter `image` defaulting to nginx + a ConfigMap manifest) — the template both instance flows instantiate. No docs screenshots (one diagnostic shot). |
| the 12 capture flows | Each takes its page's screenshots; objects whose **creation drawer is itself a docs image** are created by the flow (`docs-template`, `docs-instance`, `docs-cti-instance`, `docs-weekend-shutdown`, `docs-gpu-nodes`). |
| `_teardown.yaml` | Deletes every `docs-*` object in dependency order (instances → templates → schedule → node filter) and wakes the slept namespace. No screenshots. |

A failing flow never stops the run, so **teardown always gets its chance** — that's
why cleanup lives in one final flow rather than in each flow's own `after`. Every
teardown step is non-fatal, so a missing object doesn't block the rest; read the
`[after] … failed` lines to see what actually got removed. Single-flow runs do
**not** clean up: follow them with `./screenshots/capture.sh _teardown`.

In CI the same variables come from GitHub Actions secrets instead of `.env`.

**Until the runner additions ship in a release**, the flows need a locally
built image (they use the `wait` / `scroll-to` / `press` primitives and
animation-disabled screenshots from the browser-runner `screenshot-automation`
branch):

```sh
cd ../browser-runner/browser-runner && docker build -t browser-runner:dev .
cd - && RUNNER_IMAGE=browser-runner:dev ./screenshots/capture.sh
```

## Image standard

Every console screenshot is **2560 x 1600**: viewport `1280x800` at
`deviceScaleFactor: 2`, light color scheme. This matches the existing images
exactly (verified: all 57 console-page images are 2560x1600, except
`templateInstanceYAMLView.png` at 1864x968 — an outlier that gets re-captured
at the standard size).

## Inventory — MTO Console images (in scope, 57)

One flow per docs page (tenants is split in two for failure isolation); file
names of captures match `content/images/` exactly. Steps whose selector could
not be confirmed in the mto-console source are marked `VERIFY on first run` in
the flow files — the first capture run against the live env settles them.

| Flow (`flows/<name>.yaml`) | Docs page | Images | UI state captured |
|---|---|---|---|
| `dashboard` | `console/dashboard.md` | `dashboard.png` | Dashboard after login, cards + showback graph loaded |
| `tenants` | `console/tenants.md` | `tenants.png`, `graph-1.png`, `graph-2.png`, `graph-3.png`, `tenants_graph.png`, `tenantQuotaAggregatedView.png`, `tenantQuotaNamespaceView.png`, `tenantUtilizationNamespaces.png`, `tenantUtilizationNamespaceStats.png` | List page; tenant details: Graph / Quota (aggregated + namespace) / Utilization (list + namespace drill-down) |
| `tenants-create` | `console/tenants.md` | `tenant-overview.png`, `tenantAccessControl.png`, `tenantNamespaceTab.png`, `tenantMetadataCommonSandboxTab.png`, `tenantMetadataSpecificTab.png`, `YamlView.png` | Create-drawer walk (Overview filled, Access Control, Namespace, Metadata common + specific, YAML view) — **never submitted** |
| `namespaces` | `console/namespaces.md` | `namespaces.png` | Namespaces list |
| `quotas` | `console/quotas.md` | `quotas.png`, `quotaCreationMetadata.png`, `quotaCreationResourceQuota.png`, `quotaCreationLimitRangeContainer.png`, `quotaCreationLimitRangePod.png` | List page; create-drawer steps (Overview top + Resource Quota part, Container, Pod) — never submitted |
| `templates` | `console/templates.md` | `templates.png`, `templateCrudDrawerInfo.png`, `templateCrudDrawerParameters.png`, `templateHelmResource.png`, `templateResourceMappings.png`, `templateManifestResource.png`, `templateYAMLView.png` | **Self-seeding**: walks the create drawer with the old images' values (param `CIDR_IP`, Helm `hobo` chart, NetworkPolicy manifest), shooting each step, then really creates `docs-template`, shoots the list + YAML view, deletes it in cleanup |
| `template-instances` | `console/template-instances.md` | `templateInstances.png`, `templateInstanceDetails.png`, `templateInstanceCreateDrawer.png`, `templateInstanceCreateDrawerInfo.png`, `templateInstanceCreateDrawerParams.png`, `templateInstanceYAMLView.png` | **Self-seeding**: creates `docs-ti-template` (silently), then creates instance `docs-instance` via the drawer (shot at each step), shoots list-with-Deployed-row, details, YAML; deletes both in cleanup |
| `cluster-template-instances` | `console/cluster-template-instances.md` | `cti-tab.png`, `cti-details.png`, `cti-create.png`, `cti-create-param.png`, `cti-create-ns-selector.png`, `cti-yaml.png` | **Self-seeding**: creates `docs-cti-template` (silently), then `docs-cti-instance` scoped to only `DOCS_NAMESPACE` via its `kubernetes.io/metadata.name` label; shoots tab, details, YAML; deletes both in cleanup |
| `hibernation` | `console/hibernation.md` | `hibernation_table.png`, `sleepByLabels.png`, `sleepByNameSelection.png`, `hibernateByLabels.png`, `hibernateByNameSelection.png`, `manageHIbernationSchedules.png`, `createHibernationSchedule.png`, `createInterval.png` | **Self-seeding, really applies**: creates schedule `docs-weekend-shutdown` (via the + popup = `createInterval.png`), sleeps `DOCS_SLEEP_NS` and hibernates `DOCS_HIB_NS` by namespace name, then shoots the list with Sleeping/Hibernating badges + Wake up buttons; cleanup wakes the slept namespace and deletes the schedule (which wakes the hibernated one) |
| `capacity-planning` | `console/capacity-planning.md` | `add-node-filter.png`, `node-filtering-capacity-planning.png`, `node-filtering-capacity-planning-selected.png`, `capacity_planning.png`, `worker_pool.png`, `request_details.png` | Add-filter drawer; filter table; filter applied (chip visible); charts; node table; request table |
| `showback` | `console/showback.md` | `showback.png` | Cost Analysis page with data loaded |
| `configuration` | `console/configuration.md` | `integrationConfig.png` | IntegrationConfig page (admin-only view) |

## Where this runs in CI (phase 2)

Docs CI doesn't build the site itself — both `pull_request.yaml` and `push.yaml`
delegate to the shared `stakater/.github` versioned-doc workflows and pass a
**`PRE_BUILD_HOOK: make merge`**. That hook (`scripts/pre_build_merge.sh`) already
runs *after* the theme is prepared and *before* `mkdocs build`, which is exactly
the window a capture needs: the content tree exists, nothing has been rendered yet.

So capture hangs off the same hook — `make merge` gains a capture + inject step, or
the hook becomes `make docs-images` which does merge → capture → inject. No change
to the workflow files beyond secrets:

| Secret | Value |
|---|---|
| `CONSOLE_URL` | the docs-capture console URL (fixed per the release convention) |
| `CONSOLE_USER` / `CONSOLE_PASSWORD` | the capture-only admin credentials |
| `DOCS_TENANT`, `DOCS_NAMESPACE`, `DOCS_QUOTA`, `DOCS_HIB_TENANT`, `DOCS_SLEEP_NS`, `DOCS_HIB_NS` | as in `.env.example` (plain config, not secret) |

Two open decisions for that step, both noted in the design doc: whether captures
run on **every PR or only on main/release builds** (PR builds reusing the last
published images), and the **version-assertion gate** that fails the build when the
console behind `CONSOLE_URL` isn't the release being documented.

Until a tagged browser-runner image ships with the primitives these flows use
(`wait`, `scroll-to`, `press`, animation-disabled screenshots, abort-on-failure,
`optional`), CI must pin that image the same way local runs do via `RUNNER_IMAGE`.

## Known limits found while verifying the flows

- **Annotated originals can't be reproduced.** `graph-1.png`, `graph-2.png` and
  `graph-3.png` carry red callout rectangles drawn on *after* capture (around the
  Tenants sidebar item, the tenant row link, and the Graph tab). The runner
  reproduces the underlying UI only. Either re-annotate downstream, keep those
  three manual, or drop the callouts and use the plain captures.
- **Some originals are duplicates.** `worker_pool.png` and `request_details.png`
  are byte-identical (same md5) — one scroll position showing Node Capacity with
  Tenant Request Details below. `graph-2.png` is the tenants list (same view as
  `tenants.png`) and `graph-3.png` is the graph tab (same view as
  `tenants_graph.png`), differing only by the callouts. Candidates for
  consolidation in the docs.
- **`graph-1.png` is the Dashboard**, not the tenants list — the flow captures it
  right after login, before navigating to `/tenants`.
- **Testids in the deployed console lag the source.** `node-pool-name` and the
  access-control input testids don't exist in the running build, so those steps
  use structural or placeholder selectors instead.

## Console images NOT in phase 1 (3)

`mto-console-login.png` (1846x948), `mto-console-dashboard-0-tenants.png` and
`mto-console-bear-dashboard.png` (1853x954), referenced by the AWS-EKS /
Azure-AKS installation and validation pages. They are MTO Console screenshots
but depict installation-narrative data states (an empty console with **0
tenants**; a specific `bear` org) that contradict a seeded docs environment,
and they use a different, non-retina size. The login page itself is trivially
capturable; the dashboard states need a decision (re-shoot against the seeded
env and reword the pages, or leave manual). Deferred.

## Out of scope — not MTO Console

| Category | Images |
|---|---|
| OpenShift console (OperatorHub / OLM install + uninstall) | 17 images in `installation/openshift.md`, `installation/uninstalling.md` |
| Third-party UIs (ArgoCD, Mattermost, Azure AD, Keycloak, Vault mappers) | 7 images in `integrations/` |
| Diagrams / workflow art | `architecture-diagram.png`, `mto-vault-*-workflow.png` |
| Terminal/demo GIFs (kubectl plugin, tenant how-to guides) | 8 GIFs |

## Orphans (referenced by no page — flagged, NOT deleted)

`architecture.png`, `eks-access-config.png`, `eks-access-entry.png`,
`eks-denied-ns-access.png`, `eks-nodegroup.png`, `mto-console-dasboard.png`,
`mto-console-falcon-dashboard.png`, `noInterval.png`, `realm.png`,
`routes.png`, `tenant-operator-basic-overview.png`,
`tenant-operator-edit-overview.jpg`, `tenant-operator-owner-overview.jpg`,
`tenant-operator-view-overview.jpg`, `tenantsAdmin.png`, `tenants_yaml.png`,
`tenantUtilizationNamespaceWorkloads.png`, `to-architecture.png`,
`uninstall-from-ui-csv.png`

## Environment / seed-data contract

Most flows are now **self-seeding**: templates, template instances, CTIs, the
hibernation schedule, and the capacity-planning node filter are created by the
flows themselves under `docs-*` names and deleted again in their cleanup
(`after`) phase. What the environment must still provide:

- Tenant `DOCS_TENANT` with namespace `DOCS_NAMESPACE` (detail views, TI
  target, CTI selector)
- A quota named `DOCS_QUOTA` (Create Tenant drawer)
- Hibernation: tenant `DOCS_HIB_TENANT` with two currently-ACTIVE namespaces
  (`DOCS_SLEEP_NS`, `DOCS_HIB_NS`) and >=1 namespace label matching
  `DOCS_HIB_LABEL`
- Showback / Utilization / dashboard cost graph: accumulated metering data
  (time-series — only a long-running environment has this)

Mutations are bounded and reversed: the hibernation flow really sleeps /
hibernates its two namespaces (cleanup wakes them), instance flows deploy one
ConfigMap into `DOCS_NAMESPACE` (deleted with the instance). **If a run dies
before cleanup**, `docs-*` leftovers can remain and the next run's create hits
a name-already-exists error — delete the leftover objects in the console and
rerun.

The current alpha-dev environment already matches most of this: the existing
docs images were captured there as `mto@stakater.com` with tenants `logistics`
and `retail` (visible in the shots themselves). Docs text still references
`arsenal`/`alpha` in places — reconcile text vs seed during review.

## browser-runner additions these flows rely on

Shipped on the browser-runner `screenshot-automation` branch (build the dev
image, see [Running](#running)):

- **`wait` primitive** (bounded, max 30s) — settles JS chart animations
  (recharts) that no DOM state marks as finished.
- **`scroll-to` primitive** — frames below-the-fold sections (Node Capacity,
  Tenant Request Details) at the top of the viewport.
- **`press` primitive** — `Escape` to dismiss open dropdown portals before a
  shot.
- **Screenshots disable CSS animations by default** — drawer slide-ins and
  tab-highlight transitions are fast-forwarded, eliminating the
  mid-animation captures ("wrong tab highlighted", "drawer half open") from
  the first validation round.

Still open: promote the repeated 6-step Dex login to a `mto-console-login`
pack once selectors are proven against the live env.
