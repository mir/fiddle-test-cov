LATEST_PROMPT := $(shell ls prompts/v*.md | sort -V | tail -1)
SUBDIRS := $(shell ls evals/github)

.PHONY: repos

repos:
	set -x; \
	mkdir -p evals/github; \
	for url in $$(cat evals/github_repos.yaml | sed 's/- //'); do \
		repo=$$(basename $$url); \
		if [ ! -d evals/github/$$repo ]; then \
			git clone $$url evals/github/$$repo; \
		fi \
	done
	echo "Repositories are in evals/github/"

.PHONY: run

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
	echo "Run completed. Run make collect to gather summaries."

.PHONY: collect

collect:
	set -x; \
	TIMESTAMP=$$(date -u +%Y%m%d_%H%M%S); \
	mkdir -p run_artifacts/$$TIMESTAMP; \
	for dir in $(SUBDIRS); do \
		if [ -f evals/github/$$dir/docs/TEST_COVERAGE_SUMMARY.md ]; then \
			echo "Collecting for $$dir"; \
			echo "## $$dir" >> run_artifacts/$$TIMESTAMP/collected_summaries.md; \
			cat evals/github/$$dir/docs/TEST_COVERAGE_SUMMARY.md >> run_artifacts/$$TIMESTAMP/collected_summaries.md; \
			echo "" >> run_artifacts/$$TIMESTAMP/collected_summaries.md; \
		fi \
	done
	echo "Collected summaries are in run_artifacts/$$TIMESTAMP/collected_summaries.md"