#!/usr/bin/env bash
# Capture docs screenshots with browser-runner.
#   ./screenshots/capture.sh            -> _seed, every capture flow, _teardown
#   ./screenshots/capture.sh tenants    -> only flows/tenants.yaml
#   ./screenshots/capture.sh _seed      -> setup only (create docs-seed-template)
#   ./screenshots/capture.sh _teardown  -> cleanup only (delete all docs-* objects)
# A failing flow does NOT stop the run, so _teardown always gets its chance to clean
# up. Config comes from screenshots/config.env, credentials from screenshots/.env
# (see .env.example). .env wins on conflicts.
# Output -> screenshots/captured/.
set -u

DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE="${RUNNER_IMAGE:-ghcr.io/stakater/browser-runner:latest}"
OUT="$DIR/captured"
CONFIG_FILE="$DIR/config.env"
ENV_FILE="$DIR/.env"           # credentials (and any overrides)

# Credentials come from .env locally; CI sets them in the environment instead.
creds=()
if [ -f "$ENV_FILE" ]; then
    creds=(--env-file "$ENV_FILE")
elif [ -n "${CONSOLE_USER:-}" ] && [ -n "${CONSOLE_PASSWORD:-}" ]; then
    creds=(-e CONSOLE_USER -e CONSOLE_PASSWORD)
else
    echo "FAIL: no credentials - copy .env.example to $ENV_FILE, or set" >&2
    echo "      CONSOLE_USER and CONSOLE_PASSWORD in the environment" >&2
    exit 1
fi

mkdir -p "$OUT"
# The runner writes as pwuser (uid 1000), which does not own the checkout on a
# GitHub runner.
chmod 0777 "$OUT"

if [ $# -ge 1 ]; then
    flows="$DIR/flows/$1.yaml"
    if [ ! -f "$flows" ]; then
        echo "FAIL: no such flow: $flows" >&2
        exit 1
    fi
    # Single-flow run: delete THIS flow's own outputs (parsed from its YAML)
    # so a partial run can never leave stale shots of later steps behind.
    # PNGs from other flows stay for comparison.
    grep -oE 'path: *[A-Za-z0-9._-]+\.png' "$flows" | awk '{print $NF}' \
        | while read -r p; do rm -f "$OUT/$p"; done
else
    # Full run: _seed first (creates the shared template), capture flows in the
    # middle, _teardown last (deletes every docs-* object). Underscore-prefixed
    # flows are excluded from the middle so ordering is explicit, not alphabetical.
    flows="$DIR/flows/_seed.yaml
$(ls "$DIR"/flows/*.yaml | grep -v '/flows/_')
$DIR/flows/_teardown.yaml"
    # Start clean so review never sees stale images from a past run.
    rm -f "$OUT"/*.png
fi

failed=0
for flow in $flows; do
    name="$(basename "$flow" .yaml)"
    echo "RUN: $name"
    if docker run --rm \
        --env-file "$CONFIG_FILE" \
        "${creds[@]}" \
        -e E2E_ARTIFACTS_DIR=/out \
        -v "$OUT:/out" \
        -v "$flow:/etc/e2e/test.yaml:ro" \
        "$IMAGE" /etc/e2e/test.yaml; then
        echo "PASS: $name"
    else
        echo "FAIL: $name (exit $?)"
        failed=1
    fi
done

exit $failed
