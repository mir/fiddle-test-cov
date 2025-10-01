# CodeSpeak

Coverage-driven automation for generating and evaluating tests across target repositories.

## Docs
See the docs/ folder for the cthought process and results.

## Setup
- Requirements: Python 3.13+, uv, Git, Make, OpenAI Codex CLI
- Install dependencies: `uv sync`

## Core Commands
- `uv run python -m codespeak download_repos` – clone repositories listed in `evals/github_repos.yaml` into `evals/github/`
- `uv run python -m codespeak generate` – apply the latest prompt from `prompts/` to each cloned repo via `codex exec`
- `uv run python -m codespeak collect_artifacts` – copy generated docs into `run_artifacts/agent_reports/`
- `uv run python -m codespeak coverage baseline` – gather pre-generation coverage metrics
- `uv run python -m codespeak coverage generated` – gather post-generation coverage metrics
- `uv run python -m codespeak coverage diff` – compare baseline vs generated coverage reports

## Repository Guide
- `codespeak/` – main package containing CLI and coverage modules
  - `cli.py` – modern CLI tool for all automation tasks
  - `coverage/` – coverage collection and analysis modules
- `pyproject.toml` – Python package metadata (requires Python ≥3.13, depends on `coverage`, `click`, `rich`)
- `docs/` – research and process notes (`1_assignment.md` … `8_wrap_up.md`, `3_research/`, `swt-bench-paper.*`)
- `prompts/` – Codex CLI prompt iterations (`v0.md`, `v1.md`, `v2.md`)
- `evals/` – evaluation assets (`github_repos*.yaml`, `bench/`, `github/` clones)
- `run_artifacts/` – collected run outputs (`agent_reports/`, `coverage_reports_before/`, `coverage_reports_after/`)
- `AGENTS.md` – operating guidelines for agents working on this project
