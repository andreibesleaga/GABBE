---
name: cloud-deploy
description: Deploy applications to modern cloud platforms (Vercel, Railway, AWS).
triggers: [deploy, vercel, railway, aws, sst, serverless, lambda, flightcontrol, neon, supabase]
tags: [ops]
context_cost: medium
---
# Cloud Deploy Skill

## Goal
To configure rapid, developer-friendly deployments on modern PaaS and Serverless platforms.

## Capabilities

### 1. Vercel (Frontend & Edge)
-   **Config**: `vercel.json` for headers, redirects, and clean URLs.
-   **Edge Functions**: Deploying middleware and lightweight backend logic.
-   **Preview Mode**: Setting up preview comments on PRs.

### 2. Railway (Backend & DBs)
-   **Config**: `railway.toml` for build commands and monorepo root.
-   **Databases**: Provisioning Postgres, Redis, MySQL plugins.
-   **Variables**: Managing secrets and environment variables.

### 3. AWS (SST / CDK)
-   **SST**: Defining `sst.config.ts` for serverless stacks (Next.js, API Gateway, DynamoDB).
-   **Constructs**: Using high-level constructs for easy setup (Cron, Bucket, Queue).
-   **IAM**: Setting up fine-grained permissions for functions.

## Steps
1.  **Platform Choice**:
    -   **Frontend/Fullstack JS**: Vercel.
    -   **Docker/Stateful/Backend**: Railway.
    -   **Enterprise/Complex/Serverless**: AWS (via SST).
2.  **Environment Parity**: Ensure `.env` vars match across local and cloud (but values differ).
3.  **Infrastructure as Code**: Always define the deployment config locally (don't click-ops settings).

## Deliverables
-   `vercel.json`
-   `railway.toml`
-   `sst.config.ts`

## Security & Guardrails

### 1. Skill Security (Cloud Deploy)
- **Declarative Infrastructure Validation**: The agent must run security linters (e.g., `checkov`, `tfsec`, `cfn-lint`) against generated `sst.config.ts` or `railway.toml` files locally before they are ever committed, detecting overly permissive IAM roles or public buckets early.
- **Immutable Artifacts**: Ensure deployment pipelines treat builds as immutable artifacts. The exact container or bundle built in Staging must be promoted to Production, preventing "works on my machine" hidden vulnerabilities.

### 2. System Integration Security
- **Least Privilege Deployments**: CI/CD runners executing the cloud deployment commands must operate under scoped roles (e.g., AWS IAM OIDC) with the minimum permissions required, eliminating the use of long-lived, omnipotent Admin Access Keys.
- **Secret Zero Strategy**: Hardcoded API keys, DB passwords, or certificates in `vercel.json` or `.env` files are strictly forbidden. The deploy skill must orchestrate the secure retrieval of variables from a designated Secret Manager (e.g., AWS Secrets Manager, Doppler) at runtime.

### 3. LLM & Agent Guardrails
- **Blind Configuration Defense**: The agent must explicitly refuse user requests to generate blanket open network security groups (e.g., `Allow 0.0.0.0/0 on Port 22/3306`) even if the user claims it is "just for testing."
- **Deployment Confirmation Gates**: When tasked with modifying Production deployment configurations via PaaS APIs, the agent must output a dry-run confirmation plan and halt execution, requiring explicit human intervention to verify that the target environment is correct.
