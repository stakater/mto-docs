# Local automation for building the docs with merged sub-operator content.
#
# The sub-operator repos to merge (and their mappings) are defined in merge.yaml.
# `make merge` is also what the CI pre-build hook runs (see .github/workflows).
VENV := .venv
PY   := $(VENV)/bin/python

.DEFAULT_GOAL := help
.PHONY: help venv test merge serve clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

venv: ## Create the local virtualenv if missing
	@test -x $(PY) || python3 -m venv $(VENV)
	@$(VENV)/bin/pip install -q --upgrade pip

test: venv ## Run the merge_docs unit tests
	$(VENV)/bin/pip install -q -r requirements-dev.txt
	$(PY) -m pytest

# Clones the repos in merge.yaml and merges their docs into content/ + mkdocs.yml.
# Assumes mkdocs.yml already exists (produced by the theme-combine step). This is
# exactly what the CI pre-build hook runs; use `make serve` for a standalone
# local preview. Set PRE_BUILD_TOKEN to clone private repos.
merge: ## Clone sub-operator repos and merge their docs (the CI pre-build hook)
	bash scripts/pre_build_merge.sh

serve: venv ## Full local preview: combine theme, merge sub-operator docs, mkdocs serve
	git submodule update --init --recursive
	$(VENV)/bin/pip install -q -r theme_common/requirements.txt
	$(PY) theme_common/scripts/combine_theme_resources.py -s theme_common/resources -ov theme_override/resources -o dist/_theme
	$(PY) theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml
	PYTHON=$(abspath $(PY)) bash scripts/pre_build_merge.sh
	$(PY) -m mkdocs serve

clean: ## Remove fetched repos and generated artifacts (surgical; never `git clean`)
	rm -rf .suboperators mkdocs.yml dist site
	@python3 -c "import sys;sys.path.insert(0,'scripts');import merge_docs;[print(o['slug']) for o in merge_docs.load_config('merge.yaml')]" 2>/dev/null \
	  | while read -r s; do [ -n "$$s" ] && find content -type d -name "$$s" -prune -exec rm -rf {} + 2>/dev/null || true; done
