"""PROJ-270 Phase 1.3: scenario template `setup(battle_engine)` deletion guard.

The legacy `setup(battle_engine)` entry point is deleted from all 5 Combat
Lab scenario templates and from the `TestScenario` base class. Scenarios
drive the unified `run_battle(spec)` path exclusively via `to_spec` +
`before_run_battle` + `wire_ships` + `custom_setup`. This test guards
against reintroduction.
"""
from combat_lab.scenarios.base import TestScenario
from combat_lab.scenarios.templates import (
    ComparisonScenario,
    DuelScenario,
    PropulsionScenario,
    ResourceScenario,
    StaticTargetScenario,
)


class TestNoLegacySetupOnTemplates:
    """`setup(battle_engine)` is deleted from every template + base class."""

    def test_base_testscenario_has_no_setup_attribute(self):
        """The base `TestScenario` class no longer defines `setup`."""
        assert not hasattr(TestScenario, 'setup'), (
            "TestScenario.setup is a PROJ-270 Phase 1.3 deletion target. "
            "Scenarios drive `run_battle(spec)` via `to_spec` + "
            "`wire_ships` + `custom_setup`; there is no `setup(engine)`."
        )

    def test_static_target_scenario_has_no_setup(self):
        assert not hasattr(StaticTargetScenario, 'setup')

    def test_duel_scenario_has_no_setup(self):
        assert not hasattr(DuelScenario, 'setup')

    def test_propulsion_scenario_has_no_setup(self):
        assert not hasattr(PropulsionScenario, 'setup')

    def test_resource_scenario_has_no_setup(self):
        assert not hasattr(ResourceScenario, 'setup')

    def test_comparison_scenario_has_no_setup(self):
        assert not hasattr(ComparisonScenario, 'setup')

    def test_comparison_scenario_has_no_legacy_setup_battle_helper(self):
        """`_setup_battle` was only called from the deleted `setup()`."""
        assert not hasattr(ComparisonScenario, '_setup_battle'), (
            "ComparisonScenario._setup_battle was only called from the "
            "deleted `setup()` method. Baseline runs via "
            "`before_run_battle`; variant runs via the spec compiler."
        )


class TestNoLegacySetupOnPropulsionScenarios:
    """PROP-005's custom scenario class also has no legacy `setup`."""

    def test_prop005_has_no_setup(self):
        from combat_lab.scenarios.propulsion_scenarios import (
            PropMassAffectsTurnRateScenario,
        )
        assert not hasattr(PropMassAffectsTurnRateScenario, 'setup')

    def test_prop_thrust_mass_ratio_has_no_setup(self):
        from combat_lab.scenarios.propulsion_scenarios import (
            PropThrustMassRatioScenario,
        )
        assert not hasattr(PropThrustMassRatioScenario, 'setup')
