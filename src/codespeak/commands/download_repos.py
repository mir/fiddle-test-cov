"""Download GitHub repositories command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

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
def download_repos(github_root: str, repos_file: str):
    """Clone GitHub repositories from YAML file.

    Reads repository URLs from the YAML file and clones them into
    the specified directory. Skips repositories that already exist.
    """
    repos_path = Path(repos_file)
    github_path = Path(github_root)

    if not repos_path.exists():
        console.print(f"[yellow]Repository file not found:[/yellow] {repos_file}\n")

        # Prompt user to choose which repositories to add
        console.print("Choose repositories to add:")
        console.print("  [1] Empty file (add repos manually later)")
        console.print("  [2] taiga-back only")
        console.print("  [3] fiddle-test-cov only")
        console.print("  [4] Both taiga-back and fiddle-test-cov")

        choice = click.prompt(
            "\nEnter your choice",
            type=click.IntRange(1, 4),
            default=2,
            show_default=True,
        )

        # Create evals directory if it doesn't exist
        repos_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine repos to add based on choice
        repos_to_add = []
        if choice == 2:
            repos_to_add = ["https://github.com/taigaio/taiga-back"]
        elif choice == 3:
            repos_to_add = ["https://github.com/mir/fiddle-test-cov"]
        elif choice == 4:
            repos_to_add = [
                "https://github.com/taigaio/taiga-back",
                "https://github.com/mir/fiddle-test-cov",
            ]

        # Write repos to file
        with open(repos_path, "w") as f:
            for repo in repos_to_add:
                f.write(f"- {repo}\n")

        console.print(f"[green]✓[/green] Created {repos_file}")
        if repos_to_add:
            console.print("  Repositories:")
            for repo in repos_to_add:
                console.print(f"    - {repo}")
        else:
            console.print("  (empty - add repositories manually)")
        console.print()

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
