# Agent Guidelines for CodeSpeak

## Build/Test Commands
- **Install dependencies**: `uv sync`
- **Run tests**: `uv run python -m pytest` (if pytest configured)
- **Run single test**: `uv run python -m pytest path/to/test_file.py::test_function`
- **Coverage**: `uv run python -m coverage run -m pytest && uv run python -m coverage report`
- **Lint**: No specific linter configured
- **Format**: No specific formatter configured

## Project Structure
- Use `docs/` for documentation and research files
- Use `evals/` for evaluation framework
- Use `prompts/` for AI agent prompts
- Use `run_artifacts/` for generated outputs

## Development Workflow
- Use `make repos` to clone target repositories
- Use `make run` to execute test generation on repositories
- Use `make collect` to gather results
- Commit changes only when explicitly requested