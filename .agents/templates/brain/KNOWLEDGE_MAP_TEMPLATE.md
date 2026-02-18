# Knowledge Map & Integration Strategy

**Project:** `[Project Name]`
**Date:** `[YYYY-MM-DD]`
**Maintainer:** `[Role/Person]`

## 1. Knowledge Sources

| Source Name | Type | Location/URL | Update Frequency | Connector (MCP/API) |
|---|---|---|---|---|
| **Core Documentation** | Markdown | `/docs` | Weekly | Filesystem |
| **API Specs** | OpenAPI | `/api/openapi.yaml` | On Change | Filesystem / URL |
| **Corporate Wiki** | Notion | `[URL]` | Daily | Notion MCP |
| **Customer Tickets** | Zendesk | `[URL]` | Real-time | Zendesk MCP |
| **Codebase** | Git Repo | `[Repo URL]` | Real-time | GitHub MCP |

## 2. Vector Database Schema

**Store:** [Qdrant / Chroma / Pinecone / Pgvector]

### Collection: `domain_knowledge`
*   **Content**: Technical documentation, RFCs, Architecture decision records.
*   **Metadata Fields**:
    *   `source`: [url/path]
    *   `author`: [email]
    *   `last_updated`: [timestamp]
    *   `tags`: [list]
*   **Embedding Model**: [text-embedding-3-small / all-MiniLM-L6-v2]

### Collection: `legal_compliance`
*   **Content**: Regulatory docs (GDPR, HIPAA), Terms of Service.
*   **Metadata Fields**:
    *   `jurisdiction`: [EU/US/Global]
    *   `valid_until`: [date]

## 3. Ingestion Pipeline
*   **Trigger**: [Git Hook / Scheduled Cron / Manual]
*   **Chunking Strategy**:
    *   Size: 1000 tokens
    *   Overlap: 200 tokens
    *   Splitter: [MarkdownHeaderSplitter / RecursiveCharacterSplitter]
*   **Quality Gate**:
    *   [ ] Remove duplicates?
    *   [ ] Filter PII/Secrets? (Mandatory)

## 4. Retrieval Strategy (RAG)
*   **Top-K**: 5 chunks
*   **Re-ranking**: [Yes/No] (e.g., using Cohere Rerank)
*   **Hybrid Search**: [Keyword + Vector] enabled?

## 5. Access Control
*   [ ] Verify user permissions before returning results?
*   [ ] Encrypt vectors at rest?
