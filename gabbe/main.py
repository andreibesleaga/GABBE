import argparse
import logging
import sys
from .config import Colors, LOG_LEVEL
from .database import init_db
from . import __version__


def main():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}GABBE CLI (experimental) - Agentic Engineering Platform{Colors.ENDC}",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
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
    db_parser.add_argument(
        "--init", action="store_true", help="Initialize the database schema"
    )

    # --- COMMAND: sync ---
    subparsers.add_parser("sync", help="Sync Markdown <-> SQLite")

    # --- COMMAND: verify ---
    subparsers.add_parser("verify", help="Run integrity checks")

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
    replay_parser.add_argument("--from-step", type=int, default=0, metavar="N", help="Start replay from step N")

    # --- COMMAND: resume ---
    resume_parser = subparsers.add_parser("resume", help="Resume a paused/escalated run")
    resume_parser.add_argument("run_id", help="Run ID to resume")

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
                        cost = f"${r['total_cost_usd']:.4f}" if r['total_cost_usd'] else "$0.0000"
                        print(f"{r['id']:<38} {(r['command'] or '')[:20]:<20} {(r['status'] or ''):<16} {(r['started_at'] or ''):<22} {cost:>8}")
            finally:
                conn.close()

        elif args.command == "audit":
            from .database import get_db
            from .audit import AuditTracer
            conn = get_db()
            tracer = AuditTracer(args.run_id, db_conn=conn)
            if args.format == "json":
                print(tracer.export_json(args.run_id))
            else:
                spans = tracer.get_run_trace(args.run_id)
                if not spans:
                    print(f"No audit spans found for run {args.run_id}")
                else:
                    print(f"{'EVENT TYPE':<18} {'NODE':<25} {'DURATION(ms)':>14} {'COST(USD)':>12} {'STATUS':<10}")
                    print("-" * 82)
                    for s in spans:
                        dur = f"{s['duration_ms']:.2f}" if s['duration_ms'] else "N/A"
                        cost = f"${s['cost_usd']:.6f}" if s['cost_usd'] else "$0.000000"
                        print(f"{(s['event_type'] or ''):<18} {(s['node_name'] or '')[:25]:<25} {dur:>14} {cost:>12} {(s['status'] or ''):<10}")
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
                    (args.run_id,)
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
