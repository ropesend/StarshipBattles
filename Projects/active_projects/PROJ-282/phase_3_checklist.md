# Phase 3: Extract BattleSetupViewModel

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract view-state attributes from `FleetBattleSetupScreen` into a new `BattleSetupViewModel` class. ViewModel is a pure data object — no behavior — mirroring the TestLab pattern.

**Prerequisite:** Phase 2 complete — `BattleSetupState` owns all data-model state (including complex toggles). ViewModel handles only VIEW state (selections, expansions, scroll positions).

---

## Tasks

### Task 3.1: Identify view-state attributes on the screen [Simple]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** N/A (research)

Read the screen end-to-end and enumerate every attribute that represents VIEW state (not DOMAIN state). Candidates from the audit:
- [ ] Selected fleet index
- [ ] Expanded task force / squadron nodes in the hierarchy tree
- [ ] Scroll positions on left/center/right panels
- [ ] Currently-highlighted design in the library
- [ ] Current UI element references (avoid — these are renderer-owned)
- [ ] Record findings in `.agent_reports/PROJ-282-audit/view_state_attrs.md` or inline here

**Notes:**

### Task 3.2: Write tests for BattleSetupViewModel [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [ ] Test: default construction has sensible defaults (nothing selected, nothing expanded)
- [ ] Test: each view-state attribute has a setter-like method if interaction is needed
- [ ] Test: ViewModel is a dataclass (frozen=False — view state mutates) with type hints
- [ ] Test: ViewModel has no dependency on `BattleSetupState` — takes no constructor args OR takes state as reference only for reactive updates
- [ ] Test: instance can be constructed in isolation for unit tests (no pygame, no registries)

**Notes:**

### Task 3.3: Implement `BattleSetupViewModel` [Medium]
**File:** `game/ui/screens/battle_setup/view_model.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [ ] Create the module + class as a `@dataclass`
- [ ] Include every view-state attribute identified in Task 3.1 with type hints + defaults
- [ ] Keep it PURE DATA — no methods that talk to the screen, state, or UI elements
- [ ] Verify 100% of Task 3.2 tests pass

**Notes:** Follow the exact shape of [game/ui/screens/test_lab/view_model.py](../../../game/ui/screens/test_lab/view_model.py) for consistency.

### Task 3.4: Migrate screen to own a BattleSetupViewModel [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] In `__init__`, instantiate `self.view_model = BattleSetupViewModel()`
- [ ] Replace every direct screen attribute read with `self.view_model.attr` read
- [ ] Replace every direct screen attribute write with `self.view_model.attr = ...` write
- [ ] Verify the screen still compiles and renders
- [ ] Run existing screen tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BattleSetupViewModel` class exists in `game/ui/screens/battle_setup/view_model.py`
- [ ] Screen no longer holds direct view-state attributes (all via ViewModel)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4 (extract Renderer)
