"""Data models for coverage operations."""

from __future__ import annotations

from dataclasses import dataclass, field


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
    coverage_totals: dict | None
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

    covered_lines: int | None
    num_statements: int | None
    percent_covered: float | None

    @classmethod
    def from_dict(cls, data: dict | None) -> CoverageTotals:
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

    def as_dict(self) -> dict[str, float | None]:
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

    def delta_lines(self) -> int | None:
        """Calculate change in covered lines."""
        if self.baseline.covered_lines is None or self.generated.covered_lines is None:
            return None
        return self.generated.covered_lines - self.baseline.covered_lines

    def delta_percent(self) -> float | None:
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


@dataclass
class DockerConfig:
    """Docker configuration for a repository."""

    enabled: bool = True
    image: str = "ghcr.io/astral-sh/uv:python3.11-bookworm-slim"
    packages: list[str] = field(default_factory=list)
    pip_packages: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict | None) -> DockerConfig:
        """Create from a dictionary."""
        if not data:
            return cls()
        return cls(
            enabled=data.get("enabled", True),
            image=data.get("image", "ghcr.io/astral-sh/uv:python3.11-bookworm-slim"),
            packages=data.get("packages", []),
            pip_packages=data.get("pip_packages", []),
            env=data.get("env", {}),
        )


@dataclass
class CoverageConfig:
    """Coverage execution configuration for a repository."""

    run_command: str = "uv run python -m coverage run -m pytest"
    export_formats: list[str] = field(default_factory=lambda: ["json", "xml", "html"])

    @classmethod
    def from_dict(cls, data: dict | None) -> CoverageConfig:
        """Create from a dictionary."""
        if not data:
            return cls()
        return cls(
            run_command=data.get("run_command", "uv run python -m coverage run -m pytest"),
            export_formats=data.get("export_formats", ["json", "xml", "html"]),
        )


@dataclass
class RepoConfig:
    """Configuration for a single repository."""

    url: str
    name: str
    docker: DockerConfig = field(default_factory=DockerConfig)
    requirements: list[str] = field(default_factory=list)
    coverage: CoverageConfig = field(default_factory=CoverageConfig)

    @classmethod
    def from_dict(cls, data: dict | str) -> RepoConfig:
        """Create from a dictionary or URL string."""
        # Support legacy format: just a URL string
        if isinstance(data, str):
            url = data.strip()
            name = url.rstrip("/").split("/")[-1].replace(".git", "")
            return cls(
                url=url,
                name=name,
                docker=DockerConfig(),
                requirements=[],
                coverage=CoverageConfig(),
            )

        # New format: dictionary with configuration
        url = data["url"].strip()
        name = url.rstrip("/").split("/")[-1].replace(".git", "")
        return cls(
            url=url,
            name=name,
            docker=DockerConfig.from_dict(data.get("docker")),
            requirements=data.get("requirements", []),
            coverage=CoverageConfig.from_dict(data.get("coverage")),
        )
