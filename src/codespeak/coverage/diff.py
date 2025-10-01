"""Compare baseline and generated coverage artifacts."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .models import CoverageTotals, RepoDiff


def load_coverage_from_json(json_path: Path) -> CoverageTotals:
    """Load coverage totals from a coverage.json file."""
    if not json_path.exists():
        return CoverageTotals(None, None, None)
    try:
        data = json.loads(json_path.read_text())
    except json.JSONDecodeError:
        return CoverageTotals(None, None, None)
    return CoverageTotals.from_dict(data)


def collect_repositories(baseline_dir: Path, generated_dir: Path) -> list[str]:
    """Find all repositories that have coverage data in either baseline or generated."""
    baseline_repos = {p.name for p in baseline_dir.iterdir() if p.is_dir()}
    generated_repos = {p.name for p in generated_dir.iterdir() if p.is_dir()}
    return sorted(baseline_repos | generated_repos)


def load_repo_diff(repo: str, baseline_dir: Path, generated_dir: Path) -> RepoDiff:
    """Load and compare coverage data for a single repository."""
    baseline_path = baseline_dir / repo
    generated_path = generated_dir / repo

    baseline_totals = load_coverage_from_json(baseline_path / "coverage.json")
    generated_totals = load_coverage_from_json(generated_path / "coverage.json")

    status_parts: list[str] = []
    if not baseline_path.exists():
        status_parts.append("missing_baseline")
    if not generated_path.exists():
        status_parts.append("missing_generated")
    if baseline_totals.covered_lines is None:
        status_parts.append("no_baseline_data")
    if generated_totals.covered_lines is None:
        status_parts.append("no_generated_data")
    if not status_parts:
        status_parts.append("ok")

    status = ",".join(status_parts)
    return RepoDiff(repo, baseline_totals, generated_totals, status)


def aggregate(records: list[RepoDiff]) -> dict:
    """Aggregate coverage statistics across all repositories."""
    total_baseline_lines = 0
    total_generated_lines = 0
    total_statements = 0

    for record in records:
        base = record.baseline
        gen = record.generated
        if base.covered_lines is None or gen.covered_lines is None:
            continue
        if base.num_statements is None or gen.num_statements is None:
            continue
        # Prefer generated statement count if they differ (new tests may uncover more files)
        statements = max(base.num_statements, gen.num_statements)
        total_baseline_lines += base.covered_lines
        total_generated_lines += gen.covered_lines
        total_statements += statements

    percent_baseline = (total_baseline_lines / total_statements) * 100 if total_statements else None
    percent_generated = (
        (total_generated_lines / total_statements) * 100 if total_statements else None
    )
    delta_lines = total_generated_lines - total_baseline_lines if total_statements else None
    delta_percent = (
        percent_generated - percent_baseline
        if percent_baseline is not None and percent_generated is not None
        else None
    )

    return {
        "baseline": {
            "covered_lines": total_baseline_lines if total_statements else None,
            "percent_covered": percent_baseline,
        },
        "generated": {
            "covered_lines": total_generated_lines if total_statements else None,
            "percent_covered": percent_generated,
        },
        "delta": {
            "covered_lines": delta_lines,
            "percent_covered": delta_percent,
        },
        "total_statements": total_statements if total_statements else None,
    }


def format_repo_line(diff: RepoDiff) -> str:
    """Format a single repository's coverage comparison as a string."""
    base = diff.baseline
    gen = diff.generated
    delta_lines = diff.delta_lines()
    delta_percent = diff.delta_percent()

    def fmt_lines(totals: CoverageTotals) -> str:
        if totals.covered_lines is None or totals.num_statements is None:
            return "n/a"
        percent = totals.percent_covered if totals.percent_covered is not None else 0.0
        return f"{totals.covered_lines}/{totals.num_statements} ({percent:.2f}%)"

    def fmt_delta(value: float | None, suffix: str = "") -> str:
        if value is None:
            return "n/a"
        sign = "+" if value >= 0 else ""
        if isinstance(value, float):
            return f"{sign}{value:.2f}{suffix}"
        return f"{sign}{value}{suffix}"

    return (
        f"{diff.name}: baseline {fmt_lines(base)} | "
        f"generated {fmt_lines(gen)} | Δlines {fmt_delta(delta_lines)} | "
        f"Δpct {fmt_delta(delta_percent, '%')} | status={diff.status}"
    )


def compute_diff(
    artifacts_root: Path,
    baseline_dir: Path | None = None,
    generated_dir: Path | None = None,
) -> tuple[list[RepoDiff], dict]:
    """
    Compare baseline and generated coverage across repositories.

    Args:
        artifacts_root: Root directory for artifacts
        baseline_dir: Optional explicit path to baseline directory
        generated_dir: Optional explicit path to generated directory

    Returns:
        Tuple of (list of RepoDiff objects, aggregate summary dict)
    """
    if baseline_dir is None:
        baseline_dir = artifacts_root / "coverage_reports_before"
    if generated_dir is None:
        generated_dir = artifacts_root / "coverage_reports_after"

    if not baseline_dir.exists() or not generated_dir.exists():
        raise FileNotFoundError(
            f"Baseline ({baseline_dir}) or generated ({generated_dir}) directory missing."
        )

    repos = collect_repositories(baseline_dir, generated_dir)
    if not repos:
        raise ValueError("No repositories found under the provided artifact paths.")

    records = [load_repo_diff(repo, baseline_dir, generated_dir) for repo in repos]
    aggregate_summary = aggregate(records)

    return records, aggregate_summary


def save_diff_json(
    output_path: Path,
    baseline_dir: Path,
    generated_dir: Path,
    records: list[RepoDiff],
    aggregate_summary: dict,
) -> None:
    """Save diff results to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "baseline_dir": str(baseline_dir),
        "generated_dir": str(generated_dir),
        "aggregate": aggregate_summary,
        "repositories": [record.as_dict() for record in records],
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
