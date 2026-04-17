# Phase 5: Update Serializer + Bump Save Format

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 5`

**Status:** Not Started
**Objective:** Remove `component_damage` from save shape. Bump format version. No migration code.

---

## Tasks

### Task 5.1: Remove `component_damage` from serialize path [Medium]
**File:** `game/strategy/data/ship_instance_serializer.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py -v`

- [ ] Per audit: 3 serializer sites
- [ ] `to_dict`/`serialize` path: stop writing `component_damage` key
- [ ] `from_dict`/`deserialize` path: do NOT read `component_damage` — if present in old saves, ignore
- [ ] Verify `components` field is correctly serialized (it already is, per PROJ-269 Phase 2)
- [ ] Run serializer tests — 5 tests in `test_ship_instance_serializer.py`. Several likely reference `component_damage` — update per Phase 7. For now, just ensure core round-trip of `components` works.

**Notes:**

### Task 5.2: Bump save format version [Simple]
**File:** `game/strategy/data/ship_instance_serializer.py` (or wherever save format version is defined)
**Tests:** Manual

- [ ] Locate the save format version constant (e.g. `SAVE_FORMAT_VERSION = "1.2"` or similar)
- [ ] Bump major or minor per project conventions (document in decisions.md)
- [ ] If there's any save-load compatibility check, ensure it REJECTS old saves with a clear user message: "Save format changed in PROJ-276; old saves are not migrated."

**Notes:**

### Task 5.3: Roundtrip test [Simple]
**File:** `tests/integration/save_load/test_roundtrip_ships.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py -v`

- [ ] Test: save a ShipInstance with per-instance component state, reload, verify all instance HPs preserved
- [ ] Test: multi-instance ship with partial damage on #1, roundtrip, verify #1 still partial / #0 and #2 still full
- [ ] Remove any test that asserts `component_damage` serialization (those will fail and need rewriting)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 5`
