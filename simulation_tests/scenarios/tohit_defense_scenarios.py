"""
ToHitDefenseModifier Test Scenarios (TOHIT-DEF-001 to TOHIT-DEF-004)

These tests validate the ToHitDefenseModifier ability using A/B comparison
battles.  Each test uses the same attacker (low accuracy beam, no sensor)
and varies the TARGET to test the defense modifier.

Stacking rules (inter-group SUM, intra-group MAX):
- Same stack_group: only the highest value counts (redundancy)
- Different stack_groups: values are summed (stacking)
- No stack_group: each component is its own group (all stack)

All tests use the low-accuracy beam (base_accuracy=0.5, falloff=0.002)
at mid-range (400px).  With damage=1 per hit and no reload,
damage_dealt equals the number of hits.

Expected hit rates (target defense_score=0.332 from size + ECM bonus):
- No ECM:                 36.1%  (size_defense only)
- +1.0 ECM:               17.2%  (ECM reduces hit rate)
- +1.0 ECM same group x2: 17.2%  (MAX=1.0, no change)
- +1.0 ECM diff groups:    7.1%  (SUM=2.0)
- -0.5 ECM penalty:       48.2%  (penalty makes target easier to hit)
"""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.templates import ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_tost, check_true
from simulation_tests.test_constants import (
    MID_RANGE_DISTANCE,
    STANDARD_SEED,
    STANDARD_MARGIN,
    ECM_DEFENSE_VALUE,
    ECM_PENALTY_VALUE,
    BEAM_LOW_ACCURACY,
    BEAM_LOW_FALLOFF,
)


# =============================================================================
# EXPECTED VALUES
# =============================================================================
# Beam: base_accuracy=0.5, falloff=0.002, no sensor (attack_bonus=0)
# Target: mass=400, radius=29.47px, stationary
# Surface distance: 400 - 29.47 = 370.53px
# Range penalty: 0.002 * 370.53 = 0.7411
# Size defense: 0.3316

TOHIT_DEF_TEST_TICKS = 1000
TOHIT_DEF_BASELINE_HIT_RATE = 0.3606       # sigmoid(-0.5727) — no ECM
TOHIT_DEF_ECM_HIT_RATE = 0.1718            # sigmoid(-1.5727) — +1.0 ECM
TOHIT_DEF_DOUBLE_ECM_HIT_RATE = 0.0709     # sigmoid(-2.5727) — +2.0 ECM
TOHIT_DEF_PENALTY_HIT_RATE = 0.4818        # sigmoid(-0.0727) — -0.5 penalty

# Common attacker for all defense tests (low accuracy beam, no modifiers)
TOHIT_DEF_ATTACKER = "Test_Attacker_Beam360_Low.json"


# =============================================================================
# TOHIT-DEF-001: ECM Reduces Hit Rate
# =============================================================================

class ECMReducesHitRateComparisonScenario(ComparisonScenario):
    """
    TOHIT-DEF-001: ECM Reduces Hit Rate

    Battle A: Target with no ECM → ~36% hit rate
    Battle B: Target with ToHitDefenseModifier(1.0) → ~17% hit rate

    Proves that the ToHitDefenseModifier ability reduces the attacker's
    hit probability by increasing the target's defense score.
    """

    metadata = TestMetadata(
        test_id="TOHIT-DEF-001",
        category="ToHitDefenseModifier",
        subcategory="Basic Effect",
        name="ECM Reduces Hit Rate",
        summary="Compares measured hit rate against undefended vs ECM-equipped target",
        conditions=[
            f"Attacker: {TOHIT_DEF_ATTACKER} (low accuracy beam, no sensor)",
            "Target (no ECM): Test_Target_Stationary.json",
            "Target (with ECM): Test_Target_ECM.json (+1.0 defense bonus)",
            f"Distance: {MID_RANGE_DISTANCE} pixels (mid range)",
            f"Beam: base_accuracy={BEAM_LOW_ACCURACY}, falloff={BEAM_LOW_FALLOFF}",
            f"Test Duration: {TOHIT_DEF_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "ECM bonus adds to defense_score which is subtracted in sigmoid",
            "Both battles use identical seed for fair comparison",
        ],
        expected_outcome=f"No ECM ~{TOHIT_DEF_BASELINE_HIT_RATE:.0%}, "
                         f"With ECM ~{TOHIT_DEF_ECM_HIT_RATE:.0%}",
        pass_criteria="ECM target takes less damage than undefended target",
        max_ticks=TOHIT_DEF_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "ecm", "defense-modifier", "comparison"],
    )

    baseline_attacker_ship = TOHIT_DEF_ATTACKER
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = TOHIT_DEF_ATTACKER
    variant_target_ship = "Test_Target_ECM.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify ECM is present on variant target
        ecm = self.get_ability(self.target, 'ToHitDefenseModifier')
        checks.append(check_exact(
            "ECM Defense Value", ECM_DEFENSE_VALUE,
            ecm.value if ecm else 0.0,
        ))

        # Precondition: undefended target took damage
        checks.append(check_true(
            "Undefended Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: ECM reduces measured damage
        checks.append(check_true(
            "ECM Reduces Damage Taken",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"no_ecm={self.baseline_damage_dealt}, "
                   f"with_ecm={self.variant_damage_dealt}, "
                   f"reduction={self.baseline_damage_dealt - self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Statistical: hit rates match expected values
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_tost(
            "Hit Rate (no ECM)",
            TOHIT_DEF_BASELINE_HIT_RATE,
            int(self.baseline_damage_dealt),
            baseline_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))
        checks.append(check_tost(
            "Hit Rate (with ECM)",
            TOHIT_DEF_ECM_HIT_RATE,
            int(self.variant_damage_dealt),
            variant_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-DEF-002: Same Stacking Group Does Not Stack
# =============================================================================

class ECMSameGroupDoesNotStackScenario(ComparisonScenario):
    """
    TOHIT-DEF-002: Same ECM Group Does Not Stack

    Battle A: Target with 1 ECM (group_a) → ~17% hit rate
    Battle B: Target with 2 ECM (both group_a) → ~17% hit rate

    Proves that intra-group MAX applies: two identical ECM modules in the
    same stacking group provide no additional defense over one.
    """

    metadata = TestMetadata(
        test_id="TOHIT-DEF-002",
        category="ToHitDefenseModifier",
        subcategory="Stacking Rules",
        name="Same ECM Group Does Not Stack",
        summary="Two ECM modules in the same stacking group provide no additional defense",
        conditions=[
            f"Attacker: {TOHIT_DEF_ATTACKER} (low accuracy beam, no sensor)",
            "Target (1 ECM): Test_Target_ECM_GroupA.json (1x group_a)",
            "Target (2 ECM): Test_Target_ECM_2xGroupA.json (2x group_a)",
            f"Distance: {MID_RANGE_DISTANCE} pixels",
            f"Test Duration: {TOHIT_DEF_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Intra-group MAX: MAX(1.0, 1.0) = 1.0",
            "Redundant ECM in same group provides no stacking benefit",
        ],
        expected_outcome=f"Both battles ~{TOHIT_DEF_ECM_HIT_RATE:.0%} (identical — same group MAX)",
        pass_criteria="damage taken is identical in both battles",
        max_ticks=TOHIT_DEF_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "ecm", "stacking", "same-group", "comparison"],
    )

    baseline_attacker_ship = TOHIT_DEF_ATTACKER
    baseline_target_ship = "Test_Target_ECM_GroupA.json"
    variant_attacker_ship = TOHIT_DEF_ATTACKER
    variant_target_ship = "Test_Target_ECM_2xGroupA.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: ECM target took some damage
        checks.append(check_true(
            "ECM Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: damage should be identical (same seed, same effective defense)
        checks.append(check_exact(
            "Same Group No Extra Defense",
            self.baseline_damage_dealt,
            self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-DEF-003: Different Stacking Groups Stack Additively
# =============================================================================

class ECMDifferentGroupsStackScenario(ComparisonScenario):
    """
    TOHIT-DEF-003: Different ECM Groups Stack Additively

    Battle A: Target with 1 ECM (group_a) → ~17% hit rate
    Battle B: Target with ECM group_a + group_b → ~7% hit rate

    Proves that inter-group SUM applies: ECM from different stacking groups
    combine additively (1.0 + 1.0 = 2.0 total defense bonus).
    """

    metadata = TestMetadata(
        test_id="TOHIT-DEF-003",
        category="ToHitDefenseModifier",
        subcategory="Stacking Rules",
        name="Different ECM Groups Stack Additively",
        summary="ECM from different stacking groups combine additively for stronger defense",
        conditions=[
            f"Attacker: {TOHIT_DEF_ATTACKER} (low accuracy beam, no sensor)",
            "Target (1 ECM group): Test_Target_ECM_GroupA.json (group_a only)",
            "Target (2 ECM groups): Test_Target_ECM_GroupAB.json (group_a + group_b)",
            f"Distance: {MID_RANGE_DISTANCE} pixels",
            f"Test Duration: {TOHIT_DEF_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Inter-group SUM: 1.0 + 1.0 = 2.0 total defense bonus",
            "Higher defense → lower net_score → lower sigmoid output",
        ],
        expected_outcome=f"1 group ~{TOHIT_DEF_ECM_HIT_RATE:.0%}, "
                         f"2 groups ~{TOHIT_DEF_DOUBLE_ECM_HIT_RATE:.0%}",
        pass_criteria="dual-ECM target takes less damage than single-ECM target",
        max_ticks=TOHIT_DEF_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "ecm", "stacking", "different-groups", "comparison"],
    )

    baseline_attacker_ship = TOHIT_DEF_ATTACKER
    baseline_target_ship = "Test_Target_ECM_GroupA.json"
    variant_attacker_ship = TOHIT_DEF_ATTACKER
    variant_target_ship = "Test_Target_ECM_GroupAB.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: single-ECM target took damage
        checks.append(check_true(
            "Single ECM Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: dual-ECM target takes less damage
        checks.append(check_true(
            "Additional ECM Group Reduces Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"single_ecm={self.baseline_damage_dealt}, "
                   f"dual_ecm={self.variant_damage_dealt}, "
                   f"reduction={self.baseline_damage_dealt - self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Statistical: dual-ECM hit rate matches 2.0 defense expectation
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_tost(
            "Hit Rate (2 ECM groups)",
            TOHIT_DEF_DOUBLE_ECM_HIT_RATE,
            int(self.variant_damage_dealt),
            variant_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))

        return checks


# =============================================================================
# TOHIT-DEF-004: Negative Defense Modifier Makes Target Easier to Hit
# =============================================================================

class NegativeDefenseModifierScenario(ComparisonScenario):
    """
    TOHIT-DEF-004: Negative Defense Modifier Makes Target Easier to Hit

    Battle A: Target with no modifier → ~36% hit rate
    Battle B: Target with ToHitDefenseModifier(-0.5) → ~48% hit rate

    Proves that negative ToHitDefenseModifier values reduce the target's
    defense score, making it easier to hit.
    """

    metadata = TestMetadata(
        test_id="TOHIT-DEF-004",
        category="ToHitDefenseModifier",
        subcategory="Basic Effect",
        name="Negative Defense Modifier Increases Hit Rate",
        summary="Negative ToHitDefenseModifier makes target easier to hit",
        conditions=[
            f"Attacker: {TOHIT_DEF_ATTACKER} (low accuracy beam, no sensor)",
            "Target (no modifier): Test_Target_Stationary.json",
            "Target (penalty): Test_Target_ECM_Penalty.json (-0.5 defense penalty)",
            f"Distance: {MID_RANGE_DISTANCE} pixels",
            f"Test Duration: {TOHIT_DEF_TEST_TICKS} ticks per battle",
        ],
        edge_cases=[
            "Negative value reduces defense_score in sigmoid",
            "Target becomes easier to hit than unmodified baseline",
        ],
        expected_outcome=f"No penalty ~{TOHIT_DEF_BASELINE_HIT_RATE:.0%}, "
                         f"With penalty ~{TOHIT_DEF_PENALTY_HIT_RATE:.0%} (easier to hit)",
        pass_criteria="penalized target takes more damage than unmodified target",
        max_ticks=TOHIT_DEF_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["tohit", "ecm", "penalty", "negative", "defense-modifier", "comparison"],
    )

    baseline_attacker_ship = TOHIT_DEF_ATTACKER
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = TOHIT_DEF_ATTACKER
    variant_target_ship = "Test_Target_ECM_Penalty.json"
    distance = MID_RANGE_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty on variant target
        penalty = self.get_ability(self.target, 'ToHitDefenseModifier')
        checks.append(check_exact(
            "Defense Penalty Value", ECM_PENALTY_VALUE,
            penalty.value if penalty else 0.0,
        ))

        # Precondition: both targets took damage
        checks.append(check_true(
            "Unmodified Target Took Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))
        checks.append(check_true(
            "Penalized Target Took Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
        ))

        # Outcome: penalized target takes MORE damage (easier to hit)
        checks.append(check_true(
            "Penalty Increases Damage Taken",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"unmodified={self.baseline_damage_dealt}, "
                   f"penalized={self.variant_damage_dealt}, "
                   f"increase=+{self.variant_damage_dealt - self.baseline_damage_dealt}",
            phase="outcome",
        ))

        # Statistical: penalized target hit rate matches expectation
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_tost(
            "Hit Rate (defense penalty)",
            TOHIT_DEF_PENALTY_HIT_RATE,
            int(self.variant_damage_dealt),
            variant_shots,
            margin=STANDARD_MARGIN,
            phase="outcome",
        ))

        return checks
