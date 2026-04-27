# Phase 4: Refactor `system_effects_collector` onto the iterator

**Status:** Not Started
**Objective:** Replace the planet-walking logic in `_collect_effects` with iterator-based source enumeration. Existing tests should stay green — this is a behavior-preserving refactor.

---

## Tasks

### Task 4.1: Refactor `_collect_effects` to consume `IAbilitySource` [Medium]
**File:** `game/strategy/services/system_effects_collector.py`
**Tests:** `pytest tests/unit/strategy/services/test_system_effects_collector.py`

- [ ] Read current `collect_sector_effects` (lines 131-163) and `_collect_effects` (lines 166-287).
- [ ] Replace planet-walking outer loop in `_collect_effects` with an iterator-driven `_aggregate(sources, allowed_scopes, empire_id, registries, hex_coord)`:
  ```python
  def _aggregate(sources, allowed_scopes, empire_id, registries, hex_coord):
      raw_providers = {}
      for source in sources:
          if hex_coord is not None and not source.affects_hex(hex_coord):
              continue
          # Owner filter: ownerless sources apply universally; owned sources
          # only contribute to the matching empire-scoped query.
          if source.owner_id is not None and empire_id is not None and source.owner_id != empire_id:
              continue
          for ability_name, ability_data in source.get_abilities().items():
              ... (existing per-ability loop, but provider record uses source.source_kind/source_label/source_id) ...
      return _build_effect_results(raw_providers)
  ```
- [ ] `collect_sector_effects` becomes a 3-line wrapper calling `iter_ability_sources_at_hex(...)` then `_aggregate(..., _SECTOR_SCOPES, ...)`.
- [ ] `collect_system_effects` becomes a wrapper calling `iter_ability_sources_in_system(...)` then `_aggregate(..., _SYSTEM_SCOPES, ...)`.

**Notes:**

### Task 4.2: Update provider entry shape [Medium]
**File:** `game/strategy/services/system_effects_collector.py`
**Tests:** Same as 4.1.

- [ ] Replace legacy provider fields (`planet_name`, `planet_id`, `facility_name`, `facility_id`, `component_key`) with universal:
  ```python
  provider = {
      'source_kind': source.source_kind,
      'source_label': source.source_label,
      'source_id': source.source_id,
      'owner_id': source.owner_id,
      'status': status,
      'is_active': is_active,
      'value': value,
      'ability_data': entry,
  }
  ```
- [ ] Update tests in `test_system_effects_collector.py` to read `provider['source_label']` etc. (Existing tests verifying `provider['planet_name']` need rewriting.)
- [ ] Run all collector tests — green.

**Notes:** UI consumers in `system_tree_panel.py` will be updated in Phase 8. Until then, the panel may render bare labels — acceptable temporary state since collector tests pass.

### Task 4.3: Add `kind` discriminator + dispatch to right aggregator [Medium]
**File:** `game/strategy/services/system_effects_collector.py`

- [ ] In `_build_effect_results`, determine `kind` per group: if any provider's `ability_data` has `multiplier`, `kind='multiplier'`; if any has `rate`, `kind='rate'`; mixed = `ValidationException`.
- [ ] Dispatch to `aggregate_multipliers` (default 1.0) or `aggregate_rates` (default 0.0) based on `kind`.
- [ ] Add `kind` and `damage_type` fields to the returned effect dict.
- [ ] Add tests:
  - [ ] `test_multiplier_effect_has_kind_multiplier`
  - [ ] `test_rate_effect_has_kind_rate_with_default_zero`
  - [ ] `test_environmental_damage_carries_damage_type`

**Notes:**

### Task 4.4: Add `find_sector_effect` and `aggregate_value_or` helpers [Simple]
**File:** `game/strategy/services/system_effects_collector.py`

- [ ] Add tests:
  - [ ] `test_find_sector_effect_returns_match`
  - [ ] `test_find_sector_effect_returns_none_when_absent`
  - [ ] `test_find_sector_effect_with_filter_by_damage_type`
  - [ ] `test_aggregate_value_or_returns_aggregate_when_present`
  - [ ] `test_aggregate_value_or_returns_default_when_absent`
- [ ] Implement:
  ```python
  def find_sector_effect(effects, ability_name, **filters):
      for e in effects:
          if e['ability_name'] != ability_name:
              continue
          if all(e.get(k) == v for k, v in filters.items()):
              return e
      return None

  def aggregate_value_or(effects, ability_name, default, **filters):
      e = find_sector_effect(effects, ability_name, **filters)
      return e['aggregate_value'] if e else default
  ```

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] All `test_system_effects_collector.py` tests green (existing + new)
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status to `Complete`
- [ ] Update plan.md
