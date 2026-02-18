# No-Code & Low-Code Integration Guide

**Bridge the gap between Pro-Code Agents and Citizen Developers.**

This guide explains how to integrate the Agentic Engineering Kit with No-Code platforms (n8n, Make, Zapier) to create hybrid workflows.

---

## 1. The Hybrid Architecture

in 2026, the strongest systems use a Hybrid approach:
*   **Agents (Code):** Handle complex reasoning, edge cases, and deeply custom logic.
*   **No-Code (Visual):** Handle standard triggers, simple data piping, and approval flows.

### Architecture Pattern: "The Agent Node"
Instead of replacing No-Code, the Agent becomes a "Super Node" inside the No-Code flow.

`[ Webhook ] --> [ Transformation ] --> [ **AGENT NODE** ] --> [ CRM Update ] --> [ Slack Notify ]`

---

## 2. Platforms & Protocols

### n8n (Self-Hostable)
*   **Best For:** Heavy data processing, privacy-conscious deployments.
*   **Integration:**
    *   **LangChain Node:** Use n8n's native LangChain integration to call your Agent.
    *   **HTTP Request:** Call your Agent's API Endpoint (see `eng-api` persona).
    *   **Pattern:** Agent returns structured JSON, n8n maps it to the next node.

### Make.com (formerly Integromat)
*   **Best For:** Visualizing complex logic branches.
*   **Integration:**
    *   Use the "HTTP / Make Request" module.
    *   Set `Content-Type: application/json`.
    *   **Timeout Warning:** Agents can be slow. Set Make timeout to > 60s or use Webhooks (Async pattern).

### Zapier
*   **Best For:** Simple "If This Then That" flows.
*   **Integration:**
    *   **Zapier AI Actions:** Expose your Agent's tools as Zapier Actions.
    *   **Webhooks:** Standard Request/Response.

---

## 3. The "Citizen Developer" Bridge

How to let non-coders control your Agent:

1.  **Configuration Schemas:**
    *   Agent exposes a `config.json` or YAML.
    *   No-Code tool reads this config to generate a Form.
    *   User fills Form -> Agent executes logic.

2.  **Approval Gates (Human-in-the-Loop):**
    *   Agent performs work -> Pauses -> Sends Webhook to Slack/Teams.
    *   User clicks "Approve" (No-Code button).
    *   No-Code tool calls Agent's "Resume" endpoint.

---

## 4. Generating No-Code Assets

The Agent can *write* the No-Code configuration for you.

*   **n8n:** Agent generates the JSON definition of a Workflow. You import it.
*   **OpenAPI:** Agent generates `openapi.yaml`. You import it into Custom Connectors (Zapier/PowerAutomate).

### Example Prompt for Agent:
> "Generate an n8n workflow JSON that triggers on a Webhook, sends the body to my Summarizer Agent API, and posts the result to Slack."

---

## 5. Security & Governance

*   **API Keys:** Never hardcode keys in No-Code tools. Use their Credential Managers.
*   **Rate Limiting:** Protect your Agent API from run-away No-Code loops.
*   **Validation:** Agent must strictly validate all inputs coming from No-Code sources (Zod/Pydantic).

---

**Related Skills:**
*   `architecture/api-design.skill.md`: How to build the API your No-Code tool calls.
*   `coding/tool-construction.skill.md`: Building tools that Agents can use.
