import re
import json
from .config import Colors, ROUTE_COMPLEXITY_THRESHOLD
from .llm import call_llm

# PII patterns — keep these local to avoid sending PII to an external LLM
_PII_PATTERNS = [
    re.compile(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'),          # email
    re.compile(r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'),           # US phone
    re.compile(r'\b\d{9}\b'),                                  # SSN (no dashes)
    re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),                     # SSN (dashes)
    re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),               # credit card
    re.compile(r'(?i)\b(?:password|passwd|api[_\-]?key|secret|token)\s*[:=]\s*\S+'),  # credentials
]


def calculate_complexity(prompt):
    """Estimate complexity score (0-100). Uses heuristics first, then LLM."""
    # Heuristics (save money/time)
    if len(prompt) < 100 and "```" not in prompt:
        print(f"  {Colors.CYAN}Complexity Analysis (Heuristic): Simple{Colors.ENDC}")
        return 10, "Heuristic: Short prompt, no code blocks"

    print(f"  {Colors.CYAN}Analyzing Complexity via LLM...{Colors.ENDC}")

    system_prompt = (
        "You are a complexity analyzer. Rate the following coding task complexity "
        'from 0-100. Return ONLY a JSON object: {"score": 50, "reason": "explanation"}.'
    )

    try:
        response = call_llm(prompt, system_prompt)
        if response is None:
            raise ValueError("LLM returned no response")
        data = json.loads(response)
        return data.get("score", 50), data.get("reason", "No reason provided")
    except Exception as e:
        # Fallback heuristic if LLM fails
        print(f"  {Colors.WARNING}LLM Analysis Failed: {e}{Colors.ENDC}")
        score = 0
        if len(prompt) > 500:
            score += 40
        if "architect" in prompt.lower():
            score += 30
        return score, "Fallback Heuristic (LLM Error)"


def detect_pii(prompt):
    """Detect common PII patterns using local regex (no external calls)."""
    for pattern in _PII_PATTERNS:
        if pattern.search(prompt):
            return True
    return False


def route_request(prompt):
    """Arbitrate between Local and Remote LLM."""
    print(f"{Colors.HEADER}🔀 Cost-Effective Router{Colors.ENDC}")
    print(f"  Prompt: \"{prompt[:50]}...\"")

    has_pii = detect_pii(prompt)

    if has_pii:
        print(f"  {Colors.FAIL}PII DETECTED! Routing to LOCAL ONLY.{Colors.ENDC}")
        return "LOCAL"

    complexity, reason = calculate_complexity(prompt)

    print(f"  {Colors.BLUE}Analysis:{Colors.ENDC}")
    print(f"  - Complexity Score: {complexity}/100")
    print(f"  - Reason: {reason}")

    decision = "REMOTE" if complexity > ROUTE_COMPLEXITY_THRESHOLD else "LOCAL"
    color = Colors.GREEN if decision == "LOCAL" else Colors.MAGENTA
    print(f"  {Colors.BOLD}Decision: {color}{decision}{Colors.ENDC}")

    return decision
