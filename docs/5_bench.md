# SWT-Bench Benchmark

SWT-Bench is the benchmark we use to measure the quality of AI-generated tests, extending the plan laid out in `docs/2_think.md` to build a repeatable quality signal. The dataset transforms each SWE-Bench bug-fix task into a test-generation problem, letting us evaluate whether an agent can derive reproducing tests from a natural-language issue.

## How the benchmark is created
- Start from the SWE-Bench corpus of 15 popular Python repositories that pair each GitHub issue with the pre-fix repository snapshot, the golden code patch that resolves the issue, and the maintainer-authored "golden" tests.
- Convert every code-repair task into a test-generation task by keeping the original repository state and golden patch, but treating the golden tests as the target solution. A generated test is considered correct when it fails on the original snapshot and passes once the golden patch is applied.
- Filter for unresolved GitHub issues so that all instances represent real-world bugs that still required developer action at the time of data collection.
- Preserve the rich repository context from SWE-Bench: 1.9K+ instances spanning large projects (often >1.5K files and >300K LoC), with patches typically touching 1-2 files and modifying ~32 lines, so that generated tests must navigate realistic codebases.

## Where the data lives
- Upstream data and tooling are published at `https://github.com/logic-star-ai/SWT-Bench`, which mirrors the SWE-Bench layout and contains scripts for downloading repository snapshots, golden patches, and reference tests.
- Each benchmark instance bundles: the natural-language issue description, the pre-patch repository snapshot, the golden patch (`X*`), and the maintainer-written reference tests (`T*`).
- When we hydrate the benchmark locally, we store the raw release under `data/swt-bench/` (mirroring the upstream structure) so that evaluation pipelines can mount repositories read-only and materialize working copies per task.

## Evaluation process
- For every task, create two worktrees: `R` (original repository snapshot) and `R + X*` (original snapshot with the golden patch applied).
- Ask the test-generation system to output patch files that add or update tests (in practice, we accept either unified diff or the SWT-Bench fault-tolerant diff format that allows rewriting or inserting complete functions).
- Apply the generated tests to the original repository. If the patch is not well-formed or cannot be applied cleanly, the attempt is marked as inapplicable.
- Execute the augmented test suite on both `R` and `R + X*`. Tests that fail on `R` but pass on `R + X*` are labeled fail-to-pass (`F->P`) and counted as successful reproductions. Any test that still fails after applying `X*` (`X->F`) invalidates the run.
- Collect coverage information (via Python line coverage) while running the suites so we can measure how much of the code modified by `X*` is exercised by the generated tests.

## Metrics we track
- **Success rate (S)**: percentage of benchmark instances where at least one generated test is `F->P` and no test regresses after the golden patch. This is the headline metric for "did the agent reproduce the bug?".
- **Fail-to-any rate (F->X)** and **fail-to-pass rate (F->P)**: diagnostic counts of how often the system at least hits failing behavior and how often it reaches full reproduction, respectively.
- **Pass-to-pass rate (P->P)**: how often the system emits well-formed but irrelevant tests that pass in both states, indicating sanity of generation.
- **Patch well-formedness (W)**: fraction of instances where the generated patch applies cleanly; it upper-bounds the achievable success rate because ill-formed patches cannot be executed.
- **Change coverage (Delta C)**: for each task, compute the share of executable lines touched by the golden patch that receive new coverage when the generated tests run, compared against the baseline coverage from the original and golden test suites. This is derived by comparing per-line execution counts on `R` and `R + X*` with and without the generated tests, focusing only on lines actually executed by any suite.

Together these measurements let us compare test-generation systems, debug their failure modes, and decide whether automatically generated tests are trustworthy enough to gate code changes.
