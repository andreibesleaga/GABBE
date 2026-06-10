CREATE INDEX idx_audit_spans_run_id ON audit_spans(run_id);
CREATE UNIQUE INDEX idx_tasks_title ON tasks(title);
CREATE TABLE audit_spans
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
                      FOREIGN KEY(run_id) REFERENCES runs(id));
CREATE TABLE budget_snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      tokens_used INTEGER,
                      tool_calls_used INTEGER,
                      wall_time_sec REAL,
                      iterations INTEGER,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id));
CREATE TABLE checkpoints
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      node_name TEXT,
                      state_snapshot TEXT,
                      policy_version TEXT,
                      parent_checkpoint_id INTEGER,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id),
                      FOREIGN KEY(parent_checkpoint_id) REFERENCES checkpoints(id));
CREATE TABLE events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      actor TEXT,
                      action TEXT,
                      message TEXT,
                      context_summary TEXT);
CREATE TABLE forecast_snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      projected_tokens INTEGER,
                      projected_cost REAL,
                      current_error_rate REAL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(run_id) REFERENCES runs(id));
CREATE TABLE genes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      skill_name TEXT,
                      prompt_content TEXT,
                      success_rate REAL DEFAULT 0.0,
                      generation INTEGER DEFAULT 0,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE pending_escalations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      run_id TEXT,
                      step INTEGER,
                      trigger TEXT,
                      context TEXT,
                      status TEXT,
                      response TEXT,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      resolved_at DATETIME,
                      FOREIGN KEY(run_id) REFERENCES runs(id));
CREATE TABLE pricing_registry
                     (model_id TEXT PRIMARY KEY,
                      input_token_price REAL DEFAULT 0.0,
                      output_token_price REAL DEFAULT 0.0,
                      reasoning_token_price REAL DEFAULT 0.0,
                      cache_creation_price REAL DEFAULT 0.0,
                      cache_read_price REAL DEFAULT 0.0,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE project_state
                     (key TEXT PRIMARY KEY,
                      value TEXT,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE runs
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
                      config_snapshot TEXT);
CREATE TABLE schema_version (version INTEGER);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE tasks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL UNIQUE,
                      status TEXT DEFAULT 'TODO',
                      tags TEXT,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP);
