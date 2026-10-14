.DEFAULT_GOAL := help

# The project's one Makefile. Everything runs through the project virtualenv, which
# `make install` builds with uv from pyproject.toml + uv.lock. See docs/SDLC.md.
#
# Agents run targets as `bobp make <target>` (captures output, posts status). Team tooling such
# as chat and TL;DR summaries is provided by bobp itself (`bobp chat`, `bobp tldr`), not here.
PYTHON := .venv/bin/python
PYTHONS := 3.14 3.15
# The published package (docs/SDLC.md section 7).
FP := packages/fingerprint-sampler

# First line of any recipe that needs the environment.
define need_venv
	@test -x $(PYTHON) || { echo "No .venv - run 'make install' first"; exit 1; }
endef

define need_uv
	@command -v uv >/dev/null || { echo "uv is not installed - run 'pipx install uv' (see docs/SDLC.md)"; exit 1; }
endef

.PHONY: help install install-hooks check test test-fingerprint test-fingerling test-all smoke lint quality format secrets build release-check run fingerprint gharchive demo demo-live clean distclean via_index

help: ## Show available make targets
	@echo ""
	@echo "  Project targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: install-hooks ## Build .venv from uv.lock (all extras + dev tools) and install the git hooks
	$(need_uv)
	@uv sync --all-packages --all-extras --quiet
	@echo "Installed into .venv"

install-hooks: ## Point git at .githooks/ (gitleaks pre-commit scan)
	@git config core.hooksPath .githooks

check: ## Byte-compile all sources (fast syntax check, no tests run)
	$(need_venv)
	@$(PYTHON) -m compileall -q fingerling examples tests $(FP)/src $(FP)/tests

test: test-fingerprint test-fingerling ## Run both test suites

test-fingerprint: ## Tests of the published fingerprint-sampler package (ARGS="test_cli" for one module)
	$(need_venv)
	@cd $(FP) && $(CURDIR)/$(PYTHON) -m unittest $(if $(ARGS),$(ARGS),discover -s tests)

test-fingerling: ## Tests of the parked fingerling modules and the compatibility shims
	$(need_venv)
	@$(PYTHON) -m unittest discover -s tests

test-all: ## Run the test suite on every supported Python (3.14, 3.15) in throwaway environments
	$(need_uv)
	@for v in $(PYTHONS); do \
		echo "== Python $$v =="; \
		out=$$(uv run --isolated --all-packages --all-extras --quiet --python $$v sh -c 'python -m unittest discover -s $(FP)/tests && python -m unittest discover -s tests' 2>&1) \
			|| { echo "$$out" | tail -n 40; exit 1; }; \
		echo "$$out" | grep -E '^(Ran|OK|FAILED)'; \
	done

lint: ## Static checks: ruff lint + format check (changes nothing)
	$(need_venv)
	@.venv/bin/ruff check .
	@.venv/bin/ruff format --check .

quality: ## Report smells in the published package: extended ruff, dead code, complexity (never fails)
	$(need_venv)
	@echo "== ruff (extended rules)"; .venv/bin/ruff check $(FP)/src --select C90,SIM,PL,RET,ARG,PIE,FBT --output-format concise --exit-zero
	@echo "== vulture (dead code)"; .venv/bin/vulture $(FP)/src --min-confidence 60 --ignore-names total_occurrences,first_seen,last_seen || true
	@echo "== radon (complexity grade C or worse)"; .venv/bin/radon cc -s -nc $(FP)/src

format: ## Rewrite files to the project style (ruff format + import sorting)
	$(need_venv)
	@.venv/bin/ruff check --select I --fix .
	@.venv/bin/ruff format .

secrets: ## Scan the git history and working tree for leaked secrets (gitleaks)
	@command -v gitleaks >/dev/null || { echo "gitleaks is not installed - see docs/SDLC.md"; exit 1; }
	@gitleaks detect --source .

clean: ## Remove caches, build output and downloaded test data in data/ (keeps .venv)
	@find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +
	@rm -rf fingerling.egg-info .ruff_cache dist data

distclean: clean ## Also remove the virtualenv
	@rm -rf .venv

via_index: ## Build the via index required by the via MCP server
	@via index "$(CURDIR)"

build: ## Build the fingerprint-sampler wheel + sdist into dist/ and smoke-test the wheel in a clean environment
	$(need_uv)
	@rm -rf dist
	@uv build --package fingerprint-sampler --out-dir dist --quiet
	@uv run --isolated --no-project --quiet --with dist/*.whl fingerprint --version
	@ls dist

smoke: build ## Install the built wheel in a throwaway environment and run the smoke suite against it
	@uv run --isolated --no-project --quiet --with dist/*.whl python -m unittest discover -s $(FP)/smoke -t $(FP)/smoke

release-check: ## Fail unless TAG (e.g. TAG=v0.1.0) matches the fingerprint-sampler version
	$(need_uv)
	@version=$$(uv version --package fingerprint-sampler --short); \
	test "v$$version" = "$(TAG)" \
		|| { echo "Tag '$(TAG)' does not match fingerprint-sampler version '$$version' (expected v$$version)"; exit 1; }
	@echo "Tag $(TAG) matches fingerprint-sampler $$(uv version --package fingerprint-sampler --short)"

run: ## Run the fingerprint CLI (ARGS="merge --help")
	$(need_venv)
	@.venv/bin/fingerprint $(ARGS)

fingerprint: ## Merge JSONL events into a fingerprint set (ARGS="-p PROFILE -s SET [EVENTS|-]"; ARGS=--help for more)
	$(need_venv)
	@.venv/bin/fingerprint merge $(ARGS)

GH_HOUR ?= 2024-01-01-15
GH_DIR := data/gharchive

gharchive: ## Fingerprint one hour of GitHub events from GH Archive (GH_HOUR=YYYY-MM-DD-H); downloads it once into data/
	$(need_venv)
	@mkdir -p $(GH_DIR)
	@test -s $(GH_DIR)/$(GH_HOUR).json.gz || curl -sSfL -o $(GH_DIR)/$(GH_HOUR).json.gz https://data.gharchive.org/$(GH_HOUR).json.gz
	@gunzip -c $(GH_DIR)/$(GH_HOUR).json.gz | .venv/bin/fingerprint merge -p $(FP)/examples/gharchive.yaml -s $(GH_DIR)/gh.fingerprints.yaml -

demo: ## Run the interactive vaccination TUI (see docs/USER_GUIDE.md)
	$(need_venv)
	@$(PYTHON) -m examples.demo

demo-live: ## Run the TUI with real eBPF capture (needs Linux, root, bpftrace; see docs/USER_GUIDE.md)
	$(need_venv)
	@sudo $(PYTHON) -m examples.demo
