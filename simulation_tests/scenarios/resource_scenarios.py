"""
Resource Consumption Test Scenarios (RESOURCE-001 to RESOURCE-006)

These tests validate that weapons correctly consume and respect resource limits:
- Energy consumption per beam shot
- Ammo consumption per projectile/seeker shot
- Weapons stop firing when resources depleted
- Resource regeneration (energy generation)

Test Coverage:
- Beam Energy: 2 tests (with/without generator)
- Projectile Ammo: 2 tests (consumption/depletion)
- Seeker Ammo: 2 tests (consumption/depletion)

Key Mechanics:
- ResourceConsumption: Constant drain or activation cost
- ResourceStorage: Adds capacity to ship's resource pool
- ResourceGeneration: Regenerates resource per tick

These tests use small storage components (25 energy, 10 ammo) to verify
depletion behavior without requiring many shots.
"""

import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata


# ============================================================================
# BEAM ENERGY CONSUMPTION TESTS
# ============================================================================

class BeamEnergyConsumptionWithGeneratorScenario(TestScenario):
    """
    RESOURCE-001: Beam Weapon Consumes Energy (With Generator)

    Tests that beam weapons consume energy per shot, and that energy
    regeneration allows continued firing. Validates the energy consumption
    and regeneration mechanics work correctly together.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-001",
        category="Resource System",
        subcategory="Energy",
        name="Beam Energy Consumption with Regeneration",
        summary="Validates beam weapon consumes energy per shot and generator regenerates energy for continued firing",
        conditions=[
            "Attacker: test_beam_med_acc + test_storage_energy_small + test_gen_fusion",
            "Target: Test_Target_Stationary.json",
            "Energy Storage: 25 units (small battery)",
            "Energy Cost: 10 per beam shot",
            "Energy Generation: 100 per second (test_gen_fusion)",
            "Expected Shots: Limited by reload, not energy (generator keeps up)",
            "Distance: 100 pixels (point-blank)",
            "Test Duration: 50 ticks"
        ],
        edge_cases=[
            "Generator regenerates faster than weapon consumes",
            "Energy may drop initially but should stabilize",
            "Weapon should fire successfully multiple times"
        ],
        expected_outcome="Beam fires successfully, dealing damage. Energy regeneration prevents depletion.",
        pass_criteria="damage_dealt > 0 (beam successfully fired at least once)",
        max_ticks=50,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["resource", "energy", "consumption", "regeneration", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Create attacker with limited energy storage and generator
        attacker = self._create_ship_with_components(
            ["test_beam_med_acc", "test_storage_energy_small", "test_gen_fusion"],
            "Limited Energy Attacker (With Gen)"
        )

        # Load target
        target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at close range
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0  # Facing right
        target.position = pygame.math.Vector2(100, 0)
        target.angle = 0

        # Store initial state
        self.initial_energy = attacker.resources.get_value('energy')
        self.initial_hp = target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if beam fired and dealt damage."""
        damage_dealt = self.initial_hp - self.target.hp
        final_energy = self.attacker.resources.get_value('energy')

        # Store results
        self.results['initial_energy'] = self.initial_energy
        self.results['final_energy'] = final_energy
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Pass if damage was dealt (beam successfully fired)
        return damage_dealt > 0


class BeamEnergyDepletionScenario(TestScenario):
    """
    RESOURCE-002: Beam Stops Firing When Energy Depleted (No Generator)

    Tests that beam weapons stop firing when energy is fully depleted.
    With 25 energy and 10 per shot, weapon can fire 2 shots maximum
    before running out of energy.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-002",
        category="Resource System",
        subcategory="Energy",
        name="Beam Energy Depletion (No Regeneration)",
        summary="Validates beam weapon stops firing when energy is depleted without regeneration",
        conditions=[
            "Attacker: test_beam_med_acc + test_storage_energy_small (NO generator)",
            "Target: Test_Target_Stationary.json",
            "Initial Energy: 25 units",
            "Energy Cost: 10 per beam shot",
            "Maximum Shots: 2 (25 / 10 = 2.5, rounds down to 2)",
            "Distance: 100 pixels (point-blank)",
            "Test Duration: 100 ticks (enough time to deplete)"
        ],
        edge_cases=[
            "No energy regeneration",
            "Weapon fires until energy < cost threshold (10)",
            "Final energy should be less than 10 (insufficient for another shot)",
            "Energy depletion is a hard stop (weapon cannot fire)"
        ],
        expected_outcome="Energy depletes to below 10 units, weapon stops firing",
        pass_criteria="final_energy < 10 (insufficient energy for another shot)",
        max_ticks=100,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=10,
        tags=["resource", "energy", "depletion", "beam-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Create attacker with limited energy storage, NO generator
        attacker = self._create_ship_with_components(
            ["test_beam_med_acc", "test_storage_energy_small"],
            "Limited Energy Attacker (No Gen)"
        )

        # Load target
        target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at close range
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(100, 0)
        target.angle = 0

        # Store initial state
        self.initial_energy = attacker.resources.get_value('energy')
        self.initial_hp = target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if energy was depleted."""
        damage_dealt = self.initial_hp - self.target.hp
        final_energy = self.attacker.resources.get_value('energy')

        # Store results
        self.results['initial_energy'] = self.initial_energy
        self.results['final_energy'] = final_energy
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Pass if energy depleted below cost threshold
        return final_energy < 10


# ============================================================================
# PROJECTILE AMMO CONSUMPTION TESTS
# ============================================================================

class ProjectileAmmoConsumptionScenario(TestScenario):
    """
    RESOURCE-003: Projectile Weapon Consumes Ammo Per Shot

    Tests that projectile weapons consume ammo with each shot fired.
    Validates the ammo consumption mechanic works correctly.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-003",
        category="Resource System",
        subcategory="Ammo",
        name="Projectile Ammo Consumption",
        summary="Validates projectile weapon consumes ammo per shot fired",
        conditions=[
            "Attacker: test_weapon_proj_fixed + test_storage_ammo_small",
            "Target: Test_Target_Stationary.json",
            "Initial Ammo: 10 units",
            "Ammo Cost: 1 per shot",
            "Weapon Reload: 1.0 seconds",
            "Distance: 100 pixels (point-blank)",
            "Test Duration: 200 ticks (~2 seconds, allowing 2+ shots)"
        ],
        edge_cases=[
            "First shot at tick ~0",
            "Second shot at tick ~100 (1 second reload = 100 ticks)",
            "Ammo should decrease by 1 per shot",
            "Some damage should be dealt if shots connect"
        ],
        expected_outcome="Ammo is consumed with each shot, final_ammo < initial_ammo",
        pass_criteria="final_ammo < initial_ammo (ammo was consumed)",
        max_ticks=200,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["resource", "ammo", "consumption", "projectile-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Create attacker with limited ammo storage
        attacker = self._create_ship_with_components(
            ["test_weapon_proj_fixed", "test_storage_ammo_small"],
            "Limited Ammo Projectile Attacker"
        )

        # Load target
        target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at close range
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(100, 0)
        target.angle = 0

        # Store initial state
        self.initial_ammo = attacker.resources.get_value('ammo')
        self.initial_hp = target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive and self.target.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if ammo was consumed."""
        damage_dealt = self.initial_hp - self.target.hp
        final_ammo = self.attacker.resources.get_value('ammo')

        # Store results
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = self.initial_ammo - final_ammo
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Pass if ammo was consumed
        return final_ammo < self.initial_ammo


class ProjectileAmmoDepletionScenario(TestScenario):
    """
    RESOURCE-004: Projectile Weapon Stops Firing When Ammo Depleted

    Tests that projectile weapons stop firing when ammo is fully depleted.
    With 10 ammo and 1 per shot, weapon can fire 10 shots maximum.
    With 1-second reload, this takes ~10 seconds = 1000 ticks.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-004",
        category="Resource System",
        subcategory="Ammo",
        name="Projectile Ammo Depletion",
        summary="Validates projectile weapon stops firing when ammo is fully depleted",
        conditions=[
            "Attacker: test_weapon_proj_fixed + test_storage_ammo_small",
            "Target: Test_Target_Stationary.json",
            "Initial Ammo: 10 units",
            "Ammo Cost: 1 per shot",
            "Maximum Shots: 10",
            "Weapon Reload: 1.0 seconds (100 ticks)",
            "Time to Deplete: ~10 seconds = 1000 ticks",
            "Distance: 100 pixels (point-blank)",
            "Test Duration: 1200 ticks (allow full depletion)"
        ],
        edge_cases=[
            "No ammo regeneration",
            "Weapon fires until ammo == 0",
            "Final ammo should be exactly 0",
            "Ammo depletion is a hard stop (weapon cannot fire)"
        ],
        expected_outcome="Ammo depletes to 0, weapon stops firing",
        pass_criteria="final_ammo == 0 (ammo fully depleted)",
        max_ticks=1200,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=9,
        tags=["resource", "ammo", "depletion", "projectile-weapons"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Create attacker with limited ammo storage
        attacker = self._create_ship_with_components(
            ["test_weapon_proj_fixed", "test_storage_ammo_small"],
            "Limited Ammo Projectile Attacker"
        )

        # Load target
        target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at close range
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(100, 0)
        target.angle = 0

        # Store initial state
        self.initial_ammo = attacker.resources.get_value('ammo')
        self.initial_hp = target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if ammo was fully depleted."""
        damage_dealt = self.initial_hp - self.target.hp
        final_ammo = self.attacker.resources.get_value('ammo')

        # Store results
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = self.initial_ammo - final_ammo
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Pass if ammo fully depleted
        return final_ammo == 0


# ============================================================================
# SEEKER AMMO CONSUMPTION TESTS
# ============================================================================

class SeekerAmmoConsumptionScenario(TestScenario):
    """
    RESOURCE-005: Seeker Weapon Consumes Ammo Per Launch

    Tests that seeker weapons consume ammo with each missile launched.
    Seeker consumes 5 ammo per shot, so 10 ammo = 2 launches maximum.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-005",
        category="Resource System",
        subcategory="Ammo",
        name="Seeker Ammo Consumption",
        summary="Validates seeker weapon consumes ammo per missile launched (5 ammo per launch)",
        conditions=[
            "Attacker: test_weapon_missile_omni + test_storage_ammo_small",
            "Target: Test_Target_Stationary.json",
            "Initial Ammo: 10 units",
            "Ammo Cost: 5 per launch",
            "Maximum Launches: 2 (10 / 5 = 2)",
            "Weapon Reload: 5.0 seconds (500 ticks)",
            "Distance: 500 pixels (allow missiles to track)",
            "Test Duration: 600 ticks (~6 seconds, allow 1+ launches)"
        ],
        edge_cases=[
            "Seeker consumes more ammo per shot than projectile (5 vs 1)",
            "First launch at tick ~0",
            "Second launch at tick ~500 (5 second reload)",
            "Ammo should decrease by 5 per launch"
        ],
        expected_outcome="Ammo is consumed with each launch, final_ammo < initial_ammo",
        pass_criteria="final_ammo < initial_ammo (ammo was consumed)",
        max_ticks=600,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["resource", "ammo", "consumption", "seeker-weapons", "missiles"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Create attacker with limited ammo storage
        attacker = self._create_ship_with_components(
            ["test_weapon_missile_omni", "test_storage_ammo_small"],
            "Limited Ammo Seeker Attacker"
        )

        # Load target
        target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at mid-range (allow missiles to track)
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(500, 0)
        target.angle = 0

        # Store initial state
        self.initial_ammo = attacker.resources.get_value('ammo')
        self.initial_hp = target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive and self.target.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if ammo was consumed."""
        damage_dealt = self.initial_hp - self.target.hp
        final_ammo = self.attacker.resources.get_value('ammo')

        # Store results
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = self.initial_ammo - final_ammo
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Pass if ammo was consumed
        return final_ammo < self.initial_ammo


class SeekerAmmoDepletionScenario(TestScenario):
    """
    RESOURCE-006: Seeker Weapon Stops Launching When Ammo Depleted

    Tests that seeker weapons stop launching when ammo is fully depleted.
    With 10 ammo and 5 per launch, weapon can launch 2 missiles maximum.
    With 5-second reload, this takes ~10 seconds = 1000 ticks.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-006",
        category="Resource System",
        subcategory="Ammo",
        name="Seeker Ammo Depletion",
        summary="Validates seeker weapon stops launching when ammo is fully depleted",
        conditions=[
            "Attacker: test_weapon_missile_omni + test_storage_ammo_small",
            "Target: Test_Target_Stationary.json",
            "Initial Ammo: 10 units",
            "Ammo Cost: 5 per launch",
            "Maximum Launches: 2 (10 / 5 = 2)",
            "Weapon Reload: 5.0 seconds (500 ticks)",
            "Time to Deplete: ~10 seconds = 1000 ticks",
            "Distance: 500 pixels (allow missiles to track)",
            "Test Duration: 1200 ticks (allow full depletion)"
        ],
        edge_cases=[
            "No ammo regeneration",
            "Weapon launches until ammo < cost threshold (5)",
            "Final ammo should be exactly 0",
            "Ammo depletion is a hard stop (weapon cannot launch)"
        ],
        expected_outcome="Ammo depletes to 0, weapon stops launching",
        pass_criteria="final_ammo == 0 (ammo fully depleted)",
        max_ticks=1200,
        seed=42,
        battle_end_mode="time_based",  # Run for full duration regardless of ship status
        ui_priority=8,
        tags=["resource", "ammo", "depletion", "seeker-weapons", "missiles"]
    )

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Create attacker with limited ammo storage
        attacker = self._create_ship_with_components(
            ["test_weapon_missile_omni", "test_storage_ammo_small"],
            "Limited Ammo Seeker Attacker"
        )

        # Load target
        target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at mid-range
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(500, 0)
        target.angle = 0

        # Store initial state
        self.initial_ammo = attacker.resources.get_value('ammo')
        self.initial_hp = target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        attacker.current_target = target

        # Store references
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if ammo was fully depleted."""
        damage_dealt = self.initial_hp - self.target.hp
        final_ammo = self.attacker.resources.get_value('ammo')

        # Store results
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = self.initial_ammo - final_ammo
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive

        # Pass if ammo fully depleted
        return final_ammo == 0


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    'BeamEnergyConsumptionWithGeneratorScenario',
    'BeamEnergyDepletionScenario',
    'ProjectileAmmoConsumptionScenario',
    'ProjectileAmmoDepletionScenario',
    'SeekerAmmoConsumptionScenario',
    'SeekerAmmoDepletionScenario'
]
