#!/usr/bin/env python3
"""Modern CLI for managing code evaluation workflows."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from codespeak.coverage import (
    compute_diff,
    discover_repositories,
    execute_coverage_collection,
    format_repo_line,
    save_diff_json,
    save_summary,
)

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CodeSpeak - Modern CLI for code evaluation workflows.

    Manage repositories, run evaluations, and track code coverage.

    \b
    Quick start:
      run-all              - Execute complete workflow automatically

    \b
    Typical workflow (manual):
      1. download-repos    - Clone repositories from YAML file
      2. coverage baseline - Collect baseline coverage metrics
      3. generate          - Generate tests with codex
      4. collect-artifacts - Gather generated documentation
      5. coverage generated- Collect post-generation coverage
      6. coverage diff     - Compare coverage improvements
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
def download_repos(github_root: str, repos_file: str):
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
def generate(github_root: str, prompts_dir: str, repo: tuple[str, ...]):
    """Execute codex commands on repositories with the latest prompt.

    Resets each repository to a clean state, then runs the codex tool
    with the latest versioned prompt file.
    """
    github_path = Path(github_root)
    prompts_path = Path(prompts_dir)

    if not github_path.exists():
        console.print(f"[red]Error:[/red] GitHub root not found: {github_root}")
        console.print("Run [bold]codespeak download-repos[/bold] first")
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
        console.print("Run [bold]codespeak download-repos[/bold] to clone repositories first")
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
                    "codex",
                    "exec",
                    "--cd",
                    str(repo_dir),
                    "--sandbox",
                    "workspace-write",
                    prompt_content,
                ],
                check=True,
            )
            console.print("  ✓ [green]Completed[/green]\n")
        except subprocess.CalledProcessError:
            console.print("  ✗ [red]Failed[/red]\n")

    console.print("[bold green]✓[/bold green] Run completed")
    console.print("Run [bold]codespeak collect-artifacts[/bold] to gather summaries")


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
            import shutil

            shutil.rmtree(dest_dir)

        # Copy docs
        import shutil

        shutil.copytree(docs_dir, dest_dir)
        console.print(f"  ✓ [green]{repo_name}[/green]")
        collected += 1

    console.print(f"\n[bold green]✓[/bold green] Collected {collected} artifacts")
    console.print(f"Docs are in {artifacts_path}/")


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
@click.option(
    "--prompts-dir",
    default="prompts",
    help="Directory containing prompt files",
    show_default=True,
)
@click.option(
    "--artifacts-root",
    default="run_artifacts",
    help="Directory for coverage artifacts",
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
    "--skip-html",
    is_flag=True,
    help="Skip HTML report generation",
)
@click.option(
    "--repo",
    multiple=True,
    help="Specific repository to process (can be specified multiple times)",
)
def run_all(
    github_root: str,
    repos_file: str,
    prompts_dir: str,
    artifacts_root: str,
    docker_image: str,
    docker_cache: str | None,
    skip_html: bool,
    repo: tuple[str, ...],
):
    """Run the complete evaluation workflow.

    Executes all steps in sequence:
    1. Download repositories
    2. Collect baseline coverage
    3. Generate tests
    4. Collect artifacts
    5. Collect generated coverage
    6. Compare coverage
    """
    console.print("[bold blue]Starting complete evaluation workflow...[/bold blue]\n")

    # Step 1: Download repos
    console.print("[bold]Step 1/6:[/bold] Downloading repositories...")
    ctx = click.get_current_context()
    ctx.invoke(
        download_repos,
        github_root=github_root,
        repos_file=repos_file,
    )
    console.print()

    # Step 2: Baseline coverage
    console.print("[bold]Step 2/6:[/bold] Collecting baseline coverage...")
    ctx.invoke(
        coverage_baseline,
        artifacts_root=artifacts_root,
        github_root=github_root,
        docker_image=docker_image,
        docker_cache=docker_cache,
        repo=repo,
        skip_html=skip_html,
    )
    console.print()

    # Step 3: Generate tests
    console.print("[bold]Step 3/6:[/bold] Generating tests...")
    ctx.invoke(
        generate,
        github_root=github_root,
        prompts_dir=prompts_dir,
        repo=repo,
    )
    console.print()

    # Step 4: Collect artifacts
    console.print("[bold]Step 4/6:[/bold] Collecting artifacts...")
    ctx.invoke(
        collect_artifacts,
        github_root=github_root,
        artifacts_root=artifacts_root,
        repo=repo,
    )
    console.print()

    # Step 5: Generated coverage
    console.print("[bold]Step 5/6:[/bold] Collecting generated coverage...")
    ctx.invoke(
        coverage_generated,
        artifacts_root=artifacts_root,
        github_root=github_root,
        docker_image=docker_image,
        docker_cache=docker_cache,
        repo=repo,
        skip_html=skip_html,
    )
    console.print()

    # Step 6: Coverage diff
    console.print("[bold]Step 6/6:[/bold] Computing coverage diff...")
    ctx.invoke(
        coverage_diff,
        artifacts_root=artifacts_root,
        output=None,
    )
    console.print()

    console.print("[bold green]✓ Complete workflow finished successfully![/bold green]")


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

    # Execute coverage collection
    results = execute_coverage_collection(
        phase="baseline",
        artifacts_root=artifacts_path,
        github_root=github_path,
        repos=repos,
        skip_html=skip_html,
        docker_image=docker_image,
        docker_cache=docker_cache_path,
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

    # Execute coverage collection
    results = execute_coverage_collection(
        phase="generated",
        artifacts_root=artifacts_path,
        github_root=github_path,
        repos=repos,
        skip_html=skip_html,
        docker_image=docker_image,
        docker_cache=docker_cache_path,
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


if __name__ == "__main__":
    cli()
