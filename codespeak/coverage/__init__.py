"""Coverage collection and analysis for code repositories."""

from .diff import compute_diff, format_repo_line, save_diff_json
from .models import CommandResult, CoverageTotals, RepoDiff, RepoResult
from .runner import execute_coverage_collection, save_summary
from .utils import discover_repositories

__all__ = [
    "CommandResult",
    "CoverageTotals",
    "RepoDiff",
    "RepoResult",
    "compute_diff",
    "discover_repositories",
    "execute_coverage_collection",
    "format_repo_line",
    "save_diff_json",
    "save_summary",
]
