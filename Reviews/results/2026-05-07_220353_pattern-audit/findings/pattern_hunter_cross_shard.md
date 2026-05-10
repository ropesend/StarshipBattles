# Cross-Shard Pattern Hunter Report

## Summary
- Pattern Checks Performed: 5
- Total Findings: 14
- Critical: 2 | Major: 4 | Minor: 8

---

## Facade Integrity (#5)

### CRITICAL — StrategyScreen dual-reference bypass (`strategy_screen.py:79,83,86,155-182`)

`StrategyScreen` holds **both** a raw `GameSession` as `self.session` **and** a `StrategySessionFacade` as `self._facade`. The pattern explicitly requires the facade to be the **only** entry point from UI into strategy. Instead, six public properties directly tunnel through the raw session:

| Property | Line | Bypass Path |
|---|---|---|
| `galaxy` | 155 | `self.session.galaxy` |
| `empires` | 159 | `self.session.empires` |
| `systems` | 163 | `self.session.systems` |
| `active_empire` | 174 | `self.session.active_empire` |
| `enemy_empire` | 178 | `self.session.enemy_empire` |
| `human_player_ids` | 182 | `self.session.human_player_ids` |

These properties are consumed by **21+ access sites** across strategy UI components (`strategy_colonization.py`, `strategy_renderer.py`, `strategy_click_dispatcher.py`, `strategy_fleet_ops.py`, `strategy_camera_nav.py`, `strategy_superweapons.py`). The facets directly bypass the facade and return mutable domain objects (e.g. `Galaxy`, `list[Empire]`, `list[StarSystem]`) rather than read-only DTOs.

### CRITICAL — Widespread `scene.session` access throughout UI (12 sites)

Even outside the StrategyScreen properties, UI code reaches directly into `scene.session`:

| File | Line | What's Accessed | Why This Bypasses Facade |
|---|---|---|---|
| `strategy_detail_formatter.py` | 112 | `self.scene.session.registries` | Registry access bypasses facade |
| `strategy_detail_formatter.py` | 278 | `self.scene.session.registries` | Same |
| `strategy_detail_formatter.py` | 395–396 | `self.scene.session.turn_engine.validate_colonize_order(...)` | **Direct turn engine call** — worst bypass |
| `strategy_render/hex_outlines.py` | 30 | `scene.session.active_empire` | State query bypass |
| `strategy_render/fleets.py` | 85 | `r.scene.session.get_fleet_path_projection(fleet)` | Fleet query bypass |
| `strategy_windows/empire_panel_ctrl.py` | 48 | `c.scene.session.registries` | Registry bypass |
| `strategy_windows/list_windows.py` | 60–61 | `c.scene.session.empires`, `c.scene.session.registries` | Domain + registry bypass |
| `strategy_windows/build_queue_windows.py` | 73 | `session=c.scene.session` | Raw session leak to child window |
| `strategy_event_router.py` | 193, 338 | `scene.session.get_empire(planet.owner_id)` | Empire lookup bypass |
| `transfer_controller.py` | 137 | `session = scene.session` | Session capture bypass |

### MAJOR — Zero usage of facade `dispatch_*` helpers

The facade auto-generates `dispatch_*` bound methods for every registered command via `_install_dispatch_forwarders()` (`strategy_session_facade.py:405-434`). **Not a single UI caller uses them.** All 32 `facade.handle_command(...)` callsites construct command DTOs manually by importing from `game.strategy.engine.commands` — meaning 127 UI imports from `game.strategy.(data|engine)`.

### MAJOR — Direct domain object imports in UI for runtime use

| File | Line | Import |
|---|---|---|
| `battle_setup_state.py` | 14 | `from game.strategy.data.fleet import Fleet` (runtime, not TYPE_CHECKING) |
| `battle_setup/spec_compiler.py` | 74 | `from game.strategy.data.fleet import Fleet` (method-local runtime) |
| `battle_setup/fleet_hierarchy_editor.py` | 22 | `from game.strategy.data.fleet import Fleet` (TYPE_CHECKING only, acceptable) |
| `food_allocation_editor.py` | 40 | `from game.strategy.data.planet import Planet` (method-local runtime) |
| `galaxy_test/galaxy_mode.py` | 18 | `from game.strategy.data.galaxy import Galaxy` (runtime) |
| `strategy_superweapons.py` | 30 | `from game.strategy.data.fleet import Fleet` (method-local runtime) |

`galaxy_test/` and `battle_setup/` screens are developer-facing test utilities, which reduces severity, but `strategy_superweapons.py` and `food_allocation_editor.py` are production screens.

### MINOR — Import of `GameSession` type in `strategy_screen.py:81`

The constructor creates a `GameSession` directly when none is passed, and the import is unconditional (not TYPE_CHECKING). The facade pattern should handle session creation.

---

## Registry Pattern Consistency (#4)

### MINOR — Unauthorized session-level registry access

`strategy_detail_formatter.py:112,278` accesses `self.scene.session.registries` directly rather than using `get_default_registry_provider()`. This creates an inconsistent access path — the same registries are reached via facade session in some places and via the global provider in others.

### MINOR — Registry provider gated behind optional `session` reference

`strategy_windows/empire_panel_ctrl.py:48` and `list_windows.py:61` propagate registries as `c.scene.session.registries`. The screen's `session` reference serves as a backdoor for registries that could instead be obtained through the canonical `get_default_registry_provider()` path that the rest of the UI already uses consistently.

---

## Event Bus Fragmentation (#10)

Three EventBus implementations exist and are appropriately scoped:
- **Builder EventBus** (`game/ui/screens/builder/event_bus.py`) — workshop UI pub/sub; consumers limited to builder/test-lab/build-queue screens. No cross-use with other buses.
- **Core EventBus** (`game/core/event_logging.py`) — session-scoped, used by `GameSession` and sub-engines for structured event logging.
- **CombatEventBus** (`game/simulation/combat/combat_events.py`) — battle-scoped for damage/armor telemetry, segregated from the strategy event log.

### MAJOR — Simulation layer uses global `log_event` shim

`game/simulation/entities/projectile.py:4` imports `from game.core.event_logging import log_event`. This is a **module-level global** in the simulation layer, violating the rule that "simulation code must not call module-level random/repository globals" (extended here to event logging). The `EventBus` should be injected through `BattleEngine`, which already creates a `CombatEventBus` at `battle_engine.py:220-221`. The projectile fires events through a process-global handler — if two battles run concurrently or tests share state, they will interfere.

### MINOR — Strategy data classes fall back to global `log_event`

`game/strategy/data/empire.py:118` and `game/strategy/data/fleet.py:400` accept `event_bus: Optional[EventBus]` but fall back to `from game.core.event_logging import log_event` when `event_bus is None`. This creates a split path — properly injected when called from the engine, global when called from tests or edge cases. Both sites handle event logging for fleet removal/pursuer redirection, which involves strategy state mutation outside the command handler path.

### MINOR — Missing event bus in `superweapon_order_processor.py`

`game/strategy/engine/superweapon_order_processor.py:64` declares `event_bus: Optional EventBus` as a constructor parameter described as "Currently unused". This is dead code in the event bus injection surface.

---

## CQRS-lite Audit (#6)

### MAJOR — Direct turn engine call bypassing all CQRS pathways

`game/ui/screens/strategy_detail_formatter.py:395-396`:
```python
if self.scene.session and self.scene.session.turn_engine:
    res = self.scene.session.turn_engine.validate_colonize_order(self.scene.galaxy, obj, None)
```
This reaches **three layers deep** past the facade (`scene -> session -> turn_engine`) to call `validate_colonize_order` directly. This subverts:
- The facade (no `facade.` prefix)
- CQRS-lite (no command DTO, no handler, no validation pipeline)
- The composition root (turn engine is not a public API surface)

The facade already exposes `can_colonize(fleet_id, planet_id) -> ValidationResult` at line 379, which should be used instead. This bypass is for the **entire turn engine's colonize validation**, not just a simple attribute read.

### MINOR — `dispatch_*` methods exist but are completely unused

The facade's `_install_dispatch_forwarders()` (`strategy_session_facade.py:434`) generates one bound method per registered command, but no UI code consumes them. Every caller manually imports the command DTO and calls `facade.handle_command(cmd)`. While the command still flows through `handle_command` (preserving the write-path contract), the `dispatch_*` abstraction — intended to hide command construction from the UI — is dead code at the call site.

### MINOR — DTO barrier inconsistency in BuildQueue operations

`BuildQueueSourceDTO` exists in `game/strategy/facade/dto/build_queue_dto.py`, but UI files import the mutable `BuildQueueSource` from `game/strategy/data/build_queue_source.py` directly (6 files: `build_queue_screen.py`, `build_queue_controller.py`, `build_queue_panel_factory.py`, `empire_build_queue_window.py`, `build_queue_selector.py`, `empire_build_queue_viewmodel.py`). The facade provides `get_empire_build_queues() -> List[BuildQueueSourceDTO]` and `get_hex_build_queues() -> List[BuildQueueSourceDTO]`, but these are unused in favor of direct domain imports.

---

## Ability Source Drift (#29)

### MINOR — Documentation miscount (docs say 8 adapters, code has 7)

`docs/02_PATTERNS.md §29` states "Adapters include facility, storm, planet intrinsic, star, warp point, system, and fleet sources." That listing counts 7, but the preamble says "8 documented adapters." Verified source files under `game/strategy/services/ability_sources/`:

| Adapter | File | Status |
|---|---|---|
| `FacilityAbilitySource` | `facility.py` | Active, implements `IAbilitySource` |
| `StormAbilitySource` | `storm.py` | Active, implements `IAbilitySource` |
| `PlanetIntrinsicAbilitySource` | `planet_intrinsic.py` | Active, implements `IAbilitySource` |
| `StarAbilitySource` | `star.py` | Active, implements `IAbilitySource` |
| `WarpPointAbilitySource` | `warp_point.py` | Active, implements `IAbilitySource` |
| `SystemAbilitySource` | `system_archetype.py` | Active, implements `IAbilitySource` |
| `FleetAbilitySource` | `fleet.py` | Active, implements `IAbilitySource` |

Additional files: `intrinsic_roll.py` (shared utility, not an adapter), `labels.py` (formatting utility, not an adapter). All 7 adapters are properly registered via `register_source_provider` / `register_source_provider_in_system`. No new ability sources were found outside the adapter pattern.

### MINOR — `intrinsic_roll.py` uses `import random` for type annotations only

`game/strategy/services/ability_sources/intrinsic_roll.py:9` imports `import random` (the module). The function `roll_intrinsic_abilities(template, rng: random.Random)` correctly consumes only the injected `rng` parameter. The module import serves only the type annotation and never calls `random.seed()` or `random.uniform()`. This is safe but mildly fragile for future readers.

---

## Prioritized Architectural Recommendations

1. **Fix StrategyScreen dual-reference** (CRITICAL): Remove `self.session` as a public attribute. Route all six properties through `self._facade`. Add facade methods for any missing read paths (e.g. `get_galaxy_summary()`, `get_active_empire_id()`). Eliminate all `scene.session` direct access across UI by providing facade equivalents.

2. **Fix `strategy_detail_formatter.py:395-396` turn engine bypass** (MAJOR): Replace `self.scene.session.turn_engine.validate_colonize_order(...)` with `self.scene.facade.can_colonize(fleet_id, planet_id)`.

3. **Inject EventBus into simulation layer** (MAJOR): Replace `game/core/event_logging.log_event` global in `projectile.py` with an injected `CombatEventBus` from `BattleEngine`. The engine already creates a `CombatEventBus` at `battle_engine.py:220` — thread it through to projectile construction.

4. **Eliminate domain object imports from production UI** (MAJOR): Migrate `food_allocation_editor.py` and `strategy_superweapons.py` to use facade DTOs instead of importing `Planet` / `Fleet` directly.

5. **Adopt `facade.dispatch_*` or remove the dispatch layer** (MINOR): Either update UI code to call `facade.dispatch_issue_move(...)` with kwargs, or remove `_install_dispatch_forwarders()` as dead code. The current state adds ~30 lines of maintenance overhead for zero consumption.

6. **Fix `BuildQueueSource` import proliferation** (MINOR): Direct all UI build queue operations through `facade.get_empire_build_queues()` / `facade.get_hex_build_queues()` with `BuildQueueSourceDTO` instead of importing `BuildQueueSource` from `game/strategy/data/`.

7. **Resolve `empire.py`/`fleet.py` global `log_event` fallback** (MINOR): Make `event_bus` a required parameter in fleet removal/pursuer redirection methods, removing the global fallback. This simplifies the branching logic at `empire.py:114-127` where one branch uses injected `event_bus` and the `else` branch falls to `log_event`.

8. **Fix 7 vs 8 adapter doc mismatch** (MINOR): Correct `docs/02_PATTERNS.md §29` to state "7 documented adapters" instead of 8.
