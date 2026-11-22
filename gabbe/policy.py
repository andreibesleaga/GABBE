# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .config import GABBE_POLICY_FILE, PII_PATTERNS, SECRET_PATTERNS


class PolicyError(ValueError):
    """The policy document has a wrong shape. The message starts with
    "policy file invalid:" and names the key and the expected shape."""


def _invalid(key: str, expected: str, got: Any) -> PolicyError:
    return PolicyError(
        f"policy file invalid: `{key}` must be {expected}, got {type(got).__name__} ({got!r})"
    )


def _is_name(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _name_list(key: str, value: Any) -> List[str]:
    """A list of non-empty strings; null is NOT an empty list (the documents never say so)."""
    if not isinstance(value, list) or not all(_is_name(v) for v in value):
        raise _invalid(key, "a list of non-empty strings", value)
    return list(value)


def _tool_lists(tools: Any) -> tuple[List[str], List[str]]:
    """(allowed, denied). A missing or non-mapping `tools` section denies all (fail-closed);
    a mapping without `allowed` is blocklist mode (allow all but `denied`)."""
    if not isinstance(tools, dict):
        return [], []
    allowed = _name_list("tools.allowed", tools["allowed"]) if "allowed" in tools else ["*"]
    denied = _name_list("tools.denied", tools["denied"]) if "denied" in tools else []
    return allowed, denied


def _role_map(roles: Any) -> Dict[str, List[str]]:
    if roles is None:
        return {}
    if not isinstance(roles, dict):
        raise _invalid("roles", "a mapping of role name to a list of tool names", roles)
    return {_role_name(r): _name_list(f"roles.{r}", tools) for r, tools in roles.items()}


def _role_name(role: Any) -> str:
    if not _is_name(role):
        raise _invalid("roles", "a mapping with non-empty string role names", role)
    return str(role)


def _content_safety_enabled(section: Any) -> bool:
    if not isinstance(section, dict):
        raise _invalid("content_safety", "a mapping such as {enabled: true}", section)
    enabled = section.get("enabled", False)
    if not isinstance(enabled, bool):
        raise _invalid("content_safety.enabled", "true or false", enabled)
    return enabled


def _bound(param: str, limits: Any) -> Dict[str, float]:
    if not isinstance(limits, dict):
        raise _invalid(f"parameter_bounds.{param}", "a mapping with numeric min and/or max", limits)
    for edge in ("min", "max"):
        if limits.get(edge) is not None and not _is_number(limits[edge]):
            raise _invalid(f"parameter_bounds.{param}.{edge}", "a number", limits[edge])
    return dict(limits)


def _bounds_map(section: Any) -> Dict[str, Dict[str, float]]:
    if section is None:
        return {}
    if not isinstance(section, dict):
        raise _invalid("parameter_bounds", "a mapping of parameter name to {min, max}", section)
    return {str(param): _bound(str(param), limits) for param, limits in section.items()}


def _arguments(context: Dict[str, Any]) -> Dict[str, Any] | None:
    """The request arguments; absent means none; None is returned for a wrong shape."""
    args = context.get("arguments", {}) if "arguments" in context else {}
    return args if isinstance(args, dict) else None


@dataclass
class PolicyResult:
    allowed: bool
    reason: str
    policy_name: str


class Policy:
    name: str = "BasePolicy"

    def check(self, context: Dict[str, Any]) -> PolicyResult:
        raise NotImplementedError


class ToolAllowlistPolicy(Policy):
    name = "ToolAllowlistPolicy"

    def __init__(self, allowed_tools: List[str], denied_tools: List[str]):
        self.allowed = set(allowed_tools)
        self.denied = set(denied_tools)

    def check(self, context: Dict[str, Any]) -> PolicyResult:
        # No `tool` key at all means the request is not a tool call (nothing to check).
        # A `tool` key that is empty or not a string cannot be named: denied.
        if "tool" not in context:
            return PolicyResult(True, "No tool to check", self.name)
        tool_name = context["tool"]
        if not _is_name(tool_name):
            return PolicyResult(False, "Tool name is empty or not a string", self.name)

        if tool_name in self.denied or ("*" in self.denied):
            return PolicyResult(False, f"Tool {tool_name} is explicitly denied", self.name)

        if "*" in self.allowed or tool_name in self.allowed:
            return PolicyResult(True, f"Tool {tool_name} is allowed", self.name)

        return PolicyResult(False, f"Tool {tool_name} is not in allowlist", self.name)


class RolePolicy(Policy):
    name = "RolePolicy"

    def __init__(self, roles: Dict[str, List[str]]):
        self.roles = roles

    def check(self, context: Dict[str, Any]) -> PolicyResult:
        tool_name = context.get("tool")
        role_name = context.get("role")

        # Fail-closed: a RolePolicy only exists when the operator has configured
        # role-based access. A call that omits the role (or the tool) cannot be
        # affirmatively authorized, so it must be DENIED rather than waved through
        # — otherwise an empty/None role silently bypasses all role restrictions.
        if not isinstance(role_name, str) or not isinstance(tool_name, str):
            return PolicyResult(
                False, "Missing role or tool context — denied (fail-closed)", self.name
            )
        if not role_name or not tool_name:
            return PolicyResult(
                False, "Missing role or tool context — denied (fail-closed)", self.name
            )

        allowed_for_role = self.roles.get(role_name, [])
        if "*" in allowed_for_role or tool_name in allowed_for_role:
            return PolicyResult(True, f"Role {role_name} allowed to use {tool_name}", self.name)

        return PolicyResult(False, f"Role {role_name} denied from using {tool_name}", self.name)


class ContentSafetyPolicy(Policy):
    """Deny tool calls whose input text contains PII patterns."""

    name = "ContentSafetyPolicy"

    def check(self, context: Dict[str, Any]) -> PolicyResult:
        text = context.get("input", "")
        if not text:
            # Also check arguments dict values
            args = _arguments(context)
            if args is None:
                return PolicyResult(False, "Arguments are not a mapping — denied", self.name)
            text = " ".join(str(v) for v in args.values())
        text = str(text)
        for pattern in list(PII_PATTERNS) + list(SECRET_PATTERNS):
            if pattern.search(text):
                return PolicyResult(False, "Input contains PII — routing to LOCAL only", self.name)
        return PolicyResult(True, "No PII detected", self.name)


class ParameterRangePolicy(Policy):
    """Validate numeric parameters against defined min/max bounds."""

    name = "ParameterRangePolicy"

    def __init__(self, bounds: Dict[str, Dict[str, float]]):
        # bounds = {"param_name": {"min": 0, "max": 100}, ...}
        self.bounds = bounds

    def check(self, context: Dict[str, Any]) -> PolicyResult:
        args = _arguments(context)
        if args is None:
            return PolicyResult(False, "Arguments are not a mapping — denied", self.name)
        for param, value in args.items():
            if param in self.bounds and _is_number(value):
                lo = self.bounds[param].get("min")
                hi = self.bounds[param].get("max")
                if lo is not None and value < lo:
                    return PolicyResult(False, f"Param {param}={value} below min {lo}", self.name)
                if hi is not None and value > hi:
                    return PolicyResult(False, f"Param {param}={value} above max {hi}", self.name)
        return PolicyResult(True, "All parameters in range", self.name)


class PolicyEngine:
    def __init__(self, policies: List[Policy]):
        self.policies = policies
        self.version = "unknown"

    def evaluate(self, context: Dict[str, Any]) -> PolicyResult:
        for p in self.policies:
            res = p.check(context)
            if not res.allowed:
                return res
        return PolicyResult(True, "All policies passed", "PolicyEngine")

    def evaluate_all(self, context: Dict[str, Any]) -> List[PolicyResult]:
        return [p.check(context) for p in self.policies]

    @staticmethod
    def _policies_from_document(data: Dict[str, Any]) -> List[Policy]:
        """Build the policies from a parsed document; any wrong shape raises PolicyError.

        Fail-closed: a document with no usable `tools` mapping denies all tools (an empty
        `tools:` or a non-mapping value is a misconfiguration, not a license).
        """
        allowed, denied = _tool_lists(data.get("tools"))
        policies: List[Policy] = [ToolAllowlistPolicy(allowed, denied)]
        roles = _role_map(data.get("roles"))
        if roles:
            policies.append(RolePolicy(roles))
        if "content_safety" in data and _content_safety_enabled(data["content_safety"]):
            policies.append(ContentSafetyPolicy())
        bounds = _bounds_map(data.get("parameter_bounds"))
        if bounds:
            policies.append(ParameterRangePolicy(bounds))
        return policies

    @classmethod
    def from_yaml(cls, path: Path | str | None = None) -> "PolicyEngine":
        # Accept str for caller convenience; normalize so .exists()/open() always
        # operate on a Path. None falls back to the configured policy file.
        path = Path(path) if path is not None else GABBE_POLICY_FILE
        version = "1"
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            if data is None:
                data = {}
            if not isinstance(data, dict):
                raise _invalid("<top level>", "a mapping of sections", data)
            version = data.get("version", "1")
            policies = cls._policies_from_document(data)
        else:
            # Policy file not found: default to deny-all and warn the operator.
            # This is the secure default — explicit policies must be created to allow tools.
            import logging as _logging

            _logging.getLogger("gabbe.policy").warning(
                "Policy file not found at %s — defaulting to deny-all. "
                "Create project/policies.yml to configure tool access.",
                path,
            )
            policies = [ToolAllowlistPolicy([], [])]

        engine = cls(policies)
        engine.version = version
        return engine
