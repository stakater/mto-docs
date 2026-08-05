# MTO docs structure migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure mto-docs to the shared layout in `structure.md` (moving existing pages, rewriting nav, adding redirects for every moved path, updating merge.yaml), landing net-new pages as stubs.

**Architecture:** Pure structural migration. Existing `.md` files are relocated with `git mv` (history preserved) and the nav in `theme_override/mkdocs.yml` is rewritten section by section so `mkdocs build --strict` stays green after every task. New pages land as buildable stubs. Redirects are added via the `mkdocs-redirects` plugin. `merge.yaml` is repointed so sub-operator docs land 1:1 into the new sections. Content authoring of the stubs is out of scope (separate follow-up plans).

**Tech Stack:** MkDocs + mkdocs-material, mkdocs-redirects, Python (merge_docs.py), pytest, git submodule (shared theme).

## Global Constraints

- `mkdocs build --strict` must pass with **0 warnings** after every task.
- `theme_common` is a git submodule (`stakater/stakater-docs-mkdocs-theme`); do not edit its files in this repo — depend on it and bump the pin.
- Redirect entries use **source file paths** (e.g. `about/key-features.md: overview/key-features.md`), one per moved page.
- Nav edits go only in `theme_override/mkdocs.yml`. The build combines it with the theme config into `mkdocs.yml`.
- Preserve git history on moves: use `git mv`, never delete+recreate.
- No commits are pushed; local commits only (per user preference, no co-author trailer).

## Reusable commands

**One-time environment setup (run before Task 1 verification):**

```bash
cd ~/Documents/work/mto-docs
git submodule update --init --recursive
python3 -m venv .venv 2>/dev/null || true
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r theme_common/requirements.txt -r requirements-dev.txt mkdocs-redirects
```

**BUILD (MTO-only, no merge) — the per-task verification:**

```bash
.venv/bin/python theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml
.venv/bin/python -m mkdocs build --strict
```
Expected: `INFO - Documentation built` with no `WARNING`/`ERROR` lines.

---

### Task 1: Enable the redirects dependency

**Files:**
- Create: `docs/superpowers/shared-theme-redirects.md`

The `mkdocs-redirects` plugin is not installed by CI (build installs only from the shared-theme submodule's `requirements.txt`). This task documents the required shared-theme change and unblocks local builds. The plugin block itself is added in Task 9.

- [ ] **Step 1: Check whether the shared theme already ships the plugin**

Run:
```bash
grep -n "mkdocs-redirects" theme_common/requirements.txt || echo "NOT PRESENT"
```
If present: the dependency is done upstream; note the current submodule commit and skip Step 3's upstream action (still keep the note file). If `NOT PRESENT`: proceed.

- [ ] **Step 2: Write the shared-theme note**

Create `docs/superpowers/shared-theme-redirects.md`:

```markdown
# Enabling redirects — required shared-theme change

The docs restructure moved many pages. To keep old bookmarks working,
`theme_override/mkdocs.yml` declares the `mkdocs-redirects` plugin with a
`redirect_maps` block (old path -> new path). At build time the plugin emits a
small HTML redirect stub at each old URL.

## What must be done in the shared theme repo

The build installs Python deps only from `theme_common/requirements.txt`, which
lives in the shared theme submodule:

- Repo: `stakater/stakater-docs-mkdocs-theme` (the `theme_common` submodule)
- File: `requirements.txt`
- Change: add `mkdocs-redirects>=1.2.1,<2.0.0`

After that lands, bump the `theme_common` submodule here
(`git submodule update --remote theme_common`) and CI + local builds pick up the
plugin automatically.

## Until the shared change lands

Local unblock (does not fix CI): `pip install mkdocs-redirects`. Or comment out
the `plugins: redirects` block in `theme_override/mkdocs.yml` to build without
redirects.
```

- [ ] **Step 3: Run environment setup and confirm the plugin imports**

Run the one-time environment setup block above, then:
```bash
.venv/bin/python -c "import mkdocs_redirects; print('ok')"
```
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/shared-theme-redirects.md
git commit -m "docs: note shared-theme mkdocs-redirects dependency for restructure"
```

---

### Task 2: Move Overview pages

**Files:**
- Move: `content/about/{key-features,use-cases,benefits}.md` -> `content/overview/`
- Modify: `theme_override/mkdocs.yml` (Overview nav block)

- [ ] **Step 1: Move the files**

```bash
mkdir -p content/overview
git mv content/about/key-features.md content/overview/key-features.md
git mv content/about/use-cases.md   content/overview/use-cases.md
git mv content/about/benefits.md    content/overview/benefits.md
rmdir content/about 2>/dev/null || true
```

- [ ] **Step 2: Update the Overview nav block in `theme_override/mkdocs.yml`**

Replace the existing `- Overview:` block with:
```yaml
  - Overview:
      - Introduction: index.md
      - overview/key-features.md
      - overview/use-cases.md
      - overview/benefits.md
```

- [ ] **Step 3: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 4: Commit**

```bash
git add content/overview theme_override/mkdocs.yml
git commit -m "docs: move Overview pages to overview/"
```

---

### Task 3: Move Concepts pages

**Files:**
- Move: `content/architecture/architecture.md` -> `content/concepts/architecture.md`
- Move: `content/architecture/concepts.md` -> `content/concepts/terminology.md`
- Move: `content/kubernetes-resources/tenant/tenant-overview.md` -> `content/concepts/tenant.md`
- Move: `content/kubernetes-resources/quota.md` -> `content/concepts/quota.md`
- Move: `content/kubernetes-resources/extensions.md` -> `content/concepts/extensions.md`
- Move: `content/kubernetes-resources/integration-config.md` -> `content/concepts/integration-config.md`
- Modify: `theme_override/mkdocs.yml` (add Concepts block). The matching `reference/api/*` spec stubs are created in Task 7 when they enter the nav, so no intermediate not-in-nav warning occurs.

- [ ] **Step 1: Move the concept pages**

```bash
mkdir -p content/concepts
git mv content/architecture/architecture.md content/concepts/architecture.md
git mv content/architecture/concepts.md      content/concepts/terminology.md
git mv content/kubernetes-resources/tenant/tenant-overview.md content/concepts/tenant.md
git mv content/kubernetes-resources/quota.md            content/concepts/quota.md
git mv content/kubernetes-resources/extensions.md       content/concepts/extensions.md
git mv content/kubernetes-resources/integration-config.md content/concepts/integration-config.md
rmdir content/architecture 2>/dev/null || true
```

- [ ] **Step 2: Add the Concepts nav block in `theme_override/mkdocs.yml`**

Insert after the Overview block:
```yaml
  - Concepts:
      - concepts/architecture.md
      - concepts/terminology.md
      - concepts/tenant.md
      - concepts/quota.md
      - concepts/extensions.md
      - concepts/integration-config.md
```

- [ ] **Step 3: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 4: Commit**

```bash
git add content/concepts theme_override/mkdocs.yml
git commit -m "docs: move resource/architecture pages to concepts/"
```

---

### Task 4: Move Getting Started pages

**Files:**
- Move: `content/installation/*` -> `content/getting-started/installation/*`
- Move: `content/installation/uninstalling.md` -> `content/getting-started/uninstalling.md`
- Create: `content/getting-started/quick-start.md` (stub)
- Modify: `theme_override/mkdocs.yml` (Install block -> Getting Started)

- [ ] **Step 1: Move installation tree**

```bash
mkdir -p content/getting-started/installation
git mv content/installation/overview.md   content/getting-started/installation/overview.md
git mv content/installation/openshift.md   content/getting-started/installation/openshift.md
git mv content/installation/kubernetes.md  content/getting-started/installation/kubernetes.md
git mv content/installation/azure-aks content/getting-started/installation/azure-aks
git mv content/installation/aws-eks   content/getting-started/installation/aws-eks
git mv content/installation/uninstalling.md content/getting-started/uninstalling.md
rmdir content/installation 2>/dev/null || true
```

- [ ] **Step 2: Create the Quick Start stub**

`content/getting-started/quick-start.md`:
```markdown
# Quick Start

<!-- TODO: condensed install + first tenant walkthrough (authoring phase) -->
```

- [ ] **Step 3: Replace the `- Install:` nav block with Getting Started**

```yaml
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
```

- [ ] **Step 4: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 5: Commit**

```bash
git add content/getting-started theme_override/mkdocs.yml
git commit -m "docs: move installation to getting-started/ and add quick-start stub"
```

---

### Task 5: Move Guides (18 tenant how-to pages)

**Files:**
- Move: `content/kubernetes-resources/tenant/how-to-guides/*.md` -> `content/guides/*.md`
- Modify: `theme_override/mkdocs.yml` (Guides block -> flat, new paths)

- [ ] **Step 1: Move all guide files**

```bash
mkdir -p content/guides
git mv content/kubernetes-resources/tenant/how-to-guides/*.md content/guides/
rmdir content/kubernetes-resources/tenant/how-to-guides 2>/dev/null || true
rmdir content/kubernetes-resources/tenant 2>/dev/null || true
```

- [ ] **Step 2: Replace the Guides nav block**

```yaml
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
```

- [ ] **Step 3: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 4: Commit**

```bash
git add content/guides theme_override/mkdocs.yml
git commit -m "docs: move tenant how-to-guides to flat guides/"
```

---

### Task 6: Rename Extensions section to Integrations

**Files:**
- Modify: `theme_override/mkdocs.yml` (Extensions block -> Integrations; no file moves — `content/integrations/*` already exist)

- [ ] **Step 1: Replace the `- Extensions:` nav block with Integrations**

```yaml
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
```

- [ ] **Step 2: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 3: Commit**

```bash
git add theme_override/mkdocs.yml
git commit -m "docs: rename Extensions nav section to Integrations"
```

---

### Task 7: Build the Reference section

**Files:**
- Move: `content/cli/kubectl-plugin.md` -> `content/reference/cli.md`
- Create: `content/reference/api/{tenant,quota,extensions,integration-config}.md` (spec stubs)
- Create: `content/reference/{configuration,rbac,metrics,webhooks,security-model}.md` (stubs)
- Modify: `theme_override/mkdocs.yml` (remove top-level `- CLI:` and `- API Reference:`; add `- Reference:` block)

- [ ] **Step 1: Move the CLI page**

```bash
mkdir -p content/reference/api
git mv content/cli/kubectl-plugin.md content/reference/cli.md
rmdir content/cli 2>/dev/null || true
```

- [ ] **Step 2: Create the four API Reference spec stubs**

Each file (adjust resource name per file), e.g. `content/reference/api/tenant.md`:
```markdown
# Tenant API Reference

<!-- TODO: spec/field reference split from concepts/tenant.md (authoring phase) -->

See [Tenant concept](../../concepts/tenant.md) for an overview.
```
Repeat for `quota.md`, `extensions.md`, `integration-config.md`, adjusting the title and concept link (`../../concepts/quota.md`, etc.).

- [ ] **Step 3: Create the five Reference stub pages**

Each, e.g. `content/reference/rbac.md`:
```markdown
# RBAC

<!-- TODO: authored from tenant-operator config/rbac/* (authoring phase) -->
```
Repeat for `configuration.md`, `metrics.md`, `webhooks.md`, `security-model.md`, adjusting the title.

- [ ] **Step 4: Remove the old `- CLI:` and `- API Reference:` top-level nav blocks**

Delete both blocks from `theme_override/mkdocs.yml` (their pages are now under Reference / Concepts).

- [ ] **Step 5: Add the Reference nav block**

```yaml
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
```

- [ ] **Step 6: Build (strict gate)**

Run the BUILD block. Expected: 0 warnings — all stubs created in this task are now in nav.

- [ ] **Step 7: Commit**

```bash
git add content/reference theme_override/mkdocs.yml
git commit -m "docs: add Reference section (cli, api stubs, new reference stubs)"
```

---

### Task 8: Rename changelog and finalize section order

**Files:**
- Move: `content/changelog.md` -> `content/release-notes.md`
- Modify: `theme_override/mkdocs.yml` (tail nav: Console/Troubleshooting/Release Notes/Pricing/EULA order)

- [ ] **Step 1: Rename changelog**

```bash
git mv content/changelog.md content/release-notes.md
```

- [ ] **Step 2: Set the tail nav blocks**

Ensure the Console block sits after Getting Started, and replace the trailing `pricing.md / changelog.md / eula.md / troubleshooting.md` entries with:
```yaml
  - Troubleshooting: troubleshooting.md
  - Release Notes: release-notes.md
  - Pricing: pricing.md
  - EULA: eula.md
```
Confirm the full top-level order matches the spec: Overview, Concepts, Getting Started, Console, Guides, Integrations, Reference, Troubleshooting, Release Notes, Pricing, EULA.

- [ ] **Step 3: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 4: Commit**

```bash
git add content/release-notes.md theme_override/mkdocs.yml
git commit -m "docs: rename changelog to release-notes and finalize nav order"
```

---

### Task 9: Add the redirect map

**Files:**
- Modify: `theme_override/mkdocs.yml` (add `plugins: - redirects: redirect_maps:`)

**Interfaces:**
- Consumes: the complete set of moves from Tasks 2–8.
- Produces: a redirect stub at every old URL.

- [ ] **Step 1: Add the redirects plugin block**

Insert a `plugins:` block (before `nav:`, matching the sub-operators' placement) with every moved path:
```yaml
plugins:
  - redirects:
      redirect_maps:
        about/key-features.md: overview/key-features.md
        about/use-cases.md: overview/use-cases.md
        about/benefits.md: overview/benefits.md
        architecture/architecture.md: concepts/architecture.md
        architecture/concepts.md: concepts/terminology.md
        kubernetes-resources/tenant/tenant-overview.md: concepts/tenant.md
        kubernetes-resources/quota.md: concepts/quota.md
        kubernetes-resources/extensions.md: concepts/extensions.md
        kubernetes-resources/integration-config.md: concepts/integration-config.md
        installation/overview.md: getting-started/installation/overview.md
        installation/openshift.md: getting-started/installation/openshift.md
        installation/kubernetes.md: getting-started/installation/kubernetes.md
        installation/azure-aks/preparation.md: getting-started/installation/azure-aks/preparation.md
        installation/azure-aks/installation.md: getting-started/installation/azure-aks/installation.md
        installation/azure-aks/validation.md: getting-started/installation/azure-aks/validation.md
        installation/aws-eks/preparation.md: getting-started/installation/aws-eks/preparation.md
        installation/aws-eks/installation.md: getting-started/installation/aws-eks/installation.md
        installation/aws-eks/validation.md: getting-started/installation/aws-eks/validation.md
        installation/uninstalling.md: getting-started/uninstalling.md
        cli/kubectl-plugin.md: reference/cli.md
        kubernetes-resources/tenant/how-to-guides/create-tenant.md: guides/create-tenant.md
        kubernetes-resources/tenant/how-to-guides/create-namespaces.md: guides/create-namespaces.md
        kubernetes-resources/tenant/how-to-guides/create-sandbox.md: guides/create-sandbox.md
        kubernetes-resources/tenant/how-to-guides/assign-metadata.md: guides/assign-metadata.md
        kubernetes-resources/tenant/how-to-guides/hibernate-tenant.md: guides/hibernate-tenant.md
        kubernetes-resources/tenant/how-to-guides/restrict-nodepool-per-tenant.md: guides/restrict-nodepool-per-tenant.md
        kubernetes-resources/tenant/how-to-guides/disable-intra-tenant-networking.md: guides/disable-intra-tenant-networking.md
        kubernetes-resources/tenant/how-to-guides/ingress-sharding.md: guides/ingress-sharding.md
        kubernetes-resources/tenant/how-to-guides/host-validation.md: guides/host-validation.md
        kubernetes-resources/tenant/how-to-guides/storage-classes.md: guides/storage-classes.md
        kubernetes-resources/tenant/how-to-guides/pod-priority-classes.md: guides/pod-priority-classes.md
        kubernetes-resources/tenant/how-to-guides/service-accounts.md: guides/service-accounts.md
        kubernetes-resources/tenant/how-to-guides/image-registries.md: guides/image-registries.md
        kubernetes-resources/tenant/how-to-guides/custom-roles.md: guides/custom-roles.md
        kubernetes-resources/tenant/how-to-guides/extend-default-roles.md: guides/extend-default-roles.md
        kubernetes-resources/tenant/how-to-guides/delete-tenant.md: guides/delete-tenant.md
        kubernetes-resources/tenant/how-to-guides/templated-metadata-values.md: guides/templated-metadata-values.md
        changelog.md: release-notes.md
```

Note: if the combined theme config already defines a `plugins:` list, the combine script merges plugin lists; add only the `- redirects:` entry so `search`/`glightbox` are preserved. Verify after the build that search still works.

- [ ] **Step 2: Build**

Run the BUILD block. Expected: 0 warnings.

- [ ] **Step 3: Verify a redirect stub is emitted**

```bash
grep -r "http-equiv=\"refresh\"" site/about/key-features/index.html
grep -r "http-equiv=\"refresh\"" site/kubernetes-resources/tenant/how-to-guides/create-tenant/index.html
```
Expected: each prints a `<meta http-equiv="refresh" ...>` line pointing at the new relative path.

- [ ] **Step 4: Commit**

```bash
git add theme_override/mkdocs.yml
git commit -m "docs: add redirect map for all relocated pages"
```

---

### Task 10: Repoint merge.yaml to the new sections

**Files:**
- Modify: `merge.yaml`

**Interfaces:**
- Consumes: the new nav section names/folders (Guides, Reference, Integrations, concepts).
- Produces: merge that lands sub-operator docs 1:1 into the new structure.

- [ ] **Step 1: Update the mappings**

In `merge.yaml`, for both operators change the reference mapping and the hibernation integrations mapping:
- Template `reference/api.md` and Hibernation `reference/api/**`: `into: "reference/api"`, `under: "Reference"` (was `into: "kubernetes-resources"`, `under: "API Reference"`).
- Hibernation `integrations/**`: `under: "Integrations"` (was `under: "Extensions"`).
- Guides mappings (`into: "guides"`, `under: "Guides"`) stay as-is.

Also update the NOTE comment at the top to say the migration is done and mappings are 1:1.

- [ ] **Step 2: Run the merge unit tests**

```bash
make test
```
Expected: all tests pass (34).

- [ ] **Step 3: Commit**

```bash
git add merge.yaml
git commit -m "chore: repoint merge.yaml mappings to new Reference/Integrations sections"
```

---

### Task 11: Full end-to-end verification

**Files:** none (verification only)

- [ ] **Step 1: Clean build with merge against live sub-operators**

```bash
make clean
make serve &
sleep 25 && curl -sf http://127.0.0.1:8000/ >/dev/null && echo "SERVE OK"
kill %1
```
Expected: `SERVE OK`; no build warnings in the `make serve` output. (This exercises the theme-combine + merge + build path CI uses.)

Alternative non-interactive check:
```bash
.venv/bin/python theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml
PYTHON=$(pwd)/.venv/bin/python bash scripts/pre_build_merge.sh
.venv/bin/python -m mkdocs build --strict
```
Expected: `Documentation built`, 0 warnings, merged Template/Hibernation pages present under Guides/Reference/Integrations.

- [ ] **Step 2: Run unit tests**

```bash
make test
```
Expected: all pass.

- [ ] **Step 3: Confirm no orphaned/leftover old directories**

```bash
ls content/about content/architecture content/cli content/installation content/kubernetes-resources 2>&1 | grep -i "No such" && echo "OLD DIRS GONE"
```
Expected: `OLD DIRS GONE` (old dirs removed; `content/kubernetes-resources` may remain only if other files still live there — confirm it's empty of moved pages).

- [ ] **Step 4: Bump the theme submodule (only if Task 1 required the upstream change)**

If the shared theme's `requirements.txt` gained `mkdocs-redirects` upstream:
```bash
git submodule update --remote theme_common
git add theme_common
git commit -m "chore: bump theme_common for mkdocs-redirects support"
```
If the plugin was already present upstream, skip.

- [ ] **Step 5: Final strict build confirmation**

Run the BUILD block once more. Expected: 0 warnings. Migration complete.

---

## Out of scope (follow-up authoring plans)

Content for the stub pages, authored from `~/Documents/work/tenant-operator`:
- `getting-started/quick-start.md`
- `reference/{configuration,rbac,metrics,webhooks,security-model}.md`
- `reference/api/{tenant,quota,extensions,integration-config}.md` (spec split from the concept pages)
