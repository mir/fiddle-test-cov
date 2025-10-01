"""Test CLI basic functionality."""

import subprocess


def test_help_message_non_empty():
    """Test that --help message is non-empty."""
    result = subprocess.run(
        ["uv", "run", "codespeak", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0
    assert "codespeak" in result.stdout.lower() or "usage" in result.stdout.lower()
