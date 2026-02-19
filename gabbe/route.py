import re
from .config import Colors

def calculate_complexity(prompt):
    """Estimate complexity score (0-100)."""
    score = 0
    
    # 1. Length heuristic
    tokens = len(prompt.split())
    if tokens > 500: score += 40
    elif tokens > 100: score += 10
    
    # 2. Keyword heuristic
    high_complexity_terms = ["architect", "design practice", "security audit", "refactor", "migration"]
    for term in high_complexity_terms:
        if term in prompt.lower():
            score += 20
            
    # 3. Code density
    if "```" in prompt:
        score += 15
        
    return min(score, 100)

def detect_pii(prompt):
    """Simple PII detection."""
    # This is a placeholder for more robust PII detection
    # Regex for email
    if re.search(r'[\w\.-]+@[\w\.-]+', prompt):
        return True
    return False

def route_request(prompt):
    """Arbitrate between Local and Remote LLM."""
    print(f"{Colors.HEADER}🔀 Cost-Effective Router{Colors.ENDC}")
    print(f"  Prompt: \"{prompt[:50]}...\"")
    
    complexity = calculate_complexity(prompt)
    has_pii = detect_pii(prompt)
    
    print(f"  {Colors.BLUE}Analysis:{Colors.ENDC}")
    print(f"  - Complexity Score: {complexity}/100")
    print(f"  - PII Detected: {has_pii}")
    
    decision = "LOCAL"
    reason = "Low complexity task"
    
    if has_pii:
        decision = "LOCAL"
        reason = "Privacy (PII Detected)"
    elif complexity > 50:
        decision = "REMOTE"
        reason = "High complexity requires SOTA model"
        
    color = Colors.GREEN if decision == "LOCAL" else Colors.MAGENTA
    print(f"  {Colors.BOLD}Decision: {color}{decision}{Colors.ENDC} ({reason})")
    
    return decision
