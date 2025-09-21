#!/usr/bin/env python3
"""Orchestrate coverage collection for repositories under evals/github."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run coverage for repositories and archive artifacts.",
    )
    parser.add_argument(
        "phase",
        choices=["baseline", "generated"],
        help="Which stage of the workflow is being executed.",
    )

    parser.add_argument(
        "--artifacts-root",
        default="run_artifacts",
        help="Directory where coverage artifacts are stored.",
    )
    parser.add_argument(
        "--github-root",
        default="evals/github",
        help="Root directory containing cloned target repositories.",
    )
    parser.add_argument(
        "--repo",
        dest="repos",
        action="append",
        help="Specific repository name(s) under --github-root. If omitted, all subdirectories are used.",
    )
    parser.add_argument(
        "--skip-html",
        action="store_true",
        help="Do not generate coverage HTML reports (useful for faster iterations).",
    )
    parser.add_argument(
        "--docker-image",
        default=os.environ.get("COVERAGE_DOCKER_IMAGE", "ghcr.io/astral-sh/uv:latest"),
        help="Docker image to use for running coverage commands. Use 'local' to run commands on host.",
    )
    parser.add_argument(
        "--docker-cache",
        help="Optional host path to mount as the container's UV cache directory.",
    )
    return parser.parse_args()


@dataclass
class CommandResult:
    command: List[str]
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


def run_command(command: Iterable[str]) -> CommandResult:
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


@dataclass
class RepoResult:
    name: str
    status: str
    commands: List[CommandResult]
    artifacts: List[str]
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


def iso_timestamp(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts, dt.UTC).isoformat(timespec="seconds") + "Z"


def format_log_entry(result: CommandResult) -> str:
    lines = [f"$ {' '.join(result.command)}"]
    if result.stdout:
        lines.append(result.stdout.rstrip())
    if result.stderr:
        lines.append(result.stderr.rstrip())
    lines.append(f"[exit {result.returncode} | {result.duration_seconds:.2f}s]")
    return "\n".join(line for line in lines if line)


def discover_repositories(root: Path, explicit: Optional[List[str]]) -> List[str]:
    if explicit:
        return sorted(explicit)
    if not root.exists():
        return []
    return sorted(child.name for child in root.iterdir() if child.is_dir())


def copy_artifact(src: Path, dest: Path) -> bool:
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
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def load_coverage_totals(json_path: Path) -> Optional[dict]:
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


def build_docker_command(
    image: str,
    repo_path: Path,
    docker_cache: Optional[Path],
    inner_command: Iterable[str],
    env: Optional[dict] = None,
) -> List[str]:
    command: List[str] = ["docker", "run"]
    if sys.stdout.isatty():
        command.append("-t")

    # uid_fn = getattr(os, "getuid", None)
    # gid_fn = getattr(os, "getgid", None)
    # if callable(uid_fn) and callable(gid_fn):
    #     uid = uid_fn()
    #     gid = gid_fn()
    #     command.extend(["--user", f"{uid}:{gid}"])

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
    docker_cache: Optional[Path],
    inner_command: Iterable[str],
    env: Optional[dict] = None,
) -> CommandResult:
    docker_cmd = build_docker_command(image, repo_path, docker_cache, list(inner_command), env)
    return run_command(docker_cmd)


def ensure_timestamp(value: Optional[str]) -> str:
    if value:
        return value
    return dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def should_run(repo_path: Path) -> bool:
    markers = ["pyproject.toml", "requirements.txt", "setup.py", "tox.ini"]
    return any((repo_path / marker).exists() for marker in markers)


def execute_for_repo(
    repo: str,
    phase: str,
    artifacts_root: Path,
    github_root: Path,
    skip_html: bool,
    docker_image: str,
    docker_cache: Optional[Path],
) -> RepoResult:
    repo_path = github_root / repo
    # Use static folder structure instead of timestamp
    phase_dir = artifacts_root / ("coverage_reports_before" if phase == "baseline" else "coverage_reports_after")
    artifacts_dir = phase_dir / repo
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    commands: List[CommandResult] = []
    artifacts: List[str] = []

    log_lines: List[str] = []

    env = {"DJANGO_SETTINGS_MODULE": "tests.config"}
    if docker_cache is None:
        env = {**env, "UV_CACHE_DIR": "/workspace/.uv_cache"}

    if not repo_path.exists():
        finished = time.time()
        log_lines.append(f"Repository {repo} not found at {repo_path}")
        log_lines.append("Skipping coverage collection.")
        (artifacts_dir / "coverage.log").write_text("\n".join(log_lines))
        return RepoResult(
            name=repo,
            status="missing_repository",
            commands=commands,
            artifacts=artifacts,
            coverage_totals=None,
            started_at=iso_timestamp(started),
            finished_at=iso_timestamp(finished),
        )

    if not should_run(repo_path):
        finished = time.time()
        log_lines.append(
            "No standard Python project markers found; skipping coverage instrumentation."
        )
        (artifacts_dir / "coverage.log").write_text("\n".join(log_lines))
        return RepoResult(
            name=repo,
            status="skipped_no_python_project",
            commands=commands,
            artifacts=artifacts,
            coverage_totals=None,
            started_at=iso_timestamp(started),
            finished_at=iso_timestamp(finished),
        )

    # Step 1: install basic testing tools and Django
    user_env = {**(env or {}), "PYTHONUSERBASE": "/workspace/.local"}
    result = run_docker_command(docker_image, repo_path, docker_cache, ["pip", "install", "--user", "coverage", "pytest", "pytest-django", "django==3.2.19", "pyjwt", "celery", "python-jose"], user_env)
    commands.append(result)
    log_lines.append(format_log_entry(result))

    status = "completed"
    if result.returncode != 0:
        status = "dependency_sync_failed"

    # Step 1b: install project dependencies
    if (repo_path / "requirements.txt").exists():
        req_result = run_docker_command(docker_image, repo_path, docker_cache, ["pip", "install", "--user", "-r", "requirements.txt"], user_env)
        commands.append(req_result)
        log_lines.append(format_log_entry(req_result))
        if req_result.returncode != 0 and status == "completed":
            status = "dependency_sync_failed"

    # Step 1c: install test dependencies
    if (repo_path / "requirements-tests.txt").exists():
        test_req_result = run_docker_command(docker_image, repo_path, docker_cache, ["pip", "install", "--user", "-r", "requirements-tests.txt"], user_env)
        commands.append(test_req_result)
        log_lines.append(format_log_entry(test_req_result))
        if test_req_result.returncode != 0 and status == "completed":
            status = "dependency_sync_failed"



    # Determine the python command prefix based on docker image
    if "uv" in docker_image:
        python_cmd = ["run", "python"]
    else:
        python_cmd = ["python"]

    # Set PATH to include user-installed binaries
    user_env = {**(env or {}), "PYTHONUSERBASE": "/workspace/.local", "PATH": "/workspace/.local/bin:/usr/local/bin:/usr/bin:/bin"}

    # Step 2: clear previous coverage data.
    erase = run_docker_command(docker_image, repo_path, docker_cache, python_cmd + ["-m", "coverage", "erase"], user_env)
    commands.append(erase)
    log_lines.append(format_log_entry(erase))

    # Step 3: execute pytest under coverage.
    coverage_run = run_docker_command(
        docker_image,
        repo_path,
        docker_cache,
        python_cmd + ["-m", "coverage", "run", "-m", "pytest"],
        user_env,
    )
    commands.append(coverage_run)
    log_lines.append(format_log_entry(coverage_run))

    if coverage_run.returncode != 0 and status == "completed":
        status = "tests_failed"

    # Step 4: export coverage data.
    json_export = run_docker_command(
        docker_image,
        repo_path,
        docker_cache,
        python_cmd + [
            "-m",
            "coverage",
            "json",
            "-o",
            "coverage.json",
        ],
        user_env,
    )
    commands.append(json_export)
    log_lines.append(format_log_entry(json_export))

    if json_export.returncode != 0 and status == "completed":
        status = "export_failed"

    xml_export = run_docker_command(
        docker_image,
        repo_path,
        docker_cache,
        python_cmd + [
            "-m",
            "coverage",
            "xml",
            "-o",
            "coverage.xml",
        ],
        user_env,
    )
    commands.append(xml_export)
    log_lines.append(format_log_entry(xml_export))

    if xml_export.returncode != 0 and status == "completed":
        status = "export_failed"

    html_export: Optional[CommandResult] = None
    if not skip_html:
        html_export = run_docker_command(
            docker_image,
            repo_path,
            docker_cache,
            python_cmd + ["-m", "coverage", "html"],
            user_env,
        )
        commands.append(html_export)
        log_lines.append(format_log_entry(html_export))
        if html_export.returncode != 0 and status == "completed":
            status = "export_failed"

    coverage_files = {
        ".coverage": artifacts_dir / ".coverage",
        "coverage.json": artifacts_dir / "coverage.json",
        "coverage.xml": artifacts_dir / "coverage.xml",
    }

    for filename, destination in coverage_files.items():
        if copy_artifact(repo_path / filename, destination):
            artifacts.append(destination.name)

    if not skip_html:
        htmlcov_src = repo_path / "htmlcov"
        htmlcov_dest = artifacts_dir / "htmlcov"
        if copy_artifact(htmlcov_src, htmlcov_dest):
            artifacts.append("htmlcov/")

    # Store metadata and logs.
    coverage_json_path = artifacts_dir / "coverage.json"
    coverage_totals = load_coverage_totals(coverage_json_path)

    log_path = artifacts_dir / "coverage.log"
    log_content = "\n\n".join(log_lines)
    log_path.write_text(log_content)
    artifacts.append(log_path.name)

    metadata_path = artifacts_dir / "metadata.json"
    metadata = {
        "phase": phase,
        "repository": repo,
        "status": status,
        "commands": [cmd.as_dict() for cmd in commands],
        "artifacts": artifacts,
        "coverage_totals": coverage_totals,
        "docker_image": docker_image,
        "docker_cache": str(docker_cache) if docker_cache else None,
        "started_at": iso_timestamp(started),
        "finished_at": iso_timestamp(time.time()),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))
    if metadata_path.name not in artifacts:
        artifacts.append(metadata_path.name)

    # Clean up repository artifacts to keep working tree tidy.
    for filename in coverage_files:
        remove_artifact(repo_path / filename)
    if not skip_html:
        remove_artifact(repo_path / "htmlcov")

    finished = time.time()

    return RepoResult(
        name=repo,
        status=status,
        commands=commands,
        artifacts=artifacts,
        coverage_totals=coverage_totals,
        started_at=iso_timestamp(started),
        finished_at=iso_timestamp(finished),
    )


def main() -> int:
    args = parse_args()
    artifacts_root = Path(args.artifacts_root)
    github_root = Path(args.github_root)
    docker_image = args.docker_image
    docker_cache = None
    if args.docker_cache:
        docker_cache_path = Path(args.docker_cache)
        if not docker_cache_path.is_absolute():
            docker_cache_path = (Path.cwd() / docker_cache_path).resolve()
        docker_cache = docker_cache_path

    repos = discover_repositories(github_root, args.repos)
    if not repos:
        print("No repositories to process. Did you run `make repos`?", file=sys.stderr)
        return 1

    print(
        textwrap.dedent(
            f"""
            Running coverage phase '{args.phase}' for {len(repos)} repos.
            Artifacts root: {artifacts_root}
            GitHub root: {github_root}
            """
        ).strip()
    )

    results: List[RepoResult] = []
    for repo in repos:
        print(f"\n[{args.phase}] {repo}")
        repo_result = execute_for_repo(
            repo=repo,
            phase=args.phase,
            artifacts_root=artifacts_root,
            github_root=github_root,
            skip_html=args.skip_html,
            docker_image=docker_image,
            docker_cache=docker_cache,
        )
        results.append(repo_result)
        totals = repo_result.coverage_totals
        if totals:
            covered = totals.get("covered_lines")
            statements = totals.get("num_statements")
            percent = totals.get("percent_covered")
            coverage_str = (
                "{covered}/{statements} lines ({percent:.2f}%)".format(
                    covered=covered or 0,
                    statements=statements or 0,
                    percent=percent or 0.0,
                )
                if covered is not None and statements is not None and percent is not None
                else "coverage totals unavailable"
            )
        else:
            coverage_str = "coverage totals unavailable"
        print(f"Status: {repo_result.status}")
        print(f"Coverage: {coverage_str}")

    summary = {
        "phase": args.phase,
        "generated_at": iso_timestamp(time.time()),
        "artifacts_root": str(artifacts_root),
        "github_root": str(github_root),
        "docker_image": docker_image,
        "docker_cache": str(docker_cache) if docker_cache else None,
        "results": [result.as_dict() for result in results],
    }

    # Use static folder structure instead of timestamp
    phase_dir = artifacts_root / ("coverage_reports_before" if args.phase == "baseline" else "coverage_reports_after")
    phase_dir.mkdir(parents=True, exist_ok=True)
    summary_path = phase_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))

    print(f"\nSummary written to {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
