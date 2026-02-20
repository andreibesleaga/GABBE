---
name: infra-devops
description: Design and implement cloud infrastructure (Terraform/K8s) and CI/CD pipelines.
context_cost: medium
---
# Infra & DevOps Skill

## Triggers
- infra
- terraform
- k8s
- kubernetes
- docker
- cicd
- pipeline
- devops
- aws
- gcp
- azure

## Purpose
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

## Instructions
1.  **Analyze Request**: Determine cloud provider (AWS/GCP/Azure) and tool (Terraform/Pulumi).
2.  **Security First**: Always enable encryption, private subnets, and least privilege.
3.  **Idempotency**: Ensure scripts and manifests can be applied multiple times safeley.
4.  **Cost Awareness**: Recommend spot instances or serverless where appropriate.

## Deliverables
-   `infra/` directory structure.
-   `Dockerfile` optimization (multi-stage builds).
-   `pipeline.yaml` for CI/CD.
