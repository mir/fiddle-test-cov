LATEST_PROMPT := $(shell ls prompts/v*.md | sort -V | tail -1)
SUBDIRS := $(shell ls evals/github)

run:
	set -x; \
	for dir in $(SUBDIRS); do \
		echo "Processing $$dir"; \
		(cd evals/github/$$dir && \
		git reset --hard HEAD && \
		git clean -fd && \
		cd ../../../ && \
		codex exec --cd . --sandbox workspace-write "$$(cat $(LATEST_PROMPT))"); \
	done

.PHONY: collect

collect:
	set -x; \
	for dir in $(SUBDIRS); do \
		if [ -f evals/github/$$dir/docs/TEST_COVERAGE_SUMMARY.md ]; then \
			echo "Collecting for $$dir"; \
			echo "## $$dir" >> collected_summaries.md; \
			cat evals/github/$$dir/docs/TEST_COVERAGE_SUMMARY.md >> collected_summaries.md; \
			echo "" >> collected_summaries.md; \
		fi \
	done