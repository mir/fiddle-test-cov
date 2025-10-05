# CodeSpeak

Coverage-driven automation for generating and evaluating tests across target repositories.

## Docs
See the docs/ folder for the thought process and results.

## Installation

Install as a tool from GitHub:

```bash
uv tool install git+ssh://git@github.com/mir/fiddle-test-cov.git
```

## Setup
- Requirements: Python 3.13+, uv, Git, OpenAI Codex CLI
- Install dependencies (for development): `uv sync`

## Usage

### Update Tests in Any Project

After installation, run in any project directory:

```bash
codespeak update-tests
```

This applies AI-powered test generation to improve coverage in your current directory.

### Full Evaluation Workflow (Development)

For development and evaluation, clone this repo and use:

#### Quick Start

```bash
uv run codespeak run-all
```

#### Manual Steps

1. **Download repositories**: `uv run codespeak download-repos`
2. **Collect baseline coverage**: `uv run codespeak coverage baseline`
3. **Generate tests**: `uv run codespeak generate`
4. **Collect artifacts**: `uv run codespeak collect-artifacts`
5. **Collect generated coverage**: `uv run codespeak coverage generated`
6. **Compare coverage**: `uv run codespeak coverage diff`

## Core Commands

### Main Command
- `codespeak update-tests` – apply AI-powered test generation in current directory

### Development Commands
- `codespeak run-all` – run complete evaluation workflow
- `codespeak download-repos` – clone repositories from `evals/github_repos.yaml`
- `codespeak generate` – apply prompts to cloned repos
- `codespeak collect-artifacts` – gather generated reports
- `codespeak coverage baseline` – collect pre-generation coverage
- `codespeak coverage generated` – collect post-generation coverage
- `codespeak coverage diff` – compare coverage reports

## Repository Guide
- `src/codespeak/` – main package containing CLI and coverage modules
  - `cli.py` – modern CLI tool for all automation tasks
  - `coverage/` – coverage collection and analysis modules
  - `prompts/` – Codex CLI prompt iterations (`v0.md`, `v1.md`, `v2.md`)
- `pyproject.toml` – Python package metadata (requires Python ≥3.13, depends on `coverage`, `click`, `rich`)
- `docs/` – research and process notes (`1_assignment.md` … `8_wrap_up.md`, `3_research/`, `swt-bench-paper.*`)
- `evals/` – evaluation assets (`github_repos*.yaml`, `bench/`, `github/` clones)
- `run_artifacts/` – collected run outputs (`agent_reports/`, `coverage_reports_before/`, `coverage_reports_after/`)
- `AGENTS.md` – operating guidelines for agents working on this project
