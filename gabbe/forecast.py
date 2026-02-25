import sqlite3
from .config import Colors
from .database import get_db

def run_forecast():
    """Evaluate done vs remaining work, and forecast remaining budget costs based on historical run data."""
    print(f"{Colors.HEADER}📈 GABBE Strategic Forecast{Colors.ENDC}")
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 1. Active Run Costs
        cursor.execute("SELECT SUM(total_cost_usd), SUM(total_tokens_used) FROM runs")
        row = cursor.fetchone()
        total_cost = row[0] or 0.0
        total_tokens = row[1] or 0

        # 2. Task Completion Metrics
        cursor.execute("SELECT status, count(*) FROM tasks GROUP BY status")
        stats = {r['status']: r['count(*)'] for r in cursor.fetchall()}
        done = stats.get('DONE', 0)
        in_progress = stats.get('IN_PROGRESS', 0)
        todo = stats.get('TODO', 0)
        remaining = in_progress + todo

        print(f"  {Colors.CYAN}Total spent so far:{Colors.ENDC} ${total_cost:.4f} ({total_tokens} tokens)")
        print(f"  {Colors.CYAN}Tasks:{Colors.ENDC} {done} DONE | {in_progress} IN_PROGRESS | {todo} TODO")

        if done == 0:
            # No completed tasks yet — cannot derive a meaningful per-task cost.
            print(f"  {Colors.YELLOW}No completed tasks yet — insufficient data for cost projection.{Colors.ENDC}")
            avg_cost_per_task = 0.0
            avg_tokens_per_task = 0
            projected_remaining_cost = 0.0
            projected_remaining_tokens = 0
        else:
            avg_cost_per_task = total_cost / done
            avg_tokens_per_task = total_tokens / done
            projected_remaining_cost = avg_cost_per_task * remaining
            projected_remaining_tokens = int(avg_tokens_per_task * remaining)
            print(f"  {Colors.CYAN}Average cost per completed task:{Colors.ENDC} ${avg_cost_per_task:.4f}")
            print(f"  {Colors.CYAN}Projected remaining cost:{Colors.ENDC} ${projected_remaining_cost:.4f} ({projected_remaining_tokens} tokens)")

        # Snapshot this forecast — run_id is a fixed sentinel for standalone forecast runs.
        cursor.execute("""
            INSERT INTO forecast_snapshots (run_id, step, projected_tokens, projected_cost, current_error_rate)
            VALUES (?, ?, ?, ?, ?)
        """, ("forecast_cmd", 0, projected_remaining_tokens, projected_remaining_cost, 0.0))
        conn.commit()

    except sqlite3.Error as e:
        print(f"  {Colors.FAIL}Database Error:{Colors.ENDC} {e}")
    except Exception as e:
        print(f"  {Colors.FAIL}Unexpected Error:{Colors.ENDC} {e}")
    finally:
        if conn:
            conn.close()
