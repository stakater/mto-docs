"""Helpers for .github/workflows/doctest.yaml.

    python scripts/doctest_ci.py matrix               # pages.yaml -> GitHub Actions matrix JSON
    python scripts/doctest_ci.py newest-node-image    # kind release notes on stdin -> image ref
"""

import json
import re
import sys
from pathlib import Path

import yaml

NODE_IMAGE = re.compile(r"kindest/node:v(\d+)\.(\d+)\.(\d+)@sha256:[0-9a-f]+")


def newest_node_image(release_notes):
    """The newest node image a kind release lists. A release only lists images
    built for it, so this is always one that release supports."""
    found = {m.group(0): tuple(int(x) for x in m.groups()) for m in NODE_IMAGE.finditer(release_notes)}
    if not found:
        raise ValueError("no kindest/node image in the release notes")
    return max(found, key=found.get)


def matrix(config):
    return {
        "include": [
            {"page": entry["page"], "variant": v["name"], "file": v.get("file", "")}
            for entry in config["pages"]
            for v in entry["variants"]
        ]
    }


def main(argv):
    if argv[1:] == ["matrix"]:
        config = yaml.safe_load(Path("tests/doctest/pages.yaml").read_text())
        print(json.dumps(matrix(config)))
    elif argv[1:] == ["newest-node-image"]:
        print(newest_node_image(sys.stdin.read()))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
