from __future__ import annotations
import json
import logging
import uuid
import time
from .database import get_db
from .budget import Budget
from .hardstop import HardStop
from .audit import AuditTracer
from .gateway import ToolGateway
from .policy import PolicyEngine
from .escalation import EscalationHandler
from .replay import CheckpointStore

logger = logging.getLogger("gabbe.context")

class RunContext:
    def __init__(self, command: str, initiator: str = "cli", agent_persona: str | None = None, 
                 run_id: str | None = None, budget: Budget | None = None, hard_stop: HardStop | None = None, 
                 policy: PolicyEngine | None = None, gateway: ToolGateway | None = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.command = command
        self.initiator = initiator
        self.agent_persona = agent_persona
        
        self.budget = budget or Budget.from_config()
        self.hard_stop = hard_stop or HardStop()
        self.policy = policy or PolicyEngine.from_yaml()
        
        self.db_conn = get_db()
        self.tracer = AuditTracer(self.run_id, db_conn=self.db_conn)
        self.gateway = gateway or ToolGateway()
        self.escalation = EscalationHandler(self.run_id, db_conn=self.db_conn)
        self.checkpoints = CheckpointStore(db_conn=self.db_conn)

        self._start_time = time.monotonic()
        self._is_active = False

    def __enter__(self):
        try:
            cursor = self.db_conn.cursor()
            
            # Serialize the active limits as config snapshot
            config_snap = {
                "budget": {
                    "max_tokens": self.budget.max_tokens,
                    "max_cost_usd": self.budget.max_cost_usd,
                    "max_tool_calls": self.budget.max_tool_calls
                },
                "policy_version": self.policy.version
            }

            cursor.execute("""
                INSERT INTO runs 
                (id, command, status, initiator, agent_persona, config_snapshot)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.run_id, self.command, "running", self.initiator, 
                  self.agent_persona, json.dumps(config_snap)))
            self.db_conn.commit()
            self._is_active = True
        except Exception as e:
            logger.error(f"Failed to activate RunContext {self.run_id}: {e}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._is_active:
            return
            
        status = "completed"
        stop_reason = "success"
        
        if exc_type:
            status = "error"
            stop_reason = str(exc_val)
            # Differentiate specific exceptions
            if "BudgetExceeded" in str(exc_type):
                status = "budget_exceeded"
            elif "EscalationPaused" in str(exc_type):
                status = "escalated"

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                UPDATE runs 
                SET ended_at = CURRENT_TIMESTAMP, status = ?, stop_reason = ?, 
                    total_tokens_used = ?, total_cost_usd = ?
                WHERE id = ?
            """, (status, stop_reason, self.budget.tokens_used, self.budget.cost_usd, self.run_id))
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to finalize RunContext {self.run_id}: {e}")
            
        self.db_conn.close()

    @classmethod
    def from_config(cls, command: str = "brain activate", **kwargs):
        return cls(command=command, **kwargs)

    @classmethod
    def from_checkpoint(cls, checkpoint_id: int) -> "RunContext":
        """Reconstruct a RunContext from a saved checkpoint for replay."""
        db_conn = get_db()
        try:
            # Load the checkpoint row
            row = db_conn.execute(
                "SELECT * FROM checkpoints WHERE id = ?", (checkpoint_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"Checkpoint {checkpoint_id} not found")
            run_id = row["run_id"]

            # Load the original run's config snapshot to restore budget limits
            run_row = db_conn.execute(
                "SELECT * FROM runs WHERE id = ?", (run_id,)
            ).fetchone()
            budget = Budget.from_config()
            if run_row and run_row["config_snapshot"]:
                snap = json.loads(run_row["config_snapshot"])
                budget_snap = snap.get("budget", {})
                budget = Budget.from_dict(budget_snap)

            return cls(
                command=f"replay:{run_id}",
                initiator="replay",
                run_id=str(uuid.uuid4()),  # new run_id for the replay
                budget=budget,
            )
        finally:
            db_conn.close()
