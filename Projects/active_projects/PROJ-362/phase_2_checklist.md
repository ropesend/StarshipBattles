# Phase 2: EffectAbilityMetadata registry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-362 2`
> 2. Only proceed if PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Introduce `EffectAbilityMetadata` registry that replaces `SYSTEM_EFFECT_ABILITIES`, `_RATE_ABILITIES`, `_OWNER_AWARE_SCOPES`, and the special-case branches in `make_group_key` / `make_display_name`. The collector continues to behave identically; the registry is the new source of truth.

---

## Tasks

### Task 2.1: Define dataclass + registry [Medium]
**File:** `game/strategy/services/effect_ability_metadata.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_effect_ability_metadata.py -v`

- [ ] Module docstring referencing PROJ-362 Phase 2 and the stabilizer_registry pattern (`stabilizer_registry.py:54-70`).
- [ ] Define `EffectAbilityMetadata` (frozen dataclass) with fields per design.md:
  ```python
  @dataclass(frozen=True)
  class EffectAbilityMetadata:
      ability_name: str
      display_name: str | None
      kind: Literal['rate', 'multiplier']
      is_activatable: bool
      grouping_key_field: str | None
      owner_aware_scopes: frozenset[str]
      value_field_primary: str
      value_field_fallback: str
  ```
- [ ] Define `EFFECT_ABILITY_METADATA: tuple[EffectAbilityMetadata, ...]` populated with the 12 abilities currently in `SYSTEM_EFFECT_ABILITIES`. For each:
  - GeologicStabilizer / StellarStabilizer / WarpFieldStabilizer: kind=multiplier, is_activatable=True, grouping_key_field=None
  - ResourceHarvestBooster: display_name=None (derived), kind=multiplier, grouping_key_field='resource_type'
  - QualityImprovement: display_name="Quality Enrichment", kind=multiplier, grouping_key_field='resource_type'
  - BuildRateBooster: display_name="Construction Acceleration", kind=multiplier
  - ShieldModifier / DamageModifier / ThrustModifier / StrategicSpeedModifier: kind=multiplier
  - EnvironmentalDamage: kind=rate, grouping_key_field='damage_type', value_field_primary='rate'
  - FuelDrain: kind=rate, value_field_primary='rate'
- [ ] Add owner_aware_scopes for all entries: the same set as `_OWNER_AWARE_SCOPES` (ownership-aware scopes apply to any ability that declares them).
- [ ] Define lookup helpers:
  - `find_metadata(ability_name: str) -> EffectAbilityMetadata | None`
  - `is_known_effect_ability(ability_name: str) -> bool`
- [ ] Add registry contract test: `test_metadata_for_each_legacy_ability_name` parametrized over the 12 names from `SYSTEM_EFFECT_ABILITIES`, asserting `find_metadata(name) is not None`.

**Notes:** _(filled during implementation)_

### Task 2.2: Wire metadata registry into collector helpers [Medium]
**File:** `game/strategy/services/system_effects_collector.py`
**Tests:** `pytest tests/unit/strategy/services/test_system_effects_collector*.py -v`

- [ ] Replace `_ability_kind(ability_name)` body with metadata lookup; preserve signature for any existing callers.
- [ ] Replace `make_group_key`'s ResourceHarvestBooster / QualityImprovement / EnvironmentalDamage branches with: `metadata.grouping_key_field` lookup. If `grouping_key_field is None`, return `ability_name`.
- [ ] Replace `make_display_name` similarly: if `metadata.display_name is not None`, return it; else derive from `metadata.grouping_key_field` value in `ability_data`.
- [ ] Replace the `if ability_name not in SYSTEM_EFFECT_ABILITIES` filter at line 200 and line 323 with `if not is_known_effect_ability(ability_name)`.
- [ ] Replace the value extraction at line 364-367 with: read `metadata.value_field_primary` from entry, fall back to `metadata.value_field_fallback`, then to default 0.0/1.0 per kind.
- [ ] Replace `_OWNER_AWARE_SCOPES` lookup at line 336 with metadata-driven check (use the union of all entries' `owner_aware_scopes` for the global filter, or per-ability check if more precision is wanted).
- [ ] Run characterization tests from Phase 1: all still green.
- [ ] Run existing `test_system_effects_collector.py`: all still green.
- [ ] Verify: no remaining references to `SYSTEM_EFFECT_ABILITIES`, `_RATE_ABILITIES`, `_OWNER_AWARE_SCOPES` inside the collector module.

**Notes:** _(filled during implementation)_

### Task 2.3: Deprecate or delete the legacy module-level constants [Simple]
**File:** `game/strategy/services/system_effects_collector.py`

- [ ] Confirm no external code imports `SYSTEM_EFFECT_ABILITIES`, `_RATE_ABILITIES`, `_OWNER_AWARE_SCOPES` (per findings/02 — none do).
- [ ] Delete the three constants + their docstrings (lines 62-90).
- [ ] Run full focused suite: `pytest tests/unit/strategy/services/ tests/unit/strategy/engine/ -v`. Green.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] EffectAbilityMetadata registry exists and is unit-tested
- [ ] Collector no longer references the three deleted constants
- [ ] Phase 1 characterization tests still green
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State to point to Phase 3
