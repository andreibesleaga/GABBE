# MCP Server Configurations Guide

> **Audience:** users wiring MCP servers. **Scope:** install/config/usage for every supported MCP server (package names verified 2026-06-10).

Comprehensive installation, configuration, and usage guide for every MCP (Model Context Protocol) server supported by the GABBE kit.

> **Config file**: `agents/templates/core/MCP_CONFIG_TEMPLATE.json`
> **How to apply**: Copy the relevant server entry into your tool's MCP config (Claude `.mcp.json`, VS Code `.vscode/mcp.json`, Cursor settings, etc.) and restart.
> **Prerequisites**: Node.js 18+ and `npx` available in PATH for all `npx`-based servers.

> [!IMPORTANT]
> **Package names verified 2026-06-10** against the npm/PyPI registries. Several
> entries were corrected to their current upstream package (e.g. Context7 →
> `@upstash/context7-mcp`, Sentry → `@sentry/mcp-server`, Stripe → `@stripe/mcp`,
> Azure → `@azure/mcp`). The `@modelcontextprotocol/server-*` reference servers
> are **archived** (still installable, no longer maintained) — prefer official
> successors where they exist (e.g. the GitHub MCP is now the Go
> `github-mcp-server`/Docker image).
>
> **Hosted / desktop servers (no `npx` package)** — connect via the vendor's URL
> or app instead of installing: **Zapier** (per-user URL at `mcp.zapier.com`),
> **Vercel** (hosted MCP + `@vercel/mcp-adapter` to build your own), **Datadog**
> (hosted MCP), **Figma** (Dev Mode MCP in the Figma desktop app), **Docker**
> (MCP Toolkit in Docker Desktop). **AWS** ships `awslabs.*` servers on PyPI;
> **Grafana** ships the Go `mcp-grafana`; **HashiCorp Terraform** ships a
> Docker/Go `terraform-mcp-server`; **Confluence/Jira** use community Atlassian
> servers (e.g. `mcp-atlassian`, `@aashari/mcp-server-atlassian-*`). The
> `@anthropic/mcp-server-shell` entry has no published package and should not be
> used. See `OpenSourceAudit/projects/GABBE/mcp-verification-2026-06.md` for the
> full per-server status.

---

## Table of Contents

1. [Essential Servers](#1-essential-servers)
2. [Version Control & Project Management](#2-version-control--project-management)
3. [Databases](#3-databases)
4. [Security & Code Quality](#4-security--code-quality)
5. [Observability & Monitoring](#5-observability--monitoring)
6. [Browser & Web](#6-browser--web)
7. [Cloud & Infrastructure](#7-cloud--infrastructure)
8. [Design & Visual Architecture](#8-design--visual-architecture)
9. [Knowledge Bases & Vector Databases](#9-knowledge-bases--vector-databases)
10. [Project Management & Collaboration](#10-project-management--collaboration)
11. [API Introspection & Knowledge](#11-api-introspection--knowledge)
12. [Payments & Automation](#12-payments--automation)
13. [Security Rules & Best Practices](#13-security-rules--best-practices)
14. [Environment Variables Summary](#14-environment-variables-summary)

---

> **GABBE's own MCP server (`gabbe serve-mcp`) hardens its tool inputs.** The
> `run_command` tool input is a single bounded JSON Schema contract: the `command`
> string is constrained by **charset** (a `pattern` forbidding control characters
> and NUL) and **length** (`maxLength`), with `additionalProperties: false`. This
> defends against injection-via-tool-feedback and oversized payloads (MCP-38
> threat taxonomy / NSA MCP guidance) and is regression-tested by
> `gabbe/tests/test_mcp_contract.py`. When authoring downstream MCP tool schemas,
> apply the same rule: never expose a `type: "string"` input without bounding its
> length and character set.

## 1. Essential Servers

These servers are recommended for **every project**.

---

### Context7

Up-to-date SDK documentation — prevents the agent from hallucinating deprecated APIs.

| Property | Value |
|---|---|
| **Package** | `@upstash/context7-mcp` |
| **Website** | [context7.com](https://context7.com) |
| **API Key** | None required |
| **GABBE Skill** | `research.skill`, all coding skills |

**Install & Config:**
```json
{
  "context7": {
    "command": "npx",
    "args": ["@upstash/context7-mcp"],
    "env": {}
  }
}
```

**Usage:**
```
> "Use Context7 to look up the latest Next.js App Router API before implementing."
```

---

### Sequential Thinking

Structured chain-of-thought reasoning before acting. Improves planning quality for complex tasks.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-sequential-thinking` |
| **Website** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **API Key** | None required |
| **GABBE Skill** | `brain/sequential-thinking.skill` |

**Install & Config:**
```json
{
  "sequential-thinking": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
    "env": {}
  }
}
```

---

### Brave Search

Authoritative web research with source filtering. Powers the `research.skill`.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-brave-search` |
| **Website** | [brave.com/search/api](https://brave.com/search/api/) |
| **API Key** | **Required**: `BRAVE_API_KEY` |
| **Get API Key** | [api.search.brave.com/register](https://api.search.brave.com/register) (free tier available) |
| **GABBE Skill** | `core/research.skill` |

**Install & Config:**
```json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"
    }
  }
}
```

**Usage:**
```
> "Research the latest OAuth 2.1 specification changes using authoritative sources."
```

---

### Filesystem

Read-only access to local project files for knowledge ingestion (internal RAG).

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-filesystem` |
| **Website** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **API Key** | None required |
| **Security** | Restrict path argument to project directory only |
| **GABBE Skill** | `core/knowledge-connect.skill` |

**Install & Config:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"],
    "env": {}
  }
}
```

> [!WARNING]
> Never pass system directories (`/etc`, `/home`, `~`) as the path argument. Restrict to `./` (project root).

---

## 2. Version Control & Project Management

---

### GitHub

PR review, code search, issue management, and git history.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-github` |
| **Website** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **API Key** | **Required**: `GITHUB_TOKEN` (Personal Access Token with `repo` scope) |
| **Get API Key** | GitHub → Settings → Developer Settings → Personal Access Tokens |
| **GABBE Skill** | `coding/git-workflow.skill`, `coding/code-review.skill` |

**Install & Config:**
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

**Usage:**
```
> "Create a PR from feature/auth to main with a summary of changes."
> "Search for all open issues labeled 'bug' in this repo."
```

---

### GitHits

Lets the agent **navigate the open-source code your app depends on**. Your agent can already read your local codebase; GitHits extends that reach to your dependencies — searching, grepping, and reading source, docs, issues, PRs, and changelogs of packages **without cloning them locally**. Acts like Context7 for dependency *source code* (not just SDK docs), preventing the agent from hallucinating a dependency's API or upgrade behaviour.

| Property | Value |
|---|---|
| **Package** | `githits` (npm) |
| **Website** | [githits.com](https://githits.com) · [docs.githits.com](https://docs.githits.com/) |
| **API Key** | None required |
| **GABBE Skill** | `research.skill`, `coding/code-review.skill`, `security/dependency-security.skill` |

**Capabilities:** code examples (real implementation patterns from repos/issues/discussions/PRs of your deps), code navigation (dependency search, source grep, package-path resolution, line-range reads), documentation access (hosted + repo-backed package docs), and package inspection (metadata, vulnerabilities, changelogs, upgrade context).

**Install (automatic — recommended):**
```bash
# Detects your tool (Claude Code, Cursor, VS Code/Copilot, Windsurf, Cline,
# Claude Desktop, Codex CLI, Gemini CLI, OpenCode, …) and wires up the MCP server.
npx githits@latest init
```

**Config (manual — universal stdio entry):**
```json
{
  "githits": {
    "command": "npx",
    "args": ["-y", "githits@latest", "mcp", "start"],
    "env": {}
  }
}
```

> [!NOTE]
> The server runs as a local stdio subprocess — no background service, global install, env vars, or remote HTTP URL required. For tools not auto-detected, add the manual config above and restart, then confirm `githits` shows as a connected server. See [docs.githits.com/installation/manual-setup](https://docs.githits.com/installation/manual-setup).

**Usage:**
```
> "Use GitHits to find how `fastapi` implements dependency injection in its source."
> "Read the changelog and breaking changes for the `pydantic` v1 → v2 upgrade."
> "Grep the `react` dependency source for how `useEffect` cleanup is scheduled."
```

---

### GitLab

GitLab alternative to the GitHub MCP. Same capabilities for GitLab-hosted repos.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-gitlab` |
| **Website** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **API Key** | **Required**: `GITLAB_TOKEN` (Personal Access Token) |
| **Get API Key** | GitLab → Preferences → Access Tokens |

**Install & Config:**
```json
{
  "gitlab": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-gitlab"],
    "env": {
      "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_TOKEN}",
      "GITLAB_API_URL": "https://gitlab.com"
    }
  }
}
```

---

## 3. Databases

---

### PostgreSQL (Dev)

Read-write PostgreSQL access for development environments.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-postgres` |
| **Website** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **API Key** | **Required**: `DATABASE_URL_DEV` (connection string) |
| **GABBE Skill** | `data/db-migration.skill`, `data/sql-optimization.skill` |

**Install & Config:**
```json
{
  "postgres-dev": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": {
      "POSTGRES_CONNECTION_STRING": "${DATABASE_URL_DEV}"
    }
  }
}
```

> [!CAUTION]
> **DEVELOPMENT ONLY** — never use read-write access in production. See `postgres-prod` for production config.

---

### PostgreSQL (Prod — Read-Only)

Read-only PostgreSQL for production schema introspection. Enable only when needed.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-postgres` |
| **API Key** | **Required**: `DATABASE_URL_PROD_READONLY` |
| **Security** | Read-only access enforced by database user permissions |

**Install & Config:**
```json
{
  "postgres-prod": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": {
      "POSTGRES_CONNECTION_STRING": "${DATABASE_URL_PROD_READONLY}"
    }
  }
}
```

---

### GreptimeDB

Time-series analytics and robust metrics logging.

| Property | Value |
|---|---|
| **Package** | `greptimedb-mcp-server` |
| **Website** | [greptime.com](https://greptime.com) |
| **API Key** | **Required**: `GREPTIME_HOST`, `GREPTIME_DB`, `GREPTIME_USERNAME`, `GREPTIME_PASSWORD` |

**Install & Config:**
```json
{
  "greptime": {
    "command": "npx",
    "args": ["-y", "greptimedb-mcp-server"],
    "env": {
      "GREPTIME_HOST": "${GREPTIME_HOST}",
      "GREPTIME_DB": "${GREPTIME_DB}",
      "GREPTIME_USERNAME": "${GREPTIME_USERNAME}",
      "GREPTIME_PASSWORD": "${GREPTIME_PASSWORD}"
    }
  }
}
```

---

### ClickHouse

Agentic OLAP and real-time reporting.

| Property | Value |
|---|---|
| **Package** | `mcp-clickhouse` |
| **Website** | [clickhouse.com](https://clickhouse.com) |
| **API Key** | **Required**: `CLICKHOUSE_URL`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` |

**Install & Config:**
```json
{
  "clickhouse": {
    "command": "npx",
    "args": ["-y", "mcp-clickhouse"],
    "env": {
      "CLICKHOUSE_URL": "${CLICKHOUSE_URL}",
      "CLICKHOUSE_USER": "${CLICKHOUSE_USER}",
      "CLICKHOUSE_PASSWORD": "${CLICKHOUSE_PASSWORD}"
    }
  }
}
```

---

### MongoDB

MongoDB exploration, queries, and collection management.

| Property | Value |
|---|---|
| **Package** | `mongodb-lens` |
| **Website** | [mongodb.com](https://www.mongodb.com) |
| **API Key** | **Required**: `MONGODB_URI` (connection string) |

**Install & Config:**
```json
{
  "mongodb": {
    "command": "npx",
    "args": ["-y", "mongodb-lens"],
    "env": {
      "MONGODB_CONNECTION_STRING": "${MONGODB_URI}"
    }
  }
}
```

---

### Redis

Redis key-value interaction and management.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-redis` |
| **Website** | [redis.io](https://redis.io) |
| **API Key** | **Required**: `REDIS_URL` (e.g., `redis://localhost:6379`) |
| **GABBE Skill** | `ops/caching-strategy.skill` |

**Install & Config:**
```json
{
  "redis": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-redis"],
    "env": {
      "REDIS_URL": "${REDIS_URL}"
    }
  }
}
```

---

### SQLite

SQLite database explorer (read-only recommended).

| Property | Value |
|---|---|
| **Package** | `sqlite-mcp` |
| **API Key** | None — local file path |

**Install & Config:**
```json
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "sqlite-mcp"],
    "env": {
      "SQLITE_PATH": "./database.sqlite"
    }
  }
}
```

---

### DBHub (Universal)

Universal database client supporting MySQL, MariaDB, PostgreSQL, and SQL Server.

| Property | Value |
|---|---|
| **Package** | `@bytebase/dbhub` |
| **Website** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **API Key** | None (uses local DB connections) |

**Install & Config:**
```json
{
  "dbhub": {
    "command": "npx",
    "args": ["-y", "@bytebase/dbhub"],
    "env": {}
  }
}
```

---

## 4. Security & Code Quality

---

### Semgrep

SAST code scanning, security analysis with custom rules.

| Property | Value |
|---|---|
| **Package** | `semgrep_mcp` (Python) |
| **Website** | [semgrep.dev](https://semgrep.dev) |
| **API Key** | Optional: `SEMGREP_APP_TOKEN` |
| **Get API Key** | [semgrep.dev/settings/tokens](https://semgrep.dev/settings/tokens) |
| **Prerequisite** | `pip install semgrep` |
| **GABBE Skill** | `security/security-audit.skill` |

**Install & Config:**
```bash
pip install semgrep
```
```json
{
  "semgrep": {
    "command": "python",
    "args": ["-m", "semgrep_mcp"],
    "env": {
      "SEMGREP_APP_TOKEN": "${SEMGREP_APP_TOKEN}"
    }
  }
}
```

---

### Time Complexity

Estimates Big-O time complexity via static analysis using tree-sitter. No code execution.

| Property | Value |
|---|---|
| **Package** | Local build — `time-complexity-mcp` |
| **Website** | [github.com/Luzgan/time-complexity-mcp](https://github.com/Luzgan/time-complexity-mcp) |
| **API Key** | None required |
| **Prerequisite** | Node.js 18+, `git` (for `analyze_github_repo`) |
| **GABBE Skill** | `coding/time-complexity.skill` |
| **GABBE Guide** | `guides/patterns/time-complexity-analysis.md` |
| **GABBE Template** | `templates/coding/TIME_COMPLEXITY_REPORT_TEMPLATE.md` |

**Install (from release — recommended):**
```bash
# Download from https://github.com/Luzgan/time-complexity-mcp/releases/latest
tar xzf time-complexity-mcp-linux-x64-v*.tar.gz
```

**Install (from source):**
```bash
git clone https://github.com/Luzgan/time-complexity-mcp.git
cd time-complexity-mcp
npm install
npm run build
```

**Config:**
```json
{
  "time-complexity": {
    "command": "node",
    "args": ["/absolute/path/to/time-complexity-mcp/dist/index.js"],
    "env": {}
  }
}
```

**Tools provided:** `analyze_file`, `analyze_function`, `analyze_directory`, `analyze_github_repo`, `get_supported_languages`

**Supported languages:** JavaScript, TypeScript, Python, Java, Go, PHP, Dart, Kotlin

**Usage:**
```
> "Scan src/ for complexity hotspots"
> "What's the complexity of the fibonacci function in recursion.py?"
```

---

### Snyk

Vulnerability scanning for code and dependencies.

| Property | Value |
|---|---|
| **Package** | `snyk-mcp-server` |
| **Website** | [snyk.io](https://snyk.io) |
| **API Key** | **Required**: `SNYK_TOKEN` |
| **Get API Key** | [app.snyk.io/account](https://app.snyk.io/account) |
| **GABBE Skill** | `security/dependency-security.skill` |

**Install & Config:**
```json
{
  "snyk": {
    "command": "npx",
    "args": ["-y", "snyk-mcp-server"],
    "env": {
      "SNYK_TOKEN": "${SNYK_TOKEN}"
    }
  }
}
```

---

### SonarQube

Code quality and security analysis.

| Property | Value |
|---|---|
| **Package** | `sonarqube-mcp` |
| **Website** | [sonarqube.org](https://www.sonarsource.com/products/sonarqube/) |
| **API Key** | **Required**: `SONAR_URL`, `SONAR_TOKEN` |

**Install & Config:**
```json
{
  "sonarqube": {
    "command": "npx",
    "args": ["-y", "sonarqube-mcp"],
    "env": {
      "SONAR_URL": "${SONAR_URL}",
      "SONAR_TOKEN": "${SONAR_TOKEN}"
    }
  }
}
```

---

### Gitleaks

Secret detection in git repositories. No API key required.

| Property | Value |
|---|---|
| **Package** | `gitleaks-mcp` |
| **Website** | [gitleaks.io](https://gitleaks.io) |
| **API Key** | None required |
| **GABBE Skill** | `security/secrets-management.skill` |

**Install & Config:**
```json
{
  "gitleaks": {
    "command": "npx",
    "args": ["-y", "gitleaks-mcp"],
    "env": {}
  }
}
```

---

## 5. Observability & Monitoring

---

### Sentry

Error tracking, bug context, and performance issue correlation.

| Property | Value |
|---|---|
| **Package** | `@sentry/mcp-server` |
| **Website** | [sentry.io](https://sentry.io) |
| **API Key** | **Required**: `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT` |
| **Get API Key** | Sentry → Settings → API Keys |
| **GABBE Skill** | `ops/incident-response.skill` |

**Install & Config:**
```json
{
  "sentry": {
    "command": "npx",
    "args": ["-y", "@sentry/mcp-server"],
    "env": {
      "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}",
      "SENTRY_ORG": "${SENTRY_ORG}",
      "SENTRY_PROJECT": "${SENTRY_PROJECT}"
    }
  }
}
```

---

### Datadog

Monitoring, alerts, and observability queries.

| Property | Value |
|---|---|
| **Package** | `@datadog/mcp-server` |
| **Website** | [datadoghq.com](https://www.datadoghq.com) |
| **API Key** | **Required**: `DATADOG_API_KEY`, `DATADOG_APP_KEY` |
| **Get API Key** | Datadog → Organization Settings → API Keys |

**Install & Config:**
```json
{
  "datadog": {
    "command": "npx",
    "args": ["-y", "@datadog/mcp-server"],
    "env": {
      "DD_API_KEY": "${DATADOG_API_KEY}",
      "DD_APP_KEY": "${DATADOG_APP_KEY}"
    }
  }
}
```

---

### Grafana

Dashboard search, datasource queries, and incident management.

| Property | Value |
|---|---|
| **Package** | `@grafana/mcp-server` |
| **Website** | [grafana.com](https://grafana.com) |
| **API Key** | **Required**: `GRAFANA_URL`, `GRAFANA_API_KEY` |
| **Get API Key** | Grafana → Administration → Service Accounts → Add Token |

**Install & Config:**
```json
{
  "grafana": {
    "command": "npx",
    "args": ["-y", "@grafana/mcp-server"],
    "env": {
      "GRAFANA_URL": "${GRAFANA_URL}",
      "GRAFANA_API_KEY": "${GRAFANA_API_KEY}"
    }
  }
}
```

---

## 6. Browser & Web

---

### Playwright

Browser automation for visual TDD and E2E testing.

| Property | Value |
|---|---|
| **Package** | `@playwright/mcp` |
| **Website** | [playwright.dev](https://playwright.dev) |
| **API Key** | None required |
| **GABBE Skill** | `coding/browser-tdd.skill` |

**Install & Config:**
```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp", "--headless"],
    "env": {}
  }
}
```

> [!NOTE]
> Use `--headless` for CI environments. Remove it for local debugging with a visible browser.

---

### Tavily

Real-time web search and content extraction. Alternative to Brave Search.

| Property | Value |
|---|---|
| **Package** | `tavily-mcp` |
| **Website** | [tavily.com](https://tavily.com) |
| **API Key** | **Required**: `TAVILY_API_KEY` |
| **Get API Key** | [tavily.com](https://tavily.com) (free tier available) |
| **GABBE Skill** | `core/research.skill` |

**Install & Config:**
```json
{
  "tavily": {
    "command": "npx",
    "args": ["-y", "tavily-mcp"],
    "env": {
      "TAVILY_API_KEY": "${TAVILY_API_KEY}"
    }
  }
}
```

---

### Firecrawl

Turn websites into LLM-ready markdown. Website scraping and content extraction.

| Property | Value |
|---|---|
| **Package** | `firecrawl-mcp` |
| **Website** | [firecrawl.dev](https://firecrawl.dev) |
| **API Key** | **Required**: `FIRECRAWL_API_KEY` |

**Install & Config:**
```json
{
  "firecrawl": {
    "command": "npx",
    "args": ["-y", "firecrawl-mcp"],
    "env": {
      "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
    }
  }
}
```

---

### Image Recognition

Vision API proxy for image analysis — sketch recognition, diagram interpretation, and OCR.

| Property | Value |
|---|---|
| **Package** | `mcp-image-recognition` |
| **Website** | [github.com/mario-andreschak/mcp-image-recognition](https://github.com/mario-andreschak/mcp-image-recognition) |
| **API Key** | **Required** (one of): `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `CLOUDFLARE_API_TOKEN` |
| **Optional** | Tesseract OCR installed for text extraction |
| **GABBE Skill** | `coding/sketch-to-diagram.skill` |

**Install & Config:**
```json
{
  "image-recognition": {
    "command": "npx",
    "args": ["-y", "mcp-image-recognition"],
    "env": {
      "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
    }
  }
}
```

**Usage:**
```
> "Analyze this whiteboard photo and describe all architecture elements"
> "Recognize the hand-drawn flowchart in sketch.jpg and convert to Mermaid"
```

> [!WARNING]
> Images are sent to the configured external vision API for processing. Do not send sketches containing sensitive information (credentials, internal IPs) without user consent.

---

### DuckDuckGo

Privacy-focused web search. No API key required.

| Property | Value |
|---|---|
| **Package** | `duckduckgo-mcp-server` |
| **Website** | [duckduckgo.com](https://duckduckgo.com) |
| **API Key** | None required |

**Install & Config:**
```json
{
  "duckduckgo": {
    "command": "npx",
    "args": ["-y", "duckduckgo-mcp-server"],
    "env": {}
  }
}
```

---

## 7. Cloud & Infrastructure

---

### Terraform

Agentic Infrastructure as Code (IaC) via HashiCorp.

| Property | Value |
|---|---|
| **Package** | `@hashicorp/terraform-mcp-server` |
| **Website** | [terraform.io](https://www.terraform.io) |
| **API Key** | Optional: `TERRAFORM_CLOUD_TOKEN` |
| **GABBE Skill** | `ops/infra-devops.skill` |

**Install & Config:**
```json
{
  "terraform": {
    "command": "npx",
    "args": ["-y", "@hashicorp/terraform-mcp-server"],
    "env": {
      "TERRAFORM_CLOUD_TOKEN": "${TERRAFORM_CLOUD_TOKEN}"
    }
  }
}
```

---

### Docker

Docker daemon integration — manage containers, images, and read local logs.

| Property | Value |
|---|---|
| **Package** | `@docker/mcp-server` |
| **Website** | [docker.com](https://www.docker.com) |
| **API Key** | None (uses local Docker daemon) |
| **Prerequisite** | Docker Desktop or Docker Engine running |
| **GABBE Skill** | `ops/docker-dev.skill` |

**Install & Config:**
```json
{
  "docker": {
    "command": "npx",
    "args": ["-y", "@docker/mcp-server"],
    "env": {}
  }
}
```

---

### AWS Core

AWS core services — documentation, CDK, Lambda.

| Property | Value |
|---|---|
| **Package** | `@aws/mcp-server-core` |
| **Website** | [aws.amazon.com](https://aws.amazon.com) |
| **API Key** | **Required**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` |
| **GABBE Skill** | `ops/cloud-deploy.skill` |

**Install & Config:**
```json
{
  "aws-core": {
    "command": "npx",
    "args": ["-y", "@aws/mcp-server-core"],
    "env": {
      "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
      "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
      "AWS_REGION": "${AWS_REGION}"
    }
  }
}
```

---

### Google Cloud

Google Cloud Platform — Firebase, Cloud Run, GKE, BigQuery.

| Property | Value |
|---|---|
| **Package** | `@googlecloud/mcp-server` |
| **Website** | [cloud.google.com](https://cloud.google.com) |
| **API Key** | **Required**: `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON) |

**Install & Config:**
```json
{
  "google-cloud": {
    "command": "npx",
    "args": ["-y", "@googlecloud/mcp-server"],
    "env": {
      "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS}"
    }
  }
}
```

---

### Azure

Azure Resource management — Key Vault, CosmosDB, Azure Storage.

| Property | Value |
|---|---|
| **Package** | `@azure/mcp` |
| **Website** | [azure.microsoft.com](https://azure.microsoft.com) |
| **API Key** | **Required**: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID` |

**Install & Config:**
```json
{
  "azure": {
    "command": "npx",
    "args": ["-y", "@azure/mcp"],
    "env": {
      "AZURE_CLIENT_ID": "${AZURE_CLIENT_ID}",
      "AZURE_CLIENT_SECRET": "${AZURE_CLIENT_SECRET}",
      "AZURE_TENANT_ID": "${AZURE_TENANT_ID}"
    }
  }
}
```

---

### Vercel

Vercel deployments, aliases, and serverless log integration.

| Property | Value |
|---|---|
| **Package** | `@vercel/mcp-server` |
| **Website** | [vercel.com](https://vercel.com) |
| **API Key** | **Required**: `VERCEL_API_TOKEN` |
| **Get API Key** | Vercel → Settings → Tokens |

**Install & Config:**
```json
{
  "vercel": {
    "command": "npx",
    "args": ["-y", "@vercel/mcp-server"],
    "env": {
      "VERCEL_API_TOKEN": "${VERCEL_API_TOKEN}"
    }
  }
}
```

---

### Kubernetes

Cluster state, pod logs, and deployment management.

| Property | Value |
|---|---|
| **Package** | `mcp-server-kubernetes` |
| **Website** | [kubernetes.io](https://kubernetes.io) |
| **API Key** | **Required**: `KUBECONFIG` (path to kubeconfig file) |
| **GABBE Skill** | `ops/k8s-dev.skill` |

**Install & Config:**
```json
{
  "kubernetes": {
    "command": "npx",
    "args": ["-y", "mcp-server-kubernetes"],
    "env": {
      "KUBECONFIG": "${KUBECONFIG}"
    }
  }
}
```

> [!WARNING]
> Use **read-only** kubeconfig for production clusters. Never allow exec, delete, or scale operations on production.

---

## 8. Design & Visual Architecture

---

### Figma

UI/UX semantic understanding, component specs, and design-to-code.

| Property | Value |
|---|---|
| **Package** | `@figma/mcp-server` |
| **Website** | [figma.com](https://www.figma.com) |
| **API Key** | **Required**: `FIGMA_ACCESS_TOKEN` |
| **Get API Key** | Figma → Account Settings → Personal Access Tokens |
| **GABBE Skill** | `coding/visual-design.skill`, `architecture/visual-whiteboarding.skill` |

**Install & Config:**
```json
{
  "figma": {
    "command": "npx",
    "args": ["-y", "@figma/mcp-server"],
    "env": {
      "FIGMA_ACCESS_TOKEN": "${FIGMA_ACCESS_TOKEN}"
    }
  }
}
```

---

### Draw.io

Programmatic generation and editing of C4, UML, and network diagrams.

| Property | Value |
|---|---|
| **Package** | `drawio-mcp-server` |
| **Website** | [draw.io](https://www.drawio.com) |
| **API Key** | None required |
| **GABBE Skill** | `architecture/visual-whiteboarding.skill` |

**Install & Config:**
```json
{
  "drawio": {
    "command": "npx",
    "args": ["-y", "drawio-mcp-server"],
    "env": {}
  }
}
```

---

### Excalidraw

Create and manage Excalidraw diagrams — nodes, edges, and diagram state. Hand-drawn aesthetic.

| Property | Value |
|---|---|
| **Package** | `@cmd8/excalidraw-mcp` |
| **Website** | [github.com/cmd8/excalidraw-mcp](https://github.com/cmd8/excalidraw-mcp) |
| **API Key** | None required |
| **Prerequisite** | Node.js 18+, local `.excalidraw` file path |
| **GABBE Skill** | `coding/excalidraw.skill`, `coding/sketch-to-diagram.skill` |

**Install & Config:**
```json
{
  "excalidraw": {
    "command": "npx",
    "args": ["-y", "@cmd8/excalidraw-mcp", "--diagram", "./docs/architecture.excalidraw"],
    "env": {}
  }
}
```

**Tools:** `createNode`, `createEdge`, `deleteElement`, `getFullDiagramState`

**Usage:**
```
> "Create an Excalidraw architecture diagram: API Gateway → Auth, Users, Orders"
```

> [!NOTE]
> The `--diagram` flag specifies the target `.excalidraw` file. The file is created automatically if it doesn't exist. Excalidraw files are JSON-based and git-diffable.

---

### tldraw

Persistent visual canvas — create, manage, and search `.tldr` files for wireframing, prototyping, and visual scratchpads.

| Property | Value |
|---|---|
| **Package** | `@talhaorak/tldraw-mcp` |
| **Website** | [github.com/talhaorak/tldraw-mcp](https://github.com/talhaorak/tldraw-mcp) |
| **Canvas viewer** | [tldraw.com](https://www.tldraw.com) or VS Code tldraw extension |
| **API Key** | None required |
| **GABBE Skill** | `coding/tldraw-canvas.skill` |

**Install & Config:**
```json
{
  "tldraw": {
    "command": "npx",
    "args": ["-y", "@talhaorak/tldraw-mcp"],
    "env": {}
  }
}
```

**Tools (9):** `tldraw_create`, `tldraw_read`, `tldraw_write`, `tldraw_list`, `tldraw_search`, `tldraw_get_shapes`, `tldraw_add_shape`, `tldraw_update_shape`, `tldraw_delete_shape`

**Usage:**
```
> "Create a tldraw wireframe for the login page with a header, form inputs, and submit button"
> "Search all tldraw canvases for shapes mentioning 'auth'"
```

> [!TIP]
> tldraw files are JSON-based and git-diffable. Use them as persistent visual notes that AI agents can read and search across.

---

### Miro

Read context from virtual whiteboards and sync architecture PRDs.

| Property | Value |
|---|---|
| **Package** | `@mirohq/miro-mcp-server` |
| **Website** | [miro.com](https://miro.com) |
| **API Key** | **Required**: `MIRO_ACCESS_TOKEN` |
| **GABBE Skill** | `architecture/visual-whiteboarding.skill` |

**Install & Config:**
```json
{
  "miro": {
    "command": "npx",
    "args": ["-y", "@mirohq/miro-mcp-server"],
    "env": {
      "MIRO_ACCESS_TOKEN": "${MIRO_ACCESS_TOKEN}"
    }
  }
}
```

---

### Mermaid

Translate Mermaid/PlantUML syntax into SVG/PNG images.

| Property | Value |
|---|---|
| **Package** | `mermaid-mcp-server` |
| **Website** | [mermaid.js.org](https://mermaid.js.org) |
| **API Key** | None required |
| **GABBE Skill** | `architecture/diagramming.skill` |

**Install & Config:**
```json
{
  "mermaid": {
    "command": "npx",
    "args": ["-y", "mermaid-mcp-server"],
    "env": {}
  }
}
```

---

## 9. Knowledge Bases & Vector Databases

---

### Qdrant

Semantic memory layer — vector search for long-term project knowledge.

| Property | Value |
|---|---|
| **Package** | `mcp-server-qdrant` |
| **Website** | [qdrant.tech](https://qdrant.tech) |
| **API Key** | **Required**: `QDRANT_URL`, `QDRANT_API_KEY` |
| **GABBE Skill** | `core/knowledge-connect.skill` |

**Install & Config:**
```json
{
  "qdrant": {
    "command": "npx",
    "args": ["-y", "mcp-server-qdrant"],
    "env": {
      "QDRANT_URL": "${QDRANT_URL}",
      "QDRANT_API_KEY": "${QDRANT_API_KEY}",
      "COLLECTION_NAME": "project-knowledge"
    }
  }
}
```

---

### Pinecone

Managed vector database for semantic search.

| Property | Value |
|---|---|
| **Package** | `pinecone-mcp` |
| **Website** | [pinecone.io](https://www.pinecone.io) |
| **API Key** | **Required**: `PINECONE_API_KEY` |

**Install & Config:**
```json
{
  "pinecone": {
    "command": "npx",
    "args": ["-y", "pinecone-mcp"],
    "env": {
      "PINECONE_API_KEY": "${PINECONE_API_KEY}"
    }
  }
}
```

---

### ChromaDB

Open-source embedding database. No API key required for local mode.

| Property | Value |
|---|---|
| **Package** | `chromadb-mcp` |
| **Website** | [trychroma.com](https://www.trychroma.com) |
| **API Key** | None (local mode) |

**Install & Config:**
```json
{
  "chroma": {
    "command": "npx",
    "args": ["-y", "chromadb-mcp"],
    "env": {}
  }
}
```

---

### Weaviate

Vector search engine for semantic queries.

| Property | Value |
|---|---|
| **Package** | `weaviate-mcp` |
| **Website** | [weaviate.io](https://weaviate.io) |
| **API Key** | **Required**: `WEAVIATE_URL`, `WEAVIATE_API_KEY` |

**Install & Config:**
```json
{
  "weaviate": {
    "command": "npx",
    "args": ["-y", "weaviate-mcp"],
    "env": {
      "WEAVIATE_URL": "${WEAVIATE_URL}",
      "WEAVIATE_API_KEY": "${WEAVIATE_API_KEY}"
    }
  }
}
```

---

### Elasticsearch

Full-text search, log analysis, and knowledge base indexing.

| Property | Value |
|---|---|
| **Package** | `elasticsearch-mcp-server` |
| **Website** | [elastic.co](https://www.elastic.co) |
| **API Key** | **Required**: `ELASTICSEARCH_URL`, `ELASTICSEARCH_API_KEY` |
| **GABBE Skill** | `security/log-analysis.skill` |

**Install & Config:**
```json
{
  "elasticsearch": {
    "command": "npx",
    "args": ["-y", "elasticsearch-mcp-server"],
    "env": {
      "ELASTICSEARCH_URL": "${ELASTICSEARCH_URL}",
      "ELASTICSEARCH_API_KEY": "${ELASTICSEARCH_API_KEY}"
    }
  }
}
```

---

## 10. Project Management & Collaboration

---

### Jira

Jira Cloud task interaction — read and update tickets.

| Property | Value |
|---|---|
| **Package** | `@aashari/mcp-server-atlassian-jira` |
| **Website** | [atlassian.com/jira](https://www.atlassian.com/software/jira) |
| **API Key** | **Required**: `JIRA_SITE`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| **Get API Key** | [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |

**Install & Config:**
```json
{
  "jira": {
    "command": "npx",
    "args": ["-y", "@aashari/mcp-server-atlassian-jira"],
    "env": {
      "ATLASSIAN_SITE_NAME": "${JIRA_SITE}",
      "ATLASSIAN_USER_EMAIL": "${JIRA_EMAIL}",
      "ATLASSIAN_API_TOKEN": "${JIRA_API_TOKEN}"
    }
  }
}
```

---

### Confluence

Confluence pages and spaces.

| Property | Value |
|---|---|
| **Package** | `@modelcontextprotocol/server-confluence` |
| **Website** | [atlassian.com/confluence](https://www.atlassian.com/software/confluence) |
| **API Key** | **Required**: `CONFLUENCE_URL`, `CONFLUENCE_EMAIL`, `CONFLUENCE_TOKEN` |

**Install & Config:**
```json
{
  "confluence": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-confluence"],
    "env": {
      "ATLASSIAN_URL": "${CONFLUENCE_URL}",
      "ATLASSIAN_USERNAME": "${CONFLUENCE_EMAIL}",
      "ATLASSIAN_API_TOKEN": "${CONFLUENCE_TOKEN}"
    }
  }
}
```

---

### Notion

Notion workspace access — pages, databases, docs.

| Property | Value |
|---|---|
| **Package** | `@notionhq/notion-mcp-server` |
| **Website** | [notion.so](https://www.notion.so) |
| **API Key** | **Required**: `NOTION_TOKEN` (internal integration token) |
| **Get API Key** | [notion.so/my-integrations](https://www.notion.so/my-integrations) |

**Install & Config:**
```json
{
  "notion": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": {
      "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ${NOTION_TOKEN}\"}"
    }
  }
}
```

---

### Linear

Linear issue tracking and project management.

| Property | Value |
|---|---|
| **Package** | `linear-mcp-server` |
| **Website** | [linear.app](https://linear.app) |
| **API Key** | **Required**: `LINEAR_API_KEY` |
| **Get API Key** | Linear → Settings → API → Personal API Keys |

**Install & Config:**
```json
{
  "linear": {
    "command": "npx",
    "args": ["-y", "linear-mcp-server"],
    "env": {
      "LINEAR_API_KEY": "${LINEAR_API_KEY}"
    }
  }
}
```

---

### Slack

Workspace channels, DMs, and message history.

| Property | Value |
|---|---|
| **Package** | `slack-mcp-server` |
| **Website** | [api.slack.com](https://api.slack.com) |
| **API Key** | **Required**: `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` |
| **Get API Key** | [api.slack.com/apps](https://api.slack.com/apps) → Create App → Bot Token |

**Install & Config:**
```json
{
  "slack": {
    "command": "npx",
    "args": ["-y", "slack-mcp-server"],
    "env": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
    }
  }
}
```

---

## 11. API Introspection & Knowledge

---

### GraphQL

GraphQL schema introspection, query validation, and documentation.

| Property | Value |
|---|---|
| **Package** | `graphql-mcp-server` |
| **API Key** | **Required**: `GRAPHQL_ENDPOINT`, Optional: `GRAPHQL_TOKEN` |
| **GABBE Skill** | `architecture/graphql-schema.skill` |

**Install & Config:**
```json
{
  "graphql": {
    "command": "npx",
    "args": ["-y", "graphql-mcp-server"],
    "env": {
      "GRAPHQL_ENDPOINT": "${GRAPHQL_ENDPOINT}",
      "GRAPHQL_HEADERS": "{\"Authorization\": \"Bearer ${GRAPHQL_TOKEN}\"}"
    }
  }
}
```

---

### OpenAPI

Load and query any OpenAPI/Swagger specification for API exploration.

| Property | Value |
|---|---|
| **Package** | `openapi-mcp-server` |
| **API Key** | None — requires `OPENAPI_SPEC_URL` (path or URL to spec) |
| **GABBE Skill** | `architecture/api-design.skill` |

**Install & Config:**
```json
{
  "openapi": {
    "command": "npx",
    "args": ["-y", "openapi-mcp-server"],
    "env": {
      "OPENAPI_SPEC_URL": "${OPENAPI_SPEC_URL}"
    }
  }
}
```

---

### Shell

Execute shell commands for local build, test, and system introspection.

| Property | Value |
|---|---|
| **Package** | `@anthropic/mcp-server-shell` |
| **API Key** | None required |

**Install & Config:**
```json
{
  "shell": {
    "command": "npx",
    "args": ["-y", "@anthropic/mcp-server-shell"],
    "env": {}
  }
}
```

> [!CAUTION]
> **DEVELOPMENT ONLY** — restrict to project directory. Never enable in production environments. Risk of arbitrary command execution.

---

### Jupyter

Execute Python code in Jupyter notebooks.

| Property | Value |
|---|---|
| **Package** | `jupyter-mcp-server` |
| **Prerequisite** | Jupyter installed locally |
| **API Key** | None required |

**Install & Config:**
```json
{
  "jupyter": {
    "command": "npx",
    "args": ["-y", "jupyter-mcp-server"],
    "env": {}
  }
}
```

---

## 12. Payments & Automation

---

### Stripe

Search and manage Stripe payment resources.

| Property | Value |
|---|---|
| **Package** | `@stripe/mcp` |
| **Website** | [stripe.com](https://stripe.com) |
| **API Key** | **Required**: `STRIPE_SECRET_KEY` |
| **Get API Key** | Stripe Dashboard → Developers → API Keys |

**Install & Config:**
```json
{
  "stripe": {
    "command": "npx",
    "args": ["-y", "@stripe/mcp"],
    "env": {
      "STRIPE_API_KEY": "${STRIPE_SECRET_KEY}"
    }
  }
}
```

> [!WARNING]
> Use **test mode** keys during development. Never expose live secret keys in config files.

---

### Zapier

Connect to 6,000+ apps via Zapier Natural Language Actions.

| Property | Value |
|---|---|
| **Package** | `@zapier/mcp-server` |
| **Website** | [zapier.com](https://zapier.com) |
| **API Key** | **Required**: `ZAPIER_NLA_API_KEY` |
| **Get API Key** | [nla.zapier.com/credentials](https://nla.zapier.com/credentials) |

**Install & Config:**
```json
{
  "zapier": {
    "command": "npx",
    "args": ["-y", "@zapier/mcp-server"],
    "env": {
      "ZAPIER_NLA_API_KEY": "${ZAPIER_NLA_API_KEY}"
    }
  }
}
```

---

## 13. Security Rules & Best Practices

These rules apply to all MCP server configurations:

| Rule | Description |
|---|---|
| **Production databases** | Read-only access only — use a dedicated read-only DB user |
| **Development databases** | Read-write allowed — never point dev config at a production DB |
| **Secrets policy** | All credentials via environment variables — never hardcoded |
| **File system** | Restrict to project directory only — no access to `/etc`, `/home`, system dirs |
| **Kubernetes (prod)** | Read-only mode only — no exec, no delete, no scale |
| **Browser CI** | Headless mode only for CI — headed mode for local debugging only |
| **Shell** | Development only — never enable in production |

---

## 14. Environment Variables Summary

All credentials should be set as environment variables in your shell profile or `.env` file.

### Essential (recommended for every project)
| Variable | Source | Required By |
|---|---|---|
| `BRAVE_API_KEY` | [api.search.brave.com/register](https://api.search.brave.com/register) | Brave Search |
| `GITHUB_TOKEN` | GitHub → Settings → Developer Settings → PAT | GitHub MCP |

### Databases
| Variable | Description | Required By |
|---|---|---|
| `DATABASE_URL_DEV` | PostgreSQL connection string (dev) | PostgreSQL Dev |
| `DATABASE_URL_PROD_READONLY` | PostgreSQL read-only connection (prod) | PostgreSQL Prod |
| `MONGODB_URI` | MongoDB connection string | MongoDB |
| `REDIS_URL` | Redis URL (e.g., `redis://localhost:6379`) | Redis |

### Security & Code Quality
| Variable | Source | Required By |
|---|---|---|
| `SEMGREP_APP_TOKEN` | [semgrep.dev/settings/tokens](https://semgrep.dev/settings/tokens) | Semgrep |
| `SNYK_TOKEN` | [app.snyk.io/account](https://app.snyk.io/account) | Snyk |
| `SONAR_URL` / `SONAR_TOKEN` | SonarQube instance | SonarQube |

### Observability
| Variable | Source | Required By |
|---|---|---|
| `SENTRY_AUTH_TOKEN` | Sentry → Settings → API Keys | Sentry |
| `SENTRY_ORG` / `SENTRY_PROJECT` | Sentry organization settings | Sentry |
| `DATADOG_API_KEY` / `DATADOG_APP_KEY` | Datadog → Org Settings | Datadog |
| `GRAFANA_URL` / `GRAFANA_API_KEY` | Grafana administration | Grafana |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com) | Tavily |

### Cloud
| Variable | Description | Required By |
|---|---|---|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` | AWS IAM credentials | AWS Core |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON | Google Cloud |
| `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` | Azure AD app registration | Azure |
| `VERCEL_API_TOKEN` | Vercel token | Vercel |
| `TERRAFORM_CLOUD_TOKEN` | Terraform Cloud | Terraform |

### Collaboration
| Variable | Source | Required By |
|---|---|---|
| `GITLAB_TOKEN` | GitLab → Preferences → Access Tokens | GitLab |
| `JIRA_SITE` / `JIRA_EMAIL` / `JIRA_API_TOKEN` | Atlassian API tokens | Jira |
| `CONFLUENCE_URL` / `CONFLUENCE_EMAIL` / `CONFLUENCE_TOKEN` | Atlassian | Confluence |
| `NOTION_TOKEN` | [notion.so/my-integrations](https://www.notion.so/my-integrations) | Notion |
| `LINEAR_API_KEY` | Linear → Settings → API | Linear |
| `SLACK_BOT_TOKEN` / `SLACK_TEAM_ID` | [api.slack.com/apps](https://api.slack.com/apps) | Slack |

### Design & Visual
| Variable | Source | Required By |
|---|---|---|
| `FIGMA_ACCESS_TOKEN` | Figma → Account Settings | Figma |
| `MIRO_ACCESS_TOKEN` | Miro developer portal | Miro |

### Vector Databases
| Variable | Description | Required By |
|---|---|---|
| `QDRANT_URL` / `QDRANT_API_KEY` | Qdrant instance | Qdrant |
| `PINECONE_API_KEY` | Pinecone console | Pinecone |
| `WEAVIATE_URL` / `WEAVIATE_API_KEY` | Weaviate instance | Weaviate |
| `ELASTICSEARCH_URL` / `ELASTICSEARCH_API_KEY` | Elastic deployment | Elasticsearch |

### Payments & Automation
| Variable | Source | Required By |
|---|---|---|
| `STRIPE_SECRET_KEY` | Stripe Dashboard → Developers | Stripe |
| `ZAPIER_NLA_API_KEY` | [nla.zapier.com/credentials](https://nla.zapier.com/credentials) | Zapier |
| `FIRECRAWL_API_KEY` | firecrawl.dev | Firecrawl |

---

*See also: `agents/templates/core/MCP_CONFIG_TEMPLATE.json` for the raw configuration template.*
*See also: [README.md](../README.md) for the Essential MCP Servers quick reference.*
*See also: [README_FULL.md](README_FULL.md) for the full MCP coverage matrix.*

---

## SWEBOK v4 Priority Map

A lifecycle-oriented view of the highest-value, self-hostable/free-tier MCP servers,
mapped to the SWEBOK v4 knowledge areas. Most run locally via Docker or Node so
credentials never leave the host. Servers marked **(new in v1.0)** were added to
`MCP_CONFIG_TEMPLATE.json` as opt-in (`_enabled: false`) entries.

| SWEBOK area | Priority MCP servers | GABBE tie-in |
|---|---|---|
| **Requirements & Design** | `figma`, `notion`, `obsidian` (new), `knowledge-graph-memory` (new) | S00–S03; `knowledge-connect.skill`, ADR/spec search; persistent semantic memory prevents architectural-decision drift |
| **Construction & Architecture** | `github`, `githits` (new), `supabase` (new), `postgres-dev`/`postgres-prod`, `mongodb`, `aws-core`, `azure`, `kubernetes`, `docker` | S05; direct schema/query execution instead of guessed SQL; `githits` reads dependency source/docs so the agent doesn't guess third-party APIs |
| **Testing & Quality** | `sentry`, `snyk`, `semgrep`, `mcp-evals` (new), `mcp-chaos-rig` (new) | S06–S07; `mcp-evals` ↔ `eval-driven-development.skill`; `mcp-chaos-rig` ↔ `chaos-fault-injection.skill` + `gabbe verify --chaos` |
| **Maintenance & Config Mgmt** | `pagerduty` (new), `cloudflare` (new), `vercel`, `gitlab` | S11–S13 Day-2; on-call automation, edge deploy logs |
| **Eng. Management & Economics** | `linear`, `jira`, `confluence`, `slack`, `discord` (new), `stripe` | management + software economics; comms triage, billing/churn |
| **Computing & Foundations** | `firecrawl`, `qdrant`, `chroma`/`weaviate`/`pinecone`, `google-genai-toolbox` (new), `context7`, `sequential-thinking` | research, RAG long-term memory, foundational data access |

**Deployment note:** the vast majority of these run locally via Docker or Node, so API
keys/credentials stay on the host unless explicitly routed through an enterprise gateway.
All new entries are opt-in — enable per project by setting `_enabled: true` and the listed
env vars.
