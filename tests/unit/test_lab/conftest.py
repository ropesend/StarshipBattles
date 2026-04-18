"""Shared fixtures for tests/unit/test_lab/.

Currently provides only the PROJ-279 spec-compiler patch needed by tests
that mock TestScenario instances and expect the legacy
`scenario.to_spec()` injection point to work.
"""
import pytest

from tests.fixtures.test_scenarios import (
    patch_spec_compiler_to_delegate_to_mock_scenario,
)


@pytest.fixture(autouse=True)
def _proj279_patch_spec_compiler():
    """PROJ-279: production code now calls `build_test_battle_spec(scenario)`
    directly instead of `scenario.to_spec()`. Patch the spec compiler so
    mocked scenarios that set `to_spec.return_value` still flow through
    correctly without rewriting every test."""
    with patch_spec_compiler_to_delegate_to_mock_scenario():
        yield
