# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*QA Session 20260314_201559: 15 bugs confirmed fixed and archived (BUG-73, 81, 83-95). BUG-70 fix rejected — TRANSFER order still missing from colonize workflow. BUG-68 remains in deep investigation. BUG-80, BUG-96 still awaiting confirmation.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-68 | 2026-02-07 | Fleet Report - ship selection + ship report + remove from fleet | Awaiting Confirmation | [BUG-68.md](active_bugs/BUG-68.md) |
| BUG-70 | 2026-02-07 | Colonize order should load population before moving | Awaiting Confirmation | [BUG-70.md](active_bugs/BUG-70.md) |
| BUG-80 | 2026-02-11 | Planets List - Planet details panel dimensions and positioning | Awaiting Confirmation | [BUG-80.md](active_bugs/BUG-80.md) |
| BUG-96 | 2026-03-14 | Build queue shows 1.0 turns and total cost instead of per-turn usage | Awaiting Confirmation | [BUG-96.md](active_bugs/BUG-96.md) |
| BUG-97 | 2026-03-14 | Crash when clicking confirmation dialog to clear fleet orders (missing `_pending_confirmation_dialog` attribute) | Awaiting Confirmation | [BUG-97.md](active_bugs/BUG-97.md) |

## 3. Current Focus: BUG-70
**Status:** Deep dive complete. Reworked fix applied — LOAD_POPULATION is now a generic queued order, colony resolved at execution time. Awaiting user confirmation.

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
