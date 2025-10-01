# Agent Guidelines for CodeSpeak

## Build/Test Commands
- **Install dependencies**: `uv sync --all-groups`
- **Run tests**: `uv run python -m pytest` (if pytest configured)
- **Run single test**: `uv run python -m pytest path/to/test_file.py::test_function`
- **Coverage**: `uv run python -m coverage run -m pytest && uv run python -m coverage report`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Fix lint issues**: `uv run ruff check --fix .`

## Project Structure
- Main package: `src/codespeak/` contains CLI and coverage modules
- Use `docs/` for documentation and research files
- Use `evals/` for evaluation framework
- Use `prompts/` for AI agent prompts
- Use `run_artifacts/` for generated outputs

## Development Workflow
- Use `uv run codespeak download-repos` to clone target repositories
- Use `uv run codespeak run-all` to execute complete workflow automatically
- Use `uv run codespeak generate` to execute test generation on repositories
- Use `uv run codespeak collect-artifacts` to gather results
- Use `uv run codespeak coverage diff` to compare coverage improvements
- Commit changes only when explicitly requested