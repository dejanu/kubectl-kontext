PLUGIN_NAME=kubectl-kontext
PLATFORMS=darwin-arm64 linux-arm64

# MCP install layout (Claude Code / Desktop): keep KUBECONFIG stable by pointing at this path and updating the symlink.
MCP_DIR := $(HOME)/.local/bin/kubectl-kontext
ACTIVE_CONFIG := $(MCP_DIR)/active-config

.PHONY: all archives sha release clean remove-index install-mcp go-build go-run compare-go \
	add-mcp-server-claude-code mcp-verify-kubeconfig

all: archives sha

archives:
	@for platform in $(PLATFORMS); do \
	  tar -czf $(PLUGIN_NAME)-$$platform.tar.gz $(PLUGIN_NAME); \
	done

sha:
	@for platform in $(PLATFORMS); do \
	  echo "$$platform:"; \
	  shasum -a 256 $(PLUGIN_NAME)-$$platform.tar.gz | awk '{print $$1}'; \
	done

release: archives sha

go-build:
	@mkdir -p bin
	@go build -o bin/kubectl-kontext ./cmd/kubectl-kontext-go
	@chmod +x bin/kubectl-kontext
	@cp bin/kubectl-kontext $(HOME)/.krew/bin/kubectl-kontext # place bin in krew path to be discoverable by kubectl

install-mcp: go-build
	@mkdir -p $(MCP_DIR)
	@cp bin/kubectl-kontext $(MCP_DIR)/kubectl-kontext
	@cp local_mpc_setup/mcp_server.py $(MCP_DIR)/mcp_server.py
	@chmod +x $(MCP_DIR)/kubectl-kontext
	@if [ ! -e "$(ACTIVE_CONFIG)" ] && [ -f "$(HOME)/.kube/config" ]; then \
		ln -sf "$(HOME)/.kube/config" "$(ACTIVE_CONFIG)"; \
		echo "Created symlink $(ACTIVE_CONFIG) -> $(HOME)/.kube/config"; \
	fi
	@echo "Installed to $(MCP_DIR)/"
	@echo "Claude Desktop: see local_mpc_setup/setup_instructions.md"
	@echo "Kubeconfig pointer for MCP (optional): ln -sf /absolute/path/to/config $(ACTIVE_CONFIG)"

add-mcp-server-claude-code: install-mcp
	@echo "Registering kubectl-kontext MCP for Claude Code (user scope)..."
	-claude mcp remove -s user kubectl-kontext 2>/dev/null || true
	# Server name must come *before* -e; otherwise variadic -e consumes the name as a bogus env var.
	claude mcp add -s user kubectl-kontext -e "KUBECONFIG=$(ACTIVE_CONFIG)" -- uv run "$(MCP_DIR)/mcp_server.py"
	@echo ""
	@echo "KUBECONFIG for this MCP server is fixed to: $(ACTIVE_CONFIG)"
	@echo "Point it at a kubeconfig (use an absolute path for the source file):"
	@echo "  ln -sf /absolute/path/to/kubeconfig $(ACTIVE_CONFIG)"
	@echo "Verify same as MCP: make mcp-verify-kubeconfig"
	@echo "After changing the symlink, restart Claude Code (or reload MCP) — the old server process keeps the old file open until it exits."

# Prints current context using the same kubeconfig path Claude Code passes to the MCP server.
mcp-verify-kubeconfig:
	@echo "active-config path: $(ACTIVE_CONFIG)"
	@ls -la "$(ACTIVE_CONFIG)" 2>/dev/null || echo "missing — create with: ln -sf /path/to/kubeconfig $(ACTIVE_CONFIG)"
	@kubectl --kubeconfig="$(ACTIVE_CONFIG)" config current-context 2>&1 || true

remove-index:
	kubectl krew uninstall kontext
	kubectl krew index remove my-index

clean:
	rm -f $(PLUGIN_NAME)-*.tar.gz
	rm -f bin/kubectl-kontext