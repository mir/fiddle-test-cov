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
		codex exec --cd evals/github/$$dir --sandbox workspace-write "$$(cat $(LATEST_PROMPT))"); \
	done
	echo "Run completed. Run make collect to gather summaries."

.PHONY: collect

collect:
	set -x; \
	TIMESTAMP=$$(date -u +%Y%m%d_%H%M%S); \
	mkdir -p run_artifacts/$$TIMESTAMP; \
	for dir in $(SUBDIRS); do \
		if [ -d evals/github/$$dir/docs ]; then \
			echo "Collecting for $$dir"; \
			mkdir -p run_artifacts/$$TIMESTAMP/$$dir; \
			cp -r evals/github/$$dir/docs/* run_artifacts/$$TIMESTAMP/$$dir/; \
		fi \
	done
	echo "Collected docs are in run_artifacts/$$TIMESTAMP/"

.PHONY: clean

clean:
	set -x; \
	if [ -d run_artifacts ]; then \
		rm -rf run_artifacts/*; \
		echo "Cleaned run_artifacts directory"; \
	else \
		echo "run_artifacts directory does not exist"; \
	fi