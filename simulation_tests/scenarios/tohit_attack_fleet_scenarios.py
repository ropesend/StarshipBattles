"""
ToHitAttackModifier Fleet Scope Test Scenarios (TOHIT-ATK-FLEET-001 to 004)

Tests fleet-scoped to-hit attack modifiers:
- Fleet bonus applied to all friendly ships
- Bonus removed when provider destroyed
- Stacking: same group MAX, different groups SUM
- External battle conditions (from BattleConfig)
"""
import pygame
from simulation_tests.scenarios.base import TestMetadata, TestScenario
from simulation_tests.scenarios.templates import StaticTargetScenario
from simulation_tests.scenarios.validation import (
    check_true, check_approx, check_exact,
)
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE, STANDARD_TEST_TICKS, STANDARD_SEED,
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
        summary="Ship with fleet-scope ToHitAttackModifier provides bonus to all friendly ships",
        conditions=["Attacker has fleet-scope +2 ToHitAttack sensor",
                     "Point-blank range, guaranteed-hit beam"],
        edge_cases=["Bonus should appear in ship.fleet_attack_bonus"],
        expected_outcome="fleet_attack_bonus is non-zero on attacker",
        pass_criteria="fleet_attack_bonus == 2.0",
        max_ticks=10,
        seed=STANDARD_SEED,
    )

    attacker_ship = "Test_Attacker_Beam_FleetSensor.json"
    target_ship = "Test_Target_Stationary.json"
    distance = POINT_BLANK_DISTANCE
    force_fire = True

    def validate(self, engine) -> list:
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

        # Outcome: verify bonus is non-zero (firing tested in existing TOHIT-ATK tests)
        checks.append(check_true(
            "Fleet Bonus Non-Zero",
            bonus_val > 0,
            actual=bonus_val,
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
        summary="Per-team modifier from BattleConfig applies to all ships on that team",
        conditions=["Team 0 gets +3 ToHitAttack from external source",
                     "No fleet-scope abilities on ships"],
        edge_cases=["Bonus persists entire battle (not tied to a ship)"],
        expected_outcome="Team 0 ships have fleet_attack_bonus == 3.0",
        pass_criteria="fleet_attack_bonus == 3.0 on team 0 ship",
        max_ticks=10,
        seed=STANDARD_SEED,
    )

    def setup(self, battle_engine):
        from game.simulation.combat.fleet_aura_manager import ExternalModifier

        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        attacker.position = pygame.math.Vector2(0, 0)
        target.position = pygame.math.Vector2(POINT_BLANK_DISTANCE, 0)
        attacker.ai_strategy = 'test_stationary_fire'
        target.ai_strategy = 'test_do_nothing'

        end_condition = self._create_end_condition()
        battle_engine.start([attacker], [target],
                           seed=self.metadata.seed,
                           end_condition=end_condition)

        # Inject external battle condition after engine start
        battle_engine.aura_manager._external.append(
            ExternalModifier(
                ability_name='ToHitAttackModifier',
                value=3.0,
                source_name='System Sensor Array',
                team_id=0,
            )
        )
        battle_engine.aura_manager._recalculate(battle_engine.ships)

        self.attacker = attacker
        self.target = target

    def validate(self, engine) -> list:
        checks = []

        fleet_bonus = getattr(self.attacker, 'fleet_attack_bonus', 0.0)
        checks.append(check_exact(
            "External Bonus Applied",
            3.0,
            fleet_bonus if isinstance(fleet_bonus, (int, float)) else 0.0,
        ))

        return checks
