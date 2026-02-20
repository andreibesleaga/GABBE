import sqlite3
from .config import DB_PATH, GABBE_DIR, Colors

# Increment this whenever the schema changes.
SCHEMA_VERSION = 2


def _migrate(conn):
    """Apply pending schema migrations in order."""
    c = conn.cursor()
    # Prevent migration race conditions by locking the database immediately
    try:
        conn.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError:
        # If already in a transaction or locked, we proceed but log a warning if possible,
        # or we rely on the fact that this is usually the first call.
        pass

    c.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
    c.execute("SELECT version FROM schema_version")
    row = c.fetchone()
    current = row[0] if row else 0

    if current < 1:
        # v1: initial schema
        c.execute("""CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL UNIQUE,
                      status TEXT DEFAULT 'TODO',
                      tags TEXT,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE TABLE IF NOT EXISTS project_state
                     (key TEXT PRIMARY KEY,
                      value TEXT,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE TABLE IF NOT EXISTS events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      actor TEXT,
                      action TEXT,
                      message TEXT,
                      context_summary TEXT)""")

        c.execute("""CREATE TABLE IF NOT EXISTS genes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      skill_name TEXT,
                      prompt_content TEXT,
                      success_rate REAL DEFAULT 0.0,
                      generation INTEGER DEFAULT 0,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    if current < 2:
        # v2: ensure UNIQUE index on tasks.title (no-op if table was just created above)
        try:
            c.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title)"
            )
        except sqlite3.OperationalError as e:
            if "already exists" not in str(e).lower():
                raise

    # Upsert schema version
    if row:
        c.execute("UPDATE schema_version SET version = ?", (SCHEMA_VERSION,))
    else:
        c.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    conn.commit()


def init_db():
    """Initialize (or migrate) the SQLite database schema."""
    if not GABBE_DIR.exists():
        GABBE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}Created project directory{Colors.ENDC}")

    conn = sqlite3.connect(DB_PATH)
    try:
        _migrate(conn)
    finally:
        conn.close()
    print(f"{Colors.GREEN}✓ Database initialized at {DB_PATH}{Colors.ENDC}")


def get_db():
    """Return a database connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
