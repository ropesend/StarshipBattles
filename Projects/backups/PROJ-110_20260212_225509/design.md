# PROJ-110: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The codebase has 8164 tests passing across three test tiers:
- `tests/unit/` - Fast unit tests (primary target for PROJ-110)
- `tests/integration/` - Integration tests (some modules only have integration coverage)
- `simulation_tests/` - Battle simulation scenario tests

### Existing Coverage Landscape

**Well-tested areas (>80% coverage):**
- Registry system, DI, validation, constants, exceptions, protocols
- Density map primitives, pathfinding, production engine
- Fleet movement engine, population engine, component health

**Coverage gaps identified (54 findings):**
- 10 CRITICAL findings (zero unit tests on critical-path modules)
- 19 MAJOR findings (incomplete coverage on important modules)
- 25 MINOR findings (missing edge cases on otherwise-tested modules)

### Test Infrastructure Available

**Existing patterns observed:**
- `pytest` with `pytest-xdist` for parallelism
- `unittest.mock` (Mock, MagicMock, patch) used extensively
- Class-based test organization (`class TestXxx:`)
- Parametrized tests via `@pytest.mark.parametrize`
- Fixtures defined locally in test files (no global conftest fixtures for strategy/ai)
- Pure function testing preferred over integration-heavy mock setups

**Key fixtures/factories:**
- `RegistryManager.reset()` / `StrategyManager.reset()` for singleton cleanup
- `Mock()` objects for ships, controllers, grids (AI tests)
- `DensityMap` + `RadialPrimitive` for galaxy generation tests
- `RaceConfig.from_dict()` for race configuration tests

## Sweep Findings Summary

### Layer Distribution
| Layer | CRITICAL | MAJOR | MINOR | Total |
|-------|----------|-------|-------|-------|
| Foundation (core/ai/research/engine) | 3 | 7 | 11 | 21 |
| Simulation | 4 | 5 | 9 | 18 |
| Strategy | 3 | 5 | 7 | 15 |
| **Total** | **10** | **17** | **27** | **54** |

### Architecture Notes

**Foundation Layer:**
- `hex_math.py` (250 LOC) - Pure math, no dependencies. Integration test exists in strategy but no unit tests. Ideal for pure function testing.
- `behaviors.py` (514 LOC) - 13 behavior classes. Each takes a `controller` (with `.ship`, `.navigate_to()`, `.check_avoidance()` methods). All behaviors testable with mocked controller.
- `resources.py` (143 LOC) - Two functions with 4 error catch paths each. Requires mocking `load_json_required` and `RegistryManager`.

**Simulation Layer:**
- `component_constants.py` (69 LOC) - Simple enums + data classes. Very straightforward to test.
- `physics_constants.py` (30 LOC) - Constants only. Tests verify formula correctness with known inputs.
- `battle_config.py` (54 LOC) - Dataclass + enum. Tests verify defaults, modes, serialization.
- `modifier_schema.py` (259 LOC) - Pure validation functions. Test with valid/invalid input dicts.
- `modifier_effects.py` (326 LOC) - Formula evaluation + effect generation. Tests verify formula parsing and ModifierEffect creation.
- `modifiers.py` (185 LOC) - Effect application to stats dicts. Pure function testing.

**Strategy Layer:**
- `physics.py` (57 LOC) - Pure calculation, depends on `Spectrum` and `hex_distance`. Very testable.
- `strategy_session_facade.py` (451 LOC) - Thin delegation layer. All methods delegate to `_session`. Test with Mock session.
- `region_classifier.py` (281 LOC) - Pure geometry. Test with known layout configs and verify classifications.
- `stars.py` (561 LOC) - Star generation with randomness. Test with seeded RNG for determinism.

### Key Patterns to Reuse
- **Singleton reset pattern**: `StrategyManager.reset()` before tests, used in `test_strategy_manager_singleton.py`
- **Mock controller pattern**: AI behavior tests use `Mock()` controller with `.ship`, `.navigate_to()` etc.
- **Seeded RNG pattern**: Galaxy generation tests use `random.Random(seed)` for deterministic testing
- **Parametrized validation**: `@pytest.mark.parametrize` for schema validation with many input variants
- **Pure function testing**: Modifier system functions take dicts and return dicts - no mocking needed

### Dependencies & Risks
1. **Pygame dependency in screenshot_manager.py** - Tests must mock `pygame.display.get_surface()` and `pygame.image.save()`
2. **Singleton state leaks** - StrategyManager, ScreenshotManager are singletons. Must reset between tests.
3. **File I/O in resources.py/registry_loader.py** - Use `unittest.mock.patch` for `load_json_required`/file operations
4. **Random behavior in star generation** - Use seeded `random.Random()` instances for deterministic tests
5. **Circular import risk in behaviors.py** - Imports `AIConfig`, `PhysicsConfig`. Tests should import behaviors directly.

### Opportunities Discovered
- Integration test `test_hex_math_strategy.py` already has 7 test methods covering basic HexCoord functionality. Can migrate these to unit tests and expand with edge cases.
- Placement strategy tests (`test_placement_strategies.py`) are thorough for placement but don't cover `RegionClassifier` at all.
- `test_engine_interfaces.py` exists in strategy tests - check if it already covers the contract testing needed for TCG-STR-006.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
