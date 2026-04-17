"""
Projectile Weapon Test Scenarios (PROJECTILE-001 to PROJECTILE-006, PROJECTILE-DMG-*)

These tests validate projectile weapon mechanics:
- Projectile travel time and physics
- Hit detection with moving projectiles
- Predictive leading for moving targets
- Damage consistency across ranges
- Out-of-range behavior

Projectile Weapon Mechanics:
- Projectiles are physical objects that travel through space at a fixed speed
- Travel time = distance / effective_speed (e.g., 200px / 200px/tick = 1 tick)
- Hit detection occurs when projectile position overlaps with target
- For moving targets, weapon system calculates leading angle
- Leading prediction assumes constant linear velocity
- Projectiles despawn after reaching max_range or hitting target
- Unlike beams, projectiles have travel time - target can move during flight

Test Coverage:
- Stationary target accuracy: 1 test (PROJECTILE-001)
- Linear moving target tests: 2 tests (PROJECTILE-002, PROJECTILE-003)
- Erratic target tests: 2 tests (PROJECTILE-004, PROJECTILE-005)
- Range limit test: 1 test (PROJECTILE-006)
- Damage at various ranges: 3 tests (PROJECTILE-DMG-010, -050, -090)

Projectile Weapon Stats (test_weapon_proj_omni):
- Damage: 1 per hit (keeps math simple: damage_dealt == hits)
- Range: 1000 pixels
- Projectile Speed: 20000 (200 px/tick after PROJECTILE_SPEED_SCALE)
- Reload Time: 0.0s (fires every tick for high sample counts)
- Firing Arc: 360 degrees

All targets use extreme HP armor (1 billion HP) so they survive the full
test duration regardless of hit count.
"""

import pygame
from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario, ComparisonScenario
from combat_lab.scenarios.validation import check_exact, check_approx, check_true
from combat_lab.test_constants import (
    STANDARD_TEST_TICKS,
    STANDARD_SEED,
    STATIONARY_TARGET_MASS,
    PROJECTILE_OUT_OF_RANGE_DISTANCE,
    POINT_BLANK_DISTANCE,
)


def calculate_projectile_travel_time(distance: float, projectile_speed: float) -> float:
    """
    Calculate time in seconds for projectile to reach target.

    Args:
        distance: Distance in pixels
        projectile_speed: Speed in pixels/second

    Returns:
        Travel time in seconds
    """
    return distance / projectile_speed



# ============================================================================
# STATIONARY TARGET TEST
# ============================================================================

class ProjectileStationaryTargetScenario(StaticTargetScenario):
    """
    PROJECTILE-001: 100% Accuracy vs Stationary Target

    Tests that projectile weapons hit consistently against a stationary target
    at close range (200px) where travel time is minimal.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-001",
        category="Projectile Weapons",
        subcategory="Accuracy",
        name="Projectile vs Stationary - Point Blank (200px)",
        summary="Validates projectile weapons hit consistently against stationary targets with minimal travel time",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Stationary.json",
            "Distance: 200 pixels",
            "Projectile Speed: 20000 (200 px/tick)",
            "Travel Time: 200px / 200px/tick = 1 tick",
            "Reload Time: 0.0s (fires every tick)",
            "Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Minimal projectile travel time at close range",
            "Target is stationary - no leading calculation needed",
            "Should hit ~100% of shots fired",
            "damage_dealt == number of hits (1 dmg per hit)"
        ],
        expected_outcome="Near-100% hit rate against stationary target",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        ui_priority=10,
        tags=["accuracy", "projectile", "stationary-target", "point-blank"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 200

    def custom_setup(self, battle_engine):
        """Store projectile mechanics for results."""
        self.travel_time = calculate_projectile_travel_time(200, 20000)

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store projectile-specific results."""
        self.results['travel_time_seconds'] = self.travel_time
        self.results['weapon_type'] = 'Projectile360'
        self.results['weapon_damage'] = 1
        self.results['weapon_range'] = 1000
        self.results['projectile_speed'] = 20000
        self.results['reload_time'] = 0.0

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase: verify weapon and target loaded correctly
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        # Precondition phase: verify geometry
        center_dist = self.attacker.position.distance_to(self.target.position)
        checks.append(check_approx("Center Distance", float(self.distance), center_dist,
                                   tolerance=0.01, phase="precondition"))
        # Outcome phase: stationary target must be hit with near-perfect accuracy
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        checks.append(check_true("Shots Fired", resolved > 100,
                                 actual=resolved, phase="outcome",
                                 detail="weapon should fire hundreds of shots in 500 ticks"))
        checks.append(check_true("100% Resolved Hit Rate", resolved > 0 and hits == resolved,
                                 actual=f"{hits}/{resolved}",
                                 phase="outcome",
                                 detail="stationary target: every resolved shot must hit"))
        return checks


# ============================================================================
# MOVING TARGET TESTS - LINEAR
# ============================================================================

class ProjectileLinearSlowTargetScenario(StaticTargetScenario):
    """
    PROJECTILE-002: Accuracy vs Slow Linearly Moving Target (crossing engagement)

    Tests predictive leading against a slow target that crosses through the
    attacker's engagement zone.  The target starts at (100, -1200), out of
    weapon range, heading upward (angle 90).  It reaches full speed (1.25
    px/tick) by tick 9 and enters range at tick ~168.  It remains in range
    for the rest of the 500-tick test (~332 in-range shots).

    Same starting position as PROJECTILE-003 (fast target) so the only
    variable is target speed.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-002",
        category="Projectile Weapons",
        subcategory="Moving Targets",
        name="Projectile vs Slow Linear Target (crossing)",
        summary="Validates predictive leading allows hits on slow-moving linear targets",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Linear_Slow.json",
            "Target Start: (100, -1200), heading 90 (upward)",
            "Target Speed: max 1.25 px/tick (full speed by tick 9)",
            "Enters Range: tick ~168, stays in range for ~332 ticks",
            "Projectile Speed: 20000 (200 px/tick after scale)",
            "Reload Time: 0.0s (fires every tick)",
            "Damage: 1 per hit (damage_dealt == hits)",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Target moves during projectile flight",
            "Weapon system predicts future position",
            "Leading calculation assumes constant velocity",
            "Slow targets easier to predict than fast"
        ],
        expected_outcome="High hit rate from successful leading predictions",
        pass_criteria="damage_dealt > 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        ui_priority=8,
        tags=["accuracy", "projectile", "moving-target", "linear", "slow", "leading", "crossing"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Linear_Slow.json"
    distance = 1204  # Initial center-to-center distance from (0,0) to (100,-1200)

    def custom_setup(self, battle_engine):
        """Position target out of range, heading upward through engagement zone."""
        self.target.position = pygame.math.Vector2(100, -1200)
        self.target.angle = 90
        self.target.movement_policy = 'test_straight_line'

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store hit tracking with resolved stats (excluding in-flight)."""
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        in_flight = self.results.get('attacker_in_flight', 0)
        self.results['shots_fired'] = self.results.get('attacker_total_shots_fired', 0)
        self.results['hits'] = hits
        self.results['in_flight'] = in_flight
        self.results['hit_rate'] = hits / resolved if resolved > 0 else 0.0

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase: verify weapon and target loaded correctly
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        checks.append(check_approx("Target Max Speed", 1.25, self.target.max_speed,
                                   tolerance=0.01))
        # Precondition phase: verify target moved and entered range
        target_speed = self.target.velocity.length()
        checks.append(check_approx("Target At Full Speed", 1.25, target_speed,
                                   tolerance=0.01, phase="precondition"))
        target_displacement = self.target.position.distance_to(pygame.math.Vector2(100, -1200))
        checks.append(check_true("Target Displaced > 500px", target_displacement > 500,
                                 actual=f"{target_displacement:.0f}px",
                                 phase="precondition",
                                 detail="slow target should have traveled ~619px from start"))
        resolved = self.results.get('attacker_resolved_shots', 0)
        checks.append(check_true("Target Entered Range", resolved > 100,
                                 actual=resolved, phase="precondition",
                                 detail="slow target should be in range for ~332 ticks"))
        # Outcome phase: leading should achieve high hit rate
        hits = self.results.get('attacker_resolved_hits', 0)
        hit_rate = hits / resolved if resolved > 0 else 0
        checks.append(check_true("Hits Registered", hits > 0,
                                 actual=hits, phase="outcome",
                                 detail="leading should land hits on slow target"))
        checks.append(check_true("Hit Rate > 80%", hit_rate > 0.80,
                                 actual=f"{hit_rate:.1%} ({hits}/{resolved})",
                                 phase="outcome",
                                 detail="slow linear target should be hit consistently"))
        checks.append(check_true("Hit Rate < 100%", hit_rate < 1.0,
                                 actual=f"{hit_rate:.1%}",
                                 phase="outcome",
                                 detail="moving target should cause some misses"))
        return checks


class ProjectileLinearFastTargetScenario(StaticTargetScenario):
    """
    PROJECTILE-003: Accuracy vs Fast Linearly Moving Target (crossing engagement)

    Tests predictive leading against a fast target that crosses through the
    attacker's engagement zone.  The target starts at (100, -1200), out of
    weapon range, heading upward (angle 90).  It reaches full speed (37.5
    px/tick) by tick 9 and enters range at the same tick.  It crosses
    closest approach (~100px) around tick 38 and exits range around tick 63.
    Engagement window: ~54 in-range ticks.

    Same starting position as PROJECTILE-002 (slow target) so the only
    variable is target speed.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-003",
        category="Projectile Weapons",
        subcategory="Moving Targets",
        name="Projectile vs Fast Linear Target (crossing)",
        summary="Validates predictive leading against a fast target crossing through the engagement zone",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Linear_Fast.json",
            "Target Start: (100, -1200), heading 90 (upward)",
            "Target Speed: max 37.5 px/tick (full speed by tick 9)",
            "Enters Range: tick ~9, closest ~100px at tick ~38, exits tick ~63",
            "Engagement Window: ~54 ticks in range",
            "Projectile Speed: 20000 (200 px/tick after scale)",
            "Reload Time: 0.0s (fires every tick)",
            "Damage: 1 per hit (damage_dealt == hits)",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Fast target crosses through engagement zone briefly",
            "Leading angle changes rapidly as target passes",
            "Hit rate expected to be lower than slow target (PROJECTILE-002)",
            "Projectile travel time significant at longer ranges"
        ],
        expected_outcome="Some hits during the ~54-tick engagement window",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        ui_priority=7,
        tags=["accuracy", "projectile", "moving-target", "linear", "fast", "leading", "crossing"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Linear_Fast.json"
    distance = 1204  # Initial center-to-center distance from (0,0) to (100,-1200)

    def custom_setup(self, battle_engine):
        """Position target out of range, heading upward through engagement zone."""
        self.target.position = pygame.math.Vector2(100, -1200)
        self.target.angle = 90
        self.target.movement_policy = 'test_straight_line'

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store hit tracking with resolved stats (excluding in-flight)."""
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        in_flight = self.results.get('attacker_in_flight', 0)
        self.results['shots_fired'] = self.results.get('attacker_total_shots_fired', 0)
        self.results['hits'] = hits
        self.results['in_flight'] = in_flight
        self.results['hit_rate'] = hits / resolved if resolved > 0 else 0.0

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase: verify weapon and target loaded correctly
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        checks.append(check_approx("Target Max Speed", 37.5, self.target.max_speed,
                                   tolerance=0.01))
        # Precondition phase: verify target moved fast and crossed through zone
        target_speed = self.target.velocity.length()
        checks.append(check_approx("Target At Full Speed", 37.5, target_speed,
                                   tolerance=0.01, phase="precondition"))
        target_displacement = self.target.position.distance_to(pygame.math.Vector2(100, -1200))
        checks.append(check_true("Target Displaced > 10000px", target_displacement > 10000,
                                 actual=f"{target_displacement:.0f}px",
                                 phase="precondition",
                                 detail="fast target should have traveled far from start"))
        resolved = self.results.get('attacker_resolved_shots', 0)
        checks.append(check_true("Shots During Engagement", resolved > 20,
                                 actual=resolved, phase="precondition",
                                 detail="fast target should be in range for ~54 ticks"))
        # Outcome phase: leading should hit the fast target
        hits = self.results.get('attacker_resolved_hits', 0)
        hit_rate = hits / resolved if resolved > 0 else 0
        checks.append(check_true("Hits Registered", hits > 0,
                                 actual=hits, phase="outcome",
                                 detail="leading should land some hits on fast target"))
        checks.append(check_true("Hit Rate > 50%", hit_rate > 0.50,
                                 actual=f"{hit_rate:.1%} ({hits}/{resolved})",
                                 phase="outcome",
                                 detail="fast linear target should be hittable with leading"))
        return checks


# ============================================================================
# MOVING TARGET TESTS - ERRATIC
# ============================================================================

class ProjectileErraticSmallTargetScenario(StaticTargetScenario):
    """
    PROJECTILE-004: Accuracy vs Small Erratically Moving Target

    Tests that erratic movement patterns significantly reduce hit rate
    as leading predictions fail when target changes velocity.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-004",
        category="Projectile Weapons",
        subcategory="Moving Targets",
        name="Projectile vs Erratic Small Target (300px)",
        summary="Validates that erratic targets with unpredictable movement are harder to hit",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Erratic_Small.json",
            "Distance: ~300 pixels",
            "Target Movement: Erratic/unpredictable pattern",
            "Target Size: Small (harder to hit)",
            "Projectile Speed: 20000 (200 px/tick)",
            "Reload Time: 0.0s (fires every tick)",
            "Damage: 1 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "Erratic movement invalidates leading predictions",
            "Target changes velocity unpredictably",
            "Small size reduces hit window",
            "Projectiles miss when target dodges",
            "Low hit rate expected"
        ],
        expected_outcome="Low hit rate due to erratic movement",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        ui_priority=6,
        tags=["accuracy", "projectile", "moving-target", "erratic", "small", "difficult"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Erratic_Small.json"
    distance = 300
    track_positions = True

    def custom_setup(self, battle_engine):
        self._tracking_weapon_range = 1000
        self.target.movement_policy = 'test_erratic_leashed'

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase: verify weapon loaded correctly
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        # Precondition phase: verify target moved erratically and stayed in range
        target_speed = self.target.velocity.length()
        checks.append(check_approx("Target At Full Speed", 31.25, target_speed,
                                   tolerance=0.01, phase="precondition"))
        checks.append(check_true("Target Moved From Start", self.target.position.distance_to(
            pygame.math.Vector2(self.distance, 0)) > 1, phase="precondition",
            detail="Erratic target should move from starting position"))
        summary = self.results.get('tracking_summary', {}).get('target', {})
        max_dist = summary.get('max_distance', 0)
        checks.append(check_true("Target Maneuvered (max dist > 350px)", max_dist > 350,
                                 actual=f"{max_dist:.0f}px",
                                 phase="precondition",
                                 detail="erratic target should range across the engagement zone"))
        ticks_in = summary.get('ticks_in_range', 0)
        checks.append(check_true("Target In Range > 500 ticks", ticks_in > 500,
                                 actual=ticks_in, phase="precondition",
                                 detail="small erratic target should stay mostly in range with high thruster"))
        # Outcome phase: must fire enough shots and hit a meaningful fraction.
        # Hit rate varies widely (46%-100%) depending on the erratic movement
        # pattern, so bounds accommodate the full distribution.
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        hit_rate = hits / resolved if resolved > 0 else 0
        checks.append(check_true("Shots Fired > 500", resolved > 500,
                                 actual=resolved, phase="outcome",
                                 detail="weapon should fire most ticks while target in range"))
        checks.append(check_true("Hit Rate > 35%", hit_rate > 0.35,
                                 actual=f"{hit_rate:.1%} ({hits}/{resolved})",
                                 phase="outcome",
                                 detail="weapon must land hits against erratic target"))
        checks.append(check_true("Hit Rate < 100%", hit_rate < 1.00,
                                 actual=f"{hit_rate:.1%}",
                                 phase="outcome",
                                 detail="erratic movement should cause at least some misses"))
        return checks


class ProjectileErraticLargeTargetScenario(StaticTargetScenario):
    """
    PROJECTILE-005: Accuracy vs Large Erratically Moving Target

    Tests that larger erratic targets are easier to hit than small ones
    due to increased hit window despite unpredictable movement.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-005",
        category="Projectile Weapons",
        subcategory="Moving Targets",
        name="Projectile vs Erratic Large Target (300px)",
        summary="Validates that larger targets are easier to hit even with erratic movement",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Erratic_Large.json",
            "Distance: ~300 pixels",
            "Target Movement: Erratic/unpredictable pattern",
            "Target Size: Large (easier to hit)",
            "Projectile Speed: 20000 (200 px/tick)",
            "Reload Time: 0.0s (fires every tick)",
            "Damage: 1 per hit",
            "Test Duration: 1000 ticks"
        ],
        edge_cases=[
            "Erratic movement still invalidates predictions",
            "Larger size increases hit probability",
            "Hit rate should be higher than small erratic target",
            "Size compensates for unpredictable movement"
        ],
        expected_outcome="Higher hit rate than small erratic target (PROJECTILE-004)",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=1000,
        seed=STANDARD_SEED,
        ui_priority=5,
        tags=["accuracy", "projectile", "moving-target", "erratic", "large"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Erratic_Large.json"
    distance = 300
    track_positions = True

    def custom_setup(self, battle_engine):
        self._tracking_weapon_range = 1000
        self.target.movement_policy = 'test_erratic_leashed'

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase: verify weapon loaded correctly
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        # Precondition phase: verify target moved erratically and stayed in range
        target_speed = self.target.velocity.length()
        checks.append(check_approx("Target At Full Speed", 3.125, target_speed,
                                   tolerance=0.01, phase="precondition"))
        checks.append(check_true("Target Moved From Start", self.target.position.distance_to(
            pygame.math.Vector2(self.distance, 0)) > 1, phase="precondition",
            detail="Erratic target should move from starting position"))
        summary = self.results.get('tracking_summary', {}).get('target', {})
        max_dist = summary.get('max_distance', 0)
        checks.append(check_true("Target Maneuvered (max dist > 350px)", max_dist > 350,
                                 actual=f"{max_dist:.0f}px",
                                 phase="precondition",
                                 detail="erratic target should range across the engagement zone"))
        ticks_in = summary.get('ticks_in_range', 0)
        checks.append(check_true("Target In Range > 400 ticks", ticks_in > 400,
                                 actual=ticks_in, phase="precondition",
                                 detail="large erratic target with 4x thrusters should stay mostly in range"))
        # Outcome phase: large target should be hit consistently.
        # The large radius makes it easier to hit than PROJ-004 across all
        # erratic patterns, but some patterns still reduce the hit rate.
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        hit_rate = hits / resolved if resolved > 0 else 0
        checks.append(check_true("Shots Fired > 400", resolved > 400,
                                 actual=resolved, phase="outcome",
                                 detail="weapon should fire most ticks while target in range"))
        checks.append(check_true("Hit Rate > 90%", hit_rate > 0.90,
                                 actual=f"{hit_rate:.1%} ({hits}/{resolved})",
                                 phase="outcome",
                                 detail="large target should be hit consistently despite erratic movement"))
        checks.append(check_true("Hit Rate <= 100%", hit_rate <= 1.00,
                                 actual=f"{hit_rate:.1%}",
                                 phase="outcome",
                                 detail="hit rate must be a valid fraction"))
        return checks


# ============================================================================
# RANGE LIMIT TEST
# ============================================================================

class ProjectileOutOfRangeScenario(StaticTargetScenario):
    """
    PROJECTILE-006: Out of Range - Weapon Fires But No Hits

    Tests that projectiles cannot hit targets beyond weapon's max range (1000px).
    Weapon may fire but projectiles despawn before reaching target.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-006",
        category="Projectile Weapons",
        subcategory="Range Limits",
        name="Projectile Out of Range (1200px > 1000px max)",
        summary="Validates that projectiles cannot hit targets beyond weapon's maximum range",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Stationary.json",
            "Weapon Max Range: 1000 pixels",
            "Distance: 1200 pixels (200px beyond range)",
            "Projectile Speed: 20000 (200 px/tick)",
            "Reload Time: 0.0s (fires every tick)",
            "Damage: 1 per hit",
            "Test Duration: 500 ticks"
        ],
        edge_cases=[
            "Target is beyond weapon range",
            "Weapon may fire but projectiles despawn",
            "Projectiles destroyed at max_range distance",
            "No damage should be dealt",
            "Hard cutoff at max_range, no partial damage"
        ],
        expected_outcome="No damage dealt (damage_dealt == 0)",
        pass_criteria="damage_dealt == 0",
        max_ticks=STANDARD_TEST_TICKS,
        seed=STANDARD_SEED,
        ui_priority=9,
        tags=["range-limit", "out-of-range", "projectile"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Stationary.json"
    distance = PROJECTILE_OUT_OF_RANGE_DISTANCE

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store range-specific results."""
        self.results['distance'] = PROJECTILE_OUT_OF_RANGE_DISTANCE
        self.results['weapon_max_range'] = 1000

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase: verify weapon loaded correctly
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        # Precondition phase: verify target is actually beyond range
        center_dist = self.attacker.position.distance_to(self.target.position)
        checks.append(check_approx("Center Distance", float(PROJECTILE_OUT_OF_RANGE_DISTANCE), center_dist,
                                   tolerance=0.01, phase="precondition"))
        checks.append(check_true("Target Beyond Range", center_dist > 1000,
                                 actual=f"{center_dist:.0f}px vs 1000px max",
                                 phase="precondition",
                                 detail="target must be beyond weapon max range"))
        # Outcome phase: no damage AND verify weapon didn't fire (target out of range)
        shots = self.results.get('attacker_total_shots_fired', 0)
        checks.append(check_exact("No Shots Fired", 0, shots, phase="outcome"))
        checks.append(check_exact("No Damage At Range", 0, self.damage_dealt, phase="outcome"))
        return checks


# ============================================================================
# DAMAGE CONSISTENCY TESTS
# ============================================================================

class ProjectileDamageCloseRangeScenario(StaticTargetScenario):
    """
    PROJECTILE-DMG-010: Damage at Close Range (100px / 10% of max range)

    Tests that projectiles deal consistent full damage at close range.
    Unlike some weapon systems, projectiles don't have damage falloff.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-DMG-010",
        category="Projectile Weapons",
        subcategory="Damage",
        name="Projectile Damage - Close Range (100px / 10%)",
        summary="Validates that projectiles deal full damage at close range without falloff",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Stationary.json",
            "Distance: 100 pixels (10% of 1000px max range)",
            "Projectile Speed: 20000 (200 px/tick)",
            "Travel Time: 100px / 200px/tick = ~1 tick",
            "Reload Time: 0.0s (fires every tick)",
            "Damage Per Hit: 1",
            "No Damage Falloff: Projectiles deal full damage at any range",
            "Test Duration: 200 ticks"
        ],
        edge_cases=[
            "Very short travel time at close range",
            "Each hit should deal exactly 1 damage",
            "No damage falloff or range penalty"
        ],
        expected_outcome="damage_dealt == number of hits (no falloff)",
        pass_criteria="damage_dealt > 0",
        max_ticks=200,
        seed=STANDARD_SEED,
        ui_priority=10,
        tags=["damage", "projectile", "close-range", "consistency"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 100

    def custom_setup(self, battle_engine):
        """Calculate travel time for results."""
        self.travel_time = calculate_projectile_travel_time(100, 20000)

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store damage consistency results."""
        self.results['travel_time_seconds'] = self.travel_time
        self.results['damage_per_hit'] = 1

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        # Precondition phase
        center_dist = self.attacker.position.distance_to(self.target.position)
        checks.append(check_approx("Center Distance", 100.0, center_dist,
                                   tolerance=0.01, phase="precondition"))
        # Outcome phase: 100% resolved hit rate proves no damage falloff
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        checks.append(check_true("Shots Fired", resolved > 50,
                                 actual=resolved, phase="outcome"))
        checks.append(check_true("100% Resolved Hit Rate (No Falloff)", resolved > 0 and hits == resolved,
                                 actual=f"{hits}/{resolved}",
                                 phase="outcome",
                                 detail="close range: every resolved shot must hit"))
        return checks


class ProjectileDamageMidRangeScenario(StaticTargetScenario):
    """
    PROJECTILE-DMG-050: Damage at Mid-Range (500px / 50% of max range)

    Tests that projectiles maintain full damage at mid-range.
    Travel time increases but damage remains constant.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-DMG-050",
        category="Projectile Weapons",
        subcategory="Damage",
        name="Projectile Damage - Mid Range (500px / 50%)",
        summary="Validates that projectiles deal full damage at mid-range despite increased travel time",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Stationary.json",
            "Distance: 500 pixels (50% of 1000px max range)",
            "Projectile Speed: 20000 (200 px/tick)",
            "Travel Time: 500px / 200px/tick = ~3 ticks",
            "Reload Time: 0.0s (fires every tick)",
            "Damage Per Hit: 1",
            "No Damage Falloff: Full damage at any range",
            "Test Duration: 300 ticks"
        ],
        edge_cases=[
            "Increased travel time but same damage",
            "Each hit should deal exactly 1 damage",
            "No damage reduction at mid-range",
            "Travel time doesn't affect damage output"
        ],
        expected_outcome="damage_dealt == number of hits (no falloff)",
        pass_criteria="damage_dealt > 0",
        max_ticks=300,
        seed=STANDARD_SEED,
        ui_priority=9,
        tags=["damage", "projectile", "mid-range", "consistency"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 500

    def custom_setup(self, battle_engine):
        """Calculate travel time for results."""
        self.travel_time = calculate_projectile_travel_time(500, 20000)

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store damage consistency results."""
        self.results['travel_time_seconds'] = self.travel_time
        self.results['damage_per_hit'] = 1

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        # Precondition phase
        center_dist = self.attacker.position.distance_to(self.target.position)
        checks.append(check_approx("Center Distance", 500.0, center_dist,
                                   tolerance=0.01, phase="precondition"))
        # Outcome phase: 100% resolved hit rate proves no damage falloff at mid range
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        checks.append(check_true("Shots Fired", resolved > 50,
                                 actual=resolved, phase="outcome"))
        checks.append(check_true("100% Resolved Hit Rate (No Falloff)", resolved > 0 and hits == resolved,
                                 actual=f"{hits}/{resolved}",
                                 phase="outcome",
                                 detail="mid range: every resolved shot must hit (no falloff)"))
        return checks


class ProjectileDamageLongRangeScenario(StaticTargetScenario):
    """
    PROJECTILE-DMG-090: Damage at Long Range (900px / 90% of max range)

    Tests that projectiles maintain full damage even at edge of range.
    Maximum travel time but damage remains consistent.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-DMG-090",
        category="Projectile Weapons",
        subcategory="Damage",
        name="Projectile Damage - Long Range (900px / 90%)",
        summary="Validates that projectiles deal full damage at edge of range despite maximum travel time",
        conditions=[
            "Attacker: Test_Attacker_Proj360.json",
            "Target: Test_Target_Stationary.json",
            "Distance: 900 pixels (90% of 1000px max range)",
            "Projectile Speed: 20000 (200 px/tick)",
            "Travel Time: 900px / 200px/tick = ~5 ticks",
            "Reload Time: 0.0s (fires every tick)",
            "Damage Per Hit: 1",
            "No Damage Falloff: Full damage even at max range",
            "Test Duration: 400 ticks"
        ],
        edge_cases=[
            "Maximum travel time (0.6s per shot)",
            "Edge of weapon range",
            "Still deals full 1 damage per hit",
            "No damage reduction at long range",
            "Travel time is significant but damage unchanged"
        ],
        expected_outcome="damage_dealt == number of hits (no falloff at edge of range)",
        pass_criteria="simulation_completes (ticks_run > 0)",
        max_ticks=400,
        seed=STANDARD_SEED,
        ui_priority=8,
        tags=["damage", "projectile", "long-range", "max-range", "consistency"]
    )

    attacker_ship = "Test_Attacker_Proj360.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 900

    def custom_setup(self, battle_engine):
        """Calculate travel time for results."""
        self.travel_time = calculate_projectile_travel_time(900, 20000)

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store damage consistency results."""
        self.results['travel_time_seconds'] = self.travel_time
        self.results['damage_per_hit'] = 1

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data phase
        weapon = self.get_ability(self.attacker, 'ProjectileWeaponAbility')
        if weapon:
            checks.append(check_exact("Weapon Damage", 1, weapon.damage))
            checks.append(check_exact("Weapon Range", 1000, weapon.range))
            checks.append(check_exact("Projectile Speed", 20000, weapon.projectile_speed))
            checks.append(check_exact("Reload Time", 0.0, weapon.reload_time))
        checks.append(check_exact("Target Mass", STATIONARY_TARGET_MASS, self.target.mass))
        # Precondition phase
        center_dist = self.attacker.position.distance_to(self.target.position)
        checks.append(check_approx("Center Distance", 900.0, center_dist,
                                   tolerance=0.01, phase="precondition"))
        # Outcome phase: 100% resolved hit rate proves no damage falloff at edge of range
        resolved = self.results.get('attacker_resolved_shots', 0)
        hits = self.results.get('attacker_resolved_hits', 0)
        checks.append(check_true("Shots Fired", resolved > 50,
                                 actual=resolved, phase="outcome"))
        checks.append(check_true("100% Resolved Hit Rate (No Falloff)", resolved > 0 and hits == resolved,
                                 actual=f"{hits}/{resolved}",
                                 phase="outcome",
                                 detail="edge of range: every resolved shot must hit (no falloff)"))
        return checks


# =============================================================================
# RESOURCE DEPENDENCY TESTS (PROJECTILE-RES-001 to 003)
# =============================================================================
# These ComparisonScenarios prove projectile weapons with
# ResourceConsumption(ammo) stop firing when ammo depletes.

PROJ_RES_TEST_TICKS = 500
PROJ_RES_ATTACKER_FULL = "Test_Attacker_ProjRapid_HighAmmo.json"
PROJ_RES_ATTACKER_HALF = "Test_Attacker_ProjRapid_HalfAmmo.json"
PROJ_RES_ATTACKER_NONE = "Test_Attacker_ProjRapid_NoAmmo.json"
PROJ_RES_TARGET = "Test_Target_Stationary.json"


class ProjectileStopsWithoutAmmoScenario(ComparisonScenario):
    """
    PROJECTILE-RES-001: Projectile Stops Without Ammo

    Battle A: Projectile + 100k ammo (fires every tick)
    Battle B: Projectile + no ammo (cannot fire)

    Proves that a projectile weapon with activation ammo cost cannot fire
    without an ammo source.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-RES-001",
        category="ProjectileWeaponAbility",
        subcategory="Resource Dependency",
        name="Projectile Stops Without Ammo",
        summary="Projectile weapon with ammo cost but no magazine cannot fire",
        conditions=[
            f"Attacker (full ammo): {PROJ_RES_ATTACKER_FULL}",
            f"Attacker (no ammo): {PROJ_RES_ATTACKER_NONE}",
            f"Target: {PROJ_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PROJ_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Weapon exists and is operational but cannot afford activation cost",
            "Zero shots fired, zero damage dealt",
        ],
        expected_outcome="Full-ammo attacker deals damage. No-ammo attacker deals 0.",
        pass_criteria="variant damage == 0, variant shots_fired == 0",
        max_ticks=PROJ_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["projectile", "ammo", "resource", "no-ammo", "comparison"],
    )

    baseline_attacker_ship = PROJ_RES_ATTACKER_FULL
    baseline_target_ship = PROJ_RES_TARGET
    variant_attacker_ship = PROJ_RES_ATTACKER_NONE
    variant_target_ship = PROJ_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline fired and dealt damage
        checks.append(check_true(
            "Full-Ammo Attacker Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: no-ammo attacker dealt zero damage
        checks.append(check_exact(
            "No-Ammo Attacker — Zero Damage",
            0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        # Outcome: no-ammo attacker fired zero shots
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "No-Ammo Attacker — Zero Shots",
            0, variant_shots,
            phase="outcome",
        ))

        return checks


class ProjectileStopsAtHalfAmmoScenario(ComparisonScenario):
    """
    PROJECTILE-RES-002: Projectile Stops At 50% Ammo

    Battle A: Projectile + 100k ammo (fires all 500 ticks)
    Battle B: Projectile + 250 ammo (fires ~250 ticks then stops)

    Proves that a projectile weapon fires until ammo depletes, then stops.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-RES-002",
        category="ProjectileWeaponAbility",
        subcategory="Resource Dependency",
        name="Projectile Stops At 50% Ammo",
        summary="Projectile fires ~250 shots with 250 ammo then stops",
        conditions=[
            f"Attacker (full ammo): {PROJ_RES_ATTACKER_FULL}",
            f"Attacker (half ammo): {PROJ_RES_ATTACKER_HALF} (250 ammo = 250 shots)",
            f"Target: {PROJ_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PROJ_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Weapon fires until ammo runs out, then silently stops",
            "Damage should be roughly half of full-ammo baseline",
        ],
        expected_outcome="Half-ammo attacker fires ~250 shots (~half of baseline).",
        pass_criteria="variant damage < baseline, variant shots ≈ 250",
        max_ticks=PROJ_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["projectile", "ammo", "resource", "depletion", "comparison"],
    )

    baseline_attacker_ship = PROJ_RES_ATTACKER_FULL
    baseline_target_ship = PROJ_RES_TARGET
    variant_attacker_ship = PROJ_RES_ATTACKER_HALF
    variant_target_ship = PROJ_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline dealt damage
        checks.append(check_true(
            "Full-Ammo Attacker Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: half-ammo dealt some damage
        checks.append(check_true(
            "Half-Ammo Attacker Dealt Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: half-ammo dealt less than full-ammo
        checks.append(check_true(
            "Half-Ammo Dealt Less Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"full={self.baseline_damage_dealt}, half={self.variant_damage_dealt}",
            phase="outcome",
        ))

        # Outcome: half-ammo fired approximately 250 shots
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "Half-Ammo Shots Fired", 250, variant_shots,
            phase="outcome",
        ))

        # Outcome: half-ammo fired fewer shots than full-ammo baseline
        checks.append(check_true(
            "Half-Ammo Fired Fewer Shots",
            variant_shots < baseline_shots,
            detail=f"variant={variant_shots}, baseline={baseline_shots}",
            phase="outcome",
        ))

        return checks


class ProjectileControlWithAmmoScenario(ComparisonScenario):
    """
    PROJECTILE-RES-003: Projectile Functions With Sufficient Ammo (Control)

    Battle A: Projectile + 100k ammo
    Battle B: Projectile + 100k ammo (identical)

    Control test: both battles use the same ship. Damage should be identical.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-RES-003",
        category="ProjectileWeaponAbility",
        subcategory="Resource Dependency",
        name="Projectile Functions With Ammo (Control)",
        summary="Control: identical attackers with sufficient ammo produce identical damage",
        conditions=[
            f"Attacker (both): {PROJ_RES_ATTACKER_FULL} (100k ammo)",
            f"Target: {PROJ_RES_TARGET} (stationary, extreme HP armor)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PROJ_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "Control test — no difference between battles",
            "Validates comparison infrastructure with identical setups",
        ],
        expected_outcome="Both battles produce identical damage.",
        pass_criteria="variant damage == baseline damage",
        max_ticks=PROJ_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["projectile", "ammo", "resource", "control", "comparison"],
    )

    baseline_attacker_ship = PROJ_RES_ATTACKER_FULL
    baseline_target_ship = PROJ_RES_TARGET
    variant_attacker_ship = PROJ_RES_ATTACKER_FULL
    variant_target_ship = PROJ_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Outcome: identical damage
        checks.append(check_exact(
            "Control — Identical Damage",
            self.baseline_damage_dealt,
            self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# GENERIC RESOURCE TESTS — METALS (PROJECTILE-RES-METALS-001 to 002)
# =============================================================================

PROJ_METALS_ATTACKER_FULL = "Test_Attacker_ProjRapid_HighMetals.json"
PROJ_METALS_ATTACKER_NONE = "Test_Attacker_ProjRapid_NoMetals.json"


class ProjectileWithMetalsFires(ComparisonScenario):
    """
    PROJECTILE-RES-METALS-001: Projectile With Metals Fires

    Proves the resource system is generic: a projectile consuming "metals"
    works identically to one consuming "ammo".
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-RES-METALS-001",
        category="ProjectileWeaponAbility",
        subcategory="Generic Resource",
        name="Projectile With Metals Fires",
        summary="Projectile consuming metals (planetary resource) fires normally with supply",
        conditions=[
            f"Attacker (with metals): {PROJ_METALS_ATTACKER_FULL}",
            f"Attacker (no metals): {PROJ_METALS_ATTACKER_NONE}",
            f"Target: {PROJ_RES_TARGET}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PROJ_RES_TEST_TICKS} ticks",
        ],
        edge_cases=[
            "'metals' is a planetary resource, not a standard operational resource",
            "Proves resource system accepts any resource type from data files",
        ],
        expected_outcome="With metals: fires and deals damage. Without: zero shots.",
        pass_criteria="baseline damage > 0, variant damage == 0, variant shots == 0",
        max_ticks=PROJ_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["projectile", "metals", "generic-resource", "comparison"],
    )

    baseline_attacker_ship = PROJ_METALS_ATTACKER_FULL
    baseline_target_ship = PROJ_RES_TARGET
    variant_attacker_ship = PROJ_METALS_ATTACKER_NONE
    variant_target_ship = PROJ_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        checks.append(check_true(
            "With-Metals Attacker Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        checks.append(check_exact(
            "No-Metals Attacker — Zero Damage",
            0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_exact(
            "No-Metals Attacker — Zero Shots",
            0, variant_shots,
            phase="outcome",
        ))

        return checks


class ProjectileWithMetalsControl(ComparisonScenario):
    """
    PROJECTILE-RES-METALS-002: Projectile With Metals Control

    Control: identical metals-consuming projectiles produce identical damage.
    """

    metadata = TestMetadata(
        test_id="PROJECTILE-RES-METALS-002",
        category="ProjectileWeaponAbility",
        subcategory="Generic Resource",
        name="Projectile With Metals Control",
        summary="Control: identical metals-consuming projectiles produce identical damage",
        conditions=[
            f"Attacker (both): {PROJ_METALS_ATTACKER_FULL}",
            f"Target: {PROJ_RES_TARGET}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {PROJ_RES_TEST_TICKS} ticks",
        ],
        edge_cases=["Control test for generic resource support"],
        expected_outcome="Both battles produce identical damage.",
        pass_criteria="variant damage == baseline damage",
        max_ticks=PROJ_RES_TEST_TICKS,
        seed=STANDARD_SEED,
        tags=["projectile", "metals", "generic-resource", "control", "comparison"],
    )

    baseline_attacker_ship = PROJ_METALS_ATTACKER_FULL
    baseline_target_ship = PROJ_RES_TARGET
    variant_attacker_ship = PROJ_METALS_ATTACKER_FULL
    variant_target_ship = PROJ_RES_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, ab) -> list:
        checks = self._template_preconditions()
        checks.append(check_exact(
            "Control — Identical Damage",
            self.baseline_damage_dealt, self.variant_damage_dealt,
            phase="outcome",
        ))
        return checks


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    'ProjectileStationaryTargetScenario',
    'ProjectileLinearSlowTargetScenario',
    'ProjectileLinearFastTargetScenario',
    'ProjectileErraticSmallTargetScenario',
    'ProjectileErraticLargeTargetScenario',
    'ProjectileOutOfRangeScenario',
    'ProjectileDamageCloseRangeScenario',
    'ProjectileDamageMidRangeScenario',
    'ProjectileDamageLongRangeScenario',
    'ProjectileStopsWithoutAmmoScenario',
    'ProjectileStopsAtHalfAmmoScenario',
    'ProjectileControlWithAmmoScenario',
    'ProjectileWithMetalsFires',
    'ProjectileWithMetalsControl',
]
