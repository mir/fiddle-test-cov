## Problems
- Running tests on real-world repositories is challenging in itself.
  - Usually consists of multiple services
  - Tests have unstable external dependencies (e.g., Google search)
- SWT-bench has its own problems
  - If a test failed before the patch and passed after the patch, it doesn't mean it serves a business purpose. Agents will find ways to game the system.
- Testing costs are considerably high
  - Agents tend to consume a lot of tokens
- Testing is slow
  - Spinning up a Docker container with all dependencies
  - Checking test coverage
  - Running the agent
  - Checking coverage afterwards
- The system doesn't always use the folder I specified for generating reports and tests, sometimes saving them to /tmp/<repo-name>/docs/ or other locations. As a result, the results sometimes don't appear where expected.
- SWT-bench is quite old and is probably already part of the training datasets for most LLMs and agents

## What can we do about it
Create two sets of evaluations - fast and slow.
- The slow set should be used to identify new challenges.
- The fast set can be used to experiment with different approaches and quickly develop solutions.

### Golden set
- Hand-pick a limited number of high-quality, recently updated repositories
  - Run full Docker tests once a week
  - Actively use caching
  - Run tests in parallel

### Fast iterations
- Use SWT-bench for faster iterations
  - Extract code snippets with limited dependencies before and after issue resolution
  - Ask an LLM to create a test for a specific code snippet
  - Use a fast LLM to judge whether the newly created or modified tests accomplish the task

## Next steps
- [x] Extract some test cases from SWT-bench in Markdown format
- [ ] Read through 10 of them
- [ ] Decide which ones can be used for further work