# Phase 3: Extract BattleSetupViewModel

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract view-state attributes from `FleetBattleSetupScreen` into a new `BattleSetupViewModel` class. ViewModel is a pure data object — no behavior — mirroring the TestLab pattern.

**Prerequisite:** Phase 2 complete — `BattleSetupState` owns all data-model state (including complex toggles). ViewModel handles only VIEW state (selections, expansions, scroll positions).

---

## Tasks

### Task 3.1: Identify view-state attributes on the screen [Simple]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** N/A (research)

Read the screen end-to-end and enumerate every attribute that represents VIEW state (not DOMAIN state). Findings (from Phase 1 [delegate_map.md](../../../.agent_reports/PROJ-282-audit/delegate_map.md) instance-attribute table):
- [x] `active_side`, `active_fleet_index` — selection indices
- [x] `selected_tf_index`, `selected_sq_index`, `selected_ship_index` — hierarchy/ship selection (None = nothing selected)
- [x] `available_designs` — scanned ship designs (populated by `_scan_designs`)
- [x] NOT moved: pygame_gui element references (`_ui_manager`, `_side_dropdown`, `_fleet_buttons`, etc.) — renderer-owned; Phase 4
- [x] NOT moved: end-condition settings (`tick_limit`, `end_all_destroyed`, etc.) — these are domain config, Phase 2+later decides where they live
- [x] Expanded TF/SQ nodes / scroll positions — **not currently tracked on the screen**; would be Phase 4+ additions if needed

**Notes:** No separate audit report needed — findings match the Phase 1 audit. Scope: 6 view-state attributes to migrate.

### Task 3.2: Write tests for BattleSetupViewModel [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [x] Test: default construction has sensible defaults (nothing selected, nothing expanded)
- [x] Test: each view-state attribute has a setter-like method if interaction is needed (direct dataclass attribute assignment + `clear_selection` helper)
- [x] Test: ViewModel is a dataclass (frozen=False — view state mutates) with type hints
- [x] Test: ViewModel has no dependency on `BattleSetupState` — takes no constructor args OR takes state as reference only for reactive updates
- [x] Test: instance can be constructed in isolation for unit tests (no pygame, no registries)

**Notes:** 9 tests in new file [test_view_model.py](../../../tests/unit/ui/screens/battle_setup/test_view_model.py) covering defaults, mutation, `clear_selection`/`has_tf_selection`/`has_sq_selection` helpers, and pygame-import absence (AST-walk guard). Started red (9 fails), green after implementation.

### Task 3.3: Implement `BattleSetupViewModel` [Medium]
**File:** `game/ui/screens/battle_setup/view_model.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [x] Create the module + class as a `@dataclass`
- [x] Include every view-state attribute identified in Task 3.1 with type hints + defaults
- [x] Keep it PURE DATA — no methods that talk to the screen, state, or UI elements
- [x] Verify 100% of Task 3.2 tests pass (9/9)

**Notes:** `BattleSetupViewModel` at [game/ui/screens/battle_setup/view_model.py](../../../game/ui/screens/battle_setup/view_model.py). Added 3 pure helpers: `clear_selection()` (reset TF/SQ/ship), `has_tf_selection()`, `has_sq_selection()`. Pattern is a SIMPLIFIED TestLab pattern — no EventBus, because the screen still rebuilds pygame_gui on every mutation (rebuild-on-mutation is preserved through PROJ-282; render-every-frame is a future opportunity flagged in [testlab_pattern.md](../../../.agent_reports/PROJ-282-audit/testlab_pattern.md)).

### Task 3.4: Migrate screen to own a BattleSetupViewModel [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [x] In `__init__`, instantiate `self.view_model = BattleSetupViewModel()`
- [x] Replace every direct screen attribute read with `self.view_model.attr` read — via **property shims** on the screen class. Shims keep the existing ~60 call-sites across the screen working without mass rename.
- [x] Replace every direct screen attribute write with `self.view_model.attr = ...` write — same shims.
- [x] Verify the screen still compiles and renders (3466 regression tests pass)
- [x] Run existing screen tests (70 pass in Phase 3 scope: state + view_model + setup battle_setup suites)
- [x] Add 4 screen-delegation tests (`TestScreenDelegatesViewStateToViewModel`) as regression guards for shim routing

**Notes:** **Decided to use property shims** rather than mass-renaming all ~60 call-sites to `self.view_model.*`. Rationale: (a) the screen class is going to be deleted entirely in Phase 8 when the thin `screen.py` replaces it — mass renames now evaporate, (b) shims keep diff small + tests stable, (c) the invariant "storage is on view_model" holds — the 4 new shim-routing tests prove it. Trade-off noted in [decisions.md](decisions.md) (add).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `BattleSetupViewModel` class exists in `game/ui/screens/battle_setup/view_model.py`
- [x] Screen no longer holds direct view-state attributes — storage is on `view_model`; screen exposes property shims that route to it (verified by `TestScreenDelegatesViewStateToViewModel` in test_battle_setup_state.py)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (extract Renderer)
