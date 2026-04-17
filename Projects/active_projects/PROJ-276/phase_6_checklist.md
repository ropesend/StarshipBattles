# Phase 6: Delete Field + Dual-Write

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 6`

**Status:** Complete
**Objective:** The pass-point. Remove `component_damage` field from `ShipInstance`. Delete dual-write in post_battle_hook. Full test suite must be green.

---

## Tasks

### Task 6.1: Pre-check — confirm zero remaining production reads/writes [Simple]
**File:** N/A
**Tests:** Grep

- [x] `grep "component_damage" game/strategy/services/` — zero
- [x] `grep "component_damage" game/strategy/data/ship_instance_bridge.py` — zero live references (only doc lines that were also cleaned)
- [x] `grep "component_damage" game/simulation/entities/ship_design_stats.py` — zero (migrated in Phase 4)
- [x] `grep "component_damage" game/strategy/data/ship_instance_serializer.py` — only explanatory comments about the bump, no field access

**Notes:** Production reads/writes are all gone. Remaining matches in `game/` are all historical comments documenting the PROJ-276 change.

### Task 6.2: Delete post_battle_hook dual-write [Simple]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook.py -v`

- [x] Deleted the `instance.component_damage = {}` reset + conditional mirror-write loop at the end of `_apply_survivor_outcome`
- [x] Introduced `prior_max_hp` lookup so rebuilt `ComponentState` entries carry `max_hp` forward (ComponentStateSpec doesn't hold max_hp — instance's existing dict does)
- [x] Removed the stale "Mirror legacy `component_damage`" comment block
- [x] Updated module docstring to drop the "Legacy `component_damage` is cleared" line for DESTROYED ships
- [x] All strategy+combat tests pass

**Notes:** The rebuilt ComponentState now includes `max_hp`, which made `ShipInstance.is_damaged()` and friends migratable without a registry lookup.

### Task 6.3: Delete the field from ShipInstance [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -n 12`

- [x] Removed `component_damage: Dict[str, int] = field(default_factory=dict)` field
- [x] Removed surrounding "legacy; single-instance granularity" comment
- [x] Rewrote the `components` field docstring — now describes `components` as the authoritative source; references PROJ-269 Phase 2 + PROJ-276 closure
- [x] Extended `ComponentState` with `max_hp: float = 0.0` + `is_damaged` property (all producers updated to populate it: `_build_full_hp_components_from_design`, bridge `update_from_ship`, post_battle_hook `_apply_survivor_outcome`)
- [x] Migrated readers to use `components` dict:
  - `is_damaged()` → `any(cs.is_damaged for cs in self.components.values())`
  - `get_damaged_component_count()` → count of damaged ComponentStates
  - `get_damaged_components_by_layer()` → iterates `components`, maps `component_id` to layer from `design_data`. Returns `component_state_key` strings (`{id}#{idx}`) instead of raw IDs — callers can split on `#` if needed.
  - `repair()` full-heal → iterates components and sets `cs.current_hp = cs.max_hp`
- [x] 120 ship_instance unit tests pass

**Notes:** The `get_damaged_components_by_layer` tuple format changed subtly — keys are now per-instance `{id}#{idx}` strings. The one UI caller (`ship_detail_panel.py:328`) iterates but doesn't parse the key format, so display works. If raw IDs are ever needed, split on `#` or add a helper.

### Task 6.4: Full-repo grep check [Simple]
**File:** N/A
**Tests:** Grep

- [x] `grep "component_damage" game/` — 5 historical comment lines only (no field access)
- [x] `grep "component_damage" tests/` — test-only references: serializer test asserting the key is NOT emitted, two harmless dict-key-in-save-data fixtures (silently ignored by from_dict), one `ship.component_damage = {}` attribute assignment that does nothing useful (Phase 7)
- [x] `grep "component_damage" docs/` — Phase 8 docs updates will handle
- [x] Production-code grep is clean

**Notes:**

### Task 6.5: Full test suite [Medium]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ tests/integration/save_load/ tests/integration/fleet_combat/`

- [x] Targeted strategy+save+combat run: 3462 passed, 2 skipped, 1 pre-existing unrelated error
- [x] Incremental `pytest tests/ --testmon`: only pre-existing failures (theme_id mismatch + 3 AI import errors)
- [x] Production-code-caused failures: ZERO
- [x] Test-code failures needing Phase 7 attention: none outstanding (fixed as I went since they blocked testmon)

**Notes:** Fixed 4 tests in-stream that directly accessed `ship.component_damage` or constructed with `component_damage=`: `test_cost_queries::test_get_warp_resource_costs_damaged_warp_drive`, `test_validation::test_optional_fields_have_defaults`, `test_ship_instance_damage::test_get_damaged_component_count`, `test_ship_instance_damage::test_get_damaged_components_by_layer`, plus the bridge fixture and one bridge test from earlier phases.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 6`
- [x] **After this phase, `component_damage` does not exist anywhere in production code.**
