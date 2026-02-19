import argparse
import sys
from .config import Colors
from .database import init_db

def main():
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}GABBE CLI - Agentic Engineering Platform{Colors.ENDC}",
        formatter_class=argparse.RawTextHelpFormatter
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

    # Parse arguments
    args = parser.parse_args()

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

        else:
            parser.print_help()

    except EnvironmentError as e:
        print(f"{Colors.FAIL}Configuration Error: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted.{Colors.ENDC}", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
