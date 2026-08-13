#!/usr/bin/env bash
# Pre-build hook for the shared versioned-doc workflow.
#
# Clones the sub-operator repos listed in merge.yaml and merges their docs into
# content/ and the combined mkdocs.yml. Must run AFTER prepare_theme(_pr).sh
# (which produces mkdocs.yml) and BEFORE `mike deploy` (which runs mkdocs build).
#
# Auth: if PRE_BUILD_TOKEN is set, it is injected into https clone URLs so
# private sub-operator repos can be cloned.
set -euo pipefail

CONFIG="${1:-merge.yaml}"
WORKDIR=".suboperators"
PYTHON="${PYTHON:-python3}"
mkdir -p "$WORKDIR"

set_args=()
while IFS=$'\t' read -r slug repo branch; do
  [ -z "$slug" ] && continue
  dest="$WORKDIR/$slug"
  url="$repo"
  # inject token for https URLs (skip ssh/local paths)
  # if [ -n "${PRE_BUILD_TOKEN:-}" ] && [ "${repo#https://}" != "$repo" ]; then
  #   url="https://x-access-token:${PRE_BUILD_TOKEN}@${repo#https://}"
  # fi
  # empty branch -> clone the repo's default branch
  branch_arg=()
  [ -n "$branch" ] && branch_arg=(--branch "$branch")
  echo ">> cloning $slug${branch:+ (branch $branch)}"
  rm -rf "$dest"
  git clone --depth 1 "${branch_arg[@]}" "$url" "$dest"
  set_args+=(--set-repo "$slug=$dest")
done < <("$PYTHON" -c "import sys; sys.path.insert(0,'scripts'); import merge_docs; [print(op['slug'], op['repo'], op['branch'], sep='\t') for op in merge_docs.load_config('$CONFIG')]")

echo ">> merging sub-operator docs"
"$PYTHON" scripts/merge_docs.py --config "$CONFIG" "${set_args[@]}"
echo ">> pre-build merge complete"
