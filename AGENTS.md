# Agent Guidelines for CodeSpeak

## Build/Test Commands
- **Install dependencies**: `uv sync`
- **Run tests**: `uv run python -m pytest` (if pytest configured)
- **Run single test**: `uv run python -m pytest path/to/test_file.py::test_function`
- **Coverage**: `uv run python -m coverage run -m pytest && uv run python -m coverage report`
- **Lint**: No specific linter configured
- **Format**: No specific formatter configured

## Code Style Guidelines
- **Python version**: 3.13+
- **Imports**: Standard library first, then third-party, then local imports
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Types**: Use type hints where beneficial, but keep simple
- **Error handling**: Use try/except with specific exceptions
- **Docstrings**: Use triple quotes for module/class/function docs
- **Line length**: Keep under 100 characters
- **Formatting**: Follow PEP 8 basics, 4-space indentation

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