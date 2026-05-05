# PROJ-347: Closeout Sprint 5 - Pattern 33 placeholder gaps and Stage-1 purity from review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-347` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Pattern §33 + Stage-1 purity (T4.1 .. T4.7) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff)
**Last Action:** Project scaffolded
**Next Action:** Begin Phase 1
**Blockers:** None (file-disjoint with PROJ-343..346; can run after them in any order)

## Overview

Mechanical extension of the MAJ-001 fix for `EmpireBuildQueueWindow` to sibling classes (StarListWindow, PlanetListWindow, SystemSelectionWindow, etc.) that were missed. Plus Stage-1 purity fix for `EmpirePanelWindow.load_resource_icons` and a self-contradiction in `docs/02_PATTERNS.md`. T4.7 (NewGameSetupScreen widget extraction) is the only non-mechanical sub-task and requires user confirmation before committing.

## Goals

- T4.1: `virtual_table` placeholder added to `star_list_window.py` and `planet_list_window.py` (matches MAJ-001 fix shape).
- T4.2: `btn_confirm`/`btn_cancel` placeholders added to `system_selection_window.py`.
- T4.3: `process_event` placeholders added to `SaveSelectionWindow`, `RaceBrowserDialog`, `DesignSelectorWindow`.
- T4.4: `EmpirePanelWindow.load_resource_icons()` moved AFTER bypass guard (Stage-1 purity restored).
- T4.5: `docs/02_PATTERNS.md` self-contradiction fixed (lines 1765-1776 contradict line 1833).
- T4.6: `_window_init_bypassed = False` set in `RaceSetupScreen` and `NewGameSetupScreen` production paths.
- T4.7: NewGameSetupScreen widget extraction decision (move 400 LOC into builder, or remove builder facade) — confirm with user.

## Scope

**In:**
- `game/ui/screens/star_list_window.py:467-478` (T4.1)
- `game/ui/screens/planet_list_window.py:720-739` (T4.1)
- `game/ui/screens/system_selection_window.py:143,153` (T4.2)
- `game/ui/screens/save_selection_window.py` (T4.3)
- `game/ui/screens/race_browser_dialog.py` (T4.3 — locate via grep)
- `game/ui/screens/design_selector_window.py` (T4.3 — locate via grep)
- `game/ui/screens/empire_panel_window.py:114-116` (T4.4)
- `docs/02_PATTERNS.md` (T4.5 — lines 1765-1776 vs 1833)
- `game/ui/screens/race_setup/screen.py` (T4.6)
- `game/ui/screens/new_game_setup_screen.py` (T4.6, possibly T4.7)
- `game/ui/screens/new_game_setup_ui_builder.py` (T4.7)
- New characterization tests for each placeholder + Stage-1 purity test for T4.4

**Out:**
- Any wider Pattern §33 retrofit beyond the listed siblings.
- `race_setup/screen.py` (484 LOC) and `new_game_setup_screen.py` (733 LOC) §2.4 LOC-ceiling violations are NOTED in PROJ-349 / out of scope here unless T4.7 forces a split.

## Key Files

| Component | File Path |
|-----------|-----------|
| T4.1 a | `game/ui/screens/star_list_window.py:467-478` |
| T4.1 b | `game/ui/screens/planet_list_window.py:720-739` |
| T4.2 | `game/ui/screens/system_selection_window.py:143,153` |
| T4.3 | `game/ui/screens/{save_selection_window, race_browser_dialog, design_selector_window}.py` |
| T4.4 | `game/ui/screens/empire_panel_window.py:114-116` |
| T4.4 reference | `game/ui/panels/empire_treasury_panel.py:311-333` (`load_resource_icons`) |
| T4.5 | `docs/02_PATTERNS.md:1765-1776, 1833` |
| T4.6 | `game/ui/screens/race_setup/screen.py`, `game/ui/screens/new_game_setup_screen.py` |
| T4.7 | `game/ui/screens/new_game_setup_ui_builder.py:37-38` |

## Verification

- [ ] All Phase 1 tasks checked
- [ ] `pytest tests/unit/ui/screens/ -x -q` — all pass
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
