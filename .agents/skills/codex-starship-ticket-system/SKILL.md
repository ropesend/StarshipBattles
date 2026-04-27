---
name: codex-starship-ticket-system
description: Work Starship Battles bug and feature tickets using the Tracking system. Use for ticket-add, ticket-work, ticket-next, ticket-continue, ticket-deep-dive, ticket-close, ticket-batch-close, ticket-update, ticket-reject, and ticket-answer style requests; for active files under Tracking/bugs or Tracking/features; and for TDD ticket resolution workflows.
---

# Codex Starship Ticket System

Use the shared ticket protocols instead of inventing a new workflow.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `Tracking/README.md`.
3. Read `docs/README.md` and the docs required for the affected code area.
4. Read the specific protocol selected below.

## Protocol Routing

- Create a bug or feature ticket: `Tracking/protocols/01_ingest_ticket.md`.
- Work a specific bug or feature: `Tracking/protocols/02_work_ticket.md`.
- Work the next queued ticket: `Tracking/protocols/02_work_ticket.md`, after selecting from `Tracking/debug_plan.md` or `Tracking/feature_plan.md`.
- Continue a batch of tickets: `Tracking/protocols/02a_batch_work.md`.
- Deep investigate a bug or feature: `Tracking/protocols/02b_deep_dive.md`.
- Parallel debugging or parallel deep dive: `Tracking/protocols/02c_parallel_debug.md` or `Tracking/protocols/02d_parallel_deep_dive.md` only when the user explicitly asks for parallel/delegated agent work and the current Codex client supports it.
- Close one ticket: `Tracking/protocols/03_close_ticket.md`.
- Close multiple tickets: `Tracking/protocols/03a_batch_close.md`.
- Append new context: `Tracking/protocols/04_update_ticket.md`.
- Reject a proposed fix: `Tracking/protocols/05_reject_ticket.md`.
- Record answers to ticket questions: `Tracking/protocols/06_answer_questions.md`.

## Rules

- Respect ticket authority limits. Agents can move tickets to `[Awaiting Confirmation]`, `[Needs Clarification]`, `[Needs Refactor]`, or `[Blocked]` as the protocol allows, but cannot mark bugs `[Solved]`, mark features `[Completed]`, or archive tickets unless the user invoked the close protocol.
- For bug fixes, perform the anti-reversion check from `Tracking/protocols/02_work_ticket.md` before coding.
- Always document code/docs discrepancies in the ticket work log.
- Use strict TDD for implementation. The failing test output belongs in the ticket work log before the code fix.
- Update dashboards and ticket work logs as the protocol requires.
- Do not silently skip documentation updates when behavior, architecture, patterns, or conventions change.
