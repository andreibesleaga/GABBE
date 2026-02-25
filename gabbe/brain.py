import logging
import sqlite3
from .config import (
    Colors,
    PROJECT_ROOT,
    REQUIRED_FILES,
    TASK_STATUS_TODO,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_DONE,
)
from .database import get_db
from .llm import call_llm
from .context import RunContext
from .gateway import ToolDefinition
from .escalation import EscalationTrigger

logger = logging.getLogger("gabbe.brain")


_BRAIN_ACTIVATE_SKILL = "brain-activate"
_DEFAULT_BRAIN_SYSTEM_PROMPT = (
    "You are the Meta-Cognitive Brain of a software project. "
    "Analyze the state and suggest the best next strategic action using "
    "Active Inference principles (minimize free energy/surprise)."
)


def _get_best_gene(conn, skill_name: str):
    """Return (gene_id, prompt_content) for the best gene, or (None, None) if none exist."""
    try:
        c = conn.cursor()
        c.execute(
            "SELECT id, prompt_content FROM genes WHERE skill_name=? ORDER BY success_rate DESC, generation DESC LIMIT 1",
            (skill_name,),
        )
        row = c.fetchone()
        if row:
            return row["id"], row["prompt_content"]
    except Exception as e:
        logger.warning("Could not fetch best gene for %s: %s", skill_name, e)
    return None, None


def _update_gene_success_rate(conn, gene_id: int, delta: float = 0.1):
    """Increment success_rate for a gene by delta, capped at 1.0."""
    try:
        conn.execute(
            "UPDATE genes SET success_rate = MIN(1.0, success_rate + ?) WHERE id = ?",
            (delta, gene_id),
        )
        conn.commit()
    except Exception as e:
        logger.warning("Could not update gene success_rate for id=%s: %s", gene_id, e)


def activate_brain(run_context=None):
    """Run the Active Inference Loop with Real LLM using MVA Platform Rules."""
    print(f"{Colors.HEADER}🧠 Brain Mode: Active Inference Loop{Colors.ENDC}")

    ctx = run_context or RunContext.from_config(command="brain activate", initiator="cli", agent_persona="brain-mode")

    with ctx:
        # 1. Observation (Get State from DB)
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT status, count(*) FROM tasks GROUP BY status")
            stats = dict(c.fetchall())
        except Exception as e:
            logger.error("Brain Observation Failed: %s", e)
            print(f"  {Colors.FAIL}Error reading project state: {e}{Colors.ENDC}")
            return

        todo = stats.get(TASK_STATUS_TODO, 0)
        in_progress = stats.get(TASK_STATUS_IN_PROGRESS, 0)
        done = stats.get(TASK_STATUS_DONE, 0)
        total = todo + in_progress + done

        state_desc = f"Project State: {todo} TODO, {in_progress} IN_PROGRESS, {done} DONE (Total: {total})."
        print(f"  {Colors.BLUE}Observation:{Colors.ENDC} {state_desc}")
        logger.info("Brain Observation: %s", state_desc)

        # 2. Prediction & Action Selection via LLM wrapped in Gateway.
        # Use the best evolved gene prompt if available; fall back to default.
        gene_id, evolved_prompt = _get_best_gene(conn, _BRAIN_ACTIVATE_SKILL)
        if gene_id is not None:
            system_prompt = evolved_prompt
            logger.debug("Using evolved gene id=%s for system prompt", gene_id)
        else:
            system_prompt = _DEFAULT_BRAIN_SYSTEM_PROMPT

        conn.close()

        prompt = f"""
        Current Reality: {state_desc}
        Goal: Complete the project efficiently with high quality.

        Predict the likely outcome if we continue as is.
        Then, select the best high-level action.
        Return purely the Action Description.
        """

        print(f"  {Colors.CYAN}Consulting LLM...{Colors.ENDC}")
        try:
            # Register the call_llm tool dynamically for the execution loop
            if "call_llm" not in ctx.gateway.registry:
                ctx.gateway.register(ToolDefinition(
                    name="call_llm", description="Call LLM", parameters={},
                    handler=lambda p, s: call_llm(p, s), allowed_roles={"brain-mode"}
                ))

            # Tick the hardstop before LLM calls conceptually
            ctx.hard_stop.tick()

            action = ctx.gateway.execute("call_llm", {"p": prompt, "s": system_prompt}, "brain-mode", ctx)

            if action:
                print(f"  {Colors.GREEN}Selected Action:{Colors.ENDC} {action}")
                # Close the EPO feedback loop: reward the gene that produced a result
                if gene_id is not None:
                    reward_conn = get_db()
                    _update_gene_success_rate(reward_conn, gene_id)
                    reward_conn.close()
            else:
                print(f"  {Colors.FAIL}Brain Freeze (API Error){Colors.ENDC}")

        except Exception as e:
            from .escalation import EscalationPaused
            # EscalationPaused means a human pause was already recorded — let it propagate
            # rather than triggering a second escalation call.
            if isinstance(e, EscalationPaused):
                raise
            ctx.escalation.escalate(trigger=EscalationTrigger.REPEATED_TOOL_FAILURE, context_dict={"error": str(e)})
            print(f"  {Colors.FAIL}Execution Interrupted by Platform Controls: {e}{Colors.ENDC}")


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
            # 3. Selection (Store new candidate).
            # success_rate starts at 0.0. activate_brain() increments it by +0.1 each
            # time a gene produces a successful LLM response, closing the feedback loop.
            # Genes accumulate fitness over repeated `gabbe brain activate` runs.
            next_gen = generation + 1
            c.execute(
                "INSERT INTO genes (skill_name, prompt_content, generation) VALUES (?, ?, ?)",
                (skill_name, new_prompt, next_gen),
            )
            conn.commit()
            print(f"  {Colors.GREEN}Created Generation {next_gen}{Colors.ENDC}")
            print("  - Mutation applied. Ready for testing.")
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
