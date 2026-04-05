"""
SeekerWeaponAbility Test Scenarios

Comprehensive tests for seeker/missile weapon parameters using A/B comparison
battles. Each test isolates ONE parameter by varying it between baseline and
variant while keeping everything else identical.

Seeker mechanics:
- Projectiles with guidance: track target using predicted intercept
- Speed: projectile_speed / PROJECTILE_SPEED_SCALE (100) = px/tick
- Endurance: seconds of flight time (decremented each tick by TICK_RATE)
- Turn rate: degrees/second of heading change (limits tracking agility)
- Damage: flat warhead damage on impact (projectile_damage)
- HP: missile durability (PDC can destroy before impact)
- to_hit_defense: defense bonus against PDC beam hit-chance (sigmoid penalty)

Resource: SeekerWeaponAbility uses activation-trigger ResourceConsumption
(ammo per launch). Weapon won't fire when ammo is depleted.
"""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.templates import ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_true
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    SEEKER_TEST_TICKS,
    SEEKER_SPEED_TEST_TICKS,
    SEEKER_SPEED_SLOW,
    SEEKER_SPEED_FAST,
    SEEKER_ENDUR_SHORT,
    SEEKER_ENDUR_LONG,
    SEEKER_TURN_SLOW,
    SEEKER_TURN_FAST,
    SEEKER_DMG_LOW,
    SEEKER_DMG_HIGH,
    SEEKER_ENDURANCE_TEST_DISTANCE,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

STANDARD_TARGET = "Test_Target_Stationary.json"
PDC_TARGET = "Test_Target_PDC.json"


class _PDCMixin:
    """Mixin to force PDC target to fire (AI strategy handles it)."""

    def configure_baseline(self, engine):
        """Set target to also fire (PDC defense)."""
        self.target.ai_strategy = 'test_stationary_fire'

    def configure_variant(self, engine):
        """Set target to also fire (PDC defense)."""
        self.target.ai_strategy = 'test_stationary_fire'


# =============================================================================
# SEEKER-SPEED-001: Fast Seeker Hits, Slow Seeker Still In Flight
# =============================================================================

class SeekerSpeedComparisonScenario(ComparisonScenario):
    """
    SEEKER-SPEED-001: Projectile Speed Affects Travel Time

    Both seekers fire at a target at 1000px. Short test (100 ticks = 1 sec).
    Fast seeker (2000 px/s = 20 px/tick) reaches target in ~50 ticks.
    Slow seeker (500 px/s = 5 px/tick) needs ~200 ticks — still in flight.

    Validates: fast seeker deals damage, slow seeker doesn't (in 100 ticks).
    """

    metadata = TestMetadata(
        test_id="SEEKER-SPEED-001",
        category="SeekerWeaponAbility",
        subcategory="Speed",
        name="Fast Seeker Hits Before Slow Seeker",
        summary="Faster seeker impacts target in fewer ticks than slower seeker",
        conditions=[
            "Baseline: test_seeker_slow (500 px/s) at 1000px",
            "Variant: test_seeker_fast (2000 px/s) at 1000px",
            f"Test Duration: {SEEKER_SPEED_TEST_TICKS} ticks (1 second)",
        ],
        edge_cases=["Slow seeker still in flight at test end"],
        expected_outcome="Fast seeker deals 100 damage, slow seeker deals 0.",
        pass_criteria="variant_damage > 0, baseline_damage == 0",
        max_ticks=SEEKER_SPEED_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["seeker", "speed", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_Slow.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_Fast.json"
    variant_target_ship = STANDARD_TARGET
    distance = 1000

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Attacker Fired", baseline_shots >= 1,
            detail=f"shots={baseline_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Attacker Fired", variant_shots >= 1,
            detail=f"shots={variant_shots}", phase="precondition",
        ))

        checks.append(check_true(
            "Fast Seeker Hit",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        checks.append(check_exact(
            "Slow Seeker No Damage Yet", 0.0, self.baseline_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SEEKER-ENDUR-001: Long Endurance Reaches Target, Short Expires
# =============================================================================

class SeekerEnduranceComparisonScenario(ComparisonScenario):
    """
    SEEKER-ENDUR-001: Endurance Determines Effective Range

    Target at 3000px. Both seekers at 1000 px/s.
    Long endurance (5.0s = 5000px max travel) → reaches target, impacts.
    Short endurance (2.0s = 2000px max travel) → expires before reaching target.
    """

    metadata = TestMetadata(
        test_id="SEEKER-ENDUR-001",
        category="SeekerWeaponAbility",
        subcategory="Endurance",
        name="Long Endurance Reaches Target, Short Expires",
        summary="Seeker with sufficient endurance impacts; insufficient endurance expires",
        conditions=[
            f"Target distance: {SEEKER_ENDURANCE_TEST_DISTANCE}px",
            f"Baseline: endurance={SEEKER_ENDUR_SHORT}s (max travel=2000px < {SEEKER_ENDURANCE_TEST_DISTANCE}px)",
            f"Variant: endurance={SEEKER_ENDUR_LONG}s (max travel=5000px > {SEEKER_ENDURANCE_TEST_DISTANCE}px)",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["Short endurance seeker expires mid-flight"],
        expected_outcome="Long endurance seeker deals damage, short expires (0 damage).",
        pass_criteria="variant_damage > 0, baseline_damage == 0",
        max_ticks=SEEKER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["seeker", "endurance", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_ShortEndurance.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_LongEndurance.json"
    variant_target_ship = STANDARD_TARGET
    distance = SEEKER_ENDURANCE_TEST_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Attacker Fired", baseline_shots >= 1,
            detail=f"shots={baseline_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Attacker Fired", variant_shots >= 1,
            detail=f"shots={variant_shots}", phase="precondition",
        ))

        checks.append(check_true(
            "Long Endurance Seeker Hit",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        checks.append(check_exact(
            "Short Endurance Seeker Expired", 0.0, self.baseline_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SEEKER-TURN-001: Fast Turn Hits When Fired Backwards
# =============================================================================

class SeekerTurnRateComparisonScenario(ComparisonScenario):
    """
    SEEKER-TURN-001: Turn Rate Affects Intercept

    Both seekers launched perpendicular to target (attacker faces 90°).
    Seekers launch sideways, then must redirect using guidance.
    Fast turn (180°/s) redirects quickly and hits within endurance.
    Slow turn (30°/s, 3s endurance) can't correct fast enough and expires.

    Uses narrow firing arc (10°) so seekers launch in ship-facing direction,
    NOT auto-aimed at target.
    """

    metadata = TestMetadata(
        test_id="SEEKER-TURN-001",
        category="SeekerWeaponAbility",
        subcategory="Turn Rate",
        name="Fast Turn Redirects, Slow Turn Expires",
        summary="Seeker launched sideways: fast turn redirects and hits, slow turn expires",
        conditions=[
            "Both seekers launched 90° off-axis (narrow arc, attacker faces perpendicular)",
            f"Baseline: turn_rate={SEEKER_TURN_SLOW}°/s, endurance=3.0s",
            f"Variant: turn_rate={SEEKER_TURN_FAST}°/s, endurance=5.0s",
            "Distance: 2000px",
            "Test Duration: 1000 ticks",
        ],
        edge_cases=["Narrow arc forces launch perpendicular to target direction"],
        expected_outcome="Fast turn seeker deals damage, slow turn seeker expires.",
        pass_criteria="variant_damage > 0, baseline_damage == 0",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["seeker", "turn-rate", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_SlowTurn.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_FastTurn.json"
    variant_target_ship = STANDARD_TARGET
    distance = 2000

    def configure_baseline(self, engine):
        self.attacker.angle = 90.0

    def configure_variant(self, engine):
        self.attacker.angle = 90.0

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Attacker Fired", baseline_shots >= 1,
            detail=f"shots={baseline_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Attacker Fired", variant_shots >= 1,
            detail=f"shots={variant_shots}", phase="precondition",
        ))

        checks.append(check_true(
            "Fast Turn Seeker Hit",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        checks.append(check_exact(
            "Slow Turn Seeker No Hit", 0.0, self.baseline_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SEEKER-DMG-001: Warhead Damage Verification
# =============================================================================

class SeekerTurnRate180Scenario(ComparisonScenario):
    """
    SEEKER-TURN-002: 180° Reverse Launch

    Both seekers launched 180° away from target (narrow arc, faces backward).
    Fast turn should redirect and hit. Slow turn should expire.
    """

    metadata = TestMetadata(
        test_id="SEEKER-TURN-002",
        category="SeekerWeaponAbility",
        subcategory="Turn Rate",
        name="180° Reverse Launch",
        summary="Seeker launched directly backwards — tests guidance u-turn capability",
        conditions=[
            "Both seekers launched 180° away from target (narrow 1° arc)",
            f"Baseline: turn_rate={SEEKER_TURN_SLOW}°/s, endurance=3.0s",
            f"Variant: turn_rate={SEEKER_TURN_FAST}°/s, endurance=5.0s",
            "Distance: 1000px",
            "Test Duration: 1000 ticks",
        ],
        edge_cases=["180° off-boresight — commitment logic prevents floating-point sign flips"],
        expected_outcome="Fast turn seeker redirects and hits. Slow turn seeker expires before reaching target.",
        pass_criteria="variant_damage > 0, baseline_damage == 0",
        max_ticks=1000,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["seeker", "turn-rate", "180-reverse", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_SlowTurn.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_FastTurn.json"
    variant_target_ship = STANDARD_TARGET
    distance = 1000

    def configure_baseline(self, engine):
        self.attacker.angle = 180.0

    def configure_variant(self, engine):
        self.attacker.angle = 180.0

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Attacker Fired", baseline_shots >= 1,
            detail=f"shots={baseline_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Attacker Fired", variant_shots >= 1,
            detail=f"shots={variant_shots}", phase="precondition",
        ))

        checks.append(check_true(
            "Fast Turn Seeker Hit (180° reverse)",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        checks.append(check_exact(
            "Slow Turn Seeker No Hit (180° reverse)", 0.0, self.baseline_damage_dealt,
            phase="outcome",
        ))

        return checks


class SeekerDamageComparisonScenario(ComparisonScenario):
    """
    SEEKER-DMG-001: Warhead Damage Scales Correctly

    Both seekers impact at close range. Compare HP loss.
    Low damage (50) vs high damage (200) = 4x ratio.
    """

    metadata = TestMetadata(
        test_id="SEEKER-DMG-001",
        category="SeekerWeaponAbility",
        subcategory="Damage",
        name="Warhead Damage Scales Correctly",
        summary="Seeker with 4x damage deals 4x hull damage on impact",
        conditions=[
            f"Baseline: damage={SEEKER_DMG_LOW}, single shot at {POINT_BLANK_DISTANCE}px",
            f"Variant: damage={SEEKER_DMG_HIGH}, single shot at {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["Exact damage ratio (no falloff for seekers)"],
        expected_outcome="Variant deals exactly 4x more damage.",
        pass_criteria="variant_damage / baseline_damage == 4.0",
        max_ticks=SEEKER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["seeker", "damage", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_Dmg50.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_Dmg200.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Attacker Fired", baseline_shots >= 1,
            detail=f"shots={baseline_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Attacker Fired", variant_shots >= 1,
            detail=f"shots={variant_shots}", phase="precondition",
        ))

        checks.append(check_true("Baseline Hit", self.baseline_damage_dealt > 0,
                                 detail=f"damage={self.baseline_damage_dealt}"))
        checks.append(check_true("Variant Hit", self.variant_damage_dealt > 0,
                                 detail=f"damage={self.variant_damage_dealt}"))

        checks.append(check_exact(
            "Damage Ratio 4x",
            float(SEEKER_DMG_HIGH) / SEEKER_DMG_LOW,
            self.variant_damage_dealt / self.baseline_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# SEEKER-HP-001: Higher HP Survives PDC Better
# =============================================================================

class SeekerHPvsPDCScenario(_PDCMixin, ComparisonScenario):
    """
    SEEKER-HP-001: Missile HP Affects PDC Survivability

    Both fire seekers at a PDC-equipped target.
    Low HP (1) seekers destroyed by single PDC hit.
    High HP (10) seekers survive more PDC hits, more impacts.
    """

    metadata = TestMetadata(
        test_id="SEEKER-HP-001",
        category="SeekerWeaponAbility",
        subcategory="HP",
        name="Higher HP Survives PDC Better",
        summary="Seekers with more HP survive point defense and deal more damage",
        conditions=[
            "Target: PDC-equipped ship",
            "Baseline: seeker HP=1",
            "Variant: seeker HP=10",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["PDC beam damages seekers in flight"],
        expected_outcome="High HP seekers deal more total damage.",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=SEEKER_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["seeker", "hp", "pdc", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_LowHP.json"
    baseline_target_ship = PDC_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_HighHP.json"
    variant_target_ship = PDC_TARGET
    distance = 400  # Far enough for PDC to have time to intercept seekers in flight

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Attacker Fired", baseline_shots >= 1,
            detail=f"shots={baseline_shots}", phase="precondition",
        ))
        checks.append(check_true(
            "Variant Attacker Fired", variant_shots >= 1,
            detail=f"shots={variant_shots}", phase="precondition",
        ))

        # Outcome: high HP seekers survive PDC and deal damage
        checks.append(check_true(
            "High HP Seekers Deal Damage",
            self.variant_damage_dealt > 0,
            detail=f"variant_damage={self.variant_damage_dealt}", phase="outcome",
        ))

        # Outcome: high HP seekers deal MORE damage than low HP
        # Low HP(1) seekers may deal 0 (all destroyed by PDC) — that's expected
        checks.append(check_true(
            "High HP Survives Better Than Low HP",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# SEEKER-RES-001/002/003: Resource Dependency
# =============================================================================

class SeekerNoAmmoScenario(ComparisonScenario):
    """SEEKER-RES-001: Seeker with ammo cost but no storage cannot launch."""

    metadata = TestMetadata(
        test_id="SEEKER-RES-001",
        category="SeekerWeaponAbility",
        subcategory="Resource",
        name="Seeker Stops Without Ammo",
        summary="Seeker with ammo cost but no ammo storage cannot launch",
        conditions=[
            "Baseline: high ammo (100k)", "Variant: no ammo storage",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["Weapon exists but cannot afford activation"],
        expected_outcome="Baseline deals damage, variant deals zero.",
        pass_criteria="variant_damage == 0",
        max_ticks=SEEKER_TEST_TICKS, seed=STANDARD_SEED, battle_end_mode="time_based",
        tags=["seeker", "resource", "ammo", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_SeekerRapid_HighAmmo.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_SeekerRapid_NoAmmo.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_true("Baseline Dealt Damage", self.baseline_damage_dealt > 0,
                                 detail=f"damage={self.baseline_damage_dealt}"))
        checks.append(check_exact("No Damage Without Ammo", 0.0, self.variant_damage_dealt,
                                  phase="outcome"))
        return checks


class SeekerLimitedAmmoScenario(ComparisonScenario):
    """SEEKER-RES-002: Limited ammo causes seeker to stop launching mid-battle."""

    metadata = TestMetadata(
        test_id="SEEKER-RES-002",
        category="SeekerWeaponAbility",
        subcategory="Resource",
        name="Seeker Stops At Ammo Depletion",
        summary="Limited ammo causes seeker to stop launching mid-battle",
        conditions=[
            "Baseline: high ammo (100k)", "Variant: 100 ammo",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["Weapon fires until ammo depleted"],
        expected_outcome="Variant deals less damage.",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=SEEKER_TEST_TICKS, seed=STANDARD_SEED, battle_end_mode="time_based",
        tags=["seeker", "resource", "ammo", "depletion", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_SeekerRapid_HighAmmo.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_SeekerRapid_SmallAmmo.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_true("Baseline Dealt Damage", self.baseline_damage_dealt > 0,
                                 detail=f"damage={self.baseline_damage_dealt}"))
        checks.append(check_true("Variant Dealt Damage", self.variant_damage_dealt > 0,
                                 detail=f"damage={self.variant_damage_dealt}"))
        checks.append(check_true("Limited Ammo Less Damage",
                                 self.variant_damage_dealt < self.baseline_damage_dealt,
                                 detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
                                 phase="outcome"))

        # Outcome: variant fired fewer shots (ammo limited)
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true("Variant Fired Fewer Shots",
                                 variant_shots < baseline_shots,
                                 detail=f"variant={variant_shots}, baseline={baseline_shots}",
                                 phase="outcome"))
        return checks


class SeekerAmmoControlScenario(ComparisonScenario):
    """SEEKER-RES-003: Control — identical ammo produces identical results."""

    metadata = TestMetadata(
        test_id="SEEKER-RES-003",
        category="SeekerWeaponAbility",
        subcategory="Resource",
        name="Ammo Control (Identical Setups)",
        summary="Identical seeker + ammo setups produce identical damage",
        conditions=[
            "Both: high ammo (100k)",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["Control validates comparison infrastructure"],
        expected_outcome="Both deal identical damage.",
        pass_criteria="baseline_damage == variant_damage",
        max_ticks=SEEKER_TEST_TICKS, seed=STANDARD_SEED, battle_end_mode="time_based",
        tags=["seeker", "resource", "control", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_SeekerRapid_HighAmmo.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_SeekerRapid_HighAmmo.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()
        checks.append(check_true("Baseline Dealt Damage", self.baseline_damage_dealt > 0,
                                 detail=f"damage={self.baseline_damage_dealt}"))
        checks.append(check_exact("Same Damage (Control)",
                                  self.baseline_damage_dealt, self.variant_damage_dealt,
                                  phase="outcome"))
        return checks


# =============================================================================
# SEEKER-PD-001/002: Point Defense Interaction
# =============================================================================

class SeekerPDCReducesDamageScenario(_PDCMixin, ComparisonScenario):
    """SEEKER-PD-001: PDC intercepts some seekers, reducing damage."""

    metadata = TestMetadata(
        test_id="SEEKER-PD-001",
        category="SeekerWeaponAbility",
        subcategory="Point Defense",
        name="PDC Reduces Seeker Impacts",
        summary="PDC intercepts some seekers, reducing damage vs undefended target",
        conditions=[
            "Baseline: seekers vs undefended target",
            "Variant: seekers vs PDC-equipped target",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["PDC beam fires at incoming seekers"],
        expected_outcome="PDC target takes less damage.",
        pass_criteria="variant_damage < baseline_damage",
        max_ticks=SEEKER_TEST_TICKS, seed=STANDARD_SEED, battle_end_mode="time_based",
        tags=["seeker", "pdc", "point-defense", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_LowHP.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_LowHP.json"
    variant_target_ship = PDC_TARGET
    distance = 400  # Give PDC time to intercept seekers in flight

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: undefended target took damage
        checks.append(check_true("Undefended Target Took Damage",
                                 self.baseline_damage_dealt > 0,
                                 detail=f"damage={self.baseline_damage_dealt}",
                                 phase="precondition"))

        # Outcome: PDC reduced total damage (may reduce to 0 for HP=1 seekers)
        checks.append(check_true("PDC Reduced Damage",
                                 self.variant_damage_dealt < self.baseline_damage_dealt,
                                 detail=f"pdc_target={self.variant_damage_dealt}, undefended={self.baseline_damage_dealt}",
                                 phase="outcome"))

        return checks


class SeekerDefenseVsPDCScenario(_PDCMixin, ComparisonScenario):
    """SEEKER-PD-002: Higher to_hit_defense makes seekers harder to intercept."""

    metadata = TestMetadata(
        test_id="SEEKER-PD-002",
        category="SeekerWeaponAbility",
        subcategory="Point Defense",
        name="to_hit_defense Reduces PDC Accuracy",
        summary="Seekers with higher defense survive PDC better, dealing more damage",
        conditions=[
            "Baseline: to_hit_defense=0 (easy to hit)",
            "Variant: to_hit_defense=3.0 (hard to hit)",
            "Both vs same PDC target",
            f"Distance: {POINT_BLANK_DISTANCE}px",
            f"Test Duration: {SEEKER_TEST_TICKS} ticks",
        ],
        edge_cases=["to_hit_defense feeds into sigmoid as defense_score on the projectile"],
        expected_outcome="High defense seekers deal more damage.",
        pass_criteria="variant_damage > baseline_damage",
        max_ticks=SEEKER_TEST_TICKS, seed=STANDARD_SEED, battle_end_mode="time_based",
        tags=["seeker", "pdc", "to-hit-defense", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Seeker_LowDefense.json"
    baseline_target_ship = PDC_TARGET
    variant_attacker_ship = "Test_Attacker_Seeker_HighDefense.json"
    variant_target_ship = PDC_TARGET
    distance = 400  # Give PDC time to intercept seekers in flight

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Outcome: high defense seekers survive PDC better, deal more damage
        # Low defense (0) seekers may all get destroyed — that's expected behavior
        checks.append(check_true("High Defense Seekers Deal More",
                                 self.variant_damage_dealt > self.baseline_damage_dealt,
                                 detail=f"high_def={self.variant_damage_dealt}, low_def={self.baseline_damage_dealt}",
                                 phase="outcome"))

        # Outcome: high defense seekers actually dealt some damage
        checks.append(check_true("High Defense Seekers Reached Target",
                                 self.variant_damage_dealt > 0,
                                 detail=f"damage={self.variant_damage_dealt}",
                                 phase="outcome"))

        return checks
