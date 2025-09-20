LATEST_PROMPT := $(shell ls prompts/v*.md | sort -V | tail -1)
LATEST_PROMPT_PATH := $(abspath $(LATEST_PROMPT))
SUBDIRS := $(shell [ -d evals/github ] && ls -1 evals/github)
TIMESTAMP ?= $(shell date -u +%Y%m%d_%H%M%S)
ARTIFACTS_ROOT ?= run_artifacts
DOCKER_IMAGE ?= ghcr.io/astral-sh/uv:latest
DOCKER_CACHE ?=

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
		codex exec --cd evals/github/$$dir --sandbox workspace-write "$$(cat '$(LATEST_PROMPT_PATH)')"); \
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
.PHONY: coverage-baseline

coverage-baseline:
	@if [ ! -d evals/github ]; then \
		echo "No repositories found under evals/github. Run 'make repos' first."; \
		exit 1; \
	fi
	@echo "Collecting baseline coverage with timestamp $(TIMESTAMP)"
	uv run python scripts/run_coverage.py baseline --timestamp $(TIMESTAMP) --artifacts-root $(ARTIFACTS_ROOT) --docker-image python:3.11-bullseye $(if $(strip $(DOCKER_CACHE)),--docker-cache $(DOCKER_CACHE),)

.PHONY: coverage-generated

coverage-generated:
	@if [ ! -d $(ARTIFACTS_ROOT)/$(TIMESTAMP)/baseline ]; then \
		echo "Baseline artifacts missing at $(ARTIFACTS_ROOT)/$(TIMESTAMP)/baseline. Set TIMESTAMP=<existing run>."; \
		exit 1; \
	fi
	@echo "Collecting generated coverage with timestamp $(TIMESTAMP)"
	uv run python scripts/run_coverage.py generated --timestamp $(TIMESTAMP) --artifacts-root $(ARTIFACTS_ROOT) --docker-image $(DOCKER_IMAGE) $(if $(strip $(DOCKER_CACHE)),--docker-cache $(DOCKER_CACHE),)

.PHONY: coverage-diff

coverage-diff:
	@if [ ! -d $(ARTIFACTS_ROOT)/$(TIMESTAMP)/baseline ] || [ ! -d $(ARTIFACTS_ROOT)/$(TIMESTAMP)/generated ]; then \
		echo "Baseline or generated artifacts missing under $(ARTIFACTS_ROOT)/$(TIMESTAMP)."; \
		echo "Run 'make coverage-baseline TIMESTAMP=$(TIMESTAMP)' and 'make coverage-generated TIMESTAMP=$(TIMESTAMP)' first."; \
		exit 1; \
	fi
	uv run python scripts/coverage_diff.py --timestamp $(TIMESTAMP) --artifacts-root $(ARTIFACTS_ROOT)
