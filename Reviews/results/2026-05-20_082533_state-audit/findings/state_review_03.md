# State Management Audit — Shard 03

**Date:** 2026-05-20  
**Shard:** 03 (195 files)  
**Deterministic scan run:** `2026-05-20_082533_state-audit`

---

## Summary

| Category | Count | Status |
|---|---|---|
| CRITICAL / HIGH risk | 0 | — |
| MEDIUM risk | 1 | Class-level mutable shared RNG-bearing singleton |
| ADVISORY | 1 | Module-level mutable concurrency accounting |
| VERIFIED (pattern-compliant) | 6 | Valid `_default_*` accessor pairs and lazy caches |
| NO ISSUES | — | 0 random seed sites, 0 class mutable defaults, healthy ctx ratio (87.3%) |

---

## MEDIUM — Class-Level Mutable Shared State (`ShipCombatEngine`)

### `game/simulation/entities/ship_combat_engine.py:40–43`

```python
class ShipCombatEngine:
    _targeting_system: Optional[TargetingSystem] = None
    _damage_calculator: Optional[DamageCalculator] = None
    _weapon_firing_system: Optional[WeaponFiringSystem] = None
```

**Issue:** Three class-level attributes act as shared singletons across all instances. The `__init__` method (lines 56–63) lazily populates them on first construction:

```python
if ShipCombatEngine._damage_calculator is None:
    ShipCombatEngine._damage_calculator = DamageCalculator()
```

All three are then accessed via `self._damage_calculator` (line 162), which resolves through Python's MRO to the class attribute — there is no per-instance assignment.

**`DamageCalculator` holds RNG state.** Per Pattern #18 (Per-Battle RNG), every battle should receive its own seeded `random.Random` instance. The current workaround is in `game/simulation/systems/battle_setup.py:48–49`:

```python
ShipCombatEngine._damage_calculator = DamageCalculator(rng=engine.rng)
```

This overwrites the class-level singleton from *outside the class* before each battle, creating an implicit contract between `battle_setup` and `ShipCombatEngine`.

**Risk:**

- **Test isolation break:** If two test battles ran concurrently, they would fight over the same class-level `_damage_calculator` (and its RNG state).
- **Hidden dependency:** The `battle_setup` module must know about `ShipCombatEngine`'s internal class-level attribute — a layering concern (simulation/systems reaching into simulation/entities internals).
- **Stale state:** If `battle_setup.initialize_start_state` is not called (e.g., in a test or replay path that bypasses it), the damage calculator carries RNG state from the last battle.
- **Incomplete reset:** `_targeting_system` and `_weapon_firing_system` are not reset between battles. `_weapon_firing_system` references `_targeting_system` at construction time, forming an implicit singleton chain.

**Recommendation:** Convert class-level shared singletons to per-instance attributes initialized in `__init__`, with `DamageCalculator` receiving its RNG via constructor injection. Alternatively, thread the `DamageCalculator` through `BattleEngine` injection rather than class-level mutation. This would align with Pattern #18 and eliminate the `battle_setup.py → ShipCombatEngine._damage_calculator` cross-module write.

**Files involved:**
- `game/simulation/entities/ship_combat_engine.py:40–63`
- `game/simulation/systems/battle_setup.py:48–49`
- `game/simulation/systems/battle_engine.py:609,640` (reads `ShipCombatEngine._damage_calculator`)

---

## ADVISORY — Module-Level Concurrency Accounting (`ImageBackgroundCall`)

### `game/ui/services/image/background.py:46–48`

```python
_in_flight_calls: int = 0
_in_flight_lock: threading.Lock = threading.Lock()
_active_workers: Set[threading.Thread] = set()
```

**Issue:** Three module-level mutable objects used for cross-`ImageBackgroundCall` concurrency accounting:
- `_in_flight_calls` — an integer counter (reassigned with `global`)
- `_active_workers` — a `Set[threading.Thread]` (mutated in-place via `.add()`/`.discard()`)
- `_in_flight_lock` — a threading lock (not reassigned, purely a synchronization primitive)

**Assessment:** This is intentional and mirrors `LLMBackgroundCall`'s identical module-level accounting pattern. Both `_in_flight_calls` modifications (lines 126, 250) and `_active_workers` mutations (lines 136, 252) are guarded by `_in_flight_lock`. The `global` keyword is required because `_in_flight_calls` is reassigned (integer increment/decrement).

**Low risk** — thread-safe, well-documented, functionally correct. The pattern is consistent with Pattern #28 (Background Service Call). The `_active_workers` set is the only in-place-mutated module-level collection in this shard; `shutdown_all_image_calls()` (line 267) reads it for worker cleanup.

**Recommendation:** No action required. The only potential improvement would be migrating these counters to a class-level attribute on `ImageBackgroundCall` itself, but the current module-level design is functionally equivalent (one call = one thread, and shutdown walks all active workers).

---

## VERIFIED PASS — Pattern #12 Singleton-Accessor Pairs

### `game/core/profiling.py:17,25–28`

```python
_default_profiler: Optional['Profiler'] = None

def get_default_profiler() -> Optional['Profiler']: ...
def set_default_profiler(profiler: Optional['Profiler']) -> None:
    global _default_profiler
    _default_profiler = profiler
```

**Valid.** PROJ-258 pattern — set once by `ApplicationContext.create_production()` (line 176 of `game/context.py`). Tests swap via `set_default_profiler()`. The `global` keyword is required for reassignment. Module-level `profile_action` decorator and `profile_block` context manager read `_default_profiler` directly (no getter call), which is acceptable for performance-sensitive instrumentation code.

### `game/ui/assets/ship_theme_manager.py:54,442–452`

```python
_default_ship_theme_manager: Optional['ShipThemeManager'] = None

def get_default_ship_theme_manager() -> ShipThemeManager:
    global _default_ship_theme_manager
    if _default_ship_theme_manager is None:
        _default_ship_theme_manager = ShipThemeManager()
    return _default_ship_theme_manager

def set_default_ship_theme_manager(manager: ShipThemeManager) -> None:
    global _default_ship_theme_manager
    _default_ship_theme_manager = manager
```

**Valid.** Lazy-creation getter + explicit setter. `ApplicationContext.create_production()` calls `set_default_ship_theme_manager()` (line 181 of `game/context.py`). Includes a `clear()` method (line 92) for test isolation.

### `game/context.py:33,57–58`

```python
_default_planet_habitability_service: Optional['IHabitabilityCalculator'] = None

def _install_default_habitability_service() -> None:
    global _default_planet_habitability_service
    ...
```

**Valid.** PROJ-372 pattern. Set once at module import time by `_install_default_habitability_service()` (line 67). Has a public `get_default_planet_habitability_service()`/`set_default_planet_habitability_service()` pair.

---

## VERIFIED PASS — Lazy-Load Caches (global keyword, properly guarded)

### `game/strategy/data/container.py:77,81,94`

```python
_resource_catalog: ResourceCatalog | None = None

def _get_resource_catalog() -> ResourceCatalog:
    global _resource_catalog
    if _resource_catalog is None:
        _resource_catalog = ResourceCatalog.from_json()
    return _resource_catalog

def set_resource_catalog(catalog: ResourceCatalog | None) -> None:
    global _resource_catalog
    _resource_catalog = catalog
```

**Valid.** Lazy-load pattern with explicit test override. The `global` keyword is required for the reassignment. Set to `None` to restore default behavior. Pattern #12 variant — documented, tested, intentional.

### `game/strategy/data/galaxy_system_generator.py:237–245,294–299,315–324`

```python
_PLANET_TYPES_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_STAR_TYPES_CACHE: Optional[Dict[str, Dict[str, Any]]] = None
_SYSTEM_ARCHETYPES_CACHE: Optional[Dict[str, Any]] = None
```

**Valid.** Three lazy-loaded JSON caches, each populated exactly once on first access and never mutated thereafter. Used by `_apply_planet_intrinsic_abilities`, `_apply_star_intrinsic_abilities`, and `_apply_system_archetype` — all free functions called during galaxy generation. The `global` keyword is required for the lazy-init pattern. No test reset needed — these are configuration data, not mutable runtime state.

### `game/strategy/engine/minefield_balance.py:107,149–180`

```python
_CACHED: Optional[MinefieldBalance] = None

def load_minefield_balance(force_reload: bool = False) -> MinefieldBalance:
    global _CACHED
    ...

def reset_minefield_balance_cache() -> None:
    global _CACHED
    _CACHED = None
```

**Valid.** Lazy-load pattern with `force_reload` support and explicit test-reset helper. `MinefieldBalance` is a frozen dataclass — once loaded, the cached instance is immutable. Pattern #12 variant.

---

## NO ISSUES — Deterministic Scan Clean Categories

| Scanner | Result |
|---|---|
| `random_seed_sites_03.json` | **Empty** — zero module-level `random.seed()` or `random.<fn>()` calls in simulation/engine/AI. All `import random` in shard 03 files are for `random.Random()` class usage (Pattern #18 compliant). |
| `class_mutable_defaults_03.json` | **Empty** — zero class-level mutable default arguments (list/dict literals in parameter defaults). |
| `module_mutables_03.json` | **All `__all__` lists** — 40+ entries, every one is a standard module-level `__all__ = [...]` export list. No actual mutable state (these are list literals assigned once at import and never mutated). |
| `ctx_usage_ratio_03.json` | **87.3% ctx accesses** (62 ctx.xxx vs 9 get_default_xxx) — healthy. No singleton divergence pattern detected. |

---

## Additional Spot-Check Findings (no issues)

The following files were manually reviewed and confirmed free of state management concerns:

- `game/core/config.py` — Class-level constants only (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, etc.). No instance state, no mutable defaults.
- `game/core/paths.py` — Module-level `_PROJECT_ROOT` resolved at import time, then immutable `Paths` class with string constants.
- `game/core/event_logging.py` — `EventBus` class, session-scoped. PROJ-390 retired the module-level singleton shim. No module-level state.
- `game/strategy/engine/game_session.py` — Instance-scoped state, constructor-injected services, Pattern #42 (Bootstrap-State Single Assignment Path) compliant.
- `game/strategy/engine/turn_state_snapshot.py` — `@dataclass` with `field(default_factory=list/dict)` — function-scoped default factories, no shared mutable state.
- `game/strategy/facade/grouped_namespaces.py` — All namespace dataclasses with `__slots__`, receiving slices at construction. Pure delegation, no module-level state.
- `game/strategy/config/__init__.py` — Empty `__init__.py`.
- `game/strategy/generation/density/__init__.py` — Pure re-export `__init__.py`, no state.
- `game/strategy/generation/density/primitives/density_primitive.py` — Protocol definition + pure `clamp_density` function.
- `game/strategy/data/environmental_preference.py` — `@dataclass` with per-instance validation.
- `game/strategy/services/design_validator.py` — Constructor-injected `GameRegistries`.
- `game/strategy/services/planet_query_service.py` — All-static methods, no instance state.
- `game/strategy/services/fleet_speed_calculator.py` — All-static methods, module-level constants (`K_STRATEGIC`, etc.) only.
- `game/strategy/services/empire_economy_service.py` — Constructor-injected dependencies, per-turn caching through `FacadeSessionState`.
- `game/strategy/facade/slices/empire_slice.py` — `__slots__`, receives `FacadeSessionState` at construction.
- `game/strategy/systems/race_library.py` — Instance-scoped `RaceLibrary` and `CachedRaceRegistry`.
- `game/ui/services/modifier_icon_service.py` — Per-instance `_cache` dict, module-level `MODIFIER_ICON_MAP` is a constant dict (never mutated).
- `game/ui/services/design_loader_adapter.py` — Constructor-injected `registry_provider`.
- `game/ai/group_target_coordinator.py` — All methods are stateless (static or take inputs and return results).

---

## Compliance Summary

| Pattern | Status |
|---|---|
| #1 (ApplicationContext) | Compliant — `ctx.create_production()` sets all `_default_*` accessors; `ctx.create_test()` provides isolated overrides. |
| #4 (Registry DI) | Compliant — `get_default_registry_provider()` used only at composition roots (`GameSession._resolve_registries`); simulation files use explicit/constructor-injected registries. |
| #12 (Configuration Classes) | Compliant — three singleton-accessor flavors documented and consistent. |
| #18 (Per-Battle RNG) | **Partial divergence** — `ShipCombatEngine._damage_calculator` is correctly seeded per battle, but accessed via class-level shared attribute rather than per-instance injection. Otherwise fully compliant across simulation/AI/engine. |
| #28 (Background Service Call) | Compliant — `ImageBackgroundCall` module-level concurrency accounting mirrors `LLMBackgroundCall`. |

---

**End of Shard 03 audit.**
