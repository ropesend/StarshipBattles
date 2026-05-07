# PROJ-329A — UIWindow retrofit fast wins + inventory + deferral docs

**Branch:** `feat/03c-phase-aware-execution` (continues the audit arc)
**Started:** 2026-05-04
**Source plan:** `C:\Users\rossr\.claude\plans\noble-stirring-galaxy.md` (Tier 5 / PROJ-329A)
**Predecessors:** PROJ-321..328 (audit Sessions 1–4 closed; commits `d7cd97dc1`..`da02bee86`)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Disposition docs (DesignWorkshopScreen + SettingsWindow) | Pending | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Inventory matrix | Pending | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fast-win retrofits (5 classes) | Pending | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Verification + index update | Pending | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phase 0 (disposition docs)
**Next Action:** Add "UIWindow retrofit deferrals" section to `docs/known-issues.md` for DesignWorkshopScreen + SettingsWindow.
**Blockers:** None.

## Overview

Tier 5 of the PROJ-321..328 audit consensus reserved the long tail of
UIWindow / StrategyModalWindow subclasses that were never retrofitted to
the two-stage construction pattern. PROJ-329A is the first of three
sequential follow-ons (A → B → C), focused on:

1. Documenting the two deferrals the audit exposed:
   - DesignWorkshopScreen (NOT a UIWindow — factory pattern, separate concern).
   - SettingsWindow (raw UIWindow, no tests — defer until coverage exists).
2. Producing the canonical inventory matrix for all UIWindow / StrategyModalWindow subclasses.
3. Retrofitting the 5 lowest-risk classes to validate the recipe scales beyond PROJ-325/328's 6.

Per user direction (`noble-stirring-galaxy.md`): zero file overlap between
PROJ-329A/B/C/330 so they can in principle run in parallel; A/B/C are
sequenced to validate the recipe before each next batch; PROJ-330
(`strategy_screen.py` LOC decomposition) runs parallel-safe.

## Goals

- **Phase 0:** Add `docs/known-issues.md` section "UIWindow retrofit deferrals" with concrete rationale for both deferrals.
- **Phase 1:** `findings/uiwindow_inventory.md` matrix from the Explore agent's report (24 classes × 8 columns).
- **Phase 2:** Apply the PROJ-328 Phase A recipe to: `FoodAllocationEditor`, `FleetSelectionWindow`, `PlanetSelectionWindow`, `MoveChoiceWindow`, `PlanetTargetEditor`. Per-class commit; characterization-test diff byte-identical pre/post for any class with existing tests.
- **Phase 3:** Verification + `Projects/projects_index.md` PROJ-329A → Awaiting Verification.

## Scope

**In:**
- 5 production class refactors (low-LOC, no Stage-1 side effects, proven recipe applies)
- 5 new `tests/fixtures/{class}_ui_builder.py` files (Null + Mock pair each)
- Characterization tests written FIRST for the 4 classes without existing tests
- Inventory matrix (the canonical artefact subsequent projects reference)
- 2 deferral entries in `docs/known-issues.md`

**Out:**
- `EmpireBuildQueueWindow`, `EmpirePanelWindow`, `EventLogWindow`, `DesignSelectorWindow`, `StarListWindow`, `RaceBrowserDialog`, `SaveSelectionWindow`, `SystemSelectionWindow` — all PROJ-329B
- `PlanetListWindow`, `CargoQuickDialog`, `PlanetAbilitiesWindow` — all PROJ-329C (facade-coupled)
- `strategy_screen.py` LOC decomposition — PROJ-330
- `DesignWorkshopScreen` — deferred (Phase 0 documents the deferral)
- `SettingsWindow` — deferred (Phase 0 documents the deferral)

## Success criteria

- All 5 retrofitted classes use two-stage `__init__` matching the PROJ-328 Phase A recipe verbatim.
- For each refactored class with existing tests: pytest output byte-identical pre/post (modulo timing).
- 4 new characterization-test files for previously-untested classes (FleetSelectionWindow, PlanetSelectionWindow, MoveChoiceWindow, PlanetTargetEditor).
- `findings/uiwindow_inventory.md` lists all 24 classes with status assignment (Done / 329A / 329B / 329C / Deferred).
- `docs/known-issues.md` has a "UIWindow retrofit deferrals" section.
- Full sharded suite green (modulo the pre-existing 8 codex-discuss-skills failures unrelated to PROJ-32x).
- `python Tools/lint_test_files.py` reports 0 violations.

## Source documents

- [`Projects/active_projects/PROJ-328/phase_1_checklist.md`](../PROJ-328/phase_1_checklist.md) — canonical Phase A recipe (Tasks A.2/A.3/A.4 are reference shapes for the 5 retrofits)
- [`Projects/active_projects/PROJ-325/findings/poc_findings.md`](../PROJ-325/findings/poc_findings.md) — 4 PoC findings every retrofit hits
- [`docs/02_PATTERNS.md`](../../../docs/02_PATTERNS.md) §32 (Compositional) + §33 (Two-stage UIWindow)
- [`docs/03_CONVENTIONS.md`](../../../docs/03_CONVENTIONS.md) §1.6 (file naming) + §2.4 (LOC ceiling)
- [`tests/fixtures/ui_builder_protocol.py`](../../../tests/fixtures/ui_builder_protocol.py) — `UiBuilder[ScreenT]` Protocol (audit S4.5)
- [`tests/fixtures/ui_widget_factory.py`](../../../tests/fixtures/ui_widget_factory.py) — `make_ui_widget` + `bypass_init`

## Verification

- `pytest tests/unit/ui/screens/ -x -q` — current baseline 2285 pass / 1 skipped after audit Session 4. Expect +N for new characterization tests + new fixtures' tests.
- `python Tools/test_sharded/test_sharded.py` — full suite green; pre-existing 8 codex-discuss-skills failures stay constant.
- `python Tools/lint_test_files.py` — 0 violations.
