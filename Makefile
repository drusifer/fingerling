.DEFAULT_GOAL := help

# The project's one Makefile. Everything runs through the project virtualenv, which
# `make install` builds with uv from pyproject.toml + uv.lock. See docs/SDLC.md.
#
# Agents run targets as `bobp make <target>` (captures output, posts status). Team tooling such
# as chat and TL;DR summaries is provided by bobp itself (`bobp chat`, `bobp tldr`), not here.
PYTHON := .venv/bin/python
PYTHONS := 3.14 3.15

# First line of any recipe that needs the environment.
define need_venv
	@test -x $(PYTHON) || { echo "No .venv - run 'make install' first"; exit 1; }
endef

define need_uv
	@command -v uv >/dev/null || { echo "uv is not installed - run 'pipx install uv' (see docs/SDLC.md)"; exit 1; }
endef

.PHONY: help install install-hooks check test test-all lint format secrets demo demo-live clean distclean via_index

help: ## Show available make targets
	@echo ""
	@echo "  Project targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: install-hooks ## Build .venv from uv.lock (all extras + dev tools) and install the git hooks
	$(need_uv)
	@uv sync --all-extras --quiet
	@echo "Installed into .venv"

install-hooks: ## Point git at .githooks/ (gitleaks pre-commit scan)
	@git config core.hooksPath .githooks

check: ## Byte-compile all sources (fast syntax check, no tests run)
	$(need_venv)
	@$(PYTHON) -m compileall -q fingerling examples tests

test: ## Run the tests of the parked fingerling modules against the installed sketch-tastic
	$(need_venv)
	@$(PYTHON) -m unittest discover -s tests

test-all: ## Run the test suite on every supported Python (3.14, 3.15) in throwaway environments
	$(need_uv)
	@for v in $(PYTHONS); do \
		echo "== Python $$v =="; \
		out=$$(uv run --isolated --all-extras --quiet --python $$v python -m unittest discover -s tests 2>&1) \
			|| { echo "$$out" | tail -n 40; exit 1; }; \
		echo "$$out" | grep -E '^(Ran|OK|FAILED)'; \
	done

lint: ## Static checks: ruff lint + format check (changes nothing)
	$(need_venv)
	@.venv/bin/ruff check .
	@.venv/bin/ruff format --check .

format: ## Rewrite files to the project style (ruff format + import sorting)
	$(need_venv)
	@.venv/bin/ruff check --select I --fix .
	@.venv/bin/ruff format .

secrets: ## Scan the git history and working tree for leaked secrets (gitleaks)
	@command -v gitleaks >/dev/null || { echo "gitleaks is not installed - see docs/SDLC.md"; exit 1; }
	@gitleaks detect --source .

clean: ## Remove caches, build output, downloaded data in data/ and directories left empty (keeps .venv)
	@find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +
	@rm -rf fingerling.egg-info .ruff_cache dist data
	@find . -depth -type d -empty -not -path './.git*' -not -path './.venv*' -delete

distclean: clean ## Also remove the virtualenv
	@rm -rf .venv

via_index: ## Build the via index required by the via MCP server
	@via index "$(CURDIR)"

demo: ## Run the interactive vaccination TUI (see docs/USER_GUIDE.md)
	$(need_venv)
	@$(PYTHON) -m examples.demo

demo-live: ## Run the TUI with real eBPF capture (needs Linux, root, bpftrace; see docs/USER_GUIDE.md)
	$(need_venv)
	@sudo $(PYTHON) -m examples.demo
