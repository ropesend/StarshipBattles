# Phase 2: `FleetAbilitySource` adapter + iterator registration

**Status:** Not Started

---

## Tasks

### Task 2.1: Implement `FleetAbilitySource` [Complex]
**File:** `game/strategy/services/ability_sources/fleet.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_fleet.py` (NEW)

- [ ] Failing tests:
  - [ ] `test_source_kind_is_fleet`
  - [ ] `test_source_label_uses_flagship_name_when_available`
  - [ ] `test_source_label_falls_back_to_fleet_name`
  - [ ] `test_source_id_format`
  - [ ] `test_owner_id_from_fleet`
  - [ ] `test_get_abilities_includes_strategic_scopes_only` — fixture fleet with one ship that has both `ShieldProjection scope: fleet` (combat) and `SensorBoost scope: allied_sector` (strategic). Assert ONLY the SensorBoost entry appears in the adapter's output.
  - [ ] `test_get_abilities_skips_non_combat_capable_ships`
  - [ ] `test_get_abilities_aggregates_across_multiple_ships` — two ships, each with one strategic ability; assert both in the result.
  - [ ] `test_get_abilities_returns_list_for_collisions` — two ships projecting the same `ShieldModifier sector`; result has list of two entries.
  - [ ] `test_affects_hex_matches_fleet_location`
  - [ ] `test_get_activation_state_returns_none` — per decisions.md.
- [ ] Implement per [design.md](design.md). Use `iter_keyed_components` and `extract_abilities_from_component` from existing helpers; reuse `_STRATEGIC_SCOPES` from a shared constant in `system_effects_collector` (export if needed).
- [ ] Re-export from `__init__.py`.

**Notes:**

### Task 2.2: Register provider with iterator [Medium]
**File:** `game/strategy/services/ability_iterator.py`
**Tests:** `tests/unit/strategy/services/test_ability_iterator.py`

- [ ] Failing tests:
  - [ ] `test_iter_at_hex_with_fleet_yields_fleet_source` — fixture: a fleet at H. Iterator at H yields a `FleetAbilitySource`.
  - [ ] `test_iter_at_hex_skips_fleets_without_strategic_abilities` — fleet with only combat-scope ship abilities does NOT yield (empty `get_abilities()`).
  - [ ] `test_iter_at_other_hex_does_not_yield_fleet`.
  - [ ] `test_iter_yields_multiple_fleets_at_same_hex` — two fleets at the same hex from different empires; both yield.
- [ ] Add `_fleet_provider` walking all empires' fleets matching `fleet.location == hex_coord`.
- [ ] May need iterator API changes to plumb `registries` through; coordinate if PROJ-300 didn't provide that.

**Notes:**

### Task 2.3: Owner-aware filtering integration test [Medium]
**File:** `tests/integration/strategy/test_fleet_sector_effects_owner_filtering.py` (NEW)

- [ ] Build fixture: Player 1 has a fleet at hex H with `SensorBoost scope: allied_sector`. Player 2 has a fleet at hex H.
- [ ] `collect_sector_effects(system, H, empire_id=Player1.id)` — picks up the SensorBoost (allied scope, owner matches).
- [ ] `collect_sector_effects(system, H, empire_id=Player2.id)` — does NOT pick up the SensorBoost (allied scope, different owner).
- [ ] Confirm the existing PROJ-300 owner-filter logic in `_aggregate` handles this correctly.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
