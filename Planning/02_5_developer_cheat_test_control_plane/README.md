# Stage 2.5: Developer Cheat And Test Control Plane

## Purpose

Create a server-authoritative developer cheat, debug, and scenario-control system for fast playtesting without coupling cheats to normal UI/client code.

The finished game may eventually need more than 100 narrow controls: instant build, unlimited resources, unlimited fuel, add population, create instant colony, add resources to a fleet or planet, force battle outcomes, reveal information, create scenario setups, freeze AI, and many more. This stage defines the architecture so each future control is narrow, server-side, testable, auditable, and compatible with the future player/server architecture.

## Stage Placement

This is **Stage 2.5**. The decimal naming is intentional so future intermediate stages such as 2.3 or 2.7 can be added without renumbering the roadmap.

Plan this after Stage 2 command/package contracts are understood. Implement the first skeleton after the Stage 2 `GameSession` command facade exists. Expand it continuously as later gameplay systems are added.

Recommended sequence:

```text
Stage 0   GitRepoV2 / repository migration
Stage 1   Information boundary and fog of war
Stage 2   Server-style turn packages and commands
Stage 2.5 Developer cheat and test control plane
Stage 3   Migration-readiness standards, continuous
Stage 4+  Research, AI, tactical combat, multiplayer, language migration
```

## Core Principle

Cheats are not UI shortcuts.

A cheat is a privileged server/admin/debug command executed by the authoritative session only when cheat/debug mode is enabled. Debug panels, a developer console, automated tests, and scenario preset files are only front ends that submit typed commands.

Target shape:

```text
Debug UI / Developer Console / Scenario Preset Loader
  -> AdminCommandSubmission / DebugScenarioPreset
  -> authoritative GameSession
  -> CheatCommandRegistry
  -> server-side validation
  -> authoritative state mutation or debug package mode change
  -> CheatAuditEvent + updated player package or debug result
```

Forbidden long-term shape:

```text
DebugPanel -> raw_game_state.colony.resources += 10000
```

## User-Approved Decisions

| Topic | Decision |
|---|---|
| Stage number | Use **Stage 2.5**, not Stage 2A. |
| Save handling | Cheat-enabled saves should be flagged, but not aggressively protected. If players work around the flag, that is acceptable. |
| Scenario presets | Human-editable scenario preset files should be supported. |
| Omniscient view | Support both global omniscience and per-empire omniscience. Both must be possible to turn off. |
| Release builds | Cheat/admin command code should remain in release builds, disabled unless explicitly enabled by game/session settings. |
| Console | A developer console may be worth developing later, but it must be a front end to the typed command system, not a mutation bypass. |

## Relationship To Stage 1

Stage 1 owns the distinction between authoritative truth and player-visible information.

Most cheats mutate authoritative state. Visibility cheats are different: they change what information the server packages for a player.

Therefore omniscience, reveal-system, reveal-galaxy, reveal-contact, reset-intel, and similar commands must be implemented through the visibility/intel/package-building path. Do not give the UI hidden raw state and ask it to render more things.

Recommended visibility state:

```text
CheatModeState
  global_omniscient: bool
  omniscient_empires: set[EmpireId]
```

Required behavior:

- Omniscient view must be reversible.
- Global omniscience must be independently toggleable.
- Per-empire omniscience must be independently toggleable.
- Returning to normal visibility must resume normal Stage 1 fog/intel rules.
- Debug package modes must not become the default player package mode.

## Relationship To Stage 2

Stage 2 defines the normal player package and command boundary. Stage 2.5 reuses the same architectural ideas but should keep cheat/admin commands visibly separate from normal player orders.

Recommended distinction:

```text
OrdersSubmission        # normal gameplay orders
AdminCommandSubmission  # privileged cheat/debug/admin commands
```

Alternative acceptable shape:

```text
CommandEnvelope
  command_scope = gameplay | admin_debug
```

Hard rules:

- Normal player commands and cheat/admin commands must be distinct in type, scope, validation, and logging.
- Cheat commands must not become legal player orders by accident.
- Cheat commands must use stable IDs, not live object references.
- Cheat command validation belongs to the authoritative session, not the UI.
- Cheat commands should return structured validation/results just like normal commands.

## Relationship To Stage 3

Stage 3 migration-readiness standards apply fully to this stage. Cheat/admin commands are future server-core boundary candidates and should follow the same rules as normal commands:

- explicit DTOs at layer boundaries,
- stable IDs over object references,
- serialization-first thinking,
- deterministic behavior where practical,
- no UI objects in strategy/simulation state,
- no hidden global mutable state,
- constructor injection or explicit provider seams,
- narrow public APIs.

Do not implement a Python `eval` console or arbitrary scripting bypass as the core cheat mechanism.

## Proposed Concepts

| Concept | Responsibility |
|---|---|
| `AdminCommandSubmission` | Envelope for one or more privileged cheat/debug/admin commands. |
| `CheatCommand` / `DebugCommand` | Narrow server-side operation with typed parameters. |
| `CheatCommandRegistry` | Catalog of known cheat commands, categories, required capabilities, and handler bindings. |
| `CheatValidationContext` | Server-only validation context with authoritative state access and narrow helpers. |
| `CheatModeState` | Per-session cheat/debug enablement, scenario flags, visibility overrides, and permitted capabilities. |
| `DebugScenarioPreset` | Human-editable file describing a named set of flags and commands. |
| `CheatAuditEvent` | Log/event entry recording cheat enablement and command execution. |
| `DeveloperConsole` | Optional later text front end that parses into typed admin commands. |

## Persistent Flags Versus One-Shot Commands

Keep persistent debug flags separate from one-shot cheat commands.

Persistent examples:

```text
instant_build
unlimited_resources
unlimited_fuel
auto_win_battles_for_empire
global_omniscient
empire_omniscient_override
freeze_ai
```

One-shot examples:

```text
add_empire_resource_amount
set_empire_resource_amount
add_colony_population
create_colony_on_planet
complete_colony_build_queue_item
set_fleet_fuel
repair_fleet
teleport_fleet
reveal_system_to_empire
resolve_battle_as_victory
unlock_tech_level
```

## Save Metadata

Cheat-enabled saves should be marked for human awareness but do not need aggressive anti-cheat protection.

Suggested save metadata:

```text
SaveMetadata
  cheat_mode_ever_enabled: bool
  cheat_commands_used_count: int
  last_cheat_command_turn: int | null
  last_cheat_command_type: string | null
  debug_scenario_name: string | null
```

Possible UI wording later:

```text
This save has used debug/cheat tools.
```

## Scenario Presets

Scenario presets should be human-editable and should submit the same typed commands as the debug UI or console.

Start with a strict format before adding macros or scripting. Recommended initial format: JSON.

Example:

```json
{
  "preset_id": "early_colony_stress_test",
  "display_name": "Early Colony Stress Test",
  "description": "Sets up a young empire with extra population, resources, and nearby visible systems.",
  "requires_cheats_enabled": true,
  "commands": [
    {
      "type": "set_empire_resource_amount",
      "empire_id": "empire_001",
      "resource": "minerals",
      "amount": 100000
    },
    {
      "type": "add_colony_population",
      "colony_id": "colony_homeworld",
      "population": 500000000
    },
    {
      "type": "reveal_system_to_empire",
      "empire_id": "empire_001",
      "system_id": "system_alpha"
    }
  ],
  "flags": {
    "instant_build": false,
    "unlimited_fuel": false,
    "auto_win_battles_for_empire": null
  }
}
```

Rules:

- Presets are data, not executable code.
- Presets validate against a schema before execution.
- Presets fail safely with structured validation errors.
- Presets can apply multiple commands in sequence.
- A failed command reports clearly which preset command failed.
- Future versions may add variables/macros, but v1 should stay explicit.

## Developer Console

A developer console may be worth developing, but it should not be the first dependency and should not become an unrestricted Python execution surface.

Target shape:

```text
DeveloperConsole
  parses text command
  converts to typed AdminCommandSubmission
  submits to GameSession
  displays validation result / audit event
```

Example commands:

```text
cheat resources add empire_001 minerals 100000
cheat resources set empire_001 organics 50000
cheat colony pop add colony_homeworld 500000000
cheat vision omniscient empire empire_001 on
cheat vision omniscient global off
cheat fleet fuel set fleet_023 9999
cheat battle auto_win empire_001 on
scenario load early_colony_stress_test
```

## Initial Cheat Categories

| Category | Examples |
|---|---|
| Empire resources | Add/set minerals, organics, radioactives, credits, research points, intel points. |
| Colony | Add/set population, set happiness, add facilities, complete queue items, create colony. |
| Fleet and ship | Set fuel/supply, repair, teleport, add cargo, set movement, spawn fleet. |
| Research | Add RP, unlock tech, set tech level, complete current project. |
| Visibility and intel | Reveal system, reveal galaxy, reveal fleet/contact, reset intel, create ghost contact. |
| Combat | Auto-win, auto-lose, damage ship, kill fleet, force retreat, spawn battle. |
| Production | Instant build, free build, no maintenance, queue acceleration. |
| Scenario setup | Create empire, set diplomacy, seed planets, spawn threats, preset starts. |
| Time and turn | Advance turn, freeze AI, process one empire, rerun battle. |
| AI/debug | Show AI reasoning, force AI plan, disable AI empire, give AI omniscience for testing only. |

## Recommended First Implementation Slice

Do not start with the full cheat catalog. The first implementation slice should prove the control plane with representative command types.

Recommended first commands:

1. `EnableCheatsForSession`
2. `SetEmpireResourceAmount`
3. `AddColonyPopulation`
4. `CompleteColonyBuildQueueItem`
5. `SetFleetFuel`
6. `RevealSystemToEmpire`
7. `CreateColonyOnPlanet`
8. `AutoResolveBattleAsVictory`

This slice exercises cheat enablement, resource mutation, colony mutation, production mutation, fleet mutation, Stage 1 visibility/package interaction, object creation, combat-result override, audit events, and save flagging.

## Validation Rules

Suggested validation layers:

```text
Schema validation
  Is this a known cheat command with valid fields?

Cheat-mode validation
  Are cheats enabled for this session/save?

Capability validation
  Is this cheat category allowed in the current mode?

Identity validation
  Do referenced empire/fleet/colony/planet/system IDs exist?

Authority validation
  Is the request coming from host/admin/debug context?

State validation
  Is the target in a state where this command makes sense?

Rules validation
  Does the command violate a hard invariant that even cheats should preserve?

Result validation
  Did the mutation leave the game in a minimally coherent state?
```

Cheats may bypass normal gameplay costs and limitations. They should not bypass core data integrity rules unless a command is explicitly marked as dangerous/test-only.

## Failure Semantics

Recommended default:

- Reject malformed submissions as a whole.
- Validate each command individually when the envelope is valid.
- For scenario presets, stop on first failure by default unless the preset explicitly declares best-effort execution.
- Return structured validation results for every rejected command.
- Log accepted commands.
- Do not silently ignore failed commands.

## Audit And Logging

Every accepted cheat command should produce a structured audit event.

Suggested event fields:

```text
CheatAuditEvent
  event_id
  turn_number
  command_id
  command_type
  requested_by
  target_empire_id optional
  target_object_ids
  summary
  debug_scenario_name optional
```

The audit log is primarily for debugging and save awareness, not for anti-cheat enforcement.

## Release Build Policy

Cheat/admin command code should remain in release builds.

Default behavior:

- cheats disabled unless explicitly enabled,
- release UI may hide the developer console by default,
- command registry may still exist,
- cheat-enabled saves are flagged,
- no aggressive prevention is required if players modify local files.

## Non-Goals

- Competitive anti-cheat.
- Cryptographic save protection.
- Preventing determined single-player users from editing saves.
- Full scripting language for scenario presets in the first version.
- Developer console as the core implementation mechanism.
- Network admin/authentication implementation; that belongs to Stage 7.
- Final complete list of all cheat commands.

## Design Questions For Future Refinement

1. Should JSON remain the preset format, or should YAML/TOML be allowed later for readability?
2. Should scenario presets live in `data/debug_scenarios/`, `Tools/`, or a user-local folder?
3. Should release builds expose cheat enablement through a UI option, command-line flag, hidden setting, or mod/dev config?
4. Should scenario presets support variables such as active empire, selected fleet, selected colony, or current turn?
5. Should dangerous structural commands require an extra capability flag?
6. Should cheat audit events appear in the normal event log, a debug log, or both?
7. Should automated tests use the same cheat command system for setup, or should test fixtures stay separate?
8. Should `global_omniscient` affect AI packages, human packages, or only selected debug clients?
9. Should AI cheating/debug modes reuse Stage 2.5 controls or have a separate AI difficulty/bonus system?
10. How should cheat commands interact with future PBEM/LAN multiplayer host authority?

## Acceptance Criteria

Stage 2.5 is ready for implementation projects when the following are documented or decided:

- Admin/cheat command envelope shape.
- Cheat command registry design.
- Cheat-mode state and save metadata policy.
- Persistent flag versus one-shot command distinction.
- Scenario preset file format and validation approach.
- Omniscient visibility/package mode rules.
- Validation layers and failure semantics.
- Audit/logging fields.
- Release-build enablement policy.
- First vertical-slice command list.
- Test strategy.

## Suggested Implementation Project Slices

Use the existing `Projects/` system for implementation.

Recommended sequence:

```text
Project 1: Define Stage 2.5 DTO contracts
  - AdminCommandSubmission
  - CheatCommand DTO/protocol
  - CheatValidationResult
  - CheatAuditEvent
  - CheatModeState
  - serialization round-trip tests

Project 2: Add CheatCommandRegistry and GameSession facade
  - register command handlers
  - enable/disable cheats for session
  - submit_admin_commands(...)
  - structured validation results
  - save metadata flagging

Project 3: Implement first representative commands
  - SetEmpireResourceAmount
  - AddColonyPopulation
  - SetFleetFuel
  - CompleteColonyBuildQueueItem

Project 4: Add visibility/debug package controls
  - global omniscience
  - per-empire omniscience
  - reveal system to empire
  - reversible return to normal fog rules

Project 5: Add scenario preset loader
  - JSON schema
  - preset validation
  - command sequence execution
  - clear errors and audit events

Project 6: Add optional developer console front end
  - parse text into typed commands
  - no Python eval
  - use same registry/submission path
```

## Suggested Test Strategy

Recommended tests:

```text
Cheats are disabled by default.
Cheat command is rejected when cheats are disabled.
Enabling cheats marks session/save metadata.
Accepted cheat command produces audit event.
Cheat command uses stable IDs and rejects unknown IDs.
SetEmpireResourceAmount changes authoritative state and package reflection.
AddColonyPopulation preserves colony invariants.
SetFleetFuel preserves fleet/ship invariants.
Global omniscience changes package output and can be turned off.
Per-empire omniscience changes only that empire's package and can be turned off.
Scenario preset validates before execution.
Scenario preset reports the failing command clearly.
Developer console parser, when added, emits the same AdminCommandSubmission as UI/preset paths.
```

## Handoff Guidance For Future Agents

Future agents should:

1. Read Stage 1, Stage 2, Stage 3, and this Stage 2.5 plan before implementation.
2. Do not implement cheats as direct UI mutations.
3. Do not implement a Python eval console as the cheat system.
4. Keep cheat/admin commands distinct from normal player orders.
5. Use stable IDs and serialization-ready DTOs.
6. Keep omniscience inside the server/package-building path.
7. Add commands gradually as gameplay systems mature.
8. Prefer small, composable commands over giant scenario-specific hacks.
9. Update this document when new cheat categories or settled decisions are added.
