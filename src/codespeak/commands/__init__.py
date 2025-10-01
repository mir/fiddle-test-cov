"""CLI commands for codespeak."""

from codespeak.commands.collect_artifacts import collect_artifacts
from codespeak.commands.coverage import coverage
from codespeak.commands.download_repos import download_repos
from codespeak.commands.generate import generate
from codespeak.commands.run_all import run_all
from codespeak.commands.update_tests import update_tests

__all__ = [
    "collect_artifacts",
    "coverage",
    "download_repos",
    "generate",
    "run_all",
    "update_tests",
]
