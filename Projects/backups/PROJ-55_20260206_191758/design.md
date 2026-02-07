# PROJ-55: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Colonization System

**Flow:** UI → Command → Validation → Execution

**Key Components:**
- **Validation:** [colonize_validator.py](c:\Dev\StarshipBattles\game\strategy\validation\colonize_validator.py) - `ColonizeValidator.validate()`
- **Execution:** [fleet_order_processor.py](c:\Dev\StarshipBattles\game\strategy\engine\fleet_order_processor.py) - `process_colonize()`
- **UI:** [strategy_colonization.py](c:\Dev\StarshipBattles\game\ui\screens\strategy_colonization.py) - `ColonizationSystem`
- **Commands:** [commands.py](c:\Dev\StarshipBattles\game\strategy\engine\commands.py) - `IssueColonizeCommand`, `QueueColonizeMissionCommand`

**Current Behavior:**
- Any fleet can colonize any planet (no restrictions)
- Only checks: planet at fleet location, planet unowned
- Entire fleet consumed on colonization
- Supports "Any Planet" mode (picks first valid candidate)
- No planet type differentiation

**Current Limitations:**
1. No component requirements (any ship can colonize)
2. No planet type restrictions (gas giants colonizable same as terrestrial)
3. Entire fleet consumed (not individual ship)
4. No support for colonization chains with validation
5. No habitability considerations

### Planet System

**11 Planet Types** (defined in `PlanetType` enum):
1. CONTINENTAL - Earth-like
2. ARID - Desert
3. PELAGIC - Ocean
4. MAGMA - Volcanic
5. CRYOPLANET - Ice surface
6. BARREN - Airless rock
7. JOVIAN - Gas giant
8. ICE_GIANT - Ice giant
9. CHTHONIAN - Stripped core
10. ICE_DWARF - Pluto-like
11. PLANETOID - Large asteroid

**Planet Generation:**
- Physics-first approach (mass, radius, temperature, pressure)
- Classification decision tree in [planet_gen.py](c:\Dev\StarshipBattles\game\strategy\data\planet_gen.py)
- Thresholds loaded from [astrophysics.json](c:\Dev\StarshipBattles\data\astrophysics.json) (data-driven)
- Visual mappings in [planet_classifications.json](c:\Dev\StarshipBattles\assets\Images\Stellar Objects\Planets\Planets_V3\planet_classifications.json)

**Current Usage:**
- Visual representation only
- NOT used for colonization restrictions
- NOT used for resource differentiation
- NOT used for strategic value

### Component & Ability System

**Architecture Pattern:**
- Data-driven: Components defined in [components.json](c:\Dev\StarshipBattles\data\components.json)
- Abilities implemented as Python classes
- Registry pattern: [abilities/__init__.py](c:\Dev\StarshipBattles\game\simulation\components\abilities\__init__.py) - `ABILITY_REGISTRY`
- Supports parameterized abilities with type data

**Ability Data Patterns:**
1. **Boolean marker:** `"AbilityName": true`
2. **Simple numeric:** `"AbilityName": 150`
3. **Parameterized object:** `"AbilityName": {"param1": "value", "param2": 10}`
4. **List of instances:** `"AbilityName": [{"resource": "fuel"}, {"resource": "energy"}]`

**Vehicle Type Restrictions:**
- Components specify `"allowed_vehicle_types": ["Ship", "Planetary Complex", ...]`
- Validated by `LayerConstraintRule` in [ship_validator.py](c:\Dev\StarshipBattles\game\simulation\validation\ship_validator.py)

**Layer System:**
- `AbilityLayer.COMBAT` - Real-time tactical combat
- `AbilityLayer.STRATEGIC` - Turn-based strategy map
- `AbilityLayer.BOTH` - Active in both

**Existing Example:** `ResourceHarvesterAbility`
- Takes `resource_type` parameter
- Demonstrates pattern for type-specific components
- Pattern can be reused for planet-type-specific colony pods

### Test Coverage

**Current Tests:**
- **Unit:** [test_colonize_validator.py](c:\Dev\StarshipBattles\tests\unit\strategy\validation\test_colonize_validator.py) - 14 test cases, 266 lines
- **Integration:** [test_colonize_logic.py](c:\Dev\StarshipBattles\tests\integration\strategy\test_colonize_logic.py) - 139 lines
- **Integration:** [test_commands_colonization.py](c:\Dev\StarshipBattles\tests\integration\gameplay_loop\test_commands_colonization.py) - 243 lines
- **UI Tests:** [test_colonization_facade.py](c:\Dev\StarshipBattles\tests\integration\ui\test_colonization_facade.py)

**Coverage Scope:**
- Valid/invalid colonization scenarios
- "Any Planet" mode
- Wrong location failures
- Already-owned planet failures
- Fleet consumption
- Concurrent colonization
- Fleet destroyed between order and execution

**Test Pattern:** TDD with pytest, uses fixtures for galaxy/fleet/empire setup

## Swarm Findings Summary

### Architecture

**Clean Layer Separation:**
- Simulation layer (components/abilities) has no dependencies on Strategy layer
- Strategy layer (validation/execution) depends on Simulation
- UI layer depends on both
- This separation allows us to add colony abilities in Simulation without circular dependencies

**Registry Pattern Everywhere:**
- Components registered via JSON
- Abilities registered via `ABILITY_REGISTRY`
- Planets registered in galaxy with ID-based lookup
- Pattern supports data-driven extensibility

**Two-Phase Validation:**
- **Command time:** `ColonizeValidator.validate()` before adding order to queue
- **Execution time:** Re-validation in `FleetOrderProcessor.process_colonize()`
- This supports our chain validation (validate available pods before queuing)

### Key Patterns to Reuse

- **Parameterized Ability:** [harvester.py:15-25](c:\Dev\StarshipBattles\game\simulation\components\abilities\harvester.py) - `ResourceHarvesterAbility` with `resource_type` parameter - exact pattern for `ColonizePlanet` with `planet_type`
- **Vehicle Type Restriction:** [components.json](c:\Dev\StarshipBattles\data\components.json) - `"allowed_vehicle_types": ["Ship"]` - use for colony pods
- **Layer Specification:** [base.py:45](c:\Dev\StarshipBattles\game\simulation\components\abilities\base.py) - `layer = AbilityLayer.STRATEGIC` - colony abilities strategic-only
- **Fleet Ship Iteration:** [fleet_order_processor.py](c:\Dev\StarshipBattles\game\strategy\engine\fleet_order_processor.py) - iterate `fleet.ships` to find specific ship
- **Validation Result Pattern:** [colonize_validator.py:25-35](c:\Dev\StarshipBattles\game\strategy\validation\colonize_validator.py) - `ValidationResult` with error codes - extend with `NO_COLONY_POD`, `COLONY_POD_EXHAUSTED`

### Dependencies & Risks

1. **Fleet.ships iteration** - Need to verify Fleet class has `ships` attribute and supports iteration/removal
   - Mitigation: Check Fleet data model, add `remove_ship()` method if needed

2. **Component.get_ability()** - Assumption that this method exists for ability lookup
   - Mitigation: Verified in component.py, method exists and returns single ability instance

3. **Test updates** - Existing tests assume entire fleet consumed, will break when we change to single ship
   - Mitigation: Systematic test update, mark as expected changes

4. **Save compatibility** - Old saves won't have colony pods, players won't be able to colonize
   - Mitigation: Acceptable breaking change (clean mechanic redesign)

5. **"Any Planet" mode complexity** - When fleet has multiple pod types and multiple planet types at location
   - Mitigation: Document priority logic (e.g., pick first planet that matches any available pod)

### Opportunities Discovered

- **Habitability System:** Planet type data (temperature, pressure, water) exists but unused - could add habitability scoring later
- **Resource Specialization:** Planet resources currently uniform - could make planet types yield different resource types
- **Facility Restrictions:** Planetary facilities exist - could restrict certain facilities to certain planet types
- **Colony Tiers:** Could have basic vs advanced colony pods (basic CONTINENTAL pod vs Advanced CONTINENTAL Pod with better bonuses)
- **Multi-Component Requirements:** Ability system supports multiple abilities - could require both Colony Pod + Life Support for extreme planets

## Design Decisions

**Core Decisions (from user clarifications):**
1. **All 11 types colonizable from start** - Research gating comes later, keep simple now
2. **Colony pods as ship components** - Designed in workshop, consumed on colonization
3. **11 separate components** - One component per planet type (not single generic with parameter)
4. **Track pods, allow chaining** - System validates available pods before allowing queue

See [decisions.md](decisions.md) for the full log with rationale.
