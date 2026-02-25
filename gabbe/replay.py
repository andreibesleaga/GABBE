from __future__ import annotations
import json
import logging
from .database import get_db

logger = logging.getLogger("gabbe.replay")

class CheckpointStore:
    def __init__(self, db_conn=None):
        self._owns_db = False
        if db_conn is None:
            self.db_conn = get_db()
            self._owns_db = True
        else:
            self.db_conn = db_conn

    def __del__(self):
        if self._owns_db and self.db_conn:
            self.db_conn.close()

    def save(self, run_id: str, step: int, node_name: str, state_snapshot: dict, policy_version: str, parent_id: int | None = None) -> int | None:
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO checkpoints 
                (run_id, step, node_name, state_snapshot, policy_version, parent_checkpoint_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (run_id, step, node_name, json.dumps(state_snapshot), policy_version, parent_id))
            self.db_conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return None

    def get_history(self, run_id: str) -> list:
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT * FROM checkpoints WHERE run_id = ? ORDER BY step ASC
            """, (run_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch checkpoint history: {e}")
            return []

    def load(self, checkpoint_id: int) -> dict | None:
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT * FROM checkpoints WHERE id = ?
            """, (checkpoint_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["state_snapshot"] = json.loads(d["state_snapshot"])
                return d
            return None
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

class ReplayRunner:
    def __init__(self, store: CheckpointStore):
        self.store = store

    def replay(self, run_id: str, from_step: int = 0) -> list:
        """
        Replay a run from its checkpoints, substituting recorded tool outputs from
        audit_spans instead of calling live tools.

        Returns a list of replayed step dicts with state_snapshot and recorded output.
        """
        checkpoints = self.store.get_history(run_id)
        if not checkpoints:
            logger.warning(f"No checkpoints found for run {run_id}")
            return []

        # Load recorded tool outputs from audit_spans for this run
        recorded_outputs = {}
        try:
            cursor = self.store.db_conn.cursor()
            cursor.execute("""
                SELECT node_name, step_num, output_data FROM audit_spans
                WHERE run_id = ? ORDER BY id ASC
            """, (run_id,))
            for row in cursor.fetchall():
                key = (row["node_name"], row["step_num"] if "step_num" in row.keys() else 0)
                recorded_outputs[key] = row["output_data"]
        except Exception as e:
            logger.warning(f"Could not load recorded outputs: {e}")

        replayed = []
        for ckpt in checkpoints:
            if ckpt["step"] < from_step:
                continue
            step_result = {
                "step": ckpt["step"],
                "node_name": ckpt["node_name"],
                "state_snapshot": json.loads(ckpt["state_snapshot"]) if isinstance(ckpt["state_snapshot"], str) else ckpt["state_snapshot"],
                "policy_version": ckpt["policy_version"],
                "recorded_output": recorded_outputs.get((ckpt["node_name"], ckpt["step"])),
            }
            replayed.append(step_result)
            logger.info(f"Replayed step {ckpt['step']}: {ckpt['node_name']}")

        return replayed

    def diff(self, run_id_a: str, run_id_b: str) -> list:
        """
        Compare two runs step by step by their checkpoint node sequences.
        Returns list of dicts with step, node_name and match status.
        """
        history_a = self.store.get_history(run_id_a)
        history_b = self.store.get_history(run_id_b)

        max_len = max(len(history_a), len(history_b))
        results = []
        for i in range(max_len):
            a = history_a[i] if i < len(history_a) else None
            b = history_b[i] if i < len(history_b) else None
            node_a = a["node_name"] if a else "<missing>"
            node_b = b["node_name"] if b else "<missing>"
            results.append({
                "step": i,
                "run_a_node": node_a,
                "run_b_node": node_b,
                "match": node_a == node_b,
            })
        return results
