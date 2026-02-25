from __future__ import annotations
import json
import logging
from enum import Enum
from .database import get_db
from .config import GABBE_ESCALATION_MODE

logger = logging.getLogger("gabbe.escalation")

class EscalationTrigger(Enum):
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    REPEATED_TOOL_FAILURE = "REPEATED_TOOL_FAILURE"
    AMBIGUOUS_DECISION = "AMBIGUOUS_DECISION"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    MAX_ITERATIONS = "MAX_ITERATIONS"

class EscalationResult:
    def __init__(self, status: str, response: str | None = None):
        self.status = status
        self.response = response

class EscalationHandler:
    def __init__(self, run_id: str, db_conn=None):
        self.run_id = run_id
        # Single connection context usually passed in runtime
        self._owns_db = False
        if db_conn is None:
            self.db_conn = get_db()
            self._owns_db = True
        else:
            self.db_conn = db_conn
        self.mode = GABBE_ESCALATION_MODE.lower()  # cli, file, silent

    def __del__(self):
        if self._owns_db and self.db_conn:
            self.db_conn.close()

    def escalate(self, trigger: EscalationTrigger, context_dict: dict, step: int = 0) -> EscalationResult:
        logger.warning(f"Escalation Triggered: {trigger.value}")
        
        # 1. Store in DB
        esc_id = None
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO pending_escalations 
                (run_id, step, trigger, context, status)
                VALUES (?, ?, ?, ?, ?)
            """, (self.run_id, step, trigger.value, json.dumps(context_dict), "pending"))
            self.db_conn.commit()
            esc_id = cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to record escalation in DB: {e}")

        # 2. Handle depending on mode.
        # Intentional API contract difference:
        #   cli  — human resolves inline; escalate() returns an EscalationResult so the
        #           caller can continue or branch based on the decision.
        #   file — execution must stop immediately; raises EscalationPaused so the run is
        #           suspended and resumed later via `gabbe resume <run-id>`.
        #   silent — auto-rejects; returns EscalationResult for CI/headless contexts.
        if self.mode == "cli":
            print("\n--- [ESCALATION REQUIRED] ---")
            print(f"Trigger: {trigger.value}")
            print(f"Context: {json.dumps(context_dict, indent=2)}")
            print("-----------------------------")
            choice = input("Select Action -> [a]pprove, [r]eject, [e]dit context, or abort (Ctrl+C): ").strip().lower()
            
            status = "rejected"
            response = None
            if choice == "a":
                status = "approved"
            elif choice == "e":
                status = "edited"
                response = input("Enter edited context overrides (JSON) or notes: ")
            
            if esc_id:
                self.resolve(esc_id, status, response)
            
            return EscalationResult(status, response)
            
        elif self.mode == "file":
            print(f"[ESCALATION] Run {self.run_id} hit escalation ({trigger.value}). Pausing execution.")
            print(f"To resume, review and run: gabbe resume {self.run_id}")
            raise EscalationPaused(f"Execution paused for human review. Run ID: {self.run_id}")
            
        else:
            # Silent / CI defaults to rejecting the dangerous action
            logger.info("Silent mode: auto-rejecting escalation.")
            if esc_id:
                self.resolve(esc_id, "rejected", "auto-rejected by silent mode")
            return EscalationResult("rejected", None)

    def resolve(self, esc_id: int, status: str, response: str | None = None):
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                UPDATE pending_escalations SET status = ?, response = ?, resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, response, esc_id))
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to resolve escalation {esc_id}: {e}")

class EscalationPaused(Exception):
    pass
