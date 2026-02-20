import os
import re
import tempfile
import hashlib
from datetime import datetime
from .database import get_db
from .config import Colors, TASKS_FILE
import logging

logger = logging.getLogger("gabbe.sync")

_MARKER_START = "<!-- GABBE:TASKS:START -->"
_MARKER_END = "<!-- GABBE:TASKS:END -->"


def parse_markdown_tasks(content):
    """Parse project/TASKS.md content into a list of dicts.

    Supports both legacy full-file parsing and new marker-based parsing.
    """
    lines_to_parse = content.split("\n")

    # If markers are present, only parse between them
    if _MARKER_START in content and _MARKER_END in content:
        try:
            start_idx = content.find(_MARKER_START) + len(_MARKER_START)
            end_idx = content.find(_MARKER_END)
            if start_idx < end_idx:
                section = content[start_idx:end_idx]
                lines_to_parse = section.split("\n")
                logger.debug(
                    "Found markers, parsing %d chars of marked content", len(section)
                )
        except Exception as e:
            logger.warning(
                "Failed to parse between markers, falling back to full file: %s", e
            )

    tasks = []
    for line in lines_to_parse:
        if line.strip().startswith("- ["):
            match = re.match(r"- \[(.)\] (.*)", line.strip())
            if match:
                char = match.group(1)
                title = match.group(2).strip()

                status = "TODO"
                if char.lower() == "x":
                    status = "DONE"
                elif char == "/":
                    status = "IN_PROGRESS"

                # Generate a content hash to detect changes
                content_hash = hashlib.md5(f"{title}|{status}".encode()).hexdigest()
                tasks.append({"title": title, "status": status, "hash": content_hash})
    return tasks


def _generate_task_lines(tasks):
    """Generate just the list of task lines."""
    lines = []
    for task in tasks:
        char = " "
        if task["status"] == "DONE":
            char = "x"
        elif task["status"] == "IN_PROGRESS":
            char = "/"
        lines.append(f"- [{char}] {task['title']}")
    return "\n".join(lines)


def generate_markdown_tasks(tasks):
    """Generate project/TASKS.md content from DB tasks (Legacy / Full overwrite)."""
    # This is kept for backward compatibility or if we decide to force overwrite
    lines = ["# Project Tasks", "", _MARKER_START]
    lines.append(_generate_task_lines(tasks))
    lines.append(_MARKER_END)
    lines.append("")
    return "\n".join(lines)


def _parse_db_timestamp(value):
    """Parse a SQLite datetime string to a Unix timestamp.

    Handles both 'YYYY-MM-DD HH:MM:SS' (SQLite default) and ISO-8601
    'YYYY-MM-DDTHH:MM:SS' by normalising the separator before fromisoformat().
    """
    if not value:
        return 0
    try:
        return datetime.fromisoformat(str(value).replace(" ", "T")).timestamp()
    except (ValueError, AttributeError):
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
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _calculate_state_hash(tasks):
    """Calculate a single hash for the entire list of tasks."""
    if not tasks:
        return "0"
    # Sort by title to ensure consistent ordering for hashing
    sorted_tasks = sorted(tasks, key=lambda x: x['title'])
    combined = "".join(t['hash'] for t in sorted_tasks)
    return hashlib.md5(combined.encode()).hexdigest()


def sync_tasks():
    """Bidirectional sync for project/TASKS.md based on content changes."""
    print(f"{Colors.HEADER}🔄 Syncing Tasks...{Colors.ENDC}")
    conn = get_db()
    try:
        c = conn.cursor()

        # Check existing data
        c.execute("SELECT title, status FROM tasks")
        db_rows = c.fetchall()
        db_tasks = []
        # sqlite3.Row supports dict-like ['col'] access; row_factory is set in get_db()
        for row in db_rows:
            title = row['title']
            status = row['status']
            content_hash = hashlib.md5(f"{title}|{status}".encode()).hexdigest()
            db_tasks.append({'title': title, 'status': status, 'hash': content_hash})

        file_exists = TASKS_FILE.exists()
        file_tasks = []
        if file_exists:
            content = TASKS_FILE.read_text(encoding="utf-8")
            file_tasks = parse_markdown_tasks(content)

        # 1. Check content equality first (Fast Path)
        if _calculate_state_hash(db_tasks) == _calculate_state_hash(file_tasks):
             print(f"  {Colors.GREEN}✓ Synchronized (No changes detected).{Colors.ENDC}")
             return

        # 2. Decide Sync Direction
        db_count = len(db_tasks)
        file_count = len(file_tasks)
        db_mtime = get_db_timestamp(c)
        file_mtime = TASKS_FILE.stat().st_mtime if file_exists else 0
        
        if db_count == 0 and file_count > 0:
             print(f"  {Colors.BLUE}Bootstrap: Importing from project/TASKS.md{Colors.ENDC}")
             import_from_md(c, file_tasks)
             conn.commit()

        elif file_count == 0 and db_count > 0:
             print(f"  {Colors.BLUE}Bootstrap: Exporting to project/TASKS.md{Colors.ENDC}")
             export_to_md(c)

        elif file_mtime >= db_mtime:
             # File is newer (or equal). Check for actual changes.
             print(f"  {Colors.BLUE}Checking project/TASKS.md for new updates...{Colors.ENDC}")
             import_from_md(c, file_tasks)
             conn.commit()
        
        else:
             # DB is newer
             print(f"  {Colors.BLUE}Exporting DB changes to project/TASKS.md...{Colors.ENDC}")
             export_to_md(c)

    finally:
        conn.close()


def import_from_md(c, tasks_or_content):
    if isinstance(tasks_or_content, str):
        tasks = parse_markdown_tasks(tasks_or_content)
    else:
        tasks = tasks_or_content
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = {"updated": 0, "inserted": 0, "skipped": 0}

    for t in tasks:
        # Check if task exists
        c.execute("SELECT id, title, status FROM tasks WHERE title = ?", (t["title"],))
        row = c.fetchone()

        if row:
            db_id, db_title, db_status = row
            # Calculate DB hash
            db_hash = hashlib.md5(f"{db_title}|{db_status}".encode()).hexdigest()

            if t["hash"] != db_hash:
                # Actual change detected
                c.execute(
                    "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                    (t["status"], now, db_id),
                )
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
        else:
            c.execute(
                "INSERT INTO tasks (title, status, updated_at) VALUES (?, ?, ?)",
                (t["title"], t["status"], now),
            )
            stats["inserted"] += 1

    print(
        f"  {Colors.GREEN}✓ Sync Complete: {stats['inserted']} new, {stats['updated']} updated, {stats['skipped']} unchanged.{Colors.ENDC}"
    )


def export_to_md(c):
    c.execute("SELECT * FROM tasks ORDER BY id")
    db_tasks = c.fetchall()

    new_task_lines = _generate_task_lines(db_tasks)

    # Default content for new file
    final_content = (
        f"# Project Tasks\n\n{_MARKER_START}\n{new_task_lines}\n{_MARKER_END}\n"
    )

    # Read existing if present to preserve custom content
    if TASKS_FILE.exists():
        try:
            content = TASKS_FILE.read_text(encoding="utf-8")
            if _MARKER_START in content and _MARKER_END in content:
                # Splicing logic
                start_idx = content.find(_MARKER_START) + len(_MARKER_START)
                end_idx = content.find(_MARKER_END)

                if start_idx < end_idx:
                    logger.debug("Splicing %d tasks into existing file", len(db_tasks))
                    final_content = (
                        content[:start_idx]
                        + "\n"
                        + new_task_lines
                        + "\n"
                        + content[end_idx:]
                    )
                else:
                    logger.warning(
                        "Markers found but malformed. Overwriting task section."
                    )
            else:
                # Legacy fallback: Try to preserve header/preamble
                first_task_idx = content.find("- [")
                if first_task_idx != -1:
                    logger.info(
                        "No markers found. Preserving preamble before first task."
                    )
                    preamble = content[:first_task_idx].rstrip()
                    final_content = f"{preamble}\n\n{_MARKER_START}\n{new_task_lines}\n{_MARKER_END}\n"
                else:
                    logger.info("No markers or tasks found. Appending to file.")
                    final_content = f"{content.rstrip()}\n\n{_MARKER_START}\n{new_task_lines}\n{_MARKER_END}\n"

        except Exception as e:
            logger.error("Error reading project/TASKS.md: %s", e)

    _atomic_write(TASKS_FILE, final_content)
    print(f"  {Colors.GREEN}✓ Exported {len(db_tasks)} tasks to project/TASKS.md{Colors.ENDC}")
