import os
import re
import tempfile
from pathlib import Path
from datetime import datetime
from .database import get_db
from .config import PROJECT_ROOT, Colors, TASKS_FILE
import logging

logger = logging.getLogger("gabbe.sync")

_MARKER_START = "<!-- GABBE:TASKS:START -->"
_MARKER_END = "<!-- GABBE:TASKS:END -->"


def parse_markdown_tasks(content):
    """Parse TASKS.md content into a list of dicts.

    Supports both legacy full-file parsing and new marker-based parsing.
    """
    lines_to_parse = content.split('\n')
    
    # If markers are present, only parse between them
    if _MARKER_START in content and _MARKER_END in content:
        try:
            start_idx = content.find(_MARKER_START) + len(_MARKER_START)
            end_idx = content.find(_MARKER_END)
            if start_idx < end_idx:
                section = content[start_idx:end_idx]
                lines_to_parse = section.split('\n')
                logger.debug("Found markers, parsing %d chars of marked content", len(section))
        except Exception as e:
            logger.warning("Failed to parse between markers, falling back to full file: %s", e)

    tasks = []
    for line in lines_to_parse:
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


def _generate_task_lines(tasks):
    """Generate just the list of task lines."""
    lines = []
    for task in tasks:
        char = ' '
        if task['status'] == 'DONE':
            char = 'x'
        elif task['status'] == 'IN_PROGRESS':
            char = '/'
        lines.append(f"- [{char}] {task['title']}")
    return "\n".join(lines)


def generate_markdown_tasks(tasks):
    """Generate TASKS.md content from DB tasks (Legacy / Full overwrite)."""
    # This is kept for backward compatibility or if we decide to force overwrite
    lines = ["# Project Tasks", "", _MARKER_START]
    lines.append(_generate_task_lines(tasks))
    lines.append(_MARKER_END)
    lines.append("")
    return "\n".join(lines)


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
    
    new_task_lines = _generate_task_lines(db_tasks)
    
    # Default content for new file
    final_content = f"# Project Tasks\n\n{_MARKER_START}\n{new_task_lines}\n{_MARKER_END}\n"

    # Read existing if present to preserve custom content
    if TASKS_FILE.exists():
        try:
            content = TASKS_FILE.read_text(encoding='utf-8')
            if _MARKER_START in content and _MARKER_END in content:
                # Splicing logic
                start_idx = content.find(_MARKER_START) + len(_MARKER_START)
                end_idx = content.find(_MARKER_END)
                
                if start_idx < end_idx:
                    logger.debug("Splicing %d tasks into existing file", len(db_tasks))
                    final_content = content[:start_idx] + "\n" + new_task_lines + "\n" + content[end_idx:]
                else:
                    # Markers exist but order is wrong? Fallback to append or overwrite? 
                    # Let's overwrite safely to ensure consistency if file is corrupted
                    logger.warning("Markers found but malformed. Overwriting task section.")
            else:
                # File exists but no markers. Append or Prepend? 
                # Strategy: Wrap existing list? Or just append?
                # Best safer strategy: detailed below.
                # If we assume previous version was just a list, we might want to replace the list.
                # But to be safe against deleting notes, let's prepend the markers if it looks like a task file
                # or just overwrite if it was generated by us before.
                
                # For robust audit fix: detailed Logic #3 from Plan:
                # "Existing file without markers gets wrapped" -> This is hard if mixed content.
                # Simplified: Just overwrite if it looks like a purely generated file, 
                # BUT if user modified it, we might lose data.
                
                # Revised Strategy: If no markers, we rewrite the whole file with markers 
                # (Assuming old format). This is the risk we identified.
                # To minimize risk: We will attempt to identify the task list block?
                # Too complex. Let's stick to the Plan: "write header + markers + task list"
                # But let's verify if we can save header?
                # Legacy fallback: Try to preserve header/preamble
                # Find the first task item to determine start of the list
                first_task_idx = content.find("- [")
                if first_task_idx != -1:
                    logger.info("No markers found. Preserving preamble before first task.")
                    preamble = content[:first_task_idx].rstrip()
                    final_content = f"{preamble}\n\n{_MARKER_START}\n{new_task_lines}\n{_MARKER_END}\n"
                else:
                    # No tasks found? Append new list to existing content
                    logger.info("No markers or tasks found. Appending to file.")
                    final_content = f"{content.rstrip()}\n\n{_MARKER_START}\n{new_task_lines}\n{_MARKER_END}\n"
                
        except Exception as e:
            logger.error("Error reading TASKS.md: %s", e)

    _atomic_write(TASKS_FILE, final_content)
    print(f"  {Colors.GREEN}✓ Exported {len(db_tasks)} tasks.{Colors.ENDC}")
