# Phase 2: Write Core Validation Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-159 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Write ~12 core integration tests covering key validation scenarios

---

## Tasks

### Task 2.1: Create test file with load validation tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py` (NEW)
**Tests:** `pytest tests/integration/strategy/transfer/test_transfer_validation.py -v`

- [ ] Create test file with docstring and imports:
  ```python
  """
  Integration tests for TransferValidator.

  PROJ-159: Rewritten from unit tests to use real Planet/Fleet objects
  instead of MagicMock, which doesn't satisfy protocol checks.
  """
  import pytest
  from game.strategy.validation.transfer_validator import TransferValidator
  from game.core.hex_math import HexCoord
  ```
- [ ] Test: `test_load_passengers_success`:
  ```python
  def test_load_passengers_success(mock_galaxy, colonized_planet, transport_fleet):
      """Load is valid when fleet has capacity and colony has population."""
      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, colonized_planet,
          "passengers", "load", 50
      )
      assert result.is_valid
      assert result.errors == []
  ```
- [ ] Test: `test_load_fails_when_fleet_full`:
  ```python
  def test_load_fails_when_fleet_full(mock_galaxy, colonized_planet):
      """Load fails when fleet has no available cargo capacity."""
      full_fleet = create_transport_fleet(cargo_capacity=100, current_cargo=100)
      result = TransferValidator.validate(
          mock_galaxy, full_fleet, colonized_planet,
          "passengers", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "NO_CARGO_SPACE"
  ```
- [ ] Test: `test_load_fails_when_colony_empty`:
  ```python
  def test_load_fails_when_colony_empty(mock_galaxy, transport_fleet):
      """Load fails when colony has no population."""
      empty_colony = create_test_planet(owner_id=0, population_count=0)
      # Add empty colony to galaxy system
      mock_galaxy.systems[HexCoord(0, 0)].planets.append(empty_colony)

      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, empty_colony,
          "passengers", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "NO_POPULATION"
  ```
- [ ] Verify: `pytest tests/integration/strategy/transfer/test_transfer_validation.py::test_load* -v` passes

**Notes:**

---

### Task 2.2: Add unload validation tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py`
**Tests:** `pytest tests/integration/strategy/transfer/test_transfer_validation.py -v`

- [ ] Test: `test_unload_passengers_success`:
  ```python
  def test_unload_passengers_success(mock_galaxy, colonized_planet, loaded_fleet):
      """Unload is valid when fleet has cargo to unload."""
      result = TransferValidator.validate(
          mock_galaxy, loaded_fleet, colonized_planet,
          "passengers", "unload", 30
      )
      assert result.is_valid
      assert result.errors == []
  ```
- [ ] Test: `test_unload_fails_when_fleet_empty`:
  ```python
  def test_unload_fails_when_fleet_empty(mock_galaxy, colonized_planet, transport_fleet):
      """Unload fails when fleet has no cargo of this type."""
      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, colonized_planet,
          "passengers", "unload", 30
      )
      assert not result.is_valid
      assert result.error_code == "NO_CARGO_TO_UNLOAD"
  ```
- [ ] Verify: `pytest tests/integration/strategy/transfer/test_transfer_validation.py::test_unload* -v` passes

**Notes:**

---

### Task 2.3: Add general validation tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py`
**Tests:** `pytest tests/integration/strategy/transfer/test_transfer_validation.py -v`

- [ ] Test: `test_fails_when_fleet_not_at_planet`:
  ```python
  def test_fails_when_fleet_not_at_planet(colonized_planet):
      """Transfer fails when fleet is not at the planet's system."""
      # Planet in system at (10, 10), fleet at (0, 0)
      galaxy = MockGalaxy()
      system = MockSystem(HexCoord(10, 10), [colonized_planet])
      galaxy.add_system(system)

      fleet = create_transport_fleet(location=HexCoord(0, 0))

      result = TransferValidator.validate(
          galaxy, fleet, colonized_planet,
          "passengers", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "NOT_AT_PLANET"
  ```
- [ ] Test: `test_fails_when_planet_uncolonized`:
  ```python
  def test_fails_when_planet_uncolonized(transport_fleet, uncolonized_planet):
      """Transfer fails when planet is not colonized."""
      galaxy = MockGalaxy()
      system = MockSystem(HexCoord(0, 0), [uncolonized_planet])
      galaxy.add_system(system)

      result = TransferValidator.validate(
          galaxy, transport_fleet, uncolonized_planet,
          "passengers", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "NOT_COLONIZED"
  ```
- [ ] Test: `test_fails_when_fleet_none`:
  ```python
  def test_fails_when_fleet_none(mock_galaxy, colonized_planet):
      """Transfer fails when fleet is None."""
      result = TransferValidator.validate(
          mock_galaxy, None, colonized_planet,
          "passengers", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "FLEET_NOT_FOUND"
  ```
- [ ] Test: `test_fails_when_planet_none`:
  ```python
  def test_fails_when_planet_none(mock_galaxy, transport_fleet):
      """Transfer fails when planet is None."""
      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, None,
          "passengers", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "TARGET_NOT_FOUND"
  ```
- [ ] Test: `test_fails_with_invalid_direction`:
  ```python
  def test_fails_with_invalid_direction(mock_galaxy, colonized_planet, transport_fleet):
      """Transfer fails with invalid direction."""
      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, colonized_planet,
          "passengers", "invalid", 50
      )
      assert not result.is_valid
      assert result.error_code == "INVALID_DIRECTION"
  ```
- [ ] Test: `test_fails_with_invalid_cargo_type`:
  ```python
  def test_fails_with_invalid_cargo_type(mock_galaxy, colonized_planet, transport_fleet):
      """Transfer fails with unrecognized cargo type."""
      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, colonized_planet,
          "unknown_cargo", "load", 50
      )
      assert not result.is_valid
      assert result.error_code == "INVALID_CARGO_TYPE"
  ```
- [ ] Verify: All general tests pass

**Notes:**

---

### Task 2.4: Add species-specific edge case tests [Simple]
**File:** `tests/integration/strategy/transfer/test_transfer_validation.py`
**Tests:** `pytest tests/integration/strategy/transfer/test_transfer_validation.py -v`

- [ ] Test: `test_load_specific_species_success`:
  ```python
  def test_load_specific_species_success(mock_galaxy, transport_fleet):
      """Load passengers of specific species when available."""
      planet = create_test_planet(
          owner_id=0, population_count=500, species_id="vulcan"
      )
      mock_galaxy.systems[HexCoord(0, 0)].planets.append(planet)

      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, planet,
          "passengers", "load", 50, species_id="vulcan"
      )
      assert result.is_valid
  ```
- [ ] Test: `test_load_specific_species_not_present_fails`:
  ```python
  def test_load_specific_species_not_present_fails(mock_galaxy, colonized_planet, transport_fleet):
      """Load fails when specified species not present on planet."""
      # colonized_planet has "human" species by default
      result = TransferValidator.validate(
          mock_galaxy, transport_fleet, colonized_planet,
          "passengers", "load", 50, species_id="alien"
      )
      assert not result.is_valid
      assert result.error_code == "NO_POPULATION"
      assert "alien" in result.errors[0]
  ```
- [ ] Verify: All tests pass: `pytest tests/integration/strategy/transfer/ -v`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 12 tests in `test_transfer_validation.py` pass
- [ ] `pytest tests/integration/strategy/transfer/ -v` shows 12 passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
