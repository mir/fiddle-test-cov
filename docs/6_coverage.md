# Coverage Instrumentation

A repeatable coverage signal is the backbone of our evaluation loop. Once Codex generates new tests for a repository, we need to quantify how much additional code the suite exercises—especially the lines touched by the SWT-Bench golden patch discussed in `docs/5_bench.md`. This document lays out the coverage strategy that complements the prototype in `docs/4_prototype.md` and prepares the ground for automating the metric inside the Makefile workflow.

## Goals
- Capture a reliable baseline of line coverage before the agent writes any new tests.
- Measure the coverage delta introduced by AI-generated tests, both globally and on files modified by the golden patch.
- Persist coverage artifacts so we can audit runs, compare prompts, and feed downstream analytics.

## Tooling
- **coverage.py** (invoked through `uv run python -m coverage ...`) gives us deterministic line-by-line execution counts without polluting virtual environments.
- **pytest** remains the primary test runner; we assume each target repository either uses pytest already or supplies a command that can be mapped to `pytest` via tox or a helper script.
- **uv** handles dependency hydration (`uv sync`) and avoids cross-repo virtualenv conflicts when we orchestrate many repositories in succession.

## Workflow integration
1. **Hydrate dependencies**: run `uv sync` inside every repository before collecting coverage so that the Python environment is identical across baseline and post-agent runs.
2. **Baseline pass**: execute `uv run python -m coverage run -m pytest` prior to invoking the agent. Store the resulting `.coverage` file alongside a `coverage.json`/`coverage.xml` export for human inspection.
3. **Agent augmentation**: allow `make run` to modify or add tests via Codex. When the agent finishes, rerun the same coverage command. Use `coverage combine` if the agent introduces parametrized runs or multiple invocations.
4. **Reporting**: produce HTML (`coverage html`) and textual summaries (`coverage report`) that highlight per-file deltas, with special attention to files touched by the SWT-Bench golden patch. Export these into `run_artifacts/<timestamp>/<repo>/coverage/`.
5. **Diffing**: compare baseline vs augmented coverage data to compute the delta-change metric described in `docs/5_bench.md`. Persist the comparison in a machine-readable format (CSV or JSON) for later aggregation.

## Makefile hooks (planned)
- `make coverage-baseline`: iterate over `evals/github/*` and run the baseline command above, emitting artifacts under `run_artifacts/<timestamp>/baseline/`.
- `make coverage-generated`: assume the agent has already updated tests, rerun coverage, and place artifacts under `run_artifacts/<timestamp>/generated/`.
- `make coverage-diff`: load the two artifacts, compute aggregate numbers (overall lines covered, lines covered inside the golden patch, and delta percentages), then print a concise summary to stdout.

These targets keep the control flow explicit while remaining composable with `make run`. They also let us re-run coverage analysis without re-triggering the agent whenever we tweak prompts or adjust repository state.

## Outstanding work
- Codify the artifact schema (file names, JSON structure) so downstream tooling can parse coverage deltas without guesswork.
- Extend `make run` to optionally gate on `coverage-diff`, failing the build when coverage regresses or when newly generated tests do not exercise the patch lines.
- Explore branch coverage or mutation testing as a future enhancement once line coverage is automated and stable.
