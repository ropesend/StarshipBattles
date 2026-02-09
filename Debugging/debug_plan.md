# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*14 bugs fixed on 2026-01-24: BUG-35, BUG-37, BUG-38, BUG-42, BUG-46, BUG-47, BUG-48, BUG-49, BUG-50, BUG-52, BUG-53, BUG-54, BUG-55. All awaiting confirmation.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-46 | 2026-01-23 | Fleet Report ship top-down image too small | Awaiting Confirmation | [BUG-46.md](active_bugs/BUG-46.md) |
| BUG-49 | 2026-01-24 | Component Modifier Grid - hide irrelevant columns | Awaiting Confirmation | [BUG-49.md](active_bugs/BUG-49.md) |
| BUG-50 | 2026-01-24 | Load Design Window - right edge clipped | Awaiting Confirmation | [BUG-50.md](active_bugs/BUG-50.md) |
| BUG-52 | 2026-01-24 | Design Workshop - rightmost panel should extend full height | Awaiting Confirmation | [BUG-52.md](active_bugs/BUG-52.md) |
| BUG-53 | 2026-01-24 | Load Design Panel - overwritten by Component Modifier Grid | Awaiting Confirmation | [BUG-53.md](active_bugs/BUG-53.md) |
| BUG-54 | 2026-01-24 | Planet selection hitbox mismatch after angle increase | Awaiting Confirmation | [BUG-54.md](active_bugs/BUG-54.md) |
| BUG-55 | 2026-01-24 | Build Queue - no selection indication | Awaiting Confirmation | [BUG-55.md](active_bugs/BUG-55.md) |
| BUG-56 | 2026-02-07 | New Game Setup - Star system count selector (25-150) | Awaiting Confirmation | [BUG-56.md](active_bugs/BUG-56.md) |
| BUG-57 | 2026-02-07 | Race Setup window too small | Awaiting Confirmation | [BUG-57.md](active_bugs/BUG-57.md) |
| BUG-58 | 2026-02-07 | Race Setup - racial points not shown in Environment window | Awaiting Confirmation | [BUG-58.md](active_bugs/BUG-58.md) |
| BUG-59 | 2026-02-07 | Game Setup + Race Setup visual theme mismatch | Awaiting Confirmation | [BUG-59.md](active_bugs/BUG-59.md) |
| BUG-60 | 2026-02-07 | Rename all "Race" references to "Species" (code + UI) | Awaiting Confirmation | [BUG-60.md](active_bugs/BUG-60.md) |
| BUG-61 | 2026-02-07 | Species Setup - aptitude range 1-100, exponential cost above 50 | Awaiting Confirmation | [BUG-61.md](active_bugs/BUG-61.md) |
| BUG-62 | 2026-02-07 | Homeworld type should set default environmental preferences | Awaiting Confirmation | [BUG-62.md](active_bugs/BUG-62.md) |
| BUG-63 | 2026-02-07 | Starting planet should match species ideal conditions | Awaiting Confirmation | [BUG-63.md](active_bugs/BUG-63.md) |
| BUG-64 | 2026-02-07 | Design Workshop - component disappears in multi-layer placement | Awaiting Confirmation | [BUG-64.md](active_bugs/BUG-64.md) |
| BUG-65 | 2026-02-07 | Design Workshop - modifiers should auto-select applicable ones | Awaiting Confirmation | [BUG-65.md](active_bugs/BUG-65.md) |
| BUG-66 | 2026-02-07 | Design Workshop - hide vehicle theme selector in strategy mode | Awaiting Confirmation | [BUG-66.md](active_bugs/BUG-66.md) |
| BUG-67 | 2026-02-07 | Strategy layer - add "Build Queues" button to top bar | Awaiting Confirmation | [BUG-67.md](active_bugs/BUG-67.md) |
| BUG-68 | 2026-02-07 | Fleet Report - ship selection + ship report + remove from fleet | Awaiting Confirmation | [BUG-68.md](active_bugs/BUG-68.md) |
| BUG-69 | 2026-02-07 | Strategy view - scroll wheel zoom locks up intermittently | Awaiting Confirmation | [BUG-69.md](active_bugs/BUG-69.md) |
| BUG-70 | 2026-02-07 | Colonize order should load population before moving | Awaiting Confirmation | [BUG-70.md](active_bugs/BUG-70.md) |
| BUG-71 | 2026-02-08 | Design Workshop - +/- buttons affect wrong layer for duplicate components | Awaiting Confirmation | [BUG-71.md](active_bugs/BUG-71.md) |
| BUG-72 | 2026-02-08 | Leader needs a name in Species Setup | Awaiting Confirmation | [BUG-72.md](active_bugs/BUG-72.md) |
| BUG-73 | 2026-02-08 | Species Setup - Homeworld type selection still reports "Custom" | Awaiting Confirmation | [BUG-73.md](active_bugs/BUG-73.md) |
| BUG-74 | 2026-02-08 | Normal new games should have homeworld complexes pre-built like quickstart | Awaiting Confirmation | [BUG-74.md](active_bugs/BUG-74.md) |
| BUG-75 | 2026-02-08 | Planet details panel dimensions mismatch in planets list vs strategy layer | Awaiting Confirmation | [BUG-75.md](active_bugs/BUG-75.md) |
| BUG-76 | 2026-02-08 | Turn log does not show at start of each strategy layer turn | Awaiting Confirmation | [BUG-76.md](active_bugs/BUG-76.md) |

## 3. Current Focus: None
**Status:** All pending bugs fixed. BUG-73, BUG-74, BUG-75, BUG-76 set to Awaiting Confirmation. No pending bugs remain.
Full test suite: 7340 passed, 4 failed (pre-existing failures in test_transfer_dialog.py, unrelated to fixes).
