# Phase 4: Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-78 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit and integration tests for initial complex spawning

---

## Task 4.1: Create test_initial_complexes.py [Medium]
**File:** `tests/unit/quickstart/test_initial_complexes.py` (new file)
**Tests:** `pytest tests/unit/quickstart/test_initial_complexes.py -v`

- [x] Create new test file with the following test class:

```python
"""Tests for spawning initial complexes on home planets."""
import pytest
import shutil
import tempfile
from pathlib import Path

from game.strategy.quickstart_builder import QuickstartBuilder, INITIAL_COMPLEXES
from game.strategy.engine.game_session import GameSession


class TestSpawnInitialComplexes:
    """Tests for QuickstartBuilder.spawn_initial_complexes()"""

    @pytest.fixture
    def temp_save_folder(self):
        """Create temporary save folder."""
        folder = tempfile.mkdtemp(prefix="test_quickstart_")
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    @pytest.fixture
    def quickstart_session(self):
        """Create a quickstart game session."""
        config = QuickstartBuilder.build_1p_config(
            galaxy_radius=4000,
            system_count=5
        )
        return GameSession(config=config)

    def test_spawns_all_initial_complexes(self, temp_save_folder, quickstart_session):
        """Should spawn all 7 initial complexes on home planet."""
        QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder, quickstart_session)

        assert result is True
        home_planet = quickstart_session.empires[0].colonies[0]

        assert len(home_planet.facilities) == 7

        facility_ids = [f.design_id for f in home_planet.facilities]
        for expected_id in INITIAL_COMPLEXES:
            assert expected_id in facility_ids

    def test_spawns_shipyard_complex(self, temp_save_folder, quickstart_session):
        """Should spawn qs_complex (shipyard) on home planet."""
        QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, quickstart_session)

        home_planet = quickstart_session.empires[0].colonies[0]
        assert home_planet.has_space_shipyard

    def test_facilities_are_operational(self, temp_save_folder, quickstart_session):
        """All spawned facilities should be operational."""
        QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, quickstart_session)

        home_planet = quickstart_session.empires[0].colonies[0]
        for facility in home_planet.facilities:
            assert facility.is_operational is True

    def test_facilities_have_unique_ids(self, temp_save_folder, quickstart_session):
        """Each facility should have unique instance_id."""
        QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, quickstart_session)

        home_planet = quickstart_session.empires[0].colonies[0]
        instance_ids = [f.instance_id for f in home_planet.facilities]
        assert len(instance_ids) == len(set(instance_ids))

    def test_facilities_have_design_data(self, temp_save_folder, quickstart_session):
        """Each facility should have valid design data."""
        QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0])
        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, quickstart_session)

        home_planet = quickstart_session.empires[0].colonies[0]
        for facility in home_planet.facilities:
            assert facility.design_data is not None
            assert "name" in facility.design_data
            assert "layers" in facility.design_data

    def test_returns_false_on_missing_designs(self, temp_save_folder, quickstart_session):
        """Should return False if designs are missing."""
        # Don't copy designs, just try to spawn
        result = QuickstartBuilder.spawn_initial_complexes(temp_save_folder, quickstart_session)
        assert result is False


class TestSpawnInitialComplexes2Player:
    """Tests for 2-player quickstart scenarios."""

    @pytest.fixture
    def temp_save_folder(self):
        folder = tempfile.mkdtemp(prefix="test_quickstart_2p_")
        yield folder
        shutil.rmtree(folder, ignore_errors=True)

    def test_spawns_on_both_empires(self, temp_save_folder):
        """Should spawn complexes for both empires in 2P game."""
        config = QuickstartBuilder.build_2p_config(
            galaxy_radius=4000,
            system_count=10
        )
        session = GameSession(config=config)

        QuickstartBuilder.copy_quickstart_designs(temp_save_folder, [0, 1])
        QuickstartBuilder.spawn_initial_complexes(temp_save_folder, session)

        for empire in session.empires:
            home_planet = empire.colonies[0]
            assert len(home_planet.facilities) == 7
            assert home_planet.has_space_shipyard
```

- [x] Verify all tests pass

**Notes:** Unit tests already exist in test_quickstart_builder.py (17 tests from Phase 2). No need to duplicate.

---

## Task 4.2: Add Integration Test [Simple]
**File:** `tests/integration/quickstart/test_quickstart_flow.py` (new file)
**Tests:** `pytest tests/integration/quickstart/test_quickstart_flow.py -v`

- [x] Create integration test directory if needed: `tests/integration/quickstart/`
- [x] Create `__init__.py` in the directory
- [x] Create test file:

```python
"""Integration tests for full quickstart flow."""
import pytest
import shutil
import tempfile

from game.strategy.quickstart_builder import QuickstartBuilder
from game.strategy.engine.game_session import GameSession
from game.strategy.systems.save_game_service import SaveGameService


class TestQuickstartWithComplexes:
    """Integration tests verifying quickstart creates playable scenario."""

    @pytest.fixture
    def full_quickstart(self):
        """Run complete quickstart flow."""
        config = QuickstartBuilder.build_1p_config(
            galaxy_radius=4000,
            system_count=5
        )
        session = GameSession(config=config)

        success, message, save_path = SaveGameService.save_game(session, config.save_name)
        assert success, f"Save failed: {message}"

        session.save_path = save_path

        QuickstartBuilder.copy_quickstart_designs(save_path, [0])
        QuickstartBuilder.spawn_initial_complexes(save_path, session)

        yield session

        # Cleanup
        shutil.rmtree(save_path, ignore_errors=True)

    def test_home_planet_has_shipyard(self, full_quickstart):
        """Home planet should have operational shipyard."""
        session = full_quickstart
        home_planet = session.empires[0].colonies[0]
        assert home_planet.has_space_shipyard is True

    def test_home_planet_has_all_resource_harvesters(self, full_quickstart):
        """Home planet should have all 5 resource harvester complexes."""
        session = full_quickstart
        home_planet = session.empires[0].colonies[0]

        design_ids = [f.design_id for f in home_planet.facilities]
        assert 'qs_metals_complex' in design_ids
        assert 'qs_organics_complex' in design_ids
        assert 'qs_vapors_complex' in design_ids
        assert 'qs_radioactives_complex' in design_ids
        assert 'qs_exotics_complex' in design_ids

    def test_home_planet_has_resupply_depot(self, full_quickstart):
        """Home planet should have fuel depot."""
        session = full_quickstart
        home_planet = session.empires[0].colonies[0]

        design_ids = [f.design_id for f in home_planet.facilities]
        assert 'qs_resupply_depot' in design_ids
```

- [x] Verify all tests pass

**Notes:** 8 integration tests: 1P (7 facilities, shipyard, resource harvesters, resupply depot, operational, design data) + 2P (both empires facilities, all complex types). Used UUID-based save names to avoid xdist parallel collisions.

---

## Task 4.3: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite
- [x] Verify no regressions (baseline: 7286 passed → 7294 passed, +8 new integration tests)
- [x] Document any new test count: 7294 passed, 2 pre-existing failures

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All new tests pass
- [x] No regressions in existing tests
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Implementation Complete"
