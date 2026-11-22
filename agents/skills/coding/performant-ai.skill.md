---
name: performant-ai
description: "Cut token cost and latency in LLM systems: context pruning, prompt size, RAG chunking and re-ranking, model routing, caching. Use when an LLM feature is slow or expensive, or when its context window or retrieval quality is the limit."
triggers: [ai, llm, performance, context window, tokens, prompt engineering, rag, inference, latency]
tags: [coding, ai, architecture]
context_cost: medium
---
# Performant AI Skill

## Goal
Optimizing the interaction, speed, and cost-effectiveness of LLM-based systems by mastering context management and inference strategies.

## Capabilities

### 1. Context Window Engineering
- **Context Pruning**: Implement logic to remove irrelevant or redundant tokens from the prompt to fit within limits and reduce cost.
- **Summarization Chains**: Use "recursive summarization" for long conversations or documents.
- **Observation Masking**: Hide older or less critical data to keep the attention of the model on the immediate task.

### 2. Efficient Prompting (Latency & Cost)
- **Few-Shot Optimization**: Minimize the number of examples to the bare minimum needed for accuracy.
- **Output Structuring**: Use JSON mode or structured outputs to reduce parsing errors and retry loops.
- **Prompt Compression**: Use tools or manual techniques to shorten instructions without losing semantic meaning.

### 3. RAG Optimization (Retrieval-Augmented Generation)
- **Chunking Strategy**: Optimize chunk sizes and overlap for the specific domain (e.g., small chunks for semantic search, large for summaries).
- **Hybrid Search**: Combine Vector search (semantic) with Keyword search (BM25) for higher precision.
- **Re-ranking**: Use a secondary, smaller model to re-rank the top-K results before sending them to the expensive LLM.

### 4. Inference & Routing Strategies
- **Brain Mode Routing**: Arbitrate between "Local" models (faster/cheaper) and "Remote" models (complex/slower) based on task difficulty.
- **Speculative Decoding**: (Where possible) use smaller models to draft tokens for larger models to verify, speeding up generation.
- **Cache Hits**: Implement semantic caching (Redis) to reuse LLM responses for similar queries.

### 5. Architectural Patterns
- **Self-Correction Loops**: Build reflection phases into the agent flow to catch errors early.
- **Asynchronous Agents**: Run independent research or tool calls in parallel to reduce perceived latency (Loki Mode).

## Steps
1. **Token Audit**: Trace the token count of typical requests to find "bloat" in systemic prompts.
2. **Latency Mapping**: Break down Time-to-First-Token (TTFT) and Total Generation Time.
3. **Retrieval Benchmark**: Measure the Hit Rate and Recall of the RAG pipeline.
4. **Cost Projection**: Estimate monthly burn based on different model providers and context sizes.

## Output Format
- `COST_OPTIMIZATION_REPORT_TEMPLATE.md`: Analysis of prompt efficiency and LLM token usage.
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Configuration for vector DB, chunking, and search weights.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Logic table for local vs remote model selection and context scaling.

## Constraints
- Measure before and after each change (tokens, time to first token, retrieval hit rate); a cost projection is an estimate with its assumptions stated.
- Keep a fallback path when the primary model fails or is rate-limited.

## Limits and safety
- Remove or mask personal data before it goes to a remote model provider, and check that RAG retrieval respects the asking user's access rights.
- Set a token or cost cap per session before starting an autonomous loop, and stop at the cap.
- At most 5 reflection or self-heal attempts, as in `self-heal.skill`.
- Check critical facts the model produced against a source, and keep a conservative fallback for a failed or rate-limited model.
