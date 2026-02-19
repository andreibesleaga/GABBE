import os
import re
import time
from pathlib import Path
from datetime import datetime
from .database import get_db
from .config import PROJECT_ROOT, Colors, TASKS_FILE

# TASKS_FILE is defined in config or here
TASKS_FILE = PROJECT_ROOT / "TASKS.md"

def parse_markdown_tasks(content):
    """Parse TASKS.md content into a list of dicts."""
    tasks = []
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith("- ["):
            match = re.match(r'- \[(.)\] (.*)', line.strip())
            if match:
                char = match.group(1)
                title = match.group(2)
                
                status = 'TODO'
                if char.lower() == 'x':
                    status = 'DONE'
                elif char == '/':
                    status = 'IN_PROGRESS'
                
                tasks.append({'title': title.strip(), 'status': status})
    return tasks

def generate_markdown_tasks(tasks):
    """Generate TASKS.md content from DB tasks."""
    lines = ["# Project Tasks", ""]
    for task in tasks:
        char = ' '
        if task['status'] == 'DONE':
            char = 'x'
        elif task['status'] == 'IN_PROGRESS':
            char = '/'
        lines.append(f"- [{char}] {task['title']}")
    return "\n".join(lines) + "\n"

def get_db_timestamp(c):
    """Get the latest update timestamp from DB."""
    c.execute("SELECT MAX(updated_at) FROM tasks")
    res = c.fetchone()
    if res and res[0]:
        # SQLite stores as 'YYYY-MM-DD HH:MM:SS' usually
        try:
            dt = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
            return dt.timestamp()
        except ValueError:
            return 0
    return 0

def sync_tasks():
    """Bidirectional sync for TASKS.md based on timestamps."""
    print(f"{Colors.HEADER}🔄 Syncing Tasks...{Colors.ENDC}")
    conn = get_db()
    c = conn.cursor()
    
    # Check File stats
    file_mtime = 0
    if TASKS_FILE.exists():
        file_mtime = TASKS_FILE.stat().st_mtime
    
    # Check DB stats
    db_mtime = get_db_timestamp(c)
    
    c.execute("SELECT count(*) FROM tasks")
    db_count = c.fetchone()[0]
    
    # Logic
    if db_count == 0 and TASKS_FILE.exists():
        print(f"  {Colors.BLUE}Bootstrap: Importing from TASKS.md{Colors.ENDC}")
        import_from_md(c, TASKS_FILE.read_text())
        conn.commit()
        
    elif not TASKS_FILE.exists() and db_count > 0:
        print(f"  {Colors.BLUE}Bootstrap: Exporting to TASKS.md{Colors.ENDC}")
        export_to_md(c)
        
    elif file_mtime > db_mtime:
        print(f"  {Colors.YELLOW}File is newer ({datetime.fromtimestamp(file_mtime)} vs {datetime.fromtimestamp(db_mtime)}){Colors.ENDC}")
        print(f"  {Colors.BLUE}Importing changes from TASKS.md...{Colors.ENDC}")
        # Identify changes? For now, we clear and re-import to be safe/simple
        # A real implementation would diff by ID/Title
        c.execute("DELETE FROM tasks") 
        import_from_md(c, TASKS_FILE.read_text())
        conn.commit()
    
    elif db_mtime > file_mtime:
        print(f"  {Colors.YELLOW}DB is newer ({datetime.fromtimestamp(db_mtime)} vs {datetime.fromtimestamp(file_mtime)}){Colors.ENDC}")
        print(f"  {Colors.BLUE}Exporting changes to TASKS.md...{Colors.ENDC}")
        export_to_md(c)
        
    else:
        print(f"  {Colors.GREEN}Already in sync.{Colors.ENDC}")

    conn.close()

def import_from_md(c, content):
    tasks = parse_markdown_tasks(content)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for t in tasks:
        c.execute("INSERT INTO tasks (title, status, updated_at) VALUES (?, ?, ?)", 
                  (t['title'], t['status'], now))
    print(f"  {Colors.GREEN}✓ Imported {len(tasks)} tasks.{Colors.ENDC}")
    
def export_to_md(c):
    c.execute("SELECT * FROM tasks ORDER BY id")
    db_tasks = c.fetchall()
    content = generate_markdown_tasks(db_tasks)
    TASKS_FILE.write_text(content)
    # Touch file to match DB time (or slightly newer to avoid ping-pong)?
    # Actually, we want file mtime to be NOW so next check handles it correctly
    print(f"  {Colors.GREEN}✓ Exported {len(db_tasks)} tasks.{Colors.ENDC}")
