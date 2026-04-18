"""
ToHitAttackModifier Fleet Scope Test Scenarios (TOHIT-ATK-FLEET-001 to 004)

Tests fleet-scoped to-hit attack modifiers:
- Fleet bonus applied to all friendly ships
- Bonus removed when provider destroyed
- Stacking: same group MAX, different groups SUM
- External battle conditions (from BattleConfig)
"""
import pygame
from combat_lab.scenarios.base import TestMetadata, TestScenario
from combat_lab.scenarios.templates import StaticTargetScenario
from combat_lab.scenarios.validation import (
    check_true, check_approx, check_exact,
)
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE, STANDARD_TEST_TICKS, STANDARD_SEED,
)


def _build_two_team_spec(scenario, *, team0_ships, team1_ships):
    """PROJ-269 Task 6.7: helper for custom two-team specs.

    Each entry in `team0_ships` / `team1_ships` is `(role, design_id,
    (x, y))`. Constructs a BattleSpec with CUSTOM formations so the
    FormationResolver reproduces the scenario's per-ship positions.
    """
    from game.core.math import Vector2
    from game.simulation.battle_spec import ( BattleSpec, CombatPolicies, EntryVector,
        ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec,
    )
    from game.simulation.combat.boundary import UnboundedRegion
    from game.simulation.combat.formation import FormationShape, FormationSpec
    from game.simulation.combat.modifier_stack import ModifierStack
    from game.simulation.combat.telemetry import TelemetryLevel

    def _ship(role, design_id, x, y):
        return ShipSpec(
            instance_id=f"{scenario.metadata.test_id}:{role}",
            design_id=design_id,
            theme_id="Federation",
            name=f"{scenario.metadata.test_id}-{role}",
            position=Vector2(float(x), float(y)),
            angle=0.0,
            velocity=Vector2(0.0, 0.0),
            components=(),
            scenario_role=role,
        )

    def _team(team_id, name, entries):
        ships = tuple(_ship(role, design, x, y) for role, design, (x, y) in entries)
        positions = tuple(Vector2(float(x), float(y)) for _, _, (x, y) in entries)
        formation = FormationSpec(
            shape=FormationShape.CUSTOM,
            spacing=100.0,
            custom_positions=positions,
        )
        return TeamSpec(
            team_id=team_id, name=name,
            entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
            fleet_hierarchy=(
                TaskForceSpec(
                    task_force_id=f"tf-{team_id}",
                    formation=formation,
                    policies=CombatPolicies(),
                    squadrons=(
                        SquadronSpec(
                            squadron_id=f"sq-{team_id}",
                            policies=CombatPolicies(),
                            ships=ships,
                        ),
                    ),
                ),
            ),
        )

    teams = [_team(0, "Team0", team0_ships)]
    if team1_ships:
        teams.append(_team(1, "Team1", team1_ships))

    return BattleSpec(
        seed=scenario.metadata.seed,
        telemetry_level=TelemetryLevel.DETAILED,
        boundary=UnboundedRegion(),
        end_condition=scenario._create_end_condition(),
        absolute_max_ticks=max(scenario.metadata.max_ticks * 10, 1000),
        teams=tuple(teams),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


# =============================================================================
# TOHIT-ATK-FLEET-001: Fleet sensor provides bonus to all friendly ships
# =============================================================================

class FleetSensorBonusApplied(StaticTargetScenario):
    """TOHIT-ATK-FLEET-001: Fleet-scope sensor bonus is applied during combat."""

    metadata = TestMetadata(
        test_id="TOHIT-ATK-FLEET-001",
        category="Weapons",
        subcategory="ToHitAttackModifier",
        name="Fleet Sensor Bonus Applied",
        summary="Ship with fleet-scope ToHitAttackModifier provides bonus and deals damage",
        conditions=["Attacker: Test_Attacker_Beam_FleetSensor.json (test_beam_1dmg_guaranteed + fleet_sensor_2)",
                     "Target: Test_Target_Stationary.json (test_armor_extreme_hp, 1B HP, stationary)",
                     f"Distance: {POINT_BLANK_DISTANCE}px, {STANDARD_TEST_TICKS} ticks"],
        edge_cases=["Bonus should appear in ship.fleet_attack_bonus AND weapon should fire"],
        expected_outcome="fleet_attack_bonus == 2.0 AND damage dealt > 0",
        pass_criteria="fleet_attack_bonus == 2.0 AND damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
    )

    attacker_ship = "Test_Attacker_Beam_FleetSensor.json"
    target_ship = "Test_Target_Stationary.json"
    distance = POINT_BLANK_DISTANCE
    force_fire = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = []

        # Data: verify fleet bonus is set on the attacker
        fleet_bonus = getattr(self.attacker, 'fleet_attack_bonus', None)
        checks.append(check_true(
            "Fleet Attack Bonus Set",
            fleet_bonus is not None and isinstance(fleet_bonus, (int, float)),
            actual=fleet_bonus,
        ))

        bonus_val = fleet_bonus if isinstance(fleet_bonus, (int, float)) else 0.0
        checks.append(check_exact("Fleet Attack Bonus Value", 2.0, bonus_val))

        # Outcome: verify weapon actually fired and dealt damage (combat validation)
        checks.append(check_true(
            "Damage Dealt (combat validation)",
            self.damage_dealt > 0,
            actual=self.damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-ATK-FLEET-002: External battle condition applied
# =============================================================================

class ExternalBattleConditionApplied(TestScenario):
    """TOHIT-ATK-FLEET-002: External battle condition modifier applied via config."""

    metadata = TestMetadata(
        test_id="TOHIT-ATK-FLEET-002",
        category="Weapons",
        subcategory="ToHitAttackModifier",
        name="External Battle Condition Applied",
        summary="Per-team modifier from BattleConfig applies to all ships and weapon fires",
        conditions=["Attacker: Test_Attacker_Beam360_Low.json (low accuracy beam)",
                     "Target: Test_Target_Stationary.json (stationary)",
                     "Team 0 gets +3 ToHitAttack from external source",
                     f"Distance: {POINT_BLANK_DISTANCE}px, {STANDARD_TEST_TICKS} ticks"],
        edge_cases=["Bonus persists entire battle (not tied to a ship)"],
        expected_outcome="fleet_attack_bonus == 3.0 AND weapon fires and deals damage",
        pass_criteria="fleet_attack_bonus == 3.0 AND damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
    )

    def to_spec(self, registries=None):
        """PROJ-269: compile to a 2-team 1v1 BattleSpec."""
        _ = registries
        return _build_two_team_spec(
            self,
            team0_ships=[
                ("attacker", "Test_Attacker_Beam360_Low.json", (0, 0)),
            ],
            team1_ships=[
                ("target", "Test_Target_Stationary.json", (POINT_BLANK_DISTANCE, 0)),
            ],
        )

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        """PROJ-269: cache refs + assign movement policies.

        The ExternalModifier injection moves to `custom_setup(engine)`
        since it needs engine.aura_manager to exist (post engine.start).
        """
        _ = engine, initial_state
        self.attacker = ships_by_role["attacker"]
        self.target = ships_by_role["target"]
        self._initial_target_hp = self.target.hp
        self.attacker.movement_policy = "test_stationary"
        self.target.movement_policy = "test_do_nothing"

    def custom_setup(self, battle_engine):
        """Inject the external ToHitAttackModifier into aura_manager.

        Called by the runner's pre_tick_loop after engine.start + wire_ships.
        """
        from game.simulation.combat.fleet_aura_manager import ExternalModifier
        battle_engine.aura_manager._external.append(
            ExternalModifier(
                ability_name='ToHitAttackModifier',
                value=3.0,
                source_name='System Sensor Array',
                team_id=0,
            )
        )
        battle_engine.aura_manager._recalculate(battle_engine.ships)

    def collect_results(self, outcome, telemetry=None):
        self.results['ticks_run'] = outcome.duration_ticks
        self.results['damage_dealt'] = 0
        # Measure damage dealt to target
        if hasattr(self, 'target') and self.target:
            initial_hp = getattr(self, '_initial_target_hp', 0)
            self.results['damage_dealt'] = initial_hp - self.target.hp if initial_hp else 0

    def validate(self, outcome, telemetry=None) -> list:
        checks = []

        fleet_bonus = getattr(self.attacker, 'fleet_attack_bonus', 0.0)
        checks.append(check_exact(
            "External Bonus Applied",
            3.0,
            fleet_bonus if isinstance(fleet_bonus, (int, float)) else 0.0,
        ))

        # Outcome: weapon fired and dealt damage (combat validation)
        damage = self.results.get('damage_dealt', 0)
        checks.append(check_true(
            "Damage Dealt (combat validation)",
            damage > 0,
            actual=damage,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-ATK-FLEET-003: Same stack group = MAX (not sum)
# =============================================================================

class FleetSensorSameGroupMax(TestScenario):
    """TOHIT-ATK-FLEET-003: Two providers with same stack_group → take MAX."""

    metadata = TestMetadata(
        test_id="TOHIT-ATK-FLEET-003",
        category="Weapons",
        subcategory="ToHitAttackModifier",
        name="Same Stack Group MAX",
        summary="Two fleet-scope sensors in same stack_group: MAX(+2, +3) = +3, not +5",
        conditions=["Provider A: +2 FleetSensor group", "Provider B: +3 FleetSensor group"],
        edge_cases=["Same stack_group should MAX, not sum"],
        expected_outcome="fleet_attack_bonus == 3.0 (MAX of 2 and 3)",
        pass_criteria="fleet_attack_bonus == 3.0",
        max_ticks=5,
        seed=STANDARD_SEED,
    )

    def to_spec(self, registries=None):
        _ = registries
        return _build_two_team_spec(
            self,
            team0_ships=[
                ("provider_a", "Test_FleetSensor_Provider.json", (0, 0)),
                ("provider_b", "Test_FleetSensor_Provider_3_GroupA.json", (0, 100)),
            ],
            team1_ships=[
                ("target", "Test_Target_Stationary.json", (500, 0)),
            ],
        )

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        _ = engine, initial_state
        self.provider_a = ships_by_role["provider_a"]
        self.provider_b = ships_by_role["provider_b"]
        self.target = ships_by_role["target"]
        self.provider_a.movement_policy = "test_do_nothing"
        self.provider_b.movement_policy = "test_do_nothing"
        self.target.movement_policy = "test_do_nothing"

    def validate(self, outcome, telemetry=None) -> list:
        checks = []
        bonus_a = getattr(self.provider_a, 'fleet_attack_bonus', 0.0)
        bonus_a = bonus_a if isinstance(bonus_a, (int, float)) else 0.0
        checks.append(check_exact("Same Group MAX (not sum)", 3.0, bonus_a))
        return checks


# =============================================================================
# TOHIT-ATK-FLEET-004: Different stack groups = SUM
# =============================================================================

class FleetSensorDiffGroupSum(TestScenario):
    """TOHIT-ATK-FLEET-004: Two providers with different stack_groups → SUM."""

    metadata = TestMetadata(
        test_id="TOHIT-ATK-FLEET-004",
        category="Weapons",
        subcategory="ToHitAttackModifier",
        name="Different Stack Groups SUM",
        summary="Two fleet-scope sensors in different stack_groups: +2 (A) + +1 (B) = +3",
        conditions=["Provider A: +2 FleetSensor group", "Provider B: +1 FleetSensorB group"],
        edge_cases=["Different stack_groups should sum"],
        expected_outcome="fleet_attack_bonus == 3.0 (2 + 1)",
        pass_criteria="fleet_attack_bonus == 3.0",
        max_ticks=5,
        seed=STANDARD_SEED,
    )

    def to_spec(self, registries=None):
        _ = registries
        return _build_two_team_spec(
            self,
            team0_ships=[
                ("provider_a", "Test_FleetSensor_Provider.json", (0, 0)),
                ("provider_b", "Test_FleetSensor_Provider_GroupB.json", (0, 100)),
            ],
            team1_ships=[
                ("target", "Test_Target_Stationary.json", (500, 0)),
            ],
        )

    def wire_ships(self, ships_by_role, *, engine=None, initial_state=None):
        _ = engine, initial_state
        self.provider_a = ships_by_role["provider_a"]
        self.provider_b = ships_by_role["provider_b"]
        self.target = ships_by_role["target"]
        self.provider_a.movement_policy = "test_do_nothing"
        self.provider_b.movement_policy = "test_do_nothing"
        self.target.movement_policy = "test_do_nothing"

    def validate(self, outcome, telemetry=None) -> list:
        checks = []
        bonus = getattr(self.provider_a, 'fleet_attack_bonus', 0.0)
        bonus = bonus if isinstance(bonus, (int, float)) else 0.0
        checks.append(check_exact("Different Groups SUM", 3.0, bonus))
        return checks
