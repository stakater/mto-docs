import pytest
import merge_docs as m
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


def test_build_nav_tree_duplicate_remainder_raises():
    entries = [
        ("template.md", "kubernetes-resources/into-a/template.md"),
        ("template.md", "kubernetes-resources/into-b/template.md"),
    ]
    with pytest.raises(ValueError):
        m.build_nav_tree(entries)


def test_build_nav_tree_folder_file_conflict_raises():
    entries = [
        ("a", "kubernetes-resources/a"),
        ("a/b.md", "kubernetes-resources/a/b.md"),
    ]
    with pytest.raises(ValueError):
        m.build_nav_tree(entries)


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


# --- link rewriting (Path B) ---

def test_rewrite_links_cross_folder():
    # getting-started page links to a guides page; both moved under different roots
    mapping = {
        "getting-started/quick-start.md": "getting-started/hib/quick-start.md",
        "guides/create-resource-supervisor.md": "guides/hib/create-resource-supervisor.md",
    }
    text = "See [guide](../guides/create-resource-supervisor.md)."
    out = m.rewrite_links(text, "getting-started/quick-start.md",
                          "getting-started/hib/quick-start.md", mapping)
    assert out == "See [guide](../../guides/hib/create-resource-supervisor.md)."


def test_rewrite_links_image_and_anchor():
    mapping = {
        "getting-started/installation/openshift.md": "getting-started/hib/installation/openshift.md",
        "images/operatorHub.png": "images/hib/operatorHub.png",
        "getting-started/installation/kubernetes.md": "getting-started/hib/installation/kubernetes.md",
    }
    src = "getting-started/installation/openshift.md"
    dst = "getting-started/hib/installation/openshift.md"
    img = m.rewrite_links("![oh](../../images/operatorHub.png)", src, dst, mapping)
    assert img == "![oh](../../../images/hib/operatorHub.png)"
    # anchor is preserved
    link = m.rewrite_links("[k](kubernetes.md#argocd)", src, dst, mapping)
    assert link == "[k](kubernetes.md#argocd)"  # same dir, resolves to itself? -> in map


def test_rewrite_links_leaves_external_and_uncopied():
    mapping = {"a/x.md": "a/slug/x.md"}
    text = ("[ext](https://example.com) [anchor](#section) "
            "[abs](/root.md) [missing](../other/y.md)")
    out = m.rewrite_links(text, "a/x.md", "a/slug/x.md", mapping)
    assert out == text  # nothing in map is referenced; all left as-is


def test_rewrite_links_reference_style():
    mapping = {"guides/b.md": "guides/slug/b.md", "images/x.png": "images/slug/x.png"}
    text = "See ![img][ref].\n\n[ref]: ../images/x.png\n"
    out = m.rewrite_links(text, "guides/b.md", "guides/slug/b.md", mapping)
    assert "[ref]: ../../images/slug/x.png" in out


# combine_mkdocs_config_yaml.py emits the merged config via PyYAML, which puts
# sequence items under a mapping key at column 0 (indentless). read_nav/write_nav
# must handle that, not just the hand-indented theme_override style above.
_MKDOCS_COMBINED = (
    "site_name: MTO\n"
    "nav:\n"
    "- Overview:\n"
    "  - index.md\n"
    "- API Reference:\n"
    "  - kubernetes-resources/quota.md\n"
    "plugins:\n"
    "- search\n"
)


def test_read_nav_indentless_sequence():
    nav = m.read_nav(_MKDOCS_COMBINED)
    assert nav[0] == {"Overview": ["index.md"]}
    assert m.find_section(nav, "API Reference") == ["kubernetes-resources/quota.md"]


def test_write_nav_indentless_preserves_trailing_key():
    nav = m.read_nav(_MKDOCS_COMBINED)
    m.insert_subtree(nav, "API Reference", "Template Operator", ["a/b.md"])
    out = m.write_nav(_MKDOCS_COMBINED, nav)
    # the key after the nav block must survive untouched
    assert "plugins:\n- search\n" in out
    assert out.startswith("site_name: MTO\n")
    assert m.find_section(m.read_nav(out), "Template Operator") == ["a/b.md"]


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
