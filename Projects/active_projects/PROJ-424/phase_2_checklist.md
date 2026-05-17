# Phase 2: Add `OrderMetadataView` (lazy, cycle-safe)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/commands/order_metadata_view.py`
- `tests/unit/strategy/engine/commands/test_order_metadata_view.py`

**Objective:** create the single live read facade over `command_registry` without changing any consumers yet. The view must import `command_registry` only inside `_registry()` so importing the view module does NOT trigger the cycle through the handlers.

---

## Tasks

### Task 2.1: Write failing tests for the view [Medium]
**File:** `tests/unit/strategy/engine/commands/test_order_metadata_view.py`
**Tests:** `pytest tests/unit/strategy/engine/commands/test_order_metadata_view.py -x`

- [ ] Create the test module (and `tests/unit/strategy/engine/commands/__init__.py` if missing)
- [ ] `test_view_movement_matches_registry` — `order_metadata.movement_order_types == command_registry.movement_order_types()`
- [ ] `test_view_action_matches_registry` — same shape
- [ ] `test_view_planet_action_matches_registry` — same shape
- [ ] `test_view_planet_fms_matches_registry` — same shape (relies on Phase 1)
- [ ] `test_view_order_to_ability_matches_registry` — `order_metadata.order_to_ability_map == command_registry.order_to_ability_map()`
- [ ] `test_view_is_lazy_at_import_time` — import `order_metadata_view`, then assert that `game.strategy.engine.commands.registry` is NOT in `sys.modules` (or at least was not imported by `order_metadata_view`'s import alone — use a fresh subprocess or `importlib` reload trick if needed). The point: the cycle stays broken.
- [ ] `test_view_reflects_replace_overlay` — register a `replace=True` overlay on one OrderType, assert the view's `order_to_ability_map[that_type]` reflects the new ability immediately (no cached snapshot)
- [ ] Run all 7 tests; confirm they fail with `ImportError` (no module yet)

**Notes:** [Filled during implementation]

### Task 2.2: Implement `OrderMetadataView` [Medium]
**File:** `game/strategy/engine/commands/order_metadata_view.py`
**Tests:** `pytest tests/unit/strategy/engine/commands/test_order_metadata_view.py -x`

- [ ] Create the file with the class contract specified in [design.md](design.md)
- [ ] `_registry()` staticmethod imports `command_registry`, `seed_default_commands` from `game.strategy.engine.commands.registry` LAZILY (inside the function body, not at module top)
- [ ] On first read: if `len(command_registry) == 0`, call `seed_default_commands(command_registry)`
- [ ] Properties: `movement_order_types`, `action_order_types`, `planet_action_order_types`, `planet_fms_action_order_types`, `order_to_ability_map`
- [ ] Module-level singleton: `order_metadata = OrderMetadataView()`
- [ ] **NO** caching, **NO** invalidation API, **NO** module-level snapshots of property output
- [ ] Verify: all 7 tests pass, including `test_view_is_lazy_at_import_time` and `test_view_reflects_replace_overlay`

**Notes:** [Filled during implementation]

### Task 2.3: Confirm no consumers migrated yet [Simple]
**File:** n/a
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py -x`

- [ ] `git status --short` shows only the new view file + the new test module (plus any `__init__.py` created)
- [ ] Verify: existing characterization tests still pass — production consumers untouched in this phase

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `order_metadata_view.py` exists with lazy registry imports
- [ ] All 7 view tests pass, including lazy-import and replace-overlay guards
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
