import yaml
from dataclasses import dataclass
from typing import List, Dict
from .config import GABBE_POLICY_FILE, PII_PATTERNS

@dataclass
class PolicyResult:
    allowed: bool
    reason: str
    policy_name: str

class Policy:
    name: str = "BasePolicy"
    
    def check(self, context: dict) -> PolicyResult:
        raise NotImplementedError

class ToolAllowlistPolicy(Policy):
    name = "ToolAllowlistPolicy"
    def __init__(self, allowed_tools: List[str], denied_tools: List[str]):
        self.allowed = set(allowed_tools)
        self.denied = set(denied_tools)

    def check(self, context: dict) -> PolicyResult:
        tool_name = context.get("tool")
        if not tool_name:
            return PolicyResult(True, "No tool to check", self.name)
        
        if tool_name in self.denied or ("*" in self.denied):
            return PolicyResult(False, f"Tool {tool_name} is explicitly denied", self.name)
            
        if "*" in self.allowed or tool_name in self.allowed:
            return PolicyResult(True, f"Tool {tool_name} is allowed", self.name)
            
        return PolicyResult(False, f"Tool {tool_name} is not in allowlist", self.name)

class RolePolicy(Policy):
    name = "RolePolicy"
    def __init__(self, roles: Dict[str, List[str]]):
        self.roles = roles
        
    def check(self, context: dict) -> PolicyResult:
        tool_name = context.get("tool")
        role_name = context.get("role")
        
        if not role_name or not tool_name:
            return PolicyResult(True, "Missing role or tool context", self.name)
            
        allowed_for_role = self.roles.get(role_name, [])
        if "*" in allowed_for_role or tool_name in allowed_for_role:
            return PolicyResult(True, f"Role {role_name} allowed to use {tool_name}", self.name)
            
        return PolicyResult(False, f"Role {role_name} denied from using {tool_name}", self.name)

class ContentSafetyPolicy(Policy):
    """Deny tool calls whose input text contains PII patterns."""
    name = "ContentSafetyPolicy"

    def check(self, context: dict) -> PolicyResult:
        text = context.get("input", "")
        if not text:
            # Also check arguments dict values
            args = context.get("arguments", {})
            text = " ".join(str(v) for v in args.values()) if args else ""
        for pattern in PII_PATTERNS:
            if pattern.search(text):
                return PolicyResult(False, "Input contains PII — routing to LOCAL only", self.name)
        return PolicyResult(True, "No PII detected", self.name)


class ParameterRangePolicy(Policy):
    """Validate numeric parameters against defined min/max bounds."""
    name = "ParameterRangePolicy"

    def __init__(self, bounds: Dict[str, Dict[str, float]]):
        # bounds = {"param_name": {"min": 0, "max": 100}, ...}
        self.bounds = bounds

    def check(self, context: dict) -> PolicyResult:
        args = context.get("arguments", {})
        for param, value in args.items():
            if param in self.bounds and isinstance(value, (int, float)):
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

    def evaluate(self, context: dict) -> PolicyResult:
        for p in self.policies:
            res = p.check(context)
            if not res.allowed:
                return res
        return PolicyResult(True, "All policies passed", "PolicyEngine")

    def evaluate_all(self, context: dict) -> List[PolicyResult]:
        return [p.check(context) for p in self.policies]

    @classmethod
    def from_yaml(cls, path=None):
        path = path or GABBE_POLICY_FILE
        policies = []
        version = "1"
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
                version = data.get("version", "1")
                
                tools = data.get("tools", {})
                policies.append(ToolAllowlistPolicy(
                    allowed_tools=tools.get("allowed", ["*"]),
                    denied_tools=tools.get("denied", [])
                ))
                
                roles = data.get("roles", {})
                if roles:
                    policies.append(RolePolicy(roles))

                if data.get("content_safety", {}).get("enabled", False):
                    policies.append(ContentSafetyPolicy())

                param_bounds = data.get("parameter_bounds", {})
                if param_bounds:
                    policies.append(ParameterRangePolicy(param_bounds))
        else:
            # Policy file not found: default to deny-all and warn the operator.
            # This is the secure default — explicit policies must be created to allow tools.
            import logging as _logging
            _logging.getLogger("gabbe.policy").warning(
                "Policy file not found at %s — defaulting to deny-all. "
                "Create project/policies.yml to configure tool access.", path
            )
            policies.append(ToolAllowlistPolicy([], []))
            
        engine = cls(policies)
        engine.version = version
        return engine
