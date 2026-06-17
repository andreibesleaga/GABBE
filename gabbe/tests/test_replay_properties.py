# SPDX-License-Identifier: Apache-2.0
"""Property-based tests for checkpoint replay (Track B Phase 1).

Invariant: saving any sequence of JSON-serializable state snapshots and reading
them back preserves count, step order, and exact snapshot content (round-trip /
idempotency of the checkpoint store). PBT samples; it raises confidence, not proof.
"""

import itertools

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from gabbe.replay import CheckpointStore

# JSON-serializable snapshot values (the store json.dumps/loads them).
_json_scalar = st.one_of(
    st.integers(min_value=-(10**6), max_value=10**6),
    st.booleans(),
    st.text(max_size=20),
    st.none(),
)
_snapshot = st.dictionaries(
    keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=8),
    values=_json_scalar,
    max_size=6,
)
_S = settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=60)
_run_counter = itertools.count()


@_S
@given(snapshots=st.lists(_snapshot, max_size=15))
def test_checkpoint_roundtrip_preserves_order_and_content(tmp_project, snapshots):
    from gabbe.database import get_db

    conn = get_db()
    try:
        store = CheckpointStore(db_conn=conn)
        # A monotonic counter guarantees a unique run id per Hypothesis example, so
        # checkpoints never bleed across examples that share the function-scoped DB.
        run_id = f"run-prop-{next(_run_counter)}"
        for step, snap in enumerate(snapshots):
            store.save(
                run_id, step=step, node_name=f"n{step}", state_snapshot=snap, policy_version="v1"
            )

        history = store.get_history(run_id)
        assert len(history) == len(snapshots)
        assert [h["step"] for h in history] == list(range(len(snapshots)))
        for h, original in zip(history, snapshots):
            loaded = store.load(h["id"])
            assert loaded is not None
            assert loaded["state_snapshot"] == original
    finally:
        conn.close()
