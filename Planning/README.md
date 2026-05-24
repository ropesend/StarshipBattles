# Starship Battles Staged Planning

This folder is for long-range planning documents only. It is not an implementation project tracker and should not replace the existing `Projects/` system.

Use these documents to preserve the evolving roadmap, cross-stage dependencies, architectural decisions, and acceptance criteria for major game systems. When a stage is ready for implementation, create focused work through the existing project system and link back to the relevant planning folder.

## Current Stage Order

| Stage | Folder | Theme | Recommended Status |
|---|---|---|---|
| 1 | `01_information_boundary_and_fog_of_war/` | Player-visible state, sensors, intel memory, fog of war | Do first |
| 2 | `02_server_style_turn_packages_and_commands/` | Server-authoritative player packages and command batches | Do early, alongside Stage 1 |
| 3 | `03_migration_readiness_standards/` | Coding standards that make later Rust/C++ migration easier | Start immediately |
| 4 | `04_research_integration/` | Fully integrated research, leveled tech, component generation | After visibility foundation starts |
| 5 | `05_computer_player_ai/` | Strategic and operational AI for computer empires | After fog/research command model is stable |
| 6 | `06_tactical_combat_persistence_and_formations/` | Better tactical formations, AI, and same-turn sector battle persistence | After command/intel model is designed |
| 7 | `07_network_multiplayer_architecture/` | Real networking, remote clients, synchronization, PBEM/online flows | Defer until local server-style model exists |
| 8 | `08_language_migration_plan/` | Later migration of performance-critical systems to Rust or C++ | Defer until interfaces stabilize |

## High-Level Principle

The authoritative game state and the player-visible game state must become separate things. The server/session should own the full truth. Each human or AI player should receive only the information their empire is entitled to know.

This single principle supports fog of war, fair AI, multiplayer security, replay/debugging, and eventual migration to a faster simulation core.

## How These Documents Should Evolve

Each stage folder should contain planning notes, decisions, open questions, risks, and objective acceptance criteria. Keep implementation tasks out of these files except as links or references to project tickets.

Recommended workflow:

1. Update the relevant stage planning document when design decisions change.
2. Create one or more focused implementation projects in `Projects/` when work is ready.
3. Link implementation projects back to the planning stage.
4. Update this overview when a stage changes priority, is partially complete, or is superseded.

## Current Recommended Sequence

1. Build the player information boundary and fog-of-war foundation.
2. Introduce local server-style player turn packages and command batches.
3. Enforce migration-readiness standards continuously.
4. Integrate research into the empire economy, turn engine, and component/design systems.
5. Build computer-player AI on top of the same information and command surface used by human players.
6. Improve tactical combat formations and persist same-turn tactical sector state.
7. Add real network multiplayer once the local server-authoritative model is proven.
8. Migrate performance-critical systems to Rust or C++ only after the relevant boundaries are stable.

## Non-Goals For This Folder

- Do not store source-code changes here.
- Do not use this as a replacement for `Projects/`.
- Do not use these documents as a detailed task checklist once implementation begins.
- Do not let planning documents drift into stale claims about completed code; update or mark uncertain claims explicitly.
