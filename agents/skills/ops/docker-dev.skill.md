---
name: docker-dev
description: Set up local development with Docker - Compose with watch mode, DevContainers, multi-stage Dockerfiles, non-root users, volumes. Use when you containerise an app for local work or fix slow or broken Docker dev setups.
triggers: [docker compose for local dev, containerize this app, devcontainer config, docker compose watch, multi-stage dockerfile, dockerization]
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
4.  **Team-wide setup**: For a shared environment across a team (DevContainer features, seeding, onboarding) see `dev-environments.skill`; for work against a cluster see `k8s-dev.skill`.

## Deliverables
-   `compose.yaml` with watch config.
-   `.devcontainer/` folder.
-   `Dockerfile` (Target: dev & prod).

## Constraints
- Dev and production stages are separate targets of one Dockerfile; the production stage has no dev tools.
- Base images are official and pinned to a version or digest, not `:latest`.

## Output Format
The files named under Deliverables and the command to start and stop the environment.

## Limits and safety
- Do not run dev containers with `--privileged` or mount the host root; keep to project-directory mounts.
- Dev compose files and `.env` hold dummy credentials only; check for production values before finishing.
- Publish ports on 127.0.0.1; if the human asks for 0.0.0.0, warn that the service becomes reachable from the network.
- Keep `USER` set to a non-root user in the final image; fix file permission problems with UID/GID mapping, not by removing it.
- Before you remove volumes or run `docker system prune`, show the command and wait for the human.
