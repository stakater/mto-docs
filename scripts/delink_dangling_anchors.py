#!/usr/bin/env python3
"""Delink internal anchors that have no target heading in a markdown file.

crd-ref-docs links to helper types (e.g. api/common Namespace/Members) that it
does not render as sections, producing dangling `[Text](#anchor)` links that fail
`mkdocs build --strict`. This converts any such internal link to plain text,
leaving valid internal links and all external links untouched.

Usage: delink_dangling_anchors.py <file.md>
"""
import re
import sys


def slug(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def main(path: str) -> None:
    text = open(path, encoding="utf-8").read()
    anchors = {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.*)$", text, re.M)}
    # [text](#anchor) with optional " array" style suffixes handled by the link body only
    link_re = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")

    removed = []

    def repl(m):
        if m.group(2) not in anchors:
            removed.append(m.group(2))
            return m.group(1)
        return m.group(0)

    new = link_re.sub(repl, text)
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
    print(f"delinked {len(removed)} dangling anchor link(s): {sorted(set(removed))}")


if __name__ == "__main__":
    main(sys.argv[1])
