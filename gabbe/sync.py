import os
import re
from pathlib import Path
from datetime import datetime
from .database import get_db
from .config import PROJECT_ROOT, Colors

TASKS_FILE = PROJECT_ROOT / "TASKS.md"

def parse_markdown_tasks(content):
    """Parse TASKS.md content into a list of dicts."""
    tasks = []
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith("- ["):
            # Regex to capture status and title
            match = re.match(r'- \[(.)\] (.*)', line.strip())
            if match:
                char = match.group(1)
                title = match.group(2)
                
                status = 'TODO'
                if char == 'x' or char == 'X':
                    status = 'DONE'
                elif char == '/':
                    status = 'IN_PROGRESS'
                
                # Check for tags/metadata in comments <!-- id: 1 -->
                # For now, we just use title matching or strict ordering?
                # Ideally we need IDs. If no ID, generate one?
                # A simple approach for v1: Title matching
                
                tasks.append({'title': title, 'status': status})
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
    return "\n".join(lines)

def sync_tasks():
    """Bidirectional sync for TASKS.md."""
    conn = get_db()
    c = conn.cursor()
    
    # 1. Check file modification time
    file_mtime = 0
    if TASKS_FILE.exists():
        file_mtime = TASKS_FILE.stat().st_mtime
    
    # 2. Check last DB update
    # We'll fetch the max updated_at from tasks table
    c.execute("SELECT MAX(updated_at) FROM tasks")
    res = c.fetchone()
    db_mtime_str = res[0]
    
    db_mtime = 0
    if db_mtime_str:
         # Simplified: treat string TS as comparable or convert?
         # SQLite logs in UTC string usually.
         # For MVP, let's trust the "Source of Truth" argument or simple comparison.
         pass

    # STRATEGY: 
    # If DB is empty and File exists -> Import File
    # If File is missing and DB has tasks -> Export File
    # If both exist -> Merge? Or just win by timestamp?
    # For MVP: "Import if DB empty, else Export wins (Agent drives)" 
    # UNLESS we detect file is newer?
    
    # Let's do: Import from File if DB is empty (Boostrap)
    c.execute("SELECT count(*) FROM tasks")
    count = c.fetchone()[0]
    
    if count == 0 and TASKS_FILE.exists():
        print(f"{Colors.BLUE}Importing tasks from TASKS.md...{Colors.ENDC}")
        content = TASKS_FILE.read_text()
        tasks = parse_markdown_tasks(content)
        for t in tasks:
            c.execute("INSERT INTO tasks (title, status) VALUES (?, ?)", (t['title'], t['status']))
        conn.commit()
        print(f"{Colors.GREEN}Imported {len(tasks)} tasks.{Colors.ENDC}")
        
    elif count > 0:
        # Export DB to File (Enforce consistency)
        # TODO: This needs to be smarter (detect manual edits)
        # For now, let's overwrite to prove "Agent State -> File" flow
        print(f"{Colors.BLUE}Syncing DB -> TASKS.md...{Colors.ENDC}")
        c.execute("SELECT * FROM tasks ORDER BY id")
        db_tasks = c.fetchall()
        content = generate_markdown_tasks(db_tasks)
        TASKS_FILE.write_text(content)
        print(f"{Colors.GREEN}Updated TASKS.md{Colors.ENDC}")

    conn.close()
