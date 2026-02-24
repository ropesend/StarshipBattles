# PROJ-178: PROJ-171 Audit Remediation - Validation Consistency

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-178` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-178 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. ShipInstance Validation & Docstrings | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. PlanetaryFacility & SpeciesPopulation from_dict | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. DesignMetadata Ship Calculation Fix | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Ghost Code Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 4 - Ghost Code Cleanup
**Last Action:** Phase 3 complete - fixed _calculate_combat_power_from_ship to use major_classification/WeaponAbility, removed old layer format warnings
**Next Action:** Begin Phase 4 (remove ghost comment in galaxy.py, final verification)
**Blockers:** None
**Baseline:** 12358 passed, 1 skipped (+2 tests from Phase 3)
**Context for Next Agent:** Phase 3 was a bug fix. _calculate_combat_power_from_ship now correctly identifies weapons via major_classification=='Weapons' and extracts damage/reload from WeaponAbility instances. Old layer format warnings removed per CLAUDE.md policy.

## Overview
Remediate all findings from the PROJ-171 post-refactor audit. This project addresses validation gaps, missing docstrings, inline deserialization inconsistencies, a broken combat power calculation path, and ghost code. All changes follow established `validation_helpers.py` patterns.

## Goals
- Complete validation consistency across all `from_dict` methods (match Planet's thoroughness)
- Add `Raises: PersistenceException` docstrings to Empire, Fleet, and ShipInstance
- Extract `PlanetaryFacility.from_dict` and `SpeciesPopulation.from_dict` to use `require_keys`
- Fix broken `_calculate_combat_power_from_ship` / `_calculate_resource_cost_from_ship` (uses nonexistent `category` attribute)
- Remove ghost comment in galaxy.py and legacy "old layer format" warnings in design_metadata.py

## Scope
**In:**
- `ShipInstance.from_dict` — add `validate_non_negative` for numeric fields + docstring
- `Empire.from_dict` — add `Raises:` docstring block
- `Fleet.from_dict` — add `Raises:` docstring block
- `PlanetaryFacility` — extract `from_dict` method using `require_keys`
- `SpeciesPopulation` — extract `from_dict` method using `require_keys`
- `DesignMetadata._calculate_combat_power_from_ship` — fix to use `type_str`/`major_classification` instead of nonexistent `category`
- `DesignMetadata._calculate_resource_cost_from_ship` — remove unnecessary `hasattr(comp, 'cost')` (Component always has `.cost`)
- `DesignMetadata._calculate_combat_power` / `_calculate_resource_cost` (dict-based) — remove "Old layer format" warnings
- `galaxy.py` line 28 — remove ghost comment

**Out:**
- `RaceConfig.from_dict` — has no validation helpers but has extensive separate `validate()` method; out of scope
- New test infrastructure or test framework changes
- Any changes to the dict-based `_calculate_combat_power` / `_calculate_resource_cost` logic beyond removing old-format warnings

## Key Files
| Component | File Path |
|-----------|-----------|
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Empire | `game/strategy/data/empire.py` |
| Fleet | `game/strategy/data/fleet.py` |
| Planet (facilities/pops) | `game/strategy/data/planet.py` |
| DesignMetadata | `game/strategy/data/design_metadata.py` |
| Galaxy (ghost comment) | `game/strategy/data/galaxy.py` |
| Validation helpers | `game/core/validation_helpers.py` |
| Component (reference) | `game/simulation/components/component.py` |
| ShipInstance tests | `tests/unit/strategy/ship_instance/test_validation.py` |
| Planet tests | `tests/unit/strategy/planet/test_planet_validation.py` |
| Empire tests | `tests/unit/strategy/empire/test_empire_validation.py` |
| Fleet tests | `tests/unit/strategy/fleet/test_fleet_validation.py` |
| DesignMetadata tests | `tests/unit/strategy/test_design_metadata.py` |
| DesignMetadata validation tests | `tests/unit/strategy/data/test_design_metadata_validation.py` |
| Facility resource tests | `tests/unit/strategy/data/test_facility_resource_tracking.py` |
| Facility queue tests | `tests/unit/strategy/data/test_facility_construction_queue.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: ShipInstance Validation & Docstrings [Simple]
**Objective:** Add `validate_non_negative` to ShipInstance.from_dict and add missing `Raises:` docstring blocks to ShipInstance, Empire, and Fleet.
**Status:** Not Started

#### Task 1.1: Add validate_non_negative to ShipInstance.from_dict [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`
- [ ] Add `validate_non_negative` to import at line 21 (currently only imports `require_keys`)
- [ ] After `require_keys` call (line 644), add validation for numeric fields:
  ```python
  # Validate non-negative numeric fields (if present in data)
  if data.get('current_hp') is not None:
      validate_non_negative(data['current_hp'], 'current_hp', 'ShipInstance')
  if data.get('experience') is not None:
      validate_non_negative(data['experience'], 'experience', 'ShipInstance')
  if data.get('kills') is not None:
      validate_non_negative(data['kills'], 'kills', 'ShipInstance')
  if data.get('battles_survived') is not None:
      validate_non_negative(data['battles_survived'], 'battles_survived', 'ShipInstance')
  ```
- [ ] Verify existing tests still pass
**Notes:**

#### Task 1.2: Add tests for ShipInstance non-negative validation [Simple]
**File:** `tests/unit/strategy/ship_instance/test_validation.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_validation.py`
- [ ] Add parametrized test for negative values raising PersistenceException:
  - Fields to test: `current_hp`, `experience`, `kills`, `battles_survived`
  - Each with value `-1` should raise PersistenceException
- [ ] Add test that zero values are accepted (boundary check)
- [ ] Run tests — new tests should pass
**Notes:**

#### Task 1.3: Add Raises docstring to ShipInstance.from_dict [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** N/A (documentation only)
- [ ] Replace one-liner docstring at line 643 with full docstring:
  ```python
  """
  Deserialize from save game.

  Args:
      data: Dict with ship instance data

  Returns:
      Reconstructed ShipInstance

  Raises:
      PersistenceException: If required keys missing or values invalid
  """
  ```
**Notes:**

#### Task 1.4: Add Raises docstring to Empire.from_dict [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** N/A (documentation only)
- [ ] Add `Raises: PersistenceException: If required keys missing` to existing docstring at lines 175-184 (between Returns and closing `"""`)
**Notes:**

#### Task 1.5: Add Raises docstring to Fleet.from_dict [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** N/A (documentation only)
- [ ] Replace one-liner docstring at line 349 with full docstring including Raises block
**Notes:**

---

### Phase 2: PlanetaryFacility & SpeciesPopulation from_dict [Medium]
**Objective:** Extract inline deserialization into proper `from_dict` classmethods using `require_keys`, matching the codebase pattern.
**Status:** Not Started

#### Task 2.1: Add PlanetaryFacility.from_dict classmethod [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py tests/unit/strategy/data/test_facility_resource_tracking.py tests/unit/strategy/data/test_facility_construction_queue.py`
- [ ] Add `from_dict` classmethod to `PlanetaryFacility` class (after line 41):
  ```python
  @classmethod
  def from_dict(cls, data: dict) -> 'PlanetaryFacility':
      """
      Deserialize facility from dict.

      Args:
          data: Dict with facility data

      Returns:
          Reconstructed PlanetaryFacility

      Raises:
          PersistenceException: If required keys missing
      """
      require_keys(data, ['instance_id', 'design_id', 'name', 'design_data'], 'PlanetaryFacility')
      return cls(
          instance_id=data['instance_id'],
          design_id=data['design_id'],
          name=data['name'],
          design_data=data['design_data'],
          is_operational=data.get('is_operational', True),
          construction_queue=data.get('construction_queue', []),
          resource_levels=data.get('resource_levels', {})
      )
  ```
- [ ] Update Planet.from_dict facilities loop (lines 418-436) to call `PlanetaryFacility.from_dict(f)` instead of inline construction
- [ ] Update exception catching to include `PersistenceException`: `except (PersistenceException, KeyError, TypeError) as e:`
- [ ] Verify all existing facility tests still pass
**Notes:**

#### Task 2.2: Add SpeciesPopulation.from_dict classmethod [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/planet/test_planet_validation.py tests/unit/strategy/data/test_population_model.py`
- [ ] Find SpeciesPopulation dataclass definition and add `from_dict` classmethod:
  ```python
  @classmethod
  def from_dict(cls, data: dict) -> 'SpeciesPopulation':
      """
      Deserialize population from dict.

      Args:
          data: Dict with population data

      Returns:
          Reconstructed SpeciesPopulation

      Raises:
          PersistenceException: If required keys missing
      """
      require_keys(data, ['race_id', 'count'], 'SpeciesPopulation')
      return cls(
          race_id=data['race_id'],
          count=data['count'],
          happiness=data.get('happiness', 0.5)
      )
  ```
- [ ] Update Planet.from_dict populations loop (lines 438-452) to call `SpeciesPopulation.from_dict(p)` instead of inline construction
- [ ] Update exception catching to include `PersistenceException`: `except (PersistenceException, KeyError, TypeError) as e:`
- [ ] Verify all existing population tests still pass
**Notes:**

#### Task 2.3: Add tests for PlanetaryFacility.from_dict validation [Simple]
**File:** `tests/unit/strategy/planet/test_planet_validation.py` (or new file if cleaner)
**Tests:** `pytest tests/unit/strategy/planet/`
- [ ] Test that valid data creates a PlanetaryFacility
- [ ] Test that missing required key (instance_id, design_id, name, design_data) raises PersistenceException
- [ ] Test that optional fields default correctly (is_operational=True, construction_queue=[], resource_levels={})
**Notes:**

#### Task 2.4: Add tests for SpeciesPopulation.from_dict validation [Simple]
**File:** `tests/unit/strategy/planet/test_planet_validation.py` (or new file if cleaner)
**Tests:** `pytest tests/unit/strategy/planet/`
- [ ] Test that valid data creates a SpeciesPopulation
- [ ] Test that missing required key (race_id, count) raises PersistenceException
- [ ] Test that happiness defaults to 0.5
**Notes:**

---

### Phase 3: DesignMetadata Ship Calculation Fix [Medium]
**Objective:** Fix the broken `_calculate_combat_power_from_ship` and `_calculate_resource_cost_from_ship` methods that reference nonexistent `category` attribute, and remove legacy "old layer format" warnings from dict-based methods.
**Status:** Not Started

#### Task 3.1: Fix _calculate_combat_power_from_ship [Medium]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [ ] Replace `hasattr(comp, 'category') and comp.category == 'weapon'` (line 207) with `comp.type_str in ('beam_weapon', 'projectile_weapon', 'missile_weapon')` or `comp.major_classification == 'Weapons'` (verify which values exist in components.json first)
- [ ] Replace `hasattr(comp, 'category') and comp.category == 'armor'` (line 211) with corresponding check using `type_str` or `major_classification == 'Armor'`
- [ ] Replace `getattr(comp, 'damage', 0)` (line 208) with direct access or proper attribute (verify Component has `damage` for weapons)
- [ ] Replace `getattr(comp, 'rate_of_fire', 0)` (line 209) similarly
- [ ] Replace `getattr(comp, 'hp', 0)` (line 212) — Component has `max_hp` (line 115 of component.py), not `hp`
- [ ] Update/fix existing tests in `TestDesignMetadataCombatPowerFromShip` to use correct mock attributes
**Notes:** This is a BUG FIX. The current code always returns 0.0 because Component has no `category` attribute. Components use `type_str` (e.g., "beam_weapon") and `major_classification` (e.g., "Weapons"). Check components.json for exact values.

#### Task 3.2: Fix _calculate_resource_cost_from_ship [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [ ] Remove `hasattr(comp, 'cost')` guard (line 245) — Component always has `.cost` (defaults to 0, line 129 of component.py)
- [ ] Simplify to directly access `comp.cost`
- [ ] Verify existing tests pass
**Notes:**

#### Task 3.3: Remove "Old layer format" warnings from dict-based methods [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [ ] In `_calculate_combat_power` (line 183-185): Remove the `else` branch that logs "Old layer format" warning, just use `components = []` for non-list data or remove the isinstance check entirely if old format is impossible
- [ ] In `_calculate_resource_cost` (line 227-229): Same — remove the `else` branch with warning
- [ ] Verify existing tests pass
**Notes:** Per CLAUDE.md System Migration Policy: old formats should be eradicated, not handled gracefully.

#### Task 3.4: Update DesignMetadata tests for fixed calculations [Medium]
**File:** `tests/unit/strategy/test_design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [ ] Update `TestDesignMetadataCombatPowerFromShip` mocks to use correct Component attributes (`type_str`/`major_classification` instead of `category`)
- [ ] Verify `test_calculate_combat_power_from_ship_weapon` now correctly calculates non-zero power
- [ ] Verify `test_calculate_combat_power_from_ship_armor` now correctly calculates non-zero power
- [ ] Add test that components without weapon/armor classification contribute 0 power
- [ ] Update resource cost tests if needed for `hasattr` removal
**Notes:**

---

### Phase 4: Ghost Code Cleanup [Simple]
**Objective:** Remove obsolete comment and do final verification.
**Status:** Not Started

#### Task 4.1: Remove ghost comment in galaxy.py [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/galaxy/`
- [ ] Delete line 28: `# Planet and PlanetType moved to game.strategy.data.planet`
- [ ] Verify tests pass
**Notes:**

#### Task 4.2: Final full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] Verify baseline maintained: 12338+ passed, 0 failures
- [ ] Document final pass count
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 12338 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] No new warnings introduced

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] All 4 phase checklists complete
- [ ] Commit with clear message

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 0 (PROJ-171 audit) | 2026-02-24 | 5 findings + 1 new (broken category attribute) | This project |

## Completion Checklist
- [ ] Phase 1 complete (ShipInstance validation + docstrings)
- [ ] Phase 2 complete (Facility/Population from_dict extraction)
- [ ] Phase 3 complete (DesignMetadata calculation fix)
- [ ] Phase 4 complete (Ghost code cleanup + final verification)
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
