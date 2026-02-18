# Development Environments Guide: Local vs. Remote vs. Outer Loop

Choosing the right development environment strategy is critical for velocity. In 2025, we have moved beyond "everything on localhost".

## 1. Strategies Overview

| Strategy | Where Code Runs | Where Deps Run | Best For | Tools |
|---|---|---|---|---|
| **Local Native** | Local OS | Local (Docker) | Simple Microservices, Monoliths | Node, Go, Docker Compose |
| **Local Container**| DevContainer | Docker | Team Consistency, Onboarding | VS Code DevContainers |
| **Remote Bridge**| Local OS | Remote K8s | Microservices dependent on Cloud | Telepresence |
| **Remote Native** | Remote K8s | Remote K8s | Huge Apps, Low-Power Laptops | Okteto, DevSpace, Coder |

## 2. Local Development (Inner Loop)

**The Gold Standard**: `Docker Compose Watch`
-   **Why**: It syncs files to running containers *instantly* without rebuilding.
-   **Config**:
    ```yaml
    services:
      web:
        build: .
        develop:
          watch:
            - action: sync
              path: ./web
              target: /app/web
            - action: rebuild
              path: package.json
    ```

**DevContainers**:
-   **Why**: "It works on my machine" is solved forever. The IDE definitions *are* the environment.
-   **Pro Tip**: Include your linters and extensions in `devcontainer.json`.

## 3. Remote Development (Hybrid Inner Loop)

**When Localhost Fails**:
-   Your app needs 32GB RAM but your laptop has 16GB.
-   You need to talk to 15 downstream microservices.
-   You need proprietary cloud hardware (GPUs).

**Telepresence**:
-   Routes traffic from the cluster *to your laptop*.
-   Allows you to debug a service locally while it thinks it's in the cluster.
-   **Command**: `telepresence intercept my-service --port 8080:8080`

## 4. Outer Loop (Deployment)

This is the CI/CD world.

**Shift Left with Previews**:
-   **Vercel/Railway**: Every Pull Request gets a live URL (`pr-123.myapp.com`).
-   **Value**: QA and Product can test *before* merge.

**Infrastructure as Code**:
-   Never change settings in the AWS Console manually.
-   Use **SST** or **Terraform** so your infrastructure is versioned with your code.

## 5. Recommendation Matrix

| Scenario | Recommend |
|---|---|
| **New Project / MVP** | **Local Native** (Speed is king) |
| **Team > 5 Devs** | **DevContainers** (Consistency is king) |
| **Microservices > 10** | **Remote Bridge** (Resources are bottleneck) |
| **AI / Machine Learning**| **Remote Native** (Need GPUs) |
