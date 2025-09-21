# Wrap-Up

## Implementation Summary
- Tracked the full build story—framing through open issues—in `docs/*.md`.
- Makefile loop clones repos from `evals/github_repos.yaml`, resets them, runs the latest prompt, and drops artifacts in `run_artifacts/agent_reports/`.
- Coverage scripts (`run_coverage.py`, `coverage_diff.py`) run pytest in Docker, emit JSON/XML/HTML, log commands, and store before/after data under `run_artifacts/coverage_reports_*`.
- `make run` uses the codex cli agent to increase the coverage.
- Taiga Back dry run produced throttling tests (`evals/github/taiga-back/tests/unit/test_projects_throttling.py`) and pushed coverage to 16,641 lines (+0.16 pp) with metadata beside each report.
- Research notes in `docs/3_research/*.md` map incumbents, open-source options, and signals like TestLoter’s 83.6% coverage.

## Not Implemented
- Refresh SWT-Bench, extend it to newer issues, and add outside reviewers for quality checks.
- Parallelize runs, route coverage deltas back to the agent, and tune prompts without breaking train/test discipline.
- Finish the CLI in `main.py`; it still lacks repo selection, prompting, coverage, and reporting orchestration.
- Harden Makefile jobs with fixtures, retries, and fallbacks for missing services.
- Automate prompt iteration, self-eval, and coverage gating beyond the single-pass `make run`.
- Fold `make coverage-diff` into the default flow and aggregate results across all repos.
- Add packaging, telemetry, licensing, githug actions, and other ususal stuff.

## Real-World Fit

### Potential Buyers
- Mid-to-large Python platform teams chasing safer releases.
- QA consultancies offering “coverage-as-a-service.”
- Open-source stewards raising quality without extra burnout.

### Ideal Value Demonstration
- Baseline with `make coverage-baseline`, run `make run`, then compare via `make coverage-generated` and `make coverage-diff`.
- Showcase a generated test tied to a known incident and deliver the bundle in `run_artifacts/agent_reports/<repo>/`.
- Probably up-to-date bench is worth the money by itself.

### Priority Hiring
- Senior infra/devex engineer for orchestration, caching, and CI plumbing.
- Applied testing lead for oracles, mutation checks, and benchmark upkeep.
- Product-minded solutions engineer to translate customer pain and run pilots.

### Surviving the Journey
- Sell white-glove coverage audits powered by this pipeline.
- Partner with QA agencies or platform teams to fund pilots and gather real data.
- Open-source the core while monetizing managed runs, support, or hosted dashboards.

# Summary

I wouldn’t keep pushing this project; the commercial story is too thin. Automated coverage gains feel like second-order operational wins, so prospects keep coming back with the same objections:
- Why bother investing in tests at all?
- Why not just hire inexpensive QA engineers?
- Couldn’t Claude or another LLM already handle this?
- Isn’t there an enterprise tool that does the job?
- Why pay when an open-source option is free?

The most credible angle is a private, always-fresh benchmark that top AI labs—and platform players like Surge, Handshake, or Scale—would pay to access.
