"""Hermes CLI argument parser construction.

Extracted from ``hermes_cli.main`` so the parser tree can be imported
without triggering module-level side effects (.env loading, heavy
imports).  This is required for shell completion via *argcomplete*.
"""

from __future__ import annotations

import argparse
import os
import sys


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the full Hermes CLI argument parser.

    All inline ``cmd_*`` handlers that were originally nested inside
    ``main()`` are defined here as local functions.  Module-level handlers
    that live in ``hermes_cli.main`` are wired through thin lazy-import
    wrappers to avoid circular imports.
    """

    # ------------------------------------------------------------------
    # Root parser
    # ------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        prog="hermes",
        description="Hermes Agent - AI assistant with tool-calling capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    hermes                        Start interactive chat
    hermes chat -q "Hello"        Single query mode
    hermes -c                     Resume the most recent session
    hermes -c "my project"        Resume a session by name (latest in lineage)
    hermes --resume <session_id>  Resume a specific session by ID
    hermes setup                  Run setup wizard
    hermes logout                 Clear stored authentication
    hermes model                  Select default model
    hermes config                 View configuration
    hermes config edit            Edit config in $EDITOR
    hermes config set model gpt-4 Set a config value
    hermes gateway                Run messaging gateway
    hermes -s hermes-agent-dev,github-auth
    hermes -w                     Start in isolated git worktree
    hermes gateway install        Install gateway background service
    hermes sessions list          List past sessions
    hermes sessions browse        Interactive session picker
    hermes sessions rename ID T   Rename/title a session
    hermes update                 Update to latest version

For more help on a command:
    hermes <command> --help
"""
    )

    parser.add_argument(
        "--version", "-V",
        action="store_true",
        help="Show version and exit"
    )
    parser.add_argument(
        "--resume", "-r",
        metavar="SESSION",
        default=None,
        help="Resume a previous session by ID or title"
    )
    parser.add_argument(
        "--continue", "-c",
        dest="continue_last",
        nargs="?",
        const=True,
        default=None,
        metavar="SESSION_NAME",
        help="Resume a session by name, or the most recent if no name given"
    )
    parser.add_argument(
        "--worktree", "-w",
        action="store_true",
        default=False,
        help="Run in an isolated git worktree (for parallel agents)"
    )
    parser.add_argument(
        "--skills", "-s",
        action="append",
        default=None,
        help="Preload one or more skills for the session (repeat flag or comma-separate)"
    )
    parser.add_argument(
        "--yolo",
        action="store_true",
        default=False,
        help="Bypass all dangerous command approval prompts (use at your own risk)"
    )
    parser.add_argument(
        "--pass-session-id",
        action="store_true",
        default=False,
        help="Include the session ID in the agent's system prompt"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # ------------------------------------------------------------------
    # Lazy-import wrappers for module-level handlers in hermes_cli.main
    # ------------------------------------------------------------------
    def _lazy_cmd_chat(args):
        from hermes_cli.main import cmd_chat
        cmd_chat(args)

    def _lazy_cmd_model(args):
        from hermes_cli.main import cmd_model
        cmd_model(args)

    def _lazy_cmd_gateway(args):
        from hermes_cli.main import cmd_gateway
        cmd_gateway(args)

    def _lazy_cmd_setup(args):
        from hermes_cli.main import cmd_setup
        cmd_setup(args)

    def _lazy_cmd_whatsapp(args):
        from hermes_cli.main import cmd_whatsapp
        cmd_whatsapp(args)

    def _lazy_cmd_login(args):
        from hermes_cli.main import cmd_login
        cmd_login(args)

    def _lazy_cmd_logout(args):
        from hermes_cli.main import cmd_logout
        cmd_logout(args)

    def _lazy_cmd_status(args):
        from hermes_cli.main import cmd_status
        cmd_status(args)

    def _lazy_cmd_cron(args):
        from hermes_cli.main import cmd_cron
        cmd_cron(args)

    def _lazy_cmd_doctor(args):
        from hermes_cli.main import cmd_doctor
        cmd_doctor(args)

    def _lazy_cmd_config(args):
        from hermes_cli.main import cmd_config
        cmd_config(args)

    def _lazy_cmd_version(args):
        from hermes_cli.main import cmd_version
        cmd_version(args)

    def _lazy_cmd_update(args):
        from hermes_cli.main import cmd_update
        cmd_update(args)

    def _lazy_cmd_uninstall(args):
        from hermes_cli.main import cmd_uninstall
        cmd_uninstall(args)

    # ==================================================================
    # chat command
    # ==================================================================
    chat_parser = subparsers.add_parser(
        "chat",
        help="Interactive chat with the agent",
        description="Start an interactive chat session with Hermes Agent"
    )
    chat_parser.add_argument(
        "-q", "--query",
        help="Single query (non-interactive mode)"
    )
    chat_parser.add_argument(
        "-m", "--model",
        help="Model to use (e.g., anthropic/claude-sonnet-4)"
    )
    chat_parser.add_argument(
        "-t", "--toolsets",
        help="Comma-separated toolsets to enable"
    )
    chat_parser.add_argument(
        "-s", "--skills",
        action="append",
        default=None,
        help="Preload one or more skills for the session (repeat flag or comma-separate)"
    )
    chat_parser.add_argument(
        "--provider",
        choices=["auto", "openrouter", "nous", "openai-codex", "copilot-acp", "copilot", "anthropic", "zai", "kimi-coding", "minimax", "minimax-cn", "kilocode"],
        default=None,
        help="Inference provider (default: auto)"
    )
    chat_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    chat_parser.add_argument(
        "-Q", "--quiet",
        action="store_true",
        help="Quiet mode for programmatic use: suppress banner, spinner, and tool previews. Only output the final response and session info."
    )
    chat_parser.add_argument(
        "--resume", "-r",
        metavar="SESSION_ID",
        help="Resume a previous session by ID (shown on exit)"
    )
    chat_parser.add_argument(
        "--continue", "-c",
        dest="continue_last",
        nargs="?",
        const=True,
        default=None,
        metavar="SESSION_NAME",
        help="Resume a session by name, or the most recent if no name given"
    )
    chat_parser.add_argument(
        "--worktree", "-w",
        action="store_true",
        default=False,
        help="Run in an isolated git worktree (for parallel agents on the same repo)"
    )
    chat_parser.add_argument(
        "--checkpoints",
        action="store_true",
        default=False,
        help="Enable filesystem checkpoints before destructive file operations (use /rollback to restore)"
    )
    chat_parser.add_argument(
        "--yolo",
        action="store_true",
        default=False,
        help="Bypass all dangerous command approval prompts (use at your own risk)"
    )
    chat_parser.add_argument(
        "--pass-session-id",
        action="store_true",
        default=False,
        help="Include the session ID in the agent's system prompt"
    )
    chat_parser.set_defaults(func=_lazy_cmd_chat)

    # ==================================================================
    # model command
    # ==================================================================
    model_parser = subparsers.add_parser(
        "model",
        help="Select default model and provider",
        description="Interactively select your inference provider and default model"
    )
    model_parser.set_defaults(func=_lazy_cmd_model)

    # ==================================================================
    # gateway command
    # ==================================================================
    gateway_parser = subparsers.add_parser(
        "gateway",
        help="Messaging gateway management",
        description="Manage the messaging gateway (Telegram, Discord, WhatsApp)"
    )
    gateway_subparsers = gateway_parser.add_subparsers(dest="gateway_command")

    gateway_run = gateway_subparsers.add_parser("run", help="Run gateway in foreground")
    gateway_run.add_argument("-v", "--verbose", action="store_true")
    gateway_run.add_argument("--replace", action="store_true",
                             help="Replace any existing gateway instance (useful for systemd)")

    gateway_start = gateway_subparsers.add_parser("start", help="Start gateway service")
    gateway_start.add_argument("--system", action="store_true", help="Target the Linux system-level gateway service")

    gateway_stop = gateway_subparsers.add_parser("stop", help="Stop gateway service")
    gateway_stop.add_argument("--system", action="store_true", help="Target the Linux system-level gateway service")

    gateway_restart = gateway_subparsers.add_parser("restart", help="Restart gateway service")
    gateway_restart.add_argument("--system", action="store_true", help="Target the Linux system-level gateway service")

    gateway_status = gateway_subparsers.add_parser("status", help="Show gateway status")
    gateway_status.add_argument("--deep", action="store_true", help="Deep status check")
    gateway_status.add_argument("--system", action="store_true", help="Target the Linux system-level gateway service")

    gateway_install = gateway_subparsers.add_parser("install", help="Install gateway as service")
    gateway_install.add_argument("--force", action="store_true", help="Force reinstall")
    gateway_install.add_argument("--system", action="store_true", help="Install as a Linux system-level service (starts at boot)")
    gateway_install.add_argument("--run-as-user", dest="run_as_user", help="User account the Linux system service should run as")

    gateway_uninstall = gateway_subparsers.add_parser("uninstall", help="Uninstall gateway service")
    gateway_uninstall.add_argument("--system", action="store_true", help="Target the Linux system-level gateway service")

    gateway_subparsers.add_parser("setup", help="Configure messaging platforms")

    gateway_parser.set_defaults(func=_lazy_cmd_gateway)

    # ==================================================================
    # setup command
    # ==================================================================
    setup_parser = subparsers.add_parser(
        "setup",
        help="Interactive setup wizard",
        description="Configure Hermes Agent with an interactive wizard. "
                    "Run a specific section: hermes setup model|terminal|gateway|tools|agent"
    )
    setup_parser.add_argument(
        "section",
        nargs="?",
        choices=["model", "terminal", "gateway", "tools", "agent"],
        default=None,
        help="Run a specific setup section instead of the full wizard"
    )
    setup_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Non-interactive mode (use defaults/env vars)"
    )
    setup_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration to defaults"
    )
    setup_parser.set_defaults(func=_lazy_cmd_setup)

    # ==================================================================
    # whatsapp command
    # ==================================================================
    whatsapp_parser = subparsers.add_parser(
        "whatsapp",
        help="Set up WhatsApp integration",
        description="Configure WhatsApp and pair via QR code"
    )
    whatsapp_parser.set_defaults(func=_lazy_cmd_whatsapp)

    # ==================================================================
    # login command
    # ==================================================================
    login_parser = subparsers.add_parser(
        "login",
        help="Authenticate with an inference provider",
        description="Run OAuth device authorization flow for Hermes CLI"
    )
    login_parser.add_argument(
        "--provider",
        choices=["nous", "openai-codex"],
        default=None,
        help="Provider to authenticate with (default: nous)"
    )
    login_parser.add_argument(
        "--portal-url",
        help="Portal base URL (default: production portal)"
    )
    login_parser.add_argument(
        "--inference-url",
        help="Inference API base URL (default: production inference API)"
    )
    login_parser.add_argument(
        "--client-id",
        default=None,
        help="OAuth client id to use (default: hermes-cli)"
    )
    login_parser.add_argument(
        "--scope",
        default=None,
        help="OAuth scope to request"
    )
    login_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not attempt to open the browser automatically"
    )
    login_parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP request timeout in seconds (default: 15)"
    )
    login_parser.add_argument(
        "--ca-bundle",
        help="Path to CA bundle PEM file for TLS verification"
    )
    login_parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS verification (testing only)"
    )
    login_parser.set_defaults(func=_lazy_cmd_login)

    # ==================================================================
    # logout command
    # ==================================================================
    logout_parser = subparsers.add_parser(
        "logout",
        help="Clear authentication for an inference provider",
        description="Remove stored credentials and reset provider config"
    )
    logout_parser.add_argument(
        "--provider",
        choices=["nous", "openai-codex"],
        default=None,
        help="Provider to log out from (default: active provider)"
    )
    logout_parser.set_defaults(func=_lazy_cmd_logout)

    # ==================================================================
    # status command
    # ==================================================================
    status_parser = subparsers.add_parser(
        "status",
        help="Show status of all components",
        description="Display status of Hermes Agent components"
    )
    status_parser.add_argument(
        "--all",
        action="store_true",
        help="Show all details (redacted for sharing)"
    )
    status_parser.add_argument(
        "--deep",
        action="store_true",
        help="Run deep checks (may take longer)"
    )
    status_parser.set_defaults(func=_lazy_cmd_status)

    # ==================================================================
    # cron command
    # ==================================================================
    cron_parser = subparsers.add_parser(
        "cron",
        help="Cron job management",
        description="Manage scheduled tasks"
    )
    cron_subparsers = cron_parser.add_subparsers(dest="cron_command")

    cron_list = cron_subparsers.add_parser("list", help="List scheduled jobs")
    cron_list.add_argument("--all", action="store_true", help="Include disabled jobs")

    cron_create = cron_subparsers.add_parser("create", aliases=["add"], help="Create a scheduled job")
    cron_create.add_argument("schedule", help="Schedule like '30m', 'every 2h', or '0 9 * * *'")
    cron_create.add_argument("prompt", nargs="?", help="Optional self-contained prompt or task instruction")
    cron_create.add_argument("--name", help="Optional human-friendly job name")
    cron_create.add_argument("--deliver", help="Delivery target: origin, local, telegram, discord, signal, or platform:chat_id")
    cron_create.add_argument("--repeat", type=int, help="Optional repeat count")
    cron_create.add_argument("--skill", dest="skills", action="append", help="Attach a skill. Repeat to add multiple skills.")

    cron_edit = cron_subparsers.add_parser("edit", help="Edit an existing scheduled job")
    cron_edit.add_argument("job_id", help="Job ID to edit")
    cron_edit.add_argument("--schedule", help="New schedule")
    cron_edit.add_argument("--prompt", help="New prompt/task instruction")
    cron_edit.add_argument("--name", help="New job name")
    cron_edit.add_argument("--deliver", help="New delivery target")
    cron_edit.add_argument("--repeat", type=int, help="New repeat count")
    cron_edit.add_argument("--skill", dest="skills", action="append", help="Replace the job's skills with this set. Repeat to attach multiple skills.")
    cron_edit.add_argument("--add-skill", dest="add_skills", action="append", help="Append a skill without replacing the existing list. Repeatable.")
    cron_edit.add_argument("--remove-skill", dest="remove_skills", action="append", help="Remove a specific attached skill. Repeatable.")
    cron_edit.add_argument("--clear-skills", action="store_true", help="Remove all attached skills from the job")

    cron_pause = cron_subparsers.add_parser("pause", help="Pause a scheduled job")
    cron_pause.add_argument("job_id", help="Job ID to pause")

    cron_resume = cron_subparsers.add_parser("resume", help="Resume a paused job")
    cron_resume.add_argument("job_id", help="Job ID to resume")

    cron_run = cron_subparsers.add_parser("run", help="Run a job on the next scheduler tick")
    cron_run.add_argument("job_id", help="Job ID to trigger")

    cron_remove = cron_subparsers.add_parser("remove", aliases=["rm", "delete"], help="Remove a scheduled job")
    cron_remove.add_argument("job_id", help="Job ID to remove")

    cron_subparsers.add_parser("status", help="Check if cron scheduler is running")
    cron_subparsers.add_parser("tick", help="Run due jobs once and exit")

    cron_parser.set_defaults(func=_lazy_cmd_cron)

    # ==================================================================
    # doctor command
    # ==================================================================
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check configuration and dependencies",
        description="Diagnose issues with Hermes Agent setup"
    )
    doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues automatically"
    )
    doctor_parser.set_defaults(func=_lazy_cmd_doctor)

    # ==================================================================
    # config command
    # ==================================================================
    config_parser = subparsers.add_parser(
        "config",
        help="View and edit configuration",
        description="Manage Hermes Agent configuration"
    )
    config_subparsers = config_parser.add_subparsers(dest="config_command")

    config_subparsers.add_parser("show", help="Show current configuration")
    config_subparsers.add_parser("edit", help="Open config file in editor")

    config_set = config_subparsers.add_parser("set", help="Set a configuration value")
    config_set.add_argument("key", nargs="?", help="Configuration key (e.g., model, terminal.backend)")
    config_set.add_argument("value", nargs="?", help="Value to set")

    config_subparsers.add_parser("path", help="Print config file path")
    config_subparsers.add_parser("env-path", help="Print .env file path")
    config_subparsers.add_parser("check", help="Check for missing/outdated config")
    config_subparsers.add_parser("migrate", help="Update config with new options")

    config_parser.set_defaults(func=_lazy_cmd_config)

    # ==================================================================
    # pairing command
    # ==================================================================
    pairing_parser = subparsers.add_parser(
        "pairing",
        help="Manage DM pairing codes for user authorization",
        description="Approve or revoke user access via pairing codes"
    )
    pairing_sub = pairing_parser.add_subparsers(dest="pairing_action")

    pairing_sub.add_parser("list", help="Show pending + approved users")

    pairing_approve_parser = pairing_sub.add_parser("approve", help="Approve a pairing code")
    pairing_approve_parser.add_argument("platform", help="Platform name (telegram, discord, slack, whatsapp)")
    pairing_approve_parser.add_argument("code", help="Pairing code to approve")

    pairing_revoke_parser = pairing_sub.add_parser("revoke", help="Revoke user access")
    pairing_revoke_parser.add_argument("platform", help="Platform name")
    pairing_revoke_parser.add_argument("user_id", help="User ID to revoke")

    pairing_sub.add_parser("clear-pending", help="Clear all pending codes")

    def cmd_pairing(args):
        from hermes_cli.pairing import pairing_command
        pairing_command(args)

    pairing_parser.set_defaults(func=cmd_pairing)

    # ==================================================================
    # skills command
    # ==================================================================
    skills_parser = subparsers.add_parser(
        "skills",
        help="Search, install, configure, and manage skills",
        description="Search, install, inspect, audit, configure, and manage skills from skills.sh, well-known agent skill endpoints, GitHub, ClawHub, and other registries."
    )
    skills_subparsers = skills_parser.add_subparsers(dest="skills_action")

    skills_browse = skills_subparsers.add_parser("browse", help="Browse all available skills (paginated)")
    skills_browse.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    skills_browse.add_argument("--size", type=int, default=20, help="Results per page (default: 20)")
    skills_browse.add_argument("--source", default="all",
                               choices=["all", "official", "skills-sh", "well-known", "github", "clawhub", "lobehub"],
                               help="Filter by source (default: all)")

    skills_search = skills_subparsers.add_parser("search", help="Search skill registries")
    skills_search.add_argument("query", help="Search query")
    skills_search.add_argument("--source", default="all", choices=["all", "official", "skills-sh", "well-known", "github", "clawhub", "lobehub"])
    skills_search.add_argument("--limit", type=int, default=10, help="Max results")

    skills_install = skills_subparsers.add_parser("install", help="Install a skill")
    skills_install.add_argument("identifier", help="Skill identifier (e.g. openai/skills/skill-creator)")
    skills_install.add_argument("--category", default="", help="Category folder to install into")
    skills_install.add_argument("--force", action="store_true", help="Install despite blocked scan verdict")
    skills_install.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt (needed in TUI mode)")

    skills_inspect = skills_subparsers.add_parser("inspect", help="Preview a skill without installing")
    skills_inspect.add_argument("identifier", help="Skill identifier")

    skills_list_p = skills_subparsers.add_parser("list", help="List installed skills")
    skills_list_p.add_argument("--source", default="all", choices=["all", "hub", "builtin", "local"])

    skills_check = skills_subparsers.add_parser("check", help="Check installed hub skills for updates")
    skills_check.add_argument("name", nargs="?", help="Specific skill to check (default: all)")

    skills_update = skills_subparsers.add_parser("update", help="Update installed hub skills")
    skills_update.add_argument("name", nargs="?", help="Specific skill to update (default: all outdated skills)")

    skills_audit = skills_subparsers.add_parser("audit", help="Re-scan installed hub skills")
    skills_audit.add_argument("name", nargs="?", help="Specific skill to audit (default: all)")

    skills_uninstall = skills_subparsers.add_parser("uninstall", help="Remove a hub-installed skill")
    skills_uninstall.add_argument("name", help="Skill name to remove")

    skills_publish = skills_subparsers.add_parser("publish", help="Publish a skill to a registry")
    skills_publish.add_argument("skill_path", help="Path to skill directory")
    skills_publish.add_argument("--to", default="github", choices=["github", "clawhub"], help="Target registry")
    skills_publish.add_argument("--repo", default="", help="Target GitHub repo (e.g. openai/skills)")

    skills_snapshot = skills_subparsers.add_parser("snapshot", help="Export/import skill configurations")
    snapshot_subparsers = skills_snapshot.add_subparsers(dest="snapshot_action")
    snap_export = snapshot_subparsers.add_parser("export", help="Export installed skills to a file")
    snap_export.add_argument("output", help="Output JSON file path")
    snap_import = snapshot_subparsers.add_parser("import", help="Import and install skills from a file")
    snap_import.add_argument("input", help="Input JSON file path")
    snap_import.add_argument("--force", action="store_true", help="Force install despite caution verdict")

    skills_tap = skills_subparsers.add_parser("tap", help="Manage skill sources")
    tap_subparsers = skills_tap.add_subparsers(dest="tap_action")
    tap_subparsers.add_parser("list", help="List configured taps")
    tap_add = tap_subparsers.add_parser("add", help="Add a GitHub repo as skill source")
    tap_add.add_argument("repo", help="GitHub repo (e.g. owner/repo)")
    tap_rm = tap_subparsers.add_parser("remove", help="Remove a tap")
    tap_rm.add_argument("name", help="Tap name to remove")

    skills_subparsers.add_parser("config", help="Interactive skill configuration \u2014 enable/disable individual skills")

    def cmd_skills(args):
        if getattr(args, 'skills_action', None) == 'config':
            from hermes_cli.skills_config import skills_command as skills_config_command
            skills_config_command(args)
        else:
            from hermes_cli.skills_hub import skills_command
            skills_command(args)

    skills_parser.set_defaults(func=cmd_skills)

    # ==================================================================
    # plugins command
    # ==================================================================
    plugins_parser = subparsers.add_parser(
        "plugins",
        help="Manage plugins \u2014 install, update, remove, list",
        description="Install plugins from Git repositories, update, remove, or list them.",
    )
    plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_action")

    plugins_install = plugins_subparsers.add_parser(
        "install", help="Install a plugin from a Git URL or owner/repo"
    )
    plugins_install.add_argument(
        "identifier",
        help="Git URL or owner/repo shorthand (e.g. anpicasso/hermes-plugin-chrome-profiles)",
    )
    plugins_install.add_argument(
        "--force", "-f", action="store_true",
        help="Remove existing plugin and reinstall",
    )

    plugins_update = plugins_subparsers.add_parser(
        "update", help="Pull latest changes for an installed plugin"
    )
    plugins_update.add_argument("name", help="Plugin name to update")

    plugins_remove = plugins_subparsers.add_parser(
        "remove", aliases=["rm", "uninstall"], help="Remove an installed plugin"
    )
    plugins_remove.add_argument("name", help="Plugin directory name to remove")

    plugins_subparsers.add_parser("list", aliases=["ls"], help="List installed plugins")

    def cmd_plugins(args):
        from hermes_cli.plugins_cmd import plugins_command
        plugins_command(args)

    plugins_parser.set_defaults(func=cmd_plugins)

    # ==================================================================
    # honcho command
    # ==================================================================
    honcho_parser = subparsers.add_parser(
        "honcho",
        help="Manage Honcho AI memory integration",
        description=(
            "Honcho is a memory layer that persists across sessions.\n\n"
            "Each conversation is stored as a peer interaction in a workspace. "
            "Honcho builds a representation of the user over time \u2014 conclusions, "
            "patterns, context \u2014 and surfaces the relevant slice at the start of "
            "each turn so Hermes knows who you are without you having to repeat yourself.\n\n"
            "Modes: hybrid (Honcho + local MEMORY.md), honcho (Honcho only), "
            "local (MEMORY.md only). Write frequency is configurable so memory "
            "writes never block the response."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    honcho_subparsers = honcho_parser.add_subparsers(dest="honcho_command")

    honcho_subparsers.add_parser("setup", help="Interactive setup wizard for Honcho integration")
    honcho_subparsers.add_parser("status", help="Show current Honcho config and connection status")
    honcho_subparsers.add_parser("sessions", help="List known Honcho session mappings")

    honcho_map = honcho_subparsers.add_parser(
        "map", help="Map current directory to a Honcho session name (no arg = list mappings)"
    )
    honcho_map.add_argument(
        "session_name", nargs="?", default=None,
        help="Session name to associate with this directory. Omit to list current mappings.",
    )

    honcho_peer = honcho_subparsers.add_parser(
        "peer", help="Show or update peer names and dialectic reasoning level"
    )
    honcho_peer.add_argument("--user", metavar="NAME", help="Set user peer name")
    honcho_peer.add_argument("--ai", metavar="NAME", help="Set AI peer name")
    honcho_peer.add_argument(
        "--reasoning",
        metavar="LEVEL",
        choices=("minimal", "low", "medium", "high", "max"),
        help="Set default dialectic reasoning level (minimal/low/medium/high/max)",
    )

    honcho_mode = honcho_subparsers.add_parser(
        "mode", help="Show or set memory mode (hybrid/honcho/local)"
    )
    honcho_mode.add_argument(
        "mode", nargs="?", metavar="MODE",
        choices=("hybrid", "honcho", "local"),
        help="Memory mode to set (hybrid/honcho/local). Omit to show current.",
    )

    honcho_tokens = honcho_subparsers.add_parser(
        "tokens", help="Show or set token budget for context and dialectic"
    )
    honcho_tokens.add_argument(
        "--context", type=int, metavar="N",
        help="Max tokens Honcho returns from session.context() per turn",
    )
    honcho_tokens.add_argument(
        "--dialectic", type=int, metavar="N",
        help="Max chars of dialectic result to inject into system prompt",
    )

    honcho_identity = honcho_subparsers.add_parser(
        "identity", help="Seed or show the AI peer's Honcho identity representation"
    )
    honcho_identity.add_argument(
        "file", nargs="?", default=None,
        help="Path to file to seed from (e.g. SOUL.md). Omit to show usage.",
    )
    honcho_identity.add_argument(
        "--show", action="store_true",
        help="Show current AI peer representation from Honcho",
    )

    honcho_subparsers.add_parser(
        "migrate",
        help="Step-by-step migration guide from openclaw-honcho to Hermes Honcho",
    )

    def cmd_honcho(args):
        from honcho_integration.cli import honcho_command
        honcho_command(args)

    honcho_parser.set_defaults(func=cmd_honcho)

    # ==================================================================
    # tools command
    # ==================================================================
    tools_parser = subparsers.add_parser(
        "tools",
        help="Configure which tools are enabled per platform",
        description=(
            "Enable, disable, or list tools for CLI, Telegram, Discord, etc.\n\n"
            "Built-in toolsets use plain names (e.g. web, memory).\n"
            "MCP tools use server:tool notation (e.g. github:create_issue).\n\n"
            "Run 'hermes tools' with no subcommand for the interactive configuration UI."
        ),
    )
    tools_parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of enabled tools per platform and exit"
    )
    tools_sub = tools_parser.add_subparsers(dest="tools_action")

    tools_list_p = tools_sub.add_parser(
        "list",
        help="Show all tools and their enabled/disabled status",
    )
    tools_list_p.add_argument(
        "--platform", default="cli",
        help="Platform to show (default: cli)",
    )

    tools_disable_p = tools_sub.add_parser(
        "disable",
        help="Disable toolsets or MCP tools",
    )
    tools_disable_p.add_argument(
        "names", nargs="+", metavar="NAME",
        help="Toolset name (e.g. web) or MCP tool in server:tool form",
    )
    tools_disable_p.add_argument(
        "--platform", default="cli",
        help="Platform to apply to (default: cli)",
    )

    tools_enable_p = tools_sub.add_parser(
        "enable",
        help="Enable toolsets or MCP tools",
    )
    tools_enable_p.add_argument(
        "names", nargs="+", metavar="NAME",
        help="Toolset name or MCP tool in server:tool form",
    )
    tools_enable_p.add_argument(
        "--platform", default="cli",
        help="Platform to apply to (default: cli)",
    )

    def cmd_tools(args):
        action = getattr(args, "tools_action", None)
        if action in ("list", "disable", "enable"):
            from hermes_cli.tools_config import tools_disable_enable_command
            tools_disable_enable_command(args)
        else:
            from hermes_cli.tools_config import tools_command
            tools_command(args)

    tools_parser.set_defaults(func=cmd_tools)

    # ==================================================================
    # mcp command
    # ==================================================================
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="Manage MCP server connections",
        description=(
            "Add, remove, list, test, and configure MCP server connections.\n\n"
            "MCP servers provide additional tools via the Model Context Protocol.\n"
            "Use 'hermes mcp add' to connect to a new server with interactive\n"
            "tool discovery. Run 'hermes mcp' with no subcommand to list servers."
        ),
    )
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_action")

    mcp_add_p = mcp_sub.add_parser("add", help="Add an MCP server (discovery-first install)")
    mcp_add_p.add_argument("name", help="Server name (used as config key)")
    mcp_add_p.add_argument("--url", help="HTTP/SSE endpoint URL")
    mcp_add_p.add_argument("--command", help="Stdio command (e.g. npx)")
    mcp_add_p.add_argument("--args", nargs="*", default=[], help="Arguments for stdio command")
    mcp_add_p.add_argument("--auth", choices=["oauth", "header"], help="Auth method")

    mcp_rm_p = mcp_sub.add_parser("remove", aliases=["rm"], help="Remove an MCP server")
    mcp_rm_p.add_argument("name", help="Server name to remove")

    mcp_sub.add_parser("list", aliases=["ls"], help="List configured MCP servers")

    mcp_test_p = mcp_sub.add_parser("test", help="Test MCP server connection")
    mcp_test_p.add_argument("name", help="Server name to test")

    mcp_cfg_p = mcp_sub.add_parser("configure", aliases=["config"], help="Toggle tool selection")
    mcp_cfg_p.add_argument("name", help="Server name to configure")

    def cmd_mcp(args):
        from hermes_cli.mcp_config import mcp_command
        mcp_command(args)

    mcp_parser.set_defaults(func=cmd_mcp)

    # ==================================================================
    # sessions command
    # ==================================================================
    sessions_parser = subparsers.add_parser(
        "sessions",
        help="Manage session history (list, rename, export, prune, delete)",
        description="View and manage the SQLite session store"
    )
    sessions_subparsers = sessions_parser.add_subparsers(dest="sessions_action")

    sessions_list = sessions_subparsers.add_parser("list", help="List recent sessions")
    sessions_list.add_argument("--source", help="Filter by source (cli, telegram, discord, etc.)")
    sessions_list.add_argument("--limit", type=int, default=20, help="Max sessions to show")

    sessions_export = sessions_subparsers.add_parser("export", help="Export sessions to a JSONL file")
    sessions_export.add_argument("output", help="Output JSONL file path")
    sessions_export.add_argument("--source", help="Filter by source")
    sessions_export.add_argument("--session-id", help="Export a specific session")

    sessions_delete = sessions_subparsers.add_parser("delete", help="Delete a specific session")
    sessions_delete.add_argument("session_id", help="Session ID to delete")
    sessions_delete.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    sessions_prune = sessions_subparsers.add_parser("prune", help="Delete old sessions")
    sessions_prune.add_argument("--older-than", type=int, default=90, help="Delete sessions older than N days (default: 90)")
    sessions_prune.add_argument("--source", help="Only prune sessions from this source")
    sessions_prune.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    sessions_subparsers.add_parser("stats", help="Show session store statistics")

    sessions_rename = sessions_subparsers.add_parser("rename", help="Set or change a session's title")
    sessions_rename.add_argument("session_id", help="Session ID to rename")
    sessions_rename.add_argument("title", nargs="+", help="New title for the session")

    sessions_browse = sessions_subparsers.add_parser(
        "browse",
        help="Interactive session picker \u2014 browse, search, and resume sessions",
    )
    sessions_browse.add_argument("--source", help="Filter by source (cli, telegram, discord, etc.)")
    sessions_browse.add_argument("--limit", type=int, default=50, help="Max sessions to load (default: 50)")

    def cmd_sessions(args):
        import json as _json
        try:
            from hermes_state import SessionDB
            db = SessionDB()
        except Exception as e:
            print(f"Error: Could not open session database: {e}")
            return

        action = args.sessions_action

        if action == "list":
            sessions = db.list_sessions_rich(source=args.source, limit=args.limit)
            if not sessions:
                print("No sessions found.")
                return
            from hermes_cli.main import _relative_time
            has_titles = any(s.get("title") for s in sessions)
            if has_titles:
                print(f"{'Title':<32} {'Preview':<40} {'Last Active':<13} {'ID'}")
                print("\u2500" * 110)
            else:
                print(f"{'Preview':<50} {'Last Active':<13} {'Src':<6} {'ID'}")
                print("\u2500" * 95)
            for s in sessions:
                last_active = _relative_time(s.get("last_active"))
                preview = s.get("preview", "")[:38] if has_titles else s.get("preview", "")[:48]
                if has_titles:
                    title = (s.get("title") or "\u2014")[:30]
                    sid = s["id"]
                    print(f"{title:<32} {preview:<40} {last_active:<13} {sid}")
                else:
                    sid = s["id"]
                    print(f"{preview:<50} {last_active:<13} {s['source']:<6} {sid}")

        elif action == "export":
            if args.session_id:
                resolved_session_id = db.resolve_session_id(args.session_id)
                if not resolved_session_id:
                    print(f"Session '{args.session_id}' not found.")
                    return
                data = db.export_session(resolved_session_id)
                if not data:
                    print(f"Session '{args.session_id}' not found.")
                    return
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(_json.dumps(data, ensure_ascii=False) + "\n")
                print(f"Exported 1 session to {args.output}")
            else:
                sessions = db.export_all(source=args.source)
                with open(args.output, "w", encoding="utf-8") as f:
                    for s in sessions:
                        f.write(_json.dumps(s, ensure_ascii=False) + "\n")
                print(f"Exported {len(sessions)} sessions to {args.output}")

        elif action == "delete":
            resolved_session_id = db.resolve_session_id(args.session_id)
            if not resolved_session_id:
                print(f"Session '{args.session_id}' not found.")
                return
            if not args.yes:
                confirm = input(f"Delete session '{resolved_session_id}' and all its messages? [y/N] ")
                if confirm.lower() not in ("y", "yes"):
                    print("Cancelled.")
                    return
            if db.delete_session(resolved_session_id):
                print(f"Deleted session '{resolved_session_id}'.")
            else:
                print(f"Session '{args.session_id}' not found.")

        elif action == "prune":
            days = args.older_than
            source_msg = f" from '{args.source}'" if args.source else ""
            if not args.yes:
                confirm = input(f"Delete all ended sessions older than {days} days{source_msg}? [y/N] ")
                if confirm.lower() not in ("y", "yes"):
                    print("Cancelled.")
                    return
            count = db.prune_sessions(older_than_days=days, source=args.source)
            print(f"Pruned {count} session(s).")

        elif action == "rename":
            resolved_session_id = db.resolve_session_id(args.session_id)
            if not resolved_session_id:
                print(f"Session '{args.session_id}' not found.")
                return
            title = " ".join(args.title)
            try:
                if db.set_session_title(resolved_session_id, title):
                    print(f"Session '{resolved_session_id}' renamed to: {title}")
                else:
                    print(f"Session '{args.session_id}' not found.")
            except ValueError as e:
                print(f"Error: {e}")

        elif action == "browse":
            limit = getattr(args, "limit", 50) or 50
            source = getattr(args, "source", None)
            sessions = db.list_sessions_rich(source=source, limit=limit)
            db.close()
            if not sessions:
                print("No sessions found.")
                return

            from hermes_cli.main import _session_browse_picker
            selected_id = _session_browse_picker(sessions)
            if not selected_id:
                print("Cancelled.")
                return

            print(f"Resuming session: {selected_id}")
            import shutil
            hermes_bin = shutil.which("hermes")
            if hermes_bin:
                os.execvp(hermes_bin, ["hermes", "--resume", selected_id])
            else:
                os.execvp(
                    sys.executable,
                    [sys.executable, "-m", "hermes_cli.main", "--resume", selected_id],
                )
            return

        elif action == "stats":
            total = db.session_count()
            msgs = db.message_count()
            print(f"Total sessions: {total}")
            print(f"Total messages: {msgs}")
            for src in ["cli", "telegram", "discord", "whatsapp", "slack"]:
                c = db.session_count(source=src)
                if c > 0:
                    print(f"  {src}: {c} sessions")
            db_path = db.db_path
            if db_path.exists():
                size_mb = os.path.getsize(db_path) / (1024 * 1024)
                print(f"Database size: {size_mb:.1f} MB")

        else:
            sessions_parser.print_help()

        db.close()

    sessions_parser.set_defaults(func=cmd_sessions)

    # ==================================================================
    # insights command
    # ==================================================================
    insights_parser = subparsers.add_parser(
        "insights",
        help="Show usage insights and analytics",
        description="Analyze session history to show token usage, costs, tool patterns, and activity trends"
    )
    insights_parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    insights_parser.add_argument("--source", help="Filter by platform (cli, telegram, discord, etc.)")

    def cmd_insights(args):
        try:
            from hermes_state import SessionDB
            from agent.insights import InsightsEngine

            db = SessionDB()
            engine = InsightsEngine(db)
            report = engine.generate(days=args.days, source=args.source)
            print(engine.format_terminal(report))
            db.close()
        except Exception as e:
            print(f"Error generating insights: {e}")

    insights_parser.set_defaults(func=cmd_insights)

    # ==================================================================
    # claw command (OpenClaw migration)
    # ==================================================================
    claw_parser = subparsers.add_parser(
        "claw",
        help="OpenClaw migration tools",
        description="Migrate settings, memories, skills, and API keys from OpenClaw to Hermes"
    )
    claw_subparsers = claw_parser.add_subparsers(dest="claw_action")

    claw_migrate = claw_subparsers.add_parser(
        "migrate",
        help="Migrate from OpenClaw to Hermes",
        description="Import settings, memories, skills, and API keys from an OpenClaw installation"
    )
    claw_migrate.add_argument("--source", help="Path to OpenClaw directory (default: ~/.openclaw)")
    claw_migrate.add_argument("--dry-run", action="store_true", help="Preview what would be migrated without making changes")
    claw_migrate.add_argument("--preset", choices=["user-data", "full"], default="full", help="Migration preset (default: full). 'user-data' excludes secrets")
    claw_migrate.add_argument("--overwrite", action="store_true", help="Overwrite existing files (default: skip conflicts)")
    claw_migrate.add_argument("--migrate-secrets", action="store_true", help="Include allowlisted secrets (TELEGRAM_BOT_TOKEN, API keys, etc.)")
    claw_migrate.add_argument("--workspace-target", help="Absolute path to copy workspace instructions into")
    claw_migrate.add_argument("--skill-conflict", choices=["skip", "overwrite", "rename"], default="skip", help="How to handle skill name conflicts (default: skip)")
    claw_migrate.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")

    def cmd_claw(args):
        from hermes_cli.claw import claw_command
        claw_command(args)

    claw_parser.set_defaults(func=cmd_claw)

    # ==================================================================
    # version command
    # ==================================================================
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information"
    )
    version_parser.set_defaults(func=_lazy_cmd_version)

    # ==================================================================
    # update command
    # ==================================================================
    update_parser = subparsers.add_parser(
        "update",
        help="Update Hermes Agent to the latest version",
        description="Pull the latest changes from git and reinstall dependencies"
    )
    update_parser.set_defaults(func=_lazy_cmd_update)

    # ==================================================================
    # uninstall command
    # ==================================================================
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="Uninstall Hermes Agent",
        description="Remove Hermes Agent from your system. Can keep configs/data for reinstall."
    )
    uninstall_parser.add_argument(
        "--full",
        action="store_true",
        help="Full uninstall - remove everything including configs and data"
    )
    uninstall_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompts"
    )
    uninstall_parser.set_defaults(func=_lazy_cmd_uninstall)

    # ==================================================================
    # acp command
    # ==================================================================
    acp_parser = subparsers.add_parser(
        "acp",
        help="Run Hermes Agent as an ACP (Agent Client Protocol) server",
        description="Start Hermes Agent in ACP mode for editor integration (VS Code, Zed, JetBrains)",
    )

    def cmd_acp(args):
        try:
            from acp_adapter.entry import main as acp_main
            acp_main()
        except ImportError:
            print("ACP dependencies not installed.")
            print("Install them with:  pip install -e '.[acp]'")
            sys.exit(1)

    acp_parser.set_defaults(func=cmd_acp)

    # ==================================================================
    # completion command
    # ==================================================================
    completion_parser = subparsers.add_parser(
        "completion",
        help="Generate shell completion script",
        description=(
            "Output a completion script for your shell.\n\n"
            "Usage:\n"
            "  eval \"$(hermes completion zsh)\"   # add to ~/.zshrc\n"
            "  eval \"$(hermes completion bash)\"  # add to ~/.bashrc"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    completion_parser.add_argument(
        "shell",
        choices=["zsh", "bash"],
        help="Shell type to generate completions for",
    )

    def cmd_completion(args):
        try:
            import argcomplete  # noqa: F401
        except ImportError:
            print(
                "argcomplete is required for shell completion.\n"
                "Install it with:  pip install 'hermes-agent[completion]'",
                file=sys.stderr,
            )
            sys.exit(1)

        if args.shell == "zsh":
            print(
                '#compdef hermes\n'
                '# Zsh completion for Hermes Agent (generated by hermes completion zsh)\n'
                'autoload -U bashcompinit && bashcompinit\n'
                'eval "$(register-python-argcomplete hermes)"'
            )
        elif args.shell == "bash":
            print(
                '# Bash completion for Hermes Agent (generated by hermes completion bash)\n'
                'eval "$(register-python-argcomplete hermes)"'
            )

    completion_parser.set_defaults(func=cmd_completion)

    return parser
