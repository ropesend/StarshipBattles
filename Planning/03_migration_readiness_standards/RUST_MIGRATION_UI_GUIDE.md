# UI-Specific Rust Migration Planning Guide

This is a planning document for Stage 3: Migration-Readiness Standards.

It records guidance for keeping the current Python/Pygame UI compatible with a future Rust-based authoritative core or simulation core. It is not an implementation project. Implementation should happen later through the existing `Projects/` system.

## Purpose

The likely future migration path is not a full rewrite of the entire game at once. The safer path is:

1. Keep the UI in Python while game rules and workflows are still changing.
2. Make the UI communicate through stable DTOs, commands, events, and player-visible packages.
3. Move simulation, turn resolution, visibility, pathfinding, AI search, or server authority into Rust later, once boundaries stabilize.
4. Preserve Python UI and tooling as a client/front end as long as useful.

This document focuses on the UI side of that plan.

## Current Architecture Context

The current layer model puts UI at the top. UI may depend on AI, Strategy, Research, Simulation, Engine, Services, Assets, and Core. Lower layers should not depend on UI.

That is good for migration. It means a future Rust core can replace lower-layer behavior while the UI remains a client of stable boundary APIs.

Current UI areas include:

- `game/ui/screens/`: battle screen, strategy screen, design workshop, menus, setup screens, test lab, galaxy test, build queue, strategy render/windows, race setup, etc.
- `game/ui/renderer/`: camera, renderer, sprite manager.
- `game/ui/panels/`: battle panels, builder widgets, report panels, galleries, treasury/build queue panels.
- `game/ui/components/`: reusable UI components and table/filter widgets.
- `game/ui/widgets/`: panels, dropdowns, range controls, scroll widgets, element registry.
- `game/ui/services/`: input mapping, ship factory/I/O, component/validation services, game settings, image generation service.
- `game/ui/research/`: research UI.

The UI currently has permission to import game systems directly. Over time, this should be narrowed for migration readiness.

## Core Principle For UI Migration Readiness

The UI should become a client of a game-facing API, not a direct manipulator of game internals.

A future Rust core should not need to know that the UI is Pygame. The UI should not need to know whether the authoritative game state is Python or Rust.

Target shape:

```text
Python/Pygame UI
  -> read player-visible DTOs/packages
  -> render screens/panels/widgets
  -> create command DTOs / order submissions
  -> send commands to authoritative game API
  -> receive events/results/snapshots

Rust or Python authoritative core
  -> owns true game state
  -> validates commands
  -> processes turns/combat/visibility
  -> returns player-visible DTOs/packages
```

## What The UI Should Own Long-Term

The UI should own presentation concerns only:

- Screen flow.
- Layout.
- Camera position and zoom.
- Window placement.
- User input mapping.
- Selection state.
- Sorting/filtering/pagination state.
- Expanded/collapsed UI panels.
- Visual effects.
- Tooltips.
- Render caches.
- Local-only preferences.
- Modal dialogs.
- Human-readable presentation of DTO data.

The UI should not own authoritative game rules, hidden information, command authorization, or turn resolution.

## What The UI Should Not Own Long-Term

The UI should not be the source of truth for:

- Fleet location.
- Planet ownership.
- Colony resources.
- Ship component status.
- Research completion.
- Visibility/fog-of-war truth.
- Enemy fleet composition.
- Combat outcome.
- Turn advancement.
- Command legality.
- Build queue resolution.
- Production output.
- AI decisions.
- Random outcomes.

The UI may display these things, but it should receive them through player-visible DTOs or events.

## Recommended Boundary Objects

The UI should increasingly talk to the game through explicit boundary objects.

### Read-side DTOs

Examples:

- `PlayerTurnPackage`
- `IntelSnapshot`
- `SectorContact`
- `ShipContact`
- `FleetInfo`
- `PlanetInfo`
- `SystemInfo`
- `EmpireInfo`
- `ResearchStateInfo`
- `BuildQueueInfo`
- `BattleSetupInfo`
- `BattleOutcomeInfo`
- `EventLogInfo`

These should be stable, typed, serializable, and usable whether they are built by Python or Rust.

### Write-side DTOs

Examples:

- `OrdersSubmission`
- `CommandBatch`
- `IssueMoveCommand`
- `IssueWarpCommand`
- `IssueBuildOrderCommand`
- `SetResearchAllocationCommand`
- `ActivateAbilityCommand`
- `SetSensorModeCommand`
- `SetScannerModeCommand`
- `ConfigureFleetFormationCommand`

Commands should use stable IDs and value data, not live Python object references.

### Event DTOs

Examples:

- `TurnProcessedEvent`
- `FleetMovedEvent`
- `ContactDetectedEvent`
- `ContactLostEvent`
- `GhostContactUpdatedEvent`
- `ResearchBreakthroughEvent`
- `BattleResolvedEvent`
- `BuildCompletedEvent`
- `ValidationFailedEvent`

Events should be filtered by player/empire when hidden information matters.

## UI API Target Shape

A future-compatible UI-facing game API might look conceptually like this:

```text
GameClientApi:
  get_current_player_package() -> PlayerTurnPackage
  submit_orders(OrdersSubmission) -> ValidationResult / SubmissionResult
  process_turn() -> TurnResolutionReport / PlayerTurnPackage
  get_battle_setup(context_id) -> BattleSetupInfo
  submit_battle_orders(...) -> BattleCommandSubmission
  get_research_state(empire_id) -> ResearchStateInfo
  get_event_log(empire_id, filters) -> EventLogInfo
```

This can start as a Python facade over the current game state. Later, the same conceptual API can call Rust via FFI, IPC, local server transport, or serialized files.

## UI Rules For Migration Readiness

### 1. Prefer DTO reads over raw object reads

Bad long-term pattern:

```text
screen.selected_fleet.ships[0].components[...]
```

Better long-term pattern:

```text
selected_ship_info = player_package.visible_ships[ship_contact_id]
```

The UI should increasingly consume read-only DTOs, especially for strategy map, intel, research, production, and enemy contacts.

### 2. Prefer commands over direct mutation

Bad long-term pattern:

```text
fleet.location = target_hex
planet.build_queue.append(item)
```

Better long-term pattern:

```text
facade.commands.issue_move(fleet_id=..., target_hex=...)
facade.commands.add_to_construction_queue(...)
```

Eventually the UI should submit commands to a game API rather than call direct mutators.

### 3. Use stable IDs across the UI boundary

The UI should store and pass stable IDs:

- `empire_id`
- `fleet_id`
- `ship_instance_id`
- `planet_id`
- `system_id`
- `contact_id`
- `component_instance_id`
- `tech_id`
- `command_id`

Avoid holding long-lived references to mutable domain objects. This is especially important for Rust migration because Python object identity will not cross the language boundary.

### 4. Keep UI state separate from game state

UI-specific state should remain UI-owned:

- Selected contact/fleet/planet ID.
- Camera center/zoom.
- Open windows.
- Sort/filter state.
- Active tab.
- Hovered item.
- Tooltip state.

Game state should remain authoritative-core-owned.

### 5. Avoid UI-side hidden-information filtering

The authoritative game API should not send hidden information to the UI and rely on the UI to hide it.

Bad long-term pattern:

```text
UI receives all enemy fleets and filters by visibility.
```

Better long-term pattern:

```text
UI receives only SectorContact/ShipContact data the player is allowed to know.
```

This is required for multiplayer and also makes AI fairness cleaner.

### 6. Keep rendering data separate from game data

Rendered sprites, colors, icons, image paths, animation state, and cached surfaces should not be part of authoritative DTOs.

DTOs may contain symbolic display hints such as:

- `icon_id`
- `sprite_key`
- `color_role`
- `display_name`
- `size_class`

But the Pygame-specific surface/image/cache should stay in UI/Assets code.

### 7. Keep long-running turn/combat processing out of UI loops

The UI may show progress and pump events, but turn/combat resolution should be game-core work. The UI should receive progress callbacks, events, or status updates rather than owning the algorithm.

### 8. Make UI services replaceable

UI services should be injectable or swappable where reasonable:

- Asset manager.
- Sprite manager.
- Input mapping.
- Game settings.
- Image provider.
- Game client API.

This allows tests and future Rust-backed adapters to substitute implementations.

## Recommended UI Refactor Direction

Do not try to refactor the entire UI at once.

Use vertical slices.

Suggested order:

1. Identify one screen/panel that currently reads raw strategy state.
2. Define the DTO it actually needs.
3. Add a Python adapter that builds that DTO from the current game state.
4. Convert the screen/panel to use the DTO.
5. Add tests for DTO construction and screen behavior if practical.
6. Repeat for the next UI area.

Good first candidates:

- Strategy map enemy contacts.
- Fleet report panel.
- Planet report panel.
- Research panel.
- Build queue panel.
- Event log.

The visibility/fog-of-war work should strongly prioritize this pattern because enemy contacts must not expose raw enemy fleet objects.

## Strategy UI And Future Rust Core

The strategy UI should eventually treat the game as an external authoritative service, even if it is in-process Python today.

Target flow:

```text
StrategyScreen asks GameClientApi for PlayerTurnPackage.
StrategyScreen renders known stars, owned assets, visible contacts, remembered contacts, events, research, and economy.
User input creates command DTOs.
Commands are submitted to GameClientApi.
GameClientApi returns validation results or updated local package.
Turn processing returns a new PlayerTurnPackage and filtered events.
```

This makes the UI compatible with:

- Current Python GameSession.
- Future Rust library called through FFI.
- Future local server process.
- Future network multiplayer server.
- Future PBEM-style file exchange.

## Battle UI And Future Rust Core

Battle UI should also avoid owning authoritative simulation state long term.

Target flow:

```text
BattleScreen receives BattleSetupInfo / BattleSpec view data.
User issues tactical commands or chooses policies/formations.
Simulation core resolves ticks/battle state.
UI renders BattleFrameSnapshot or subscribes to battle state updates.
Battle outcome is returned as a BattleOutcomeInfo / BattleOutcome DTO.
```

If tactical combat eventually moves to Rust, the Python UI should not need to know whether ticks were simulated by Python or Rust.

Important boundary objects:

- Battle setup DTO.
- Battle frame snapshot DTO.
- Tactical command DTO.
- Battle outcome DTO.
- Replay DTO.

Avoid direct UI mutation of simulation entities during authoritative combat.

## Research UI And Future Rust Core

Research UI should display research state and submit allocation commands.

Target flow:

```text
Research UI receives ResearchStateInfo.
User changes allocation.
UI sends SetResearchAllocationCommand or ResearchAllocationSubmission.
Game core validates budget and tech availability.
Turn processing advances research.
UI receives updated ResearchStateInfo and filtered research events.
```

The UI should not be the authority on:

- RP budget.
- Available nodes.
- Breakthrough rolls.
- Tech completion.
- Component unlock legality.

## Visibility/Fog UI And Future Rust Core

The UI should render contacts, not hidden truth.

Target flow:

```text
Game core computes IntelSnapshot for active empire.
UI renders:
- known stars
- known systems
- owned fleets/colonies
- current contacts
- remembered/ghost contacts
- visible planets/warp points

UI does not receive raw hidden enemy fleets.
```

This is a major migration-readiness requirement because hidden information must be enforced by the authoritative core, not by UI convention.

## Suggested Serialization Discipline

UI-facing DTOs should be designed as if they will cross a process/language boundary.

Recommended constraints:

- JSON-compatible primitives where practical.
- Stable enum/string IDs.
- No Python object references.
- No Pygame types.
- No callbacks inside DTOs.
- No arbitrary lambdas/functions.
- Explicit versioning for large schemas.
- Round-trip tests for important DTOs.

Rust compatibility is easier if DTOs can map naturally to:

```text
structs
enums
Vec<T>
HashMap<K, V>
Option<T>
Result<T, E>
```

Avoid UI DTO shapes that depend on Python inheritance tricks, dynamic attributes, monkey-patching, or non-serializable closures.

## Possible Communication Boundary Options

Do not choose too early, but keep these options open:

| Option | Description | Pros | Cons |
|---|---|---|---|
| In-process Python adapter | Current Python facade builds DTOs. | Easy now. | Not a Rust boundary yet. |
| Rust FFI library | Python calls Rust functions directly. | Fast, local. | More complex memory/error boundary. |
| Local server process | Python UI talks to Rust/Python server over IPC/HTTP/WebSocket. | Clean authority boundary. | More infrastructure. |
| PBEM/file packages | Export/import turn packages and orders. | Very debuggable. | Less interactive. |
| Network server | True multiplayer server. | Final multiplayer direction. | Most complex. |

The UI should be written so that changing the transport does not require rewriting screens.

## UI Anti-Patterns To Avoid

Avoid adding new code that:

- Stores long-lived mutable domain object references in UI widgets.
- Mutates strategy/simulation entities directly from UI event handlers.
- Filters hidden enemy information in UI after receiving raw truth.
- Computes authoritative game rules in panels/screens.
- Uses Pygame types in DTOs intended for game-core boundaries.
- Builds large command payloads from arbitrary dicts with no schema.
- Assumes Python object identity is stable across save/load or turn processing.
- Requires a full UI loop to test core algorithms.
- Uses module-level mutable state as the hidden communication channel between UI and game logic.

## UI-Friendly Migration Checklist

For each UI screen/panel/window, eventually answer:

1. What authoritative game data does it read today?
2. What player-visible DTO should replace that direct read?
3. What commands does it create?
4. Does it directly mutate domain objects?
5. Does it store long-lived object references that should become IDs?
6. Does it receive hidden information and filter it locally?
7. Does it run game rules that belong in Strategy/Simulation/Research/Core?
8. Does it depend on Pygame-only types in boundary data?
9. Can it be tested with fake DTOs and fake command results?
10. Would it still work if the game core lived in a Rust process?

## Suggested Implementation Projects Later

Use the existing `Projects/` system. Possible future project slices:

1. Create a `GameClientApi` Python protocol/facade for UI-to-game communication.
2. Add `PlayerTurnPackage` DTO and adapter for current GameSession.
3. Convert strategy map enemy rendering to contacts instead of raw enemy fleets.
4. Convert one report panel from raw objects to DTOs.
5. Convert research UI to allocation commands and read-only research DTOs.
6. Convert build queue UI to commands and build queue DTOs.
7. Add UI boundary serialization tests for major DTOs.
8. Add lints or tests preventing lower layers from importing UI.
9. Add tests that UI can run with fake game-client data.
10. Prototype a second GameClientApi implementation that calls a fake external process or serialized package.

## Open Questions For Future Planning

1. Should Python/Pygame remain the long-term UI even after the core migrates to Rust?
2. Should the first Rust boundary be FFI or a separate local server process?
3. Should the UI eventually be web-based instead of Pygame, or is that out of scope?
4. How strict should DTO serialization compatibility be before Rust work begins?
5. Should battle visualization remain Python-driven while Rust simulates ticks?
6. Should UI tests use fake DTO packages as the primary strategy?
7. Which screen should be the first vertical slice for DTO-only data access?
8. Should UI selection state always store IDs rather than object references?
9. How much display metadata should come from the core versus Assets/UI registries?
10. Should the game client API support async/progress streaming from the start?

## Current Recommendation

Keep the UI in Python for now. Do not plan a full UI rewrite as part of the Rust migration.

Instead, make the UI increasingly backend-agnostic:

- Read DTOs/packages.
- Send commands.
- Store IDs, not object references.
- Keep UI state local.
- Keep hidden information out of UI inputs.
- Keep rendering assets separate from game rules.
- Add tests using fake DTOs.

If these rules are followed, a future Rust core can replace performance-critical systems without forcing a simultaneous UI rewrite.
