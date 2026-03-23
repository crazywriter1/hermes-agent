"""Tests for shell completion support (Issue #2582).

Verifies that:
  - ``build_parser()`` returns a proper ``ArgumentParser``
  - the ``completion`` subcommand exists and works for zsh/bash
  - graceful error when argcomplete is not installed
  - all expected subcommands are present
  - ``_SUBCOMMANDS`` matches the parser's actual subcommands
  - ``argcomplete.autocomplete()`` is a no-op without ``_ARGCOMPLETE``
"""

from __future__ import annotations

import argparse
import io
import sys
from unittest import mock

import pytest

from hermes_cli.parser import build_parser


# ── 1. build_parser() returns ArgumentParser ────────────────────────────

def test_build_parser_returns_argument_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


# ── 2. completion subcommand exists ─────────────────────────────────────

def test_completion_subcommand_exists():
    parser = build_parser()
    args = parser.parse_args(["completion", "zsh"])
    assert hasattr(args, "func")
    assert args.shell == "zsh"


# ── 3. hermes completion zsh outputs valid zsh script ───────────────────

def test_completion_zsh_output(capsys):
    parser = build_parser()
    args = parser.parse_args(["completion", "zsh"])
    with mock.patch.dict("sys.modules", {"argcomplete": mock.MagicMock()}):
        args.func(args)
    captured = capsys.readouterr()
    assert "#compdef" in captured.out
    assert "register-python-argcomplete" in captured.out


# ── 4. hermes completion bash outputs valid bash script ─────────────────

def test_completion_bash_output(capsys):
    parser = build_parser()
    args = parser.parse_args(["completion", "bash"])
    with mock.patch.dict("sys.modules", {"argcomplete": mock.MagicMock()}):
        args.func(args)
    captured = capsys.readouterr()
    assert "register-python-argcomplete" in captured.out
    assert "#compdef" not in captured.out


# ── 5. graceful error when argcomplete not installed ────────────────────

def test_completion_graceful_error_without_argcomplete(capsys):
    parser = build_parser()
    args = parser.parse_args(["completion", "bash"])

    original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

    def _fake_import(name, *a, **kw):
        if name == "argcomplete":
            raise ImportError("No module named 'argcomplete'")
        return original_import(name, *a, **kw)

    with mock.patch("builtins.__import__", side_effect=_fake_import):
        with pytest.raises(SystemExit) as exc_info:
            args.func(args)
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "argcomplete" in captured.err


# ── 6. all expected subcommands present in parser ───────────────────────

EXPECTED_SUBCOMMANDS = {
    "chat", "model", "gateway", "setup", "whatsapp", "login", "logout",
    "status", "cron", "doctor", "config", "pairing", "skills", "tools",
    "mcp", "sessions", "insights", "version", "update", "uninstall",
    "plugins", "honcho", "claw", "acp", "completion",
}


def test_all_expected_subcommands_present():
    parser = build_parser()
    # argparse stores subparsers in _subparsers._group_actions
    subparser_actions = [
        action for action in parser._subparsers._group_actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    assert len(subparser_actions) == 1
    actual = set(subparser_actions[0].choices.keys())
    missing = EXPECTED_SUBCOMMANDS - actual
    assert not missing, f"Missing subcommands: {missing}"


# ── 7. _SUBCOMMANDS matches parser subcommands (drift prevention) ──────

def test_subcommands_set_matches_parser():
    """Ensure _SUBCOMMANDS in _coalesce_session_name_args stays in sync."""
    import inspect
    from hermes_cli.main import _coalesce_session_name_args

    src = inspect.getsource(_coalesce_session_name_args)
    # Extract _SUBCOMMANDS set from the source
    local_ns: dict = {}
    # Run the function body up to the _SUBCOMMANDS definition
    for line in src.split("\n"):
        stripped = line.strip()
        if "_SUBCOMMANDS" in stripped and "=" in stripped:
            # Collect the full set literal
            idx = src.index(stripped)
            # Find matching closing brace
            brace_start = src.index("{", idx)
            brace_end = src.index("}", brace_start)
            set_literal = src[brace_start:brace_end + 1]
            local_ns["_SUBCOMMANDS"] = eval(set_literal)  # noqa: S307
            break

    assert "_SUBCOMMANDS" in local_ns, "Could not extract _SUBCOMMANDS from source"
    code_subcommands = local_ns["_SUBCOMMANDS"]

    parser = build_parser()
    subparser_actions = [
        action for action in parser._subparsers._group_actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    parser_subcommands = set(subparser_actions[0].choices.keys())

    missing_from_set = parser_subcommands - code_subcommands
    assert not missing_from_set, (
        f"Subcommands in parser but missing from _SUBCOMMANDS: {missing_from_set}"
    )


# ── 8. argcomplete.autocomplete() is no-op without _ARGCOMPLETE env ────

def test_argcomplete_noop_without_env():
    """Calling autocomplete without _ARGCOMPLETE env var should be a no-op."""
    parser = build_parser()
    try:
        import argcomplete
        # Make sure _ARGCOMPLETE is NOT set
        env_backup = {}
        for key in ("_ARGCOMPLETE", "COMP_LINE", "COMP_POINT"):
            if key in sys.modules.get("os", __import__("os")).environ:
                env_backup[key] = __import__("os").environ.pop(key)
        try:
            argcomplete.autocomplete(parser)
        finally:
            __import__("os").environ.update(env_backup)
    except ImportError:
        pytest.skip("argcomplete not installed")
