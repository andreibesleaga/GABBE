---
name: infra-devops
description: "Write infrastructure as code (Terraform, OpenTofu), Kubernetes manifests and CI/CD pipelines with least privilege, private networks and remote state. Use when you create or change cloud infrastructure, Helm charts or pipeline files."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/infra-devops.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
---
# Infra & DevOps Skill

## Goal
To assist with Infrastructure as Code (IaC), container orchestration, and automated delivery pipelines.

## Capabilities

### 1. Infrastructure as Code (Terraform/OpenTofu)
-   **Generate Modules**: VPC, RDS, EKS/GKE, Lambda/CloudRun.
-   **Best Practices**: State locking, module modularity, tagging strategies.
-   **Security**: IAM least privilege, security groups, encryption at rest.

### 2. Kubernetes (K8s)
-   **Manifests**: Deployments, Services, Ingress, ConfigMaps, Secrets.
-   **Helm**: Chart creation and value overrides.
-   **Debug**: `kubectl` commands for troubleshooting pods/nodes.

### 3. CI/CD Pipelines
-   **GitHub Actions / GitLab CI**: Workflow generation.
-   **Steps**: Build, Test, Security Scan, Push Registry, Deploy.
-   **GitOps**: ArgoCD configuration.

## Steps
1.  **Analyze Request**: Determine cloud provider (AWS/GCP/Azure) and tool (Terraform/Pulumi).
2.  **Security First**: Always enable encryption, private subnets, and least privilege.
3.  **Idempotency**: Ensure scripts and manifests can be applied multiple times safeley.
4.  **Cost Awareness**: Recommend spot instances or serverless where appropriate.
5.  **Hosting platforms**: For Vercel, Railway or AWS SST deployments see `cloud-deploy.skill`.

## Deliverables
-   `infra/` directory structure.
-   `Dockerfile` optimization (multi-stage builds).
-   `pipeline.yaml` for CI/CD.

## Constraints
- State is stored remotely with locking and versioning, never committed.
- Databases and internal services sit in private networks with no public address.

## Output Format
The files named under Deliverables (`infra/`, Dockerfile, pipeline file) and the plan output of the IaC tool for the human to review.

## Limits and safety
- Run `terraform plan` (or the tool's equivalent) first and show it; `apply` and `destroy` are proposed with the exact command and run only after the human confirms.
- If the plan destroys a database, bucket or key, stop and report; do not apply.
- Use short-lived identity-based credentials (OIDC) in pipelines where the platform provides them; no raw cloud keys in pipeline files.
- Do not give a database a public IP; propose a VPN or session-manager route instead.
- If a linter or benchmark scan (checkov, tfsec, CIS checks) is installed, run it on the generated files before they are committed.
