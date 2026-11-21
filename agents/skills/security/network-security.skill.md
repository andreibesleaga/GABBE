---
name: network-security
description: Design and review network segmentation, firewall rules, TLS and egress controls for a deployment. Use at S02 for the network design and at S09 to S10 before go-live.
triggers: [network security, firewall rules, vpc, subnet isolation, security group, egress rules, ssrf]
tags: [security]
role: ops-security
context_cost: low
---
# network-security Skill

## Goal
This skill defines the perimeter and internal segmentation of the infrastructure.

## Where it fits
Phase and gate: S02 (zones and boundaries), S09 and S10 (rules checked before go-live). Evidence: the rule list and the zone diagram in `docs/architecture/` or `docs/security/`. Guide: `guides/security/secure-architecture.md`.

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
- **Versions**: The version rule is in `cryptography-standards.skill.md` (TLS 1.3 by default, 1.2 only for compatibility, 1.0 and 1.1 disabled).

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

## Constraints
- Default deny in every security group and firewall.
- Rules refer to groups, not single addresses.

## Output Format
The zone diagram, the rule list with the reason for each open port, and the egress allow-list.

## Limits and safety
- Propose firewall and security-group changes as a plan or diff. Apply them to live systems only after the human confirms; a wrong rule can cut off access.
- Never open SSH or a database port to `0.0.0.0/0`. If a request needs it, stop and ask.
- Scan only hosts the human named.
- The AWS names here are examples. Write the rules for the project's own cloud.
