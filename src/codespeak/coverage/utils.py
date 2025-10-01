"""Utility functions for coverage operations."""

from __future__ import annotations

import datetime as dt
import json
import shutil
import subprocess
import sys
import time
from collections.abc import Iterable
from pathlib import Path

from .models import CommandResult


def run_command(command: Iterable[str]) -> CommandResult:
    """Execute a shell command and capture its output."""
    command_list = list(command)
    start = time.perf_counter()
    try:
        proc = subprocess.run(  # noqa: S603, S607 - deliberate subprocess call
            command_list,
            capture_output=True,
            text=True,
            check=False,
        )
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except FileNotFoundError as exc:
        returncode = 127
        stdout = ""
        stderr = str(exc)
    duration = time.perf_counter() - start
    return CommandResult(command_list, returncode, stdout, stderr, duration)


def build_docker_command(
    image: str,
    repo_path: Path,
    docker_cache: Path | None,
    inner_command: Iterable[str],
    env: dict | None = None,
) -> list[str]:
    """Build a docker run command with appropriate volume mounts and environment."""
    command: list[str] = ["docker", "run"]
    if sys.stdout.isatty():
        command.append("-t")

    repo_abs = repo_path.resolve()
    command.extend(["-v", f"{repo_abs}:/workspace", "-w", "/workspace"])

    if docker_cache is not None:
        cache_abs = docker_cache.resolve()
        command.extend(["-v", f"{cache_abs}:/root/.cache/uv"])
        env = {**(env or {}), "UV_CACHE_DIR": "/root/.cache/uv"}

    if env:
        for key, value in env.items():
            command.extend(["-e", f"{key}={value}"])

    command.append(image)
    command.extend(inner_command)
    return command


def run_docker_command(
    image: str,
    repo_path: Path,
    docker_cache: Path | None,
    inner_command: Iterable[str],
    env: dict | None = None,
) -> CommandResult:
    """Execute a command inside a Docker container."""
    docker_cmd = build_docker_command(image, repo_path, docker_cache, list(inner_command), env)
    return run_command(docker_cmd)


def iso_timestamp(ts: float) -> str:
    """Convert a Unix timestamp to ISO format with timezone."""
    return dt.datetime.fromtimestamp(ts, dt.UTC).isoformat(timespec="seconds") + "Z"


def format_log_entry(result: CommandResult) -> str:
    """Format a command result as a log entry."""
    lines = [f"$ {' '.join(result.command)}"]
    if result.stdout:
        lines.append(result.stdout.rstrip())
    if result.stderr:
        lines.append(result.stderr.rstrip())
    lines.append(f"[exit {result.returncode} | {result.duration_seconds:.2f}s]")
    return "\n".join(line for line in lines if line)


def discover_repositories(root: Path, explicit: list[str] | None) -> list[str]:
    """Find repositories to process."""
    if explicit:
        return sorted(explicit)
    if not root.exists():
        return []
    return sorted(child.name for child in root.iterdir() if child.is_dir())


def copy_artifact(src: Path, dest: Path) -> bool:
    """Copy a file or directory artifact to the destination."""
    if not src.exists():
        return False
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return True


def remove_artifact(path: Path) -> None:
    """Remove a file or directory artifact."""
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def load_coverage_totals(json_path: Path) -> dict | None:
    """Load coverage totals from a coverage.json file."""
    if not json_path.exists():
        return None
    try:
        data = json.loads(json_path.read_text())
    except json.JSONDecodeError:
        return None
    totals = data.get("totals") or data.get("summary")
    if not totals:
        return None
    covered = totals.get("covered_lines")
    statements = totals.get("num_statements")
    percent = totals.get("percent_covered") or (
        None if covered is None or statements in (None, 0) else (covered / statements) * 100
    )
    return {
        "covered_lines": covered,
        "num_statements": statements,
        "percent_covered": percent,
    }


def should_run(repo_path: Path) -> bool:
    """Check if a repository has Python project markers."""
    markers = ["pyproject.toml", "requirements.txt", "setup.py", "tox.ini"]
    return any((repo_path / marker).exists() for marker in markers)
