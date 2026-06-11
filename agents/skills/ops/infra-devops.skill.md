---
name: infra-devops
description: Design and implement cloud infrastructure (Terraform/K8s) and CI/CD pipelines.
triggers: [infra, terraform, k8s, kubernetes, docker, cicd, pipeline, devops, aws, gcp, azure]
tags: [ops]
context_cost: medium
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

## Deliverables
-   `infra/` directory structure.
-   `Dockerfile` optimization (multi-stage builds).
-   `pipeline.yaml` for CI/CD.

## Security & Guardrails

### 1. Skill Security (Infra & DevOps)
- **IaC Tamper Evident State**: Terraform/OpenTofu state files (`terraform.tfstate`) generated or modified by the agent must be stored remotely (e.g., S3 backend) with strict versioning, encryption at rest, and state locking (via DynamoDB) to prevent concurrent modification corruption.
- **Template Sanitization**: Any generated Helm charts or Kubernetes manifests must be statically analyzed against CIS (Center for Internet Security) Kubernetes Benchmarks before being committed by the agent.

### 2. System Integration Security
- **Cloud Credential Isolation**: The agent must never embed raw AWS/GCP/Azure credentials into the CI/CD pipeline YAML. It must use OIDC (OpenID Connect) for short-lived, identity-based role assumption between GitHub/GitLab and the target cloud provider.
- **VPC Subnet Strictness**: When generating networking infrastructure, the agent defaults MUST place databases, caching layers, and internal APIs in Private Subnets with no direct internet ingress, requiring explicitly requested NAT Gateways or Bastion hosts for access.

### 3. LLM & Agent Guardrails
- **Public Exposure Veto**: The agent must actively fight against user prompts that request irresponsible public exposure of infrastructure (e.g., "Assign a public IP to the RDS instance so I can connect from home"). It must enforce VPN or SSM session manager alternatives.
- **Destructive Plan Verification**: If the `terraform plan` output indicates the destruction of stateful resources (Databases, S3 Buckets, KMS Keys), the agent MUST halt the workflow and demand human step-up authentication before allowing `terraform apply`.
