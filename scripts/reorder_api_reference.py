"""Reshape the type sections of a crd-ref-docs markdown page.

Two things, both of which the generator has no knob for:

- **Order.** crd-ref-docs renders every type of a group version alphabetically
  (`GroupVersionDetails.SortedTypes`), so `Tenant` ends up buried after
  `AccessControl`. Instead the types are walked as the tree they are: depth
  first from each kind, in field order, so the types a section references sit
  directly below it — scroll past `TenantSpec` and you are in the types
  `TenantSpec` is made of. Kinds are taken one at a time, so their subtrees do
  not interleave, and anything no kind reaches is left alphabetical at the end.
- **Depth.** A kind's heading sits directly under its package; every type that
  something else references is one step smaller, however deep in the tree it is,
  so a package reads as a list of kinds with their parts under them.
  The `Resource Types` heading and its list of kinds are dropped along the way:
  it was the only thing between a package and its types, and with the kinds
  ordered first it said nothing the page does not.

Run it after generation, alongside the fixups in
docs/generating-api-reference.md:

    python scripts/reorder_api_reference.py content/reference/api.md

Section bodies are moved verbatim (only their heading level and trailing blank
lines change), and re-running the script changes nothing.
"""
import argparse
import re
import sys
from pathlib import Path

# A group-version heading, e.g. "tenantoperator.stakater.com/v1beta3". Type
# names never contain a slash, so this cannot match a type section.
GV_RE = re.compile(r"^[A-Za-z0-9.\-]+/[A-Za-z0-9.\-]+$")
HEADING_RE = re.compile(r"(#{1,6})\s+(.*\S)\s*$")
KIND_BULLET_RE = re.compile(r"^-\s+\[([A-Za-z0-9_]+)\]")
KIND_ROW_RE = re.compile(r"\|\s*`kind`\s+_string_\s*\|")
ANCHOR_LINK_RE = re.compile(r"\]\(#([A-Za-z0-9_-]+)\)")
SUFFIXES = ("Spec", "Status")


def anchor(name):
    """The in-page anchor crd-ref-docs links a type by."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def code_flags(lines):
    """One bool per line, True inside a ``` / ~~~ fence, so that a `#` in a
    YAML sample is never mistaken for a heading. Mirrors merge_docs._md_lines;
    kept local so this script can be dropped into a sub-operator docs repo."""
    fence, out = None, []
    for line in lines:
        mo = re.match(r"(`{3,}|~{3,})", line.strip())
        marker = mo.group(1)[0] if mo else None
        if fence:
            out.append(True)
            if marker == fence:
                fence = None
        elif marker:
            fence = marker
            out.append(True)
        else:
            out.append(False)
    return out


def headings(lines, flags):
    """(line index, level, title) for every ATX heading outside code fences."""
    out = []
    for i, line in enumerate(lines):
        if flags[i]:
            continue
        mo = HEADING_RE.match(line)
        if mo:
            out.append((i, len(mo.group(1)), mo.group(2).strip()))
    return out


def type_order(kinds, blocks, refs=None):
    """The order type sections should appear in: one depth-first walk per kind,
    following its fields in the order they are declared, so whatever a section
    references sits directly below it. `<Kind>Spec` and `<Kind>Status` are
    walked after the kind as a fallback, in case `ignoreFields` dropped the rows
    that would have linked them. Types no kind reaches follow alphabetically.
    With no kinds at all the existing order is kept."""
    refs = refs or {}
    order, seen = [], set()

    def walk(name):
        if name not in blocks or name in seen:
            return
        seen.add(name)
        order.append(name)
        for ref in refs.get(name, ()):
            walk(ref)

    for kind in kinds:
        walk(kind)
        for suffix in SUFFIXES:
            walk(kind + suffix)
    rest = [name for name in blocks if name not in seen]
    order.extend(sorted(rest) if kinds else rest)
    return order


def references(lines, flags, spans):
    """Forward references per type, in field order: the other types of this group
    version that its field table links to, plus an alias's underlying type.
    Only table rows are read, so the `Appears in:` bullet list — which points the
    other way — never becomes an edge."""
    known = {anchor(name): name for name in spans}
    out = {}
    for name, (start, stop) in spans.items():
        refs, seen = [], {name}
        for j in range(start, stop):
            line = lines[j]
            if flags[j]:
                continue
            if not (line.startswith("|") or "_Underlying type:_" in line):
                continue
            for target in ANCHOR_LINK_RE.findall(line):
                ref = known.get(target)
                if ref and ref not in seen:
                    seen.add(ref)
                    refs.append(ref)
        out[name] = refs
    return out


def resource_types_span(lines, flags, section, rt_level):
    """The half-open line range one group version's `Resource Types` heading and
    its list of kinds occupy, so the caller can drop the block."""
    for i, level, title in section:
        if level != rt_level or title.lower() != "resource types":
            continue
        j, seen_bullet = i + 1, False
        while j < len(lines):
            line = lines[j].strip()
            if flags[j] or line.startswith("#"):
                break
            if not line:
                if seen_bullet:
                    break
                j += 1
                continue
            if not KIND_BULLET_RE.match(line):
                break
            seen_bullet = True
            j += 1
        return i, j
    return None


def kind_sections(lines, flags, spans):
    """The type names that are kinds, in page order. crd-ref-docs gives a type
    with a GVK an `apiVersion` and a `kind` row that nothing else has, so this
    does not depend on the `Resource Types` list — which this script deletes, and
    which therefore cannot be the thing that identifies them."""
    kinds = []
    for name, (start, stop) in sorted(spans.items(), key=lambda kv: kv[1][0]):
        for j in range(start, stop):
            if not flags[j] and KIND_ROW_RE.match(lines[j]):
                kinds.append(name)
                break
    return kinds


def at_level(lines, flags, start, stop, level):
    """One type section with its heading set to `level`, and any heading inside
    it moved by the same amount. Kinds sit directly under their package; a type
    something else references is a step smaller, whatever its depth in the tree.
    Trailing blank lines are normalised to one, so that the section which
    happened to sit last in the file does not end up flush against the next
    heading once moved."""
    mo = HEADING_RE.match(lines[start])
    shift = level - len(mo.group(1)) if mo else 0
    out = []
    for j in range(start, stop):
        line = lines[j]
        if not flags[j] and shift:
            mo = HEADING_RE.match(line)
            if mo:
                depth = min(max(len(mo.group(1)) + shift, 1), 6)
                line = "#" * depth + line[len(mo.group(1)):]
        out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return out + [""]


def reorder_text(text):
    lines = text.splitlines()
    flags = code_flags(lines)
    heads = headings(lines, flags)

    out, pos = [], 0
    for n, (start, level, title) in enumerate(heads):
        if not GV_RE.match(title):
            continue
        end = len(lines)
        for i, lvl, _ in heads[n + 1:]:
            if lvl <= level:
                end = i
                break
        section = [h for h in heads if start < h[0] < end]
        # Every heading just below the package is a type section, at whichever
        # level it currently sits: crd-ref-docs puts them all at level + 2 under
        # `Resource Types`, and this script leaves kinds at level + 1 and the
        # rest at level + 2, so both shapes have to be recognised.
        types = [(i, t) for i, lvl, t in section
                 if level < lvl <= level + 2 and t.lower() != "resource types"]
        if not types:
            continue

        rt_span = resource_types_span(lines, flags, section, level + 1)
        bounds = [i for i, _ in types] + [end]
        spans = {t: (i, bounds[k + 1]) for k, (i, t) in enumerate(types)}
        refs = references(lines, flags, spans)
        kinds = set(kind_sections(lines, flags, spans))
        blocks = {t: at_level(lines, flags, *spans[t],
                              level + (1 if t in kinds else 2))
                  for t in spans}
        # the package doc, up to whatever the types used to be introduced by
        preamble = lines[pos:rt_span[0] if rt_span else types[0][0]]
        while preamble and not preamble[-1].strip():
            preamble.pop()
        out.extend(preamble + [""])
        for name in type_order(kind_sections(lines, flags, spans), blocks, refs):
            out.extend(blocks[name])
        pos = end
    out.extend(lines[pos:])

    result = "\n".join(out)
    return result + "\n" if text.endswith("\n") else result


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Order kinds before their nested types in a crd-ref-docs "
                    "page, and drop the Resource Types wrapper.")
    ap.add_argument("paths", nargs="+", type=Path, help="markdown files to reorder")
    ap.add_argument("--check", action="store_true",
                    help="report files that would change, write nothing")
    args = ap.parse_args(argv)

    changed = []
    for path in args.paths:
        text = path.read_text(encoding="utf-8")
        new = reorder_text(text)
        if new == text:
            print(f"{path}: already reshaped")
            continue
        changed.append(path)
        if args.check:
            print(f"{path}: would be reshaped")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"{path}: reshaped")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
