# Knowledge Integration Guide

> **Goal**: Equip your agents with persistent, searchable knowledge (RAG) and active connections to external systems.

---

## 1. Overview: The "Second Brain"
Agents have limited context windows. To build expert systems, you must give them a "Second Brain" — a Vector Database or Knowledge Graph that stores infinite context.

**Components:**
1.  **Connectors (MCP)**: The "Hands" — fetch data from Notion, GitHub, Google Drive.
2.  **Embedding Model**: The "Translator" — converts text to numbers (vectors).
3.  **Vector DB**: The "Long-Term Memory" — stores vectors for fast similarity search.
4.  **Integration Skill**: `core/knowledge-connect.skill.md` — The "Workflow".

---

## 2. Quick Start: Local RAG (Zero Cost)

1.  **Install Connectors**:
    Ensure `filesystem-kb` or basic file reading is enabled.

2.  **Create Knowledge Map**:
    Fill out `agents/templates/brain/KNOWLEDGE_MAP_TEMPLATE.md`.
    *Example*: Map your `/docs` folder to a `project_docs` collection.

3.  **Ingest (Manual/Scripted)**:
    *   Use a simple script (Python/JS) to read Markdown files.
    *   Split by headers (`#`, `##`).
    *   Store in a local vector store (e.g., ChromaDB or simple JSON with embeddings).

4.  **Query**:
    *   *User*: "How does the auth system work?"
    *   *Agent*:
        1.  Embeds query "auth system".
        2.  Searches Vector DB.
        3.  Retrieves `docs/auth.md` chunk.
        4.  Answers: "According to `docs/auth.md`, we use OAuth2..."

---

## 3. High-Scale Patterns (Enterprise)

### Pattern A: Live MCP Retrieval
Instead of verifying, let the Agent ask the source directly via MCP.
*   *Agent*: "I need the latest Q3 roadmap."
*   *Tool*: `notion_mcp.search("Q3 Roadmap")`
*   *Result*: Returns page content within seconds.
*   **Pros**: Always fresh. **Cons**: Slower, API rate limits.

### Pattern B: Async Ingestion Pipeline
Background jobs sync sources to Vector DB.
*   **ETL Job**: Runs every hour. Syncs GitHub -> Qdrant.
*   **Agent**: Queries Qdrant (fast, <100ms).
*   **Pros**: Fast, scalable. **Cons**: Data latency (can be stale).

### Pattern C: A2A (Agent-to-Agent) Knowledge Exchange
One agent acts as the "Librarian".
*   *Coder Agent*: "Hey Librarian, do we have a standard for error handling?"
*   *Librarian Agent*: Checks semantic memory, returns the specific "Error Handling RFC".

---

## 4. Vector Database Options

| Database | Best For | Setup |
|---|---|---|
| **Qdrant** | Production, performance, filtering | `docker run qdrant/qdrant` |
| **Chroma** | Simplicity, local dev (Python/JS) | `pip install chromadb` |
| **Pinecone** | Managed service (Serverless) | Cloud Sign-up |
| **Pgvector** | Use if you already have Postgres | Extension on existing DB |

---

## 5. Security & Governance

> [!WARNING]
> **Never index secrets.** A RAG system will happily retrieve "AWS_SECRET_KEY" if asked, if you indexed your `.env` file.

*   **Pii Scrubbing**: Use `presidio` or Regex to purge emails/phones before indexing.
*   **ACLs**: Store `user_id` or `group_id` in metadata. Verify access time.
*   **Data Sovereignty**: Ensure Vector DB location complies with GDPR (e.g., EU region).
