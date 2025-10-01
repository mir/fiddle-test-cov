# Refactoring & Polish

## Changes Made (Oct 1, 2025)

### Code Structure
- Refactored CLI into modular commands under `src/codespeak/commands/`:
  - `download_repos.py` - Repository cloning with sensible defaults
  - `generate.py` - Test generation via codex CLI
  - `collect_artifacts.py` - Artifact collection
  - `coverage.py` - Coverage analysis orchestration
  - `run_all.py` - Complete workflow automation
- Added `coverage/models.py` with proper dataclasses for coverage metrics
- Improved `coverage/runner.py` with better Docker handling and error reporting
- Enhanced `coverage/utils.py` with robust path and file operations

### Coverage System Improvements
- Added `pytest-cov` to dependencies for standardized coverage collection
- Updated Docker image reference in coverage runner
- Implemented structured coverage data models (CoverageStats, CoverageReport)
- Better separation between baseline and generated coverage collection
- Fixed coverage diff logic to handle missing reports gracefully

### Repository Management
- Added `github_repos.yaml.example` with comprehensive examples
- Implemented sensible defaults for repo cloning (depth, branch detection)
- Better error handling for missing/invalid YAML files
- Support for custom branch specifications per repository

### Prompt Optimization
- Updated `prompts/v2.md` for faster execution
- Trade-off: slightly less comprehensive but more practical for testing
- Simplified agent instructions to reduce token consumption

### Code Quality
- Added linting with ruff (pycodestyle, pyflakes, isort, bugbear)
- Applied formatting standards (line length: 100, Python 3.13 target)
- Ran `ruff check --fix` and `ruff format` across codebase
- Created test structure with `tests/test_cli.py`

### Documentation
- Created `AGENTS.md` with development workflows and command reference
- Updated `CLAUDE.md` to reference agent guidelines
- Fixed README typo ("cthought" → "thought")

## Technical Debt Addressed
- Removed Makefile in favor of unified CLI tool
- Consolidated scattered coverage logic into cohesive module
- Eliminated hardcoded paths and magic strings
- Added proper type hints throughout

## Still Missing
- Comprehensive test suite (only basic CLI tests exist)
- Integration tests for full workflow
- CI/CD pipeline configuration
- Telemetry and observability hooks
