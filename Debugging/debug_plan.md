# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*System initialized. TDD Workflow active. Queue populated from recent conversation history.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Spec File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-15 | 2026-01-18 | Screenshot system strategy layer support | Awaiting Confirmation | [BUG-15.md](active_bugs/BUG-15.md) |
| BUG-29 | 2026-01-20 | Build Queue shows designs from other games | Awaiting Confirmation | [BUG-29.md](active_bugs/BUG-29.md) |
| BUG-30 | 2026-01-20 | Load Game buttons non-functional (Load, Show Turns, Delete) | Awaiting Confirmation | [BUG-30.md](active_bugs/BUG-30.md) |

## 3. Current Focus: BUG-29
**Status:** [Awaiting Confirmation]
**Protocol:** 02b Deep Dive - Persistent bug investigation
**Fix Applied:** Removed shared temp folder fallback in DesignLibrary. When `save_path` is `None`, `designs_folder` is now `None` (no designs available for unsaved games).
