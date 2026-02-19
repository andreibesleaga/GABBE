import os
import re
import tempfile
from pathlib import Path
from datetime import datetime
from .database import get_db
from .config import PROJECT_ROOT, Colors, TASKS_FILE


def parse_markdown_tasks(content):
    """Parse TASKS.md content into a list of dicts."""
    tasks = []
    for line in content.split('\n'):
        if line.strip().startswith("- ["):
            match = re.match(r'- \[(.)\] (.*)', line.strip())
            if match:
                char = match.group(1)
                title = match.group(2).strip()

                status = 'TODO'
                if char.lower() == 'x':
                    status = 'DONE'
                elif char == '/':
                    status = 'IN_PROGRESS'

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
    return "\n".join(lines) + "\n"


def _parse_db_timestamp(value):
    """Parse a SQLite datetime string to a Unix timestamp.

    Handles both 'YYYY-MM-DD HH:MM:SS' and ISO-8601 'YYYY-MM-DDTHH:MM:SS'
    variants that SQLite may return on different platforms.
    """
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).timestamp()
        except ValueError:
            continue
    return 0


def get_db_timestamp(c):
    """Get the latest update timestamp from DB."""
    c.execute("SELECT MAX(updated_at) FROM tasks")
    res = c.fetchone()
    if res and res[0]:
        return _parse_db_timestamp(res[0])
    return 0


def _atomic_write(path, content):
    """Write *content* to *path* atomically using a temp file + rename."""
    dir_ = path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_, prefix=".tmp_tasks_")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def sync_tasks():
    """Bidirectional sync for TASKS.md based on timestamps."""
    print(f"{Colors.HEADER}🔄 Syncing Tasks...{Colors.ENDC}")
    conn = get_db()
    try:
        c = conn.cursor()

        # Check File stats
        file_mtime = TASKS_FILE.stat().st_mtime if TASKS_FILE.exists() else 0

        # Check DB stats
        db_mtime = get_db_timestamp(c)

        c.execute("SELECT count(*) FROM tasks")
        db_count = c.fetchone()[0]

        # Bootstrap: DB empty and file exists → import
        if db_count == 0 and TASKS_FILE.exists():
            print(f"  {Colors.BLUE}Bootstrap: Importing from TASKS.md{Colors.ENDC}")
            import_from_md(c, TASKS_FILE.read_text())
            conn.commit()

        # Bootstrap: file missing and DB has data → export
        elif not TASKS_FILE.exists() and db_count > 0:
            print(f"  {Colors.BLUE}Bootstrap: Exporting to TASKS.md{Colors.ENDC}")
            export_to_md(c)

        # Both empty — nothing to do
        elif db_count == 0 and not TASKS_FILE.exists():
            print(f"  {Colors.GREEN}Nothing to sync (both empty).{Colors.ENDC}")

        # File newer → import
        elif file_mtime > db_mtime:
            print(f"  {Colors.YELLOW}File is newer ({datetime.fromtimestamp(file_mtime)} vs {datetime.fromtimestamp(db_mtime)}){Colors.ENDC}")
            print(f"  {Colors.BLUE}Importing changes from TASKS.md...{Colors.ENDC}")
            import_from_md(c, TASKS_FILE.read_text())
            conn.commit()

        # DB newer → export
        elif db_mtime > file_mtime:
            print(f"  {Colors.YELLOW}DB is newer ({datetime.fromtimestamp(db_mtime)} vs {datetime.fromtimestamp(file_mtime)}){Colors.ENDC}")
            print(f"  {Colors.BLUE}Exporting changes to TASKS.md...{Colors.ENDC}")
            export_to_md(c)

        else:
            print(f"  {Colors.GREEN}Already in sync.{Colors.ENDC}")
    finally:
        conn.close()


def import_from_md(c, content):
    tasks = parse_markdown_tasks(content)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = {"updated": 0, "inserted": 0}

    for t in tasks:
        # Upsert by title — relies on the UNIQUE(title) constraint in the schema
        c.execute("SELECT id FROM tasks WHERE title = ?", (t['title'],))
        row = c.fetchone()

        if row:
            c.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (t['status'], now, row[0])
            )
            stats["updated"] += 1
        else:
            c.execute(
                "INSERT INTO tasks (title, status, updated_at) VALUES (?, ?, ?)",
                (t['title'], t['status'], now)
            )
            stats["inserted"] += 1

    print(f"  {Colors.GREEN}✓ Sync Complete: {stats['inserted']} new, {stats['updated']} updated.{Colors.ENDC}")


def export_to_md(c):
    c.execute("SELECT * FROM tasks ORDER BY id")
    db_tasks = c.fetchall()
    content = generate_markdown_tasks(db_tasks)
    _atomic_write(TASKS_FILE, content)
    print(f"  {Colors.GREEN}✓ Exported {len(db_tasks)} tasks.{Colors.ENDC}")
