#!/usr/bin/env python3
"""Modern CLI for managing code evaluation workflows."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CodeSpeak - Modern CLI for code evaluation workflows.

    Manage repositories, run evaluations, and track code coverage.
    """
    pass


@cli.command()
@click.option(
    "--github-root",
    default="evals/github",
    help="Directory to clone repositories into",
    show_default=True,
)
@click.option(
    "--repos-file",
    default="evals/github_repos.yaml",
    help="YAML file containing repository URLs",
    show_default=True,
)
def repos(github_root: str, repos_file: str):
    """Clone GitHub repositories from YAML file.

    Reads repository URLs from the YAML file and clones them into
    the specified directory. Skips repositories that already exist.
    """
    repos_path = Path(repos_file)
    github_path = Path(github_root)

    if not repos_path.exists():
        console.print(f"[red]Error:[/red] Repository file not found: {repos_file}")
        sys.exit(1)

    # Load repository URLs
    with open(repos_path) as f:
        repo_urls = yaml.safe_load(f)

    if not repo_urls:
        console.print("[yellow]Warning:[/yellow] No repositories found in YAML file")
        return

    # Create github root directory
    github_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold blue]Cloning {len(repo_urls)} repositories...[/bold blue]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for url in repo_urls:
            url = url.strip()
            if not url:
                continue

            repo_name = Path(url).name.replace(".git", "")
            repo_dir = github_path / repo_name

            if repo_dir.exists():
                progress.console.print(f"  ✓ [dim]{repo_name}[/dim] (already exists)")
                continue

            task = progress.add_task(f"Cloning {repo_name}...", total=None)

            try:
                subprocess.run(
                    ["git", "clone", url, str(repo_dir)],
                    capture_output=True,
                    check=True,
                )
                progress.console.print(f"  ✓ [green]{repo_name}[/green]")
            except subprocess.CalledProcessError as e:
                progress.console.print(f"  ✗ [red]{repo_name}[/red] - {e.stderr.decode()}")
            finally:
                progress.remove_task(task)

    console.print(f"\n[bold green]✓[/bold green] Repositories are in {github_root}/")


@cli.command()
@click.option(
    "--github-root",
    default="evals/github",
    help="Root directory containing cloned repositories",
    show_default=True,
)
@click.option(
    "--prompts-dir",
    default="prompts",
    help="Directory containing prompt files",
    show_default=True,
)
@click.option(
    "--repo",
    multiple=True,
    help="Specific repository to run (can be specified multiple times)",
)
def run(github_root: str, prompts_dir: str, repo: tuple[str, ...]):
    """Execute codex commands on repositories with the latest prompt.

    Resets each repository to a clean state, then runs the codex tool
    with the latest versioned prompt file.
    """
    github_path = Path(github_root)
    prompts_path = Path(prompts_dir)

    if not github_path.exists():
        console.print(f"[red]Error:[/red] GitHub root not found: {github_root}")
        console.print("Run [bold]codespeak repos[/bold] first")
        sys.exit(1)

    # Find latest prompt
    prompt_files = sorted(prompts_path.glob("v*.md"))
    if not prompt_files:
        console.print(f"[red]Error:[/red] No prompt files found in {prompts_dir}")
        sys.exit(1)

    latest_prompt = prompt_files[-1].resolve()
    console.print(f"[bold]Using prompt:[/bold] {latest_prompt.name}\n")

    # Load prompt content
    prompt_content = latest_prompt.read_text()

    # Get list of repositories
    if repo:
        repos = list(repo)
    else:
        repos = [d.name for d in github_path.iterdir() if d.is_dir()]

    if not repos:
        console.print("[yellow]Warning:[/yellow] No repositories found")
        return

    console.print(f"[bold blue]Processing {len(repos)} repositories...[/bold blue]\n")

    for repo_name in repos:
        repo_dir = github_path / repo_name
        if not repo_dir.exists():
            console.print(f"  ✗ [red]{repo_name}[/red] - not found")
            continue

        console.print(f"[bold]→ {repo_name}[/bold]")

        # Reset repository
        try:
            subprocess.run(
                ["git", "reset", "--hard", "HEAD"],
                cwd=repo_dir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "clean", "-fd"],
                cwd=repo_dir,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            console.print(f"  ✗ Failed to reset repository: {e.stderr.decode()}")
            continue

        # Run codex
        try:
            subprocess.run(
                [
                    "codex", "exec",
                    "--cd", str(repo_dir),
                    "--sandbox", "workspace-write",
                    prompt_content,
                ],
                check=True,
            )
            console.print(f"  ✓ [green]Completed[/green]\n")
        except subprocess.CalledProcessError:
            console.print(f"  ✗ [red]Failed[/red]\n")

    console.print("[bold green]✓[/bold green] Run completed")
    console.print("Run [bold]codespeak collect[/bold] to gather summaries")


@cli.command()
@click.option(
    "--github-root",
    default="evals/github",
    help="Root directory containing repositories",
    show_default=True,
)
@click.option(
    "--artifacts-root",
    default="run_artifacts",
    help="Directory to store collected artifacts",
    show_default=True,
)
@click.option(
    "--repo",
    multiple=True,
    help="Specific repository to collect from (can be specified multiple times)",
)
def collect(github_root: str, artifacts_root: str, repo: tuple[str, ...]):
    """Collect documentation artifacts from repositories.

    Gathers generated docs from each repository and copies them
    to the artifacts directory for review.
    """
    github_path = Path(github_root)
    artifacts_path = Path(artifacts_root) / "agent_reports"

    if not github_path.exists():
        console.print(f"[red]Error:[/red] GitHub root not found: {github_root}")
        sys.exit(1)

    # Get list of repositories
    if repo:
        repos = list(repo)
    else:
        repos = [d.name for d in github_path.iterdir() if d.is_dir()]

    if not repos:
        console.print("[yellow]Warning:[/yellow] No repositories found")
        return

    artifacts_path.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold blue]Collecting from {len(repos)} repositories...[/bold blue]\n")

    collected = 0
    for repo_name in repos:
        repo_dir = github_path / repo_name
        docs_dir = repo_dir / "docs"

        if not docs_dir.exists():
            console.print(f"  - [dim]{repo_name}[/dim] (no docs)")
            continue

        dest_dir = artifacts_path / repo_name

        # Remove existing artifacts
        if dest_dir.exists():
            import shutil
            shutil.rmtree(dest_dir)

        # Copy docs
        import shutil
        shutil.copytree(docs_dir, dest_dir)
        console.print(f"  ✓ [green]{repo_name}[/green]")
        collected += 1

    console.print(f"\n[bold green]✓[/bold green] Collected {collected} artifacts")
    console.print(f"Docs are in {artifacts_path}/")


@cli.group()
def coverage():
    """Code coverage analysis commands.

    Track baseline and generated test coverage across repositories.
    """
    pass


@coverage.command("baseline")
@click.option(
    "--artifacts-root",
    default="run_artifacts",
    help="Directory for coverage artifacts",
    show_default=True,
)
@click.option(
    "--github-root",
    default="evals/github",
    help="Root directory containing repositories",
    show_default=True,
)
@click.option(
    "--docker-image",
    default="python:3.11-bullseye",
    help="Docker image for running coverage",
    show_default=True,
)
@click.option(
    "--docker-cache",
    help="Host path to mount as UV cache directory",
)
@click.option(
    "--repo",
    multiple=True,
    help="Specific repository to analyze (can be specified multiple times)",
)
@click.option(
    "--skip-html",
    is_flag=True,
    help="Skip HTML report generation",
)
def coverage_baseline(
    artifacts_root: str,
    github_root: str,
    docker_image: str,
    docker_cache: Optional[str],
    repo: tuple[str, ...],
    skip_html: bool,
):
    """Collect baseline coverage before test generation.

    Runs existing tests to establish coverage baseline for comparison.
    """
    github_path = Path(github_root)

    if not github_path.exists():
        console.print(f"[red]Error:[/red] No repositories found under {github_root}")
        console.print("Run [bold]codespeak repos[/bold] first")
        sys.exit(1)

    console.print("[bold blue]Collecting baseline coverage...[/bold blue]\n")

    # Build command
    cmd = [
        sys.executable,
        "scripts/run_coverage.py",
        "baseline",
        "--artifacts-root", artifacts_root,
        "--github-root", github_root,
        "--docker-image", docker_image,
    ]

    if docker_cache:
        cmd.extend(["--docker-cache", docker_cache])

    if skip_html:
        cmd.append("--skip-html")

    for r in repo:
        cmd.extend(["--repo", r])

    # Run coverage script
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


@coverage.command("generated")
@click.option(
    "--artifacts-root",
    default="run_artifacts",
    help="Directory for coverage artifacts",
    show_default=True,
)
@click.option(
    "--github-root",
    default="evals/github",
    help="Root directory containing repositories",
    show_default=True,
)
@click.option(
    "--docker-image",
    default="python:3.11-bullseye",
    help="Docker image for running coverage",
    show_default=True,
)
@click.option(
    "--docker-cache",
    help="Host path to mount as UV cache directory",
)
@click.option(
    "--repo",
    multiple=True,
    help="Specific repository to analyze (can be specified multiple times)",
)
@click.option(
    "--skip-html",
    is_flag=True,
    help="Skip HTML report generation",
)
def coverage_generated(
    artifacts_root: str,
    github_root: str,
    docker_image: str,
    docker_cache: Optional[str],
    repo: tuple[str, ...],
    skip_html: bool,
):
    """Collect coverage after test generation.

    Runs tests including generated ones to measure coverage improvement.
    """
    artifacts_path = Path(artifacts_root) / "coverage_reports_before"

    if not artifacts_path.exists():
        console.print(f"[red]Error:[/red] No baseline coverage found under {artifacts_root}")
        console.print("Run [bold]codespeak coverage baseline[/bold] first")
        sys.exit(1)

    console.print("[bold blue]Collecting generated coverage...[/bold blue]\n")

    # Build command
    cmd = [
        sys.executable,
        "scripts/run_coverage.py",
        "generated",
        "--artifacts-root", artifacts_root,
        "--github-root", github_root,
        "--docker-image", docker_image,
    ]

    if docker_cache:
        cmd.extend(["--docker-cache", docker_cache])

    if skip_html:
        cmd.append("--skip-html")

    for r in repo:
        cmd.extend(["--repo", r])

    # Run coverage script
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


@coverage.command("diff")
@click.option(
    "--artifacts-root",
    default="run_artifacts",
    help="Directory containing coverage artifacts",
    show_default=True,
)
@click.option(
    "--output",
    help="File to write JSON summary to",
)
def coverage_diff(artifacts_root: str, output: Optional[str]):
    """Compare baseline vs generated coverage.

    Shows coverage improvements from generated tests.
    """
    artifacts_path = Path(artifacts_root)
    baseline_path = artifacts_path / "coverage_reports_before"
    generated_path = artifacts_path / "coverage_reports_after"

    if not baseline_path.exists() or not generated_path.exists():
        console.print(f"[red]Error:[/red] Baseline or generated artifacts missing under {artifacts_root}")
        console.print("Run [bold]codespeak coverage baseline[/bold] and [bold]codespeak coverage generated[/bold] first")
        sys.exit(1)

    console.print("[bold blue]Computing coverage diff...[/bold blue]\n")

    # Build command
    cmd = [
        sys.executable,
        "scripts/coverage_diff.py",
        "--artifacts-root", artifacts_root,
    ]

    if output:
        cmd.extend(["--output", output])

    # Run diff script
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    cli()
