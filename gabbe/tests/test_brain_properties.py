# SPDX-License-Identifier: Apache-2.0
"""Property-based tests for the brain evolution engine (Track B Phase 3).

Real-engine invariants proving the *self-evolving* claim:
  * gene success_rate is monotonic non-decreasing and capped at 1.0;
  * epsilon-greedy selection ALWAYS returns a gene that exists (it never
    fabricates), and returns (None, None) for an empty pool.
PBT samples; it raises confidence, not proof. The free-energy framing is
conceptual — the implementation is an epsilon-greedy bandit over prompt variants.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from gabbe.brain import _get_best_gene, _update_gene_success_rate

_S = settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=60)


@_S
@given(
    updates=st.integers(min_value=0, max_value=30),
    delta=st.floats(min_value=0.01, max_value=0.5, allow_nan=False),
)
def test_success_rate_monotonic_and_capped(tmp_project, updates, delta):
    from gabbe.database import get_db

    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO genes (skill_name, prompt_content, success_rate, generation) "
            "VALUES (?, ?, 0.0, 0)",
            ("s", "p"),
        )
        gid = cur.lastrowid
        conn.commit()
        prev = 0.0
        for _ in range(updates):
            _update_gene_success_rate(conn, gid, delta)
            rate = conn.execute("SELECT success_rate FROM genes WHERE id=?", (gid,)).fetchone()[
                "success_rate"
            ]
            assert rate >= prev  # monotonic non-decreasing
            assert rate <= 1.0 + 1e-9  # capped at 1.0
            prev = rate
    finally:
        conn.close()


@_S
@given(rates=st.lists(st.floats(min_value=0, max_value=1, allow_nan=False), min_size=1, max_size=8))
def test_get_best_gene_always_returns_a_real_gene(tmp_project, rates):
    from gabbe.database import get_db

    conn = get_db()
    try:
        skill = f"sk{abs(hash(tuple(rates))) % 10_000_000}"
        ids = []
        for i, r in enumerate(rates):
            cur = conn.execute(
                "INSERT INTO genes (skill_name, prompt_content, success_rate, generation) "
                "VALUES (?, ?, ?, ?)",
                (skill, f"p{i}", r, i),
            )
            ids.append(cur.lastrowid)
        conn.commit()
        # Across many selections (both the 20% explore and 80% exploit branches),
        # the chosen gene is ALWAYS one that exists — never fabricated.
        for _ in range(40):
            gid, content = _get_best_gene(conn, skill)
            assert gid in ids
            assert content is not None
    finally:
        conn.close()


def test_get_best_gene_empty_pool_returns_none(tmp_project):
    from gabbe.database import get_db

    conn = get_db()
    try:
        assert _get_best_gene(conn, "no-such-skill") == (None, None)
    finally:
        conn.close()
