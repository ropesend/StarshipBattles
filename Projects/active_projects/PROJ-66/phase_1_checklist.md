# Phase 1: Data Layer - RaceConfig Enhancement [Medium]

**Objective:** Add all new fields to RaceConfig with serialization, defaults, and validation
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v`

---

## Task 1.1: Add Constant Lists [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "constant"`

- [ ] Add `GOVERNMENT_TYPES` list constant (14 items: Empire, Hegemony, Alliance, etc.)
- [ ] Add `GOVERNMENT_ORGANIZATIONS` list constant (13 items: Anarchy, Democracy, etc.)
- [ ] Add `LEADER_TITLES` list constant (27 items: Central Speaker, Chairman, etc.)
- [ ] Add `PHYSICAL_TYPES` list constant (14 items: Felinoid, Caninoid, etc.)
- [ ] Add `SOCIETY_TYPES` list constant (17 items: Artisans, Berserkers, etc.)
- [ ] Add `APTITUDE_NAMES` list constant (9 items: strength, intelligence, constitution, dexterity, tolerance_other_species, cooperation, happiness, population_growth, conflict_tolerance)
- [ ] Write test: `test_government_types_list_has_14_items`
- [ ] Write test: `test_government_organizations_list_has_13_items`
- [ ] Write test: `test_leader_titles_list_has_27_items`
- [ ] Write test: `test_physical_types_list_has_14_items`
- [ ] Write test: `test_society_types_list_has_17_items`
- [ ] Write test: `test_aptitude_names_list_has_9_items`
- [ ] Run tests: all pass
**Notes:**

---

## Task 1.2: Add Identity Fields to RaceConfig [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "identity"`

- [ ] Add field `faction_name: str = ""` (auto-generated from race name + government type)
- [ ] Add field `race_name: str = ""` (species name, e.g., "Rossarians")
- [ ] Add field `race_name_plural: str = ""` (e.g., "Rossarians")
- [ ] Add field `government_type: str = ""` (from GOVERNMENT_TYPES)
- [ ] Add field `government_organization: str = ""` (from GOVERNMENT_ORGANIZATIONS)
- [ ] Add field `leader_title: str = ""` (from LEADER_TITLES)
- [ ] Add field `physical_type: str = ""` (from PHYSICAL_TYPES)
- [ ] Add field `society_type: str = ""` (from SOCIETY_TYPES)
- [ ] Write test: `test_create_race_with_identity_fields` - verify all defaults
- [ ] Write test: `test_create_race_with_custom_identity` - set all fields, verify stored
- [ ] Run tests: all pass
**Notes:** The existing `name` field continues to function as the display name / faction_name for backward compatibility. New `race_name` is the species name.

---

## Task 1.3: Add Homeworld & Water Fields [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "homeworld or water"`

- [ ] Add field `homeworld_type: str = ""` (PlanetType name or empty)
- [ ] Add field `water_ideal: float = 0.5` (0.0-1.0, fraction of surface)
- [ ] Add field `water_tolerance: float = 0.2` (0.0-1.0)
- [ ] Write test: `test_default_water_preferences` - verify defaults 0.5/0.2
- [ ] Write test: `test_create_race_with_homeworld_type` - set to "CONTINENTAL", verify stored
- [ ] Run tests: all pass
**Notes:**

---

## Task 1.4: Add Aptitude Fields [Simple]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "aptitude"`

- [ ] Add field `aptitude_strength: int = 5` (1-10)
- [ ] Add field `aptitude_intelligence: int = 5` (1-10)
- [ ] Add field `aptitude_constitution: int = 5` (1-10)
- [ ] Add field `aptitude_dexterity: int = 5` (1-10)
- [ ] Add field `aptitude_tolerance_other_species: int = 5` (1-10)
- [ ] Add field `aptitude_cooperation: int = 5` (1-10)
- [ ] Add field `aptitude_happiness: int = 5` (1-10)
- [ ] Add field `aptitude_population_growth: int = 5` (1-10)
- [ ] Add field `aptitude_conflict_tolerance: int = 5` (1-10)
- [ ] Write test: `test_default_aptitudes_are_5` - all default to 5
- [ ] Write test: `test_create_race_with_custom_aptitudes` - set various values
- [ ] Run tests: all pass
**Notes:**

---

## Task 1.5: Update Serialization [Medium]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "serial or dict"`

- [ ] Update `to_dict()` to include all new fields (identity, homeworld, water, aptitudes)
- [ ] Update `from_dict()` to deserialize all new fields with defaults for missing keys
- [ ] Write test: `test_to_dict_includes_all_new_fields` - verify all 20+ keys present
- [ ] Write test: `test_from_dict_with_all_new_fields` - round-trip with all fields set
- [ ] Write test: `test_from_dict_backward_compatible` - load old format (missing new fields) → defaults applied
- [ ] Write test: `test_serialization_round_trip_complete` - full round-trip preserves everything
- [ ] Verify existing serialization tests still pass
- [ ] Run tests: all pass
**Notes:** Backward compatibility is critical. from_dict() must use `.get(key, default)` for every new field.

---

## Task 1.6: Update Validation [Medium]
**File:** `game/strategy/data/race_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_config.py -v -k "valid"`

- [ ] Add validation: `water_ideal` must be 0.0-1.0
- [ ] Add validation: `water_tolerance` must be 0.0-1.0
- [ ] Add validation: each aptitude must be 1-10
- [ ] Add validation: `government_type` if set must be in GOVERNMENT_TYPES
- [ ] Add validation: `government_organization` if set must be in GOVERNMENT_ORGANIZATIONS
- [ ] Add validation: `leader_title` if set must be in LEADER_TITLES
- [ ] Add validation: `physical_type` if set must be in PHYSICAL_TYPES
- [ ] Add validation: `society_type` if set must be in SOCIETY_TYPES
- [ ] Add validation: `homeworld_type` if set must be valid PlanetType name
- [ ] Write test: `test_validate_water_ideal_out_of_range`
- [ ] Write test: `test_validate_water_tolerance_out_of_range`
- [ ] Write test: `test_validate_aptitude_below_minimum`
- [ ] Write test: `test_validate_aptitude_above_maximum`
- [ ] Write test: `test_validate_invalid_government_type`
- [ ] Write test: `test_validate_invalid_homeworld_type`
- [ ] Write test: `test_validate_valid_race_with_all_new_fields` - fully populated → valid
- [ ] Verify existing validation tests still pass
- [ ] Run tests: all pass
**Notes:** Identity fields are optional — empty string passes validation. Only validate if set.

---

## Phase 1 Completion Checklist
- [ ] All tasks above checked off
- [ ] Run `pytest tests/unit/strategy/data/test_race_config.py -v` — all pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] RaceConfig backward compatibility verified (old JSON loads with defaults)
