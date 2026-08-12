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
    """Fallback folder title when the sub-operator's nav has no name for it."""
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


def compute_dest(remainder, into, slug, flatten=False):
    if flatten:   # keep slug (namespacing), drop sub-dirs: into/<slug>/<basename>
        return "/".join(p for p in (into, slug, remainder.rsplit("/", 1)[-1]) if p)
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


def build_nav_tree(entries, folder_titles=None):
    """Build a nested nav list from (remainder, dest, src) entries.

    Folder node labels come from `folder_titles` (source-folder-path -> title,
    taken from the sub-operator's own nav) when available, else `prettify`.
    """
    folder_titles = folder_titles or {}
    root = {}
    src_of = {}   # remainder-prefix -> source folder path (to look up its title)
    for remainder, dest, src in sorted(entries):
        parts = remainder.split("/")
        src_parts = src.split("/")
        base_len = len(src_parts) - len(parts)   # leading src comps stripped in remainder
        node = root
        for i, folder in enumerate(parts[:-1]):
            src_of["/".join(parts[:i + 1])] = "/".join(src_parts[:base_len + i + 1])
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
        node[leaf] = dest
    return _to_nav(root, "", src_of, folder_titles)


def _to_nav(node, prefix, src_of, folder_titles):
    out = []
    for key, val in node.items():
        if isinstance(val, dict):
            child_prefix = f"{prefix}/{key}" if prefix else key
            title = folder_titles.get(src_of.get(child_prefix, "")) or prettify(key)
            out.append({title: _to_nav(val, child_prefix, src_of, folder_titles)})
        else:
            out.append(val)
    return out


def _collect_files(items):
    """All file-path strings reachable under a nav item list."""
    out = []
    for item in items:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            for val in item.values():
                if isinstance(val, list):
                    out.extend(_collect_files(val))
                elif isinstance(val, str):
                    out.append(val)
    return out


def nav_folder_titles(nav):
    """Map source folder path -> title, derived from a sub-operator's own nav.

    Each titled section is mapped to the common directory of the files beneath
    it, so e.g. a section 'API Reference' over reference/api/*.md yields
    {'reference/api': 'API Reference'}.
    """
    titles = {}

    def walk(items):
        for item in items:
            if isinstance(item, dict):
                for title, val in item.items():
                    if not isinstance(val, list):
                        continue
                    # recurse first so a deeper (more specific) section claims the
                    # folder; a broad ancestor then won't override it (setdefault)
                    walk(val)
                    files = _collect_files(val)
                    if files:
                        common = (posixpath.dirname(files[0]) if len(files) == 1
                                  else posixpath.commonpath(files))
                        if common:
                            titles.setdefault(common, title)

    walk(nav)
    return titles


def read_folder_titles(repo):
    """Read a sub-operator repo's own nav and return source-folder -> title."""
    for candidate in ("theme_override/mkdocs.yml", "mkdocs.yml"):
        path = repo / candidate
        if not path.is_file():
            continue
        try:
            nav = read_nav(path.read_text(encoding="utf-8"))
        except (ValueError, KeyError, TypeError):
            continue
        if nav:
            return nav_folder_titles(nav)
    return {}


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


def insert_leaves(nav, under, leaves):
    """Append leaf nav entries directly into the `under` section (flatten mode).

    No operator wrapper folder: each leaf (a bare dest string or a {title: dest}
    dict) becomes a direct child of the target section.
    """
    section = find_section(nav, under)
    if section is None:
        raise KeyError(f"menu section {under!r} not found in nav")
    section.extend(leaves)


def _leaf_path(item):
    """The dest a direct-child nav leaf points at (bare string or single-key
    dict), else None for a folder or multi-key node."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict) and len(item) == 1:
        (val,) = item.values()
        if isinstance(val, str):
            return val
    return None


def find_base_leaf(section, base, exclude):
    """A direct-child leaf in `section` whose file basename is `base` and whose
    path isn't in `exclude` -- i.e. mto-docs' own page, not a merged one."""
    for item in section or []:
        path = _leaf_path(item)
        if path and path not in exclude and path.rsplit("/", 1)[-1] == base:
            return path
    return None


def apply_group(nav, group):
    """Regroup duplicate pages under a shared folder with per-source labels.

    A group declares a `title` folder under an existing `under` section and the
    `items` (each a content-relative `page` + optional `title` label) to gather
    into it. Standalone leaves for those pages are removed from the section and
    replaced, in the slot of the first one, by the folder. Combines a merged
    page with MTO's own since both are just final dest paths.
    """
    under, title, items = group["under"], group["title"], group["items"]
    section = find_section(nav, under)
    if section is None:
        raise KeyError(f"menu section {under!r} not found in nav")
    pages = {it["page"] for it in items}
    folder = {title: [{it["title"]: it["page"]} if it.get("title") else it["page"]
                      for it in items]}
    new_section, placed = [], False
    for item in section:
        if _leaf_path(item) in pages:
            if not placed:
                new_section.append(folder)
                placed = True
            continue   # drop the standalone leaf (folded into the group)
        new_section.append(item)
    if not placed:
        new_section.append(folder)
    section[:] = new_section


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


def insert_extra_list(text, key, values):
    """Add `key: [values]` under the top-level `extra:` mapping in mkdocs.yml text.

    Text-level insertion for the same reason the nav is edited that way: the file
    carries `!!python/name:` tags that a safe_load round-trip would drop. When the
    file has no top-level `extra:` block, one is appended.
    """
    if not values:
        return text
    block = yaml.safe_dump({key: values}, sort_keys=False, allow_unicode=True,
                           default_flow_style=False)
    body = "".join(f"  {line}\n" for line in block.splitlines())
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if re.match(r"^extra\s*:\s*$", line):
            for j in range(i + 1, len(lines)):
                if not lines[j][0].isspace():
                    break
                if re.match(rf"^  {re.escape(key)}\s*:", lines[j]):
                    raise ValueError(f"extra.{key} already present in {lines[j].strip()!r}")
            return "".join(lines[:i + 1]) + body + "".join(lines[i + 1:])
    if text and not text.endswith("\n"):
        text += "\n"
    return text + "extra:\n" + body


def load_config(path):
    data = yaml.safe_load(Path(path).read_text())
    operators = []
    for raw in data["operators"]:
        operators.append({
            "title": raw["title"],
            "repo": raw["repo"],
            "branch": raw.get("branch") or "",   # empty -> repo default branch
            "slug": raw.get("slug") or slugify(raw["title"]),
            "docs_dir": raw.get("docs_dir", "content"),
            "exclude": raw.get("exclude") or [],
            "live_url": raw.get("live_url"),
            "live_url_style": raw.get("live_url_style", "directory"),
            "mappings": raw["mappings"],
        })
    return operators


def read_h1(path):
    """First level-1 heading text in a markdown file, else None."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        mo = re.match(r"#\s+(.+?)\s*#*\s*$", line.strip())
        if mo:
            return mo.group(1).strip()
    return None


def build_duplicate_groups(nav, flat_pages, content_dir, site_title):
    """Describe folders that gather pages colliding by basename across sources.

    `flat_pages` is (under, dest, source_title) for each flattened, untitled
    page. Any basename appearing under the same section in >=2 sources (the
    operators here plus mto-docs' own matching nav leaf) yields a group: a folder
    titled by the page's H1 with one labelled leaf per source. Fully derived --
    no per-duplicate configuration.
    """
    by_key, order = {}, []
    for under, dest, source in flat_pages:
        key = (under, dest.rsplit("/", 1)[-1])
        if key not in by_key:
            by_key[key] = []
            order.append(key)
        by_key[key].append((source, dest))

    groups = []
    for under, base in order:
        members = by_key[(under, base)]
        section = find_section(nav, under)
        merged = {d for _, d in members}
        own = find_base_leaf(section, base, merged) if section is not None else None
        entries = ([(site_title, own)] if own else []) + members
        if len(entries) < 2:
            continue   # not actually a duplicate; leave it as a flat leaf
        stem = base[:-3] if base.endswith(".md") else base
        title = read_h1(Path(content_dir) / entries[0][1]) or prettify(stem)
        groups.append({"under": under, "title": title,
                       "items": [{"title": t, "page": p} for t, p in entries]})
    return groups


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


def _to_live_url(path, live_url, style):
    """Map a source-relative path to a URL on the operator's published site."""
    base = live_url if live_url.endswith("/") else live_url + "/"
    if path.endswith(".md"):
        stem = path[:-3]
        if style == "html":
            suffix = stem + ".html"
        elif stem == "index":
            suffix = ""
        elif stem.endswith("/index"):
            suffix = stem[: -len("index")]   # keep the trailing slash
        else:
            suffix = stem + "/"
        return base + suffix
    return base + path   # assets keep their path


def _rewrite_url(url, src_dir, dest_dir, mapping, live_url, style, external):
    """Whitelisted target -> local relative link; otherwise -> live_url fallback."""
    if not url or url[0] in "#/" or "://" in url or url.startswith("mailto:"):
        return url
    mo = re.match(r"^([^#?]*)([#?].*)?$", url)
    path_part, frag = mo.group(1), mo.group(2) or ""
    if not path_part:
        return url
    resolved = posixpath.normpath(posixpath.join(src_dir, path_part))
    if resolved in mapping:
        return posixpath.relpath(mapping[resolved], dest_dir or ".") + frag
    # not whitelisted: fall back to the operator's live docs, if configured
    if live_url and not resolved.startswith(".."):
        external.append(resolved)
        return _to_live_url(resolved, live_url, style) + frag
    return url


def rewrite_links(text, src_rel, dest_rel, mapping, live_url=None,
                  live_url_style="directory"):
    """Rewrite links in a moved markdown file.

    Whitelisted targets (files copied by the merge, present in `mapping`) become
    local relative links. Any other relative link falls back to `live_url` (the
    operator's published docs) when provided, else is left unchanged. Anchors are
    preserved. Returns (new_text, externalized) where `externalized` lists the
    source paths that were pointed at the live site.
    """
    src_dir = posixpath.dirname(src_rel)
    dest_dir = posixpath.dirname(dest_rel)
    external = []

    def _inline(m):
        url, title = _split_url_title(m.group(2))
        new = _rewrite_url(url, src_dir, dest_dir, mapping, live_url, live_url_style, external)
        if new == url:
            return m.group(0)
        return m.group(1) + new + (" " + title if title else "") + m.group(3)

    def _ref(m):
        new = _rewrite_url(m.group(2), src_dir, dest_dir, mapping, live_url, live_url_style, external)
        return m.group(1) + new + m.group(3)

    text = _INLINE_LINK_RE.sub(_inline, text)
    text = _REF_LINK_RE.sub(_ref, text)
    return text, external


def validate_mapping(mapping):
    """Reject `label` combinations that cannot render as an operator header."""
    if not mapping.get("label"):
        return
    where = mapping.get("from")
    if not mapping.get("flatten"):
        raise ValueError(f"label requires flatten: true (mapping from {where!r})")
    if mapping.get("title"):
        raise ValueError(f"label and title are mutually exclusive (mapping from {where!r})")
    if not mapping.get("under"):
        raise ValueError(f"label requires under (mapping from {where!r})")


def run(operators, content_dir, mkdocs_path, repo_overrides=None, site_title=None):
    content_dir = Path(content_dir)
    overrides = repo_overrides or {}
    text = Path(mkdocs_path).read_text()
    nav = read_nav(text)
    seen = {}
    flat_pages = []   # (under, dest, source_title) for flattened untitled pages
    nav_labels = []   # operator titles emitted as nav labels, in first-seen order

    for op in operators:
        repo = Path(overrides.get(op["slug"], op["repo"]))
        docs = repo / op["docs_dir"]
        if not docs.is_dir():
            raise FileNotFoundError(f"docs dir not found: {docs}")

        folder_titles = read_folder_titles(repo)   # from the sub-op's own nav
        under_entries = {}
        # (under, kind, payload) for flatten mappings, in mapping order.
        # kind "leaf" -> a direct child of the section; kind "group" -> the
        # operator-titled section the theme renders as a label header.
        flat_inserts = []
        op_map = {}       # source-relative path -> content-relative destination
        md_files = []     # (src_rel, dest_rel) of copied markdown, for link rewriting
        for mapping in op["mappings"]:
            validate_mapping(mapping)
            base = glob_base(mapping["from"])
            matches = find_matches(docs, mapping["from"], op["exclude"])
            if not matches:
                raise ValueError(f"{mapping['from']!r} matched no files in {docs}")
            flatten = mapping.get("flatten", False)
            mapping_dests = []   # dests of copied .md in this mapping (nav order)
            for rel in matches:
                remainder = strip_base(rel, base)
                dest_rel = compute_dest(remainder, mapping["into"], op["slug"], flatten)
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
                        if flatten:
                            mapping_dests.append(dest_rel)
                        else:
                            under_entries.setdefault(mapping["under"], []).append((remainder, dest_rel, rel))
            # flatten: merge as direct leaves under the section (no op wrapper).
            # A `title` renames a single-file mapping; with several files it names
            # a folder holding them, else each page keeps its own H1 as the label.
            # `label` instead groups the pages under the operator's own title,
            # which the theme renders as a plain header (see extra.nav_labels).
            if flatten and mapping_dests:
                title = mapping.get("title")
                if mapping.get("label"):
                    flat_inserts.append((mapping["under"], "group", mapping_dests))
                    if op["title"] not in nav_labels:
                        nav_labels.append(op["title"])
                elif title and len(mapping_dests) == 1:
                    flat_inserts.append((mapping["under"], "leaf", {title: mapping_dests[0]}))
                elif title:
                    flat_inserts.append((mapping["under"], "leaf", {title: mapping_dests}))
                else:
                    flat_inserts.extend((mapping["under"], "leaf", d) for d in mapping_dests)
                    # untitled flat pages are candidates for duplicate auto-grouping
                    flat_pages.extend((mapping["under"], d, op["title"]) for d in mapping_dests)

        # rewrite links now that all destinations are known: whitelisted targets
        # become local, everything else falls back to the operator's live docs
        live_url = op.get("live_url")
        style = op.get("live_url_style", "directory")
        externalized = []
        for src_rel, dest_rel in md_files:
            dest = content_dir / dest_rel
            original = dest.read_text(encoding="utf-8")
            updated, ext = rewrite_links(original, src_rel, dest_rel, op_map, live_url, style)
            externalized.extend(ext)
            if updated != original:
                dest.write_text(updated, encoding="utf-8")
        if externalized:
            print(f">> {op['title']}: {len(externalized)} link(s) point to live docs "
                  f"({live_url}); distinct targets:")
            for target in sorted(set(externalized)):
                print(f"     {target}")

        for under, entries in under_entries.items():
            insert_subtree(nav, under, op["title"], build_nav_tree(entries, folder_titles))
        for under, kind, payload in flat_inserts:
            if kind == "group":
                insert_subtree(nav, under, op["title"], payload)
            else:
                insert_leaves(nav, under, [payload])

    # post-merge: auto-fold pages that collide by basename across sources into a
    # per-page folder with per-source labels (e.g. ArgoCD -> {MTO, Hibernation})
    if site_title is None:
        mo = re.search(r"(?m)^site_name:\s*(.+?)\s*$", text)
        site_title = mo.group(1).strip().strip("\"'") if mo else "Multi-Tenant Operator"
    for group in build_duplicate_groups(nav, flat_pages, content_dir, site_title):
        apply_group(nav, group)

    out = write_nav(text, nav)
    out = insert_extra_list(out, "nav_labels", nav_labels)
    Path(mkdocs_path).write_text(out)


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
    site_title = (yaml.safe_load(Path(args.config).read_text()) or {}).get("site_title")
    overrides = parse_repo_overrides(args.set_repo)
    run(operators, args.content_dir, args.mkdocs, overrides, site_title=site_title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
