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


def test_product_subsections_collapses_single_page():
    nodes = m.product_subsections([
        ("Overview", ["templates/overview/index.md"]),
        ("Guides", ["templates/guides/a.md", "templates/guides/b.md"]),
    ])
    assert nodes == [
        {"Overview": "templates/overview/index.md"},          # single -> leaf
        {"Guides": ["templates/guides/a.md", "templates/guides/b.md"]},
    ]


def test_fill_placeholder_fills_and_raises():
    nav = [{"Templates": []}, {"Extensions": ["x.md"]}]
    m.fill_placeholder(nav, "Templates", [{"Overview": "t/o.md"}])
    assert nav[0] == {"Templates": [{"Overview": "t/o.md"}]}
    with pytest.raises(KeyError):
        m.fill_placeholder(nav, "Ghost", [])


def test_set_single_leaf_with_label():
    nav = [{"Reference": ["reference/api.md", "reference/rbac.md"]}]
    m._set_single_leaf(nav, "Reference", "reference/api.md", label="API Reference")
    assert nav[0]["Reference"][0] == {"API Reference": "reference/api.md"}


# --- duplicate auto-grouping ---

def test_read_h1(tmp_path):
    p = tmp_path / "argocd.md"
    p.write_text("<!-- comment -->\n\n# ArgoCD\n\nbody\n")
    assert m.read_h1(p) == "ArgoCD"
    p.write_text("no heading here\n## sub\n")
    assert m.read_h1(p) is None


def test_find_base_leaf():
    section = ["integrations/argocd.md", {"Vault": ["integrations/vault/vault.md"]},
               "integrations/devworkspace.md"]
    # mto's own argocd, excluding the merged copy
    assert m.find_base_leaf(section, "argocd.md",
                            {"integrations/hib/argocd.md"}) == "integrations/argocd.md"
    assert m.find_base_leaf(section, "missing.md", set()) is None


def test_apply_group_folds_leaves_into_folder():
    nav = [{"Integrations": [
        "integrations/argocd.md",
        "integrations/devworkspace.md",
        "integrations/hib/argocd.md",
    ]}]
    m.apply_group(nav, {"under": "Integrations", "title": "ArgoCD", "items": [
        {"title": "MTO", "page": "integrations/argocd.md"},
        {"title": "Hibernation", "page": "integrations/hib/argocd.md"},
    ]})
    assert nav[0] == {"Integrations": [
        {"ArgoCD": [
            {"MTO": "integrations/argocd.md"},
            {"Hibernation": "integrations/hib/argocd.md"},
        ]},
        "integrations/devworkspace.md",
    ]}   # folder takes the first leaf's slot; the other leaf is removed


def test_build_duplicate_groups_detects_collision(tmp_path):
    (tmp_path / "integrations").mkdir()
    (tmp_path / "integrations/argocd.md").write_text("# ArgoCD\n")
    (tmp_path / "integrations/hib").mkdir()
    (tmp_path / "integrations/hib/argocd.md").write_text("# ArgoCD\n")
    nav = [{"Integrations": ["integrations/argocd.md", "integrations/hib/argocd.md"]}]
    # a merged flat page from Hibernation collides with mto's own argocd
    flat_pages = [("Integrations", "integrations/hib/argocd.md", "Hibernation")]
    groups = m.build_duplicate_groups(nav, flat_pages, str(tmp_path), "MTO")
    assert groups == [{
        "under": "Integrations", "title": "ArgoCD",
        "items": [{"title": "MTO", "page": "integrations/argocd.md"},
                  {"title": "Hibernation", "page": "integrations/hib/argocd.md"}],
    }]


def test_build_duplicate_groups_no_collision_is_skipped(tmp_path):
    (tmp_path / "guides").mkdir(parents=True)
    (tmp_path / "guides").joinpath("unique.md").write_text("# Unique\n")
    nav = [{"Guides": ["guides/own.md"]}]
    flat_pages = [("Guides", "guides/hib/unique.md", "Hibernation")]
    assert m.build_duplicate_groups(nav, flat_pages, str(tmp_path), "MTO") == []


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


def test_load_config_section_defaults_to_title(tmp_path):
    cfg = tmp_path / "merge.yaml"
    cfg.write_text(
        "operators:\n"
        "  - title: Templates\n"
        "    repo: /x\n"
        "    mappings: []\n"
        "  - title: FinOps\n"
        "    section: Finance\n"
        "    repo: /y\n"
        "    mappings: []\n"
    )
    ops = m.load_config(str(cfg))
    assert ops[0]["section"] == "Templates"      # defaults to title
    assert ops[1]["section"] == "Finance"        # explicit override
    assert ops[0]["product_first"] is False      # no explicit section -> legacy
    assert ops[1]["product_first"] is True       # explicit section -> product-first


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


def test_run_auto_groups_duplicate_across_source_and_mto(tmp_path):
    repo = tmp_path / "hib-docs"
    _touch(repo / "content", "integrations/argocd.md")
    (repo / "content/integrations/argocd.md").write_text("# ArgoCD\n")
    content = tmp_path / "content"
    (content / "integrations").mkdir(parents=True)
    (content / "integrations/argocd.md").write_text("# ArgoCD\n")   # mto's own
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: Multi-Tenant Operator\nnav:\n"
        "  - Integrations:\n      - integrations/argocd.md\n"
    )
    operators = [{
        "title": "Hibernation Operator", "repo": str(repo), "slug": "hibernation-operator",
        "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "integrations/**", "into": "integrations",
                      "under": "Integrations", "flatten": True}],
    }]
    m.run(operators, str(content), str(mkdocs))

    section = m.find_section(m.read_nav(mkdocs.read_text()), "Integrations")
    # ArgoCD folder with mto's own (site_title from site_name) + the merged page
    assert {"ArgoCD": [
        {"Multi-Tenant Operator": "integrations/argocd.md"},
        {"Hibernation Operator": "integrations/hibernation-operator/argocd.md"},
    ]} in section
    # the standalone argocd leaves are gone
    assert "integrations/argocd.md" not in section


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


def test_insert_extra_list_under_existing_extra():
    text = (
        "docs_dir: content\n"
        "extra:\n"
        "  version:\n"
        "    provider: mike\n"
        "nav:\n"
        "  - index.md\n"
    )
    got = m.insert_extra_list(text, "nav_labels", ["Template Operator", "Hibernation Operator"])
    assert got == (
        "docs_dir: content\n"
        "extra:\n"
        "  nav_labels:\n"
        "  - Template Operator\n"
        "  - Hibernation Operator\n"
        "  version:\n"
        "    provider: mike\n"
        "nav:\n"
        "  - index.md\n"
    )


def test_insert_extra_list_appends_extra_when_missing():
    text = "docs_dir: content\nnav:\n  - index.md\n"
    got = m.insert_extra_list(text, "nav_labels", ["Template Operator"])
    assert got == (
        "docs_dir: content\n"
        "nav:\n"
        "  - index.md\n"
        "extra:\n"
        "  nav_labels:\n"
        "  - Template Operator\n"
    )


def test_insert_extra_list_empty_values_is_noop():
    text = "extra:\n  version:\n    provider: mike\n"
    assert m.insert_extra_list(text, "nav_labels", []) == text


def test_insert_extra_list_existing_key_raises():
    # a stale nav_labels already in the file would otherwise be duplicated, and
    # PyYAML keeps the last one on reload -- silently dropping our fresh labels
    text = "extra:\n  nav_labels:\n  - Stale Operator\n"
    with pytest.raises(ValueError, match="nav_labels"):
        m.insert_extra_list(text, "nav_labels", ["Template Operator"])


def test_validate_mapping_label_requires_flatten():
    with pytest.raises(ValueError, match="flatten"):
        m.validate_mapping({"from": "guides/**", "into": "guides",
                            "under": "Guides", "label": True})


def test_validate_mapping_label_conflicts_with_title():
    with pytest.raises(ValueError, match="title"):
        m.validate_mapping({"from": "guides/**", "into": "guides", "under": "Guides",
                            "flatten": True, "label": True, "title": "Guides"})


def test_validate_mapping_label_requires_under():
    with pytest.raises(ValueError, match="under"):
        m.validate_mapping({"from": "guides/**", "into": "guides",
                            "flatten": True, "label": True})


def test_validate_mapping_accepts_valid_mappings():
    m.validate_mapping({"from": "guides/**", "into": "guides", "under": "Guides",
                        "flatten": True, "label": True})
    m.validate_mapping({"from": "reference/api.md", "into": "reference/api",
                        "under": "API Reference", "flatten": True, "title": "Template"})
    m.validate_mapping({"from": "images/**", "into": "images"})


def test_run_label_groups_pages_under_operator_header(tmp_path):
    repo = tmp_path / "template-operator-docs"
    _touch(repo / "content", "guides/create.md", "guides/delete.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: MTO\nextra:\n  version:\n    provider: mike\n"
        "nav:\n  - Guides:\n      - guides/own.md\n"
    )
    operators = [{
        "title": "Template Operator", "repo": str(repo), "slug": "template-operator",
        "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "guides/**", "into": "guides", "under": "Guides",
                      "flatten": True, "label": True}],
    }]
    m.run(operators, str(content), str(mkdocs))

    out = mkdocs.read_text()
    section = m.find_section(m.read_nav(out), "Guides")
    # mto's own leaf stays first and bare, the operator's pages sit in a titled group
    assert section == [
        "guides/own.md",
        {"Template Operator": ["guides/template-operator/create.md",
                              "guides/template-operator/delete.md"]},
    ]
    # the theme needs the title in extra.nav_labels to render it as a label
    assert "  nav_labels:\n  - Template Operator\n" in out


def test_run_label_merges_two_mappings_into_one_group(tmp_path):
    repo = tmp_path / "repo"
    _touch(repo / "content", "guides/create.md", "howto/extra.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Guides:\n      - guides/own.md\n")
    operators = [{
        "title": "Template Operator", "repo": str(repo), "slug": "template-operator",
        "docs_dir": "content", "exclude": [],
        "mappings": [
            {"from": "guides/**", "into": "guides", "under": "Guides",
             "flatten": True, "label": True},
            {"from": "howto/**", "into": "guides", "under": "Guides",
             "flatten": True, "label": True},
        ],
    }]
    m.run(operators, str(content), str(mkdocs))

    section = m.find_section(m.read_nav(mkdocs.read_text()), "Guides")
    # one header, not two
    assert section == [
        "guides/own.md",
        {"Template Operator": ["guides/template-operator/create.md",
                              "guides/template-operator/extra.md"]},
    ]
    # nav_labels is de-duplicated (this fixture has no `extra:`, so the whole
    # appended block is exactly the one key with one entry)
    extra_block = mkdocs.read_text().split("extra:\n", 1)[1]
    assert extra_block == "  nav_labels:\n  - Template Operator\n"


def test_run_labelled_pages_are_not_folded_as_duplicates(tmp_path):
    repo = tmp_path / "hib-docs"
    _touch(repo / "content", "integrations/argocd.md")
    (repo / "content/integrations/argocd.md").write_text("# ArgoCD\n")
    content = tmp_path / "content"
    (content / "integrations").mkdir(parents=True)
    (content / "integrations/argocd.md").write_text("# ArgoCD\n")   # mto's own
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: Multi-Tenant Operator\nnav:\n"
        "  - Integrations:\n      - integrations/argocd.md\n"
    )
    operators = [{
        "title": "Hibernation Operator", "repo": str(repo), "slug": "hibernation-operator",
        "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "integrations/**", "into": "integrations",
                      "under": "Integrations", "flatten": True, "label": True}],
    }]
    m.run(operators, str(content), str(mkdocs))

    section = m.find_section(m.read_nav(mkdocs.read_text()), "Integrations")
    # the header disambiguates, so no shared "ArgoCD" folder is created
    assert section == [
        "integrations/argocd.md",
        {"Hibernation Operator": ["integrations/hibernation-operator/argocd.md"]},
    ]


def test_run_without_labels_writes_no_nav_labels(tmp_path):
    repo = tmp_path / "repo"
    _touch(repo / "content", "guides/create.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Guides:\n      - guides/own.md\n")
    operators = [{
        "title": "Template Operator", "repo": str(repo), "slug": "template-operator",
        "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "guides/**", "into": "guides", "under": "Guides",
                      "flatten": True}],
    }]
    m.run(operators, str(content), str(mkdocs))
    assert "nav_labels" not in mkdocs.read_text()


def test_run_invalid_label_mapping_raises(tmp_path):
    repo = tmp_path / "repo"
    _touch(repo / "content", "guides/create.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Guides:\n      - guides/own.md\n")
    operators = [{
        "title": "Template Operator", "repo": str(repo), "slug": "template-operator",
        "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "guides/**", "into": "guides", "under": "Guides",
                      "label": True}],   # no flatten
    }]
    with pytest.raises(ValueError, match="flatten"):
        m.run(operators, str(content), str(mkdocs))


def test_run_two_operators_label_into_same_section(tmp_path):
    # the real merge.yaml shape: Template Operator and Hibernation Operator both
    # label their own concepts into the shared Concepts section
    template_repo = tmp_path / "template-operator-docs"
    _touch(template_repo / "content", "concepts/tier.md")
    hib_repo = tmp_path / "hibernation-operator-docs"
    _touch(hib_repo / "content", "concepts/schedule.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Concepts:\n      - concepts/own.md\n")
    operators = [
        {
            "title": "Template Operator", "repo": str(template_repo),
            "slug": "template-operator", "docs_dir": "content", "exclude": [],
            "mappings": [{"from": "concepts/**", "into": "concepts", "under": "Concepts",
                          "flatten": True, "label": True}],
        },
        {
            "title": "Hibernation Operator", "repo": str(hib_repo),
            "slug": "hibernation-operator", "docs_dir": "content", "exclude": [],
            "mappings": [{"from": "concepts/**", "into": "concepts", "under": "Concepts",
                          "flatten": True, "label": True}],
        },
    ]
    m.run(operators, str(content), str(mkdocs))

    out = mkdocs.read_text()
    section = m.find_section(m.read_nav(out), "Concepts")
    # MTO's own leaf first, then the two operator groups, in operator order
    assert section == [
        "concepts/own.md",
        {"Template Operator": ["concepts/template-operator/tier.md"]},
        {"Hibernation Operator": ["concepts/hibernation-operator/schedule.md"]},
    ]
    assert "  nav_labels:\n  - Template Operator\n  - Hibernation Operator\n" in out


def test_run_unlabelled_operator_folds_while_labelled_one_stays_grouped(tmp_path):
    # one labelled operator, one unlabelled operator, both with a same-named page
    # as MTO's own: the unlabelled one still folds into a shared duplicate group;
    # the labelled one keeps its own page inside its operator header, unfolded
    labelled_repo = tmp_path / "template-operator-docs"
    _touch(labelled_repo / "content", "integrations/argocd.md")
    (labelled_repo / "content/integrations/argocd.md").write_text("# ArgoCD\n")
    unlabelled_repo = tmp_path / "hibernation-operator-docs"
    _touch(unlabelled_repo / "content", "integrations/argocd.md")
    (unlabelled_repo / "content/integrations/argocd.md").write_text("# ArgoCD\n")
    content = tmp_path / "content"
    (content / "integrations").mkdir(parents=True)
    (content / "integrations/argocd.md").write_text("# ArgoCD\n")   # mto's own
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: Multi-Tenant Operator\nnav:\n"
        "  - Integrations:\n      - integrations/argocd.md\n"
    )
    operators = [
        {
            "title": "Template Operator", "repo": str(labelled_repo),
            "slug": "template-operator", "docs_dir": "content", "exclude": [],
            "mappings": [{"from": "integrations/**", "into": "integrations",
                          "under": "Integrations", "flatten": True, "label": True}],
        },
        {
            "title": "Hibernation Operator", "repo": str(unlabelled_repo),
            "slug": "hibernation-operator", "docs_dir": "content", "exclude": [],
            "mappings": [{"from": "integrations/**", "into": "integrations",
                          "under": "Integrations", "flatten": True}],
        },
    ]
    m.run(operators, str(content), str(mkdocs))

    section = m.find_section(m.read_nav(mkdocs.read_text()), "Integrations")
    # the labelled operator's own ArgoCD stays inside its header, untouched
    assert {"Template Operator": ["integrations/template-operator/argocd.md"]} in section
    # mto's own leaf folded with the unlabelled operator's page into a shared folder
    assert {"ArgoCD": [
        {"Multi-Tenant Operator": "integrations/argocd.md"},
        {"Hibernation Operator": "integrations/hibernation-operator/argocd.md"},
    ]} in section
    # no bare leaves remain for either duplicate source
    assert "integrations/argocd.md" not in section
    assert "integrations/hibernation-operator/argocd.md" not in section


# --- merged pages (single page, per-source H2 sections) ---

def test_apply_concat_builds_page_and_leaf(tmp_path):
    content = tmp_path / "content"
    (content / "reference").mkdir(parents=True)
    (content / "reference/api.md").write_text(
        "# API Reference\n\n## Packages\n\nmto crds\n")          # mto's own (self)
    opdocs = tmp_path / "hib" / "content"
    (opdocs / "reference").mkdir(parents=True)
    (opdocs / "reference/api.md").write_text(
        "# API Reference\n\n## Widgets\n\nhib crds\n")
    nav = [{"Reference": ["reference/api.md", "reference/rbac.md"]}]
    op_ctx = {"Hibernation Operator": {"docs": opdocs, "op_map": {},
                                       "live_url": None, "style": "directory"}}
    targets = {"reference/api.md": {
        "under": "Reference", "as": "API Reference",
        "sections": [("Hibernation Operator", "Hibernation Operator", "reference/api.md")],
    }}
    m.apply_concat(nav, targets, str(content), op_ctx, "Tenant Operator")

    page = (content / "reference/api.md").read_text()
    assert page.startswith("# API Reference")
    assert "## Tenant Operator" in page and "## Hibernation Operator" in page
    assert "### Packages" in page and "### Widgets" in page          # demoted
    section = m.find_section(nav, "Reference")
    assert section[0] == {"API Reference": "reference/api.md"}       # labeled leaf
    assert "reference/rbac.md" in section                            # siblings kept


def test_shift_headings_skips_code_fences_and_caps():
    text = "# Title\n## Sec\n```yaml\n# not a heading\n```\n### Deep\n###### Max"
    assert m.shift_headings(text, 1) == (
        "## Title\n### Sec\n```yaml\n# not a heading\n```\n#### Deep\n###### Max")


def test_split_h1_removes_first_real_h1():
    text = "```\n# fake\n```\n# Real Title\n\nbody\n## sub"
    h1, body = m.split_h1(text)
    assert h1 == "Real Title"
    assert "# Real Title" not in body
    assert "# fake" in body and "## sub" in body   # fenced hash and rest kept




def test_run_product_first_fills_placeholder_and_concats(tmp_path):
    repo = tmp_path / "tpl"
    _touch(repo / "content", "overview/index.md",
           "guides/a.md", "guides/b.md")
    (repo / "content/reference").mkdir(parents=True)
    (repo / "content/reference/api.md").write_text(
        "# API Reference\n\n## Kinds\n\ntpl crds\n")
    content = tmp_path / "content"
    (content / "reference").mkdir(parents=True)
    (content / "reference/api.md").write_text(
        "# API Reference\n\n## Packages\n\nmto crds\n")
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: MTO\nnav:\n"
        "  - Templates: []\n"
        "  - Reference:\n      - reference/api.md\n")
    operators = [{
        "title": "Templates", "section": "Templates", "repo": str(repo),
        "slug": "templates", "docs_dir": "content", "exclude": [],
        "live_url": "https://d/templates/", "live_url_style": "directory",
        "mappings": [
            {"from": "overview/**", "into": "templates/overview", "under": "Overview"},
            {"from": "guides/**", "into": "templates/guides", "under": "Guides"},
            {"from": "reference/api.md", "concat_into": "reference/api.md",
             "under": "Reference", "as": "API Reference", "heading": "Template Operator"},
        ],
    }]
    m.run(operators, str(content), str(mkdocs), site_title="Tenant Operator")

    nav = m.read_nav(mkdocs.read_text())
    templates = m.find_section(nav, "Templates")
    assert {"Overview": "templates/templates/overview/index.md"} in templates  # single -> leaf
    assert {"Guides": ["templates/templates/guides/a.md",
                       "templates/templates/guides/b.md"]} in templates
    # concat page built, single labeled leaf, mto's own + operator sections
    page = (content / "reference/api.md").read_text()
    assert "## Tenant Operator" in page and "## Template Operator" in page
    assert "### Packages" in page and "### Kinds" in page
    ref = m.find_section(nav, "Reference")
    assert {"API Reference": "reference/api.md"} in ref
    # the concat source is NOT copied as a standalone page
    assert not (content / "templates/templates/reference").exists()


def test_run_concat_conflicting_under_raises(tmp_path):
    repo = tmp_path / "op"
    _touch(repo / "content", "reference/api.md")
    (repo / "content/reference/api.md").write_text("# API\n\n## X\n\nbody\n")
    content = tmp_path / "content"; content.mkdir()
    (content / "reference").mkdir()
    (content / "reference/api.md").write_text("# API\n\n## Own\n\nmto\n")
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Reference:\n      - reference/api.md\n")
    operators = [{
        "title": "Op", "section": None, "product_first": False,
        "repo": str(repo), "slug": "op", "docs_dir": "content", "exclude": [],
        "mappings": [
            {"from": "reference/api.md", "concat_into": "reference/api.md",
             "under": "Reference", "as": "API Reference", "heading": "One"},
            {"from": "reference/api.md", "concat_into": "reference/api.md",
             "under": "Somewhere Else", "heading": "Two"},   # conflicting under
        ],
    }]
    with pytest.raises(ValueError):
        m.run(operators, str(content), str(mkdocs))


def test_run_concat_multi_file_glob_each_file_becomes_a_section(tmp_path):
    # a single concat mapping whose `from` glob matches more than one file: each
    # matched file is recorded as its own section (heading, op, rel) in match
    # order, so all of them contribute to the merged page under the same heading.
    repo = tmp_path / "op"
    (repo / "content/guides").mkdir(parents=True)
    (repo / "content/guides/a.md").write_text("# Guides\n\n## First\n\nfrom a\n")
    (repo / "content/guides/b.md").write_text("# Guides\n\n## Second\n\nfrom b\n")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Guides: []\n")
    operators = [{
        "title": "Op", "section": None, "product_first": False,
        "repo": str(repo), "slug": "op", "docs_dir": "content", "exclude": [],
        "mappings": [
            {"from": "guides/*.md", "concat_into": "guides/combined.md",
             "under": "Guides", "as": "Combined Guides", "heading": "Op Guides"},
        ],
    }]
    m.run(operators, str(content), str(mkdocs), site_title="Tenant Operator")

    page = (content / "guides/combined.md").read_text()
    # both glob-matched files contribute a section (same heading, since it comes
    # from the mapping, not per-file), in sorted match order
    assert page.count("## Op Guides") == 2
    assert "### First" in page and "from a" in page
    assert "### Second" in page and "from b" in page
    section = m.find_section(m.read_nav(mkdocs.read_text()), "Guides")
    assert {"Combined Guides": "guides/combined.md"} in section


def test_run_product_first_missing_placeholder_raises(tmp_path):
    repo = tmp_path / "op"
    _touch(repo / "content", "overview/index.md")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Reference:\n      - r.md\n")  # no Templates placeholder
    operators = [{
        "title": "Templates", "section": "Templates", "product_first": True,
        "repo": str(repo), "slug": "templates", "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "overview/**", "into": "overview", "under": "Overview"}],
    }]
    with pytest.raises(KeyError):
        m.run(operators, str(content), str(mkdocs))


# --- menu order from the sub-operator's own nav ---

def test_read_source_order(tmp_path):
    repo = tmp_path / "op"; repo.mkdir()
    (repo / "mkdocs.yml").write_text(
        "site_name: Op\nnav:\n  - Guides:\n      - guides/b.md\n      - guides/a.md\n"
        "  - x.md\n")
    assert m.read_source_order(repo) == ["guides/b.md", "guides/a.md", "x.md"]


def test_read_source_order_missing_nav_is_empty(tmp_path):
    repo = tmp_path / "op"; repo.mkdir()
    assert m.read_source_order(repo) == []


def test_run_product_first_orders_by_suboperator_nav(tmp_path):
    repo = tmp_path / "op"
    _touch(repo / "content", "guides/zebra.md", "guides/alpha.md", "guides/mid.md",
           "guides/unlisted.md")
    # sub-op nav orders them zebra, mid, alpha (NOT alphabetical); unlisted absent
    (repo / "mkdocs.yml").write_text(
        "site_name: Op\nnav:\n  - Guides:\n"
        "      - guides/zebra.md\n      - guides/mid.md\n      - guides/alpha.md\n")
    content = tmp_path / "content"; content.mkdir()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: MTO\nnav:\n  - Op: []\n")
    operators = [{
        "title": "Op", "section": "Op", "product_first": True,
        "repo": str(repo), "slug": "op", "docs_dir": "content", "exclude": [],
        "mappings": [{"from": "guides/**", "into": "guides", "under": "Guides"}],
    }]
    m.run(operators, str(content), str(mkdocs))
    section = m.find_section(m.read_nav(mkdocs.read_text()), "Op")
    # nav order preserved; the page absent from the sub-op nav ranks last
    assert {"Guides": [
        "op/guides/zebra.md",
        "op/guides/mid.md",
        "op/guides/alpha.md",
        "op/guides/unlisted.md",
    ]} in section
