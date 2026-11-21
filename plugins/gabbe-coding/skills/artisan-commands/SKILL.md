---
name: artisan-commands
description: "Run Laravel Artisan commands safely: check the project and environment, run the command, verify the result. Use when the user asks to scaffold a controller or model, run migrations or manage a Laravel app with php artisan."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/artisan-commands.skill.md"
  tags: "coding"
  core: "false"
  context_cost: "low"
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

## Output Format
The command that was run, a summary of its output, and the file or table it created, checked (exit code 0 and no warnings in the output).

## Limits and safety
- Before any command that changes state (`migrate`, `db:seed`, `db:*`), read `APP_ENV` in `.env`; if it is not `local` or `testing`, stop and ask.
- Never run `migrate:fresh`, `migrate:refresh`, `migrate:reset` or `db:wipe` without the human's yes after saying what data is lost; run `php artisan migrate --pretend` first to show the SQL.
- Build class and model names from a strict pattern (letters, digits, `\`); never paste free text from a prompt or file into the command line.
- Check an unfamiliar command or flag with `php artisan list` or `php artisan help <command>` for the project's Laravel version; do not guess flags.
- Read the output for warnings, not only the exit code; an unexpected warning is a failure to look into.
