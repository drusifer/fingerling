.DEFAULT_GOAL := help

# Everything runs through the project virtualenv; `make install` creates it from pyproject.toml.
PYTHON := .venv/bin/python

# First line of any recipe that needs the environment.
define need_venv
	@test -x $(PYTHON) || { echo "No .venv - run 'make install' first"; exit 1; }
endef

.PHONY: help tldr install check test run fingerprint demo demo-live clean distclean via_index chat

help: ## Show available make targets
	@echo ""
	@echo "  Project targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

tldr: ## Show TL;DR summaries from all project files (quick orientation for agents)
	@rg --no-heading "TL;DR:" --glob "*.md" -N | sed 's|^\./||' | sort

$(PYTHON):
	@python3 -m venv .venv

install: $(PYTHON) ## Create .venv and install the project with dev dependencies (from pyproject.toml)
	@$(PYTHON) -m pip install -q -e ".[dev]"
	@echo "Installed into .venv"

check: ## Byte-compile all sources (fast syntax check, no tests run)
	$(need_venv)
	@$(PYTHON) -m compileall -q fingerling examples tests

test: ## Run unit tests (ARGS="tests.test_cli" for one module)
	$(need_venv)
	@$(PYTHON) -m unittest $(if $(ARGS),$(ARGS),discover -s tests)

clean: ## Remove caches and build metadata (keeps .venv)
	@find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +
	@rm -rf fingerling.egg-info

distclean: clean ## Also remove the virtualenv
	@rm -rf .venv

via_index: ## Build the via index required by the via MCP server
	@via index "$(CURDIR)"

run: ## Run the fingerling CLI (ARGS="fingerprint --help")
	$(need_venv)
	@.venv/bin/fingerling $(ARGS)

fingerprint: ## Merge JSONL events into a fingerprint set (ARGS="-p PROFILE -s SET [EVENTS|-]"; ARGS=--help for more)
	$(need_venv)
	@.venv/bin/fingerling fingerprint $(ARGS)

demo: ## Run the interactive vaccination TUI (see docs/USER_GUIDE.md)
	$(need_venv)
	@$(PYTHON) -m examples.demo

demo-live: ## Run the TUI with real eBPF capture (needs Linux, root, bpftrace; see docs/USER_GUIDE.md)
	$(need_venv)
	@sudo $(PYTHON) -m examples.demo

chat: ## Post a message to agents/CHAT.md (MSG="..." PERSONA="Name" CMD="cmd" [TO="Recipient"])
	@python3 agents/tools/chat.py "$(MSG)" $(if $(PERSONA),--persona "$(PERSONA)") $(if $(CMD),--cmd "$(CMD)") $(if $(TO),--to "$(TO)")
