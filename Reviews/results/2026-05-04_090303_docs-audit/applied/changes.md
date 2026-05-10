# Applied Changes

Per-CONFIRMED-fix before/after snippets. Cross-reference verdicts in [verification_log.md](verification_log.md).

---

## T0-01: Dead test path in adding_modifiers.md

**Doc:** `docs/guides/adding_modifiers.md`

**Before:**
```text
Add regression test in `tests/regression/test_modifier_ability_snapshots.py`:
```

**After:**
```text
Add regression test in the appropriate file under `tests/regression/modifier_ability_snapshots/` (e.g. `test_weapon_modifiers.py` for weapon modifiers, `test_utility_modifiers.py` for utility modifiers):
```

`Last verified` line updated to 2026-05-04.

---

## T0-02: Stale movement.py imports in adding_abilities.md (2 sites)

**Doc:** `docs/guides/adding_abilities.md`

**Before (line 135 in __init__.py example block):**
```text
from .movement import ThrusterAbility
```

**After:**
```text
from .propulsion import ThrusterAbility
```

**Before (line 404 in unit-test example block):**
```text
    from game.simulation.components.abilities.movement import ThrusterAbility
```

**After:**
```text
    from game.simulation.components.abilities.propulsion import ThrusterAbility
```

`Last verified` line updated to 2026-05-04.

---

## T1-04: protocols.py → protocols/ across 4 docs (12 sites)

### `docs/01_ARCHITECTURE.md` (3 sites)

**Before (line 124, core-module table):**
```text
| `protocols.py`        | All cross-layer Protocol definitions (see Protocols section) |
```
**After:**
```text
| `protocols/`          | All cross-layer Protocol definitions, decomposed into 9 sub-modules (PROJ-309): `boundary.py`, `combat.py`, `common.py`, `persistence.py`, `registry.py`, `strategy_domain.py`, `strategy_entities.py`, `ui.py` (see Protocols section) |
```

**Before (line 276):**
```text
All defined in `game/core/protocols.py`. Uses `@runtime_checkable` Protocol classes...
```
**After:**
```text
All defined in `game/core/protocols/` (9-module package; PROJ-309). Uses `@runtime_checkable` Protocol classes... The package's `__init__.py` re-exports every symbol so `from game.core.protocols import X` continues to work.
```

**Before (line 346):**
```text
Layers communicate through Protocol definitions in `game/core/protocols.py`.
```
**After:**
```text
Layers communicate through Protocol definitions in `game/core/protocols/`.
```

### `docs/02_PATTERNS.md` (7 sites)

**Line 150:** `game/core/protocols.py -- all protocol definitions...` → `game/core/protocols/ -- 9-module package (PROJ-309) holding every protocol definition...` (with sub-module list).

**Line 158 (code-block comment):** `# game/core/protocols.py (actual code)` → `# game/core/protocols/strategy_entities.py (actual code)`.

**Line 183:** `see game/core/protocols.py for the full list` → `see game/core/protocols/ for the full list`.

**Line 207:** `(protocol in protocols.py)` → `(protocol in game/core/protocols/registry.py)`.

**Line 1185 (Pattern #17):** `Protocol: game/core/protocols.py -- ISerializable` → `Protocol: game/core/protocols/persistence.py -- ISerializable`.

**Line 1526 (Quick Reference):** `Protocol+TypeGuard | game/core/protocols.py | IFleet, is_fleet()` → `Protocol+TypeGuard | game/core/protocols/strategy_entities.py | IFleet, is_fleet()`.

**Line 1546 (Quick Reference):** `Serializable | game/core/protocols.py | ISerializable` → `Serializable | game/core/protocols/persistence.py | ISerializable`.

### `docs/04_SERVICES.md` (1 site)

**Line 1114:** `IRaceRegistry in game/core/protocols.py` → `IRaceRegistry in game/core/protocols/strategy_domain.py`.

### `docs/systems/strategy_layer.md` (1 site)

**Line 680:** `IOrderable protocol (game/core/protocols.py)` → `IOrderable protocol (game/core/protocols/strategy_entities.py)`.

`Last verified` updated on all 4 docs.

---

## T1-05: Exception count in 01_ARCHITECTURE.md

**Doc:** `docs/01_ARCHITECTURE.md`

**Before:**
```text
| `exceptions.py`       | GameException hierarchy (10 exception classes) |
```

**After:**
```text
| `exceptions.py`       | GameException hierarchy (26 exception classes including LLM and Image hierarchies from PROJ-296 and PROJ-314) |
```

---

## T1-06: Core exports count

**Doc:** `docs/01_ARCHITECTURE.md`

**Before:**
```text
### `game.core` (46 exports)
```
**After:**
```text
### `game.core` (53 exports)
```

---

## T1-07: Pattern count 30/31 → 33 in README (3 sites)

**Doc:** `docs/README.md`

**Before (Last verified line):**
```text
> **Last verified:** 2026-04-28 — PROJ-318 documentation consistency pass: pattern count is 31, ...
```
**After:** Replaced with 2026-05-04 audit-fix entry; pattern count = 33.

**Before (line 17, Reading Order table):**
```text
| 2 | [02_PATTERNS.md](02_PATTERNS.md) | 30 design patterns with file locations and code examples |
```
**After:**
```text
| 2 | [02_PATTERNS.md](02_PATTERNS.md) | 33 design patterns with file locations and code examples |
```

**Before (line 68, Directory Structure):**
```text
├── 02_PATTERNS.md               # 30 design patterns (... Registrar Close-Callback, ...)
```
**After:**
```text
├── 02_PATTERNS.md               # 33 design patterns (... Compositional Construction, UI Widget Test Factory, ...)
```

(Replaced "Registrar Close-Callback" callout with two current pattern names per cross-doc finding §8.1 row 2.)

---

## T1-08: test_lab handler filename

**Doc:** `docs/03_CONVENTIONS.md`

**Before:**
```text
| `TestLabInputHandler` | `game/ui/screens/test_lab/test_lab_input_handler.py` |
```
**After:**
```text
| `TestLabInputHandler` | `game/ui/screens/test_lab/screen_input_handler.py` |
```

---

## T1-09: Stale planetary.py ability list in combat_simulation.md

**Doc:** `docs/systems/combat_simulation.md`

**Before:**
```text
| `planetary.py` | PlanetaryShieldAbility, PlanetaryEnergyGeneratorAbility, PlanetaryEnergyStorageAbility |
```
**After:**
```text
| `planetary.py` | PlanetaryShieldAbility, StrategicResourceGenerationAbility, GeologicStabilizerAbility, StellarStabilizerAbility, WarpFieldStabilizerAbility, ResourceHarvestBoosterAbility, BuildRateBoosterAbility, AtmosphereModifierAbility, QualityImprovementAbility, ShieldModifierAbility, DamageModifierAbility, GravityModifierAbility, WaterModifierAbility, RadiationShieldAbility, ThrustModifierAbility, StrategicSpeedModifierAbility, EnvironmentalDamageAbility, FuelDrainAbility |
```

---

## T1-10: PodStorageAbility class claim in ability_reference.md (2 sites)

**Doc:** `docs/systems/ability_reference.md`

**Before (lines 773-774, detail row):**
```text
| Class | `PodStorageAbility` |
| Source | `cargo.py` |
```
**After:**
```text
| Class | _none — `PodStorage` has no Python class; data is read directly from the raw `comp.abilities['PodStorage']` dict in `game/simulation/entities/ship_stats.py`_ |
| Source | `game/simulation/entities/ship_stats.py` (raw dict access; no `cargo.py` ability class) |
```

**Before (line 1555, quick-ref table):**
```text
| `PodStorage` | PodStorageAbility | Cargo |
```
**After:**
```text
| `PodStorage` | _no ability class — raw dict access in `ship_stats.py`_ | Cargo |
```

---

## T1-11: §10.2 PNG section reference

**Doc:** `docs/03_CONVENTIONS.md`

**Before:**
```text
- All ship-theme assets are PNG only (per §5 / `docs/03_CONVENTIONS.md`
  §285–288). JPG is not supported.
```
**After:**
```text
- All ship-theme assets are PNG only (per §3.2 "Image Asset Format
  Convention"). JPG is not supported.
```

---

## T1-12: Duplicate §6.5 → §6.6

**Doc:** `docs/03_CONVENTIONS.md`

**Before:**
```text
### 6.5 System Migration
```
**After:**
```text
### 6.6 System Migration
```

(First §6.5 "No Hardcoded Type Lists" at line 495 retained; second §6.5 at line 512 renumbered to §6.6.)

---

## T2-15: Missing core modules in architecture table

**Doc:** `docs/01_ARCHITECTURE.md`

**Before (between input_actions.py and json_utils.py):**
```text
| `input_actions.py`    | InputAction enum for key bindings |
| `json_utils.py`       | JSON serialization helpers |
```

**After:**
```text
| `input_actions.py`    | InputAction enum for key bindings |
| `ship_classes.py`     | Ship class enumeration / categorization |
| `component_state.py`  | Per-component runtime state container |
| `state_machine.py`    | `ScreenStateMachine` (PROJ-259) — generic state transitions |
| `return_destination.py`| Battle-flow return-destination data type |
| `json_utils.py`       | JSON serialization helpers |
```

---

## T2-16: replay_player.py late-import addition

**Doc:** `docs/01_ARCHITECTURE.md`

**Before (Late Imports list, last entry):**
```text
- `Fleet.trigger_speed_recalculation()` imports FleetSpeedCalculator (edge operation)
```

**After:**
```text
- `Fleet.trigger_speed_recalculation()` imports FleetSpeedCalculator (edge operation)
- `ReplayPlayer._materialize_ship_state()` imports ShipInstanceSerializer from `game/strategy/data/` (`game/simulation/replay/replay_player.py:72`; cross-layer boundary required for replay reconstruction)
```

---

## T2-19: Missing strategic abilities in quick-reference table

**Doc:** `docs/systems/ability_reference.md`

**Before (transition row from Planet Modifiers to Superweapons):**
```text
| `RadiationShield` | RadiationShieldAbility | Planet Modifiers |
| `DestroyPlanet` | DestroyPlanet | Superweapons |
```

**After:**
```text
| `RadiationShield` | RadiationShieldAbility | Planet Modifiers |
| `EnvironmentalDamage` | EnvironmentalDamageAbility | Strategic Sector/System (PROJ-300..305) |
| `FuelDrain` | FuelDrainAbility | Strategic Sector/System (PROJ-300..305) |
| `StrategicSpeedModifier` | StrategicSpeedModifierAbility | Strategic Sector/System (PROJ-300..305) |
| `ThrustModifier` | ThrustModifierAbility | Strategic Sector/System (PROJ-300..305) |
| `DestroyPlanet` | DestroyPlanet | Superweapons |
```

---

## T2-21: WORKER_TEMPLATE.md retired Protocol 08 reference

**Doc:** `Projects/protocols/WORKER_TEMPLATE.md`

**Before:**
```text
**Primary:** `Projects/protocols/08_automated_loop_protocol.md`
```
**After:**
```text
**Primary:** `Projects/protocols/08_automated_loop_protocol.md` _(RETIRED — kept for historical reference; the automated-loop runner workflow is no longer active. Use `03a_continue_working.md` for the current autonomous-work loop.)_
```

---

## Summary of `Last verified` updates

Per `docs/03_CONVENTIONS.md` §9, every modified `docs/` file received a fresh `Last verified` line for 2026-05-04:

| Doc | Items in this run |
|-----|-------------------|
| `docs/01_ARCHITECTURE.md` | T1-04 (×3), T1-05, T1-06, T2-15, T2-16 |
| `docs/02_PATTERNS.md` | T1-04 (×7) |
| `docs/03_CONVENTIONS.md` | T1-08, T1-11, T1-12 |
| `docs/04_SERVICES.md` | T1-04 (×1) |
| `docs/README.md` | T1-07 (×3) |
| `docs/guides/adding_abilities.md` | T0-02 (×2) |
| `docs/guides/adding_modifiers.md` | T0-01 |
| `docs/systems/ability_reference.md` | T1-10 (×2), T2-19 |
| `docs/systems/combat_simulation.md` | T1-09 |
| `docs/systems/strategy_layer.md` | T1-04 (×1) |

`Projects/protocols/WORKER_TEMPLATE.md` was edited (T2-21) but lives outside `docs/`, so no `Last verified` line is required there per protocol scope notes.
