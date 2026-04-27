# Phase 2: Register four new ability names

**Status:** Complete (2026-04-27)
**Objective:** Add `ThrustModifier`, `StrategicSpeedModifier`, `EnvironmentalDamage`, `FuelDrain` to the recognized ability registries so the collector and combat path treat them as first-class. Pure additive change — no behavior change yet.

---

## Tasks

### Task 2.1: Extend `SYSTEM_EFFECT_ABILITIES` [Simple]
**File:** `game/strategy/services/system_effects_collector.py`
**Tests:** `pytest tests/unit/strategy/services/test_system_effects_collector.py`

- [ ] Add to the `SYSTEM_EFFECT_ABILITIES` dict (currently at lines 39-48):
  ```python
  'ThrustModifier': 'Thrust Modifier',
  'StrategicSpeedModifier': 'Strategic Speed Modifier',
  'EnvironmentalDamage': None,  # Display name derived from damage_type
  'FuelDrain': 'Fuel Drain',
  ```
- [ ] Update `_make_display_name` (around lines 98-106) to handle `EnvironmentalDamage`:
  ```python
  if ability_name == 'EnvironmentalDamage' and isinstance(ability_data, dict):
      damage_type = ability_data.get('damage_type', 'environmental')
      return f"{damage_type.capitalize()} Damage"
  ```
- [ ] Update `_make_group_key` (around lines 82-95) to group `EnvironmentalDamage` per `damage_type`:
  ```python
  if ability_name == 'EnvironmentalDamage' and isinstance(ability_data, dict):
      damage_type = ability_data.get('damage_type', 'environmental')
      return f"{ability_name}:{damage_type}"
  ```

**Notes:**

### Task 2.2: Register `ThrustModifier` in `ABILITY_STAT_REGISTRY` [Simple]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py`

- [ ] Read the existing registry file to confirm format (existing entries: `ShieldModifier`, `DamageModifier`, `ShieldProjection`).
- [ ] Add a `ThrustModifier` entry binding to `stat_key="thrust_mult"`. Use the same shape as `ShieldModifier` (`shield_capacity_mult`).
- [ ] Add a test verifying `ThrustModifier` is in the registry and emits the expected stat key.
- [ ] **Note:** Combat consumption of `thrust_mult` is OUT OF SCOPE for PROJ-300. The stat is registered so storm data flows through `_entries_from_sector_effects` (Phase 6c) without raising; downstream consumption is a separate follow-up.

**Notes:**

### Task 2.3: Add tests for collector recognition [Simple]
**File:** `tests/unit/strategy/services/test_system_effects_collector.py`

- [ ] Add a fixture creating a facility design with a component that declares one of the four new abilities (e.g. a `ThrustModifier scope: sector` ability).
- [ ] Test: `collect_sector_effects` returns an effect with `ability_name='ThrustModifier'`, correct `display_name`, correct provider info.
- [ ] Test for `EnvironmentalDamage` with `damage_type: plasma` — confirm `group_key = 'EnvironmentalDamage:plasma'` and display name is `"Plasma Damage"`.
- [ ] Run tests — confirm green.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md
