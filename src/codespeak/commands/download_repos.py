"""Download GitHub repositories command."""

from __future__ import annotations

import subprocess
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from codespeak.coverage.models import RepoConfig

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

    # Load repository configurations
    with open(repos_path) as f:
        repo_data = yaml.safe_load(f)

    if not repo_data:
        console.print("[yellow]Warning:[/yellow] No repositories found in YAML file")
        return

    # Parse into RepoConfig objects (supports both legacy URL strings and new format)
    repo_configs = [RepoConfig.from_dict(item) for item in repo_data]

    # Create github root directory
    github_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold blue]Cloning {len(repo_configs)} repositories...[/bold blue]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for config in repo_configs:
            repo_dir = github_path / config.name

            if repo_dir.exists():
                progress.console.print(f"  ✓ [dim]{config.name}[/dim] (already exists)")
                continue

            task = progress.add_task(f"Cloning {config.name}...", total=None)

            try:
                progress.console.print(f"  $ git clone {config.url} {repo_dir}")
                subprocess.run(
                    ["git", "clone", config.url, str(repo_dir)],
                    capture_output=False,  # Show output in real-time
                    check=True,
                )
                progress.console.print(f"  ✓ [green]{config.name}[/green]")
            except subprocess.CalledProcessError as e:
                progress.console.print(f"  ✗ [red]{config.name}[/red] - Command failed with exit code {e.returncode}")
            finally:
                progress.remove_task(task)

    console.print(f"\n[bold green]✓[/bold green] Repositories are in {github_root}/")
