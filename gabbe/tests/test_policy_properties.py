# SPDX-License-Identifier: Apache-2.0
"""Property tests for the policy loader and engine (assurance ladder level 1).

Promises tested: a policy file that is damaged, empty or of the wrong shape never
opens a door (fail-closed); a tool that is not explicitly allowed is denied; allowing
one tool allows no other; the same input gives the same answer.

A policy document of the wrong shape is refused at load time with PolicyError (a ValueError).
"""

import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from gabbe.policy import PolicyEngine, PolicyError

_SETTINGS = settings(max_examples=60, derandomize=True, deadline=None, database=None)

_name = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Zs")), min_size=1, max_size=12
)
_name_or_star = st.one_of(_name, st.just("*"))
_name_lists = st.lists(_name_or_star, max_size=5)
# Section shapes the loader is meant to cope with, including the wrong ones it handles today.
_tools = st.one_of(
    st.none(),
    st.text(max_size=5),
    st.integers(),
    st.lists(_name, max_size=3),
    st.fixed_dictionaries({}, optional={"allowed": _name_lists, "denied": _name_lists}),
)
_roles: st.SearchStrategy[Any] = st.one_of(
    st.none(),
    st.just({}),
    st.dictionaries(_name, _name_lists, max_size=3),
)
_bounds = st.one_of(
    st.none(),
    st.dictionaries(
        _name,
        st.fixed_dictionaries({}, optional={"min": st.integers(-5, 5), "max": st.integers(-5, 5)}),
        max_size=3,
    ),
)
_documents = st.fixed_dictionaries(
    {},
    optional={
        "version": st.one_of(st.text(max_size=3), st.integers(), st.none()),
        "tools": _tools,
        "roles": _roles,
        "content_safety": st.fixed_dictionaries({}, optional={"enabled": st.booleans()}),
        "parameter_bounds": _bounds,
    },
)


def _load(text):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "policies.yml"
        path.write_text(text, encoding="utf-8")
        return PolicyEngine.from_yaml(path)


def _load_doc(doc):
    return _load(yaml.safe_dump(doc))


def _tool_decision(doc, tool):
    """What the tool section of a document promises for `tool`: True means allowed."""
    section = doc.get("tools")
    if isinstance(section, dict):
        allowed = section.get("allowed", ["*"])
        denied = section.get("denied", [])
    else:
        allowed, denied = [], []  # no usable tools section: deny all
    if tool in denied or "*" in denied:
        return False
    return "*" in allowed or tool in allowed


@given(_documents, _name, _name)
@_SETTINGS
def test_tool_not_allowed_by_the_document_is_always_denied(doc, tool, role):
    """Fail-closed: if the document does not allow a tool, the engine denies it,
    whatever the other sections say."""
    engine = _load_doc(doc)
    result = engine.evaluate({"tool": tool, "role": role})
    if not _tool_decision(doc, tool):
        assert result.allowed is False


@given(_documents, _name, _name)
@_SETTINGS
def test_engine_never_allows_more_than_the_tool_section(doc, tool, role):
    """The engine's answer is allowed only when the tool section allows it (roles,
    content and bounds can only narrow the answer, never widen it)."""
    engine = _load_doc(doc)
    if engine.evaluate({"tool": tool, "role": role}).allowed:
        assert _tool_decision(doc, tool)


@given(st.lists(_name, min_size=1, max_size=5, unique=True), _name)
@_SETTINGS
def test_allowing_one_tool_does_not_allow_another(allowed, other):
    """With an explicit allow-list, a tool that is not in it is denied even though the
    listed tools are allowed."""
    engine = _load_doc({"tools": {"allowed": allowed}})
    for tool in allowed:
        assert engine.evaluate({"tool": tool}).allowed is True
    if other not in allowed:
        assert engine.evaluate({"tool": other}).allowed is False


@given(_documents, _name, _name)
@_SETTINGS
def test_same_policy_and_input_give_the_same_answer(doc, tool, role):
    """Evaluation is deterministic: two evaluations, and two fresh loads of the same
    text, agree on every field."""
    text = yaml.safe_dump(doc)
    context = {"tool": tool, "role": role, "arguments": {"n": 1}}
    first, second = _load(text), _load(text)
    a, b = first.evaluate(context), second.evaluate(context)
    assert a == b == first.evaluate(context)
    assert first.evaluate_all(context) == second.evaluate_all(context)


@given(st.text(max_size=60))
@_SETTINGS
def test_arbitrary_text_loads_or_fails_with_a_yaml_error(text):
    """Any text either loads into an engine, raises the YAML parser's own error, or raises
    PolicyError (a wrong shape); nothing else ever escapes."""
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError:
        with pytest.raises(yaml.YAMLError):
            _load(text)
        return
    try:
        _load(text)
    except PolicyError:
        assert parsed is not None


@pytest.mark.parametrize("text", ["", "null", "{}", "tools:\n", "tools: []\n"])
def test_empty_or_unusable_policy_denies_every_tool(text):
    """A policy file that is empty, null or has no usable tools section denies all."""
    engine = _load(text)
    assert engine.evaluate({"tool": "anything"}).allowed is False


# ---- wrong shapes: refused at load time, never at evaluation ----------------------------

_BAD_SHAPES = [
    ("- a\n", "<top level>", "a top-level list"),
    ("42\n", "<top level>", "a top-level number"),
    ("tools: {allowed: null}\n", "tools.allowed", "tools.allowed set to null"),
    ("tools: {denied: null}\n", "tools.denied", "tools.denied set to null"),
    ("tools: {allowed: [[1]]}\n", "tools.allowed", "a list inside tools.allowed"),
    ("tools: {allowed: ['']}\n", "tools.allowed", "an empty tool name in tools.allowed"),
    ("content_safety: null\n", "content_safety", "content_safety set to null"),
    ("content_safety: {enabled: 'yes'}\n", "content_safety.enabled", "enabled is not a boolean"),
    ("roles: [a]\n", "roles", "roles given as a list"),
    ("roles: {a: null}\n", "roles.a", "a role with null tools"),
    ("roles: {a: x}\n", "roles.a", "a role with a string instead of a list"),
    ("parameter_bounds: [a]\n", "parameter_bounds", "parameter_bounds as a list"),
    ("parameter_bounds: {t: 5}\n", "parameter_bounds.t", "bounds of a parameter not a mapping"),
    ("parameter_bounds: {t: {min: low}}\n", "parameter_bounds.t.min", "non-numeric minimum"),
    ("parameter_bounds: {t: {max: true}}\n", "parameter_bounds.t.max", "boolean maximum"),
]


@pytest.mark.parametrize(
    "text,key", [(t, k) for t, k, _ in _BAD_SHAPES], ids=[why for _, _, why in _BAD_SHAPES]
)
def test_wrongly_shaped_policy_is_refused_at_load_naming_the_key(text, key):
    """One exception type, a message that starts the same way and names the key."""
    with pytest.raises(PolicyError) as err:
        _load(text)
    assert str(err.value).startswith("policy file invalid: ")
    assert f"`{key}`" in str(err.value)
    assert isinstance(err.value, ValueError)


def test_empty_tool_name_is_denied_by_a_deny_all_policy():
    """With `tools: {allowed: []}` every call is denied, including the empty tool name."""
    engine = _load("tools:\n  allowed: []\n")
    assert engine.evaluate({"tool": ""}).allowed is False


@pytest.mark.parametrize("tool", ["", None, 5, ["x"], {}])
def test_tool_key_that_is_not_a_name_is_denied_even_by_allow_all(tool):
    """A request that carries a `tool` key must name a tool: empty or non-string is denied."""
    engine = _load("tools:\n  allowed: ['*']\n")
    assert engine.evaluate({"tool": tool}).allowed is False


def test_request_without_a_tool_key_is_not_a_tool_call():
    """No `tool` key at all keeps its meaning: nothing to check for the allowlist."""
    engine = _load("tools:\n  allowed: []\n")
    assert engine.evaluate({"arguments": {}}).allowed is True


@pytest.mark.parametrize("arguments", [None, [1], "x", 3])
def test_arguments_of_the_wrong_shape_are_denied_not_a_crash(arguments):
    """Content safety and parameter bounds deny a request whose arguments are not a mapping."""
    engine = _load(
        "tools: {allowed: ['*']}\ncontent_safety: {enabled: true}\n"
        "parameter_bounds: {t: {min: 0}}\n"
    )
    assert engine.evaluate({"tool": "x", "arguments": arguments}).allowed is False
    assert [r.allowed for r in engine.evaluate_all({"tool": "x", "arguments": arguments})] == [
        True,
        False,
        False,
    ]


@pytest.mark.parametrize("role,tool", [(5, "t"), ("a", 5), (["a"], "t"), ("a", ["t"])])
def test_role_policy_denies_names_that_are_not_strings(role, tool):
    engine = _load("tools: {allowed: ['*']}\nroles: {a: ['*']}\n")
    assert engine.evaluate({"tool": tool, "role": role}).allowed is False


def test_numeric_bounds_still_work_after_validation():
    engine = _load("tools: {allowed: ['*']}\nparameter_bounds: {t: {min: 0, max: 1.5}}\n")
    assert engine.evaluate({"tool": "x", "arguments": {"t": 1}}).allowed is True
    assert engine.evaluate({"tool": "x", "arguments": {"t": 2}}).allowed is False
