# Starship Battles Staged Planning

This folder is for long-range planning documents only. It is not an implementation project tracker and should not replace the existing `Projects/` system.

Use these documents to preserve the evolving roadmap, cross-stage dependencies, architectural decisions, and acceptance criteria for major game systems. When a stage is ready for implementation, create focused work through the existing project system and link back to the relevant planning folder.

## Current Stage Order

| Stage | Folder | Theme | Recommended Status |
|---|---|---|---|
| 0 | `gitrepoV2/` | Clean canonical V2 repository, artifact policy, LFS rules, multi-machine workflow | Do before major Stage 1 implementation |
| 1 | `01_information_boundary_and_fog_of_war/` | Player-visible state, sensors, intel memory, fog of war | First major game architecture stage |
| 2 | `02_server_style_turn_packages_and_commands/` | Server-authoritative player packages and command batches | Do early, alongside Stage 1 |
| 2.5 | `02_5_developer_cheat_test_control_plane/` | Server-authoritative cheat/debug/test scenario command surface | Plan after Stage 2 contracts; implement skeleton after the Stage 2 `GameSession` command facade exists; expand continuously |
| 3 | `03_migration_readiness_standards/` | Coding standards that make later Rust/C++ migration easier | Start immediately and continue through all stages |
| 4 | `04_research_integration/` | Fully integrated research, leveled tech, component generation | After visibility foundation starts |
| 5 | `05_computer_player_ai/` | Strategic and operational AI for computer empires | After fog/research command model is stable |
| 6 | `06_tactical_combat_persistence_and_formations/` | Better tactical formations, AI, and same-turn sector battle persistence | After command/intel model is designed |
| 7 | `07_network_multiplayer_architecture/` | Real networking, remote clients, synchronization, PBEM/online flows | Defer until local server-style model exists |
| 8 | `08_language_migration_plan/` | Later migration of performance-critical systems to Rust or C++ | Defer until interfaces stabilize |

## High-Level Principle

The authoritative game state and the player-visible game state must become separate things. The server/session should own the full truth. Each human or AI player should receive only the information their empire is entitled to know.

This single principle supports fog of war, fair AI, multiplayer security, replay/debugging, and eventual migration to a faster simulation core.

## Stage 0 Principle

Before major architecture implementation begins, create and validate a clean V2 repository so future work happens in the canonical repo rather than in the historical `StarshipBattles` repository.

Stage 0 is repository hygiene and workflow migration, not a game rewrite. The detailed Stage 0 plan lives in `gitrepoV2/STAGE_0_PLAN.md`, and settled user decisions live in `gitrepoV2/STAGE_0_DECISIONS.md`.

## Stage 2.5 Principle

Stage 2.5 adds a server-authoritative developer cheat and test control plane. It is not a client-side debug shortcut layer.

Cheat/debug/scenario controls should be privileged admin commands submitted to the authoritative session, validated server-side, logged, and kept distinct from normal player orders. Developer UI, a future console, automated tests, and human-editable scenario preset files should all call the same typed command surface.

Stage 2.5 depends on Stage 2's command/package boundary and Stage 3's DTO/stable-ID/serialization discipline. Visibility cheats such as omniscient view also depend on Stage 1's information-boundary model and should alter server-built player packages rather than giving hidden raw state to the UI.

## How These Documents Should Evolve

Each stage folder should contain planning notes, decisions, open questions, risks, and objective acceptance criteria. Keep implementation tasks out of these files except as links or references to project tickets.

Each stage folder also has a **`CURRENT_STATE.md`** scaffold. These are intentionally empty templates: future agents should fill them in by surveying the actual codebase, so each stage's plan can be grounded in reality (what exists, what overlaps, what's missing, what blocks the planned design) rather than being purely aspirational. Update the "As of" date when refreshing. Stages 0 and 2.5 also have settled-vs-proposed **`*_DECISIONS.md`** files — that pattern should propagate to other stages as decisions firm up.

Recommended workflow:

1. Update the relevant stage planning document when design decisions change.
2. Create one or more focused implementation projects in `Projects/` when work is ready.
3. Link implementation projects back to the planning stage.
4. Update this overview when a stage changes priority, is partially complete, or is superseded.

## Current Recommended Sequence

0. Create and validate the clean V2 repository so future work happens in the canonical repo.
1. Build the player information boundary and fog-of-war foundation.
2. Introduce local server-style player turn packages and command batches.
2.5. Add the server-authoritative developer cheat/test control plane after the command facade skeleton exists.
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
