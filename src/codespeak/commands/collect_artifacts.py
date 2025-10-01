"""Collect artifacts command."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
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
def collect_artifacts(github_root: str, artifacts_root: str, repo: tuple[str, ...]):
    """Collect documentation artifacts from repositories.

    Gathers generated docs from each repository and copies them
    to the artifacts directory for review.
    """
    github_path = Path(github_root)
    artifacts_path = Path(artifacts_root) / "agent_reports"

    if not github_path.exists():
        console.print(f"[red]Error:[/red] GitHub root not found: {github_root}")
        console.print("Run [bold]codespeak download-repos[/bold] to clone repositories first")
        sys.exit(1)

    # Get list of repositories
    if repo:
        repos = list(repo)
    else:
        repos = [d.name for d in github_path.iterdir() if d.is_dir()]

    if not repos:
        console.print("[yellow]Warning:[/yellow] No repositories found")
        console.print("Run [bold]codespeak download-repos[/bold] to clone repositories first")
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
            shutil.rmtree(dest_dir)

        # Copy docs
        shutil.copytree(docs_dir, dest_dir)
        console.print(f"  ✓ [green]{repo_name}[/green]")
        collected += 1

    console.print(f"\n[bold green]✓[/bold green] Collected {collected} artifacts")
    console.print(f"Docs are in {artifacts_path}/")
