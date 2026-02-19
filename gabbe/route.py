import re
import json
from .config import Colors
from .llm import call_llm

def calculate_complexity(prompt):
    """Estimate complexity score (0-100) using LLM."""
    print(f"  {Colors.CYAN}Analyzing Complexity via LLM...{Colors.ENDC}")
    
    system_prompt = "You are a complexity analyzer. Rate the following coding task complexity from 0-100. Return ONLY a JSON object: {\"score\": 50, \"reason\": \"explanation\"}."
    
    response = call_llm(prompt, system_prompt)
    
    try:
        data = json.loads(response)
        return data.get("score", 50), data.get("reason", "No reason provided")
    except:
        # Fallback heuristic if LLM fails or returns bad JSON
        score = 0
        if len(prompt) > 500: score += 40
        if "architect" in prompt.lower(): score += 30
        return score, "Fallback Heuristic"

def detect_pii(prompt):
    """Simple PII detection (Regex based to avoid leaking PII to LLM)."""
    # We do NOT want to send PII to an external LLM to check for PII :)
    if re.search(r'[\w\.-]+@[\w\.-]+', prompt):
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
    
    decision = "LOCAL"
    if complexity > 50:
        decision = "REMOTE"
        
    color = Colors.GREEN if decision == "LOCAL" else Colors.MAGENTA
    print(f"  {Colors.BOLD}Decision: {color}{decision}{Colors.ENDC}")
    
    return decision
