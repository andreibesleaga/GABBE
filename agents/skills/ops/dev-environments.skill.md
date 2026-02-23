---
name: dev-environments
description: Set up, configure, and maintain local/remote development environments
triggers: [setup dev environment, configure docker compose, build devcontainer]
tags: [ops]
context_cost: medium
---
# dev-environments

## Goal
Automate the setup, orchestration, and maintenance of identical development environments across the team (using DevContainers, DevSpace, or Docker Compose).


## Steps
1. **Analyze Requirements**: Parse the `PLAN.md` to identify all necessary languages, databases, and dependencies.
2. **Configuration**: Generate `DEVCONTAINER_TEMPLATE.json` or `docker-compose.yml` defining the required services.
3. **Scripting**: Write setup scripts for seeding local databases and pulling necessary environment variables.
4. **Verification**: Run `docker-compose build` or equivalent to verify the environment spins up without errors.

## Security & Guardrails

### 1. Skill Security
- **Local Sandbox Escape**: Do not map the entire host filesystem to the container (e.g., `-v /:/host`). Bind-mount only the project directory.
- **Privileged Mode Veto**: Never run development containers with `--privileged` flags unless explicitly requested and warning the user of root compromises.

### 2. System Integration Security
- **Port Collision & Exposure**: Ensure local development environments do not accidentally bind ports to `0.0.0.0` on the host, exposing unauthenticated dev databases to the local LAN.
- **Production Secret Pollution**: The development setup scripts MUST use dummy/sample `.env` variables and verify they do not download production secrets.

### 3. LLM & Agent Guardrails
- **Dependency Hallucination**: The LLM must not inject outdated, unsigned/unverified third-party scripts into the Dockerfiles.
- **OS Bias**: Development environments must remain cross-platform (Linux/Mac/WSL). The LLM cannot implement a solution that breaks for developers not matching its assumed OS.
