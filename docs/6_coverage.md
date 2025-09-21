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
- **Dockerized environment**: every coverage command runs in a container (default image `python:3.11-bullseye`) so dependency installs remain isolated and reproducible across repositories.

## Workflow integration
1. **Hydrate dependencies**: run `uv sync` inside every repository before collecting coverage so that the Python environment is identical across baseline and post-agent runs.
2. **Baseline pass**: execute `uv run python -m coverage run -m pytest` prior to invoking the agent. Store the resulting `.coverage` file alongside a `coverage.json`/`coverage.xml` export for human inspection.
3. **Agent augmentation**: allow `make run` to modify or add tests via Codex. When the agent finishes, rerun the same coverage command. Use `coverage combine` if the agent introduces parametrized runs or multiple invocations.
4. **Reporting**: produce HTML (`coverage html`) and textual summaries (`coverage report`) that highlight per-file deltas, with special attention to files touched by the SWT-Bench golden patch. Export these into `run_artifacts/<timestamp>/<phase>/<repo>/`.
5. **Diffing**: compare baseline vs augmented coverage data with `scripts/coverage_diff.py` to compute the delta-change metric described in `docs/5_bench.md`. Persist the comparison as `coverage_diff.json` (and future derivatives) for later aggregation.

All of the steps above are orchestrated by `scripts/run_coverage.py`, which mounts each repository into a Docker container before running `uv` and `coverage` so dependency installs never leak onto the host machine.

## Makefile hooks
- `make coverage-baseline TIMESTAMP=<bucket>` runs `scripts/run_coverage.py baseline ...` for each repo and writes artifacts under `run_artifacts/<bucket>/baseline/` (including per-repo logs, `summary.json`, and coverage exports).
- `make coverage-generated` automatically reuses the most recent baseline bucket when `TIMESTAMP` is not provided, producing artifacts in `run_artifacts/<bucket>/generated/`. Override the bucket with `TIMESTAMP=<bucket>` when you need to target a specific run.
- `make coverage-diff` also defaults to the latest baseline bucket and requires matching generated artifacts. Set `TIMESTAMP=<bucket>` explicitly to diff older runs.

Override `TIMESTAMP` when invoking the targets to reuse the same bucket across baseline, generated, and diff phases. With no override, `make` computes a fresh UTC timestamp on each invocation. Set `DOCKER_IMAGE` to point at a different container (for example, a custom image with extra system dependencies) and optionally provide `DOCKER_CACHE` when you want to reuse a mounted `uv` cache inside the workspace. The targets remain composable with `make run`, letting us iterate on coverage without re-triggering the agent when only prompts or analysis code change.

## Outstanding work
- Codify the artifact schema (file names, JSON structure) so downstream tooling can parse coverage deltas without guesswork.
- Extend `make run` to optionally gate on `coverage-diff`, failing the build when coverage regresses or when newly generated tests do not exercise the patch lines.
- Explore branch coverage or mutation testing as a future enhancement once line coverage is automated and stable.
