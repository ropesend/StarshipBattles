# Phase 2: Template Refactor & Projectile Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Refactor `StaticTargetScenario.verify()` to support result collection hooks, then migrate projectile scenarios from raw `TestScenario` to `StaticTargetScenario`.

**Prerequisite:** Phase 1 complete

---

## Tasks

### Task 2.1: Refactor `StaticTargetScenario.verify()` [Medium]
**File:** `simulation_tests/scenarios/templates.py`
**Tests:** `pytest simulation_tests/ -v`

The current `verify()` at lines 168-222 combines result collection with pass/fail logic. Subclasses that override `verify()` lose all standard result collection. Split into two parts.

- [x] Create `_collect_results(self, battle_engine)` method that extracts the result-storage portion of `verify()`:
  ```python
  def _collect_results(self, battle_engine):
      """Collect standard results. Always called, even if verify() is overridden."""
      self.damage_dealt = self.initial_hp - self.target.hp
      self.results['initial_hp'] = self.initial_hp
      self.results['final_hp'] = self.target.hp
      self.results['damage_dealt'] = self.damage_dealt
      self.results['ticks_run'] = battle_engine.tick_counter
      self.results['target_alive'] = self.target.is_alive
      if battle_engine.tick_counter > 0 and self.damage_dealt > 0:
          self.results['hit_rate'] = self.damage_dealt / battle_engine.tick_counter
      for key in self.custom_result_keys:
          if hasattr(self, key):
              self.results[key] = getattr(self, key)
      # Hook for subclasses to add extra results
      if hasattr(self, '_collect_extra_results'):
          self._collect_extra_results(battle_engine)
      # Run validation rules
      if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
          self.run_validation(battle_engine)
  ```
- [x] Update `verify()` to call `_collect_results()` first, then apply pass criteria:
  ```python
  def verify(self, battle_engine) -> bool:
      if self.skip_test:
          self.results['skipped'] = True
          self.results['skip_reason'] = self.skip_reason
          return False
      self._collect_results(battle_engine)
      # Pass criteria precedence (highest to lowest):
      # 1. measurement_mode - always passes if simulation completed
      # 2. expect_no_damage - passes if zero damage
      # 3. min_damage_threshold - passes if damage >= threshold
      # 4. verify_damage_dealt - passes if any damage dealt
      # 5. NotImplementedError - subclass must override
      if self.measurement_mode:
          return battle_engine.tick_counter > 0
      elif self.expect_no_damage:
          return self.damage_dealt == 0
      elif self.min_damage_threshold > 0:
          return self.damage_dealt >= self.min_damage_threshold
      elif self.verify_damage_dealt:
          return self.damage_dealt > 0
      else:
          raise NotImplementedError(...)
  ```
- [x] Document pass criteria precedence in a docstring/comment on `verify()` (Issue 5)
- [x] Verify: Run `pytest simulation_tests/ -v` - all existing tests pass unchanged

**Notes:** Subclasses that currently override `verify()` will still work - they just won't benefit from `_collect_results()` yet. Phases 3 will update them.

---

### Task 2.2: Migrate Projectile Scenarios to `StaticTargetScenario` [Complex]
**File:** `simulation_tests/scenarios/projectile_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

All 9 projectile scenarios extend raw `TestScenario`. They need to extend `StaticTargetScenario` and use its setup/update/verify machinery.

**Strategy:** Migrate one scenario at a time. After each, run tests to verify identical behavior.

- [x] Study first projectile scenario (`ProjectileStationaryTargetScenario`) - note its setup, update, verify logic
- [x] Compare with `StaticTargetScenario` template - identify what's identical vs. unique
- [x] Migrate `ProjectileStationaryTargetScenario`:
  - Change base class to `StaticTargetScenario`
  - Set class attributes: `attacker_ship`, `target_ship`, `distance`
  - Remove manual `setup()` - rely on template (or use `custom_setup` for unique parts)
  - Remove manual `update()` - rely on template `force_fire=True`
  - Simplify `verify()` - use template flags or call `_collect_results()`
  - Ensure test ID and pass/fail behavior unchanged
- [x] Verify: `pytest simulation_tests/ -v` - ProjectileStationaryTargetScenario passes
- [x] Migrate remaining 8 projectile scenarios one at a time:
  - [x] `ProjectileLinearSlowTargetScenario` (was listed as ProjectileLongRangeScenario)
  - [x] `ProjectileLinearFastTargetScenario` (was listed as ProjectileOutOfRangeScenario)
  - [x] `ProjectileErraticSmallTargetScenario` (was listed as ProjectileHighDamageScenario)
  - [x] `ProjectileErraticLargeTargetScenario` (was listed as ProjectileMultiShotScenario)
  - [x] `ProjectileOutOfRangeScenario` (was listed as ProjectileSpeedVariationScenario)
  - [x] `ProjectileDamageCloseRangeScenario` (was listed as ProjectileDamageAccumulationScenario)
  - [x] `ProjectileDamageMidRangeScenario` (was listed as ProjectileDestructionScenario)
  - [x] `ProjectileDamageLongRangeScenario` (was listed as ProjectileMaxRangeScenario)
- [x] Verify after each migration: `pytest simulation_tests/ -v`
- [x] Remove helper functions in projectile_scenarios.py that are no longer needed (`calculate_ticks_needed` removed; `calculate_projectile_travel_time` still used by 4 scenarios)
- [x] Update `simulation_tests/scenarios/__init__.py` exports if class names changed (they didn't)

**Notes:** The key constraint is that test IDs and pass/fail must be identical. This is a refactor.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest simulation_tests/ -v` passes
- [x] `pytest tests/ -n 4` passes (full suite)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
