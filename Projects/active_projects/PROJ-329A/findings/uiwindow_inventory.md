# UIWindow / StrategyModalWindow Subclass Inventory

**Date:** 2026-05-04 (updated 2026-05-04 after Phase 2 pre-flight)
**Author:** PROJ-329A Phase 1 (canonical artefact for PROJ-329A/B/C + PROJ-330)
**Source data:** `grep -lE "class.*\(.*UIWindow\)|class.*\(.*StrategyModalWindow\)|class.*\(.*PlanetTargetEditor\)" game/ui/ -r` + Explore agent inventory (PROJ-329 planning).

**28 classes total** after adding the 4 PlanetTargetEditor concrete subclasses (atmosphere/gravity/water/radiation editors) that the original grep missed because they extend `PlanetTargetEditor` transitively, not `UIWindow`/`StrategyModalWindow` directly.

Distribution:
- **7 done** (PROJ-324/325/328 — including StrategyModalWindow base shell)
- **3 in-scope PROJ-329A** (was 5; PlanetTargetEditor + MoveChoiceWindow turned out to need no retrofit — see Phase 2 pre-flight findings below)
- **8 in-scope PROJ-329B**, **3 in-scope PROJ-329C** (unchanged)
- **7 deferred / no-retrofit-needed** (was 2; +4 PlanetTargetEditor concrete subclasses with no UI tests, +1 MoveChoiceWindow needs no retrofit)
- **1 not-a-UIWindow** (DesignWorkshopScreen, factory pattern; documented in `docs/known-issues.md`)

## Phase 2 pre-flight findings (2026-05-04)

Two 329A targets evaporated on inspection:

1. **`MoveChoiceWindow`** (`game/ui/screens/strategy_windows/move_choice_dialog.py:26`) — has NO `__init__` of its own; inherits everything from `StrategyModalWindow`. Widget construction happens INSIDE a sibling `MoveChoiceDialog.show()` AFTER the window is built (UILabel/UIButton with `container=win`). The bypass shell from `StrategyModalWindow` (PROJ-324 Phase 1) already makes it trivially testable. **No retrofit needed.**
2. **`PlanetTargetEditor`** (`game/ui/screens/planet_target_editor_base.py:29`) — is a BASE class with NO `__init__` of its own. It owns only `process_event` and a `_button_handlers` template-method. **No retrofit needed at the base level.**

The 4 concrete subclasses of `PlanetTargetEditor` (atmosphere/gravity/water/radiation editors, ~951 LOC total) DO have `__init__` work and matching widget construction. They have no UI tests in the `tests/` tree. Deferred for the same reason as `SettingsWindow` (audit S1.7's deferral rubric: retrofit value is proportional to existing test coverage; refactoring untested production code adds risk without locking behavior).

## Reading the matrix

- **Test pattern:** `__new__` (legacy bypass-init via `Cls.__new__(Cls)`), `bypass_init` (PROJ-324 flag), `Compositional` (Pattern §32), `two-stage` (Pattern §33), `none` (no tests found).
- **Builder seam:** Yes/No — does the class accept an explicit `ui_builder` parameter for tests to inject Mock/Null builders?
- **Stage-1 side effects:** Does the cheap-state init (before bypass guard) reach into `scene.facade`, perform I/O, or invoke heavy delegates? Yes/No + brief.
- **Risk tier:** LOW (≤200 LOC, no Stage-1 reaches), MED (200–500 LOC OR Stage-1 reaches), HIGH (>500 LOC OR facade-coupled MVVM).
- **Project assignment:** done / 329A / 329B / 329C / 330 / deferred.

## Inventory matrix

| # | Class | Production file | LOC | Test file(s) | Test pattern | Builder seam? | Stage-1 side effects | Risk | Assigned |
|---|---|---|---:|---|---|---|---|---|---|
| 1 | `RaceSetupScreen` | `game/ui/screens/race_setup/screen.py` | 484 | `test_race_setup_screen.py` (+helpers) | two-stage | Yes (`RaceSetupUiBuilder`) | Yes — delegate factory init | LOW | **done** (PROJ-325) |
| 2 | `BuildQueueListWindow` | `game/ui/screens/build_queue_list_window.py` | 221 | `test_build_queue_list_window.py` | two-stage | Yes (`BuildQueueListUiBuilder`) | No — pure row collection | LOW | **done** (PROJ-328 A) |
| 3 | `OrdersWindow` | `game/ui/screens/orders_window.py` | 469 | `test_orders_window.py` (+helpers) | two-stage | Yes (`OrdersWindowUiBuilder`) | No — pure dataclass init | LOW | **done** (PROJ-328 A) |
| 4 | `FleetReportWindow` | `game/ui/screens/fleet_report_window.py` | 430 | `test_fleet_report_window.py` (+filters) | two-stage | Yes (`FleetReportLayoutBuilder`) | No — widget-free state | LOW | **done** (PROJ-328 A) |
| 5 | `NewGameSetupScreen` | `game/ui/screens/new_game_setup_screen.py` | 733 | `test_new_game_setup_*.py` (3) | two-stage | Yes (`NewGameSetupUiBuilder`) | No — ViewModel only | LOW | **done** (PROJ-328 B) |
| 6 | `TransferDialog` | `game/ui/screens/transfer_dialog.py` | 475 | `test_transfer_dialog*.py` (3) | two-stage | Yes (`TransferDialogUiBuilder`) | Yes — `discover_pod_designs(scene)` I/O | MED | **done** (PROJ-328 C) |
| 7 | `FoodAllocationEditor` | `game/ui/screens/food_allocation_editor.py` | 360 | `test_food_allocation_editor.py` | `__new__` bypass | No | Yes — `gather_rows()` pure-Python, no I/O | LOW | **329A** |
| 8 | `FleetSelectionWindow` | `game/ui/screens/fleet_selection_window.py` | 123 | none | none | No | No | LOW | **329A** (TDD-first) |
| 9 | `PlanetSelectionWindow` | `game/ui/screens/planet_selection_window.py` | 189 | none | none | No | No | LOW | **329A** (TDD-first) |
| 10 | `MoveChoiceWindow` | `game/ui/screens/strategy_windows/move_choice_dialog.py` | 94 | none | inherits | No | No (no `__init__`) | — | **no-retrofit-needed** (no `__init__`; bypass shell from `StrategyModalWindow` already covers) |
| 11 | `PlanetTargetEditor` (base) | `game/ui/screens/planet_target_editor_base.py` | 63 | none | inherits | No | No (no `__init__`) | — | **no-retrofit-needed** (base class; no `__init__`) |
| 11a | `AtmosphereTargetEditor` | `game/ui/screens/atmosphere_target_editor.py` | 273 | none | none | No | Unknown — has `__init__`, not yet inspected | MED | **deferred** (no UI tests; same rubric as SettingsWindow) |
| 11b | `GravityTargetEditor` | `game/ui/screens/gravity_target_editor.py` | 220 | none | none | No | Unknown | MED | **deferred** (no UI tests) |
| 11c | `WaterTargetEditor` | `game/ui/screens/water_target_editor.py` | 227 | none | none | No | Unknown | MED | **deferred** (no UI tests) |
| 11d | `RadiationShieldEditor` | `game/ui/screens/radiation_shield_editor.py` | 231 | none | none | No | Unknown | MED | **deferred** (no UI tests) |
| 12 | `EmpireBuildQueueWindow` | `game/ui/screens/empire_build_queue_window.py` | 569 | `test_empire_build_queue_window.py` + 7 helpers | `__new__` bypass | No | No — state init only | MED | **329B** |
| 13 | `EmpirePanelWindow` | `game/ui/screens/empire_panel_window.py` | 539 | none | none | No | No — state init only | MED | **329B** (TDD-first) |
| 14 | `EventLogWindow` | `game/ui/screens/event_log_window.py` | 515 | `test_event_log_window.py` + integration (3 files) | `__new__` bypass (×3) | No | No — list + callbacks only | MED | **329B** |
| 15 | `DesignSelectorWindow` | `game/ui/screens/design_selector_window.py` | 615 | `test_design_selector_window.py` + integration | `__new__` bypass | No | No — pure library iteration | MED | **329B** |
| 16 | `StarListWindow` | `game/ui/screens/star_list_window.py` | 439 | none | none | No | No — delegates built after super() | MED | **329B** (TDD-first) |
| 17 | `RaceBrowserDialog` | `game/ui/screens/race_browser_dialog.py` | 303 | `test_race_browser_dialog.py` | `__new__` bypass | No | No | LOW | **329B** |
| 18 | `SaveSelectionWindow` | `game/ui/screens/save_selection_window.py` | 399 | `test_save_selection.py` | `__new__` bypass | No | No | LOW | **329B** |
| 19 | `SystemSelectionWindow` | `game/ui/screens/system_selection_window.py` | 125 | `test_system_selection_window.py` | `__new__` bypass | No | No | LOW | **329B** |
| 20 | `PlanetListWindow` | `game/ui/screens/planet_list_window.py` | 698 | `test_planet_list_window.py` + 5 component tests | `__new__` bypass | No | Yes — `facade` parameter in `__init__` | HIGH | **329C** |
| 21 | `CargoQuickDialog` | `game/ui/screens/cargo_quick_dialog.py` | 298 | `test_cargo_quick_dialog*.py` (3 files) | `__new__` bypass | No | Yes — `scene.facade` reach in Stage 1 | MED | **329C** |
| 22 | `PlanetAbilitiesWindow` | `game/ui/screens/planet_abilities_window.py` | 359 | `test_planet_abilities_window_lifecycle.py` | `__new__` bypass | No | Yes — `facade` passed in Stage 1 | MED | **329C** |
| 23 | `StrategyModalWindow` (base) | `game/ui/screens/strategy_modal_window.py` | 160 | `test_strategy_modal_window.py` | two-stage | Yes (implicit `bypass_init` guard, PROJ-324 Phase 1) | No — thin shell | LOW | **done** (PROJ-324 Phase 1 / PROJ-328 A.1) |
| 24 | `SettingsWindow` | `game/ui/screens/settings_window.py` | 109 | none | none | No | Unknown — not in scope | LOW | **deferred** (no tests; see `docs/known-issues.md`) |
| (25) | `DesignWorkshopScreen` | `game/ui/screens/workshop_screen.py` | 648 | various | factory | N/A — not a UIWindow | N/A | OUT | **deferred** (factory pattern; see `docs/known-issues.md`) |

> Row 25 is included for completeness but is not a `UIWindow` /
> `StrategyModalWindow` subclass — it's a bare class instantiated by
> `app.py`. Audit (PROJ-322 Task 5.10) miscategorized it; documented as
> deferred with rationale.

## Summary

| Status | Count | Classes |
|---|---:|---|
| Done (PROJ-324/325/328 + base shell) | 7 | rows 1–6, 23 |
| PROJ-329A (fast wins, post-pre-flight) | 3 | rows 7–9 (FoodAllocationEditor, FleetSelectionWindow, PlanetSelectionWindow) |
| PROJ-329B (mid-tier modals + bundled-test suites) | 8 | rows 12–19 |
| PROJ-329C (facade-coupled, higher risk) | 3 | rows 20–22 |
| No-retrofit-needed (no `__init__` to guard) | 2 | rows 10–11 (MoveChoiceWindow, PlanetTargetEditor base) |
| Deferred — no UI tests (same rubric as SettingsWindow) | 5 | rows 11a–11d, 24 (4 PlanetTargetEditor concrete subclasses + SettingsWindow) |
| Deferred — not a UIWindow | 1 | row 25 (DesignWorkshopScreen) |
| **In-scope total (PROJ-329A + B + C)** | **14** | — |

## Cross-project file-overlap verification

Per the user-approved scoping principle (`C:\Users\rossr\.claude\plans\noble-stirring-galaxy.md`),
PROJ-329A/B/C/330 should have **zero file overlap** so the projects can in
principle run in parallel without stepping on each other.

| Project | Production files touched | Test files touched (incl. fixtures) | Doc files touched |
|---|---|---|---|
| 329A | 5 (rows 7–11) | 5 (one new fixture pair per class) + 1 existing test (FoodAllocation) + 4 new characterization | `docs/known-issues.md`, `Projects/projects_index.md`, `Projects/active_projects/PROJ-329A/*` |
| 329B | 8 (rows 12–19) | ~13 (Empire bundle, EventLog bundle, others) + 8 new fixture pairs + 2 new characterization (StarList, EmpirePanel) | `Projects/projects_index.md`, `Projects/active_projects/PROJ-329B/*` |
| 329C | 3 (rows 20–22) + 3 new controllers + 3 new ui_builders (production) | ~10 (PlanetList components, Cargo cluster, PlanetAbilities) + 3 new fixture pairs | `Projects/projects_index.md`, `Projects/active_projects/PROJ-329C/*` |
| 330 | `game/ui/screens/strategy_screen.py` + 2–3 new helper modules in same dir | `tests/unit/ui/screens/test_strategy_screen.py` (potentially) + new direct-helper unit tests | `Projects/projects_index.md`, `Projects/active_projects/PROJ-330/*` |

**Overlap check:** No production file appears in two projects. The only
shared files are `Projects/projects_index.md` (status row updates — sequential
edits cleanly mergeable) and `docs/known-issues.md` (only 329A touches it).
✓ Zero blocking overlap.

## How to update this matrix

When a class ships, change its `Assigned` cell from the project ID to
`done (PROJ-329X)` and update the per-project Summary count. When a new
UIWindow subclass is added to the codebase, append a row, classify it by
the rubric, and assign it to a project (or document deferral in
`docs/known-issues.md` with rationale).

The grep that produced the row set:
```
grep -lE "class.*\(.*UIWindow\)|class.*\(.*StrategyModalWindow\)|class.*\(.*PlanetTargetEditor\)" game/ui/ -r | sort
```
Re-run this when auditing. The third disjunct (`PlanetTargetEditor`) catches
the 4 concrete editor subclasses that extend `PlanetTargetEditor`
transitively rather than `UIWindow`/`StrategyModalWindow` directly. If the
codebase grows additional intermediate base classes, extend the regex
similarly. If the count of paths changes and this matrix isn't updated, the
inventory is stale.
