# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*14 bugs fixed on 2026-01-24: BUG-35, BUG-37, BUG-38, BUG-42, BUG-46, BUG-47, BUG-48, BUG-49, BUG-50, BUG-52, BUG-53, BUG-54, BUG-55. All awaiting confirmation.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-68 | 2026-02-07 | Fleet Report - ship selection + ship report + remove from fleet | Deep Investigation | [BUG-68.md](active_bugs/BUG-68.md) |
| BUG-70 | 2026-02-07 | Colonize order should load population before moving | Awaiting Confirmation | [BUG-70.md](active_bugs/BUG-70.md) |
| BUG-73 | 2026-02-08 | Species Setup - Homeworld type selection still reports "Custom" | Awaiting Confirmation | [BUG-73.md](active_bugs/BUG-73.md) |
| BUG-80 | 2026-02-11 | Planets List - Planet details panel dimensions and positioning | Awaiting Confirmation | [BUG-80.md](active_bugs/BUG-80.md) |
| BUG-81 | 2026-02-11 | Species Setup - Load Saved Species does nothing | Awaiting Confirmation | [BUG-81.md](active_bugs/BUG-81.md) |
| BUG-82 | 2026-02-11 | Design Workshop - Load Design window is very slow to open | Awaiting Confirmation | [BUG-82.md](active_bugs/BUG-82.md) |
| BUG-83 | 2026-02-11 | Fleet Report - Missing special capability columns and filters | Awaiting Confirmation | [BUG-83.md](active_bugs/BUG-83.md) |
| BUG-84 | 2026-02-11 | Warp Gate Close and Planet Destroyer orders not registering | Blocked | [BUG-84.md](active_bugs/BUG-84.md) |
| BUG-85 | 2026-02-11 | New game colonies report 0 population instead of max | Awaiting Confirmation | [BUG-85.md](active_bugs/BUG-85.md) |
| BUG-86 | 2026-02-11 | Build Queue planet details missing resource production numbers | Awaiting Confirmation | [BUG-86.md](active_bugs/BUG-86.md) |
| BUG-87 | 2026-02-11 | Empire Treasury window missing colony resource production totals | Awaiting Confirmation | [BUG-87.md](active_bugs/BUG-87.md) |
| BUG-88 | 2026-02-11 | Empire Population tab blank - missing species information cards | Awaiting Confirmation | [BUG-88.md](active_bugs/BUG-88.md) |
| BUG-89 | 2026-02-28 | Workshop Screen Crash on Design Button Click | Awaiting Confirmation | [BUG-89.md](active_bugs/BUG-89.md) |
| BUG-90 | 2026-02-28 | Incorrect atmosphere coloring in planet details box | Awaiting Confirmation | [BUG-90.md](active_bugs/BUG-90.md) |
| BUG-91 | 2026-02-28 | Missing planet portrait in build yard UI | Awaiting Confirmation | [BUG-91.md](active_bugs/BUG-91.md) |
| BUG-92 | 2026-02-28 | New Game Setup fails to populate loaded species data | Awaiting Confirmation | [BUG-92.md](active_bugs/BUG-92.md) |
| BUG-93 | 2026-02-28 | Fleet move targeting state cannot be completed or canceled | Awaiting Confirmation | [BUG-93.md](active_bugs/BUG-93.md) |
| BUG-94 | 2026-03-14 | Star visual radius too small relative to hex grid | Awaiting Confirmation | [BUG-94.md](active_bugs/BUG-94.md) |
| BUG-95 | 2026-03-14 | Load Species dialog — hover/click only registers in row margins | Awaiting Confirmation | [BUG-95.md](active_bugs/BUG-95.md) |
| BUG-96 | 2026-03-14 | Build queue shows 1.0 turns and total cost instead of per-turn usage | Awaiting Confirmation | [BUG-96.md](active_bugs/BUG-96.md) |

## 3. Current Focus: None
**Status:** BUG-94/95/96 fixed. All bugs in queue fixed or blocked. BUG-84 blocked (needs runtime debugging). All others awaiting confirmation.

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
