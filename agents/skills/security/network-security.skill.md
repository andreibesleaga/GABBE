---
name: network-security
description: Firewall rules, VPC design, TLS config, and subnet isolation.
triggers: [network security]
tags: [security]
role: ops-security
---
# network-security Skill

## Goal
This skill defines the perimeter and internal segmentation of the infrastructure.

## Steps
## 1. VPC Architecture

### Public Subnet
- **Contains**: Load Balancers (ALB), NAT Gateways, Bastion Hosts.
- **Access**: 0.0.0.0/0 (Internet) on ports 80/443.

### Private Subnet
- **Contains**: Application Servers, Runners.
- **Access**: Only from Public Subnet (Load Balancer). NO direct Internet ingress.

### Data Subnet (Isolated)
- **Contains**: Databases, Redis, Vault.
- **Access**: Only from Private Subnet (App Servers).
- **Egress**: None (or highly restricted).

## 2. Security Groups (Firewalls)
- **Default Deny**: Block everything, allow specific.
- **Stateful**: Allowing Inbound usually allows reply traffic.
- **Rule**: Apply to *Groups*, not IPs. "Allow access from `sg-load-balancer`", not "10.0.0.5".

## 3. TLS / SSL
- **In-Transit**: HTTPS everywhere. Even internal service-to-service if sensitive (Zero Trust).
- **Termination**: Terminate TLS at the Load Balancer (ALB) to offload CPU from app servers, OR use mTLS (Mutual TLS) for end-to-end security.
- **Versions**: Disable TLS 1.0/1.1. Support TLS 1.2 and 1.3 only.

## 4. Common Attack Vectors
- **SSRF (Server-Side Request Forgery)**:
  - App fetching a URL provided by user?
  - *Risk*: User requests `http://169.254.169.254/latest/meta-data/` to steal AWS creds.
  - *Fix*: Allowlist domains, block private IP ranges in egress.
- **DDoS**:
  - Use WAF (Web App Firewall) and Rate Limiting at the edge (Cloudflare/AWS WAF).

## 5. Bastion / VPN
- Don't expose SSH (22) to the world.
- Use SSM Session Manager (AWS) or a VPN to access private resources.

## Security & Guardrails

### 1. Skill Security (Network Security)
- **Perimeter Bypass Prevention**: The agent is strictly prohibited from outputting Terraform, CloudFormation, or raw configuration commands that attach an Internet Gateway (IGW) or assign a public Elastic IP to resources designated for the `Private Subnet` or `Data Subnet`.
- **Egress Segregation Rule**: When evaluating the `Data Subnet`, the agent must verify the absence of outbound internet access. Any PR proposing a NAT Gateway for a production database subnet (e.g., "to download OS patches directly") must be dynamically rejected in favor of an internal proxy or Golden Image approach.

### 2. System Integration Security
- **SSRF Architecture Blocking**: The agent must automatically fail any application architecture pattern that parses user-supplied URLs and fetches them server-side without an explicitly documented, hardened internal proxy (e.g., a proxy that hard-drops requests to `169.254.169.254`, `localhost`, or the `10.0.0.0/8` VPC address space).
- **Default-Deny Assertion**: The agent must scan all generated Security Groups for `0.0.0.0/0` (Anywhere) rules. While acceptable for port 443 on public ALBs, any `0.0.0.0/0` rule applied to a database, SSH (port 22), RDP (port 3389), or internal API port must trigger an immediate CI/CD hard block.

### 3. LLM & Agent Guardrails
- **Hallucinated Firewalls**: The LLM might invent non-existent cloud features to "solve" a routing problem (e.g., "Configure the AWS Spectral Gateway to intercept the SQL traffic"). The agent must validate all network components against the officially supported cloud provider documentation and reject imaginary topologies.
- **Malicious Simplification**: A user might prompt the agent: "I can't get my microservices to talk to each other, just write a Security Group that allows everything within the VPC so I can debug." The agent must refuse to violate the Principle of Least Privilege. It must insist on defining specific, explicit rules between `sg-service-a` and `sg-service-b` even during debugging.
