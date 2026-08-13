# Local automation for building the docs with merged sub-operator content.
#
# The sub-operator repos to merge (and their mappings) are defined in merge.yaml.
# `make merge` is also what the CI pre-build hook runs (see .github/workflows).
VENV := .venv
PY   := $(VENV)/bin/python

# Where local clones of the sub-operator docs repos live, used by the *-local
# targets so a preview does not re-clone. Each repo is expected at
# $(SUBOPS)/<repo name from merge.yaml>, e.g. ~/Documents/work/template-operator-docs.
SUBOPS ?= $(HOME)/Documents/work

.DEFAULT_GOAL := help
.PHONY: help venv test theme merge merge-local screenshots screenshots-check docs-images serve serve-local clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

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

# Same merge, but against checkouts you already have, so no network and no clone.
# Whatever those checkouts have committed is what you preview, branch included.
merge-local: venv ## Merge from local sub-operator checkouts under SUBOPS (no cloning)
	@args=$$($(PY) -c "import sys; sys.path.insert(0,'scripts'); import merge_docs; \
	  print(' '.join('--set-repo %s=$(SUBOPS)/%s' % (o['slug'], o['repo'].rstrip('/').split('/')[-1].removesuffix('.git')) \
	  for o in merge_docs.load_config('merge.yaml')))"); \
	echo ">> merging from $(SUBOPS)"; \
	$(PY) scripts/merge_docs.py $$args

# The build resolves {{ screenshot: ... }} itself (see screenshots/mkdocs_hook.py).
screenshots: ## Capture live console screenshots into screenshots/captured/
	bash screenshots/capture.sh

screenshots-check: ## Read-only: check every {{ screenshot: ... }} has a captured image
	python3 screenshots/inject.py --check

docs-images: merge ## CI pre-build hook: merge sub-operator docs, then capture screenshots
	@test -n "$$PRE_BUILD_USER" -a -n "$$PRE_BUILD_PASSWORD" \
	  || { echo "docs-images: PRE_BUILD_USER/PRE_BUILD_PASSWORD not set"; exit 1; }
	@printf 'CONSOLE_USER=%s\nCONSOLE_PASSWORD=%s\n' "$$PRE_BUILD_USER" "$$PRE_BUILD_PASSWORD" > screenshots/.env
	bash screenshots/capture.sh
	python3 screenshots/inject.py --check

theme: venv ## Combine the shared theme with theme_override into dist/_theme and mkdocs.yml
	git submodule update --init --recursive
	$(VENV)/bin/pip install -q -r theme_common/requirements.txt
	$(PY) theme_common/scripts/combine_theme_resources.py -s theme_common/resources -ov theme_override/resources -o dist/_theme
	$(PY) theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml

serve: theme ## Full local preview: clones the sub-operator repos, then mkdocs serve
	PYTHON=$(abspath $(PY)) bash scripts/pre_build_merge.sh
	$(PY) -m mkdocs serve

serve-local: theme merge-local ## Same preview from local checkouts, no cloning
	$(PY) -m mkdocs serve

clean: ## Remove fetched repos and generated artifacts (surgical; never `git clean`)
	rm -rf .suboperators mkdocs.yml dist site
	@python3 -c "import sys;sys.path.insert(0,'scripts');import merge_docs;[print(o['slug']) for o in merge_docs.load_config('merge.yaml')]" 2>/dev/null \
	  | while read -r s; do [ -n "$$s" ] && find content -type d -name "$$s" -prune -exec rm -rf {} + 2>/dev/null || true; done
