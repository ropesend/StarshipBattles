# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*QA Session 20260323_143412: BUG-98 fix rejected (only works for limiting resource, not all resource types) — reverted to In-Progress. New tickets: BUG-100 (planet list column swap missing), BUG-101 (fleet info panel raw order enum names). BUG-80, BUG-99 still awaiting confirmation.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-80 | 2026-02-11 | Planets List - Planet details panel dimensions and positioning | Awaiting Confirmation | [BUG-80.md](active_bugs/BUG-80.md) |
| BUG-98 | 2026-03-22 | Build Queue "Next Turn" resource columns show incorrect per-item values | Awaiting Confirmation | [BUG-98.md](active_bugs/BUG-98.md) |
| BUG-99 | 2026-03-22 | "Remove from Fleet" button in Fleet Report does nothing when clicked | Awaiting Confirmation | [BUG-99.md](active_bugs/BUG-99.md) |
| BUG-100 | 2026-03-23 | Planet List Window column reorder arrows do not swap columns | Awaiting Confirmation | [BUG-100.md](active_bugs/BUG-100.md) |
| BUG-101 | 2026-03-23 | Fleet info panel shows raw enum names for MOVE_TO_FLEET and JOIN_FLEET orders | Pending | [BUG-101.md](active_bugs/BUG-101.md) |

## 3. Current Focus: None
**Status:** No bug currently in focus. BUG-98 and BUG-99 are pending.

## 4. Status Reference
| Status | Meaning |
| :--- | :--- |
| Pending | Not yet started |
| In-Progress | Currently being worked on |
| Needs Clarification | Ambiguous fix — questions posted in ticket, awaiting user answers |
| Awaiting Confirmation | Fix applied, awaiting user verification |
| Deep Investigation | Undergoing thorough investigation (Protocol 02b) |
| Blocked | Stuck after 3+ attempts, needs human input |
| Needs Human Debug | Investigation exhausted, requires manual debugging |
