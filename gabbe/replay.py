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

        # Load recorded tool outputs from audit_spans for this run.
        # audit_spans has no step column, so we assign a per-node sequential index
        # (0, 1, 2, …) matching the order spans were recorded. This aligns with
        # checkpoint steps when each node produces one span per invocation.
        recorded_outputs = {}
        try:
            cursor = self.store.db_conn.cursor()
            cursor.execute("""
                SELECT node_name, output_data FROM audit_spans
                WHERE run_id = ? ORDER BY id ASC
            """, (run_id,))
            node_occurrence: dict = {}
            for row in cursor.fetchall():
                nn = row["node_name"]
                idx = node_occurrence.get(nn, 0)
                node_occurrence[nn] = idx + 1
                recorded_outputs[(nn, idx)] = row["output_data"]
        except Exception as e:
            logger.warning(f"Could not load recorded outputs: {e}")

        # Track per-node occurrence index during replay to align with the index used
        # when recorded_outputs was built (sequential per node, not by step number).
        node_replay_occurrence: dict = {}
        replayed = []
        for ckpt in checkpoints:
            if ckpt["step"] < from_step:
                continue
            nn = ckpt["node_name"]
            idx = node_replay_occurrence.get(nn, 0)
            node_replay_occurrence[nn] = idx + 1
            step_result = {
                "step": ckpt["step"],
                "node_name": nn,
                "state_snapshot": json.loads(ckpt["state_snapshot"]) if isinstance(ckpt["state_snapshot"], str) else ckpt["state_snapshot"],
                "policy_version": ckpt["policy_version"],
                "recorded_output": recorded_outputs.get((nn, idx)),
            }
            replayed.append(step_result)
            logger.info(f"Replayed step {ckpt['step']}: {nn}")

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
