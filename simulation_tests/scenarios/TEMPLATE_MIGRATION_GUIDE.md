# Scenario Template Migration Guide

## Overview

The scenario template system eliminates **~2000 lines of duplicated code** across 35+ test scenarios by providing reusable base classes for common test patterns.

**Templates Created:**
- `StaticTargetScenario` - Attacker vs stationary target (beam/seeker weapon tests)
- `DuelScenario` - Two ships engaging each other (combat tests)
- `PropulsionScenario` - Single ship movement/physics tests (engine/thruster tests)

**Location:** `simulation_tests/scenarios/templates.py`

## Benefits

### Before Templates (Typical Scenario = ~150-180 lines)
```python
class BeamPointBlankTest(TestScenario):
    metadata = TestMetadata(...)  # 100 lines

    def setup(self, battle_engine):
        # 30 lines of duplicate setup code
        self.attacker = self._load_ship("Attacker.json")
        self.target = self._load_ship("Target.json")
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.target.position = pygame.math.Vector2(50, 0)
        # ... etc

    def update(self, battle_engine):
        # 5 lines of duplicate fire logic
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        # 20 lines of duplicate result storage
        damage_dealt = self.initial_hp - self.target.hp
        self.results['initial_hp'] = self.initial_hp
        # ... etc
        return damage_dealt > 0
```

### After Templates (Same Scenario = ~120 lines)
```python
class BeamPointBlankTest(StaticTargetScenario):
    # Template configuration (3 lines replaces 55 lines of setup/update/verify)
    attacker_ship = "Attacker.json"
    target_ship = "Target.json"
    distance = 50

    metadata = TestMetadata(...)  # 100 lines (unchanged)

    def verify(self, battle_engine) -> bool:
        # Template already stores standard results
        # Only implement test-specific logic
        return self.damage_dealt > 0
```

**Result:**
- Eliminates 30-60 lines of boilerplate per scenario
- 35+ scenarios × 40 lines average = **~1,400 lines removed**
- Plus eliminates update() and most verify() code = **~2,000 total lines**

## Migration Examples

### Example 1: Static Target Scenario (Most Common)

**Before (56 lines of setup/update/verify):**
```python
class BeamLowAccuracyPointBlankScenario(TestScenario):
    metadata = TestMetadata(...)

    def setup(self, battle_engine):
        """Setup test scenario."""
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Beam360_Low.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at point-blank range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0  # Facing right
        self.target.position = pygame.math.Vector2(50, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition (TIME_BASED: runs for full duration)
        end_condition = self._create_end_condition()

        # Start battle with time-based end condition
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

        # Custom calculation
        self.expected_hit_chance = calculate_expected_hit_chance(...)

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check if damage was dealt."""
        damage_dealt = self.initial_hp - self.target.hp

        # Store results
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['expected_hit_chance'] = self.expected_hit_chance
        self.results['target_alive'] = self.target.is_alive

        # Pass if any damage was dealt
        return damage_dealt > 0
```

**After (15 lines - eliminates 41 lines):**
```python
class BeamLowAccuracyPointBlankScenario(StaticTargetScenario):
    # Template configuration (replaces entire setup/update)
    attacker_ship = "Test_Attacker_Beam360_Low.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 50

    metadata = TestMetadata(...)

    def custom_setup(self, battle_engine):
        """Called after standard setup - only custom logic."""
        self.expected_hit_chance = calculate_expected_hit_chance(...)

    def verify(self, battle_engine) -> bool:
        """Template already stores all standard results."""
        # self.damage_dealt, self.results['damage_dealt'], etc. already set
        self.results['expected_hit_chance'] = self.expected_hit_chance
        return self.damage_dealt > 0
```

**What the Template Does Automatically:**
- Loads both ships from JSON
- Positions attacker at origin, target at specified distance
- Stores `initial_hp` for damage calculations
- Creates time-based end condition
- Starts battle with proper seed
- Sets `attacker.current_target = target`
- Forces attacker to fire each tick (auto-update)
- Calculates `damage_dealt = initial_hp - target.hp`
- Stores standard results: `initial_hp`, `final_hp`, `damage_dealt`, `ticks_run`, `target_alive`, `hit_rate`

**Custom Hooks Available:**
- `custom_setup(battle_engine)` - Called after standard setup
- `custom_update(battle_engine)` - Called after standard update

### Example 2: Seeker Weapon Scenario

**Before (40 lines):**
```python
class SeekerCloseRangeImpactScenario(TestScenario):
    metadata = TestMetadata(...)

    def setup(self, battle_engine):
        # Load ships
        self.attacker = self._load_ship("Test_Attacker_Seeker360.json")
        self.target = self._load_ship("Test_Target_Stationary.json")

        # Position ships at close range
        self.attacker.position = pygame.math.Vector2(0, 0)
        self.attacker.angle = 0
        self.target.position = pygame.math.Vector2(500, 0)
        self.target.angle = 0

        # Store initial state
        self.initial_hp = self.target.hp

        # Create end condition
        end_condition = self._create_end_condition()

        # Start battle
        battle_engine.start([self.attacker], [self.target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Set target
        self.attacker.current_target = self.target

    def update(self, battle_engine):
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        damage_dealt = self.initial_hp - self.target.hp
        self.results['initial_hp'] = self.initial_hp
        self.results['final_hp'] = self.target.hp
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = battle_engine.tick_counter
        self.results['target_alive'] = self.target.is_alive
        return damage_dealt >= 100
```

**After (10 lines - eliminates 30 lines):**
```python
class SeekerCloseRangeImpactScenario(StaticTargetScenario):
    # Template configuration
    attacker_ship = "Test_Attacker_Seeker360.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 500

    metadata = TestMetadata(...)

    def verify(self, battle_engine) -> bool:
        # Template already calculated damage_dealt and stored results
        return self.damage_dealt >= 100
```

### Example 3: Propulsion Scenario

**Before (50 lines):**
```python
class PropEngineAccelerationScenario(TestScenario):
    metadata = TestMetadata(...)

    def setup(self, battle_engine):
        # Load minimal ship with engine
        self.ship = self._load_ship('Test_Engine_1x_LowMass.json')

        # Position at origin with zero velocity
        self.ship.position = pygame.math.Vector2(0, 0)
        self.ship.velocity = pygame.math.Vector2(0, 0)
        self.ship.angle = 0

        # Create end condition
        end_condition = self._create_end_condition()

        # Start battle
        battle_engine.start([self.ship], [],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        # Store initial state
        self.initial_velocity = self.ship.velocity.length()
        self.initial_position = self.ship.position.copy()

    def update(self, battle_engine):
        # Apply thrust to make the ship accelerate
        self.ship.thrust_forward()

    def verify(self, battle_engine) -> bool:
        final_velocity = self.ship.velocity.length()
        self.results['initial_velocity'] = self.initial_velocity
        self.results['final_velocity'] = final_velocity
        self.results['distance_traveled'] = (self.ship.position - self.initial_position).length()
        self.results['ticks_run'] = battle_engine.tick_counter
        return final_velocity > self.initial_velocity and final_velocity > 0
```

**After (12 lines - eliminates 38 lines):**
```python
class PropEngineAccelerationScenario(PropulsionScenario):
    # Template configuration
    ship_file = 'Test_Engine_1x_LowMass.json'
    thrust_forward = True  # Auto-thrust each tick

    metadata = TestMetadata(...)

    def verify(self, battle_engine) -> bool:
        # Template already stored: initial_velocity, final_velocity,
        # distance_traveled, all results, etc.
        return self.final_velocity.length() > self.start_velocity.length() and \
               self.final_velocity.length() > 0
```

## Template Configuration Reference

### StaticTargetScenario

**Required Attributes:**
```python
attacker_ship = "filename.json"  # Attacker ship JSON file
target_ship = "filename.json"    # Target ship JSON file
distance = 500                    # Distance in pixels
```

**Optional Attributes:**
```python
attacker_angle = 0.0     # Attacker rotation (default: 0 = facing right)
target_angle = 0.0       # Target rotation (default: 0)
verify_damage_dealt = False  # If True, auto-verifies damage > 0
force_fire = True        # If True, auto-fires weapon each tick
```

**Custom Hooks:**
```python
def custom_setup(self, battle_engine):
    """Called after standard setup completes."""
    pass

def custom_update(self, battle_engine):
    """Called after standard update (firing)."""
    pass
```

**Automatic Results Stored:**
- `initial_hp` - Target HP before test
- `final_hp` - Target HP after test
- `damage_dealt` - Damage dealt (initial_hp - final_hp)
- `ticks_run` - Number of simulation ticks
- `target_alive` - Target survival status
- `hit_rate` - Damage per tick (if applicable)

**Attributes Available in verify():**
- `self.attacker` - Attacker ship object
- `self.target` - Target ship object
- `self.initial_hp` - Target initial HP
- `self.damage_dealt` - Damage dealt

### DuelScenario

**Required Attributes:**
```python
ship1_file = "filename.json"  # First ship JSON file
ship2_file = "filename.json"  # Second ship JSON file
distance = 500                 # Distance between ships
```

**Optional Attributes:**
```python
ship1_angle = 0.0       # Ship 1 rotation (default: facing right)
ship2_angle = 180.0     # Ship 2 rotation (default: facing left)
ship1_position = None   # Override position (default: calculated)
ship2_position = None   # Override position (default: calculated)
auto_target = True      # Auto-set mutual targeting
force_fire = True       # Auto-fire weapons each tick
```

**Automatic Results Stored:**
- `ship1_initial_hp`, `ship2_initial_hp` - HP before test
- `ship1_final_hp`, `ship2_final_hp` - HP after test
- `ship1_damage_dealt`, `ship2_damage_dealt` - Damage dealt
- `ship1_damage_taken`, `ship2_damage_taken` - Damage taken
- `ticks_run` - Simulation ticks
- `ship1_alive`, `ship2_alive` - Survival status
- `winner` - 'ship1', 'ship2', 'draw', or None

**Attributes Available in verify():**
- `self.ship1`, `self.ship2` - Ship objects
- `self.ship1_damage_dealt`, `self.ship2_damage_dealt`
- `self.winner` - Winner determination

### PropulsionScenario

**Required Attributes:**
```python
ship_file = "filename.json"  # Ship JSON file to test
```

**Optional Attributes:**
```python
initial_position = Vector2(0, 0)  # Starting position
initial_velocity = Vector2(0, 0)  # Starting velocity
initial_angle = 0.0               # Starting rotation
thrust_forward = False            # Auto-thrust forward
thrust_backward = False           # Auto-thrust backward
turn_left = False                 # Auto-turn left
turn_right = False                # Auto-turn right
```

**Automatic Results Stored:**
- `initial_position`, `final_position` - Position tuples
- `initial_velocity`, `final_velocity` - Velocity tuples
- `initial_velocity_magnitude`, `final_velocity_magnitude`
- `initial_angle`, `final_angle` - Rotations
- `distance_traveled` - Total distance moved
- `velocity_change` - Velocity magnitude change
- `angle_change` - Rotation change
- `ticks_run` - Simulation ticks
- `expected_max_speed`, `expected_acceleration_rate` - Physics

**Attributes Available in verify():**
- `self.ship` - Ship object
- `self.start_position`, `self.final_position` - Vector2
- `self.start_velocity`, `self.final_velocity` - Vector2
- `self.distance_traveled`, `self.velocity_change`, `self.angle_change`

## Migration Checklist

For each scenario to migrate:

1. **Change base class:**
   ```python
   # Before
   class MyTest(TestScenario):

   # After
   class MyTest(StaticTargetScenario):  # or DuelScenario, PropulsionScenario
   ```

2. **Add template configuration:**
   ```python
   # Add at top of class (before metadata)
   attacker_ship = "Attacker.json"
   target_ship = "Target.json"
   distance = 500
   ```

3. **Delete standard setup() if no custom logic:**
   - If setup() only loads ships, positions them, creates end condition → DELETE IT
   - If setup() has custom calculations → Move to `custom_setup()`

4. **Delete standard update() if no custom logic:**
   - If update() only fires weapon → DELETE IT (template does this)
   - If update() has custom behavior → Move to `custom_update()`

5. **Simplify verify():**
   - Delete result storage lines (template does this)
   - Keep only test-specific verification logic
   - Use `self.damage_dealt` instead of calculating

6. **Test the migrated scenario:**
   ```bash
   pytest simulation_tests/tests/test_beam_weapons.py::test_specific_scenario -v
   ```

## Migration Order (Recommended)

1. **Start with simplest scenarios** (pure StaticTargetScenario, no custom logic)
2. **Migrate beam weapon scenarios** (11 scenarios, all similar)
3. **Migrate seeker weapon scenarios** (11 scenarios, all similar)
4. **Migrate propulsion scenarios** (4 scenarios)
5. **Migrate custom scenarios** (any with unique patterns)

## Testing After Migration

### Quick Import Test
```bash
python -c "from simulation_tests.scenarios.beam_scenarios import BeamLowAccuracyPointBlankScenario; print('Success')"
```

### Run Single Test
```bash
pytest simulation_tests/tests/test_beam_weapons.py::test_beam_low_accuracy_point_blank -v
```

### Run All Tests in Category
```bash
pytest simulation_tests/tests/test_beam_weapons.py -v
```

### Compare Results
Before migration:
```bash
pytest simulation_tests/tests/test_beam_weapons.py -v > before.txt
```

After migration:
```bash
pytest simulation_tests/tests/test_beam_weapons.py -v > after.txt
diff before.txt after.txt  # Should show no test behavior changes
```

## Common Pitfalls

### 1. Forgetting to import template
```python
# WRONG
from simulation_tests.scenarios import TestScenario

# RIGHT
from simulation_tests.scenarios.templates import StaticTargetScenario
```

### 2. Not setting required attributes
```python
# WRONG - will raise ValueError
class MyTest(StaticTargetScenario):
    metadata = TestMetadata(...)

# RIGHT
class MyTest(StaticTargetScenario):
    attacker_ship = "Attacker.json"  # Required
    target_ship = "Target.json"      # Required
    distance = 500                    # Required
    metadata = TestMetadata(...)
```

### 3. Overriding setup() without calling super()
```python
# WRONG - breaks template setup
def setup(self, battle_engine):
    self.my_custom_thing = 42

# RIGHT - use custom_setup hook
def custom_setup(self, battle_engine):
    self.my_custom_thing = 42
```

### 4. Recalculating values template already provides
```python
# WRONG - redundant calculation
def verify(self, battle_engine) -> bool:
    damage_dealt = self.initial_hp - self.target.hp  # Template already does this
    return damage_dealt > 0

# RIGHT - use template attribute
def verify(self, battle_engine) -> bool:
    return self.damage_dealt > 0  # Already calculated
```

## Estimated Effort

- **Per scenario migration:** 5-10 minutes (simple) to 15-20 minutes (complex)
- **Total time for all scenarios:** 6-10 hours
- **Lines of code removed:** ~2,000 lines
- **Maintenance benefit:** Significantly easier to update test patterns

## Next Steps

1. **Verify templates work:** Import test to confirm no syntax errors
2. **Migrate one scenario:** Start with simplest beam weapon test
3. **Test migrated scenario:** Ensure behavior unchanged
4. **Migrate similar scenarios:** Batch migrate related tests
5. **Run full test suite:** Confirm no regressions
6. **Update documentation:** Mark completion in code review

## Questions?

- Template code location: [templates.py](templates.py)
- Base scenario documentation: [base.py](base.py)
- Example scenarios: [beam_scenarios.py](beam_scenarios.py), [seeker_scenarios.py](seeker_scenarios.py)
