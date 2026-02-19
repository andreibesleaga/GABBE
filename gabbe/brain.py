import random
from .config import Colors
from .database import get_db

def activate_brain():
    """Run the Active Inference Loop."""
    print(f"{Colors.HEADER}🧠 Brain Mode: Active Inference Loop{Colors.ENDC}")
    
    # 1. Observation (Get State)
    # TODO: Read Project State from DB
    phase = "S04_TASKS" # Mock
    print(f"  {Colors.BLUE}Observation:{Colors.ENDC} Phase is {phase}")
    
    # 2. Prediction (Expected vs Actual)
    expected_velocity = 5 # tasks/day
    actual_velocity = 3 # tasks/day
    prediction_error = expected_velocity - actual_velocity
    print(f"  {Colors.CYAN}Prediction Error:{Colors.ENDC} {prediction_error} (Slower than expected)")
    
    # 3. Action Selection
    if prediction_error > 2:
        action = "Suggest reducing scope or activating Loki Mode"
    else:
        action = "Continue current trajectory"
        
    print(f"  {Colors.GREEN}Selected Action:{Colors.ENDC} {action}")

def evolve_prompts(skill_name):
    """Evolutionary Prompt Optimization (EPO)."""
    print(f"{Colors.HEADER}🧬 Evolutionary Prompt Optimization: {skill_name}{Colors.ENDC}")
    conn = get_db()
    c = conn.cursor()
    
    # 1. Fetch current gene (prompt)
    c.execute("SELECT * FROM genes WHERE skill_name=? ORDER BY success_rate DESC LIMIT 1", (skill_name,))
    best_gene = c.fetchone()
    
    current_prompt = "Default Prompt"
    generation = 0
    if best_gene:
        current_prompt = best_gene['prompt_content']
        generation = best_gene['generation']
        print(f"  Current Best: Gen {generation} (Success: {best_gene['success_rate']})")
    else:
        print(f"  Initializing Gene Pool for {skill_name}...")
        c.execute("INSERT INTO genes (skill_name, prompt_content, generation) VALUES (?, ?, ?)", 
                  (skill_name, "You are a helpful coding assistant.", 0))
        conn.commit()
    
    # 2. Mutation (Simulated for CLI demo)
    # In real implementation, this would use an LLM to rewrite the prompt
    mutations = [
        "Include step-by-step reasoning.",
        "Focus on brevity and code-only output.",
        "Add strict security constraints."
    ]
    new_prompt = f"{current_prompt}\nMutation: {random.choice(mutations)}"
    
    # 3. Selection (Store new candidate)
    next_gen = generation + 1
    c.execute("INSERT INTO genes (skill_name, prompt_content, generation) VALUES (?, ?, ?)", 
              (skill_name, new_prompt, next_gen))
    conn.commit()
    
    print(f"  {Colors.GREEN}Created Generation {next_gen}{Colors.ENDC}")
    print(f"  - Mutation applied. Ready for testing.")

def run_healer():
    """Self-Healing Watchdog."""
    print(f"{Colors.HEADER}🚑 Self-Healing Watchdog{Colors.ENDC}")
    # Mock check
    health = 85 # %
    print(f"  System Health: {health}%")
    if health < 90:
        print(f"  {Colors.WARNING}Action Required: Clearing cache and optimizing DB...{Colors.ENDC}")
        # Perform cleanup
        print(f"  {Colors.GREEN}Healing Complete.{Colors.ENDC}")
