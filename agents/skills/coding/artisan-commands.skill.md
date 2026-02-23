---
name: artisan-commands
description: Execute Laravel Artisan commands safely
triggers: [artisan, laravel, php artisan, make controller, migrate]
tags: [coding]
context_cost: low
---
# Artisan Commands Skill

## Goal
Execute Laravel Artisan commands to scaffold code, run migrations, or manage the application state.

## Steps

1. **Verify Context**
   - Ensure you are in the root of a Laravel project (look for `artisan` file).
   - If not found, stop and ask user for correct directory.

2. **Construct Command**
   - Use `php artisan <command> <arguments>`.
   - Examples:
     - `php artisan make:controller UserController`
     - `php artisan make:model Post -m`
     - `php artisan migrate:status`
   - NEVER run `migrate:fresh` or destructive commands without explicit user confirmation.

3. **Execute**
   - Run the command using `run_command`.
   - Capture output.

4. **Verify**
   - Check exit code is 0.
   - Verify the expected file was created (e.g., `app/Http/Controllers/UserController.php`).
   - If migration, verify table exists (using command output).

## Constraints
- Do NOT run commands that wipe data (`migrate:fresh`, `db:wipe`) without asking.
- Do NOT run `tinker` in a way that hangs the shell (interactive mode).

## Security & Guardrails

### 1. Skill Security (Artisan Commands)
- **Command Injection Prevention**: Artisan commands accept arguments. If an agent constructs a command using unsanitized input from a user prompt or external file (e.g., `php artisan make:model ${userInput}`), it creates a critical command injection vulnerability. The agent must strictly validate all arguments against a strict alphanumeric allow-list before executing any `run_command` invocation.
- **Destructive Command Veto**: The skill explicitly forbids `migrate:fresh` without human approval. However, an attacker might try to bypass this by asking the agent to run `db:wipe` or alias commands. The agent must maintain a hardcoded, immutable denylist of destructive Artisan commands and automatically abort execution if any match is detected, regardless of the surrounding context or user justification.

### 2. System Integration Security
- **Production Environment Lockout**: Artisan commands behave differently depending on the `.env` file. If the agent accidentally runs a migration or seeder in a production environment (where `APP_ENV=production`), it could corrupt live data. The agent must physically verify that the environment is strictly local/development (`APP_ENV=local` or `testing`) before executing any state-mutating Artisan command.
- **Tinker Sandbox Escape**: The `tinker` command provides a full interactive PHP shell. If an agent executes `tinker` and passes it arbitrary PHP code derived from an untrusted source, it achieves Remote Code Execution (RCE) on the host framework. The agent must either categorically refuse to run `tinker` autonomously or restrict its usage to strictly sandboxed, read-only queries with hard timeouts.

### 3. LLM & Agent Guardrails
- **Hallucinated Artisan Signatures**: The LLM might hallucinate non-existent flags for valid commands (e.g., `php artisan make:controller --secure`) or entirely fictitious commands. Executing hallucinated commands can lead to unpredictable application states or silent failures. The agent must verify the exact syntax against the project's specific Laravel version documentation before execution.
- **Confirmation Bias in Verification**: In Step 4, the agent checks if the exit code is 0. An LLM might assume 0 means "success and safe" even if the command output contains prominent warning messages (e.g., "Warning: Data truncated"). The agent must semantically parse the `stdout` and `stderr` streams, treating any unexpected warning as a hard failure requiring re-evaluation.
