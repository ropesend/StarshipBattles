# Phase 3: `WarpPointAbilitySource` adapter + iterator registration

**Status:** Not Started

---

## Tasks

### Task 3.1: Implement `WarpPointAbilitySource` [Medium]
**File:** `game/strategy/services/ability_sources/warp_point.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_warp_point.py` (NEW)

- [ ] Standard adapter test set (source_kind, source_label, source_id, owner_id, get_abilities, affects_hex true at warp_point's hex / false elsewhere, affects_system, get_activation_state returns None).
- [ ] Implement per [design.md](design.md). Adapter takes parent system for global location resolution.
- [ ] Re-export from `__init__.py`.

**Notes:**

### Task 3.2: Register provider with iterator [Simple]
**File:** `game/strategy/services/ability_iterator.py`

- [ ] Failing test: querying `iter_ability_sources_at_hex` at an unstable warp point's hex yields a `WarpPointAbilitySource`.
- [ ] Failing test: a stable warp point (empty abilities) does NOT yield.
- [ ] Add `_warp_point_provider` and register.

**Notes:**

### Task 3.3: Integration test — fleet traversing unstable warp point takes damage [Medium]
**File:** `tests/integration/strategy/test_fleet_through_unstable_warp_point.py` (NEW)

- [ ] Build fixture: a fleet at an unstable warp point's hex.
- [ ] Run `process_environmental_tick`; confirm damage applies per `EnvironmentalDamage`.
- [ ] Confirm Sector panel content for that hex includes the warp_point provider.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
