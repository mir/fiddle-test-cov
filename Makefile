LATEST_PROMPT := $(shell ls prompts/v*.md | sort -V | tail -1)
LATEST_PROMPT_PATH := $(abspath $(LATEST_PROMPT))
SUBDIRS := $(shell [ -d evals/github ] && ls -1 evals/github)
ARTIFACTS_ROOT ?= run_artifacts
DOCKER_IMAGE ?= python:3.11-bullseye
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
		cd - && \
		codex exec --cd evals/github/$$dir --sandbox workspace-write "$$(cat '$(LATEST_PROMPT_PATH)')"); \
	done
	echo "Run completed. Run make collect to gather summaries."

.PHONY: collect

collect:
	set -x; \
	mkdir -p $(ARTIFACTS_ROOT)/agent_reports; \
	for dir in $(SUBDIRS); do \
		if [ -d evals/github/$$dir/docs ]; then \
			echo "Collecting for $$dir"; \
			rm -rf $(ARTIFACTS_ROOT)/agent_reports/$$dir; \
			mkdir -p $(ARTIFACTS_ROOT)/agent_reports/$$dir; \
			cp -r evals/github/$$dir/docs/* $(ARTIFACTS_ROOT)/agent_reports/$$dir/; \
		fi \
	done
	echo "Collected docs are in $(ARTIFACTS_ROOT)/agent_reports/"

.PHONY: coverage-baseline

coverage-baseline:
	@if [ ! -d evals/github ]; then \
		echo "No repositories found under evals/github. Run 'make repos' first."; \
		exit 1; \
	fi
	@echo "Collecting baseline coverage"
	@mkdir -p $(ARTIFACTS_ROOT)/coverage_reports_before
	@rm -rf $(ARTIFACTS_ROOT)/coverage_reports_before/*
	uv run python scripts/run_coverage.py baseline --artifacts-root $(ARTIFACTS_ROOT) --docker-image python:3.11-bullseye $(if $(strip $(DOCKER_CACHE)),--docker-cache $(DOCKER_CACHE),)

.PHONY: coverage-generated

coverage-generated:
	@if [ ! -d $(ARTIFACTS_ROOT)/coverage_reports_before ]; then \
		echo "No baseline coverage artifacts found under $(ARTIFACTS_ROOT)/coverage_reports_before. Run 'make coverage-baseline' first."; \
		exit 1; \
	fi
	@echo "Collecting generated coverage"
	@mkdir -p $(ARTIFACTS_ROOT)/coverage_reports_after
	@rm -rf $(ARTIFACTS_ROOT)/coverage_reports_after/*
	uv run python scripts/run_coverage.py generated --artifacts-root $(ARTIFACTS_ROOT) --docker-image $(DOCKER_IMAGE) $(if $(strip $(DOCKER_CACHE)),--docker-cache $(DOCKER_CACHE),)

.PHONY: coverage-diff

coverage-diff:
	@if [ ! -d $(ARTIFACTS_ROOT)/coverage_reports_before ] || [ ! -d $(ARTIFACTS_ROOT)/coverage_reports_after ]; then \
		echo "Baseline or generated artifacts missing under $(ARTIFACTS_ROOT)."; \
		echo "Run 'make coverage-baseline' and 'make coverage-generated' first."; \
		exit 1; \
	fi
	uv run python scripts/coverage_diff.py --artifacts-root $(ARTIFACTS_ROOT)
