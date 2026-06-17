# SPDX-License-Identifier: Apache-2.0
"""Property-based tests for Markdown<->task sync (Track B Phase 1).

Invariants: generate→parse round-trips task title+status for any task list, the
state hash is deterministic, and generate/parse is idempotent. Pure functions —
no DB. PBT samples; it raises confidence, it does not prove.
"""

import string

from hypothesis import given
from hypothesis import strategies as st

from gabbe.sync import (
    _calculate_state_hash,
    generate_markdown_tasks,
    parse_markdown_tasks,
)

_titles = (
    st.text(alphabet=string.ascii_letters + string.digits + " ", min_size=1, max_size=40)
    .map(str.strip)
    .filter(lambda s: len(s) > 0)
)
_status = st.sampled_from(["TODO", "IN_PROGRESS", "DONE"])
_task = st.builds(lambda t, s: {"title": t, "status": s}, _titles, _status)


def _pairs(tasks):
    return [(t["title"], t["status"]) for t in tasks]


@given(st.lists(_task, max_size=25))
def test_generate_parse_roundtrip(tasks):
    parsed = parse_markdown_tasks(generate_markdown_tasks(tasks))
    assert _pairs(parsed) == _pairs(tasks)


@given(st.lists(_task, max_size=25))
def test_generate_is_idempotent(tasks):
    once = generate_markdown_tasks(tasks)
    twice = generate_markdown_tasks(parse_markdown_tasks(once))
    assert once == twice


@given(st.lists(_task, max_size=25))
def test_state_hash_is_deterministic_and_roundtrip_stable(tasks):
    # parse adds the per-task content 'hash' key that _calculate_state_hash needs.
    parsed = parse_markdown_tasks(generate_markdown_tasks(tasks))
    assert _calculate_state_hash(parsed) == _calculate_state_hash(parsed)
    # Re-generating and re-parsing yields the same content hash (idempotent).
    reparsed = parse_markdown_tasks(generate_markdown_tasks(parsed))
    assert _calculate_state_hash(reparsed) == _calculate_state_hash(parsed)
