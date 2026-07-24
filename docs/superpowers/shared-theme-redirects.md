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
