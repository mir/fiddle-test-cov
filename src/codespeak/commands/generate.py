"""Generate tests command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
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
