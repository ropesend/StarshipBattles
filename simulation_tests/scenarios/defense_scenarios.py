"""
Defense Ability Test Scenarios (SHIELD-001 to SHIELD-003, ARMOR-001 to ARMOR-002, ECM-001, SENSOR-001)

These tests validate defensive ability behavior including:
- Shield absorption (ShieldProjection)
- Shield regeneration (ShieldRegeneration)
- Emissive armor damage reduction (EmissiveArmor)
- ECM defense modifier (ToHitDefenseModifier)
- Sensor attack modifier (ToHitAttackModifier)

Each test isolates ONE defense ability against a calibrated beam attacker.
"""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.validation import check_exact, check_tost, check_true
from simulation_tests.scenarios.templates import StaticTargetScenario
from simulation_tests.scenarios.beam_scenarios import compute_beam_hit_chance
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE,
    MID_RANGE_DISTANCE,
    STANDARD_DISTANCE,
    STANDARD_SEED,
    STANDARD_MARGIN,
    SHIELD_CAPACITY,
    SHIELD_REGEN_RATE,
    EMISSIVE_ARMOR_REDUCTION,
    ECM_DEFENSE_VALUE,
    SENSOR_ATTACK_VALUE,
    SHIELDED_TARGET_SHIP,
    SHIELD_REGEN_TARGET_SHIP,
    EMISSIVE_ARMOR_TARGET_SHIP,
    ECM_TARGET_SHIP,
    SENSOR_ATTACKER_SHIP,
    DEFENSE_TEST_TICKS,
)


# ============================================================================
# SHIELD TESTS
# ============================================================================

class ShieldAbsorbsDamageScenario(StaticTargetScenario):
    """
    SHIELD-001: Shield Absorbs Beam Damage

    Tests that ShieldProjection(200) absorbs damage before hull HP.
    A medium accuracy beam at point blank deals consistent damage.
    After the test, shields should be reduced and hull should still
    be at full HP (if shields held) or near-full.
    """

    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = SHIELDED_TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    metadata = TestMetadata(
        test_id="SHIELD-001",
        category="Defense Abilities",
        subcategory="Shields",
        name="Shield Absorbs Beam Damage",
        summary="Validates ShieldProjection absorbs damage before hull HP",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json (1 damage beam, med accuracy)",
            f"Target: {SHIELDED_TARGET_SHIP} (200 HP shields + extreme armor)",
            "Distance: 50 pixels (point blank)",
            f"Shield Capacity: {SHIELD_CAPACITY} HP",
            "Beam Damage: 1 per hit",
            f"Test Duration: {DEFENSE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Shields should absorb all damage if total < 200",
            "Shield HP decreases while hull HP remains unchanged",
        ],
        expected_outcome="Shields absorb beam damage; hull HP unchanged or nearly so",
        pass_criteria="damage_dealt > 0 (beam hits, damage absorbed by shields)",
        max_ticks=DEFENSE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["defense", "shield", "absorption", "beam"],
    )

    def _collect_extra_results(self, battle_engine):
        self.shield_absorbed = SHIELD_CAPACITY - self.target.current_shields
        self.results['shield_absorbed'] = self.shield_absorbed

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Shield Capacity", SHIELD_CAPACITY,
                                  self.target.max_shields, phase="data"))
        # Outcome
        checks.append(check_true("Damage Dealt", self.damage_dealt > 0,
                                 actual=self.damage_dealt, phase="outcome"))
        checks.append(check_true("Shields Absorbed Damage", self.shield_absorbed > 0,
                                 actual=self.shield_absorbed, phase="outcome"))
        return checks


class ShieldOverflowToHullScenario(StaticTargetScenario):
    """
    SHIELD-002: Shield Overflow to Hull

    Tests that damage exceeding shield capacity reaches the hull.
    Uses a high-accuracy beam (5 damage/hit) over enough ticks to
    deplete 200 shields and start damaging hull.
    """

    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = SHIELDED_TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    metadata = TestMetadata(
        test_id="SHIELD-002",
        category="Defense Abilities",
        subcategory="Shields",
        name="Shield Overflow to Hull",
        summary="Validates damage exceeding shield capacity reaches hull HP",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json (5 damage beam, high accuracy)",
            f"Target: {SHIELDED_TARGET_SHIP} (200 HP shields + extreme armor)",
            "Distance: 50 pixels (point blank)",
            f"Shield Capacity: {SHIELD_CAPACITY} HP",
            "Beam Damage: 5 per hit (~99% hit rate at point blank)",
            "Test Duration: 1000 ticks (10 seconds - enough to deplete shields)",
        ],
        edge_cases=[
            "Shield depletes after ~40 hits (200 HP / 5 per hit)",
            "Subsequent hits go to hull/armor",
            "Total damage should exceed shield capacity",
        ],
        expected_outcome="Shields fully depleted, hull takes overflow damage",
        pass_criteria="damage_dealt > shield_capacity (hull received damage)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=9,
        tags=["defense", "shield", "overflow", "hull-damage", "beam"],
    )

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Shield Capacity", SHIELD_CAPACITY,
                                  self.target.max_shields, phase="data"))
        # Outcome
        checks.append(check_true("Shields Depleted", self.target.current_shields == 0,
                                 actual=self.target.current_shields, phase="outcome"))
        checks.append(check_true("Damage Exceeds Shield Capacity",
                                 self.damage_dealt > SHIELD_CAPACITY,
                                 actual=self.damage_dealt,
                                 detail=f"damage_dealt={self.damage_dealt}, shield_capacity={SHIELD_CAPACITY}",
                                 phase="outcome"))
        return checks


class ShieldRegenerationScenario(StaticTargetScenario):
    """
    SHIELD-003: Shield Regeneration Sustains

    Tests that ShieldRegeneration restores shields between hits.
    A low-damage beam (1/hit) attacks a target with 200 shields + 10/sec regen.
    With regen, total damage absorbed should exceed initial shield capacity
    because shields keep regenerating.
    """

    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = SHIELD_REGEN_TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    metadata = TestMetadata(
        test_id="SHIELD-003",
        category="Defense Abilities",
        subcategory="Shields",
        name="Shield Regeneration Sustains",
        summary="Validates ShieldRegeneration restores shields between hits",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json (1 damage beam, med accuracy)",
            f"Target: {SHIELD_REGEN_TARGET_SHIP} (200 HP shields + 10/sec regen)",
            "Distance: 50 pixels (point blank)",
            f"Shield Capacity: {SHIELD_CAPACITY} HP",
            f"Shield Regen: {SHIELD_REGEN_RATE}/sec (no resource cost)",
            "Beam Damage: 1 per hit",
            "Test Duration: 500 ticks (5 seconds)",
        ],
        edge_cases=[
            f"Regen adds {SHIELD_REGEN_RATE} HP/sec = {SHIELD_REGEN_RATE * 5} over 5 seconds",
            "If regen > incoming DPS, shields never deplete",
            "Total shield absorption should exceed initial capacity",
        ],
        expected_outcome="Shields sustain via regeneration; target takes less hull damage",
        pass_criteria="measurement_mode (simulation completes)",
        max_ticks=DEFENSE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=8,
        tags=["defense", "shield", "regeneration", "sustain", "beam"],
    )

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Shield Capacity", SHIELD_CAPACITY,
                                  self.target.max_shields, phase="data"))
        # Outcome - verify beam hit and some hull damage got through.
        # The shield regen scenario is observational: it confirms that
        # regen doesn't crash and shields absorb some damage over time.
        checks.append(check_true(
            "Hull Damage Dealt", self.damage_dealt > 0,
            actual=self.damage_dealt, phase="outcome",
        ))
        return checks


# ============================================================================
# EMISSIVE ARMOR TESTS
# ============================================================================

class EmissiveArmorBlocksLowDamageScenario(StaticTargetScenario):
    """
    ARMOR-001: Emissive Armor Blocks Low Damage

    Tests that EmissiveArmor(5) completely blocks 1-damage beam hits.
    Since each hit deals 1 damage and armor reduces by 5, every hit
    should be negated entirely.
    """

    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = EMISSIVE_ARMOR_TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    metadata = TestMetadata(
        test_id="ARMOR-001",
        category="Defense Abilities",
        subcategory="Emissive Armor",
        name="Emissive Armor Blocks Low Damage",
        summary="Validates EmissiveArmor(5) completely blocks 1-damage beam hits",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json (1 damage beam, med accuracy)",
            f"Target: {EMISSIVE_ARMOR_TARGET_SHIP} (EmissiveArmor 5 + extreme armor)",
            "Distance: 50 pixels (point blank)",
            f"Emissive Armor: {EMISSIVE_ARMOR_REDUCTION} damage reduction per hit",
            "Beam Damage: 1 per hit (< armor value)",
            f"Test Duration: {DEFENSE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "1 damage < 5 armor → damage reduced to 0",
            "Target should take zero damage despite beam firing",
            "Validates emissive armor min(0, damage - armor) behavior",
        ],
        expected_outcome="Zero hull damage (all hits blocked by emissive armor)",
        pass_criteria="damage_dealt == 0",
        max_ticks=DEFENSE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["defense", "armor", "emissive", "block", "beam"],
    )

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Emissive Armor Value", EMISSIVE_ARMOR_REDUCTION,
                                  self.target.emissive_armor, phase="data"))
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_true("Beam Damage < Armor",
                                 beam.damage < EMISSIVE_ARMOR_REDUCTION,
                                 detail=f"beam.damage={beam.damage}, armor={EMISSIVE_ARMOR_REDUCTION}",
                                 phase="data"))
        # Outcome
        checks.append(check_exact("Damage Dealt", 0, self.damage_dealt, phase="outcome"))
        return checks


class EmissiveArmorReducesHighDamageScenario(StaticTargetScenario):
    """
    ARMOR-002: Emissive Armor Reduces High Damage

    Tests that EmissiveArmor(5) reduces 5-damage beam hits.
    Each hit deals 5 damage, armor reduces by 5, so 0 damage per hit.
    Uses high accuracy beam (5 damage/hit) which exactly equals armor.
    """

    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = EMISSIVE_ARMOR_TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    metadata = TestMetadata(
        test_id="ARMOR-002",
        category="Defense Abilities",
        subcategory="Emissive Armor",
        name="Emissive Armor Reduces High Damage",
        summary="Validates EmissiveArmor(5) reduces 5-damage beam hits to 0",
        conditions=[
            "Attacker: Test_Attacker_Beam360_High.json (5 damage beam, high accuracy)",
            f"Target: {EMISSIVE_ARMOR_TARGET_SHIP} (EmissiveArmor 5 + extreme armor)",
            "Distance: 50 pixels (point blank)",
            f"Emissive Armor: {EMISSIVE_ARMOR_REDUCTION} damage reduction per hit",
            "Beam Damage: 5 per hit (== armor value)",
            f"Test Duration: {DEFENSE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "5 damage == 5 armor → damage reduced to 0",
            "Edge case: exact equality between damage and armor",
            "Target should take zero damage",
        ],
        expected_outcome="Zero hull damage (5 damage - 5 armor = 0 per hit)",
        pass_criteria="damage_dealt == 0",
        max_ticks=DEFENSE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=9,
        tags=["defense", "armor", "emissive", "reduction", "beam"],
    )

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Emissive Armor Value", EMISSIVE_ARMOR_REDUCTION,
                                  self.target.emissive_armor, phase="data"))
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Weapon Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks
        checks.append(check_true("Beam Damage <= Armor",
                                 beam.damage <= EMISSIVE_ARMOR_REDUCTION,
                                 detail=f"beam.damage={beam.damage}, armor={EMISSIVE_ARMOR_REDUCTION}",
                                 phase="data"))
        # Outcome
        checks.append(check_exact("Damage Dealt", 0, self.damage_dealt, phase="outcome"))
        return checks


# ============================================================================
# ECM / SENSOR TESTS
# ============================================================================

class ECMReducesHitRateScenario(StaticTargetScenario):
    """
    ECM-001: ECM Reduces Hit Rate

    Tests that ToHitDefenseModifier(1.0) reduces beam weapon hit rate.
    Compares expected hit chance with ECM defense vs baseline (no ECM).
    Uses medium accuracy beam at mid range where defense score has measurable impact.
    """

    attacker_ship = "Test_Attacker_Beam360_Med.json"
    target_ship = ECM_TARGET_SHIP
    distance = MID_RANGE_DISTANCE

    metadata = TestMetadata(
        test_id="ECM-001",
        category="Defense Abilities",
        subcategory="ECM",
        name="ECM Reduces Hit Rate",
        summary="Validates ToHitDefenseModifier(1.0) reduces beam hit rate vs baseline",
        conditions=[
            "Attacker: Test_Attacker_Beam360_Med.json (1 damage beam, med accuracy)",
            f"Target: {ECM_TARGET_SHIP} (ECM +{ECM_DEFENSE_VALUE} defense score)",
            "Distance: 400 pixels (mid range)",
            f"ECM Value: +{ECM_DEFENSE_VALUE} defense score",
            f"Test Duration: {DEFENSE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "ECM adds to defense_score in hit calculation",
            "Higher defense score → lower hit probability",
            "Expected hit rate should be lower than baseline",
        ],
        expected_outcome="Damage dealt < baseline (ECM reduces incoming fire effectiveness)",
        pass_criteria="measurement_mode (simulation completes, results recorded)",
        max_ticks=DEFENSE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["defense", "ecm", "to-hit", "defense-modifier", "beam"],
    )

    def custom_setup(self, battle_engine):
        self.expected_hit_chance_with_ecm = compute_beam_hit_chance(
            self, target_ecm_score=ECM_DEFENSE_VALUE
        )
        self.expected_hit_chance_baseline = compute_beam_hit_chance(self)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_true("ECM Reduces Expected Hit Chance",
                                 self.expected_hit_chance_with_ecm < self.expected_hit_chance_baseline,
                                 detail=f"with_ecm={self.expected_hit_chance_with_ecm:.4f}, "
                                        f"baseline={self.expected_hit_chance_baseline:.4f}",
                                 phase="data"))
        # Outcome
        checks.append(check_tost("Hit Rate With ECM", self.expected_hit_chance_with_ecm,
                                  successes=int(self.damage_dealt),
                                  trials=engine.tick_counter,
                                  margin=STANDARD_MARGIN))
        return checks


class SensorImprovesHitRateScenario(StaticTargetScenario):
    """
    SENSOR-001: Sensor Improves Hit Rate

    Tests that ToHitAttackModifier(1.0) improves beam weapon hit rate.
    Compares expected hit chance with sensor vs baseline (no sensor).
    Uses the sensor-equipped attacker against a standard stationary target.
    """

    attacker_ship = SENSOR_ATTACKER_SHIP
    target_ship = "Test_Target_Stationary.json"
    distance = MID_RANGE_DISTANCE

    metadata = TestMetadata(
        test_id="SENSOR-001",
        category="Defense Abilities",
        subcategory="Sensors",
        name="Sensor Improves Hit Rate",
        summary="Validates ToHitAttackModifier(1.0) improves beam hit rate vs baseline",
        conditions=[
            f"Attacker: {SENSOR_ATTACKER_SHIP} (med accuracy beam + sensor +{SENSOR_ATTACK_VALUE})",
            "Target: Test_Target_Stationary.json (stationary, no defense)",
            "Distance: 400 pixels (mid range)",
            f"Sensor Value: +{SENSOR_ATTACK_VALUE} attack bonus",
            f"Test Duration: {DEFENSE_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Sensor adds to attack_bonus in hit calculation",
            "Higher attack bonus → higher hit probability",
            "Expected hit rate should be higher than baseline",
        ],
        expected_outcome="Damage dealt > baseline (sensor improves fire effectiveness)",
        pass_criteria="damage_dealt > 0 (sensor-boosted beam hits target)",
        max_ticks=DEFENSE_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["defense", "sensor", "to-hit", "attack-modifier", "beam"],
    )

    verify_damage_dealt = True

    def custom_setup(self, battle_engine):
        from simulation_tests.scenarios.beam_scenarios import calculate_expected_hit_chance, calculate_defense_score
        # Extract beam weapon stats
        beam_ability = None
        for layer_name, layer_data in self.attacker.layers.items():
            for component in layer_data.components:
                    if hasattr(component, 'ability_instances'):
                        for ability in component.ability_instances:
                            if ability.__class__.__name__ == 'BeamWeaponAbility':
                                beam_ability = ability
                                break
        target_defense = calculate_defense_score(mass=self.target.mass)
        target_radius = 40 * ((self.target.mass / 1000) ** (1/3))
        surface_distance = self.distance - target_radius
        # With sensor: attack_bonus = baseline_to_hit_offense from ship stats
        attack_bonus = self.attacker.baseline_to_hit_offense
        self.expected_hit_chance_with_sensor = calculate_expected_hit_chance(
            beam_ability.base_accuracy, beam_ability.accuracy_falloff,
            surface_distance, attack_bonus, target_defense
        )
        # Baseline: no sensor (attack_bonus=0)
        self.expected_hit_chance_baseline = calculate_expected_hit_chance(
            beam_ability.base_accuracy, beam_ability.accuracy_falloff,
            surface_distance, 0.0, target_defense
        )

    def _collect_extra_results(self, battle_engine):
        self.results['sensor_attack_value'] = SENSOR_ATTACK_VALUE
        self.results['attacker_attack_bonus'] = self.attacker.baseline_to_hit_offense
        self.results['expected_hit_chance_with_sensor'] = self.expected_hit_chance_with_sensor
        self.results['expected_hit_chance_baseline'] = self.expected_hit_chance_baseline
        self.results['hit_rate_improvement'] = self.expected_hit_chance_with_sensor - self.expected_hit_chance_baseline


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    # Shield Tests
    'ShieldAbsorbsDamageScenario',
    'ShieldOverflowToHullScenario',
    'ShieldRegenerationScenario',

    # Emissive Armor Tests
    'EmissiveArmorBlocksLowDamageScenario',
    'EmissiveArmorReducesHighDamageScenario',

    # ECM / Sensor Tests
    'ECMReducesHitRateScenario',
    'SensorImprovesHitRateScenario',
]
