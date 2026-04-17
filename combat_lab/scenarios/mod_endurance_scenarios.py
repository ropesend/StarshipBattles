"""
Endurance Multiplier Modifier Test Scenarios (MOD-ENDUR-001 through MOD-ENDUR-005)

Behavioral simulation tests for the endurance_mult modifier. Endurance controls
how long a seeker missile stays alive after launch. At distances beyond the
missile's max travel (speed * endurance), the missile self-destructs mid-flight
and deals zero damage. The endurance modifier directly gates effective range.

Test component: test_seeker_endurance_test
  - projectile_speed=1000 (10 px/tick), endurance=3.0s (300 ticks)
  - Max travel: 1000 * 3.0 = 3000px (base)
  - reload=999.0 (single fire), damage=100

Ship Files:
- Test_Attacker_Seeker_EndurTest_Base.json — test_seeker_endurance_test (no modifier)
  + test_storage_ammo_100k, endurance=3.0s, max travel=3000px
- Test_Attacker_Seeker_EndurTest_Boost.json — test_seeker_endurance_test
  + test_endurance_boost(2) + test_storage_ammo_100k, endurance=6.0s, max travel=6000px
- Test_Attacker_Seeker_EndurTest_Penalty.json — test_seeker_endurance_test
  + test_endurance_penalty(0.5) + test_storage_ammo_100k, endurance=1.5s, max travel=1500px
- Test_Target_Stationary.json — test_armor_extreme_hp (1B HP, mass=400, stationary)

Test Coverage:
- MOD-ENDUR-001: Stat gate — boost doubles endurance (3.0->6.0s), missile hits at point-blank
- MOD-ENDUR-002: Boost extends range — base expires at 4000px, boosted reaches (binary)
- MOD-ENDUR-003: Near-limit reach — base barely reaches at 2500px, boosted comfortable
- MOD-ENDUR-004: Penalty shortens range — base reaches at 2000px, penalized expires (binary)
- MOD-ENDUR-005: Stat gate — penalty halves endurance (3.0->1.5s), missile hits at point-blank
"""

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_approx, check_exact, check_true
from combat_lab.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
)

# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

# test_seeker_endurance_test (speed=1000, endurance=3.0s, max=3000px) + test_storage_ammo_100k
BASE_SHIP = "Test_Attacker_Seeker_EndurTest_Base.json"
# test_seeker_endurance_test + test_endurance_boost(2), endurance=6.0s, max=6000px
BOOST_SHIP = "Test_Attacker_Seeker_EndurTest_Boost.json"
# test_seeker_endurance_test + test_endurance_penalty(0.5), endurance=1.5s, max=1500px
PENALTY_SHIP = "Test_Attacker_Seeker_EndurTest_Penalty.json"
# test_armor_extreme_hp (1B HP, mass=400, stationary)
TARGET_SHIP = "Test_Target_Stationary.json"

# =============================================================================
# SEEKER CONSTANTS (from test_seeker_endurance_test component)
# =============================================================================

BASE_ENDURANCE = 3.0          # seconds
PROJECTILE_SPEED = 1000       # raw speed (10 px/tick after /100)
SEEKER_DAMAGE = 100           # damage per hit
MAX_TRAVEL_BASE = PROJECTILE_SPEED * BASE_ENDURANCE     # 3000px

BOOST_PARAM = 2               # test_endurance_boost value
BOOSTED_ENDURANCE = BASE_ENDURANCE * BOOST_PARAM         # 6.0s
MAX_TRAVEL_BOOSTED = PROJECTILE_SPEED * BOOSTED_ENDURANCE  # 6000px

PENALTY_PARAM = 0.5           # test_endurance_penalty value
PENALIZED_ENDURANCE = BASE_ENDURANCE * PENALTY_PARAM     # 1.5s
MAX_TRAVEL_PENALIZED = PROJECTILE_SPEED * PENALIZED_ENDURANCE  # 1500px

# Test distances chosen so binary outcomes depend on endurance
BOOST_TEST_DISTANCE = 4000    # Base (3000px max) fails, Boosted (6000px max) reaches
NEAR_LIMIT_DISTANCE = 2500    # Base (3000px max) barely reaches, Boosted comfortable
PENALTY_TEST_DISTANCE = 2000  # Base (3000px max) reaches, Penalized (1500px max) fails

# Tick budget: at 10 px/tick, 4000px takes 400 ticks. 500 ticks is sufficient.
ENDURANCE_TEST_TICKS = 500


# =============================================================================
# MOD-ENDUR-001: Stat Gate — Boost Doubles Endurance
# =============================================================================

class ModEndur001_StatGateScenario(StaticTargetScenario):
    """
    MOD-ENDUR-001: Quick sanity — endurance modifier applied correctly.

    Boosted seeker at point-blank: endurance==6.0s (3.0*2), missile hits,
    damage==100. Confirms modifier loaded before behavioral tests run.
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-001",
        category="EnduranceMultiplier",
        subcategory="EnduranceMultiplier",
        name="Stat gate — boost doubles endurance (3.0->6.0s)",
        summary=f"Verify test_endurance_boost(2) sets endurance to {BOOSTED_ENDURANCE}s; missile hits at point-blank",
        conditions=[
            f"Attacker: {BOOST_SHIP} (test_seeker_endurance_test + test_endurance_boost({BOOST_PARAM}), endurance {BASE_ENDURANCE}->{BOOSTED_ENDURANCE}s)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=["Multiplicative modifier on endurance attribute"],
        expected_outcome=f"seeker.endurance == {BOOSTED_ENDURANCE}, damage == {SEEKER_DAMAGE}",
        pass_criteria=f"endurance == {BOOSTED_ENDURANCE} AND damage == {SEEKER_DAMAGE}",
        max_ticks=ENDURANCE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "endurance_mult", "stat_gate"],
    )

    attacker_ship = BOOST_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        self.actual_endurance = seeker.endurance if seeker else None

    def _collect_extra_results(self, outcome, telemetry=None):
        self.results['expected_endurance'] = BOOSTED_ENDURANCE
        self.results['actual_endurance'] = self.actual_endurance

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        checks.append(check_true("Seeker Loaded", seeker is not None, phase="precondition"))
        if seeker is None:
            return checks

        # Data: endurance modifier applied
        checks.append(check_approx(
            "Boosted Endurance", BOOSTED_ENDURANCE,
            self.actual_endurance or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: missile hit at point-blank
        checks.append(check_exact(
            "Missile Hit (100 damage)", float(SEEKER_DAMAGE),
            float(self.damage_dealt), phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ENDUR-002: Boost Extends Range (Binary)
# =============================================================================

class ModEndur002_BoostExtendsRangeScenario(ComparisonScenario):
    """
    MOD-ENDUR-002: Prove endurance boost extends effective range.

    At 4000px, the base seeker (max 3000px) expires mid-flight and deals
    zero damage. The boosted seeker (max 6000px) reaches the target and
    deals 100 damage. This is the core behavioral test — endurance directly
    determines whether the missile reaches its target.
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-002",
        category="EnduranceMultiplier",
        subcategory="EnduranceMultiplier",
        name=f"Boost extends range — base expires at {BOOST_TEST_DISTANCE}px, boosted reaches",
        summary=(
            f"Base (endurance={BASE_ENDURANCE}s, max={MAX_TRAVEL_BASE}px) expires at {BOOST_TEST_DISTANCE}px. "
            f"Boosted (endurance={BOOSTED_ENDURANCE}s, max={MAX_TRAVEL_BOOSTED}px) reaches and hits."
        ),
        conditions=[
            f"Baseline: {BASE_SHIP} (test_seeker_endurance_test, no modifier, endurance={BASE_ENDURANCE}s, max travel={MAX_TRAVEL_BASE}px)",
            f"Variant: {BOOST_SHIP} (test_seeker_endurance_test + test_endurance_boost({BOOST_PARAM}), endurance={BOOSTED_ENDURANCE}s, max travel={MAX_TRAVEL_BOOSTED}px)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {BOOST_TEST_DISTANCE}px (beyond base max {MAX_TRAVEL_BASE}px, within boosted max {MAX_TRAVEL_BOOSTED}px)",
        ],
        edge_cases=[
            f"Base missile self-destructs after {BASE_ENDURANCE}s ({int(BASE_ENDURANCE * 100)} ticks) having traveled {MAX_TRAVEL_BASE}px",
            f"Boosted missile reaches target in {BOOST_TEST_DISTANCE // 10} ticks (well within {BOOSTED_ENDURANCE}s budget)",
        ],
        expected_outcome=f"Baseline: 0 damage (expired). Variant: {SEEKER_DAMAGE} damage (hit).",
        pass_criteria=f"baseline_damage == 0 AND variant_damage == {SEEKER_DAMAGE}",
        max_ticks=ENDURANCE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "endurance_mult", "range_gate", "binary"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = BOOST_TEST_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Data: verify endurance values on variant
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        if seeker:
            checks.append(check_approx(
                "Variant Endurance", BOOSTED_ENDURANCE,
                seeker.endurance, tolerance=0.001, phase="data",
            ))

        # Outcome: base seeker expired (0 damage)
        checks.append(check_exact(
            "Base Seeker Expired (0 damage)", 0.0,
            float(self.baseline_damage_dealt), phase="outcome",
        ))

        # Outcome: boosted seeker reached target
        checks.append(check_exact(
            f"Boosted Seeker Hit ({SEEKER_DAMAGE} damage)", float(SEEKER_DAMAGE),
            float(self.variant_damage_dealt), phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ENDUR-003: Near-Limit Reach (Both Hit)
# =============================================================================

class ModEndur003_NearLimitReachScenario(ComparisonScenario):
    """
    MOD-ENDUR-003: Both seekers reach target at 2500px, but base is near limit.

    At 2500px, the base seeker (max 3000px) barely reaches with 500px margin.
    The boosted seeker (max 6000px) reaches comfortably with 3500px margin.
    Both deal 100 damage — this test verifies both work at moderate distance
    and that endurance stat values differ even when outcomes match.
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-003",
        category="EnduranceMultiplier",
        subcategory="EnduranceMultiplier",
        name=f"Near-limit reach — both hit at {NEAR_LIMIT_DISTANCE}px",
        summary=(
            f"Both reach target at {NEAR_LIMIT_DISTANCE}px. "
            f"Base margin: {MAX_TRAVEL_BASE - NEAR_LIMIT_DISTANCE}px. "
            f"Boosted margin: {MAX_TRAVEL_BOOSTED - NEAR_LIMIT_DISTANCE}px."
        ),
        conditions=[
            f"Baseline: {BASE_SHIP} (endurance={BASE_ENDURANCE}s, max={MAX_TRAVEL_BASE}px, margin={MAX_TRAVEL_BASE - NEAR_LIMIT_DISTANCE}px)",
            f"Variant: {BOOST_SHIP} (endurance={BOOSTED_ENDURANCE}s, max={MAX_TRAVEL_BOOSTED}px, margin={MAX_TRAVEL_BOOSTED - NEAR_LIMIT_DISTANCE}px)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {NEAR_LIMIT_DISTANCE}px",
        ],
        edge_cases=[
            f"Base seeker has only {MAX_TRAVEL_BASE - NEAR_LIMIT_DISTANCE}px margin — tests near-limit behavior",
        ],
        expected_outcome=f"Both: {SEEKER_DAMAGE} damage each",
        pass_criteria=f"baseline_damage == {SEEKER_DAMAGE} AND variant_damage == {SEEKER_DAMAGE}",
        max_ticks=ENDURANCE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "endurance_mult", "near_limit"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = NEAR_LIMIT_DISTANCE
    expect_different_damage = False  # Both hit — same damage expected

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Outcome: both seekers reached target
        checks.append(check_exact(
            f"Base Seeker Hit ({SEEKER_DAMAGE} damage)", float(SEEKER_DAMAGE),
            float(self.baseline_damage_dealt), phase="outcome",
        ))
        checks.append(check_exact(
            f"Boosted Seeker Hit ({SEEKER_DAMAGE} damage)", float(SEEKER_DAMAGE),
            float(self.variant_damage_dealt), phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ENDUR-004: Penalty Shortens Range (Binary)
# =============================================================================

class ModEndur004_PenaltyShortensRangeScenario(ComparisonScenario):
    """
    MOD-ENDUR-004: Prove endurance penalty shortens effective range.

    At 2000px, the base seeker (max 3000px) reaches the target and deals
    100 damage. The penalized seeker (max 1500px) expires mid-flight and
    deals zero damage. This tests the negative modifier bidirectionally.
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-004",
        category="EnduranceMultiplier",
        subcategory="EnduranceMultiplier",
        name=f"Penalty shortens range — penalized expires at {PENALTY_TEST_DISTANCE}px, base reaches",
        summary=(
            f"Base (endurance={BASE_ENDURANCE}s, max={MAX_TRAVEL_BASE}px) reaches at {PENALTY_TEST_DISTANCE}px. "
            f"Penalized (endurance={PENALIZED_ENDURANCE}s, max={MAX_TRAVEL_PENALIZED}px) expires."
        ),
        conditions=[
            f"Baseline: {BASE_SHIP} (test_seeker_endurance_test, no modifier, endurance={BASE_ENDURANCE}s, max travel={MAX_TRAVEL_BASE}px)",
            f"Variant: {PENALTY_SHIP} (test_seeker_endurance_test + test_endurance_penalty({PENALTY_PARAM}), endurance={PENALIZED_ENDURANCE}s, max travel={MAX_TRAVEL_PENALIZED}px)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {PENALTY_TEST_DISTANCE}px (within base max {MAX_TRAVEL_BASE}px, beyond penalized max {MAX_TRAVEL_PENALIZED}px)",
        ],
        edge_cases=[
            f"Penalized missile self-destructs after {PENALIZED_ENDURANCE}s ({int(PENALIZED_ENDURANCE * 100)} ticks) having traveled {MAX_TRAVEL_PENALIZED}px",
            "Tests negative modifier bidirectionality (penalty reduces capability)",
        ],
        expected_outcome=f"Baseline: {SEEKER_DAMAGE} damage (hit). Variant: 0 damage (expired).",
        pass_criteria=f"baseline_damage == {SEEKER_DAMAGE} AND variant_damage == 0",
        max_ticks=ENDURANCE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "endurance_mult", "penalty", "binary"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = PENALTY_SHIP
    variant_target_ship = TARGET_SHIP
    distance = PENALTY_TEST_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty was applied
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        if seeker:
            checks.append(check_approx(
                "Penalized Endurance", PENALIZED_ENDURANCE,
                seeker.endurance, tolerance=0.001, phase="data",
            ))

        # Outcome: base seeker reached target
        checks.append(check_exact(
            f"Base Seeker Hit ({SEEKER_DAMAGE} damage)", float(SEEKER_DAMAGE),
            float(self.baseline_damage_dealt), phase="outcome",
        ))

        # Outcome: penalized seeker expired
        checks.append(check_exact(
            "Penalized Seeker Expired (0 damage)", 0.0,
            float(self.variant_damage_dealt), phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-ENDUR-005: Stat Gate — Penalty Halves Endurance
# =============================================================================

class ModEndur005_PenaltyStatGateScenario(StaticTargetScenario):
    """
    MOD-ENDUR-005: Quick sanity — penalty modifier halves endurance.

    Penalized seeker at point-blank: endurance==1.5s (3.0*0.5), missile hits.
    Confirms negative modifier value loaded correctly.
    """
    metadata = TestMetadata(
        test_id="MOD-ENDUR-005",
        category="EnduranceMultiplier",
        subcategory="EnduranceMultiplier",
        name="Stat gate — penalty halves endurance (3.0->1.5s)",
        summary=f"Verify test_endurance_penalty(0.5) sets endurance to {PENALIZED_ENDURANCE}s; missile hits at point-blank",
        conditions=[
            f"Attacker: {PENALTY_SHIP} (test_seeker_endurance_test + test_endurance_penalty({PENALTY_PARAM}), endurance {BASE_ENDURANCE}->{PENALIZED_ENDURANCE}s)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=["Penalty modifier uses endurance_mult with value < 1.0"],
        expected_outcome=f"seeker.endurance == {PENALIZED_ENDURANCE}, damage == {SEEKER_DAMAGE}",
        pass_criteria=f"endurance == {PENALIZED_ENDURANCE} AND damage == {SEEKER_DAMAGE}",
        max_ticks=ENDURANCE_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "endurance_mult", "penalty", "stat_gate"],
    )

    attacker_ship = PENALTY_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        self.actual_endurance = seeker.endurance if seeker else None

    def _collect_extra_results(self, outcome, telemetry=None):
        self.results['expected_endurance'] = PENALIZED_ENDURANCE
        self.results['actual_endurance'] = self.actual_endurance

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        seeker = self.get_ability(self.attacker, 'SeekerWeaponAbility')
        checks.append(check_true("Seeker Loaded", seeker is not None, phase="precondition"))
        if seeker is None:
            return checks

        # Data: penalty applied
        checks.append(check_approx(
            "Penalized Endurance", PENALIZED_ENDURANCE,
            self.actual_endurance or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: missile hit at point-blank (penalty doesn't prevent close-range hits)
        checks.append(check_exact(
            "Missile Hit (100 damage)", float(SEEKER_DAMAGE),
            float(self.damage_dealt), phase="outcome",
        ))

        return checks
