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

        # Prompt user to create the file with default taiga repo
        create = click.confirm(
            "Would you like to create the file with the taiga-back repository as default?",
            default=True,
        )

        if not create:
            console.print("[red]Aborted.[/red] Please create the file manually.")
            sys.exit(1)

        # Create evals directory if it doesn't exist
        repos_path.parent.mkdir(parents=True, exist_ok=True)

        # Write default taiga repo
        default_repo = "https://github.com/taigaio/taiga-back"
        with open(repos_path, "w") as f:
            f.write(f"- {default_repo}\n")

        console.print(f"[green]✓[/green] Created {repos_file} with default repository")
        console.print(f"  Default: {default_repo}\n")

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
