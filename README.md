# CodeSpeak

Coverage-driven automation for generating and evaluating tests across target repositories.

## Docs
See the docs/ folder for the cthought process and results.

## Setup
- Requirements: Python 3.13+, uv, Git, Make, OpenAI Codex CLI
- Install dependencies: `uv sync`

## Core Commands
- `uv run codespeak/main.py repos` – clone repositories listed in `evals/github_repos.yaml` into `evals/github/`
- `uv run codespeak/main.py run` – apply the latest prompt from `prompts/` to each cloned repo via `codex exec`
- `uv run codespeak/main.py collect` – copy generated docs into `run_artifacts/agent_reports/`
- `uv run codespeak/main.py coverage baseline` – gather pre-generation coverage metrics
- `uv run codespeak/main.py coverage generated` – gather post-generation coverage metrics
- `uv run codespeak/main.py coverage diff` – compare baseline vs generated coverage reports

## Repository Guide
- `codespeak/cli.py` – modern CLI tool for all automation tasks
- `pyproject.toml` – Python package metadata (requires Python ≥3.13, depends on `coverage`, `click`, `rich`)
- `docs/` – research and process notes (`1_assignment.md` … `8_wrap_up.md`, `3_research/`, `swt-bench-paper.*`)
- `prompts/` – Codex CLI prompt iterations (`v0.md`, `v1.md`, `v2.md`)
- `evals/` – evaluation assets (`github_repos*.yaml`, `bench/`, `github/` clones)
- `scripts/` – coverage implementation scripts (`run_coverage.py`, `coverage_diff.py`)
- `run_artifacts/` – collected run outputs (`agent_reports/`, `coverage_reports_before/`, `coverage_reports_after/`)
- `AGENTS.md` – operating guidelines for agents working on this project
