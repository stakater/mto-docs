"""Merge sub-operator docs into the mto-docs content tree and nav.

Driven by merge.yaml. Runs after the mkdocs config-combine step and before
`mkdocs build`. See docs/superpowers/specs/2026-07-03-merge-sub-operator-docs-design.md.
"""
import argparse
import fnmatch
import posixpath
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
        line = lines[j]
        if line.strip() == "":
            continue
        # Indented lines and column-0 list items ("- ...", as PyYAML emits
        # sequences under a mapping key) belong to the nav block. The block
        # ends only at the next top-level mapping key.
        if line[0].isspace() or line[0] == "-":
            continue
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


_INLINE_LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")
_REF_LINK_RE = re.compile(r"(?m)^([ \t]*\[[^\]]+\]:[ \t]+)(\S+)(.*)$")


def _split_url_title(target):
    """Split a link target into (url, title) where title includes its quotes."""
    s = target.strip()
    title = ""
    mo = re.match(r'^(.*?)(\s+(?:"[^"]*"|\'[^\']*\'))\s*$', s)
    if mo:
        s, title = mo.group(1).strip(), mo.group(2).strip()
    if s.startswith("<") and s.endswith(">"):
        s = s[1:-1]
    return s, title


def _rewrite_url(url, src_dir, dest_dir, mapping):
    """Rewrite one relative link so it still resolves after relocation."""
    if not url or url[0] in "#/" or "://" in url or url.startswith("mailto:"):
        return url
    mo = re.match(r"^([^#?]*)([#?].*)?$", url)
    path_part, frag = mo.group(1), mo.group(2) or ""
    if not path_part:
        return url
    resolved = posixpath.normpath(posixpath.join(src_dir, path_part))
    if resolved in mapping:
        return posixpath.relpath(mapping[resolved], dest_dir or ".") + frag
    return url


def rewrite_links(text, src_rel, dest_rel, mapping):
    """Rewrite intra-merge relative links/images in a moved markdown file.

    `mapping` maps source-relative paths (as they were in the sub-operator repo)
    to their new content-relative destinations. Links resolving to a file in the
    map are rewritten relative to the moved file; everything else is untouched.
    """
    src_dir = posixpath.dirname(src_rel)
    dest_dir = posixpath.dirname(dest_rel)

    def _inline(m):
        url, title = _split_url_title(m.group(2))
        new = _rewrite_url(url, src_dir, dest_dir, mapping)
        if new == url:
            return m.group(0)
        return m.group(1) + new + (" " + title if title else "") + m.group(3)

    def _ref(m):
        new = _rewrite_url(m.group(2), src_dir, dest_dir, mapping)
        return m.group(1) + new + m.group(3)

    text = _INLINE_LINK_RE.sub(_inline, text)
    text = _REF_LINK_RE.sub(_ref, text)
    return text


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
        op_map = {}       # source-relative path -> content-relative destination
        md_files = []     # (src_rel, dest_rel) of copied markdown, for link rewriting
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
                op_map[rel] = dest_rel
                dest = content_dir / dest_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(docs / rel, dest)
                # only markdown pages become nav entries; assets are copied only
                if rel.endswith(".md"):
                    md_files.append((rel, dest_rel))
                    if mapping.get("under"):
                        under_entries.setdefault(mapping["under"], []).append((remainder, dest_rel))

        # rewrite intra-operator relative links now that all destinations are known
        for src_rel, dest_rel in md_files:
            dest = content_dir / dest_rel
            original = dest.read_text(encoding="utf-8")
            updated = rewrite_links(original, src_rel, dest_rel, op_map)
            if updated != original:
                dest.write_text(updated, encoding="utf-8")

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
