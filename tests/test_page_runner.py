"""Tests for scripts/page_runner.py, the runner that executes a docs page."""

import textwrap

import pytest

import page_runner as dt


def page(text):
    return textwrap.dedent(text).lstrip()


PAGE = page(
    """
    # A page

    Create `demo/values.yaml`:

    ```yaml
    name: demo
    ```

    Run it:

    ```bash
    echo hello
    ```

    ```text
    hello
    ```

    This one fails on purpose:

    ```bash
    kubectl get configmap missing
    ```

    ```text
    Error from server (NotFound): configmaps "missing" not found
    ```

    ```yaml
    # an illustration, not a file
    kind: ConfigMap
    ```
    """
)


def test_parse_finds_files_commands_and_expected_failures():
    steps = dt.parse(PAGE)
    assert [s.kind for s in steps] == ["file", "run", "run"]
    assert steps[0].path == "demo/values.yaml"
    assert steps[0].body == "name: demo\n"
    assert steps[1].body == "echo hello"
    assert steps[1].expect_error is False
    assert steps[1].expected == "hello"
    assert steps[2].expect_error is True


def test_parse_ignores_blocks_without_a_create_line():
    steps = dt.parse(PAGE)
    assert not any("illustration" in s.body for s in steps)


def test_create_line_applies_only_to_the_next_block():
    text = page(
        """
        Create `a.yaml`:

        ```yaml
        a: 1
        ```

        ```yaml
        b: 2
        ```
        """
    )
    steps = dt.parse(text)
    assert [s.kind for s in steps] == ["file"]


@pytest.mark.parametrize(
    "rules, want",
    [
        ([], "image: kindest/node:v1.33.4"),
        ([{"from": "kindest/node:v1.33.4", "to": "kindest/node:v1.34.0"}], "image: kindest/node:v1.34.0"),
    ],
)
def test_substitutions_apply_to_commands_and_files(rules, want):
    text = page(
        """
        ```bash
        echo 'image: kindest/node:v1.33.4'
        ```
        """
    )
    steps = dt.apply_substitutions(dt.parse(text), rules)
    assert want in steps[0].body


def test_a_substitution_that_matches_nothing_is_an_error():
    steps = dt.parse("```bash\necho hi\n```\n")
    with pytest.raises(dt.DoctestError, match="matched nothing"):
        dt.apply_substitutions(steps, [{"from": "not there", "to": "x"}])


def test_run_writes_files_and_runs_commands(tmp_path):
    report = dt.run(dt.parse(PAGE), tmp_path, shell=_fake_shell({"kubectl get configmap missing": 1}))
    assert (tmp_path / "demo/values.yaml").read_text() == "name: demo\n"
    assert report.ok


def test_run_fails_when_a_command_fails(tmp_path):
    steps = dt.parse("```bash\nfalse-command\n```\n")
    report = dt.run(steps, tmp_path, shell=_fake_shell({"false-command": 2}))
    assert not report.ok
    assert "false-command" in report.failure


def test_run_fails_when_an_expected_error_does_not_happen(tmp_path):
    report = dt.run(dt.parse(PAGE), tmp_path, shell=_fake_shell({}))
    assert not report.ok
    assert "expected the command to fail" in report.failure


def test_run_can_resume_at_a_command(tmp_path):
    seen = []

    def shell(body, cwd):
        seen.append(body)
        return 1 if body.startswith("kubectl") else 0

    report = dt.run(dt.parse(PAGE), tmp_path, shell=shell, start="kubectl get")
    assert report.ok
    assert seen == ["kubectl get configmap missing"]
    # files are always written, so a resumed run still has the chart
    assert (tmp_path / "demo/values.yaml").exists()


def _fake_shell(exit_codes):
    def shell(body, cwd):
        return exit_codes.get(body, 0)

    return shell


def _registered_variants():
    from pathlib import Path

    import yaml

    root = Path(__file__).resolve().parent.parent
    config = yaml.safe_load((root / "tests/doctest/pages.yaml").read_text())
    for entry in config["pages"]:
        for variant in entry["variants"]:
            yield root, entry["page"], variant


@pytest.mark.parametrize("root, page_path, variant", list(_registered_variants()), ids=lambda v: str(v)[-40:])
def test_every_registered_variant_still_applies_to_its_page(root, page_path, variant):
    """A page edit that breaks a variant fails here, on the pull request, not
    in the scheduled end-to-end run a week later."""
    import yaml

    steps = dt.parse((root / page_path).read_text())
    assert any(s.kind == "run" for s in steps), f"{page_path} has no commands"
    if "file" in variant:
        rules = (yaml.safe_load((root / variant["file"]).read_text()) or {}).get("substitutions", [])
        dt.apply_substitutions(steps, rules)


def test_setup_runs_first_and_teardown_runs_even_after_a_failure(tmp_path):
    seen = []

    def shell(body, cwd):
        seen.append(body)
        return 3 if body == "page-command" else 0

    steps = dt.parse("```bash\npage-command\n```\n")
    report = dt.run(steps, tmp_path, shell=shell, setup="make-cluster", teardown="delete-cluster")
    assert not report.ok
    assert seen == ["make-cluster", "page-command", "delete-cluster"]


def test_a_failed_setup_skips_the_page_but_still_tears_down(tmp_path):
    seen = []

    def shell(body, cwd):
        seen.append(body)
        return 1 if body == "make-cluster" else 0

    report = dt.run(dt.parse("```bash\npage-command\n```\n"), tmp_path, shell=shell,
                    setup="make-cluster", teardown="delete-cluster")
    assert not report.ok and "setup failed" in report.failure
    assert seen == ["make-cluster", "delete-cluster"]


@pytest.mark.parametrize(
    "output, fails",
    [
        ("no", True),
        ("yes", False),
        ("Error from server (Forbidden): x", True),
        ('The configmaps "policy-check" is invalid: : ValidatingAdmissionPolicy denied', True),
        ("The answer is invalid in prose", False),
        ("nothing", False),
    ],
)
def test_documented_refusals_are_expected_failures(output, fails):
    steps = dt.parse(f"```bash\nkubectl auth can-i get pods\n```\n\n```text\n{output}\n```\n")
    assert steps[0].expect_error is fails
