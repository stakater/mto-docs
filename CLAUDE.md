# mto-docs

## File naming

Kebab-case for every file and directory: `quota-creation-metadata.png`, not
`quotaCreationMetadata.png` or `quota_creation_metadata.png`. Applies to images,
YAML, Markdown and directories alike. Exceptions are names a tool fixes
(`README.md`, `Makefile`, `Dockerfile`) and Python modules, which stay
`snake_case.py` because the filename is the import path.

## Console screenshots

Pages under `content/console/` reference images as `{{ screenshot: name }}`, not
`![…](../images/…)`. The build resolves each directive to `screenshots/captured/<name>.png`
and fails if one is missing, so never add a plain image path to a console page.

Those captures are committed. `screenshots.yaml` refreshes them on PR approval or a
manual run; no docs build talks to the live console. See `screenshots/README.md`.

Images outside `content/console/` are hand-made and referenced by path as usual.
