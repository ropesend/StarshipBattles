# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*QA Session 20260325_191105: BUG-101, BUG-102, BUG-105, BUG-106 confirmed fixed and archived. Remaining: BUG-80, BUG-107, BUG-108, BUG-109 still awaiting confirmation.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-80 | 2026-02-11 | Planets List - Planet details panel dimensions and positioning | Awaiting Confirmation | [BUG-80.md](active_bugs/BUG-80.md) |
| BUG-107 | 2026-03-24 | Game crashes on turn advance after loading a save — ShipInstance missing registries | Awaiting Confirmation | [BUG-107.md](active_bugs/BUG-107.md) |
| BUG-108 | 2026-03-24 | Planet generation does not check for hex collisions with secondary/additional stars | Awaiting Confirmation | [BUG-108.md](active_bugs/BUG-108.md) |
| BUG-109 | 2026-03-24 | Resources decline each turn despite large production surplus — eventual total maintenance failure | Awaiting Confirmation | [BUG-109.md](active_bugs/BUG-109.md) |
| BUG-111 | 2026-03-28 | SeekerPointDefenseNoneScenario crashes during batch run — missing `attacker` attribute | Awaiting Confirmation | [BUG-111.md](active_bugs/BUG-111.md) |
| BUG-115 | 2026-04-26 | New Game Setup — Cancel button does not work | Awaiting Confirmation | [BUG-115.md](bugs/active/BUG-115.md) |
| BUG-116 | 2026-04-27 | Workshop quick-add places armor components in wrong layer (CORE/OUTER instead of ARMOR) | Pending | [BUG-116.md](bugs/active/BUG-116.md) |
| BUG-117 | 2026-04-27 | Ship details "Main Systems" shows broken "Max Egy: --" / "Egy Gen: --" rows | Awaiting Confirmation | [BUG-117.md](bugs/active/BUG-117.md) |
| BUG-118 | 2026-04-27 | Race Setup — "Randomize All" doesn't refresh Summary tab left-column labels | Awaiting Confirmation | [BUG-118.md](bugs/active/BUG-118.md) |
| BUG-119 | 2026-04-27 | Plasma Storm sector effects not displayed (storm hex coordinate-frame mismatch) | Pending | [BUG-119.md](bugs/active/BUG-119.md) |
| BUG-120 | 2026-04-27 | Planet "Yard" resource row shows yard capacity instead of actual queue consumption | Pending | [BUG-120.md](bugs/active/BUG-120.md) |
| BUG-121 | 2026-04-27 | Strategy screen mouse-wheel zoom does not work | Pending | [BUG-121.md](bugs/active/BUG-121.md) |

## 3. Current Focus: None
No bugs currently in progress.

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
