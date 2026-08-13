# Merge sub-operator docs at build time

Adds a build-time tool that merges the docs of sub-operators (Template, Hibernation) into the MTO docs site, driven by a single `merge.yaml`. Sub-operator content is fetched in CI and never committed here.

## How it works

`scripts/merge_docs.py` reads `merge.yaml` and, per operator:

- **Copies** whitelisted files (glob `from` + `exclude`) into `content/<into>/<slug>/…` (the `<slug>` namespaces each operator, so pages never collide with MTO's own or each other; `flatten` keeps the slug but drops sub-folders → `content/<into>/<slug>/<file>`).
- **Builds nav** for the copied `.md` pages and nests it under an existing menu section (`under`), with folder titles taken from the sub-operator's own nav (falling back to title-case). With `flatten: true` the pages merge as **direct leaf entries** in the section (no operator wrapper, menu-flat); a `title` renames a single-file mapping (e.g. Template's API → one "Template Operator" entry). Splices only the `nav:` block of the combined `mkdocs.yml`, leaving the rest byte-for-byte.
- **Auto-groups duplicates**: when a page's filename appears in more than one source under the same flattened section (e.g. `argocd.md` in both MTO's own docs and Hibernation's), they're folded into a per-page folder titled by the page's H1 (→ `ArgoCD`), with one labelled leaf per source (`Multi-Tenant Operator`, `Hibernation Operator`). This is a rule, not a hand-maintained list — the labels come from operator titles and `site_title` (default: the mkdocs `site_name`).
- **Concatenates the API** (`concat_into` mapping mode): each operator's `reference/api.md` — plus MTO's own — merges into one **API Reference** page. Each source becomes an H2 section (`heading`, MTO's own labelled by `site_title`), its own headings demoted one level (code fences respected), so the in-page TOC lists `Tenant Operator` / `Template Operator` / `FinOps` / `Hibernation Operator`. Aggregated across operators by shared `concat_into`; one labelled leaf under `Reference`.
- **Rewrites links**: whitelisted targets → local relative links; anything else → the operator's published site (`live_url`, `directory`/`html` style), anchors preserved. Externalized links are logged.

`merge.yaml` is the whitelist; the tool fails fast on empty globs, collisions, missing repos, or unknown menu sections.

## Integration

- **CI**: `pull_request.yaml` and `push.yaml` run `PRE_BUILD_HOOK: make merge` after theme-combine, before `mike deploy` (shared workflows at `v0.0.189`). `scripts/pre_build_merge.sh` clones each repo (token-aware) and runs the merge. `release.yaml` only containerizes the already-built `gh-pages`, so it needs no hook.
- **Local**: `make serve` (combine + merge + `mkdocs serve`), `make merge`, `make clean`.
- `DockerfileLocal` gains an optional, arg-gated merge step (skipped when unset).

## Verified

- `mkdocs build --strict` passes (0 warnings) against the live `main` branches of both sub-operators.
- 62 unit tests (path/glob/nav/flatten/duplicate-grouping/page-merging/link-rewriting/title-derivation).

## Notes

- `merge.yaml` `into`/`under` target the current MTO nav; they collapse to ~1:1 pairs once MTO migrates to `structure.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
