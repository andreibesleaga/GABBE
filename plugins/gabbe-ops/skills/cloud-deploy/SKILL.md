---
name: cloud-deploy
description: "Configure and deploy an app to Vercel, Railway or AWS (SST) with config files in the repo, parity of environments and no hand-set options. Use when you pick a hosting platform or write vercel.json, railway.toml or sst.config.ts."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/cloud-deploy.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
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
3.  **Infrastructure as Code**: Always define the deployment config locally (don't click-ops settings). For Terraform, Kubernetes and pipeline files see `infra-devops.skill`.

## Deliverables
-   `vercel.json`
-   `railway.toml`
-   `sst.config.ts`

## Constraints
- Deployment settings live in files in the repository, not in a web console.
- Environment variable names match across environments; values and secrets do not live in the repository.

## Output Format
The platform config file(s) named under Deliverables, plus a short note in the project docs with the target environment, the command to deploy and the command to roll back.

## Limits and safety
- Show the exact deploy command and a dry run or plan for production, then wait for the human to confirm the target environment.
- If a linter for the config exists in the project (checkov, tfsec, cfn-lint), run it on the generated files before they are committed.
- Do not open ports such as 22 or 3306 to 0.0.0.0/0, even for a test; propose a narrow source range.
- Use short-lived or scoped credentials for the pipeline where the platform provides them; keys and passwords are not written into config files.
