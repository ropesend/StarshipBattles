"""
Reload Multiplier Modifier Test Scenarios (MOD-RELOAD-001 through MOD-RELOAD-005)

Behavioral simulation tests for the reload_mult modifier. Reload time controls
how frequently a weapon fires. The test_reload_boost modifier uses formula
1.0/param (inverse), so param=2 halves reload time (fires 2x as fast).
The test_reload_penalty uses formula param (direct), so param=2 doubles
reload time (fires half as fast).

Test component: test_beam_med_acc_1dmg_reload10
  - reload=0.1s (fires every ~10 ticks), damage=1, accuracy=2.0
  - Base: ~50 shots in 500 ticks
  - Boosted (0.5x reload): ~100 shots in 500 ticks
  - Penalized (2.0x reload): ~25 shots in 500 ticks

Shot count is the primary metric — it's deterministic (independent of hit/miss RNG).
Damage is also checked where the weapon hits (point-blank, high accuracy).

Ship Files:
- Test_Attacker_Beam_ReloadBoost.json — test_beam_med_acc_1dmg_reload10
  + test_reload_boost(2), reload 0.1->0.05s (~100 shots/500 ticks)
- Test_Attacker_Beam_ReloadBase.json — test_beam_med_acc_1dmg_reload10
  (no modifier, reload=0.1s, ~50 shots/500 ticks)
- Test_Attacker_Beam_ReloadPenalty.json — test_beam_med_acc_1dmg_reload10
  + test_reload_penalty(2), reload 0.1->0.2s (~25 shots/500 ticks)
- Test_Target_Stationary.json — test_armor_extreme_hp (1B HP, stationary)

Test Coverage:
- MOD-RELOAD-001: Stat gate — reload halved (0.1->0.05s), fires and hits
- MOD-RELOAD-002: Shot count — boosted fires ~2x more shots than baseline (100 vs 50)
- MOD-RELOAD-003: Damage ratio — boosted deals ~2x damage (more shots = more hits)
- MOD-RELOAD-004: Penalty reduces fire rate — penalized fires ~half as many shots (25 vs 50)
- MOD-RELOAD-005: Stat gate — penalty doubles reload (0.1->0.2s), fires and hits
"""

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_approx, check_true
from combat_lab.test_constants import (
    STANDARD_SEED,
    POINT_BLANK_DISTANCE,
)

# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

# test_beam_med_acc_1dmg_reload10 + test_reload_boost(2), reload 0.1->0.05s
BOOST_SHIP = "Test_Attacker_Beam_ReloadBoost.json"
# test_beam_med_acc_1dmg_reload10, no modifier, reload=0.1s
BASE_SHIP = "Test_Attacker_Beam_ReloadBase.json"
# test_beam_med_acc_1dmg_reload10 + test_reload_penalty(2), reload 0.1->0.2s
PENALTY_SHIP = "Test_Attacker_Beam_ReloadPenalty.json"
# test_armor_extreme_hp (1B HP, stationary)
TARGET_SHIP = "Test_Target_Stationary.json"

# =============================================================================
# RELOAD CONSTANTS
# =============================================================================

BASE_RELOAD = 0.1               # seconds (10 ticks per shot)
BOOST_PARAM = 2                 # test_reload_boost value
BOOSTED_RELOAD = BASE_RELOAD * (1.0 / BOOST_PARAM)  # 0.05s (5 ticks per shot)
PENALTY_PARAM = 2               # test_reload_penalty value
PENALIZED_RELOAD = BASE_RELOAD * PENALTY_PARAM       # 0.2s (20 ticks per shot)

TEST_TICKS = 500

# Expected shot counts (deterministic — weapon fires on timer regardless of hit/miss)
# Shots = floor(test_duration_seconds / reload_seconds) ≈ ticks / ticks_per_shot
# Note: first shot fires at tick 0 or after first reload cycle; approximate ±1
EXPECTED_SHOTS_BASE = 50        # 500 ticks / 10 ticks per shot
EXPECTED_SHOTS_BOOSTED = 100    # 500 ticks / 5 ticks per shot
EXPECTED_SHOTS_PENALIZED = 25   # 500 ticks / 20 ticks per shot
SHOT_TOLERANCE = 3              # ±3 shots for timing edge cases


# =============================================================================
# MOD-RELOAD-001: Stat Gate — Reload Halved
# =============================================================================

class ModReload001_StatGateScenario(StaticTargetScenario):
    """
    MOD-RELOAD-001: Quick sanity — reload modifier applied correctly.

    Boosted beam at point-blank: reload_time==0.05s (0.1 * 1/2), fires
    and hits target. Confirms modifier loaded before behavioral tests.
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-001",
        category="ReloadMultiplier",
        subcategory="ReloadMultiplier",
        name="Stat gate — reload halved (0.1->0.05s)",
        summary=f"Verify test_reload_boost(2) halves reload to {BOOSTED_RELOAD}s; weapon fires and hits",
        conditions=[
            f"Attacker: {BOOST_SHIP} (test_beam_med_acc_1dmg_reload10 + test_reload_boost({BOOST_PARAM}), reload {BASE_RELOAD}->{BOOSTED_RELOAD}s)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=["Inverse formula: reload_mult = 1.0/param = 0.5"],
        expected_outcome=f"beam.reload_time == {BOOSTED_RELOAD}, damage > 0",
        pass_criteria=f"reload_time == {BOOSTED_RELOAD} AND damage > 0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "reload_mult", "stat_gate"],
    )

    attacker_ship = BOOST_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_reload = beam.reload_time if beam else None

    def _collect_extra_results(self, outcome, telemetry=None):
        self.results['expected_reload'] = BOOSTED_RELOAD
        self.results['actual_reload'] = self.actual_reload

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: reload modifier applied
        checks.append(check_approx(
            "Boosted Reload Time", BOOSTED_RELOAD,
            self.actual_reload or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: weapon fired and hit
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            detail=f"damage={self.damage_dealt}", phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-RELOAD-002: Shot Count — Boosted Fires 2x More
# =============================================================================

class ModReload002_ShotCountScenario(ComparisonScenario):
    """
    MOD-RELOAD-002: Prove boosted reload fires ~2x more shots.

    Base (reload=0.1s): ~50 shots in 500 ticks
    Boosted (reload=0.05s): ~100 shots in 500 ticks

    Shot count is deterministic — the weapon fires on its reload timer
    regardless of hit/miss RNG. This directly measures fire rate.
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-002",
        category="ReloadMultiplier",
        subcategory="ReloadMultiplier",
        name="Shot count — boosted fires ~2x more shots",
        summary=(
            f"Base (~{EXPECTED_SHOTS_BASE} shots at {BASE_RELOAD}s reload) vs "
            f"boosted (~{EXPECTED_SHOTS_BOOSTED} shots at {BOOSTED_RELOAD}s reload)"
        ),
        conditions=[
            f"Baseline: {BASE_SHIP} (test_beam_med_acc_1dmg_reload10, no modifier, reload={BASE_RELOAD}s, ~{EXPECTED_SHOTS_BASE} shots)",
            f"Variant: {BOOST_SHIP} (test_beam_med_acc_1dmg_reload10 + test_reload_boost({BOOST_PARAM}), reload={BOOSTED_RELOAD}s, ~{EXPECTED_SHOTS_BOOSTED} shots)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
            f"Duration: {TEST_TICKS} ticks",
        ],
        edge_cases=["Shot count is deterministic (not affected by hit/miss)"],
        expected_outcome=(
            f"Baseline: ~{EXPECTED_SHOTS_BASE} shots. "
            f"Variant: ~{EXPECTED_SHOTS_BOOSTED} shots. Ratio ~2.0x."
        ),
        pass_criteria=f"Both shot counts within ±{SHOT_TOLERANCE}, ratio ≈ 2.0x",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "reload_mult", "shot_count", "behavioral"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        b_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        # Precondition: both fired
        checks.append(check_true(
            "Baseline Fired", b_shots > 0,
            detail=f"shots={b_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Fired", v_shots > 0,
            detail=f"shots={v_shots}", phase="precondition",
        ))

        # Outcome: shot counts match expected values
        checks.append(check_approx(
            "Baseline Shot Count", float(EXPECTED_SHOTS_BASE),
            float(b_shots), tolerance=SHOT_TOLERANCE, phase="outcome",
        ))
        checks.append(check_approx(
            "Variant Shot Count", float(EXPECTED_SHOTS_BOOSTED),
            float(v_shots), tolerance=SHOT_TOLERANCE, phase="outcome",
        ))

        # Outcome: ratio is ~2.0x
        if b_shots > 0:
            ratio = v_shots / b_shots
            checks.append(check_approx(
                "Shot Ratio (variant/baseline)", 2.0,
                ratio, tolerance=0.2, phase="outcome",
            ))

        return checks


# =============================================================================
# MOD-RELOAD-003: Damage Ratio — Boosted Deals ~2x Damage
# =============================================================================

class ModReload003_DamageRatioScenario(ComparisonScenario):
    """
    MOD-RELOAD-003: Prove boosted reload translates to ~2x combat damage.

    More shots at point-blank with high accuracy means proportionally more hits.
    Damage ratio should approximate the shot ratio (~2.0x).
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-003",
        category="ReloadMultiplier",
        subcategory="ReloadMultiplier",
        name="Damage ratio — boosted deals ~2x damage",
        summary=(
            f"Boosted fires ~2x shots -> ~2x hits -> ~2x damage at point-blank"
        ),
        conditions=[
            f"Baseline: {BASE_SHIP} (reload={BASE_RELOAD}s, ~{EXPECTED_SHOTS_BASE} shots)",
            f"Variant: {BOOST_SHIP} (reload={BOOSTED_RELOAD}s, ~{EXPECTED_SHOTS_BOOSTED} shots)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank, high hit rate)",
        ],
        edge_cases=["Damage ratio approximates shot ratio at high accuracy"],
        expected_outcome="Variant damage ≈ 2x baseline damage",
        pass_criteria="variant_damage > baseline_damage AND ratio ≈ 2.0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "reload_mult", "damage_ratio"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = BOOST_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Precondition: both dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage", self.baseline_damage_dealt > 10,
            detail=f"damage={self.baseline_damage_dealt}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Dealt Damage", self.variant_damage_dealt > 10,
            detail=f"damage={self.variant_damage_dealt}", phase="precondition",
        ))

        # Outcome: damage ratio ≈ 2.0x
        if self.baseline_damage_dealt > 0:
            ratio = self.variant_damage_dealt / self.baseline_damage_dealt
            checks.append(check_approx(
                "Damage Ratio (variant/baseline)", 2.0,
                ratio, tolerance=0.3, phase="outcome",
            ))

        # Outcome: variant dealt more damage
        checks.append(check_true(
            "Boosted Deals More Damage",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=(
                f"baseline={self.baseline_damage_dealt}, "
                f"variant={self.variant_damage_dealt}"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-RELOAD-004: Penalty Reduces Fire Rate
# =============================================================================

class ModReload004_PenaltyReducesFireRateScenario(ComparisonScenario):
    """
    MOD-RELOAD-004: Prove penalty modifier reduces fire rate.

    Base (reload=0.1s): ~50 shots in 500 ticks
    Penalized (reload=0.2s): ~25 shots in 500 ticks

    The penalty modifier doubles reload time, halving the fire rate.
    Shot count and damage both decrease proportionally.
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-004",
        category="ReloadMultiplier",
        subcategory="ReloadMultiplier",
        name="Penalty reduces fire rate — penalized fires ~half as many shots",
        summary=(
            f"Base (~{EXPECTED_SHOTS_BASE} shots at {BASE_RELOAD}s) vs "
            f"penalized (~{EXPECTED_SHOTS_PENALIZED} shots at {PENALIZED_RELOAD}s)"
        ),
        conditions=[
            f"Baseline: {BASE_SHIP} (test_beam_med_acc_1dmg_reload10, no modifier, reload={BASE_RELOAD}s)",
            f"Variant: {PENALTY_SHIP} (test_beam_med_acc_1dmg_reload10 + test_reload_penalty({PENALTY_PARAM}), reload={PENALIZED_RELOAD}s)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Duration: {TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Penalty uses direct multiply: reload_mult = param = 2.0",
            "Tests modifier bidirectionality (slower, not faster)",
        ],
        expected_outcome=(
            f"Baseline: ~{EXPECTED_SHOTS_BASE} shots. "
            f"Penalized: ~{EXPECTED_SHOTS_PENALIZED} shots."
        ),
        pass_criteria=f"Penalized shot count ≈ {EXPECTED_SHOTS_PENALIZED}, less than baseline",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "reload_mult", "penalty", "behavioral"],
    )

    baseline_attacker_ship = BASE_SHIP
    baseline_target_ship = TARGET_SHIP
    variant_attacker_ship = PENALTY_SHIP
    variant_target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty applied
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        if beam:
            checks.append(check_approx(
                "Penalized Reload Time", PENALIZED_RELOAD,
                beam.reload_time, tolerance=0.001, phase="data",
            ))

        b_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        v_shots = self.results.get('variant_attacker_total_shots_fired', 0)

        # Outcome: penalized fires fewer shots
        checks.append(check_approx(
            "Penalized Shot Count", float(EXPECTED_SHOTS_PENALIZED),
            float(v_shots), tolerance=SHOT_TOLERANCE, phase="outcome",
        ))
        checks.append(check_approx(
            "Baseline Shot Count", float(EXPECTED_SHOTS_BASE),
            float(b_shots), tolerance=SHOT_TOLERANCE, phase="outcome",
        ))

        # Outcome: penalty fires fewer than baseline
        checks.append(check_true(
            "Penalty Reduces Fire Rate",
            v_shots < b_shots,
            detail=f"baseline={b_shots}, penalized={v_shots}",
            phase="outcome",
        ))

        # Outcome: penalty deals less damage
        checks.append(check_true(
            "Penalty Reduces Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=(
                f"baseline_dmg={self.baseline_damage_dealt}, "
                f"penalty_dmg={self.variant_damage_dealt}"
            ),
            phase="outcome",
        ))

        return checks


# =============================================================================
# MOD-RELOAD-005: Stat Gate — Penalty Doubles Reload
# =============================================================================

class ModReload005_PenaltyStatGateScenario(StaticTargetScenario):
    """
    MOD-RELOAD-005: Quick sanity — penalty modifier doubles reload.

    Penalized beam at point-blank: reload_time==0.2s (0.1 * 2.0), fires
    and hits. Confirms negative modifier loaded correctly.
    """
    metadata = TestMetadata(
        test_id="MOD-RELOAD-005",
        category="ReloadMultiplier",
        subcategory="ReloadMultiplier",
        name="Stat gate — penalty doubles reload (0.1->0.2s)",
        summary=f"Verify test_reload_penalty(2) doubles reload to {PENALIZED_RELOAD}s",
        conditions=[
            f"Attacker: {PENALTY_SHIP} (test_beam_med_acc_1dmg_reload10 + test_reload_penalty({PENALTY_PARAM}), reload {BASE_RELOAD}->{PENALIZED_RELOAD}s)",
            f"Target: {TARGET_SHIP} (test_armor_extreme_hp, 1B HP, stationary)",
            f"Distance: {POINT_BLANK_DISTANCE}px (point-blank)",
        ],
        edge_cases=["Penalty uses direct multiply: reload_mult = param = 2.0"],
        expected_outcome=f"beam.reload_time == {PENALIZED_RELOAD}, damage > 0",
        pass_criteria=f"reload_time == {PENALIZED_RELOAD} AND damage > 0",
        max_ticks=TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["modifier", "reload_mult", "penalty", "stat_gate"],
    )

    attacker_ship = PENALTY_SHIP
    target_ship = TARGET_SHIP
    distance = POINT_BLANK_DISTANCE

    def custom_setup(self, battle_engine):
        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        self.actual_reload = beam.reload_time if beam else None

    def _collect_extra_results(self, outcome, telemetry=None):
        self.results['expected_reload'] = PENALIZED_RELOAD
        self.results['actual_reload'] = self.actual_reload

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()

        beam = self.get_ability(self.attacker, 'BeamWeaponAbility')
        checks.append(check_true("Beam Loaded", beam is not None, phase="precondition"))
        if beam is None:
            return checks

        # Data: penalty applied
        checks.append(check_approx(
            "Penalized Reload Time", PENALIZED_RELOAD,
            self.actual_reload or 0.0, tolerance=0.001, phase="data",
        ))

        # Outcome: weapon still fires and hits at point-blank
        checks.append(check_true(
            "Damage Dealt", self.damage_dealt > 0,
            detail=f"damage={self.damage_dealt}", phase="outcome",
        ))

        return checks
