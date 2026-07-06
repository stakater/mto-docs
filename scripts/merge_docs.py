"""Merge sub-operator docs into the mto-docs content tree and nav.

Driven by merge.yaml. Runs after the mkdocs config-combine step and before
`mkdocs build`. See docs/superpowers/specs/2026-07-03-merge-sub-operator-docs-design.md.
"""
import argparse
import fnmatch
import re
import shutil
import sys
import yaml
from pathlib import Path

_WILDCARD = set("*?[]")


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return s.strip("-")


def prettify(name):
    return " ".join(w.capitalize() for w in re.split(r"[-_\s]+", name) if w)


def glob_base(pattern):
    parts = pattern.split("/")
    base = []
    for p in parts:
        if any(c in _WILDCARD for c in p):
            break
        base.append(p)
    if len(base) == len(parts):   # no wildcard -> drop the file component
        base = base[:-1]
    return "/".join(base)


def strip_base(rel, base):
    if not base:
        return rel
    prefix = base + "/"
    if not rel.startswith(prefix):
        raise ValueError(f"{rel!r} not under base {base!r}")
    return rel[len(prefix):]


def compute_dest(remainder, into, slug):
    return "/".join(p for p in (into, slug, remainder) if p)


def _excluded(rel, patterns):
    name = rel.rsplit("/", 1)[-1]
    for ex in patterns:
        if fnmatch.fnmatch(rel, ex) or fnmatch.fnmatch(name, ex.replace("**/", "")):
            return True
    return False


def find_matches(docs_dir, pattern, exclude):
    glob_pat = pattern + "/*" if pattern.endswith("**") else pattern
    results = []
    for p in docs_dir.glob(glob_pat):
        if not p.is_file():
            continue
        rel = p.relative_to(docs_dir).as_posix()
        if _excluded(rel, exclude or []):
            continue
        results.append(rel)
    return sorted(results)


def build_nav_tree(entries):
    root = {}
    for remainder, full in sorted(entries):
        parts = remainder.split("/")
        node = root
        for i, folder in enumerate(parts[:-1]):
            existing = node.get(folder)
            if existing is not None and not isinstance(existing, dict):
                raise ValueError(
                    f"nav conflict: {'/'.join(parts[:i + 1])!r} is used as both a file and a folder"
                )
            node = node.setdefault(folder, {})
        leaf = parts[-1]
        if leaf in node:
            if isinstance(node[leaf], dict):
                raise ValueError(
                    f"nav conflict: {remainder!r} is used as both a file and a folder"
                )
            raise ValueError(f"duplicate nav entry for remainder {remainder!r}")
        node[leaf] = full
    return _to_nav(root)


def _to_nav(node):
    out = []
    for key, val in node.items():
        if isinstance(val, dict):
            out.append({prettify(key): _to_nav(val)})
        else:
            out.append(val)
    return out


def find_section(nav, title):
    for item in nav:
        if isinstance(item, dict):
            for key, val in item.items():
                if key == title and isinstance(val, list):
                    return val
                if isinstance(val, list):
                    found = find_section(val, title)
                    if found is not None:
                        return found
    return None


def insert_subtree(nav, under, title, subtree):
    section = find_section(nav, under)
    if section is None:
        raise KeyError(f"menu section {under!r} not found in nav")
    for item in section:
        if isinstance(item, dict) and title in item and isinstance(item[title], list):
            item[title].extend(subtree)
            return
    section.append({title: subtree})


def _nav_bounds(text):
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^nav\s*:", line):
            start = i
            break
    if start is None:
        raise ValueError("no top-level 'nav:' block found in mkdocs.yml")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == "":
            continue
        if not lines[j][0].isspace():
            end = j
            break
    return lines, start, end


def read_nav(text):
    lines, start, end = _nav_bounds(text)
    block = "".join(lines[start:end])
    return yaml.safe_load(block)["nav"]


def write_nav(text, nav):
    lines, start, end = _nav_bounds(text)
    block = yaml.safe_dump({"nav": nav}, sort_keys=False, allow_unicode=True,
                           default_flow_style=False)
    # Indent all lines except the first (nav:) with 2 spaces to match mkdocs.yml style
    block_lines = block.split('\n')
    indented = [block_lines[0]]
    for line in block_lines[1:]:
        if line:  # Don't indent empty lines
            indented.append('  ' + line)
        else:
            indented.append(line)
    block = '\n'.join(indented)
    if not block.endswith("\n"):
        block += "\n"
    return "".join(lines[:start]) + block + "".join(lines[end:])


def load_config(path):
    data = yaml.safe_load(Path(path).read_text())
    operators = []
    for raw in data["operators"]:
        operators.append({
            "title": raw["title"],
            "repo": raw["repo"],
            "slug": raw.get("slug") or slugify(raw["title"]),
            "docs_dir": raw.get("docs_dir", "content"),
            "exclude": raw.get("exclude") or [],
            "mappings": raw["mappings"],
        })
    return operators


def run(operators, content_dir, mkdocs_path, repo_overrides=None):
    content_dir = Path(content_dir)
    overrides = repo_overrides or {}
    text = Path(mkdocs_path).read_text()
    nav = read_nav(text)
    seen = {}

    for op in operators:
        repo = Path(overrides.get(op["slug"], op["repo"]))
        docs = repo / op["docs_dir"]
        if not docs.is_dir():
            raise FileNotFoundError(f"docs dir not found: {docs}")

        under_entries = {}
        for mapping in op["mappings"]:
            base = glob_base(mapping["from"])
            matches = find_matches(docs, mapping["from"], op["exclude"])
            if not matches:
                raise ValueError(f"{mapping['from']!r} matched no files in {docs}")
            for rel in matches:
                remainder = strip_base(rel, base)
                dest_rel = compute_dest(remainder, mapping["into"], op["slug"])
                if dest_rel in seen:
                    raise ValueError(f"destination collision: {dest_rel}")
                seen[dest_rel] = True
                dest = content_dir / dest_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(docs / rel, dest)
                if mapping.get("under"):
                    under_entries.setdefault(mapping["under"], []).append((remainder, dest_rel))

        for under, entries in under_entries.items():
            insert_subtree(nav, under, op["title"], build_nav_tree(entries))

    Path(mkdocs_path).write_text(write_nav(text, nav))


def parse_repo_overrides(pairs):
    out = {}
    for pair in pairs:
        slug, _, path = pair.partition("=")
        if not slug or not path:
            raise ValueError(f"--set-repo expects slug=path, got {pair!r}")
        out[slug] = path
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Merge sub-operator docs into mto-docs.")
    ap.add_argument("--config", default="merge.yaml")
    ap.add_argument("--content-dir", default="content")
    ap.add_argument("--mkdocs", default="mkdocs.yml")
    ap.add_argument("--set-repo", action="append", default=[], metavar="slug=path")
    args = ap.parse_args(argv)
    operators = load_config(args.config)
    overrides = parse_repo_overrides(args.set_repo)
    run(operators, args.content_dir, args.mkdocs, overrides)
    return 0


if __name__ == "__main__":
    sys.exit(main())
