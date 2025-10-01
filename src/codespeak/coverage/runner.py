"""Coverage collection orchestration for repositories."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from .models import CommandResult, RepoResult
from .utils import (
    copy_artifact,
    format_log_entry,
    iso_timestamp,
    load_coverage_totals,
    remove_artifact,
    run_docker_command,
    should_run,
)


def execute_for_repo(
    repo: str,
    phase: str,
    artifacts_root: Path,
    github_root: Path,
    skip_html: bool,
    docker_image: str,
    docker_cache: Optional[Path],
) -> RepoResult:
    """
    Execute coverage collection for a single repository.

    Args:
        repo: Repository name
        phase: Either "baseline" or "generated"
        artifacts_root: Root directory for artifacts
        github_root: Root directory containing repositories
        skip_html: Skip HTML report generation
        docker_image: Docker image to use for execution
        docker_cache: Optional path to Docker cache directory

    Returns:
        RepoResult with status and coverage information
    """
    repo_path = github_root / repo
    phase_dir = artifacts_root / ("coverage_reports_before" if phase == "baseline" else "coverage_reports_after")
    artifacts_dir = phase_dir / repo
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    commands: list[CommandResult] = []
    artifacts: list[str] = []
    log_lines: list[str] = []

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
    result = run_docker_command(
        docker_image,
        repo_path,
        docker_cache,
        ["pip", "install", "--user", "coverage", "pytest", "pytest-django", "django==3.2.19", "pyjwt", "celery", "python-jose"],
        user_env,
    )
    commands.append(result)
    log_lines.append(format_log_entry(result))

    status = "completed"
    if result.returncode != 0:
        status = "dependency_sync_failed"

    # Step 1b: install project dependencies
    if (repo_path / "requirements.txt").exists():
        req_result = run_docker_command(
            docker_image,
            repo_path,
            docker_cache,
            ["pip", "install", "--user", "-r", "requirements.txt"],
            user_env,
        )
        commands.append(req_result)
        log_lines.append(format_log_entry(req_result))
        if req_result.returncode != 0 and status == "completed":
            status = "dependency_sync_failed"

    # Step 1c: install test dependencies
    if (repo_path / "requirements-tests.txt").exists():
        test_req_result = run_docker_command(
            docker_image,
            repo_path,
            docker_cache,
            ["pip", "install", "--user", "-r", "requirements-tests.txt"],
            user_env,
        )
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

    # Step 2: clear previous coverage data
    erase = run_docker_command(docker_image, repo_path, docker_cache, python_cmd + ["-m", "coverage", "erase"], user_env)
    commands.append(erase)
    log_lines.append(format_log_entry(erase))

    # Step 3: execute pytest under coverage
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

    # Step 4: export coverage data
    json_export = run_docker_command(
        docker_image,
        repo_path,
        docker_cache,
        python_cmd + ["-m", "coverage", "json", "-o", "coverage.json"],
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
        python_cmd + ["-m", "coverage", "xml", "-o", "coverage.xml"],
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

    # Store metadata and logs
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

    # Clean up repository artifacts to keep working tree tidy
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


def execute_coverage_collection(
    phase: str,
    artifacts_root: Path,
    github_root: Path,
    repos: list[str],
    skip_html: bool,
    docker_image: str,
    docker_cache: Optional[Path],
) -> list[RepoResult]:
    """
    Execute coverage collection for multiple repositories.

    Args:
        phase: Either "baseline" or "generated"
        artifacts_root: Root directory for artifacts
        github_root: Root directory containing repositories
        repos: List of repository names to process
        skip_html: Skip HTML report generation
        docker_image: Docker image to use for execution
        docker_cache: Optional path to Docker cache directory

    Returns:
        List of RepoResult objects
    """
    results: list[RepoResult] = []
    for repo in repos:
        print(f"\n[{phase}] {repo}")
        repo_result = execute_for_repo(
            repo=repo,
            phase=phase,
            artifacts_root=artifacts_root,
            github_root=github_root,
            skip_html=skip_html,
            docker_image=docker_image,
            docker_cache=docker_cache,
        )
        results.append(repo_result)

        # Print coverage summary
        totals = repo_result.coverage_totals
        if totals:
            covered = totals.get("covered_lines")
            statements = totals.get("num_statements")
            percent = totals.get("percent_covered")
            coverage_str = (
                f"{covered}/{statements} lines ({percent:.2f}%)"
                if covered is not None and statements is not None and percent is not None
                else "coverage totals unavailable"
            )
        else:
            coverage_str = "coverage totals unavailable"
        print(f"Status: {repo_result.status}")
        print(f"Coverage: {coverage_str}")

    return results


def save_summary(
    phase: str,
    artifacts_root: Path,
    github_root: Path,
    docker_image: str,
    docker_cache: Optional[Path],
    results: list[RepoResult],
) -> Path:
    """
    Save execution summary to JSON file.

    Args:
        phase: Either "baseline" or "generated"
        artifacts_root: Root directory for artifacts
        github_root: Root directory containing repositories
        docker_image: Docker image used for execution
        docker_cache: Optional path to Docker cache directory
        results: List of RepoResult objects

    Returns:
        Path to the saved summary file
    """
    summary = {
        "phase": phase,
        "generated_at": iso_timestamp(time.time()),
        "artifacts_root": str(artifacts_root),
        "github_root": str(github_root),
        "docker_image": docker_image,
        "docker_cache": str(docker_cache) if docker_cache else None,
        "results": [result.as_dict() for result in results],
    }

    phase_dir = artifacts_root / ("coverage_reports_before" if phase == "baseline" else "coverage_reports_after")
    phase_dir.mkdir(parents=True, exist_ok=True)
    summary_path = phase_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))

    return summary_path
