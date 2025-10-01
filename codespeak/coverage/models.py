"""Data models for coverage operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    """Result of a shell command execution."""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float

    def as_dict(self) -> dict:
        return {
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class RepoResult:
    """Result of coverage collection for a single repository."""

    name: str
    status: str
    commands: list[CommandResult]
    artifacts: list[str]
    coverage_totals: Optional[dict]
    started_at: str
    finished_at: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "commands": [cmd.as_dict() for cmd in self.commands],
            "artifacts": self.artifacts,
            "coverage_totals": self.coverage_totals,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@dataclass
class CoverageTotals:
    """Coverage statistics for a repository."""

    covered_lines: Optional[int]
    num_statements: Optional[int]
    percent_covered: Optional[float]

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "CoverageTotals":
        """Create from a dictionary (e.g., from coverage.json)."""
        if not data:
            return cls(None, None, None)
        totals = data.get("totals") or data.get("summary") or {}
        covered = totals.get("covered_lines")
        statements = totals.get("num_statements")
        percent = totals.get("percent_covered")
        if percent is None and covered is not None and statements not in (None, 0):
            percent = (covered / statements) * 100
        return cls(covered, statements, percent)

    def as_dict(self) -> dict[str, Optional[float]]:
        return {
            "covered_lines": self.covered_lines,
            "num_statements": self.num_statements,
            "percent_covered": self.percent_covered,
        }


@dataclass
class RepoDiff:
    """Comparison of baseline and generated coverage for a repository."""

    name: str
    baseline: CoverageTotals
    generated: CoverageTotals
    status: str

    def delta_lines(self) -> Optional[int]:
        """Calculate change in covered lines."""
        if self.baseline.covered_lines is None or self.generated.covered_lines is None:
            return None
        return self.generated.covered_lines - self.baseline.covered_lines

    def delta_percent(self) -> Optional[float]:
        """Calculate change in coverage percentage."""
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
