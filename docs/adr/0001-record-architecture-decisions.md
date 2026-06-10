# 1. Record architecture decisions

- Status: Accepted
- Date: 2026-06-10

## Context

GABBE has accumulated significant architectural decisions (the Universal Skill
Compiler, the dual runtime modes, the platform-control layer) that are currently
only discoverable by reading code and long-form docs. New contributors and future
maintainers need a durable, append-only record of *why* the system is shaped the
way it is.

## Decision

We will use Architecture Decision Records (ADRs), as described by Michael Nygard,
stored in `docs/adr/` and numbered sequentially. Each ADR captures one decision
with its context, the decision itself, and consequences. ADRs are immutable once
accepted; a superseding decision gets a new ADR that references the old one.

## Consequences

- Decisions are reviewable in pull requests alongside the code that implements them.
- The record is append-only; we do not edit accepted ADRs except to mark them
  superseded.
- Lightweight enough that proposing an ADR is not a barrier to contribution.
