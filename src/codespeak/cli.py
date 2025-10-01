#!/usr/bin/env python3
"""Modern CLI for managing code evaluation workflows."""

from __future__ import annotations

import click

from codespeak.commands import (
    collect_artifacts,
    coverage,
    download_repos,
    generate,
    run_all,
)


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


# Register commands
cli.add_command(download_repos)
cli.add_command(generate)
cli.add_command(collect_artifacts)
cli.add_command(run_all)
cli.add_command(coverage)


if __name__ == "__main__":
    cli()
