PLUGIN_NAME=kubectl-kontext
PLATFORMS=darwin-arm64 linux-arm64

.PHONY: all archives sha release clean remove-index

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

remove-index:
	kubectl krew uninstall kontext
	kubectl krew index remove my-index

clean:
	rm -f $(PLUGIN_NAME)-*.tar.gz