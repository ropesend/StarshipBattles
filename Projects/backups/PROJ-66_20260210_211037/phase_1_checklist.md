# Phase 1: Data Layer - RaceConfig Enhancement [Medium]

**Objective:** Add all new fields to RaceConfig with serialization, defaults, and validation
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v`

---

## Task 1.1: Add Constant Lists [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "constant"`

- [x] Add `GOVERNMENT_TYPES` list constant (14 items: Empire, Hegemony, Alliance, etc.)
- [x] Add `GOVERNMENT_ORGANIZATIONS` list constant (13 items: Anarchy, Democracy, etc.)
- [x] Add `LEADER_TITLES` list constant (27 items: Central Speaker, Chairman, etc.)
- [x] Add `PHYSICAL_TYPES` list constant (14 items: Felinoid, Caninoid, etc.)
- [x] Add `SOCIETY_TYPES` list constant (17 items: Artisans, Berserkers, etc.)
- [x] Add `APTITUDE_NAMES` list constant (9 items: strength, intelligence, constitution, dexterity, tolerance_other_species, cooperation, happiness, population_growth, conflict_tolerance)
- [x] Write test: `test_government_types_list_has_14_items`
- [x] Write test: `test_government_organizations_list_has_13_items`
- [x] Write test: `test_leader_titles_list_has_27_items`
- [x] Write test: `test_physical_types_list_has_14_items`
- [x] Write test: `test_society_types_list_has_17_items`
- [x] Write test: `test_aptitude_names_list_has_9_items`
- [x] Run tests: all pass
**Notes:** All 6 constant list tests pass.

---

## Task 1.2: Add Identity Fields to RaceConfig [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "identity"`

- [x] Add field `faction_name: str = ""` (auto-generated from race name + government type)
- [x] Add field `race_name: str = ""` (species name, e.g., "Rossarians")
- [x] Add field `race_name_plural: str = ""` (e.g., "Rossarians")
- [x] Add field `government_type: str = ""` (from GOVERNMENT_TYPES)
- [x] Add field `government_organization: str = ""` (from GOVERNMENT_ORGANIZATIONS)
- [x] Add field `leader_title: str = ""` (from LEADER_TITLES)
- [x] Add field `physical_type: str = ""` (from PHYSICAL_TYPES)
- [x] Add field `society_type: str = ""` (from SOCIETY_TYPES)
- [x] Write test: `test_create_race_with_identity_fields` - verify all defaults
- [x] Write test: `test_create_race_with_custom_identity` - set all fields, verify stored
- [x] Run tests: all pass
**Notes:** The existing `name` field continues to function as the display name / faction_name for backward compatibility. New `race_name` is the species name.

---

## Task 1.3: Add Homeworld & Water Fields [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "homeworld or water"`

- [x] Add field `homeworld_type: str = ""` (PlanetType name or empty)
- [x] Add field `water_ideal: float = 0.5` (0.0-1.0, fraction of surface)
- [x] Add field `water_tolerance: float = 0.2` (0.0-1.0)
- [x] Write test: `test_default_water_preferences` - verify defaults 0.5/0.2
- [x] Write test: `test_create_race_with_homeworld_type` - set to "CONTINENTAL", verify stored
- [x] Run tests: all pass
**Notes:** All homeworld/water tests pass.

---

## Task 1.4: Add Aptitude Fields [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "aptitude"`

- [x] Add field `aptitude_strength: int = 5` (1-10)
- [x] Add field `aptitude_intelligence: int = 5` (1-10)
- [x] Add field `aptitude_constitution: int = 5` (1-10)
- [x] Add field `aptitude_dexterity: int = 5` (1-10)
- [x] Add field `aptitude_tolerance_other_species: int = 5` (1-10)
- [x] Add field `aptitude_cooperation: int = 5` (1-10)
- [x] Add field `aptitude_happiness: int = 5` (1-10)
- [x] Add field `aptitude_population_growth: int = 5` (1-10)
- [x] Add field `aptitude_conflict_tolerance: int = 5` (1-10)
- [x] Write test: `test_default_aptitudes_are_5` - all default to 5
- [x] Write test: `test_create_race_with_custom_aptitudes` - set various values
- [x] Run tests: all pass
**Notes:** All aptitude tests pass.

---

## Task 1.5: Update Serialization [Medium]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "serial or dict"`

- [x] Update `to_dict()` to include all new fields (identity, homeworld, water, aptitudes)
- [x] Update `from_dict()` to deserialize all new fields with defaults for missing keys
- [x] Write test: `test_to_dict_includes_all_new_fields` - verify all 20+ keys present
- [x] Write test: `test_from_dict_with_all_new_fields` - round-trip with all fields set
- [x] Write test: `test_from_dict_backward_compatible` - load old format (missing new fields) → defaults applied
- [x] Write test: `test_serialization_round_trip_complete` - full round-trip preserves everything
- [x] Verify existing serialization tests still pass
- [x] Run tests: all pass
**Notes:** All 8 serialization tests pass. Backward compatibility verified.

---

## Task 1.6: Update Validation [Medium]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "valid"`

- [x] Add validation: `water_ideal` must be 0.0-1.0
- [x] Add validation: `water_tolerance` must be 0.0-1.0
- [x] Add validation: each aptitude must be 1-10
- [x] Add validation: `government_type` if set must be in GOVERNMENT_TYPES
- [x] Add validation: `government_organization` if set must be in GOVERNMENT_ORGANIZATIONS
- [x] Add validation: `leader_title` if set must be in LEADER_TITLES
- [x] Add validation: `physical_type` if set must be in PHYSICAL_TYPES
- [x] Add validation: `society_type` if set must be in SOCIETY_TYPES
- [x] Add validation: `homeworld_type` if set must be valid PlanetType name
- [x] Write test: `test_validate_water_ideal_out_of_range`
- [x] Write test: `test_validate_water_tolerance_out_of_range`
- [x] Write test: `test_validate_aptitude_below_minimum`
- [x] Write test: `test_validate_aptitude_above_maximum`
- [x] Write test: `test_validate_invalid_government_type`
- [x] Write test: `test_validate_invalid_homeworld_type`
- [x] Write test: `test_validate_valid_race_with_all_new_fields` - fully populated → valid
- [x] Verify existing validation tests still pass
- [x] Run tests: all pass
**Notes:** All 17 validation tests pass. Identity fields are optional — empty string passes validation.

---

## Phase 1 Completion Checklist
- [x] All tasks above checked off
- [x] Run `pytest tests/unit/strategy/data/test_race_config.py -v` — 44 passed
- [x] Run `pytest tests/ -n 12` — 6222 passed (2 pre-existing failures in bug_15 tests)
- [x] RaceConfig backward compatibility verified (old JSON loads with defaults)
