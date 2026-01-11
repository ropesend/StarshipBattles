# Simulation Tests

Integration tests for the combat simulator. These tests run actual battle simulations
to verify component behaviors (engines, weapons, targeting, etc.).

## Running Tests

From project root:

```bash
# Run all simulation tests
python -m pytest simulation_tests/ -v

# Run specific test file
python -m pytest simulation_tests/tests/test_engine_physics.py -v

# Run only tests marked as simulation
python -m pytest simulation_tests/ -v -m simulation
```

## Test Data

All test data is self-contained in `simulation_tests/data/`. These files are
copies of simplified component/ship definitions for testing purposes only.

**Data files:**
- `components.json` - Test components (engines, weapons, etc.)
- `vehicleclasses.json` - Test ship classes
- `modifiers.json` - Test modifiers
- `movement_policies.json` - AI movement behaviors
- `combat_strategies.json` - AI combat strategies
- `targeting_policies.json` - AI targeting policies
- `ships/` - Pre-built ship JSON files

## Specification

See `specs/component_test_specifications.md` for detailed test requirements.

## Test Categories

| Test File | Coverage |
|-----------|----------|
| `test_engine_physics.py` | ENG-001 to ENG-005: Speed, acceleration, thrust/mass |
| `test_projectile_weapons.py` | PROJ360-*: Projectile accuracy, damage, range |
| `test_beam_weapons.py` | BEAM360-*: Beam accuracy, sigmoid formula |
| `test_seeker_weapons.py` | SEEK360-*: Missile tracking, lifetime, PD |
| `test_firing_arcs.py` | 90° arc constraints for all weapon types |
