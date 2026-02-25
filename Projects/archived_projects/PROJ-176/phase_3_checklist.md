# Phase 3: Simulation Abstractions (SimpleMultiplierAbility + SuperweaponMarker)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-176 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create SimpleMultiplierAbility base class and migrate 7 ability classes; create SuperweaponMarker base class and migrate 6 superweapon classes
**Priority:** Normal
**Estimated Time:** ~2-3 days
**Net Lines Saved:** ~82
**Dependencies:** None (independent of Phases 1-2, but ordered last due to higher risk)

> **EXTRA CARE REQUIRED:** This phase touches simulation-core code covered by 943 ability tests.
> - Never migrate more than 1 class without running the full test suite
> - Verify setattr/getattr correctness via `__init_subclass__` validation
> - Run `pytest simulation_tests/ -n 4` after each migration
> - Preserve external behavior exactly — same attribute names, same method signatures, same return values

---

## Tasks

### Task 3.1: Implement SimpleMultiplierAbility Base Class [Medium]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** NEW `tests/unit/simulation/components/abilities/test_simple_multiplier_ability.py`

- [x] Read `game/simulation/components/abilities/base.py` to understand current `Ability` class structure and `_parse_primary_value()` method
- [x] Add `SimpleMultiplierAbility(Ability)` class after the `Ability` class with:
  - Class attributes: `stat_key`, `value_attr`, `base_attr`, `ui_label`, `ui_format`, `ui_color`, `int_result`
  - `__init_subclass__` that validates required class attributes are non-empty
  - `__init__` that parses value and sets base/current attributes via setattr
  - `sync_data` that re-parses and sets base/current attributes
  - `recalculate` that applies `base * get_effective_stat(stat_key, 1.0)`
  - `get_ui_rows` that returns `[{'label': ui_label, 'value': ui_format.format(val), 'color_hint': ui_color}]`
  - `get_primary_value` that returns `float(getattr(self, value_attr))`
- [x] See `design.md` for complete API specification
- [x] Write unit tests in `tests/unit/simulation/components/abilities/test_simple_multiplier_ability.py`:
  - Create a minimal `TestAbility(SimpleMultiplierAbility)` with all required class attributes
  - `test_init_sets_base_and_value()` — verify both attributes set from data
  - `test_init_int_result()` — verify int casting when `int_result=True`
  - `test_recalculate_applies_multiplier()` — verify base * mult
  - `test_recalculate_int_result()` — verify int casting in recalculate
  - `test_sync_data_updates_base()` — verify sync resets base
  - `test_get_ui_rows_format()` — verify label, value format, color_hint
  - `test_get_primary_value()` — verify returns float of current value
  - `test_init_subclass_missing_stat_key_raises()` — verify TypeError
  - `test_init_subclass_missing_value_attr_raises()` — verify TypeError
- [x] Verify: `pytest tests/unit/simulation/components/abilities/test_simple_multiplier_ability.py -v` — all pass

**Notes:** 19 tests created, all passing. SimpleMultiplierAbility implemented with __init_subclass__ validation.

### Task 3.2: Migrate ShieldProjection to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/ -n 12`

- [x] Read `defense.py` to confirm `ShieldProjection` structure (lines ~9-31)
- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='capacity_mult'`, `value_attr='capacity'`, `base_attr='base_capacity'`, `ui_label='Shield Cap'`, `ui_format='{:.0f}'`, `ui_color=HINT_SHIELD_CAP`
- [x] Remove `__init__`, `recalculate`, `get_ui_rows`, `get_primary_value` methods (keep `STAT_BINDINGS`)
- [x] Verify: `pytest tests/ -n 12` — all pass
- [x] Verify: `pytest simulation_tests/ -n 4` — pre-existing failures only

**Notes:** Migration complete. Tests: 12178 passed.

### Task 3.3: Migrate ShieldRegeneration to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/ -n 12`

- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='energy_gen_mult'`, `value_attr='rate'`, `base_attr='base_rate'`, `ui_label='Regen'`, `ui_format='{:.1f}/s'`, `ui_color=HINT_SHIELD_REGEN`
- [x] Remove `__init__`, `recalculate`, `get_ui_rows`, `get_primary_value` methods
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete. ui_label is 'Regen' (not 'Shield Regen' as in checklist - matched existing code).

### Task 3.4: Migrate CombatPropulsion to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/ -n 12`

- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='thrust_mult'`, `value_attr='thrust_force'`, `base_attr='base_thrust'`, `ui_label='Thrust'`, `ui_format='{:.0f} N'`, `ui_color=HINT_THRUST`
- [x] Remove `__init__`, `sync_data`, `recalculate`, `get_ui_rows`, `get_primary_value` methods
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete.

### Task 3.5: Migrate ManeuveringThruster to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/ -n 12`

- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='turn_mult'`, `value_attr='turn_rate'`, `base_attr='base_turn_rate'`, `ui_label='Turn Speed'`, `ui_format='{:.1f} deg/s'`, `ui_color=HINT_TURN_SPEED`
- [x] Remove `__init__`, `sync_data`, `recalculate`, `get_ui_rows`, `get_primary_value` methods
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete.

### Task 3.6: Migrate StrategicMovement to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`
**Tests:** `pytest tests/ -n 12`

- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='strategic_mult'`, `value_attr='movement_points'`, `base_attr='base_movement_points'`, `ui_label='Strategic Mobility'`, `ui_format='{:.0f} MP'`, `ui_color=HINT_STRATEGIC_MOBILITY`
- [x] Remove `__init__`, `sync_data`, `recalculate`, `get_ui_rows`, `get_primary_value` methods
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete. Preserved layer/allowed_scopes/default_scope overrides.

### Task 3.7: Migrate CrewCapacity to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/ -n 12`

- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='crew_capacity_mult'`, `value_attr='amount'`, `base_attr='_base_amount'`, `ui_label='Crew Cap'`, `ui_format='{}'`, `ui_color=HINT_CREW_CAP`, `int_result=True`
- [x] Remove `__init__`, `recalculate`, `get_ui_rows`, `get_primary_value` methods
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete. int_result=True for integer crew counts.

### Task 3.8: Migrate LifeSupportCapacity to SimpleMultiplierAbility [Simple]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/ -n 12`

- [x] Change base class from `Ability` to `SimpleMultiplierAbility`
- [x] Add class attributes: `stat_key='life_support_capacity_mult'`, `value_attr='amount'`, `base_attr='_base_amount'`, `ui_label='Life Support'`, `ui_format='{}'`, `ui_color=HINT_LIFE_SUPPORT`, `int_result=True`
- [x] Remove `__init__`, `recalculate`, `get_ui_rows`, `get_primary_value` methods
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete.

### Task 3.9: Create SuperweaponMarker Base Class [Simple]
**File:** `game/simulation/components/abilities/superweapons.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/ -n 4` + `pytest tests/ -k superweapon -n 4`

- [x] Read `game/simulation/components/abilities/superweapons.py` to confirm all 6 classes are structurally identical
- [x] Add `SuperweaponMarker(Ability)` class at top of file with:
  - `layer = AbilityLayer.STRATEGIC`
  - `allowed_scopes = [AbilityScope.SELF]`
  - `default_scope = AbilityScope.SELF`
  - `STAT_BINDINGS = []`
  - `weapon_name: str = ''` class attribute
  - `get_ui_rows()` returning `[{'label': 'Superweapon', 'value': self.weapon_name, 'color_hint': HINT_SUPERWEAPON}]`
  - `get_primary_value()` returning `0.0`
- [x] Replace all 6 classes with 2-line subclasses:
  - `class DestroyPlanet(SuperweaponMarker): weapon_name = 'Planet Imploder'`
  - `class DestroyStar(SuperweaponMarker): weapon_name = 'Stellerator'`
  - `class OpenWarpPoint(SuperweaponMarker): weapon_name = 'Warp Point Creator'`
  - `class CloseWarpPoint(SuperweaponMarker): weapon_name = 'Warp Point Closer'`
  - `class CreateDysonSphere(SuperweaponMarker): weapon_name = 'Dyson Sphere Constructor'`
  - `class SelfDestruct(SuperweaponMarker): weapon_name = 'Self-Destruct Device'`
- [x] Verify class names unchanged (ABILITY_REGISTRY maps to class names)
- [x] Verify: `pytest tests/ -k superweapon -n 4` — 276 passed
- [x] Verify: `pytest tests/ -n 12` — all pass

**Notes:** Migration complete. ~100 lines reduced to ~55 lines. File now 110 lines vs original 197 lines.

### Task 3.10: Phase 3 Full Verification [Simple]
**Tests:** `pytest tests/ -n 12` + `pytest simulation_tests/ -n 4`

- [x] Run full test suite: `pytest tests/ -n 12` — 12178 passed, 1 skipped
- [x] Run simulation tests: `pytest simulation_tests/ -n 4` — 55 pre-existing failures (seeker weapon tests)
- [x] Verify all 7 migrated abilities inherit from `SimpleMultiplierAbility` (grep check)
- [x] Verify all 6 superweapons inherit from `SuperweaponMarker` (grep check)
- [x] Verify no migrated class still has inline `recalculate()` or `get_ui_rows()` (grep check)
- [x] Record test count — 12178 passed (+19 new SimpleMultiplierAbility tests)

**Notes:** simulation_tests failures are pre-existing (confirmed by stash test). All Phase 3 objectives met.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
