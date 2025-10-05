"""Update tests command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command()
@click.option(
    "--prompts-dir",
    default=None,
    help="Directory containing prompt files (defaults to package prompts)",
    show_default=True,
)
def update_tests(prompts_dir: str | None):
    """Execute codex command in the current directory with the latest prompt.

    Runs the codex tool with the latest versioned prompt file in the current
    working directory. Useful for maintaining test coverage in any repository.
    """
    # Use package prompts if no custom path provided
    if prompts_dir is None:
        prompts_path = Path(__file__).parent.parent / "prompts"
    else:
        prompts_path = Path(prompts_dir)

    current_dir = Path.cwd()

    # Find latest prompt
    prompt_files = sorted(prompts_path.glob("v*.md"))
    if not prompt_files:
        console.print(f"[red]Error:[/red] No prompt files found in {prompts_dir}")
        sys.exit(1)

    latest_prompt = prompt_files[-1].resolve()
    console.print(f"[bold]Using prompt:[/bold] {latest_prompt.name}")
    console.print(f"[bold]Working directory:[/bold] {current_dir}\n")

    # Load prompt content
    prompt_content = latest_prompt.read_text()

    # Run codex in current directory
    try:
        codex_cmd = [
            "codex",
            "exec",
            "--cd",
            str(current_dir),
            "--sandbox",
            "workspace-write",
            prompt_content,
        ]
        console.print(f"$ {' '.join(codex_cmd[:6])} <prompt>\n")
        subprocess.run(
            codex_cmd,
            check=True,
        )
        console.print("\n[bold green]✓[/bold green] Run completed")
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]✗ Failed[/red] - exit code {e.returncode}")
        sys.exit(1)
