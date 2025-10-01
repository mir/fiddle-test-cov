"""Coverage analysis commands."""

from __future__ import annotations

import sys
from pathlib import Path

import click
import yaml
from rich.console import Console

from codespeak.coverage import (
    compute_diff,
    discover_repositories,
    execute_coverage_collection,
    format_repo_line,
    save_diff_json,
    save_summary,
)
from codespeak.coverage.models import RepoConfig

console = Console()


def load_repo_configs(repos_file: str = "evals/github_repos.yaml") -> dict[str, RepoConfig]:
    """Load repository configurations from YAML file.

    Returns:
        Dictionary mapping repository names to their configurations
    """
    repos_path = Path(repos_file)
    if not repos_path.exists():
        return {}

    with open(repos_path) as f:
        repo_data = yaml.safe_load(f)

    if not repo_data:
        return {}

    # Parse into RepoConfig objects and create name -> config mapping
    configs = [RepoConfig.from_dict(item) for item in repo_data]
    return {config.name: config for config in configs}


@click.group()
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
    docker_cache: str | None,
    repo: tuple[str, ...],
    skip_html: bool,
):
    """Collect baseline coverage before test generation.

    Runs existing tests to establish coverage baseline for comparison.
    """
    artifacts_path = Path(artifacts_root)
    github_path = Path(github_root)

    if not github_path.exists():
        console.print(f"[red]Error:[/red] No repositories found under {github_root}")
        console.print("Run [bold]codespeak download-repos[/bold] first")
        sys.exit(1)

    console.print("[bold blue]Collecting baseline coverage...[/bold blue]\n")

    # Prepare Docker cache path
    docker_cache_path = None
    if docker_cache:
        docker_cache_path = Path(docker_cache)
        if not docker_cache_path.is_absolute():
            docker_cache_path = (Path.cwd() / docker_cache_path).resolve()

    # Discover repositories
    repos = discover_repositories(github_path, list(repo) if repo else None)
    if not repos:
        console.print("[red]Error:[/red] No repositories to process")
        console.print("Run [bold]codespeak download-repos[/bold] first")
        sys.exit(1)

    console.print(f"Running coverage phase 'baseline' for {len(repos)} repos.\n")

    # Load repository configurations
    repo_configs = load_repo_configs()

    # Execute coverage collection
    results = execute_coverage_collection(
        phase="baseline",
        artifacts_root=artifacts_path,
        github_root=github_path,
        repos=repos,
        skip_html=skip_html,
        docker_image=docker_image,
        docker_cache=docker_cache_path,
        repo_configs=repo_configs,
    )

    # Save summary
    summary_path = save_summary(
        phase="baseline",
        artifacts_root=artifacts_path,
        github_root=github_path,
        docker_image=docker_image,
        docker_cache=docker_cache_path,
        results=results,
    )

    console.print(f"\n[bold green]✓[/bold green] Summary written to {summary_path}")


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
    docker_cache: str | None,
    repo: tuple[str, ...],
    skip_html: bool,
):
    """Collect coverage after test generation.

    Runs tests including generated ones to measure coverage improvement.
    """
    artifacts_path = Path(artifacts_root)
    baseline_path = artifacts_path / "coverage_reports_before"

    if not baseline_path.exists():
        console.print(f"[red]Error:[/red] No baseline coverage found under {artifacts_root}")
        console.print("Run [bold]codespeak coverage baseline[/bold] first")
        sys.exit(1)

    console.print("[bold blue]Collecting generated coverage...[/bold blue]\n")

    github_path = Path(github_root)

    # Prepare Docker cache path
    docker_cache_path = None
    if docker_cache:
        docker_cache_path = Path(docker_cache)
        if not docker_cache_path.is_absolute():
            docker_cache_path = (Path.cwd() / docker_cache_path).resolve()

    # Discover repositories
    repos = discover_repositories(github_path, list(repo) if repo else None)
    if not repos:
        console.print("[red]Error:[/red] No repositories to process")
        console.print("Run [bold]codespeak download-repos[/bold] to clone repositories first")
        sys.exit(1)

    console.print(f"Running coverage phase 'generated' for {len(repos)} repos.\n")

    # Load repository configurations
    repo_configs = load_repo_configs()

    # Execute coverage collection
    results = execute_coverage_collection(
        phase="generated",
        artifacts_root=artifacts_path,
        github_root=github_path,
        repos=repos,
        skip_html=skip_html,
        docker_image=docker_image,
        docker_cache=docker_cache_path,
        repo_configs=repo_configs,
    )

    # Save summary
    summary_path = save_summary(
        phase="generated",
        artifacts_root=artifacts_path,
        github_root=github_path,
        docker_image=docker_image,
        docker_cache=docker_cache_path,
        results=results,
    )

    console.print(f"\n[bold green]✓[/bold green] Summary written to {summary_path}")


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
def coverage_diff(artifacts_root: str, output: str | None):
    """Compare baseline vs generated coverage.

    Shows coverage improvements from generated tests.
    """
    artifacts_path = Path(artifacts_root)
    baseline_path = artifacts_path / "coverage_reports_before"
    generated_path = artifacts_path / "coverage_reports_after"

    if not baseline_path.exists() or not generated_path.exists():
        console.print(
            f"[red]Error:[/red] Baseline or generated artifacts missing under {artifacts_root}"
        )
        console.print(
            "Run [bold]codespeak coverage baseline[/bold] and "
            "[bold]codespeak coverage generated[/bold] first"
        )
        sys.exit(1)

    console.print("[bold blue]Computing coverage diff...[/bold blue]\n")

    # Compute diff
    try:
        records, aggregate_summary = compute_diff(artifacts_path, baseline_path, generated_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Print per-repository diff
    for record in records:
        print(format_repo_line(record))

    # Print aggregate summary
    print("\nAggregate:")
    agg_base = aggregate_summary["baseline"]
    agg_gen = aggregate_summary["generated"]
    agg_delta = aggregate_summary["delta"]
    print(f"Baseline covered: {agg_base['covered_lines']} ({agg_base['percent_covered']})")
    print(f"Generated covered: {agg_gen['covered_lines']} ({agg_gen['percent_covered']})")
    print(f"Delta lines: {agg_delta['covered_lines']} | Delta pct: {agg_delta['percent_covered']}")

    # Save JSON if requested
    if output:
        output_path = Path(output)
        save_diff_json(output_path, baseline_path, generated_path, records, aggregate_summary)
        console.print(f"\n[bold green]✓[/bold green] JSON summary written to {output_path}")
