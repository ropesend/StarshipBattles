# Feature Development Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*QA Session 20260428_052952: FEAT-10, FEAT-11, FEAT-12, FEAT-14, FEAT-15, FEAT-16, FEAT-18, FEAT-19, FEAT-21 confirmed working and archived. QA Session 20260428_190154: FEAT-13, FEAT-17, FEAT-23, FEAT-24 confirmed working and archived; FEAT-20 update requested (remove dev-mode gate).*

## 2. Feature Queue
| ID | Date Added | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| FEAT-20 | 2026-04-27 | "Run 10 turns" button next to End Turn (revised: always-visible, no longer dev-gated) | In-Progress | [FEAT-20.md](features/active/FEAT-20.md) |
| FEAT-22 | 2026-04-28 | Startup phase profiling — log timings before main menu appears | Pending | [FEAT-22.md](features/active/FEAT-22.md) |
| FEAT-25 | 2026-04-28 | Planet Registry — upgrade Effects filter from on/off chips to 3-way tri-state | Pending | [FEAT-25.md](features/active/FEAT-25.md) |
| FEAT-26 | 2026-04-28 | Wire replay_id through to Event Log and add Replay button on combat entries (closes PROJ-312 UI gap) | Pending | [FEAT-26.md](features/active/FEAT-26.md) |
| FEAT-27 | 2026-04-28 | Allow new-game galaxy size as low as 1 system (default 2; enforce distinct systems per empire when N≥2) | Pending | [FEAT-27.md](features/active/FEAT-27.md) |
| FEAT-28 | 2026-04-28 | Mutual JOIN orders should make both fleets move toward each other (rendezvous) | Pending | [FEAT-28.md](features/active/FEAT-28.md) |

## 3. Current Focus: None
No features currently in progress.

## 4. Status Reference
| Status | Meaning |
| :--- | :--- |
| Pending | Not yet started |
| Analysis | Component review in progress (Phase 1) |
| In-Progress | Implementation actively being worked on |
| Needs Clarification | Ambiguous requirements — questions posted in ticket, awaiting user answers |
| Awaiting Confirmation | Implementation complete, awaiting user verification |
| Needs Refactor | Clean implementation not feasible, refactor recommended |
| Deep Investigation | Complex feature undergoing thorough analysis (Protocol 02b) |
| Needs Project | Feature too large for feature track, should become a formal Project |
| Blocked | Stuck after 3+ attempts, needs human input |
