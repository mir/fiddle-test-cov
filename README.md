# CodeSpeak-cover: AI-Powered Test Generation System

A comprehensive solution for automated test generation and maintenance, designed to help developers focus on product innovation while ensuring robust test coverage.

## Overview

CodeSpeak-cover is a coverage-driven test generation system that automatically creates and maintains tests for Python applications. The system analyzes codebases, identifies test coverage gaps, and generates appropriate test cases using AI-powered techniques. This project represents a modern approach to software testing that combines conventional testing methodologies with cutting-edge AI capabilities.

## Key Features

- **Automated Test Generation**: Generates unit tests, integration tests, and API tests automatically
- **Coverage Analysis**: Comprehensive analysis of test coverage with detailed reporting
- **Self-Healing Tests**: Tests that adapt to code changes and maintain relevance
- **Multi-Repository Support**: Can analyze and test multiple GitHub repositories
- **AI-Powered Intelligence**: Leverages large language models for intelligent test creation
- **CI/CD Integration**: Seamlessly integrates with existing development workflows

## Project Structure

```
codespeak/
├── main.py                 # Not used
├── pyproject.toml          # Python project configuration
├── Makefile               # Main entry point
├── README.md              # This file
├── docs/                  # Documentation and research
│   ├── 1_assignment.md    # Project assignment and requirements
│   ├── 2_think.md         # Thought process and planning
│   └── 3_research/        # Research on testing methodologies
│       ├── gemini_deep_research.md
│       ├── gpt5_deep_research.md
│       └── grok_deep_research.md
├── evals/                 # Evaluation framework
│   └── github_repos.yaml  # Target repositories for testing
└── prompts/               # AI agent prompts
    ├── v0.md             # Basic test generation prompt
    ├── v1.md             # Advanced test maintenance prompt
    └── v2.md             # Comprehensive testing workflow prompt
```

## Quick Start

### Prerequisites

- Python 3.13+
- uv (recommended for running Python commands and managing dependencies)
- Git
- Make
- openai codex cli
  - https://developers.openai.com/codex/cli/

## Makefile Targets

The project includes several Makefile targets for automation:

### `make repos`
Clones target repositories specified in `evals/github_repos.yaml` into the `evals/github/` directory.

### `make run`
Executes the test generation process on all cloned repositories:
- Resets each repository to HEAD
- Cleans untracked files
- Runs the codex exec command with the latest prompt
- Processes repositories sequentially

### `make collect`
Collects documentation and results from processed repositories:
- Creates timestamped artifacts in `run_artifacts/`
- Copies documentation from each repository's `docs/` folder
- Organizes results by repository name

## Research and Methodology

This project is built on extensive research into automated testing methodologies:

### Conventional Approaches
- **Search-based Testing**: Uses genetic algorithms and evolutionary techniques
- **Symbolic Execution**: Analyzes code paths to generate comprehensive test cases
- **Property-based Testing**: Generates tests from behavioral properties
- **Model-based Testing**: Derives tests from formal specifications

### AI-Powered Solutions
- **LLM Integration**: Leverages large language models for intelligent test generation
- **Self-Healing Tests**: Automatically adapts tests to code changes
- **Natural Language Processing**: Generates tests from plain English requirements
- **Predictive Analysis**: Identifies high-risk areas needing additional coverage

### Key Research Findings
- AI can reduce test maintenance effort by up to 85%
- Combined approaches (conventional + AI) yield the best results
- Focus on developer experience and test readability is crucial
- Integration with existing workflows is essential for adoption

## Target Use Case

The system is designed for:
- **Python Applications**: Primary focus on Python backend services
- **API Testing**: Comprehensive REST API and integration testing
- **Unit Testing**: Automated unit test generation with high coverage
- **Regression Testing**: Maintains test suites as code evolves

## Architecture

### Core Components

1. **Test Analyzer**: Analyzes existing test coverage and identifies gaps
2. **Test Generator**: Creates new test cases using AI and conventional methods
3. **Test Executor**: Runs generated tests and validates results
4. **Report Generator**: Creates detailed coverage and quality reports
5. **Self-Healing Engine**: Adapts tests to code changes automatically

### Workflow

1. **Research Phase**: Analyze repository structure and current test state
2. **Planning Phase**: Identify coverage gaps and prioritize improvements
3. **Generation Phase**: Create missing tests using AI-powered techniques
4. **Validation Phase**: Run tests and verify coverage improvements
5. **Maintenance Phase**: Monitor and adapt tests as code evolves

## Configuration

### Repository Configuration
Add target repositories to `evals/github_repos.yaml`:

```yaml
- https://github.com/owner/repo1
- https://github.com/owner/repo2
```

### Prompt Selection
The system uses the latest prompt version from `prompts/v*.md` automatically. Customize prompts for specific use cases by modifying these files.

## Output and Reports

The system generates several types of documentation:

- **Coverage Reports**: Detailed analysis of test coverage metrics
- **Test Plans**: Generated user stories and test scenarios
- **Architecture Documentation**: Data flow and component analysis
- **Quality Assessments**: Evaluation of generated test effectiveness

All outputs are stored in the `docs/` directory with timestamped artifacts in `run_artifacts/`.

## Future Development

### Planned Features
- Support for additional programming languages
- Advanced AI models for more intelligent test generation
- Integration with popular CI/CD platforms
- Real-time test maintenance and adaptation
- Performance testing automation

### Research Directions
- Improved oracle generation for test validation
- Better handling of complex business logic
- Enhanced integration with development workflows
- Advanced metrics for test quality assessment

## Contributing

This project is part of a test assignment exploring automated testing solutions. Contributions are welcome in the form of:

- Research into new testing methodologies
- Implementation of additional test generation techniques
- Integration with new AI models and frameworks
- Documentation improvements and examples

## License

[Add appropriate license information]

## Contact

[Add contact information or issue tracking details]

---

*This project represents an exploration of the future of automated software testing, combining traditional methodologies with cutting-edge AI capabilities to create more efficient and reliable testing workflows.*

## Auto-Update with AI

You can use AI agents like OpenCode, Codex CLI, or Claude Code to automatically update this README. Use the following prompt:

```prompt
Analyze the current project structure, code, and documentation to update the README.md file. Ensure all information is current and accurate
```