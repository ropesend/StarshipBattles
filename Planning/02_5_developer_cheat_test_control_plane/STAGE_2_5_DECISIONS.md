# Stage 2.5 Decisions — Developer Cheat And Test Control Plane

This file records settled user decisions for Stage 2.5. Future agents should treat these as approved unless the user explicitly changes them.

## Stage Identity

| Topic | Decision |
|---|---|
| Stage number | Stage **2.5**. |
| Reason for decimal stage number | Decimal numbering makes it easy to add future intermediate stages such as 2.3 or 2.7 without renumbering the roadmap. |
| Folder | `Planning/02_5_developer_cheat_test_control_plane/` |
| Short name | Developer cheat and test control plane. |

## Core Architecture Decision

Cheats are not client-side shortcuts.

Cheat/debug/scenario controls must be implemented as privileged commands submitted to the authoritative session. The server/session validates the command, mutates authoritative state if allowed, logs the action, marks save metadata when appropriate, and returns an updated package or structured result.

Debug UI, a future developer console, human-editable scenario presets, and automated tests should all use the same typed admin command surface.

Forbidden long-term pattern:

```text
UI/debug panel directly mutates authoritative objects.
```

Approved target pattern:

```text
UI / console / preset loader
  -> typed AdminCommandSubmission
  -> authoritative GameSession
  -> CheatCommandRegistry and handler
  -> structured result and CheatAuditEvent
```

## Settled User Decisions

| Topic | Decision |
|---|---|
| Save flagging | Cheat-enabled saves should be flagged, but this is informational rather than aggressively protected. If players figure out a workaround, that is acceptable. |
| Scenario presets | Human-editable scenario preset files should be supported. |
| Omniscient view | Support both global omniscience and per-empire omniscience. Both must be reversible/toggleable. |
| Release builds | Cheat/admin command code should remain in release builds. It should be disabled unless explicitly enabled by game/session settings. |
| Developer console | A console may be worth developing, but it should be a front end to the typed command system rather than a separate mutation bypass. |

## Save Metadata Policy

Use soft save metadata rather than aggressive anti-cheat protection.

Suggested fields:

```text
SaveMetadata
  cheat_mode_ever_enabled: bool
  cheat_commands_used_count: int
  last_cheat_command_turn: int | null
  last_cheat_command_type: string | null
  debug_scenario_name: string | null
```

Suggested UI wording:

```text
This save has used debug/cheat tools.
```

No cryptographic save enforcement is required for the first version.

## Scenario Preset Policy

Initial scenario preset files should be human-editable data files, not executable scripts.

Recommended initial format: JSON.

Rules:

- Presets validate before execution.
- Presets submit the same typed admin commands as debug UI and console front ends.
- Presets fail with structured validation errors.
- V1 should be explicit and boring before adding variables, macros, or scripting.

## Omniscience Policy

Omniscience is a package-building / visibility-mode concern, not a UI rendering hack.

Required behavior:

- Support global omniscience.
- Support per-empire omniscience.
- Support turning global omniscience off.
- Support turning per-empire omniscience off.
- Turning omniscience off resumes normal Stage 1 fog/intel behavior.
- Normal player packages must not accidentally become omniscient.

Suggested state:

```text
CheatModeState
  global_omniscient: bool
  omniscient_empires: set[EmpireId]
```

## Release Build Policy

Cheat/admin command code remains in release builds to avoid development-tool code rot and to keep a single command/control architecture.

Default release behavior:

- Cheats are disabled unless explicitly enabled.
- The developer console may be hidden by default.
- Cheat-enabled saves are flagged.
- No strong effort is required to prevent determined single-player users from editing files or finding workarounds.

## Developer Console Policy

A console should be a front end only.

Approved target shape:

```text
DeveloperConsole
  parses text command
  converts to typed AdminCommandSubmission
  submits to GameSession
  displays validation result / audit event
```

Do not implement the cheat system as arbitrary Python `eval`, unrestricted scripting, or direct object mutation.

## Handoff Notes

Future agents refining or implementing Stage 2.5 should read:

1. `Planning/01_information_boundary_and_fog_of_war/README.md`
2. `Planning/02_server_style_turn_packages_and_commands/README.md`
3. `Planning/02_5_developer_cheat_test_control_plane/README.md`
4. `Planning/03_migration_readiness_standards/README.md`

Then create focused implementation projects under the existing `Projects/` system rather than turning the planning folder into a task tracker.
