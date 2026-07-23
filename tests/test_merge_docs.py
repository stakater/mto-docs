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


def test_compute_dest_flatten_keeps_slug_drops_subdirs():
    # flatten: into/<slug>/<basename> -- slug kept for collision-safe namespacing,
    # sub-folders dropped
    assert m.compute_dest("api.md", "kubernetes-resources", "template", flatten=True) == \
        "kubernetes-resources/template/api.md"
    assert m.compute_dest("api/resource-supervisor.md", "kubernetes-resources", "hib",
                          flatten=True) == "kubernetes-resources/hib/resource-supervisor.md"
    # non-flatten keeps slug + full structure (default)
    assert m.compute_dest("api/rs.md", "kubernetes-resources", "hib") == \
        "kubernetes-resources/hib/api/rs.md"


def test_build_nav_tree_nests_folders():
    # entries: (remainder, dest, src)
    entries = [
        ("template.md", "kubernetes-resources/template-operator/template.md", "reference/template.md"),
        ("how-to-guides/copy.md", "kubernetes-resources/template-operator/how-to-guides/copy.md", "reference/how-to-guides/copy.md"),
        ("how-to-guides/deploy.md", "kubernetes-resources/template-operator/how-to-guides/deploy.md", "reference/how-to-guides/deploy.md"),
    ]
    assert m.build_nav_tree(entries) == [
        {"How To Guides": [
            "kubernetes-resources/template-operator/how-to-guides/copy.md",
            "kubernetes-resources/template-operator/how-to-guides/deploy.md",
        ]},
        "kubernetes-resources/template-operator/template.md",
    ]


def test_build_nav_tree_uses_folder_titles_from_source_nav():
    # folder "api" (source reference/api) is titled from the sub-op nav, not prettify
    entries = [
        ("api/rs.md", "kubernetes-resources/hib/api/rs.md", "reference/api/rs.md"),
    ]
    titles = {"reference/api": "API Reference"}
    assert m.build_nav_tree(entries, titles) == [
        {"API Reference": ["kubernetes-resources/hib/api/rs.md"]},
    ]
    # fallback to prettify when the source folder isn't in the map
    assert m.build_nav_tree(entries) == [
        {"Api": ["kubernetes-resources/hib/api/rs.md"]},
    ]


def test_build_nav_tree_duplicate_remainder_raises():
    entries = [
        ("template.md", "kubernetes-resources/into-a/template.md", "a/template.md"),
        ("template.md", "kubernetes-resources/into-b/template.md", "b/template.md"),
    ]
    with pytest.raises(ValueError):
        m.build_nav_tree(entries)


def test_build_nav_tree_folder_file_conflict_raises():
    entries = [
        ("a", "kubernetes-resources/a", "x/a"),
        ("a/b.md", "kubernetes-resources/a/b.md", "x/a/b.md"),
    ]
    with pytest.raises(ValueError):
        m.build_nav_tree(entries)


def test_nav_folder_titles_from_nav():
    nav = [
        {"Reference": [
            {"API Reference": [
                "reference/api/resource-supervisor.md",
                "reference/api/cluster-resource-supervisor.md",
            ]},
            "reference/configuration.md",
            "reference/rbac.md",
        ]},
        {"Guides": ["guides/create-resource-supervisor.md"]},
    ]
    titles = m.nav_folder_titles(nav)
    assert titles["reference/api"] == "API Reference"
    assert titles["reference"] == "Reference"
    assert titles["guides"] == "Guides"


def test_nav_folder_titles_deepest_section_wins():
    # a broad section whose files all live in one subfolder must NOT claim that
    # subfolder over the more specific inner section
    nav = [
        {"Guides": [
            {"Templates": [
                "guides/templates/copying.md",
                "guides/templates/deploying.md",
            ]},
        ]},
    ]
    titles = m.nav_folder_titles(nav)
    assert titles["guides/templates"] == "Templates"   # not "Guides"


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


def test_insert_leaves_appends_directly():
    nav = _sample_nav()
    m.insert_leaves(nav, "API Reference", [{"Templates": "k/api.md"}, "k/rs.md"])
    assert nav[1] == {"API Reference": [
        "kubernetes-resources/quota.md",
        {"Templates": "k/api.md"},
        "k/rs.md",
    ]}


def test_insert_leaves_missing_section_raises():
    nav = _sample_nav()
    with pytest.raises(KeyError):
        m.insert_leaves(nav, "Ghost", ["a/b.md"])


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
    out, ext = m.rewrite_links(text, "getting-started/quick-start.md",
                               "getting-started/hib/quick-start.md", mapping)
    assert out == "See [guide](../../guides/hib/create-resource-supervisor.md)."
    assert ext == []


def test_rewrite_links_image_and_anchor():
    mapping = {
        "getting-started/installation/openshift.md": "getting-started/hib/installation/openshift.md",
        "images/operatorHub.png": "images/hib/operatorHub.png",
        "getting-started/installation/kubernetes.md": "getting-started/hib/installation/kubernetes.md",
    }
    src = "getting-started/installation/openshift.md"
    dst = "getting-started/hib/installation/openshift.md"
    img, _ = m.rewrite_links("![oh](../../images/operatorHub.png)", src, dst, mapping)
    assert img == "![oh](../../../images/hib/operatorHub.png)"
    # anchor is preserved
    link, _ = m.rewrite_links("[k](kubernetes.md#argocd)", src, dst, mapping)
    assert link == "[k](kubernetes.md#argocd)"  # same dir, resolves to itself -> in map


def test_rewrite_links_leaves_external_and_uncopied():
    mapping = {"a/x.md": "a/slug/x.md"}
    text = ("[ext](https://example.com) [anchor](#section) "
            "[abs](/root.md) [missing](../other/y.md)")
    # no live_url -> unmatched links left as-is
    out, ext = m.rewrite_links(text, "a/x.md", "a/slug/x.md", mapping)
    assert out == text
    assert ext == []


def test_rewrite_links_reference_style():
    mapping = {"guides/b.md": "guides/slug/b.md", "images/x.png": "images/slug/x.png"}
    text = "See ![img][ref].\n\n[ref]: ../images/x.png\n"
    out, _ = m.rewrite_links(text, "guides/b.md", "guides/slug/b.md", mapping)
    assert "[ref]: ../../images/slug/x.png" in out


# --- external (live_url) fallback for non-whitelisted targets ---

def test_rewrite_links_external_directory_style():
    mapping = {"guides/b.md": "guides/slug/b.md"}   # only b is whitelisted
    text = "See [arch](../concepts/architecture.md#intro)."
    out, ext = m.rewrite_links(text, "guides/b.md", "guides/slug/b.md", mapping,
                               live_url="https://docs.example.com/op/",
                               live_url_style="directory")
    assert out == "See [arch](https://docs.example.com/op/concepts/architecture/#intro)."
    assert ext == ["concepts/architecture.md"]


def test_rewrite_links_external_html_style():
    mapping = {"guides/b.md": "guides/slug/b.md"}
    text = "[cfg](../reference/configuration.md)"
    out, _ = m.rewrite_links(text, "guides/b.md", "guides/slug/b.md", mapping,
                             live_url="https://docs.example.com/op", live_url_style="html")
    assert out == "[cfg](https://docs.example.com/op/reference/configuration.html)"


def test_rewrite_links_external_index_and_asset():
    mapping = {"guides/b.md": "guides/slug/b.md"}
    src, dst = "guides/b.md", "guides/slug/b.md"
    home, _ = m.rewrite_links("[home](../index.md)", src, dst, mapping,
                              live_url="https://docs.example.com/op/")
    assert home == "[home](https://docs.example.com/op/)"
    img, _ = m.rewrite_links("![d](../images/diagram.png)", src, dst, mapping,
                             live_url="https://docs.example.com/op/")
    assert img == "![d](https://docs.example.com/op/images/diagram.png)"


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
    branch: develop
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
    assert ops[0]["branch"] == ""          # default -> repo default branch
    assert ops[1]["slug"] == "hib"
    assert ops[1]["docs_dir"] == "site"
    assert ops[1]["exclude"] == ["**/.gitkeep"]
    assert ops[1]["branch"] == "develop"


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


def test_run_flatten_single_file_title_and_multi_leaves(tmp_path):
    repo = tmp_path / "template-operator-docs"
    _touch(repo / "content",
           "reference/api.md",
           "guides/templates/copy.md",
           "guides/templates/deploy.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: MTO\nnav:\n  - API Reference:\n      - k/quota.md\n"
        "  - Guides:\n      - k/own.md\n"
    )
    operators = [{
        "title": "Template", "repo": str(repo), "slug": "template",
        "docs_dir": "content", "exclude": [],
        "mappings": [
            {"from": "reference/api.md", "into": "kubernetes-resources",
             "under": "API Reference", "title": "Templates", "flatten": True},
            {"from": "guides/**", "into": "guides", "under": "Guides", "flatten": True},
        ],
    }]
    m.run(operators, str(content), str(mkdocs))

    # flattened path: slug kept, sub-dirs dropped
    assert (content / "kubernetes-resources/template/api.md").is_file()
    assert (content / "guides/template/copy.md").is_file()
    assert (content / "guides/template/deploy.md").is_file()

    nav = m.read_nav(mkdocs.read_text())
    # single-file mapping with title -> one renamed leaf, directly under the section
    assert {"Templates": "kubernetes-resources/template/api.md"} in \
        m.find_section(nav, "API Reference")
    # multi-file flatten -> bare dest leaves (mkdocs derives titles from each H1)
    guides = m.find_section(nav, "Guides")
    assert "guides/template/copy.md" in guides and "guides/template/deploy.md" in guides
    # no operator wrapper folder was created
    assert m.find_section(nav, "Template") is None


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
