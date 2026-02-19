from .config import Colors
from .database import get_db

def show_dashboard():
    """Render the CLI Dashboard."""
    conn = get_db()
    c = conn.cursor()
    
    # 1. Project Phase
    # Mock data for now, real implementation reads from project_state table
    phase = "S04_TASKS" 
    
    # 2. Task Statistics
    c.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    stats = dict(c.fetchall())
    total = sum(stats.values())
    done = stats.get('DONE', 0)
    in_progress = stats.get('IN_PROGRESS', 0)
    todo = stats.get('TODO', 0)
    
    percent = 0
    if total > 0:
        percent = int((done / total) * 100)
        
    # Helpers for progress bar
    bar_len = 20
    filled = int(percent / 100 * bar_len)
    bar = "█" * filled + "-" * (bar_len - filled)
    
    # Render
    print(f"\n{Colors.HEADER}=== GABBE PROJECT DASHBOARD ==={Colors.ENDC}")
    print(f"Phase: {Colors.CYAN}{phase}{Colors.ENDC}")
    print(f"Tasks: {Colors.GREEN}{done} Done{Colors.ENDC} | {Colors.YELLOW}{in_progress} In Progress{Colors.ENDC} | {Colors.BLUE}{todo} Todo{Colors.ENDC}")
    print(f"Progress: [{Colors.GREEN}{bar}{Colors.ENDC}] {percent}%")
    print(f"===============================\n")

