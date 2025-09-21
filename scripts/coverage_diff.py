#!/usr/bin/env python3
"""Compare baseline and generated coverage artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CoverageTotals:
    covered_lines: Optional[int]
    num_statements: Optional[int]
    percent_covered: Optional[float]

    @classmethod
    def from_json(cls, path: Path) -> "CoverageTotals":
        if not path.exists():
            return cls(None, None, None)
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            return cls(None, None, None)
        totals = data.get("totals") or data.get("summary") or {}
        covered = totals.get("covered_lines")
        statements = totals.get("num_statements")
        percent = totals.get("percent_covered")
        if percent is None and covered is not None and statements not in (None, 0):
            percent = (covered / statements) * 100
        return cls(covered, statements, percent)

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "covered_lines": self.covered_lines,
            "num_statements": self.num_statements,
            "percent_covered": self.percent_covered,
        }


@dataclass
class RepoDiff:
    name: str
    baseline: CoverageTotals
    generated: CoverageTotals
    status: str

    def delta_lines(self) -> Optional[int]:
        if self.baseline.covered_lines is None or self.generated.covered_lines is None:
            return None
        return self.generated.covered_lines - self.baseline.covered_lines

    def delta_percent(self) -> Optional[float]:
        if self.baseline.percent_covered is None or self.generated.percent_covered is None:
            return None
        return self.generated.percent_covered - self.baseline.percent_covered

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "baseline": self.baseline.as_dict(),
            "generated": self.generated.as_dict(),
            "status": self.status,
            "delta_lines": self.delta_lines(),
            "delta_percent": self.delta_percent(),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diff baseline vs generated coverage artifacts.")
    parser.add_argument(
        "--artifacts-root",
        default="run_artifacts",
        help="Root directory for stored artifacts.",
    )
    parser.add_argument(
        "--baseline-path",
        help="Explicit path to the baseline artifacts directory.",
    )
    parser.add_argument(
        "--generated-path",
        help="Explicit path to the generated artifacts directory.",
    )
    parser.add_argument(
        "--output",
        help="Optional file to write JSON summary to.",
    )
    return parser.parse_args()


def resolve_directories(args: argparse.Namespace) -> tuple[Path, Path]:
    artifacts_root = Path(args.artifacts_root)

    if args.baseline_path and args.generated_path:
        return Path(args.baseline_path), Path(args.generated_path)

    # Use static folder structure
    baseline_dir = artifacts_root / "coverage_reports_before"
    generated_dir = artifacts_root / "coverage_reports_after"
    return baseline_dir, generated_dir


def collect_repositories(baseline_dir: Path, generated_dir: Path) -> List[str]:
    baseline_repos = {p.name for p in baseline_dir.iterdir() if p.is_dir()}
    generated_repos = {p.name for p in generated_dir.iterdir() if p.is_dir()}
    return sorted(baseline_repos | generated_repos)


def load_repo_diff(repo: str, baseline_dir: Path, generated_dir: Path) -> RepoDiff:
    baseline_path = baseline_dir / repo
    generated_path = generated_dir / repo

    baseline_totals = CoverageTotals.from_json(baseline_path / "coverage.json")
    generated_totals = CoverageTotals.from_json(generated_path / "coverage.json")

    status_parts: List[str] = []
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


def aggregate(records: List[RepoDiff]) -> dict:
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
        # Prefer generated statement count if they differ (new tests may uncover more files).
        statements = max(base.num_statements, gen.num_statements)
        total_baseline_lines += base.covered_lines
        total_generated_lines += gen.covered_lines
        total_statements += statements

    percent_baseline = (
        (total_baseline_lines / total_statements) * 100 if total_statements else None
    )
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
    base = diff.baseline
    gen = diff.generated
    delta_lines = diff.delta_lines()
    delta_percent = diff.delta_percent()

    def fmt_lines(totals: CoverageTotals) -> str:
        if totals.covered_lines is None or totals.num_statements is None:
            return "n/a"
        percent = totals.percent_covered if totals.percent_covered is not None else 0.0
        return f"{totals.covered_lines}/{totals.num_statements} ({percent:.2f}%)"

    def fmt_delta(value: Optional[float], suffix: str = "") -> str:
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


def main() -> int:
    args = parse_args()
    baseline_dir, generated_dir = resolve_directories(args)

    if not baseline_dir.exists() or not generated_dir.exists():
        print(
            f"Baseline ({baseline_dir}) or generated ({generated_dir}) directory missing.",
            file=sys.stderr,
        )
        return 1

    repos = collect_repositories(baseline_dir, generated_dir)
    if not repos:
        print("No repositories found under the provided artifact paths.", file=sys.stderr)
        return 1

    records = [load_repo_diff(repo, baseline_dir, generated_dir) for repo in repos]
    aggregate_summary = aggregate(records)

    for record in records:
        print(format_repo_line(record))

    print("\nAggregate:")
    agg_base = aggregate_summary["baseline"]
    agg_gen = aggregate_summary["generated"]
    agg_delta = aggregate_summary["delta"]
    print(
        f"Baseline covered: {agg_base['covered_lines']} ({agg_base['percent_covered']})"
    )
    print(
        f"Generated covered: {agg_gen['covered_lines']} ({agg_gen['percent_covered']})"
    )
    print(
        f"Delta lines: {agg_delta['covered_lines']} | Delta pct: {agg_delta['percent_covered']}"
    )

    output_path: Optional[Path]
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = None

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "baseline_dir": str(baseline_dir),
            "generated_dir": str(generated_dir),
            "aggregate": aggregate_summary,
            "repositories": [record.as_dict() for record in records],
        }
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
        print(f"\nJSON summary written to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
