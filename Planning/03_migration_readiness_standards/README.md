# Stage 3: Migration-Readiness Standards

## Purpose

Adopt coding and architecture standards now that make a later migration to Rust or C++ easier, without slowing current Python iteration too much.

This stage is continuous. It should begin immediately and remain active while the game is still being designed.

## Core Principle

Do not rewrite the game before the feature boundaries stabilize. Instead, make the Python code increasingly portable by reducing hidden state, dynamic coupling, UI/game entanglement, and unstructured data flow.

## Recommended Direction

Rust is the preferred future target for server/simulation core work unless there is a strong need for C++ engine-library integration. C++ remains a viable fallback, especially for graphics/engine integration, but Rust is likely better for safe concurrency, serialization, and server-authoritative simulation.

The language choice should remain deferred until the core interfaces are stable.

## Standards To Start Enforcing

| Standard | Reason |
|---|---|
| Explicit DTOs at layer boundaries | Maps cleanly to structs and serialization. |
| Stable IDs over object references in saved/networked state | Required for multiplayer, save/load, and migration. |
| Pure services for algorithms | Easier to test and port one module at a time. |
| No UI objects in strategy/simulation state | Prevents migration blockers. |
| No hidden global mutable game state | Required for server authority and parallelism. |
| Deterministic turn processing where practical | Needed for tests, replays, debugging, and server verification. |
| Constructor injection or explicit provider seams | Avoids hard-to-port implicit dependencies. |
| Narrow public APIs | Makes future replacement modules possible. |
| Strict layer dependency direction | Prevents circular rewrite traps. |
| Serialization-first thinking | Forces clear boundaries and schema discipline. |

## Stage 2.5 Cheat/Admin Command Standards

Stage 2.5 developer cheat, debug, and scenario controls are not exempt from migration-readiness standards.

Cheat/admin commands should be treated as future server-core boundary candidates. They should be as explicit and portable as normal gameplay commands, even though they are privileged and may bypass normal game costs or limits.

Rules for Stage 2.5 work:

- Use explicit DTOs for `AdminCommandSubmission`, cheat command payloads, validation results, audit events, and scenario presets.
- Use stable IDs for empires, fleets, colonies, planets, systems, ships, battles, contacts, and technologies.
- Do not pass live Python object references through cheat command payloads.
- Do not implement cheat controls as UI-side mutations of authoritative state.
- Do not implement the developer console as arbitrary Python `eval` or an unrestricted script execution surface.
- Console commands, debug buttons, scenario presets, automated tests, and future tools should all submit the same typed admin command DTOs.
- Keep scenario presets data-driven and schema-validated before execution.
- Keep cheat-mode state and save metadata explicit rather than hidden in globals.
- Keep omniscient/debug visibility inside the authoritative package-building path, not the UI rendering path.
- Add serialization round-trip tests for important cheat/admin DTOs before relying on them as long-term boundaries.

Recommended boundary mindset:

```text
Human-editable preset / console text / debug UI
  -> typed AdminCommandSubmission DTO
  -> server-side validation and handler
  -> authoritative state mutation or debug package mode
  -> structured result and CheatAuditEvent
```

## Python-Specific Guidance

- Prefer dataclasses or small explicit classes for DTOs.
- Use type hints aggressively for boundary objects.
- Avoid passing arbitrary dictionaries across major boundaries unless they are schema-defined serialization payloads.
- Avoid dynamic monkey-patching or runtime mutation of class shapes.
- Keep algorithms separate from Pygame/UI event loops.
- Do not let convenience imports become architecture leaks.
- Keep randomness injectable or server-owned.
- Keep long-running turn logic free of UI dependencies.

## Future Migration Shape

A likely migration path is not a single full rewrite. A better path is incremental replacement:

1. Stabilize DTOs and command schemas in Python.
2. Move pure algorithms behind protocol/facade seams.
3. Port isolated hot paths first.
4. Keep Python UI/tools while replacing simulation/turn subsystems.
5. Use a serialization boundary between Python and Rust/C++ modules.
6. Eventually move the authoritative server core if justified.

Stage 2.5 admin/cheat DTOs should remain compatible with this path. If the authoritative server core later moves to Rust or C++, the cheat/test control plane should still work by sending typed command DTOs across the same boundary rather than relying on Python-only object mutation.

## Initial Non-Goals

- Immediate Rust/C++ implementation.
- Rewriting UI.
- Rewriting every data model.
- Premature FFI work.
- Optimizing without profiling.
- Implementing Stage 2.5 cheat commands as a migration-readiness shortcut.

## Design Questions

1. Should Rust be the default future target unless contradicted by profiling or tooling needs?
2. Which systems are most likely to need migration: tactical combat, turn processing, pathfinding, AI search, or visibility?
3. What serialization format should be considered long term: JSON, MessagePack, protobuf, Cap'n Proto, or custom?
4. Should deterministic simulation become a hard requirement for all server-side systems?
5. How strict should Python type checking become before migration?
6. Should code style start avoiding Python-only idioms in portable modules?
7. Should Stage 2.5 scenario preset schemas use JSON Schema, custom validation dataclasses, or a later shared schema system?

## Acceptance Criteria

This stage is active when:

- New planning and implementation projects identify their boundary DTOs.
- New systems avoid UI/game-state coupling.
- New commands and player-facing data use stable IDs.
- Services are testable without full application boot.
- Migration concerns are captured without forcing premature rewrite work.
- Stage 2.5 cheat/admin commands follow the same DTO, stable-ID, serialization, and no-UI-mutation standards as normal gameplay commands.

## Implementation Project Guidance

Use the existing `Projects/` system for enforcement projects. Suggested slices:

1. Add architecture lint/checks for forbidden imports.
2. Identify raw-dict cross-boundary APIs and replace them with DTOs.
3. Convert save/network candidates to stable ID references.
4. Add deterministic RNG seams where needed.
5. Add serialization round-trip tests for player package and command DTOs.
6. Add serialization/schema tests for Stage 2.5 admin command DTOs and scenario preset files once they exist.
