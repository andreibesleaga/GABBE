from .config import Colors, PROGRESS_BAR_LEN
from .database import get_db


def show_dashboard():
    """Render the CLI Dashboard."""
    conn = get_db()
    try:
        c = conn.cursor()

        # 1. Project Phase (read from project_state table)
        c.execute("SELECT value FROM project_state WHERE key = 'current_phase'")
        row = c.fetchone()
        phase = row["value"] if row else "—"

        # 2. Task Statistics
        c.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        stats = dict(c.fetchall())
        total = sum(stats.values())
        done = stats.get("DONE", 0)
        in_progress = stats.get("IN_PROGRESS", 0)
        todo = stats.get("TODO", 0)

        percent = int((done / total) * 100) if total > 0 else 0

        # Progress bar — percent ∈ [0,100] so filled ∈ [0, PROGRESS_BAR_LEN]
        filled = int(percent / 100 * PROGRESS_BAR_LEN)
        bar = "█" * filled + "-" * (PROGRESS_BAR_LEN - filled)

        # Render
        print(f"\n{Colors.HEADER}=== GABBE PROJECT DASHBOARD ==={Colors.ENDC}")
        print(f"Phase: {Colors.CYAN}{phase}{Colors.ENDC}")
        print(
            f"Tasks: {Colors.GREEN}{done} Done{Colors.ENDC} | {Colors.YELLOW}{in_progress} In Progress{Colors.ENDC} | {Colors.BLUE}{todo} Todo{Colors.ENDC}"
        )
        print(f"Progress: [{Colors.GREEN}{bar}{Colors.ENDC}] {percent}%")
        print(f"===============================\n")
    finally:
        conn.close()
