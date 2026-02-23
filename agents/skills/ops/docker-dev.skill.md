---
name: docker-dev
description: Assistance with Local Development using Docker (Compose, DevContainers).
triggers: [docker, compose, local dev, devcontainer, dev environment, containerize, dockerization]
tags: [ops]
context_cost: medium
---
# Docker Dev Skill

## Goal
To set up robust, reproducible local development environments using Docker technologies.

## Capabilities

### 1. Docker Compose (Local Dev)
-   **Generate `compose.yaml`**: Define services (App + DB + Redis).
-   **Watch Mode**: Configure `develop.watch` for hot-reloading (sync + rebuild).
-   **Networking**: Ensure services can talk to each other (and to host if needed).

### 2. DevContainers (VS Code)
-   **Configuration**: Generate `.devcontainer/devcontainer.json`.
-   **Features**: Add standard features (git, node, python, docker-in-docker).
-   **Extensions**: Pre-install VS Code extensions for the team.

### 3. Optimization
-   **Multi-stage Builds**: Separate build-deps from runtime-deps.
-   **Caching**: Optimize layer ordering for faster builds.
-   **Distroless**: Use distroless images for production (keep shells in dev).

## Steps
1.  **Prefer Compose Watch**: Always recommend `docker compose watch` over legacy volume mounts for code sync.
2.  **User Mapping**: Ensure file permissions work by mapping non-root user (UID/GID) inside container.
3.  **Persistence**: Use Docker Volumes for DB data so it survives restarts.

## Deliverables
-   `compose.yaml` with watch config.
-   `.devcontainer/` folder.
-   `Dockerfile` (Target: dev & prod).

## Security & Guardrails

### 1. Skill Security (Docker Dev)
- **Container Escape Mitigation**: Developer containers must avoid running in `--privileged` mode or mounting the host's root filesystem (`-v /:/host`) unless absolutely necessary, to mitigate the risk of a compromised dev environment rooting the developer's laptop.
- **Trusted Base Images**: Dockerfiles must inherit from official, verified registries (e.g., `node:22-alpine` over a random community image) and use explicit SHAs or tagged versions rather than the mutable `:latest` tag.

### 2. System Integration Security
- **Credential Segregation**: The local development `compose.yaml` and `.env` files must NEVER contain production secrets. Use dummy credentials (e.g., `POSTGRES_PASSWORD=devpassword`) to ensure accidental container leaks do not expose live systems.
- **Multi-Stage Build Sanitization**: Ensure the transition from `dev` to `prod` build stages aggressively strips developer tools (curl, vim, compilers) and test suites, minimizing the attack surface of the final runtime image.

### 3. LLM & Agent Guardrails
- **Host Network Exfiltration Warning**: If a user prompts the agent to map standard internal ports to `0.0.0.0` (all interfaces) rather than `127.0.0.1` (localhost), the agent must issue a strong warning about the risk of exposing the local development server to the public internet/local coffee shop network.
- **Root User Restriction**: The LLM must be trained to automatically insert `USER appuser` directives near the end of generated Dockerfiles and vehemently resist prompts that request removing it "to make file permissions easier."
