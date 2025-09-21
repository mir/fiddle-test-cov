## Problems
- Running the test of the real-world repo is a challenge by itself.
  - Usually consists of multiple services
  - Tests have non-stable external dependencies (e.g. google search)
- SWT-bench has its one problems
  - If the test failed before the patch and passed after the patch it doesn't mean that it serve a business purpose. Agents will cheat.
- Testing cost is considerably high
  - Agents tend to spend a lot of tokens. 
- Testing is slow
  - Spinning up a docker container with all the deps
  - Checking coverage
  - Running the agent
  - Checking coverage afterwads
- Id doesn't always use the folder I asked to for generating reports and tests, sometimes it saves it to /tmp/<repo-name>/docs/ or some other places. As a result sometimes it doesn't show up the results.
- SWT-bench is pretty old and probably already part of a training datasets for all the LLMs ang agents

## What can we do about it
Create two sets of evals - fast and slow. 
- Slow one should be used to identify a new challenge.
- Fast one can be used to experiment with different approaches and quickly develop a solution.

### Golden set
- Hand-pick a limited hihg-quality recently updated repos
  - Run full-on docker tests once a week
  - Actively use caching
  - Run tests in parallel

### Fast iterations
- Use SWT-bench for faster interations
  - Extract code snippets with limited dependensies before and after the issue resolution
  - Ask LLM to create a test for a specific code snippet
  - Use fast LLM to judge if the newly created/modified tests does the job