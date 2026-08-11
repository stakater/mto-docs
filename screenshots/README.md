# Docs screenshots — automated capture

Live MTO Console screenshots for these docs, captured with browser-runner
(design: `browser-runner/docs/docs-screenshot-automation.md`).

The 57 console screenshots aren't referenced by path any more. Each
`![…](../images/x.png)` in `content/console/*.md` is a `{{ screenshot: x }}` directive
that the build swaps for that run's capture. The old hand-taken images live in
`baseline/`, kept for diffing; the build never reads them.

Why a directive and not just the path: a path can silently render a stale file. A
directive can only resolve to an image captured for it, and fails the build if there
isn't one.

## How resolution works

`screenshots/mkdocs_hook.py` (registered under `hooks:` in
`theme_override/mkdocs.yml`) runs during `mkdocs build`:

1. copies every referenced image from `captured/` into `content/images/generated/`
2. replaces each directive with an image link, in memory — source files are never
   touched. No capture for a directive means the build fails and names the page.

`captured/` is the only source. No fallback to `baseline/`, because falling back
would publish a stale screenshot, which is what this setup exists to prevent.
Those captures are committed, so a build never has to capture to resolve them —
see [Where this runs in CI](#where-this-runs-in-ci).

A hook is used rather than `mkdocs-macros-plugin` for two reasons: macros is an
external dependency, and it would have to be added to `theme_common/requirements.txt`
(an upstream submodule); and it enables Jinja2 on every page, which would try to
evaluate the `{{ .Role }}` / `{{ issuer }}` templating examples in the integration
docs and break the build. The hook matches only `{{ screenshot: name }}`.

`make screenshots-check` reports any directive that fails to resolve, plus any
capture no page uses. It writes nothing, so it's the gate to run in CI.

## Layout

```
screenshots/
  README.md          # this file: inventory + how to run
  flows/             # one browser-runner YAML per console docs page
    _seed.yaml       #   setup: creates the shared template (runs first)
    _teardown.yaml   #   cleanup: deletes every docs-* object (runs last)
    _verify-clean.yaml #  optional: asserts the env has no leftovers (fatal)
  baseline/          # archive of the previous hand-taken images (diff reference only)
  captured/          # capture output, committed — what the directives resolve to
  inject.py          # --check gate; can also resolve directives on disk
  mkdocs_hook.py     # resolves directives during mkdocs build (in memory)
  config.env         # checked-in config: console URL, tenant/namespace/quota names
  .env.example       # template for .env — credentials only
  capture.sh         # runs all flows (or one) via docker
```

## Running

Copy `.env.example` to `.env` and fill in the credentials, then:

```sh
./screenshots/capture.sh            # _seed, all capture flows, _teardown
./screenshots/capture.sh tenants    # just flows/tenants.yaml
./screenshots/capture.sh _seed      # setup only
./screenshots/capture.sh _teardown  # cleanup only (safe to run any time)
```

A full run is setup → capture → teardown, all as flows:

| Flow | Role |
|---|---|
| `_seed.yaml` | Creates `docs-seed-template`, the template both instance flows instantiate. |
| the 12 capture flows | Take their page's screenshots. Anything whose create drawer is itself a docs image gets created by the flow (`docs-template`, `docs-instance`, `docs-cti-instance`, `docs-weekend-shutdown`, `docs-gpu-nodes`). |
| `_teardown.yaml` | Deletes every `docs-*` object — instances, then templates, then the schedule and node filter — and wakes the slept namespace. |

A failing flow doesn't stop the run, so teardown always gets to run. Its steps are
non-fatal too, so one missing object doesn't block the rest — which also means its
PASS tells you nothing; read the `[after] … failed` lines. Single-flow runs don't
clean up, so follow them with `./screenshots/capture.sh _teardown`.

`config.env` is checked in and holds everything that isn't a credential (console URL,
tenant, namespace, quota names). `.env` holds only `CONSOLE_USER` and
`CONSOLE_PASSWORD`, and can override anything in `config.env` for a one-off run.
In CI those two credentials are the only secrets — the rest comes from `config.env`.

`capture.sh` uses `ghcr.io/stakater/browser-runner:latest`. Override it to test
against a different build:

```sh
RUNNER_IMAGE=browser-runner:dev ./screenshots/capture.sh
```

## Image standard

**2560 x 1600** — a `1280x800` viewport at `deviceScaleFactor: 2`, light theme. Set in
the `viewport:` block of every flow, so all captures come out the same size and theme.

## Flows and the images they produce

One flow per docs page, except tenants which is split in two so a failure in the
create-drawer walk can't lose the detail-page shots.

| Flow (`flows/<name>.yaml`) | Docs page | Images | UI state captured |
|---|---|---|---|
| `dashboard` | `console/dashboard.md` | `dashboard.png` | Dashboard after login, metric cards + capacity chart loaded |
| `tenants` | `console/tenants.md` | `tenants.png`, `graph-1.png`, `graph-2.png`, `graph-3.png`, `tenants_graph.png`, `tenantQuotaAggregatedView.png`, `tenantQuotaNamespaceView.png`, `tenantUtilizationNamespaces.png`, `tenantUtilizationNamespaceStats.png` | List page; tenant details: Graph / Quota (aggregated + namespace) / Utilization (list + namespace drill-down) |
| `tenants-create` | `console/tenants.md` | `tenant-overview.png`, `tenantAccessControl.png`, `tenantNamespaceTab.png`, `tenantMetadataCommonSandboxTab.png`, `tenantMetadataSpecificTab.png`, `YamlView.png` | Create-drawer walk: Overview (quota picked, name still empty), Access Control, Namespace, Metadata, Specific expanded, YAML. Never submitted |
| `namespaces` | `console/namespaces.md` | `namespaces.png` | Namespaces list |
| `quotas` | `console/quotas.md` | `quotas.png`, `quotaCreationMetadata.png`, `quotaCreationResourceQuota.png`, `quotaCreationLimitRangeContainer.png`, `quotaCreationLimitRangePod.png` | List page; create-drawer steps (Overview top + Resource Quota part, Container, Pod) — never submitted |
| `templates` | `console/templates.md` | `templates.png`, `templateCrudDrawerInfo.png`, `templateCrudDrawerParameters.png`, `templateHelmResource.png`, `templateResourceMappings.png`, `templateManifestResource.png`, `templateYAMLView.png` | Walks the create drawer filling each step (param `CIDR_IP`, Helm `hobo` chart, NetworkPolicy manifest), then really creates `docs-template` and shoots the list + YAML view |
| `template-instances` | `console/template-instances.md` | `templateInstances.png`, `templateInstanceDetails.png`, `templateInstanceCreateDrawer.png`, `templateInstanceCreateDrawerInfo.png`, `templateInstanceCreateDrawerParams.png`, `templateInstanceYAMLView.png` | Shoots the create drawer untouched at each step, then really creates `docs-instance` from `docs-seed-template` and shoots the Deployed row, details and YAML |
| `cluster-template-instances` | `console/cluster-template-instances.md` | `cti-tab.png`, `cti-details.png`, `cti-create.png`, `cti-create-param.png`, `cti-create-ns-selector.png`, `cti-yaml.png` | Same, cluster-scoped: creates `docs-cti-instance` from `docs-seed-template`, its selector targeting only `DOCS_NAMESPACE` so it can't fan out across the cluster |
| `hibernation` | `console/hibernation.md` | `hibernation_table.png`, `sleepByLabels.png`, `sleepByNameSelection.png`, `hibernateByLabels.png`, `hibernateByNameSelection.png`, `manageHIbernationSchedules.png`, `createHibernationSchedule.png`, `createInterval.png` | **Self-seeding, really applies**: creates schedule `docs-weekend-shutdown` (via the + popup = `createInterval.png`), sleeps `DOCS_SLEEP_NS` and hibernates `DOCS_HIB_NS` by namespace name, then shoots the list with Sleeping/Hibernating badges + Wake up buttons; cleanup wakes the slept namespace and deletes the schedule (which wakes the hibernated one) |
| `capacity-planning` | `console/capacity-planning.md` | `add-node-filter.png`, `node-filtering-capacity-planning.png`, `node-filtering-capacity-planning-selected.png`, `capacity_planning.png`, `worker_pool.png`, `request_details.png` | Add-filter drawer; filter table; filter applied (chip visible); charts; node table; request table |
| `showback` | `console/showback.md` | `showback.png` | Cost Analysis page with data loaded |
| `configuration` | `console/configuration.md` | `integrationConfig.png` | IntegrationConfig page (admin-only view) |

## Where this runs in CI

Capture is its own workflow, `screenshots.yaml`. It runs when a PR is **approved**,
or manually from the Actions tab on any branch, and **commits the images it takes**.
Everything downstream then resolves the directives from the branch.

| Workflow | Captures? |
|---|---|
| `screenshots.yaml` | yes — on approval, or a manual run |
| `pull_request.yaml` | no — uses the committed images |
| `push.yaml` | only if the merged PR never captured |

`push.yaml` decides on the `screenshots-captured` label that a capture adds: with it,
the images are already fresh and it skips; without it, it captures so published
images are never stale. Since approval is required to merge, that fallback only fires
for a PR merged without a successful capture.

If a flow fails, nothing is committed — a broken run can't half-update the set.

Credentials come from the `CONSOLE_USER` / `CONSOLE_PASSWORD` repo secrets.


Only images under `content/console/` are automated. Everything else stays
hand-made: the OpenShift install pages, third-party UIs in `integrations/`,
diagrams, and the demo GIFs.

## What the environment needs

Templates, instances, the hibernation schedule and the node filter are created by
the flows under `docs-*` names and deleted by `_teardown`. What must already exist:

- tenant `DOCS_TENANT` with namespace `DOCS_NAMESPACE`
- a quota named `DOCS_QUOTA`
- tenant `DOCS_HIB_TENANT` with `DOCS_SLEEP_NS` and `DOCS_HIB_NS` both **Active**
  (the drawer skips namespaces that are already asleep), and at least one
  namespace label to pick in the Apply drawer
- accumulated metering data for the Cost Analysis and Utilization shots

Mutations are bounded: hibernation really sleeps its two namespaces, and the
instance flows deploy one ConfigMap into `DOCS_NAMESPACE`. `_teardown` reverses all
of it. **If a run dies before teardown**, the leftover `docs-*` objects make the
next run fail on a duplicate name — run `./screenshots/capture.sh _teardown` first.

