"""Run all workflow command."""

from __future__ import annotations

import click
from rich.console import Console

from codespeak.commands.collect_artifacts import collect_artifacts
from codespeak.commands.coverage import coverage_baseline, coverage_diff, coverage_generated
from codespeak.commands.download_repos import download_repos
from codespeak.commands.generate import generate

console = Console()


@click.command()
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
    default="ghcr.io/astral-sh/uv:python3.11-bookworm-slim",
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
