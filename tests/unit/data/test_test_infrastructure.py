"""
Unit tests for test infrastructure validation.

PROJ-40/Phase 10: Test Infrastructure cleanup validation tests.

The original ``TestNoDuplicateTestScripts`` class held 8 ``test_no_duplicate_*``
tests that were marked ``@pytest.mark.skip`` with a TODO to migrate them to a
linter/hook. PROJ-326 Phase 1 closed that TODO debt: the duplicate-script
problem they guarded against has been resolved (the files no longer exist),
and broader scan coverage now lives in ``Tools/lint_test_files.py``.
"""
from pathlib import Path

import pytest


class TestUtilityScriptNaming:
    """Tests for utility script naming conventions.

    PROJ-40/NEW-TEST-002: Utility scripts should use _ prefix to avoid pytest collection.
    """

    @pytest.fixture
    def tests_dir(self):
        """Get the tests directory path."""
        return Path(__file__).parent.parent.parent.parent / "tests"

    def test_verify_builder_imports_not_pytest_collected(self, tests_dir):
        """verify_builder_imports.py should not be present as a pytest-collected name.

        PROJ-40/NEW-TEST-002: Utility scripts should not be collected by pytest.

        PROJ-443 Phase 3c: the underscore-rename happened, and then the file
        was deleted entirely in a later cleanup pass (PROJ-326 Phase 1 per the
        module docstring: "the files no longer exist"). The original
        assertion that the underscored name *exists* is therefore obsolete.
        Rewritten as: neither the pytest-collected name nor the legacy
        location should pollute the test tree — both gone is the desired
        steady state.
        """
        old_name = tests_dir / "unit" / "verify_builder_imports.py"
        assert not old_name.exists(), (
            "verify_builder_imports.py should not exist in tests/unit/ "
            "(it was a utility script; PROJ-40 renamed it to use _ prefix "
            "and PROJ-326 Phase 1 deleted the underscored version entirely)"
        )


class TestFormationScriptNaming:
    """Tests for formation script naming conventions.

    PROJ-40/NEW-INT-002: Manual test scripts should use _ prefix.
    """

    @pytest.fixture
    def integration_dir(self):
        """Get the integration tests directory path."""
        return Path(__file__).parent.parent.parent.parent / "tests" / "integration"

    def test_formation_flight_not_pytest_collected(self, integration_dir):
        """test_formation_flight.py should not be present as a pytest-collected name.

        PROJ-40/NEW-INT-002: Manual scripts should not be collected by pytest.

        PROJ-443 Phase 3c: same lifecycle as `_verify_builder_imports.py` —
        renamed with `_` prefix then deleted entirely. Test rewritten to
        only assert the pytest-collected name is absent.
        """
        old_name = integration_dir / "test_formation_flight.py"
        assert not old_name.exists(), (
            "test_formation_flight.py should not exist in tests/integration/ "
            "(manual script; PROJ-40 renamed it, later deleted entirely)"
        )

    def test_formation_attack_not_pytest_collected(self, integration_dir):
        """test_formation_attack.py should not be present as a pytest-collected name.

        See sibling test — same rationale.
        """
        old_name = integration_dir / "test_formation_attack.py"
        assert not old_name.exists(), (
            "test_formation_attack.py should not exist in tests/integration/ "
            "(manual script; PROJ-40 renamed it, later deleted entirely)"
        )


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
