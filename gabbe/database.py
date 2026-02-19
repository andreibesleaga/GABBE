import sqlite3
import json
from datetime import datetime
from .config import DB_PATH, GABBE_DIR, Colors

def init_db():
    """Initialize the SQLite database schema."""
    if not GABBE_DIR.exists():
        GABBE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}Created .gabbe directory{Colors.ENDC}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Tasks Table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  status TEXT DEFAULT 'TODO',
                  tags TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # 2. Project State (Key-Value Store)
    c.execute('''CREATE TABLE IF NOT EXISTS project_state
                 (key TEXT PRIMARY KEY,
                  value TEXT,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # 3. Events (Episodic Logs)
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  actor TEXT,
                  action TEXT,
                  message TEXT,
                  context_summary TEXT)''')

    # 4. Genes (Evolutionary Prompts)
    c.execute('''CREATE TABLE IF NOT EXISTS genes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  skill_name TEXT,
                  prompt_content TEXT,
                  success_rate REAL DEFAULT 0.0,
                  generation INTEGER DEFAULT 0,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()
    print(f"{Colors.GREEN}✓ Database initialized at {DB_PATH}{Colors.ENDC}")

def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
