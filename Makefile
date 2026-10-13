.DEFAULT_GOAL := help

# Everything runs through the project virtualenv, which `make install` builds with uv
# from pyproject.toml + uv.lock. See docs/SDLC.md.
PYTHON := .venv/bin/python
PYTHONS := 3.10 3.11 3.12 3.13
# The published package (docs/SDLC.md section 7).
FP := packages/fingerprint-sampler

# First line of any recipe that needs the environment.
define need_venv
	@test -x $(PYTHON) || { echo "No .venv - run 'make install' first"; exit 1; }
endef

define need_uv
	@command -v uv >/dev/null || { echo "uv is not installed - run 'pipx install uv' (see docs/SDLC.md)"; exit 1; }
endef

.PHONY: help tldr install install-hooks check test test-fingerprint test-fingerling test-all lint format secrets run fingerprint demo demo-live clean distclean via_index chat

help: ## Show available make targets
	@echo ""
	@echo "  Project targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

tldr: ## Show TL;DR summaries from all project files (quick orientation for agents)
	@rg --no-heading "TL;DR:" --glob "*.md" -N | sed 's|^\./||' | sort

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

test-all: ## Run the test suite on every supported Python (3.10-3.13) in throwaway environments
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

format: ## Rewrite files to the project style (ruff format + import sorting)
	$(need_venv)
	@.venv/bin/ruff check --select I --fix .
	@.venv/bin/ruff format .

secrets: ## Scan the git history and working tree for leaked secrets (gitleaks)
	@command -v gitleaks >/dev/null || { echo "gitleaks is not installed - see docs/SDLC.md"; exit 1; }
	@gitleaks detect --source .

clean: ## Remove caches and build metadata (keeps .venv)
	@find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +
	@rm -rf fingerling.egg-info .ruff_cache dist

distclean: clean ## Also remove the virtualenv
	@rm -rf .venv

via_index: ## Build the via index required by the via MCP server
	@via index "$(CURDIR)"

run: ## Run the fingerprint CLI (ARGS="merge --help")
	$(need_venv)
	@.venv/bin/fingerprint $(ARGS)

fingerprint: ## Merge JSONL events into a fingerprint set (ARGS="-p PROFILE -s SET [EVENTS|-]"; ARGS=--help for more)
	$(need_venv)
	@.venv/bin/fingerprint merge $(ARGS)

demo: ## Run the interactive vaccination TUI (see docs/USER_GUIDE.md)
	$(need_venv)
	@$(PYTHON) -m examples.demo

demo-live: ## Run the TUI with real eBPF capture (needs Linux, root, bpftrace; see docs/USER_GUIDE.md)
	$(need_venv)
	@sudo $(PYTHON) -m examples.demo

chat: ## Post a message to agents/CHAT.md (MSG="..." PERSONA="Name" CMD="cmd" [TO="Recipient"])
	@python3 agents/tools/chat.py "$(MSG)" $(if $(PERSONA),--persona "$(PERSONA)") $(if $(CMD),--cmd "$(CMD)") $(if $(TO),--to "$(TO)")
