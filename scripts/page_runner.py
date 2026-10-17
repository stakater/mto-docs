"""Run a docs page as a test: write the files it tells the reader to create, and
run its commands in order, as a reader following it would.

A page is runnable when it follows three conventions:

- ```bash blocks are commands, run in order in one working directory.
- A block preceded by a line "Create `<path>`:" is a file, written to <path>.
  Every other non-bash block is illustration and is ignored.
- A ```text block straight after a command is its documented output. If that
  output starts with "Error from server", or is exactly "no" (a refused
  `kubectl auth can-i`), the command is expected to fail, and the run fails if
  it succeeds.

A variant may also carry setup and teardown commands, for a page that assumes
something already exists, such as a cluster.

Variants rerun a page against something newer than it pins (a Kubernetes
version, a template-operator-v2 release) by substituting text in its steps. A
substitution that matches nothing fails the run, so a variant cannot go stale
silently when the page changes.

    python scripts/page_runner.py <page.md> <workdir> [--variant <variant.yaml>] [--start <command prefix>]
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

BLOCK = re.compile(r"^```(\w*)\n(.*?)\n```$", re.S | re.M)
CREATE = re.compile(r"Create `([^`]+)`:\s*$")
EXPECTED_ERROR = "Error from server"
REFUSAL = "no"  # what `kubectl auth can-i` prints, with exit code 1


class DoctestError(Exception):
    pass


@dataclass(frozen=True)
class Step:
    kind: str  # "file" or "run"
    body: str
    path: str = ""
    expected: str = ""
    expect_error: bool = False


@dataclass
class Report:
    ok: bool
    failure: str = ""


def parse(markdown):
    """Return the page's steps, in order."""
    blocks = list(BLOCK.finditer(markdown))
    steps = []
    pos = 0
    for i, block in enumerate(blocks):
        lang, body = block.group(1), block.group(2)
        prose = markdown[pos:block.start()]
        pos = block.end()
        last_line = prose.strip().splitlines()[-1] if prose.strip() else ""
        create = CREATE.search(last_line)
        if create:
            steps.append(Step("file", body + "\n", path=create.group(1)))
        elif lang == "bash":
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            expected = ""
            if nxt is not None and nxt.group(1) == "text" and not markdown[block.end():nxt.start()].strip():
                expected = nxt.group(2)
            steps.append(Step("run", body, expected=expected, expect_error=expected.startswith(EXPECTED_ERROR) or expected.strip() == REFUSAL))
    return steps


def apply_substitutions(steps, rules):
    """Apply each {from, to} rule to every step. A rule must match somewhere."""
    for rule in rules:
        old, new = rule["from"], rule["to"]
        if not any(old in s.body for s in steps):
            raise DoctestError(f"substitution {old!r} matched nothing; update the variant to the page")
        steps = [replace(s, body=s.body.replace(old, new)) for s in steps]
    return steps


def bash(body, cwd):
    print(f"\n$ {body}", flush=True)
    return subprocess.run(["bash", "-euo", "pipefail", "-c", body], cwd=cwd).returncode


def run(steps, workdir, shell=bash, start=None, setup=None, teardown=None):
    """Write files and run commands. Files are always written, so a run resumed
    with start still has everything the page created.

    setup runs before the page, for a page that assumes something exists (a
    cluster); teardown runs afterwards whatever happened."""
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    try:
        if setup and shell(setup, workdir) != 0:
            return Report(False, f"setup failed:\n{setup}")
        return _run_steps(steps, workdir, shell, start)
    finally:
        if teardown:
            shell(teardown, workdir)


def _run_steps(steps, workdir, shell, start):
    running = start is None
    for step in steps:
        if step.kind == "file":
            target = workdir / step.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(step.body)
            continue
        if not running and step.body.startswith(start):
            running = True
        if not running:
            continue
        code = shell(step.body, workdir)
        if step.expect_error and code == 0:
            return Report(False, f"expected the command to fail, as the page documents:\n{step.body}")
        if not step.expect_error and code != 0:
            return Report(False, f"command failed with exit code {code}:\n{step.body}")
    if not running:
        return Report(False, f"no command starts with {start!r}")
    return Report(True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page")
    ap.add_argument("workdir")
    ap.add_argument("--variant", help="YAML file with a list of {from, to} substitutions")
    ap.add_argument("--start", help="resume at the first command starting with this text")
    args = ap.parse_args(argv)

    steps = parse(Path(args.page).read_text())
    if args.variant:
        variant = yaml.safe_load(Path(args.variant).read_text()) or {}
        steps = apply_substitutions(steps, variant.get("substitutions", []))
    setup = teardown = None
    if args.variant:
        setup, teardown = variant.get("setup"), variant.get("teardown")
    report = run(steps, args.workdir, start=args.start, setup=setup, teardown=teardown)
    if not report.ok:
        print(f"\nFAILED: {args.page}\n{report.failure}", file=sys.stderr)
        return 1
    print(f"\nOK: {args.page}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
