# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .config import LOG_LEVEL, Colors
from .database import init_db


def _resolve_install_target(args: argparse.Namespace) -> Path:
    """Resolve the install target: --dir > --global > project (cwd)."""
    import os

    if getattr(args, "dir", None):
        return Path(args.dir).resolve()
    if getattr(args, "global_scope", False):
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        return Path(base) / "gabbe"
    return Path.cwd()


def main() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}GABBE CLI (experimental) - Agentic Engineering Platform{Colors.ENDC}",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging and full stack traces",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- COMMAND: init ---
    subparsers.add_parser("init", help="Initialize GABBE in the current directory")

    # --- COMMAND: db ---
    db_parser = subparsers.add_parser("db", help="Database management")
    db_parser.add_argument("--init", action="store_true", help="Initialize the database schema")

    # --- COMMAND: sync ---
    subparsers.add_parser("sync", help="Sync Markdown <-> SQLite")

    # --- COMMAND: verify ---
    verify_parser = subparsers.add_parser("verify", help="Run integrity checks")
    verify_parser.add_argument(
        "--chaos",
        action="store_true",
        help="Run fault-injection self-checks (fail-closed tools, hard-stop, escalation)",
    )

    # --- COMMAND: status ---
    subparsers.add_parser("status", help="Show project dashboard")

    # --- COMMAND: route ---
    route_parser = subparsers.add_parser("route", help="Cost-Effective Router")
    route_parser.add_argument("prompt", help="The prompt to analyze")

    # --- COMMAND: brain ---
    brain_parser = subparsers.add_parser("brain", help="Brain Mode Interface")
    brain_sub = brain_parser.add_subparsers(dest="brain_command")

    brain_sub.add_parser("activate", help="Run Active Inference Loop")
    evolve_p = brain_sub.add_parser("evolve", help="Run EPO")
    evolve_p.add_argument("--skill", required=True, help="Skill to optimize")
    brain_sub.add_parser("heal", help="Run Self-Healing")

    # --- COMMAND: serve-mcp ---
    subparsers.add_parser("serve-mcp", help="Run the zero-dependency JSON-RPC MCP Server")

    # --- COMMAND: forecast ---
    subparsers.add_parser("forecast", help="Strategic Forecast of Remaining Work and Budgets")

    # --- COMMAND: runs ---
    runs_parser = subparsers.add_parser("runs", help="List recent agent runs")
    runs_parser.add_argument(
        "--status",
        choices=["running", "completed", "error", "budget_exceeded", "escalated"],
        help="Filter by run status",
    )
    runs_parser.add_argument("--limit", type=int, default=20, help="Max rows to display")

    # --- COMMAND: audit ---
    audit_parser = subparsers.add_parser("audit", help="Display structured trace for a run")
    audit_parser.add_argument("run_id", help="Run ID to inspect")
    audit_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )

    # --- COMMAND: replay ---
    replay_parser = subparsers.add_parser("replay", help="Replay a past run from checkpoints")
    replay_parser.add_argument("run_id", help="Run ID to replay")
    replay_parser.add_argument(
        "--from-step", type=int, default=0, metavar="N", help="Start replay from step N"
    )

    # --- COMMAND: resume ---
    resume_parser = subparsers.add_parser("resume", help="Resume a paused/escalated run")
    resume_parser.add_argument("run_id", help="Run ID to resume")

    # --- COMMAND: registry ---
    registry_parser = subparsers.add_parser(
        "registry", help="Publish/import skills to/from universal registries"
    )
    registry_sub = registry_parser.add_subparsers(dest="registry_command")
    rpub = registry_sub.add_parser("publish", help="Export skills as a publish-ready bundle")
    rpub.add_argument("--out", default="dist/registry", help="Output bundle directory")
    radd = registry_sub.add_parser("add", help="Import a skill/bundle (validated, namespaced)")
    radd.add_argument("source", help="Local path, .tar.gz, or http(s) URL")
    radd.add_argument("--namespace", default="ext", help="Land under agents/skills/<namespace>/")
    radd.add_argument("--apply", action="store_true", help="Write imports (default: dry run)")

    # --- COMMAND: setup ---
    subparsers.add_parser("setup", help="Run the interactive install wizard (wire agents + skills)")

    # --- COMMAND: eval ---
    eval_parser = subparsers.add_parser(
        "eval", help="Run skill eval suites (deterministic self-check; --live scores via the model)"
    )
    eval_parser.add_argument(
        "--live",
        action="store_true",
        help="Score skill outputs against the model (nightly; needs GABBE_LIVE_LLM=1)",
    )
    eval_parser.add_argument("--out", help="Write the JSON scorecard to this path")

    # --- COMMAND: doctor ---
    subparsers.add_parser(
        "doctor", help="Auto-detect OS, runtimes, and agent clients; print an install report"
    )

    # --- COMMAND: uninstall ---
    uninstall_parser = subparsers.add_parser(
        "uninstall", help="Reverse a GABBE install from its manifest (restores backups)"
    )
    uninstall_parser.add_argument(
        "--agents", help="Comma-separated agents to deselect (default: all)"
    )
    uninstall_parser.add_argument(
        "--dry-run", action="store_true", help="Print the plan; change nothing"
    )
    uninstall_parser.add_argument(
        "--purge", action="store_true", help="Also remove the agents/ kit + .gabbe/"
    )
    uninstall_parser.add_argument(
        "--global", dest="global_scope", action="store_true", help="Target the global install"
    )
    uninstall_parser.add_argument("--dir", help="Target a custom install directory")

    # --- COMMAND: update ---
    update_parser = subparsers.add_parser(
        "update", help="Additively refresh kit files; prune orphans; preserve user files"
    )
    update_parser.add_argument(
        "--agents", help="Comma-separated agents to refresh (default: manifest set)"
    )
    update_parser.add_argument(
        "--global", dest="global_scope", action="store_true", help="Target the global install"
    )
    update_parser.add_argument("--dir", help="Target a custom install directory")

    # Parse arguments
    args = parser.parse_args()

    # --debug flag overrides GABBE_LOG_LEVEL to DEBUG
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # --- DISPATCH ---
    try:
        if args.command == "init":
            print(f"{Colors.HEADER}Initializing GABBE...{Colors.ENDC}")
            init_db()

        elif args.command == "db":
            if args.init:
                init_db()
            else:
                db_parser.print_help()

        elif args.command == "sync":
            from .sync import sync_tasks

            sync_tasks()

        elif args.command == "verify":
            if getattr(args, "chaos", False):
                from .verify import run_chaos_checks

                if not run_chaos_checks():
                    sys.exit(1)
            else:
                from .verify import run_verification

                run_verification()

        elif args.command == "status":
            from .status import show_dashboard

            show_dashboard()

        elif args.command == "route":
            from .route import route_request

            route_request(args.prompt)

        elif args.command == "brain":
            from .brain import activate_brain, evolve_prompts, run_healer

            if args.brain_command == "activate":
                activate_brain()
            elif args.brain_command == "evolve":
                evolve_prompts(args.skill)
            elif args.brain_command == "heal":
                run_healer()
            else:
                brain_parser.print_help()

        elif args.command == "serve-mcp":
            from .mcp_server import serve

            serve()

        elif args.command == "forecast":
            from .forecast import run_forecast

            run_forecast()

        elif args.command == "runs":
            from .database import get_db

            conn = get_db()
            try:
                query = "SELECT id, command, status, started_at, ended_at, total_cost_usd, initiator FROM runs"
                params = []
                if hasattr(args, "status") and args.status:
                    query += " WHERE status = ?"
                    params.append(args.status)
                query += " ORDER BY started_at DESC LIMIT ?"
                params.append(args.limit)
                rows = conn.execute(query, params).fetchall()
                if not rows:
                    print("No runs found.")
                else:
                    print(f"{'ID':<38} {'CMD':<20} {'STATUS':<16} {'STARTED':<22} {'COST':>8}")
                    print("-" * 108)
                    for r in rows:
                        cost = f"${r['total_cost_usd']:.4f}" if r["total_cost_usd"] else "$0.0000"
                        print(
                            f"{r['id']:<38} {(r['command'] or '')[:20]:<20} {(r['status'] or ''):<16} {(r['started_at'] or ''):<22} {cost:>8}"
                        )
            finally:
                conn.close()

        elif args.command == "audit":
            from .audit import AuditTracer
            from .database import get_db

            conn = get_db()
            tracer = AuditTracer(args.run_id, db_conn=conn)
            if args.format == "json":
                print(tracer.export_json(args.run_id))
            else:
                spans = tracer.get_run_trace(args.run_id)
                if not spans:
                    print(f"No audit spans found for run {args.run_id}")
                else:
                    print(
                        f"{'EVENT TYPE':<18} {'NODE':<25} {'DURATION(ms)':>14} {'COST(USD)':>12} {'STATUS':<10}"
                    )
                    print("-" * 82)
                    for s in spans:
                        dur = f"{s['duration_ms']:.2f}" if s["duration_ms"] else "N/A"
                        cost = f"${s['cost_usd']:.6f}" if s["cost_usd"] else "$0.000000"
                        print(
                            f"{(s['event_type'] or ''):<18} {(s['node_name'] or '')[:25]:<25} {dur:>14} {cost:>12} {(s['status'] or ''):<10}"
                        )
            conn.close()

        elif args.command == "replay":
            from .database import get_db
            from .replay import CheckpointStore, ReplayRunner

            conn = get_db()
            store = CheckpointStore(db_conn=conn)
            runner = ReplayRunner(store)
            from_step = getattr(args, "from_step", 0)
            steps = runner.replay(args.run_id, from_step=from_step)
            if not steps:
                print(f"No checkpoints to replay for run {args.run_id}")
            else:
                print(f"Replayed {len(steps)} steps for run {args.run_id}")
                for s in steps:
                    print(f"  Step {s['step']}: {s['node_name']} (policy: {s['policy_version']})")
            conn.close()

        elif args.command == "resume":
            from .database import get_db
            from .escalation import EscalationHandler

            conn = get_db()
            try:
                rows = conn.execute(
                    "SELECT * FROM pending_escalations WHERE run_id = ? AND status = 'pending' ORDER BY id",
                    (args.run_id,),
                ).fetchall()
                if not rows:
                    print(f"No pending escalations for run {args.run_id}")
                else:
                    handler = EscalationHandler(args.run_id, db_conn=conn)
                    for row in rows:
                        print(f"\n[Escalation #{row['id']}] Trigger: {row['trigger']}")
                        print(f"  Step: {row['step']}")
                        print(f"  Context: {row['context']}")
                        choice = input("  Action -> [a]pprove / [r]eject: ").strip().lower()
                        status = "approved" if choice == "a" else "rejected"
                        handler.resolve(row["id"], status)
                        print(f"  Marked as {status}.")
            finally:
                conn.close()

        elif args.command == "registry":
            import subprocess
            from pathlib import Path

            scripts_dir = Path(__file__).resolve().parent.parent / "scripts"

            def _run_script(name: str, extra: list[str]) -> None:
                script = scripts_dir / name
                if not script.exists():
                    print(
                        f"{Colors.WARNING}{name} not found (packaged install): run from a "
                        f"GABBE repo checkout to use registry commands.{Colors.ENDC}"
                    )
                    # Missing tooling is a failure for scripting/CI, not a silent success.
                    sys.exit(2)
                result = subprocess.run([sys.executable, str(script), *extra], check=False)
                # Propagate the child's exit code so failures don't look successful.
                if result.returncode != 0:
                    sys.exit(result.returncode)

            if args.registry_command == "publish":
                _run_script("registry_export.py", ["--out", args.out])
            elif args.registry_command == "add":
                extra = [args.source, "--namespace", args.namespace]
                if args.apply:
                    extra.append("--apply")
                _run_script("registry_import.py", extra)
            else:
                registry_parser.print_help()

        elif args.command == "setup":
            import subprocess
            from pathlib import Path

            init_script = Path(__file__).resolve().parent.parent / "scripts" / "init.py"
            if init_script.exists():
                result = subprocess.run([sys.executable, str(init_script)], check=False)
                # Propagate the wizard's exit code so failures don't look successful.
                if result.returncode != 0:
                    sys.exit(result.returncode)
            else:
                print(
                    f"{Colors.WARNING}Install wizard not found (packaged install): "
                    f"use 'npx gabbe-kit init' or the repo's scripts/init.py.{Colors.ENDC}"
                )
                sys.exit(2)

        elif args.command == "eval":
            from .evals import run_evals

            rc = run_evals(live=args.live, out=args.out)
            if rc != 0:
                sys.exit(rc)

        elif args.command == "doctor":
            from .doctor import run_doctor

            rc = run_doctor()
            if rc != 0:
                sys.exit(rc)

        elif args.command == "uninstall":
            from .installer import uninstall as _uninstall

            target = _resolve_install_target(args)
            agents = (
                [a.strip() for a in args.agents.split(",") if a.strip()] if args.agents else None
            )
            removed = _uninstall(target, agents=agents, dry_run=args.dry_run, purge=args.purge)
            verb = "Would remove" if args.dry_run else "Removed"
            print(f"{verb} {len(removed)} path(s) from {target}")

        elif args.command == "update":
            from pathlib import Path as _Path

            from .installer import update_kit

            source = _Path(__file__).resolve().parent.parent / "agents"
            if not source.exists():
                print(
                    f"{Colors.WARNING}Kit source not found (packaged install): run "
                    f"'npx gabbe-kit init' / 'gabbe setup' to refresh.{Colors.ENDC}"
                )
                sys.exit(2)
            target = _resolve_install_target(args)
            agents = (
                [a.strip() for a in args.agents.split(",") if a.strip()] if args.agents else None
            )
            manifest = update_kit(target, source, agents=agents)
            print(f"Updated kit at {target} ({len(manifest['entries'])} artifacts)")

        else:
            parser.print_help()

    except EnvironmentError as e:
        if args.debug:
            raise
        print(f"{Colors.FAIL}Configuration Error: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted.{Colors.ENDC}", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        if args.debug:
            raise
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
