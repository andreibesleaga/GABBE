---
name: dev-environments
description: "Set up a team-wide development environment with DevContainers, DevSpace or Docker Compose, with seed data and sample configuration. Use when onboarding is slow, \"works on my machine\" bugs appear, or a project needs a shared dev setup."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/dev-environments.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
---
# dev-environments

## Goal
Automate the setup, orchestration, and maintenance of identical development environments across the team (using DevContainers, DevSpace, or Docker Compose).

## Steps
1. **Analyze Requirements**: Parse the `PLAN.md` to identify all necessary languages, databases, and dependencies.
2. **Configuration**: Generate `DEVCONTAINER_TEMPLATE.json` or `docker-compose.yml` defining the required services.
3. **Scripting**: Write setup scripts for seeding local databases and pulling necessary environment variables.
4. **Verification**: Run `docker-compose build` or equivalent to verify the environment spins up without errors.

## Constraints
- The setup must start from a clean checkout with the commands written in the project docs.
- Use sample values for secrets and seed data; never fetch production values.

## Output Format
The environment files (`.devcontainer/`, `docker-compose.yml` or equivalent), a sample `.env.example`, and the exact start command in the project docs.

## Limits and safety
- Bind-mount only the project directory; do not mount the host root or use `--privileged` unless the human asks for it in that request.
- Bind dev services to 127.0.0.1, not 0.0.0.0, so an unauthenticated dev database is not open to the local network.
- Setup scripts use sample `.env` values and do not download production secrets; check the scripts for production hosts.
- Take base images and scripts from official sources, pinned to a version; do not pipe unknown scripts into a shell.
- Keep the setup working on Linux, macOS and WSL, or say which one is not supported.
