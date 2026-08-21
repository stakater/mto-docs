from reorder_api_reference import (code_flags, headings, kind_sections,
                                   references, reorder_text, type_order)


def sections(text, base=2):
    """(level, name) for every type section, in document order."""
    lines = text.splitlines()
    flags = code_flags(lines)
    return [(lvl, title) for _, lvl, title in headings(lines, flags)
            if base < lvl <= base + 2 and title.lower() != "resource types"]


def names(text, base=2):
    return [name for _, name in sections(text, base)]


def levels(text, base=2):
    return {name: lvl for lvl, name in sections(text, base)}


GV = "tenantoperator.stakater.com/v1beta3"


def gv_page(kinds, types, gv_level=2, fields=None, reshaped=False):
    """A minimal crd-ref-docs page: one group version; `kinds` get the
    apiVersion/kind rows crd-ref-docs gives a type with a GVK; `fields` maps a
    type to the types its field table links to. `reshaped` renders the page as
    this script leaves it — no Resource Types block, types one level up."""
    gv, rt = "#" * gv_level, "#" * (gv_level + 1)
    out = ["# API Reference\n", f"{gv} {GV}\n", "Package v1beta3 docs\n"]
    if kinds and not reshaped:
        out.append(f"{rt} Resource Types")
        out += [f"- [{k}](#{k.lower()})" for k in kinds]
        out.append("")
    for t in types:
        # fresh output has every type at the same level, under Resource Types;
        # reshaped has the kinds a level above the types they reference
        depth = gv_level + 2
        if reshaped and t in kinds:
            depth = gv_level + 1
        body = ["#" * depth + f" {t}", "", f"{t} does a thing.", ""]
        rows = []
        if t in kinds:
            rows.append("| `apiVersion` _string_ | `group.io/v1` | | |")
            rows.append(f"| `kind` _string_ | `{t}` | | |")
        for ref in (fields or {}).get(t, []):
            rows.append(f"| `f{ref}` _[{ref}](#{ref.lower()})_ | doc | | |")
        if rows:
            body += ["| Field | Description | Default | Validation |",
                     "| --- | --- | --- | --- |"] + rows + [""]
        out.append("\n".join(body))
    return "\n".join(out)


class TestTypeOrder:
    def test_depth_first_in_field_order(self):
        blocks = ["Tenant", "TenantSpec", "TenantStatus", "AccessControl",
                  "Namespaces", "Sandboxes"]
        refs = {"Tenant": ["TenantSpec", "TenantStatus"],
                "TenantSpec": ["AccessControl", "Namespaces"],
                "Namespaces": ["Sandboxes"]}
        assert type_order(["Tenant"], blocks, refs) == [
            "Tenant", "TenantSpec", "AccessControl", "Namespaces", "Sandboxes",
            "TenantStatus"]

    def test_a_types_own_types_sit_directly_below_it(self):
        blocks = ["Kind", "KindSpec", "A", "B", "KindStatus"]
        refs = {"Kind": ["KindSpec", "KindStatus"], "KindSpec": ["A", "B"]}
        order = type_order(["Kind"], blocks, refs)
        assert order[order.index("KindSpec") + 1:order.index("KindStatus")] == \
            ["A", "B"]

    def test_spec_and_status_still_follow_a_kind_with_no_linking_rows(self):
        # ignoreFields can drop the rows that would have linked them
        blocks = ["Tenant", "TenantSpec", "TenantStatus", "Helper"]
        assert type_order(["Tenant"], blocks, {}) == [
            "Tenant", "TenantSpec", "TenantStatus", "Helper"]

    def test_kinds_do_not_interleave(self):
        blocks = ["A", "ASpec", "AHelper", "B", "BSpec", "BHelper"]
        refs = {"A": ["ASpec"], "ASpec": ["AHelper"],
                "B": ["BSpec"], "BSpec": ["BHelper"]}
        assert type_order(["A", "B"], blocks, refs) == [
            "A", "ASpec", "AHelper", "B", "BSpec", "BHelper"]

    def test_types_no_kind_reaches_follow_alphabetically(self):
        blocks = ["Tenant", "TenantSpec", "Zebra", "Orphan"]
        refs = {"Tenant": ["TenantSpec"]}
        assert type_order(["Tenant"], blocks, refs) == [
            "Tenant", "TenantSpec", "Orphan", "Zebra"]

    def test_a_reference_cycle_terminates(self):
        blocks = ["Kind", "A", "B"]
        refs = {"Kind": ["A"], "A": ["B"], "B": ["A", "Kind"]}
        assert type_order(["Kind"], blocks, refs) == ["Kind", "A", "B"]

    def test_a_reference_to_a_type_with_no_section_is_skipped(self):
        blocks = ["Kind", "KindSpec"]
        refs = {"Kind": ["KindSpec"], "KindSpec": ["ObjectMeta"]}
        assert type_order(["Kind"], blocks, refs) == ["Kind", "KindSpec"]

    def test_no_kinds_keeps_the_existing_order(self):
        assert type_order([], ["Beta", "Alpha"], {}) == ["Beta", "Alpha"]


class TestReferences:
    def build(self, page):
        lines = page.splitlines()
        flags = code_flags(lines)
        from reorder_api_reference import headings
        heads = headings(lines, flags)
        types = [(i, t) for i, lvl, t in heads if lvl == 4]
        bounds = [i for i, _ in types] + [len(lines)]
        spans = {t: (i, bounds[k + 1]) for k, (i, t) in enumerate(types)}
        return lines, flags, spans

    def test_field_table_links_become_references(self):
        page = gv_page(["Kind"], ["Kind", "KindSpec"],
                       fields={"Kind": ["KindSpec"]})
        lines, flags, spans = self.build(page)
        assert references(lines, flags, spans)["Kind"] == ["KindSpec"]

    def test_appears_in_backreference_is_not_a_reference(self):
        page = "\n".join([
            "# API Reference\n", "## group.io/v1\n",
            "#### Kind\n", "docs\n",
            "| Field | Description | Default | Validation |",
            "| --- | --- | --- | --- |",
            "| `spec` _[KindSpec](#kindspec)_ | doc | | |\n",
            "#### KindSpec\n",
            "_Appears in:_",
            "- [Kind](#kind)\n",
        ])
        lines, flags, spans = self.build(page)
        refs = references(lines, flags, spans)
        assert refs["Kind"] == ["KindSpec"]
        assert refs["KindSpec"] == []          # the back-edge is not followed

    def test_an_alias_references_its_underlying_type(self):
        page = "\n".join([
            "# API Reference\n", "## group.io/v1\n",
            "#### Alias\n",
            "_Underlying type:_ _[Real](#real)_\n",
            "#### Real\n", "docs\n",
        ])
        lines, flags, spans = self.build(page)
        assert references(lines, flags, spans)["Alias"] == ["Real"]

    def test_kinds_are_found_by_their_own_table_rows(self):
        page = gv_page(["Beta", "Alpha"], ["Alpha", "AlphaSpec", "Beta"])
        lines, flags, spans = self.build(page)
        # page order, not the order they were listed in
        assert kind_sections(lines, flags, spans) == ["Alpha", "Beta"]


class TestReorderText:
    def test_walks_the_tree_from_each_kind(self):
        page = gv_page(["Tenant"],
                       ["AccessControl", "Namespaces", "Tenant", "TenantSpec",
                        "TenantStatus"],
                       fields={"Tenant": ["TenantSpec", "TenantStatus"],
                               "TenantSpec": ["AccessControl", "Namespaces"]})
        assert names(reorder_text(page)) == [
            "Tenant", "TenantSpec", "AccessControl", "Namespaces",
            "TenantStatus"]

    def test_drops_the_resource_types_heading_and_its_list(self):
        page = gv_page(["Tenant"], ["AccessControl", "Tenant"])
        out = reorder_text(page)
        assert "Resource Types" not in out
        assert "- [Tenant](#tenant)" not in out

    def test_kinds_sit_directly_under_the_package(self):
        page = gv_page(["Tenant"], ["AccessControl", "Tenant"])
        out = reorder_text(page)
        assert "### Tenant\n" in out and "#### Tenant\n" not in out
        assert "## " + GV + "\n\nPackage v1beta3 docs\n\n### Tenant\n" in out

    def test_a_referenced_type_is_one_step_smaller_at_any_depth(self):
        page = gv_page(["Tenant"],
                       ["AccessControl", "Namespaces", "Sandboxes", "Tenant",
                        "TenantSpec"],
                       fields={"Tenant": ["TenantSpec"],
                               "TenantSpec": ["AccessControl", "Namespaces"],
                               "Namespaces": ["Sandboxes"]})
        # Sandboxes is three references deep and still only one level smaller
        assert levels(reorder_text(page)) == {
            "Tenant": 3, "TenantSpec": 4, "AccessControl": 4,
            "Namespaces": 4, "Sandboxes": 4}

    def test_a_type_no_kind_reaches_is_a_step_smaller_too(self):
        page = gv_page(["Tenant"], ["Orphan", "Tenant"])
        assert levels(reorder_text(page)) == {"Tenant": 3, "Orphan": 4}

    def test_body_of_each_section_travels_with_its_heading(self):
        page = gv_page(["Tenant"], ["AccessControl", "Tenant"])
        out = reorder_text(page)
        assert "### Tenant\n\nTenant does a thing." in out
        assert "#### AccessControl\n\nAccessControl does a thing." in out

    def test_every_section_is_separated_by_a_blank_line(self):
        # the section that happened to sit last in the file must not end up
        # flush against the next heading once it is moved
        page = gv_page(["Tenant"], ["AccessControl", "Tenant", "TenantSpec"])
        assert "does a thing.\n###" not in reorder_text(page)

    def test_reorders_a_page_it_has_already_reshaped(self):
        # kinds come from each type's own rows, so the deleted Resource Types
        # list is not needed to walk the tree a second time
        page = gv_page(["Tenant"], ["AccessControl", "Tenant", "TenantSpec"],
                       fields={"Tenant": ["TenantSpec"],
                               "TenantSpec": ["AccessControl"]},
                       reshaped=True)
        out = reorder_text(page)
        assert names(out) == ["Tenant", "TenantSpec", "AccessControl"]
        assert levels(out) == {"Tenant": 3, "TenantSpec": 4,
                               "AccessControl": 4}
        assert out == reorder_text(out)

    def test_group_versions_are_reordered_independently(self):
        page = "\n".join([
            "# API Reference\n",
            "## group.io/v1\n",
            "### Resource Types",
            "- [Alpha](#alpha)",
            "",
            "#### AHelper\n",
            "#### Alpha\n",
            "| Field | Description | Default | Validation |",
            "| --- | --- | --- | --- |",
            "| `kind` _string_ | `Alpha` | | |\n",
            "## group.io/v2\n",
            "### Resource Types",
            "- [Beta](#beta)",
            "",
            "#### BHelper\n",
            "#### Beta\n",
            "| Field | Description | Default | Validation |",
            "| --- | --- | --- | --- |",
            "| `kind` _string_ | `Beta` | | |\n",
        ])
        out = reorder_text(page)
        first, _, second = out.partition("## group.io/v2")
        assert names(first) == ["Alpha", "AHelper"]
        assert names(second) == ["Beta", "BHelper"]

    def test_works_on_merged_heading_levels(self):
        # merge_docs demotes every heading by one, so types arrive at level 5
        page = gv_page(["Tenant"], ["AccessControl", "Tenant", "TenantSpec"],
                       gv_level=3, fields={"Tenant": ["TenantSpec"]})
        out = reorder_text(page)
        assert names(out, base=3) == ["Tenant", "TenantSpec", "AccessControl"]
        assert levels(out, base=3) == {"Tenant": 4, "TenantSpec": 5,
                                       "AccessControl": 5}

    def test_headings_inside_code_fences_are_not_sections(self):
        page = "\n".join([
            "# API Reference\n",
            "## group.io/v1\n",
            "### Resource Types",
            "- [Tenant](#tenant)",
            "",
            "#### AccessControl\n",
            "```yaml",
            "#### NotAType",
            "```\n",
            "#### Tenant\n",
            "| Field | Description | Default | Validation |",
            "| --- | --- | --- | --- |",
            "| `kind` _string_ | `Tenant` | | |\n",
        ])
        out = reorder_text(page)
        assert names(out) == ["Tenant", "AccessControl"]
        assert "#### NotAType" in out                 # untouched inside the fence
        assert out.index("#### AccessControl") < out.index("#### NotAType")

    def test_content_outside_any_group_version_is_preserved(self):
        page = "\n".join([
            "# API Reference\n",
            "<!-- markdownlint-disable -->\n",
            "## Packages",
            "- [group.io/v1](#groupiov1)\n",
            "## group.io/v1\n",
            "### Resource Types",
            "- [Tenant](#tenant)",
            "",
            "#### AccessControl\n",
            "#### Tenant\n",
            "## Trailing prose\n",
            "Not a group version.\n",
        ])
        out = reorder_text(page)
        assert "<!-- markdownlint-disable -->" in out
        assert "## Packages" in out
        assert "- [group.io/v1](#groupiov1)" in out   # the package list stays
        assert out.rstrip().endswith("Not a group version.")

    def test_is_idempotent(self):
        page = gv_page(["Tenant", "Quota"],
                       ["AccessControl", "Quota", "QuotaSpec", "Tenant",
                        "TenantSpec", "TenantStatus", "Zebra"],
                       fields={"Tenant": ["TenantSpec", "TenantStatus"],
                               "TenantSpec": ["AccessControl"],
                               "Quota": ["QuotaSpec"]})
        once = reorder_text(page)
        assert reorder_text(once) == once

    def test_trailing_newline_is_preserved(self):
        page = gv_page(["Tenant"], ["AccessControl", "Tenant"])
        assert reorder_text(page + "\n").endswith("\n")

    def test_page_without_group_versions_is_unchanged(self):
        page = "# API Reference\n\nNothing generated yet.\n"
        assert reorder_text(page) == page
