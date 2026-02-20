---
name: network-security
description: Firewall rules, VPC design, TLS config, and subnet isolation.
role: ops-security
triggers:
  - firewall
  - vpc
  - subnet
  - tls
  - ssl
  - port
  - cidr
---

# network-security Skill

This skill defines the perimeter and internal segmentation of the infrastructure.

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
