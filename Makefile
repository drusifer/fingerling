.DEFAULT_GOAL := help

.PHONY: help tldr test via_index demo demo-live

help: ## Show available make targets
	@echo ""
	@echo "  Project targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

tldr: ## Show TL;DR summaries from all project files (quick orientation for agents)
	@rg --no-heading "TL;DR:" --glob "*.md" -N | sed 's|^\./||' | sort

test: ## Run unit tests
	@python3 -m unittest discover -s tests

via_index: ## Build the via index required by the via MCP server
	@via index "$(CURDIR)"

demo: ## Run the end-to-end pipeline demo (see docs/USER_GUIDE.md)
	@python3 -m examples.demo

demo-live: ## Run the real eBPF capture + live exploit demo (needs Linux, root, bpftrace; see docs/USER_GUIDE.md)
<<<<<<< HEAD
	@python3 -m examples.demo_live_exploit
=======
	@./agents/tools/mkf.py $(V) $@

demo-interactive: ## Run the interactive step-through demo (with multi-pane tmux support)
	@./agents/tools/mkf.py $(V) $@


# Interception logic:
# If we are the entry point (direct make call), intercept everything.
# If we are included, we only provide targets, unless specified.
ifeq ($(MKF_ACTIVE),)
ifdef _IS_BOB_ENTRY
%:
	@./agents/tools/mkf.py $(V) $@
endif
endif

endif
>>>>>>> ab5e554 (Interactive demo works)
