"""
CommandAndControl Test Scenarios (CNC-001 to CNC-005)

These tests validate the per-component RequiresCommandAndControl ability.
When a component declares RequiresCommandAndControl and the ship has no
active CommandAndControl provider, that component becomes non-operational
— its stats don't contribute to the ship.

This is enforced in RequiresCommandAndControl.update(), which checks for
active C&C providers each tick. Non-operational components are skipped
during stat aggregation (thrust, shields, weapon stats, etc.).

Test pattern: Ship WITH C&C bridge vs identical ship WITHOUT bridge.
The variant (no bridge) should show zero contribution from C&C-dependent
components.

CNC-005 tests mid-battle destruction: bridge in ARMOR layer (outer,
hit first) is destroyed by enemy fire, causing C&C-dependent components
to lose operational status mid-battle.
"""

from simulation_tests.scenarios import TestMetadata
from simulation_tests.scenarios.templates import ComparisonScenario
from simulation_tests.scenarios.validation import check_exact, check_true
from simulation_tests.test_constants import (
    POINT_BLANK_DISTANCE,
    STANDARD_SEED,
    CNC_TEST_TICKS,
    CNC_BRIDGE_HP,
)


# =============================================================================
# COMMON SHIP REFERENCES
# =============================================================================

STANDARD_TARGET = "Test_Target_Stationary.json"
STANDARD_ATTACKER = "Test_Attacker_Beam_Guaranteed.json"
DURABLE_ATTACKER = "Test_Attacker_Beam_Guaranteed_Durable.json"


# =============================================================================
# CNC-001: Beam Weapon Disabled Without C&C
# =============================================================================

class CNCBeamDisabledScenario(ComparisonScenario):
    """
    CNC-001: Beam Weapon Disabled Without C&C

    Battle A: Beam with C&C bridge → fires normally, deals damage
    Battle B: Beam WITHOUT bridge → beam non-operational, zero damage

    The beam component has RequiresCommandAndControl. Without an active
    CommandAndControl provider, it becomes non-operational and cannot fire.
    """

    metadata = TestMetadata(
        test_id="CNC-001",
        category="CommandAndControl",
        subcategory="Beam Weapon",
        name="Beam Weapon Disabled Without C&C",
        summary="Beam with RequiresCommandAndControl cannot fire without a bridge",
        conditions=[
            "Attacker (with C&C): Test_Attacker_Beam_CNC.json (bridge + C&C beam)",
            "Attacker (no C&C): Test_Attacker_Beam_NoCNC.json (C&C beam, NO bridge)",
            f"Target: {STANDARD_TARGET}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {CNC_TEST_TICKS} ticks",
        ],
        edge_cases=["Beam exists but is non-operational due to missing C&C"],
        expected_outcome="With C&C: normal damage. Without C&C: zero damage.",
        pass_criteria="variant_damage_dealt == 0, baseline_damage_dealt > 0",
        max_ticks=CNC_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["cnc", "command-control", "beam", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam_CNC.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Beam_NoCNC.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline fired and dealt damage
        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        # Outcome: variant dealt zero damage (beam non-operational)
        checks.append(check_exact(
            "No Damage Without C&C", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# CNC-002: Projectile Weapon Disabled Without C&C
# =============================================================================

class CNCProjectileDisabledScenario(ComparisonScenario):
    """
    CNC-002: Projectile Weapon Disabled Without C&C

    Battle A: Projectile with C&C bridge → fires normally
    Battle B: Projectile WITHOUT bridge → non-operational, zero damage
    """

    metadata = TestMetadata(
        test_id="CNC-002",
        category="CommandAndControl",
        subcategory="Projectile Weapon",
        name="Projectile Weapon Disabled Without C&C",
        summary="Projectile with RequiresCommandAndControl cannot fire without a bridge",
        conditions=[
            "Attacker (with C&C): Test_Attacker_Proj_CNC.json (bridge + C&C projectile)",
            "Attacker (no C&C): Test_Attacker_Proj_NoCNC.json (C&C projectile, NO bridge)",
            f"Target: {STANDARD_TARGET}",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {CNC_TEST_TICKS} ticks",
        ],
        edge_cases=["Projectile exists but is non-operational due to missing C&C"],
        expected_outcome="With C&C: normal damage. Without C&C: zero damage.",
        pass_criteria="variant_damage_dealt == 0, baseline_damage_dealt > 0",
        max_ticks=CNC_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["cnc", "command-control", "projectile", "comparison"],
    )

    baseline_attacker_ship = "Test_Attacker_Proj_CNC.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Attacker_Proj_NoCNC.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        checks.append(check_true(
            "Baseline Dealt Damage",
            self.baseline_damage_dealt > 0,
            detail=f"damage={self.baseline_damage_dealt}",
        ))

        checks.append(check_exact(
            "No Damage Without C&C", 0.0, self.variant_damage_dealt,
            phase="outcome",
        ))

        return checks


# =============================================================================
# CNC-003: Shield Disabled Without C&C
# =============================================================================

class CNCShieldDisabledScenario(ComparisonScenario):
    """
    CNC-003: Shield Disabled Without C&C

    Battle A: Target with C&C bridge + C&C shield → shield absorbs damage
    Battle B: Target with C&C shield but NO bridge → shield non-operational

    When the shield is non-operational, it contributes 0 to max_shields,
    so all damage goes directly to hull.
    """

    metadata = TestMetadata(
        test_id="CNC-003",
        category="CommandAndControl",
        subcategory="Shield",
        name="Shield Disabled Without C&C",
        summary="Shield with RequiresCommandAndControl provides no protection without bridge",
        conditions=[
            f"Attacker: {STANDARD_ATTACKER} (1 dmg, guaranteed hit)",
            "Target (with C&C): Test_Target_Shield_CNC.json (bridge + C&C shield)",
            "Target (no C&C): Test_Target_Shield_NoCNC.json (C&C shield, NO bridge)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {CNC_TEST_TICKS} ticks",
        ],
        edge_cases=["Shield component exists but contributes 0 to max_shields"],
        expected_outcome="With C&C: shield absorbs, less hull damage. Without C&C: all damage to hull.",
        pass_criteria="variant takes more hull damage than baseline",
        max_ticks=CNC_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["cnc", "command-control", "shield", "comparison"],
    )

    baseline_attacker_ship = STANDARD_ATTACKER
    baseline_target_ship = "Test_Target_Shield_CNC.json"
    variant_attacker_ship = STANDARD_ATTACKER
    variant_target_ship = "Test_Target_Shield_NoCNC.json"
    distance = POINT_BLANK_DISTANCE

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: variant should have 0 shields (non-operational)
        checks.append(check_exact(
            "No Shields Without C&C", 0.0, self.target.max_shields,
        ))

        # Precondition: baseline shield absorbed some damage
        checks.append(check_true(
            "Baseline Had Shields",
            self.baseline_damage_dealt < CNC_TEST_TICKS,
            detail=f"damage={self.baseline_damage_dealt} (should be < {CNC_TEST_TICKS} if shield absorbed)",
        ))

        # Outcome: variant took all damage (no shield protection)
        checks.append(check_true(
            "More Damage Without C&C Shield",
            self.variant_damage_dealt > self.baseline_damage_dealt,
            detail=f"variant={self.variant_damage_dealt}, baseline={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# CNC-004: Engine Disabled Without C&C
# =============================================================================

class CNCEngineDisabledScenario(ComparisonScenario):
    """
    CNC-004: Engine Disabled Without C&C

    Battle A: Ship with C&C bridge + C&C engine → has thrust, has max_speed
    Battle B: Ship with C&C engine but NO bridge → engine non-operational, no thrust

    We verify the stats directly: max_speed and total_thrust should be 0
    when the engine is non-operational.
    """

    metadata = TestMetadata(
        test_id="CNC-004",
        category="CommandAndControl",
        subcategory="Engine",
        name="Engine Disabled Without C&C",
        summary="Engine with RequiresCommandAndControl provides no thrust without bridge",
        conditions=[
            "Ship (with C&C): Test_Engine_CNC.json (bridge + C&C engine)",
            "Ship (no C&C): Test_Engine_NoCNC.json (C&C engine, NO bridge)",
            "No combat — just verify stats (thrust, max_speed)",
            f"Test Duration: {CNC_TEST_TICKS} ticks",
        ],
        edge_cases=["Engine contributes 0 thrust when non-operational"],
        expected_outcome="With C&C: thrust > 0. Without C&C: thrust = 0.",
        pass_criteria="variant total_thrust == 0, baseline total_thrust > 0",
        max_ticks=CNC_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["cnc", "command-control", "engine", "comparison"],
    )

    baseline_attacker_ship = "Test_Engine_CNC.json"
    baseline_target_ship = STANDARD_TARGET
    variant_attacker_ship = "Test_Engine_NoCNC.json"
    variant_target_ship = STANDARD_TARGET
    distance = POINT_BLANK_DISTANCE
    expect_different_damage = False  # Tests engine stats, not damage

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: variant should have 0 thrust (engine non-operational)
        checks.append(check_exact(
            "No Thrust Without C&C", 0, self.attacker.total_thrust,
        ))

        checks.append(check_exact(
            "No Max Speed Without C&C", 0.0, self.attacker.max_speed,
        ))

        return checks


# =============================================================================
# CNC-005: Bridge Destroyed Mid-Battle
# =============================================================================

class CNCBridgeDestroyedScenario(ComparisonScenario):
    """
    CNC-005: Bridge Destroyed Mid-Battle

    Both ships have a C&C beam in CORE and a bridge in ARMOR.
    An enemy fires at each ship.

    Battle A: Indestructible bridge (1B HP) → beam fires full test
    Battle B: Destructible bridge (50 HP) in ARMOR layer → bridge destroyed
              after ~50 hits, beam loses C&C and stops firing

    Bridge is in ARMOR (radius_pct=1.0, outermost) so damage hits it
    before the CORE weapons.
    """

    metadata = TestMetadata(
        test_id="CNC-005",
        category="CommandAndControl",
        subcategory="Destruction",
        name="Bridge Destroyed Mid-Battle Disables Weapons",
        summary="Destroying the bridge mid-battle causes C&C-dependent weapons to stop",
        conditions=[
            f"Enemy: {STANDARD_ATTACKER} (fires at both test ships)",
            "Ship (strong bridge): Test_Attacker_Beam_CNC_StrongBridge.json (1B HP bridge in ARMOR)",
            "Ship (weak bridge): Test_Attacker_Beam_CNC_WeakBridge.json (50 HP bridge in ARMOR)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {CNC_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"Bridge ({CNC_BRIDGE_HP} HP) destroyed at ~tick {CNC_BRIDGE_HP}",
            "Beam fires before bridge destruction, stops after",
        ],
        expected_outcome="Variant fires initially but stops mid-battle. "
                         "Baseline fires throughout. Variant deals less total damage.",
        pass_criteria="variant_damage_dealt > 0 AND variant_damage_dealt < baseline_damage_dealt",
        max_ticks=CNC_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["cnc", "command-control", "destruction", "mid-battle", "comparison"],
    )

    # Both ships attack the standard target, but also get attacked
    # The "attacker" is our test ship; the "target" receives fire FROM our ship
    # We need the enemy to fire AT our test ship too.
    # ComparisonScenario sets attacker.current_target = target,
    # but we also need target to fire back at attacker.
    #
    # Actually, for CNC-005 we need a DUEL setup where both ships fire at each
    # other. The test ship has bridge in ARMOR, beam in CORE. The enemy fires
    # at the test ship, destroying the bridge. Then the test ship's beam stops.
    #
    # Let's use a slightly different approach: the "target" is the CNC ship
    # (with bridge to be destroyed), and the "attacker" is the standard beam
    # that fires at it. We measure how much the CNC ship fires back.

    baseline_attacker_ship = DURABLE_ATTACKER
    baseline_target_ship = "Test_Attacker_Beam_CNC_StrongBridge.json"
    variant_attacker_ship = DURABLE_ATTACKER
    variant_target_ship = "Test_Attacker_Beam_CNC_WeakBridge.json"
    distance = POINT_BLANK_DISTANCE
    force_fire = True

    def configure_baseline(self, engine):
        """Set up mutual targeting so CNC ship fires back."""
        self.target.current_target = self.attacker

    def configure_variant(self, engine):
        """Set up mutual targeting so CNC ship fires back."""
        self.target.current_target = self.attacker

    def update(self, battle_engine):
        """Force both attacker AND target to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True
        if self.target and self.target.is_alive:
            self.target.comp_trigger_pulled = True
        self._track_tick(battle_engine.tick_counter)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: the weak bridge was destroyed
        # Find bridge component in target's ARMOR layer
        from game.core.constants import LayerType
        bridge_alive = True
        if LayerType.ARMOR in self.target.layers:
            for comp in self.target.layers[LayerType.ARMOR].components:
                if comp.has_ability('CommandAndControl'):
                    bridge_alive = comp.is_active
                    break

        checks.append(check_true(
            "Variant Bridge Destroyed",
            not bridge_alive,
            detail=f"bridge_alive={bridge_alive}",
        ))

        # Outcome: variant CNC ship dealt SOME damage (fired before bridge died)
        # We need to measure how much the TARGET (CNC ship) fired back
        # The target's weapon stats are collected as variant_target_*
        target_weapon_stats = {}
        for key, val in self.results.items():
            if key.startswith('variant_target_'):
                target_weapon_stats[key] = val

        # Check via the attacker's HP loss (CNC ship fired at attacker)
        attacker_damage = self.attacker.max_hp - self.attacker.hp
        checks.append(check_true(
            "CNC Ship Fired Before Bridge Lost",
            attacker_damage > 0,
            detail=f"attacker_damage_taken={attacker_damage}",
            phase="outcome",
        ))

        # Outcome: baseline CNC ship dealt MORE damage (bridge never destroyed)
        # Use per-weapon stats to measure how many shots the CNC ship fired
        variant_shots = self.results.get('variant_target_total_shots_fired', 0)
        baseline_shots = self.results.get('baseline_target_total_shots_fired', 0)

        checks.append(check_true(
            "Weak Bridge Ship Fired Fewer Shots",
            variant_shots < baseline_shots,
            detail=f"variant_shots={variant_shots}, baseline_shots={baseline_shots}",
            phase="outcome",
        ))

        checks.append(check_true(
            "Strong Bridge Ship Fired Full Test",
            baseline_shots > 0,
            detail=f"baseline_shots={baseline_shots}",
            phase="outcome",
        ))

        return checks


# =============================================================================
# CNC-006: Bridge Redundancy — Two Bridges Survive Single Destruction
# =============================================================================

class CNCBridgeRedundancyScenario(ComparisonScenario):
    """
    CNC-006: Bridge Redundancy

    Both ships have a C&C beam in CORE and bridges in ARMOR.
    An enemy fires at each ship.

    Battle A: Single bridge (50 HP) in ARMOR → destroyed at ~tick 50,
              beam loses C&C and stops firing
    Battle B: Two bridges (50 HP each) in ARMOR → first destroyed at ~tick 50,
              but second bridge still provides C&C → beam keeps firing
              until second bridge destroyed at ~tick 100

    The dual-bridge ship should deal more total damage because it maintains
    C&C for longer.
    """

    metadata = TestMetadata(
        test_id="CNC-006",
        category="CommandAndControl",
        subcategory="Redundancy",
        name="Bridge Redundancy — Second Bridge Maintains C&C",
        summary="Two bridges provide redundancy: destroying one does not disable C&C-dependent weapons",
        conditions=[
            f"Enemy: {DURABLE_ATTACKER} (fires at both test ships)",
            "Ship (1 bridge): Test_Attacker_Beam_CNC_WeakBridge.json (1x 50 HP bridge in ARMOR)",
            "Ship (2 bridges): Test_Attacker_Beam_CNC_DualBridge.json (2x 50 HP bridge in ARMOR)",
            f"Distance: {POINT_BLANK_DISTANCE} pixels",
            f"Test Duration: {CNC_TEST_TICKS} ticks",
        ],
        edge_cases=[
            f"First bridge ({CNC_BRIDGE_HP} HP) destroyed at ~tick {CNC_BRIDGE_HP}",
            "Second bridge provides C&C continuity after first is destroyed",
            "Dual-bridge ship fires for ~100 ticks vs single-bridge ~50 ticks",
        ],
        expected_outcome="Dual-bridge variant deals more damage than single-bridge baseline "
                         "because C&C is maintained longer.",
        pass_criteria="variant_damage_dealt > baseline_damage_dealt, both > 0",
        max_ticks=CNC_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        tags=["cnc", "command-control", "redundancy", "bridge", "comparison"],
    )

    baseline_attacker_ship = DURABLE_ATTACKER
    baseline_target_ship = "Test_Attacker_Beam_CNC_WeakBridge.json"
    variant_attacker_ship = DURABLE_ATTACKER
    variant_target_ship = "Test_Attacker_Beam_CNC_DualBridge.json"
    distance = POINT_BLANK_DISTANCE
    force_fire = True

    def configure_baseline(self, engine):
        """Set up mutual targeting so CNC ship fires back."""
        self.target.current_target = self.attacker

    def configure_variant(self, engine):
        """Set up mutual targeting so CNC ship fires back."""
        self.target.current_target = self.attacker

    def update(self, battle_engine):
        """Force both attacker AND target to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True
        if self.target and self.target.is_alive:
            self.target.comp_trigger_pulled = True
        self._track_tick(battle_engine.tick_counter)

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: single-bridge ship fired some shots before bridge died
        baseline_shots = self.results.get('baseline_target_total_shots_fired', 0)
        checks.append(check_true(
            "Single Bridge Ship Fired",
            baseline_shots > 0,
            detail=f"baseline_shots={baseline_shots}",
        ))

        # Precondition: dual-bridge ship also fired
        variant_shots = self.results.get('variant_target_total_shots_fired', 0)
        checks.append(check_true(
            "Dual Bridge Ship Fired",
            variant_shots > 0,
            detail=f"variant_shots={variant_shots}",
        ))

        # Outcome: dual-bridge ship fired more shots (C&C lasted longer)
        checks.append(check_true(
            "Dual Bridge Fired More Shots",
            variant_shots > baseline_shots,
            detail=f"variant_shots={variant_shots}, baseline_shots={baseline_shots}",
            phase="outcome",
        ))

        return checks
