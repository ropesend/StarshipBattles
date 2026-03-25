# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*QA Session 20260324_122443: BUG-98, BUG-99, BUG-100 confirmed fixed and archived. New tickets: BUG-102 (wrong ship theme image in build queue), BUG-103 (build queue removal broken for facility queues), BUG-104 (event log column reorder not wired up), BUG-105 (fleet orders dialog too narrow). BUG-80 still awaiting confirmation.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-80 | 2026-02-11 | Planets List - Planet details panel dimensions and positioning | Awaiting Confirmation | [BUG-80.md](active_bugs/BUG-80.md) |
| BUG-101 | 2026-03-23 | Fleet info panel shows raw enum names for MOVE_TO_FLEET and JOIN_FLEET orders | Awaiting Confirmation | [BUG-101.md](active_bugs/BUG-101.md) |
| BUG-102 | 2026-03-24 | Build queue ship detail panel shows wrong species theme image | Awaiting Confirmation | [BUG-102.md](active_bugs/BUG-102.md) |
| BUG-105 | 2026-03-24 | Fleet orders dialog too narrow — down arrow and X buttons hidden until resized | Awaiting Confirmation | [BUG-105.md](active_bugs/BUG-105.md) |
| BUG-106 | 2026-03-24 | "Select Move Type" dialog click passes through to hex map, creating duplicate move orders | Awaiting Confirmation | [BUG-106.md](active_bugs/BUG-106.md) |
| BUG-107 | 2026-03-24 | Game crashes on turn advance after loading a save — ShipInstance missing registries | Awaiting Confirmation | [BUG-107.md](active_bugs/BUG-107.md) |
| BUG-108 | 2026-03-24 | Planet generation does not check for hex collisions with secondary/additional stars | Awaiting Confirmation | [BUG-108.md](active_bugs/BUG-108.md) |
| BUG-109 | 2026-03-24 | Resources decline each turn despite large production surplus — eventual total maintenance failure | Awaiting Confirmation | [BUG-109.md](active_bugs/BUG-109.md) |

## 3. Current Focus: BUG-106
**Status:** Awaiting Confirmation — fix applied, all 5 untracked dialogs now tracked for click-blocking.

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
