---
name: k8s-dev
description: Set up development against a remote Kubernetes cluster with Telepresence, Okteto or DevSpace - intercepts, file sync, per-developer namespaces, RBAC. Use when the app is too big for a laptop or needs cloud-only services such as RDS or SQS.
triggers: [develop against remote cluster, telepresence intercept, okteto setup, devspace yaml, per-developer namespace, k8s dev environment]
tags: [ops]
context_cost: medium
---
# Kubernetes Dev Skill

## Goal
To develop directly against a remote Kubernetes cluster, enabling access to cloud dependencies and effectively "infinite" resources.

## Capabilities

### 1. Remote Interception (Telepresence)
-   **Intercept**: Route traffic from a remote service to your laptop.
-   **Debug**: Step through code locally while handling live remote requests.
-   **Preview URLs**: Share a specific intercept version with teammates.

### 2. Sync & Hot Reload (Okteto / DevSpace)
-   **File Sync**: Bi-directional sync between local folder and remote pod.
-   **Terminal**: Get a shell inside the remote pod.
-   **Environment**: Spin up ephemeral namespaces for each developer.

### 3. Configuration
-   **DevSpace**: Generate `devspace.yaml` for pipeline + sync.
-   **Okteto**: Generate `okteto.yaml` for hybrid dev.

## Steps
1.  **When to use**: Recommend Remote Dev when the app is too large for Docker Desktop (RAM/CPU limits) or depends on cloud-only resources (RDS, SQS).
2.  **Isolation**: Ensure developers work in their own Namespaces to avoid stepping on toes.
3.  **Security**: Use RBAC to limit developer permissions in the cluster.

## Deliverables
-   `devspace.yaml` configuration.
-   `telepresence` intercept commands.
-   `okteto.yaml` manifest.

## Constraints
- Each developer works in their own namespace with a time limit.
- Remote development targets dev or staging clusters only.

## Output Format
The files named under Deliverables (`devspace.yaml`, `okteto.yaml`, intercept commands) and the namespace and RBAC manifests.

## Limits and safety
- Never intercept or sync into the production namespace or cluster; check the current kube context before every command.
- Give developers edit and exec rights in their own namespace only, never cluster-admin.
- Set a TTL on developer namespaces; propose the cleanup command for stale ones and run it only after the human confirms.
- Exclude `.env` files and local secret folders from sync to the cluster.
- If your cluster supports network policies, block egress from dev pods to production namespaces.
