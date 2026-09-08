"""MkDocs hook that resolves `{{ screenshot: <name> }}` directives at build time.

This module is ours; what mkdocs provides is the loader -- its built-in `hooks:`
config key (theme_override/mkdocs.yml) imports this file and calls the event
functions below. So there is NO third-party plugin to install.

Why this rather than mkdocs-macros-plugin (the obvious library for `{{ }}`):
  * macros enables Jinja2 rendering for EVERY page, and these docs legitimately
    contain `{{ .Role }}`, `{{ .Tenant }}`, `{{ issuer }}`, `{{ TENANT.USERNAME }}`
    in templating examples. Jinja would try to evaluate those, and with
    `strict: true` in the config that breaks or blanks them. Avoiding it needs
    render_by_default:false plus per-page opt-in on every console page.
  * it is a pip dependency, and it would have to go in
    theme_common/requirements.txt -- an upstream submodule the shared CI installs,
    not ours to change.
This hook touches ONLY the exact `{{ screenshot: name }}` pattern, so no other
braces in the docs can be affected.

Two phases:
  on_pre_build     copies each referenced image into content/images/generated/ so
                   mkdocs picks it up when it collects files (pre_build runs first)
  on_page_markdown replaces the directive with the image path, IN MEMORY --
                   source files are never rewritten

Images come ONLY from screenshots/captured/. There is no fallback to the archived
originals in screenshots/baseline/: falling back would publish a stale screenshot,
the exact failure this system exists to prevent. A directive with no captured image
raises and fails the build, naming the page.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inject import (  # noqa: E402  (path juggling must come first)
    CONTENT,
    DIRECTIVE,
    GENERATED,
    path_for,
    resolve_source,
)


def on_pre_build(config, **kwargs):
    """Stage every referenced screenshot into content/images/generated/."""
    wanted: set[str] = set()
    for page in CONTENT.rglob("*.md"):
        wanted.update(DIRECTIVE.findall(page.read_text()))
    if not wanted:
        return

    GENERATED.mkdir(parents=True, exist_ok=True)
    staged = 0
    for name in sorted(wanted):
        src = resolve_source(name)
        if src is None:
            continue  # on_page_markdown raises, and can name the offending page
        shutil.copy2(src, GENERATED / f"{name}.png")
        staged += 1
    print(f"screenshots: staged {staged}/{len(wanted)} captured images")


def on_page_markdown(markdown, page, config, files, **kwargs):
    """Swap directives for image paths, relative to this page's depth."""
    if not DIRECTIVE.search(markdown):
        return markdown

    depth = len(Path(page.file.src_path).parent.parts)

    def replace(match):
        name = match.group(1)
        if resolve_source(name) is None:
            raise SystemExit(
                f"screenshots: {page.file.src_path} references "
                f"{{{{ screenshot: {name} }}}} but screenshots/captured/{name}.png "
                f"does not exist. Run `make screenshots` (or drop the directive)."
            )
        return path_for(name, depth)

    return DIRECTIVE.sub(replace, markdown)
