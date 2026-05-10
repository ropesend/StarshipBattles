"""
Unit tests for test infrastructure validation.

PROJ-40/Phase 10: Test Infrastructure cleanup validation tests.
"""
from pathlib import Path

import pytest


class TestNoDuplicateTestScripts:
    """Tests for duplicate test script removal.

    PROJ-40/NEW-TEST-001: Duplicate test scripts should be consolidated.
    """

    @pytest.fixture
    def tests_dir(self):
        """Get the tests directory path."""
        return Path(__file__).parent.parent.parent.parent / "tests"

    def test_no_duplicate_profile_simulation(self, tests_dir):
        """Only one profile_simulation.py should exist.

        PROJ-40/NEW-TEST-001: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "profile_simulation.py"
        perf_version = tests_dir / "unit" / "performance" / "profile_simulation.py"

        assert perf_version.exists(), "profile_simulation.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate profile_simulation.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_repro_shield(self, tests_dir):
        """Only one repro_shield.py should exist.

        PROJ-40/NEW-TEST-001: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "repro_shield.py"
        perf_version = tests_dir / "unit" / "performance" / "repro_shield.py"

        assert perf_version.exists(), "repro_shield.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate repro_shield.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_repro_energy_stats(self, tests_dir):
        """Only one repro_energy_stats.py should exist.

        PROJ-40/NEW-TEST-001: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "repro_energy_stats.py"
        perf_version = tests_dir / "unit" / "performance" / "repro_energy_stats.py"

        assert perf_version.exists(), "repro_energy_stats.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate repro_energy_stats.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_reproduce_scaling(self, tests_dir):
        """Only one reproduce_scaling.py should exist.

        PROJ-40/NEW-TEST-001: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "reproduce_scaling.py"
        perf_version = tests_dir / "unit" / "performance" / "reproduce_scaling.py"

        assert perf_version.exists(), "reproduce_scaling.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate reproduce_scaling.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_stress_test(self, tests_dir):
        """Only one stress_test.py should exist.

        PROJ-40/NEW-TEST-001: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "stress_test.py"
        perf_version = tests_dir / "unit" / "performance" / "stress_test.py"

        assert perf_version.exists(), "stress_test.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate stress_test.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_generate_test_data(self, tests_dir):
        """Only one generate_test_data.py should exist.

        PROJ-40/NEW-TEST-002: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "generate_test_data.py"
        perf_version = tests_dir / "unit" / "performance" / "generate_test_data.py"

        assert perf_version.exists(), "generate_test_data.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate generate_test_data.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_strategy_tournament(self, tests_dir):
        """Only one strategy_tournament.py should exist.

        PROJ-40/NEW-TEST-002: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "strategy_tournament.py"
        perf_version = tests_dir / "unit" / "performance" / "strategy_tournament.py"

        assert perf_version.exists(), "strategy_tournament.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate strategy_tournament.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )

    def test_no_duplicate_verify_determinism(self, tests_dir):
        """Only one verify_determinism_current.py should exist.

        PROJ-40/NEW-TEST-002: Keep performance/ version, remove unit/ duplicate.
        """
        unit_version = tests_dir / "unit" / "verify_determinism_current.py"
        perf_version = tests_dir / "unit" / "performance" / "verify_determinism_current.py"

        assert perf_version.exists(), "verify_determinism_current.py should exist in performance/"
        assert not unit_version.exists(), (
            "Duplicate verify_determinism_current.py in tests/unit/ should be removed. "
            "Keep the version in tests/unit/performance/"
        )


class TestUtilityScriptNaming:
    """Tests for utility script naming conventions.

    PROJ-40/NEW-TEST-002: Utility scripts should use _ prefix to avoid pytest collection.
    """

    @pytest.fixture
    def tests_dir(self):
        """Get the tests directory path."""
        return Path(__file__).parent.parent.parent.parent / "tests"

    def test_verify_builder_imports_renamed(self, tests_dir):
        """verify_builder_imports.py should be renamed with _ prefix.

        PROJ-40/NEW-TEST-002: Utility scripts should not be collected by pytest.
        """
        old_name = tests_dir / "unit" / "verify_builder_imports.py"
        new_name = tests_dir / "unit" / "_verify_builder_imports.py"

        assert not old_name.exists(), (
            "verify_builder_imports.py should be renamed to _verify_builder_imports.py "
            "to avoid pytest collection (it's a utility script, not a test)"
        )
        assert new_name.exists(), "_verify_builder_imports.py should exist"


class TestFormationScriptNaming:
    """Tests for formation script naming conventions.

    PROJ-40/NEW-INT-002: Manual test scripts should use _ prefix.
    """

    @pytest.fixture
    def integration_dir(self):
        """Get the integration tests directory path."""
        return Path(__file__).parent.parent.parent.parent / "tests" / "integration"

    def test_formation_flight_is_manual_script(self, integration_dir):
        """test_formation_flight.py should be renamed since it's a manual script.

        PROJ-40/NEW-INT-002: This file has no pytest test functions, just a run_test() function.
        It should be renamed with _ prefix to indicate it's a manual test script.
        """
        old_name = integration_dir / "test_formation_flight.py"
        new_name = integration_dir / "_test_formation_flight.py"

        assert not old_name.exists(), (
            "test_formation_flight.py should be renamed to _test_formation_flight.py "
            "(it's a manual test script with no pytest functions)"
        )
        assert new_name.exists(), "_test_formation_flight.py should exist"

    def test_formation_attack_is_manual_script(self, integration_dir):
        """test_formation_attack.py should be renamed since it's a manual script.

        PROJ-40/NEW-INT-002: This file has no pytest test functions, just a run_test() function.
        It should be renamed with _ prefix to indicate it's a manual test script.
        """
        old_name = integration_dir / "test_formation_attack.py"
        new_name = integration_dir / "_test_formation_attack.py"

        assert not old_name.exists(), (
            "test_formation_attack.py should be renamed to _test_formation_attack.py "
            "(it's a manual test script with no pytest functions)"
        )
        assert new_name.exists(), "_test_formation_attack.py should exist"


class TestSharedTestHelpers:
    """Tests for shared test helper consolidation.

    PROJ-40/NEW-INT-003: Shared test helpers should be in conftest.py.
    """

    def test_make_mock_ship_instance_in_conftest(self):
        """make_mock_ship_instance should be available from root conftest.

        PROJ-40/NEW-INT-003: Consolidate shared test helpers to conftest.py.
        """
        # Import should work from the conftest fixture
        from tests.conftest import make_mock_ship_instance

        # Basic functionality test
        ship = make_mock_ship_instance(name="Test Ship", owner_id=1)
        assert ship.name == "Test Ship"
        assert ship.owner_id == 1

    def test_make_mock_ship_instance_not_duplicated_in_integration(self):
        """Integration test files should not define make_mock_ship_instance locally.

        PROJ-40/NEW-INT-003: Remove duplicates after consolidation.
        """
        import ast
        tests_dir = Path(__file__).parent.parent.parent.parent / "tests"

        files_to_check = [
            tests_dir / "integration" / "test_gameplay_loop.py",
            tests_dir / "integration" / "test_colonization.py",
            tests_dir / "integration" / "test_save_load.py",
        ]

        for file_path in files_to_check:
            if file_path.exists():
                content = file_path.read_text()
                tree = ast.parse(content)

                # Find function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        assert node.name != "make_mock_ship_instance", (
                            f"Duplicate make_mock_ship_instance found in {file_path.name}. "
                            "Use the version from tests/conftest.py instead."
                        )
