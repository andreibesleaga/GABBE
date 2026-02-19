import logging
import sqlite3
import requests
from .config import Colors
from .database import get_db
from .llm import call_llm

logger = logging.getLogger("gabbe.brain")


def activate_brain():
    """Run the Active Inference Loop with Real LLM."""
    print(f"{Colors.HEADER}🧠 Brain Mode: Active Inference Loop{Colors.ENDC}")

    # 1. Observation (Get State from DB)
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT status, count(*) FROM tasks GROUP BY status")
        stats = dict(c.fetchall())
        conn.close()
    except sqlite3.Error as e:
        logger.error("Brain Observation Failed (DB): %s", e)
        print(f"  {Colors.FAIL}Error reading project state: {e}{Colors.ENDC}")
        return
    except Exception as e:
        logger.error("Brain Observation Failed: %s", e)
        print(f"  {Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        return

    todo = stats.get("TODO", 0)
    in_progress = stats.get("IN_PROGRESS", 0)
    done = stats.get("DONE", 0)
    total = todo + in_progress + done

    state_desc = f"Project State: {todo} TODO, {in_progress} IN_PROGRESS, {done} DONE (Total: {total})."
    print(f"  {Colors.BLUE}Observation:{Colors.ENDC} {state_desc}")
    logger.info("Brain Observation: %s", state_desc)

    # 2. Prediction & Action Selection via LLM
    system_prompt = (
        "You are the Meta-Cognitive Brain of a software project. "
        "Analyze the state and suggest the best next strategic action using "
        "Active Inference principles (minimize free energy/surprise)."
    )
    prompt = f"""
    Current Reality: {state_desc}
    Goal: Complete the project efficiently with high quality.

    Predict the likely outcome if we continue as is.
    Then, select the best high-level action (e.g., "Focus on critical path",
    "Stop and Refactor", "Add more tests").
    Return purely the Action Description.
    """

    print(f"  {Colors.CYAN}Consulting LLM...{Colors.ENDC}")
    action = call_llm(prompt, system_prompt)

    if action:
        print(f"  {Colors.GREEN}Selected Action:{Colors.ENDC} {action}")
        logger.info("Brain Selected Action: %s", action)
    else:
        print(f"  {Colors.FAIL}Brain Freeze (API Error){Colors.ENDC}")


def evolve_prompts(skill_name):
    """Evolutionary Prompt Optimization (EPO) with Real LLM."""
    print(
        f"{Colors.HEADER}🧬 Evolutionary Prompt Optimization: {skill_name}{Colors.ENDC}"
    )
    conn = get_db()
    try:
        c = conn.cursor()

        # 1. Fetch current gene (prompt)
        c.execute(
            "SELECT * FROM genes WHERE skill_name=? ORDER BY success_rate DESC LIMIT 1",
            (skill_name,),
        )
        best_gene = c.fetchone()

        current_prompt = "You are a helpful coding assistant."
        generation = 0
        if best_gene:
            current_prompt = best_gene["prompt_content"]
            generation = best_gene["generation"]
            print(
                f"  Current Best: Gen {generation} (Success: {best_gene['success_rate']})"
            )
        else:
            print(f"  Initializing Gene Pool for {skill_name}...")
            c.execute(
                "INSERT INTO genes (skill_name, prompt_content, generation) VALUES (?, ?, ?)",
                (skill_name, current_prompt, 0),
            )
            conn.commit()

        # 2. Mutation via LLM
        print(f"  {Colors.CYAN}Mutating via LLM...{Colors.ENDC}")
        system_prompt = "You are an Expert Prompt Engineer. Optimize the given prompt for an AI Coding Agent."
        mutation_request = f"""
        Current Prompt: "{current_prompt}"

        Task: Rewrite this prompt to be more effective, precise, and robust.
        Add constraints or better context.
        Return ONLY the new prompt text.
        """

        new_prompt = call_llm(mutation_request, system_prompt)

        if new_prompt:
            # 3. Selection (Store new candidate)
            next_gen = generation + 1
            c.execute(
                "INSERT INTO genes (skill_name, prompt_content, generation) VALUES (?, ?, ?)",
                (skill_name, new_prompt, next_gen),
            )
            conn.commit()
            print(f"  {Colors.GREEN}Created Generation {next_gen}{Colors.ENDC}")
            print(f"  - Mutation applied. Ready for testing.")
        else:
            print(f"  {Colors.FAIL}Mutation Failed (API Error){Colors.ENDC}")
    except sqlite3.Error as e:
        logger.error("Evolution Failed (DB): %s", e)
        print(f"  {Colors.FAIL}Database error during evolution: {e}{Colors.ENDC}")
    except Exception as e:
        logger.error("Evolution Failed: %s", e)
        print(f"  {Colors.FAIL}Error evolving prompt: {e}{Colors.ENDC}")
    finally:
        conn.close()


def run_healer():
    """Self-Healing Watchdog: checks DB connectivity and required files."""
    print(f"{Colors.HEADER}🚑 Self-Healing Watchdog{Colors.ENDC}")
    from .config import PROJECT_ROOT, REQUIRED_FILES

    issues = []

    # 1. Check DB connectivity
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        print(f"  {Colors.GREEN}✓ Database: Reachable{Colors.ENDC}")
    except sqlite3.Error as e:
        issues.append(f"Database unreachable: {e}")
        print(f"  {Colors.FAIL}✗ Database: {e}{Colors.ENDC}")
    except Exception as e:
        issues.append(f"Database unexpected error: {e}")
        print(f"  {Colors.FAIL}✗ Database (Unknown): {e}{Colors.ENDC}")

    # 2. Check required project files (defined centrally in config.py)
    for path in REQUIRED_FILES:
        if path.exists():
            print(
                f"  {Colors.GREEN}✓ {path.relative_to(PROJECT_ROOT)}: Present{Colors.ENDC}"
            )
        else:
            issues.append(f"Missing file: {path.relative_to(PROJECT_ROOT)}")
            print(
                f"  {Colors.FAIL}✗ {path.relative_to(PROJECT_ROOT)}: Missing{Colors.ENDC}"
            )

    # 3. Summary
    if issues:
        print(f"\n  {Colors.FAIL}Health Issues Found ({len(issues)}):{Colors.ENDC}")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n  {Colors.GREEN}System Health: Nominal{Colors.ENDC}")
