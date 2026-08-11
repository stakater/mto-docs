# Merge Sub-Operator Docs — Design

## Problem

The Multi-Tenant Operator docs (`mto-docs`) should ship as one site that also
contains the documentation of its sub-operators (`template-operator`,
`hibernation-operator`, and more later). The sub-operator content is **not**
stored in this repo — it is fetched at build time (repos cloned in the
pipeline) and merged into the site before `mkdocs build`.

We need a generic, minimal merge strategy driven by a single YAML control file
that says, per sub-operator: what to copy, where it lands in `mto-docs`, and
where it shows in the menu.

## Constraints discovered

- **Path collisions.** Every sub-operator reuses folder/file names that already
  exist in the parent (`about/`, `architecture/`, `installation/`,
  `kubernetes-resources/`, `index.md`, `eula.md`, `troubleshooting.md`). Copying
  a sub-operator's `content/` straight into the parent `content/` overwrites
  parent files. Sub-operator files must therefore land under a disambiguating
  subfolder (the operator `slug`).
- **`strict: true`.** The parent builds with `strict: true` and an explicit
  `nav:`. Any file present in `content/` but absent from the nav fails the build.
  So every copied page must get a nav entry — auto-generating nav entries is
  required, not just convenience.
- **File location ≠ menu location.** In mkdocs the on-disk path and the nav
  placement are independent. Files can live in `content/kubernetes-resources/template-operator/`
  while their menu entries hang under any section.

## Approach

A standalone Python script, `merge_docs.py`, run during the Docker build
**after** the existing theme/config-combine step and **before** `mkdocs build`.

Chosen over:
- Extending `theme_common/scripts/combine_mkdocs_config_yaml.py` — that script
  lives in the shared `theme_common` submodule; we must not fork it for one repo.
- Off-the-shelf plugins (`mkdocs-monorepo`/`multirepo`) — they pull in entire
  sub-projects with their own nav; no glob-level include/exclude or
  nest-into-parent-nav behavior.

Python (not bash) because the builder image is `python:3.13-alpine` (PyYAML is
free, no new deps), the existing theme scripts are Python, and the recursive
nav-tree generation + structured YAML injection are clean in Python and fragile
in bash+yq.

## Build flow

```
pipeline clones sub-operator repos  ──►  merge.yaml (committed in mto-docs)
                                              │
mto-docs Docker build:                        ▼
  1. combine theme resources          merge_docs.py:
  2. combine mkdocs config              • per operator: glob (from − exclude) over repo/docs_dir
  3. ► merge_docs.py ◄                  • copy matches → content/<into>/<slug>/<remainder>
  4. mkdocs build (strict)             • build nav subtree, nest under existing menu section
                                       • write updated nav back into combined mkdocs.yml
```

`merge.yaml` is the only merge artifact committed to `mto-docs`. Sub-operator
content is never stored in this repo.

## Control file: `merge.yaml`

```yaml
operators:
  - title: Template Operator
    repo: ../template-operator-docs      # clone path or git URL; overridable via CLI/env
    slug: template-operator              # subfolder inserted into each 'into' (default: slug of title)
    docs_dir: content                    # default: content
    mappings:
      - from: "kubernetes-resources/**"  # glob relative to repo/docs_dir
        into: "kubernetes-resources"     # existing mto-docs content folder to merge into
        under: "API Reference"           # existing menu section to nest the submenu under
      - from: "images/**"
        into: "images"                   # no 'under' → assets only, no menu entry
    exclude:                             # optional; applies to all mappings
      - "**/.gitkeep"

  - title: Hibernation Operator
    repo: ../hibernation-operator-docs
    mappings:
      - from: "guides/**"
        into: "kubernetes-resources/tenant/how-to-guides"
        under: "Guides"
      - from: "reference/**"
        into: "kubernetes-resources"
        under: "API Reference"
      - from: "images/**"
        into: "images"
```

### Fields

Operator:

| field      | required | default        | meaning                                             |
|------------|----------|----------------|-----------------------------------------------------|
| `title`    | yes      | —              | menu node name for this operator's inserted submenu |
| `repo`     | yes      | —              | source repo path/URL; overridable via CLI/env       |
| `slug`     | no       | slug of title  | subfolder inserted under each `into` to avoid clashes |
| `docs_dir` | no       | `content`      | where docs live inside the source repo              |
| `mappings` | yes      | —              | list of copy+menu rules                             |
| `exclude`  | no       | none           | globs excluded from all mappings                    |

Mapping:

| field   | required | meaning                                                          |
|---------|----------|------------------------------------------------------------------|
| `from`  | yes      | glob under `repo/docs_dir` (supports `**` and specific files)    |
| `into`  | yes      | existing mto-docs `content/` folder to merge into                |
| `under` | no       | existing menu section to nest the submenu under; omit for assets |

## Placement rules

**File copy.** For each file matched by a mapping's `from` (minus `exclude`):

```
destination = content/<into>/<slug>/<path remainder past the glob base>
```

The glob base is the fixed leading path of `from` before the first wildcard
(e.g. base of `kubernetes-resources/**` is `kubernetes-resources`; base of a
specific file is its parent dir). Structure is preserved under
`<into>/<slug>/`, so in-page relative links (e.g. `../images/foo.png`) keep
resolving as long as the referenced assets are also included.

**Menu.** For each mapping with `under`:

- Auto-generate a nav subtree from the files that landed for this mapping.
- File entries are emitted as bare path strings — mkdocs derives the page title
  from the page's H1 (fallback filename).
- Folder nodes get a prettified title from the folder name.
- The subtree is hung under a single `<title>` node inside the existing
  `<under>` section. Multiple mappings of the same operator sharing the same
  `under` merge into one `<title>` node.
- Nav order within a generated subtree follows path order (alphabetical).

## Error handling / edge cases

All of these **fail the build** with a clear message (favoring correctness;
strict mode would catch most anyway):

- `under` section not found in the combined nav (typo / renamed section).
- A `from` glob matches nothing (likely a mistake or renamed upstream path).
- Two copied files resolve to the same destination path (collision).
- `repo` path missing / not readable.

Notes:
- Assets (mappings without `under`) are copied but produce no menu entries.
- Images/assets are **not** auto-detected from markdown; they are listed
  explicitly as their own mappings (e.g. `from: "images/**"`, no `under`).
  Auto-scan for referenced images is a possible later enhancement.
- `merge_docs.py` edits the combined `mkdocs.yml` in place inside the build
  image; the repo's checked-in nav is untouched.

## Out of scope (YAGNI)

- Interleaving sub-operator pages *between* individual parent pages (only
  nesting under an existing section is supported).
- Rewriting cross-repo links or fixing broken upstream links.
- Auto-detecting referenced assets.
- Merging non-nav mkdocs config (theme, markdown_extensions, plugins) from
  sub-operators — only content + nav are merged; site config stays the parent's.
```

