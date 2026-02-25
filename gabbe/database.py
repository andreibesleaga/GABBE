import sqlite3
from .config import DB_PATH, GABBE_DIR, Colors

# Increment this whenever the schema changes.
SCHEMA_VERSION = 3


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
        # v2: UNIQUE index on tasks.title; IF NOT EXISTS makes this idempotent
        c.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title)"
        )

    if current < 3:
        # v3: MVA Platform Modules schema additions
        c.execute("""CREATE TABLE IF NOT EXISTS pricing_registry
                     (model_id TEXT PRIMARY KEY,
                      input_token_price REAL DEFAULT 0.0,
                      output_token_price REAL DEFAULT 0.0,
                      reasoning_token_price REAL DEFAULT 0.0,
                      cache_creation_price REAL DEFAULT 0.0,
                      cache_read_price REAL DEFAULT 0.0,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE TABLE IF NOT EXISTS runs
                     (id TEXT PRIMARY KEY,
                      command TEXT,
                      started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      ended_at DATETIME,
                      status TEXT,
                      stop_reason TEXT,
                      initiator TEXT,
                      agent_persona TEXT,
                      total_tokens_used INTEGER DEFAULT 0,
                      total_cost_usd REAL DEFAULT 0.0,
                      config_snapshot TEXT)""")

        c.execute("""CREATE TABLE IF NOT EXISTS audit_spans
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      span_id TEXT,
                      parent_span_id TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      event_type TEXT,
                      node_name TEXT,
                      input_data TEXT,
                      output_data TEXT,
                      reasoning_content TEXT,
                      model_name TEXT,
                      prompt_tokens INTEGER DEFAULT 0,
                      completion_tokens INTEGER DEFAULT 0,
                      reasoning_tokens INTEGER DEFAULT 0,
                      cache_hit_tokens INTEGER DEFAULT 0,
                      cost_usd REAL DEFAULT 0.0,
                      duration_ms REAL,
                      status TEXT,
                      metadata TEXT,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

        c.execute("CREATE INDEX IF NOT EXISTS idx_audit_spans_run_id ON audit_spans(run_id)")

        c.execute("""CREATE TABLE IF NOT EXISTS budget_snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      tokens_used INTEGER,
                      tool_calls_used INTEGER,
                      wall_time_sec REAL,
                      iterations INTEGER,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS checkpoints
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      node_name TEXT,
                      state_snapshot TEXT,
                      policy_version TEXT,
                      parent_checkpoint_id INTEGER,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id),
                      FOREIGN KEY(parent_checkpoint_id) REFERENCES checkpoints(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS pending_escalations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      trigger TEXT,
                      context TEXT,
                      status TEXT,
                      response TEXT,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      resolved_at DATETIME,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS forecast_snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      projected_tokens INTEGER,
                      projected_cost REAL,
                      current_error_rate REAL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id))""")

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
