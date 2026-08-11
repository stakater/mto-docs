# Merge Sub-Operator Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python tool (`scripts/merge_docs.py`) that, driven by a `merge.yaml` control file, copies selected sub-operator doc files into the mto-docs `content/` tree under disambiguating subfolders and auto-generates nav entries nested under existing menu sections, so the site builds with `strict: true`.

**Architecture:** A single self-contained script runs during the build **after** the theme/config-combine step and **before** `mkdocs build`. It reads `merge.yaml`, globs each sub-operator's `docs_dir`, copies matches to `content/<into>/<slug>/<remainder>`, builds a nested nav subtree per mapping, and splices it into the `nav:` block of the combined `mkdocs.yml` (text-splice so `!!python/...` tags and comments elsewhere are untouched). Fail-fast on every anomaly.

**Tech Stack:** Python 3.13 (build image `python:3.13-alpine`), PyYAML (already a build dep), stdlib `pathlib`/`fnmatch`/`shutil`/`argparse`/`re`. pytest for tests (dev-only).

## Global Constraints

- Runtime deps limited to **PyYAML + stdlib** — no new runtime dependency (build image is `python:3.13-alpine`, PyYAML comes from `theme_common/requirements.txt`).
- Never round-trip the whole `mkdocs.yml` through a YAML dumper — it contains `!!python/name:...` tags and comments. Only the `nav:` block is parsed/rewritten; the rest of the file is preserved byte-for-byte via text splice.
- **Fail-fast**: missing `under` section, a `from` glob matching nothing, a destination collision, or a missing `repo`/`docs_dir` must raise and exit non-zero.
- File on-disk location is independent of menu location. Copy rule: `destination = content/<into>/<slug>/<remainder past the glob base>`.
- Menu strategy is **nested**: each operator's pages hang under a single `<title>` node inside the named existing `<under>` section; mappings of the same operator sharing an `under` merge into one `<title>` node.
- `merge.yaml` is the only artifact committed to mto-docs; sub-operator content is fetched at build time and never stored here.
- Run order: combine theme resources → combine mkdocs config → **`merge_docs.py`** → `mkdocs build`.

---

### Task 1: Scaffolding + pure path helpers

**Files:**
- Create: `scripts/merge_docs.py`
- Create: `conftest.py`
- Create: `requirements-dev.txt`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `slugify(title: str) -> str`
  - `prettify(name: str) -> str`
  - `glob_base(pattern: str) -> str`
  - `strip_base(rel: str, base: str) -> str`
  - `compute_dest(remainder: str, into: str, slug: str) -> str`

- [ ] **Step 1: Create dev requirements**

`requirements-dev.txt`:

```
PyYAML>=6.0
pytest>=8.0
```

- [ ] **Step 2: Create conftest.py so tests can import the script**

`conftest.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
```

- [ ] **Step 3: Write the failing test**

`tests/test_merge_docs.py`:

```python
import merge_docs as m


def test_slugify():
    assert m.slugify("Template Operator") == "template-operator"
    assert m.slugify("Hibernation  Operator!") == "hibernation-operator"


def test_prettify():
    assert m.prettify("how-to-guides") == "How To Guides"
    assert m.prettify("reference") == "Reference"


def test_glob_base():
    assert m.glob_base("kubernetes-resources/**") == "kubernetes-resources"
    assert m.glob_base("kubernetes-resources/how-to-guides/**") == "kubernetes-resources/how-to-guides"
    assert m.glob_base("architecture/logs-metrics.md") == "architecture"
    assert m.glob_base("images/**") == "images"
    assert m.glob_base("index.md") == ""


def test_strip_base():
    assert m.strip_base("kubernetes-resources/template.md", "kubernetes-resources") == "template.md"
    assert m.strip_base("index.md", "") == "index.md"


def test_compute_dest():
    assert m.compute_dest("template.md", "kubernetes-resources", "template-operator") == \
        "kubernetes-resources/template-operator/template.md"
    assert m.compute_dest("how-to/copy.md", "kubernetes-resources", "template-operator") == \
        "kubernetes-resources/template-operator/how-to/copy.md"
```

- [ ] **Step 4: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'merge_docs'`

- [ ] **Step 5: Write minimal implementation**

`scripts/merge_docs.py`:

```python
"""Merge sub-operator docs into the mto-docs content tree and nav.

Driven by merge.yaml. Runs after the mkdocs config-combine step and before
`mkdocs build`. See docs/superpowers/specs/2026-07-03-merge-sub-operator-docs-design.md.
"""
import re

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
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -v`
Expected: PASS (5 tests)

- [ ] **Step 7: Commit**

```bash
git add scripts/merge_docs.py conftest.py requirements-dev.txt tests/test_merge_docs.py
git commit -m "feat(merge): path helpers for sub-operator doc merge"
```

---

### Task 2: File matching (glob + exclude)

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: nothing from prior tasks.
- Produces: `find_matches(docs_dir: Path, pattern: str, exclude: list[str]) -> list[str]` — sorted POSIX relative paths of matching **files** under `docs_dir`, excludes applied.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
from pathlib import Path


def _touch(base, *rels):
    for r in rels:
        p = base / r
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")


def test_find_matches_recursive_and_exclude(tmp_path):
    _touch(tmp_path,
           "kubernetes-resources/template.md",
           "kubernetes-resources/how-to/copy.md",
           "kubernetes-resources/.gitkeep",
           "images/logo.png")
    got = m.find_matches(tmp_path, "kubernetes-resources/**", ["**/.gitkeep"])
    assert got == ["kubernetes-resources/how-to/copy.md",
                   "kubernetes-resources/template.md"]


def test_find_matches_specific_file(tmp_path):
    _touch(tmp_path, "architecture/logs-metrics.md", "architecture/other.md")
    assert m.find_matches(tmp_path, "architecture/logs-metrics.md", []) == \
        ["architecture/logs-metrics.md"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k find_matches -v`
Expected: FAIL with `AttributeError: module 'merge_docs' has no attribute 'find_matches'`

- [ ] **Step 3: Write minimal implementation**

Add imports at the top of `scripts/merge_docs.py` (merge with existing `import re`):

```python
import fnmatch
from pathlib import Path
```

Add function:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k find_matches -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): glob-based file matching with excludes"
```

---

### Task 3: Nav subtree builder

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: `prettify` (Task 1).
- Produces: `build_nav_tree(entries: list[tuple[str, str]]) -> list` — `entries` are `(remainder, full_rel_path)` pairs; returns a nested mkdocs nav list where files are bare path strings and folders are `{Pretty Name: [...]}`, ordered by remainder.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
def test_build_nav_tree_nests_folders():
    entries = [
        ("template.md", "kubernetes-resources/template-operator/template.md"),
        ("how-to-guides/copy.md", "kubernetes-resources/template-operator/how-to-guides/copy.md"),
        ("how-to-guides/deploy.md", "kubernetes-resources/template-operator/how-to-guides/deploy.md"),
    ]
    assert m.build_nav_tree(entries) == [
        {"How To Guides": [
            "kubernetes-resources/template-operator/how-to-guides/copy.md",
            "kubernetes-resources/template-operator/how-to-guides/deploy.md",
        ]},
        "kubernetes-resources/template-operator/template.md",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k build_nav_tree -v`
Expected: FAIL with `AttributeError: ... 'build_nav_tree'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/merge_docs.py`:

```python
def build_nav_tree(entries):
    root = {}
    for remainder, full in sorted(entries):
        parts = remainder.split("/")
        node = root
        for folder in parts[:-1]:
            node = node.setdefault(folder, {})
        node[parts[-1]] = full
    return _to_nav(root)


def _to_nav(node):
    out = []
    for key, val in node.items():
        if isinstance(val, dict):
            out.append({prettify(key): _to_nav(val)})
        else:
            out.append(val)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k build_nav_tree -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): auto-build nested nav subtree from paths"
```

---

### Task 4: Nav section lookup + subtree insertion

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: nothing from prior tasks.
- Produces:
  - `find_section(nav: list, title: str) -> list | None` — recursive search; returns the children list of the section whose key equals `title`, else `None`.
  - `insert_subtree(nav: list, under: str, title: str, subtree: list) -> None` — appends `{title: subtree}` under section `under`; if a `title` node already exists there, extends it. Raises `KeyError` if `under` not found.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
import pytest


def _sample_nav():
    return [
        {"Overview": ["index.md"]},
        {"API Reference": ["kubernetes-resources/quota.md"]},
    ]


def test_find_section():
    nav = _sample_nav()
    assert m.find_section(nav, "API Reference") == ["kubernetes-resources/quota.md"]
    assert m.find_section(nav, "Nope") is None


def test_insert_subtree_appends_title_node():
    nav = _sample_nav()
    m.insert_subtree(nav, "API Reference", "Template Operator", ["a/b.md"])
    assert nav[1] == {"API Reference": [
        "kubernetes-resources/quota.md",
        {"Template Operator": ["a/b.md"]},
    ]}


def test_insert_subtree_merges_existing_title():
    nav = _sample_nav()
    m.insert_subtree(nav, "API Reference", "Template Operator", ["a/b.md"])
    m.insert_subtree(nav, "API Reference", "Template Operator", ["a/c.md"])
    assert nav[1]["API Reference"][1] == {"Template Operator": ["a/b.md", "a/c.md"]}


def test_insert_subtree_missing_section_raises():
    nav = _sample_nav()
    with pytest.raises(KeyError):
        m.insert_subtree(nav, "Ghost", "Template Operator", ["a/b.md"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k "section or subtree" -v`
Expected: FAIL with `AttributeError: ... 'find_section'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/merge_docs.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k "section or subtree" -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): nest generated subtree under existing menu section"
```

---

### Task 5: Read/write the `nav:` block via text splice

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: nothing from prior tasks.
- Produces:
  - `read_nav(text: str) -> list` — parse the `nav:` block of an mkdocs.yml string into a Python list.
  - `write_nav(text: str, nav: list) -> str` — return `text` with its `nav:` block replaced by a serialized `nav`, leaving everything else byte-for-byte.
  - Both raise `ValueError` if no top-level `nav:` block exists.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
_MKDOCS = """\
site_name: Multi-Tenant Operator
markdown_extensions:
  - pymdownx.emoji:
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
nav:
  - Overview:
      - index.md
  - API Reference:
      - kubernetes-resources/quota.md
plugins:
  - search
"""


def test_read_nav():
    nav = m.read_nav(_MKDOCS)
    assert nav[0] == {"Overview": ["index.md"]}


def test_write_nav_preserves_other_lines():
    nav = m.read_nav(_MKDOCS)
    m.insert_subtree(nav, "API Reference", "Template Operator", ["a/b.md"])
    out = m.write_nav(_MKDOCS, nav)
    # python tag line and plugins block untouched
    assert "!!python/name:material.extensions.emoji.to_svg" in out
    assert out.strip().endswith("- search")
    # new node present and re-parses
    assert m.find_section(m.read_nav(out), "Template Operator") == ["a/b.md"]


def test_read_nav_missing_raises():
    with pytest.raises(ValueError):
        m.read_nav("site_name: x\n")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k nav_ -v`
Expected: FAIL with `AttributeError: ... 'read_nav'`

- [ ] **Step 3: Write minimal implementation**

Add `import yaml` to the top of `scripts/merge_docs.py`, then add:

```python
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
    if not block.endswith("\n"):
        block += "\n"
    return "".join(lines[:start]) + block + "".join(lines[end:])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k nav_ -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): splice nav block without touching rest of mkdocs.yml"
```

---

### Task 6: Load and normalize `merge.yaml`

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: `slugify` (Task 1).
- Produces: `load_config(path: str) -> list[dict]` — returns a list of normalized operator dicts with keys `title, repo, slug, docs_dir, exclude, mappings`. Applies defaults: `slug = slugify(title)`, `docs_dir = "content"`, `exclude = []`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
_CONFIG = """\
operators:
  - title: Template Operator
    repo: ../template-operator-docs
    mappings:
      - from: "kubernetes-resources/**"
        into: "kubernetes-resources"
        under: "API Reference"
  - title: Hibernation Operator
    repo: ../hibernation-operator-docs
    slug: hib
    docs_dir: site
    exclude: ["**/.gitkeep"]
    mappings:
      - from: "guides/**"
        into: "kubernetes-resources/tenant/how-to-guides"
        under: "Guides"
"""


def test_load_config_defaults(tmp_path):
    cfg = tmp_path / "merge.yaml"
    cfg.write_text(_CONFIG)
    ops = m.load_config(str(cfg))
    assert ops[0]["slug"] == "template-operator"
    assert ops[0]["docs_dir"] == "content"
    assert ops[0]["exclude"] == []
    assert ops[1]["slug"] == "hib"
    assert ops[1]["docs_dir"] == "site"
    assert ops[1]["exclude"] == ["**/.gitkeep"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k load_config -v`
Expected: FAIL with `AttributeError: ... 'load_config'`

- [ ] **Step 3: Write minimal implementation**

Add to `scripts/merge_docs.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k load_config -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): load and normalize merge.yaml"
```

---

### Task 7: Orchestration — copy files + inject nav

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: `glob_base`, `strip_base`, `compute_dest` (Task 1); `find_matches` (Task 2); `build_nav_tree` (Task 3); `insert_subtree` (Task 4); `read_nav`, `write_nav` (Task 5).
- Produces: `run(operators: list[dict], content_dir: str, mkdocs_path: str, repo_overrides: dict | None = None) -> None` — copies matched files into `content_dir` and rewrites the nav block of `mkdocs_path` in place. Raises on empty match, destination collision, or missing repo/docs_dir.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
def test_run_copies_files_and_injects_nav(tmp_path):
    # fake sub-operator repo
    repo = tmp_path / "template-operator-docs"
    _touch(repo / "content",
           "kubernetes-resources/template.md",
           "kubernetes-resources/how-to/copy.md")
    # mto-docs side
    content = tmp_path / "content"
    content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(_MKDOCS)

    operators = [{
        "title": "Template Operator",
        "repo": str(repo),
        "slug": "template-operator",
        "docs_dir": "content",
        "exclude": [],
        "mappings": [{"from": "kubernetes-resources/**",
                      "into": "kubernetes-resources", "under": "API Reference"}],
    }]
    m.run(operators, str(content), str(mkdocs))

    assert (content / "kubernetes-resources/template-operator/template.md").is_file()
    assert (content / "kubernetes-resources/template-operator/how-to/copy.md").is_file()
    node = m.find_section(m.read_nav(mkdocs.read_text()), "Template Operator")
    assert "kubernetes-resources/template-operator/template.md" in node


def test_run_empty_match_raises(tmp_path):
    repo = tmp_path / "repo"
    _touch(repo / "content", "other/x.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"; mkdocs.write_text(_MKDOCS)
    operators = [{"title": "T", "repo": str(repo), "slug": "t", "docs_dir": "content",
                  "exclude": [], "mappings": [{"from": "missing/**",
                  "into": "kubernetes-resources", "under": "API Reference"}]}]
    with pytest.raises(ValueError):
        m.run(operators, str(content), str(mkdocs))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k run_ -v`
Expected: FAIL with `AttributeError: ... 'run'`

- [ ] **Step 3: Write minimal implementation**

Add `import shutil` to the top of `scripts/merge_docs.py`, then add:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k run_ -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest -v`
Expected: PASS (all tasks' tests green)

- [ ] **Step 6: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): orchestrate copy + nav injection with fail-fast"
```

---

### Task 8: CLI entry point + repo overrides

**Files:**
- Modify: `scripts/merge_docs.py`
- Test: `tests/test_merge_docs.py`

**Interfaces:**
- Consumes: `load_config` (Task 6), `run` (Task 7).
- Produces:
  - `parse_repo_overrides(pairs: list[str]) -> dict` — turns `["slug=path", ...]` into `{slug: path}`.
  - `main(argv: list[str] | None = None) -> int` — CLI: `--config` (default `merge.yaml`), `--content-dir` (default `content`), `--mkdocs` (default `mkdocs.yml`), repeatable `--set-repo slug=path`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_merge_docs.py`:

```python
def test_parse_repo_overrides():
    assert m.parse_repo_overrides(["template-operator=/a/b", "hib=/c"]) == \
        {"template-operator": "/a/b", "hib": "/c"}


def test_main_end_to_end(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    _touch(repo / "content", "guides/create.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"; mkdocs.write_text(_MKDOCS)
    cfg = tmp_path / "merge.yaml"
    cfg.write_text(
        "operators:\n"
        "  - title: Template Operator\n"
        "    repo: /nonexistent\n"
        "    mappings:\n"
        "      - from: \"guides/**\"\n"
        "        into: \"kubernetes-resources\"\n"
        "        under: \"API Reference\"\n"
    )
    rc = m.main(["--config", str(cfg), "--content-dir", str(content),
                 "--mkdocs", str(mkdocs),
                 "--set-repo", f"template-operator={repo}"])
    assert rc == 0
    assert (content / "kubernetes-resources/template-operator/create.md").is_file()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_merge_docs.py -k "overrides or main_end" -v`
Expected: FAIL with `AttributeError: ... 'parse_repo_overrides'`

- [ ] **Step 3: Write minimal implementation**

Add `import argparse` and `import sys` to the top of `scripts/merge_docs.py`, then add:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_merge_docs.py -k "overrides or main_end" -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_docs.py tests/test_merge_docs.py
git commit -m "feat(merge): CLI entry point with repo overrides"
```

---

### Task 9: Control file + build integration + docs

**Files:**
- Create: `merge.yaml`
- Modify: `DockerfileLocal`
- Modify: `README.md`

**Interfaces:**
- Consumes: the finished `scripts/merge_docs.py`.
- Produces: committed `merge.yaml`, a build step in `DockerfileLocal`, and README documentation. No unit test — verified by a manual local run against the real sub-operator repos.

> **NOTE for implementer:** The `into`/`under` values below are the intended mappings — confirm with the maintainer before finalizing, and confirm the exact `under:` section titles exist verbatim in `theme_override/mkdocs.yml` (`API Reference`, `Guides`).

- [ ] **Step 1: Create `merge.yaml`**

```yaml
# Controls which sub-operator docs are merged into mto-docs at build time.
# Sub-operator repos are cloned by the pipeline; paths passed via --set-repo.
operators:
  - title: Template Operator
    repo: ../template-operator-docs
    mappings:
      - from: "kubernetes-resources/**"
        into: "kubernetes-resources"
        under: "API Reference"
      - from: "images/**"
        into: "images"          # assets only, no menu entry
    exclude:
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
    exclude:
      - "**/.gitkeep"
```

- [ ] **Step 2: Add the merge step to `DockerfileLocal`**

Insert after the `combine_mkdocs_config_yaml.py` line (currently line 18) and before `RUN mkdocs build`:

```dockerfile
# merge sub-operator docs (repos must be present in the build context /
# cloned by the pipeline; pass their paths with --set-repo). Runs after the
# config-combine so it can inject nav into the final mkdocs.yml.
RUN python scripts/merge_docs.py --config merge.yaml --content-dir content --mkdocs mkdocs.yml
```

- [ ] **Step 3: Verify locally against the real repos**

Run (adjust paths to your clones):

```bash
python -m pip install -r requirements-dev.txt
# combine step normally produces mkdocs.yml; for a local check copy the nav config:
cp theme_override/mkdocs.yml mkdocs.yml
python scripts/merge_docs.py \
  --set-repo template-operator=$HOME/Documents/work/template-operator-docs \
  --set-repo hibernation-operator=$HOME/Documents/work/hibernation-operator-docs
```

Expected: exits 0; `content/kubernetes-resources/template-operator/…` and
`content/kubernetes-resources/tenant/how-to-guides/hibernation-operator/…`
exist; `mkdocs.yml` nav shows `Template Operator` under `API Reference` and
`Hibernation Operator` under `Guides`. Then discard the local artifacts:

```bash
git checkout mkdocs.yml 2>/dev/null || rm -f mkdocs.yml
git clean -fd content/kubernetes-resources/template-operator content/images
```

- [ ] **Step 4: Document in `README.md`**

Add a short "Merging sub-operator docs" section explaining: `merge.yaml` controls
the merge; repos are cloned by the pipeline and passed via `--set-repo`; the step
runs after config-combine and before `mkdocs build`; production CI performs the
build inside the shared `stakater/.github` reusable workflow, so wiring the clone
+ merge step there is a separate coordination task.

- [ ] **Step 5: Commit**

```bash
git add merge.yaml DockerfileLocal README.md
git commit -m "feat(merge): add merge.yaml, wire into local build, document"
```

---

## Self-Review

**Spec coverage:**
- Copy rule `content/<into>/<slug>/<remainder>` → Tasks 1 (`compute_dest`/`strip_base`), 7 (`run`). ✓
- Glob include with `**` and specific files → Tasks 1 (`glob_base`), 2 (`find_matches`). ✓
- Exclude globs → Task 2. ✓
- Auto nav, titles from H1 (bare path strings), folder titles prettified → Task 3. ✓
- Nested under existing menu section, merge same-`under` mappings → Tasks 4, 7. ✓
- Preserve `!!python/...` tags / rest of mkdocs.yml → Task 5. ✓
- Defaults (slug, docs_dir, exclude) → Task 6. ✓
- Fail-fast (missing section, empty match, collision, missing repo) → Tasks 4, 7. ✓
- Assets without `under` copied, no menu entry → Tasks 7, 9 (`images/**`). ✓
- Repo path overridable via CLI/env → Task 8. ✓
- Build order after config-combine → Task 9. ✓

**Placeholder scan:** No TBD/TODO in code steps; the only note is the maintainer confirmation on `merge.yaml` mappings (data, not code). ✓

**Type consistency:** `find_matches` returns `list[str]`; `run` consumes those strings via `strip_base`/`compute_dest` (all str). `build_nav_tree` takes `(remainder, full_rel_path)` tuples produced in `run`. `read_nav`/`write_nav` operate on the same `nav` list `insert_subtree` mutates. Names match across tasks. ✓
