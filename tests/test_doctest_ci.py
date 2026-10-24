"""Tests for scripts/doctest_ci.py, the helpers the doc-test workflow calls."""

import doctest_ci as ci

RELEASE_NOTES = """
## New Features
Images pre-built for this release:
- v1.37.0: `kindest/node:v1.37.0@sha256:a1ed`
- v1.36.4: `kindest/node:v1.36.4@sha256:099e`
- v1.34.11: `kindest/node:v1.34.11@sha256:44e2`
Mentioned elsewhere: kindest/node:v1.37.0@sha256:a1ed
"""


def test_newest_node_image_is_the_highest_version_not_the_first_listed():
    notes = RELEASE_NOTES.replace("v1.34.11", "v1.38.0")
    assert ci.newest_node_image(notes) == "kindest/node:v1.38.0@sha256:44e2"


def test_newest_node_image_compares_versions_numerically():
    notes = "kindest/node:v1.9.0@sha256:aa kindest/node:v1.10.1@sha256:bb"
    assert ci.newest_node_image(notes) == "kindest/node:v1.10.1@sha256:bb"


def test_newest_node_image_fails_when_none_listed():
    import pytest

    with pytest.raises(ValueError, match="no kindest/node image"):
        ci.newest_node_image("no images here")


def test_matrix_has_one_entry_per_page_and_variant():
    config = {
        "pages": [
            {"page": "a.md", "variants": [{"name": "as-written"}, {"name": "k8s", "file": "v.yaml"}]},
        ]
    }
    assert ci.matrix(config) == {
        "include": [
            {"page": "a.md", "variant": "as-written", "file": ""},
            {"page": "a.md", "variant": "k8s", "file": "v.yaml"},
        ]
    }
