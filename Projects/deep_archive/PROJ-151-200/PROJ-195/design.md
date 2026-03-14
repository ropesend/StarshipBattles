# PROJ-195: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State of RegistryManager.instance() Usage

**Baseline:** 12,718 tests passing, 1 skipped, 0 failures.

**Total References:** ~126 `RegistryManager.instance()` calls across the codebase.

#### Production Code (game/) — 12 references in 4 files
| File | Lines | Classification | Action |
|------|-------|---------------|--------|
| `game/app.py` | 114, 125 | COMPOSITION_ROOT | Keep |
| `game/core/registry.py` | 100, 231, 243, 255, 277, 281, 285, 289 | SINGLETON_DEFINITION | Keep |
| `game/simulation/entities/ship_loader.py` | 34 | PRODUCTION_LEAK | **Fix** |
| `game/simulation/services/registry_loader.py` | 13 (docstring only) | DOCUMENTATION | Fix docstring |

#### Test Infrastructure — ~20 references in conftest files
| File | Classification | Action |
|------|---------------|--------|
| `conftest.py` (root) | TEST_FIXTURE | Keep — global state reset (autouse) |
| `tests/infrastructure/session_cache.py:49` | TEST_FIXTURE | Keep — session cache loading |
| `tests/unit/core/registry/conftest.py:67` | TEST_FIXTURE | Keep — registry-specific test fixture |
| `tests/unit/core/resources_registry/conftest.py:13` | TEST_FIXTURE | Migrate |
| `tests/integration/resource_system/conftest.py:22` | TEST_FIXTURE | Migrate |
| `tests/unit/strategy/conftest.py:17,45` | TEST_FIXTURE | Migrate |

#### Legitimate Singleton Tests — ~22 references in 3 files
| File | Count | Action |
|------|-------|--------|
| `tests/unit/core/registry/test_singleton_and_thread.py` | 12 | Keep |
| `tests/unit/core/registry/test_registry_features.py` | 6 | Keep |
| `tests/regression/test_deprecated_code_removed.py` | 4 | Keep |

#### Test Code Needing Migration — ~72 references in ~20 files
These tests use `RegistryManager.instance()` for convenience where `TestRegistryProvider`, `fresh_registries`, or `minimal_registries` should be used instead.

## Swarm Findings Summary

### Architecture

The DI architecture is well-established with clear patterns:

1. **IRegistryProvider** (`game/core/protocols.py:46-78`) — Protocol with 4 methods
2. **DefaultRegistryProvider** (`game/core/registry.py:260-289`) — Wraps singleton for production
3. **TestRegistryProvider** (`game/core/registry.py:292-343`) — Isolated data for testing
4. **GameRegistries** — Dataclass container for passing registry data via DI
5. **Composition Root** (`game/app.py`) — Only legitimate singleton access point

### Key Patterns to Reuse

- **Strict DI** (`PROJ-50`): `def __init__(self, *, registries: GameRegistries)` — Required parameter, no fallback
- **Lazy DI** (`PROJ-174`): `def __init__(self, registry_provider: Optional[IRegistryProvider] = None)` — Optional with fallback
- **Test Fixtures**: `fresh_registries` (deep-copied production data), `minimal_registries` (empty), `mock_registries` (alias)
- **`@pytest.mark.use_custom_data`**: Skips autouse `reset_game_state` hydration for tests with custom data

### Migration Patterns by Test Type

**Pattern A: Test passes `RegistryManager.instance()` to API that accepts `registries=`**
```python
# BEFORE
loader = BuilderDataLoader(dir, registries=RegistryManager.instance())

# AFTER (use fresh_registries fixture)
def test_load(self, fresh_registries):
    loader = BuilderDataLoader(dir, registries=fresh_registries)
```

**Pattern B: Test accesses singleton for data setup**
```python
# BEFORE
RegistryManager.instance().vehicle_classes["TestShip"] = {...}

# AFTER (use fresh_registries and pass through DI)
def test_combat(self, fresh_registries):
    fresh_registries.vehicle_classes["TestShip"] = {...}
```

**Pattern C: Test uses `patch.object(RegistryManager.instance(), ...)` for mocking**
```python
# BEFORE
with patch.object(RegistryManager.instance(), 'clear') as mock_clear:

# AFTER (mock on the registries object instead)
with patch.object(fresh_registries, 'clear', create=True) as mock_clear:
# OR: restructure test to not need the mock at all
```

### Dependencies & Risks

1. **Root conftest `reset_game_state` uses singleton legitimately** — Global test isolation mechanism. Keep.
2. **`test_registry_provider.py` populates singleton to test DefaultRegistryProvider** — Validates delegation. Keep.
3. **`test_service_injection.py` checks singleton isolation** — Negative assertions. Keep.
4. **`test_isolation.py` tests the isolation fixture itself** — Must use singleton. Keep.
5. **Data loader tests `patch.object(RegistryManager.instance(), 'clear')`** — Need mock target change.

### Opportunities Discovered

- `registry_loader.py` line 13 is only a docstring example, not executable code
- `ship_loader.py:34` already has a `registry_provider` parameter — easy fix
- Several test files can remove `RegistryManager` import entirely after migration

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
