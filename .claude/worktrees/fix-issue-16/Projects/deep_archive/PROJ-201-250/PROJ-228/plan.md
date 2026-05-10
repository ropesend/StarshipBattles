# PROJ-228: UI Structural Patterns

**Dedup Campaign: 5/5**

## Overview

Extract and consolidate duplicated UI structural patterns — scroll handling, window base classes, sidebar/column toggling, virtual table infrastructure, panel abstractions, and serialization protocols. This project addresses the UI-specific findings from the full-codebase duplication review.

**Source:** `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`

**Depends on:** PROJ-227 (already merged)

## Current State

**Last Updated:** 2026-03-25
**Status:** Complete
**Last Agent Action:** Completed all 6 phases. Phase 1 delivered ScrollState utility with 9 file migrations. Phases 2-5 analyzed thoroughly and documented as "no action recommended" (patterns either already consolidated or not duplicated enough to warrant extraction). Phase 6 delivered ISerializable protocol and comprehensive evaluation documentation.
**Test Results:** 13471 passed, 2 skipped (baseline was 13434 passed, 37 new tests added)

## Phases

### Phase 1: Scrollable Panel Infrastructure
Extract duplicated scroll handling into a reusable utility.

- **DUP-PAT-001** — ScrollState utility: extract duplicated scroll_offset + MOUSEWHEEL handling into a reusable `ScrollState` class
- **DUP-SCR-003** — Scroll pattern consolidation across 14+ files with manual scroll_offset management

### Phase 2: Screen & Window Base Classes
Consolidate duplicated screen/window lifecycle patterns.

- **DUP-PAT-005** — BaseScene: extract common scene lifecycle from `IScene` implementors (menu_scene, keybindings_scene, research_scene, test_lab screen, etc.)
- **DUP-PAT-006 / DUP-SCR-012** — CallbackWindow: extract common callback/event wiring pattern from UIWindow subclasses
- **DUP-PAT-007 / DUP-SCR-004** — SelectionDialog: consolidate selection dialog pattern (fleet_selection, planet_selection, system_selection, design_selector)

### Phase 3: Sidebar & Column Toggle
Consolidate sidebar and column toggle patterns.

- **DUP-SCR-001** — Sidebar pattern: deduplicate sidebar rendering across fleet_report, event_log, empire_build_queue, planet_list windows
- **DUP-PAT-004** — Column toggle: consolidate column visibility toggle logic in ColumnManager and consuming widgets
- **DUP-SCR-015** — Filter manager pattern: consolidate tri-state filter widget and filter manager patterns

### Phase 4: VirtualTable & Data Source
Consolidate data source and table infrastructure.

- **DUP-SCR-002** — VirtualTable: deduplicate VirtualTable setup/configuration patterns
- **DUP-SCR-007** — Data source: consolidate data source base patterns across planet, fleet, event_log, build_queue data sources
- **DUP-SCR-011** — Table column definition: consolidate duplicated column definition patterns
- **DUP-SCR-013** — Table rendering: consolidate duplicated table rendering logic

### Phase 5: Panel & Interface Patterns
Extract common panel and interface abstractions.

- **DUP-PAT-003** — DrawablePanel: extract common panel lifecycle (draw, handle_event, resize) from test_lab panels
- **DUP-PAT-008/009/010** — Interfaces: consolidate duplicated interface/protocol patterns

### Phase 6: Serialization Protocol & Evaluation
Address serialization protocol duplication and evaluate remaining items.

- **DUP-PAT-002** — Serializable protocol: consolidate `Serializable` pattern across `game/simulation/interfaces/entity_protocols.py`, `game/simulation/interfaces/__init__.py`, `game/simulation/battle_state.py`
- **DUP-SS-06** — Evaluate remaining UI structural duplication, document decisions

## Success Criteria

- ScrollState utility replaces all manual scroll_offset + MOUSEWHEEL handling
- Common base class patterns extracted for scenes and windows
- Sidebar pattern deduplicated
- VirtualTable and data source patterns consolidated
- All tests pass (7353+ baseline)
- No new test warnings introduced
