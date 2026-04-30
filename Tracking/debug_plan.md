# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*QA Session 20260428_052952: BUG-80 (renumbered to BUG-80A due to ID collision), BUG-107, BUG-108, BUG-109, BUG-111, BUG-115, BUG-116, BUG-117, BUG-118, BUG-119, BUG-120, BUG-121 all confirmed fixed and archived. QA Session 20260428_190154 added BUG-123 / BUG-124 / BUG-125 / BUG-126 — all multi-empire / combat-correctness issues; BUG-122 fix awaiting user verification.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-122 | 2026-04-28 | Multiple fleets disappear when joining each other in the same hex — mutual-join + redirect-without-self-exclusion | Awaiting Confirmation | [BUG-122.md](bugs/active/BUG-122.md) |
| BUG-123 | 2026-04-28 | Event Log shows events from all empires combined; should filter to the active empire | Awaiting Confirmation | [BUG-123.md](bugs/active/BUG-123.md) |
| BUG-124 | 2026-04-28 | Ship skin icons broken on strategy map for every theme — loader looks for `Battlecruiser.png`, files are `battle_cruiser.png` | In-Progress | [BUG-124.md](bugs/active/BUG-124.md) |
| BUG-125 | 2026-04-28 | Hot-seat — drop Command.empire_id + fix session.active_empire rotation; planet + fleet command handlers gate correctly | Awaiting Confirmation | [BUG-125.md](bugs/active/BUG-125.md) |
| BUG-126 | 2026-04-28 | Strategy-layer combat draw silently destroys the smaller fleet — `_resolve_winner_team` survivor-count tiebreaker treats `BattleOutcome.winner=None` as a winnable contest | Awaiting Confirmation | [BUG-126.md](bugs/active/BUG-126.md) |

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
