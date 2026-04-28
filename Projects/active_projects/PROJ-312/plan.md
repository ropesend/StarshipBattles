# PROJ-312: Add Battle Replay System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-312` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-312 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Determinism Baseline | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ReplaySpec Serialization | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Capture Pipeline | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Sidecar Persistence | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Replay Player | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Replay Browser UI | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Plan Approved — Ready for Implementation
**Last Action:** Plan, design, decisions, manifest, and Phase 1 checklist finalized following Protocol 01 (Phase A baseline + 3 deep-code investigations, Phase A clarifying-question round, Phase B 4-agent swarm, Phase C plan refinement). User approved.
**Next Action:** Begin Phase 1 (Determinism Baseline) using `phase_1_checklist.md`. Use the "Continue Project" prompt to start implementation in a fresh session.
**Blockers:** None
**Test baseline at plan time:** 15672 / 15672 passing (sharded suite).

## Overview
Capture every battle's input spec + RNG seed at entry and outcome at exit, persist
as JSON sidecar files alongside the save, and offer a deterministic read-only
replay player accessible from Event Log entries. The captured battles can be
re-run from seed to reproduce the original simulation exactly.

## Goals
- Every battle (visual or headless, 2- to 8-team, strategy or Combat Lab) is
  captured automatically into a per-save sidecar without measurable runtime cost.
- A captured battle re-runs deterministically: same seed + same `BattleSpec` +
  same registry → same `BattleOutcome`.
- Players can find and replay past battles via Event Log entries; the replay
  uses the existing combat renderer in read-only mode.
- Replay storage is bounded by a configurable per-save ring buffer
  (default 50 replays).

## Scope
**In:**
- Determinism audit + fixes for the battle/AI hot path (block: `ErraticBehavior`).
- AST/lint guard preventing future unseeded `random.*` calls in
  `game/simulation/`, `game/engine/`, `game/ai/`.
- JSON-safe `ReplaySpec` mirror of `BattleSpec` (drops `post_battle_hook`,
  serializes `boundary` / `modifier_stack` / `end_condition`, replaces
  `instance_ref` with a full `ShipInstance` snapshot at battle entry).
- `to_dict` / `from_dict` on every `BattleSpec` and `BattleOutcome` DTO that
  doesn't already have them.
- Capture path that hooks into `run_battle()` and
  `BattleController.start_from_spec()` at the shared `start_engine_from_spec`
  level, writing replay sidecars atomically.
- `replay_settings.json` (in `output/settings/`) carrying `max_replays_per_save`.
- Ring-buffer eviction (write-then-evict, never the reverse).
- `BattleReplayScreen` (subclass or replay-mode flag on `BattleScreen`) using
  pause / play / 0.5x–16x speed already on `BattleScreen`, plus a
  "REPLAY MODE" badge and Exit button. Tick scrubber by re-run-from-zero.
- Replay browser UI integrated with the Event Log: each battle event entry
  gains a Replay button that opens the captured replay.
- Configurable telemetry level per replay (default NORMAL, debug toggle to
  DETAILED). Captured level is pinned in the replay metadata.
- Replay metadata header carrying `sector_name`, `turn_number`, participating
  empires, and timestamp so replays remain meaningful when galaxy state moves
  on.
- Schema versioning on replay JSON (strict-match policy mirroring saves).
- Graceful UI degradation on corrupt / version-mismatched replays
  (silent skip + debug log, mirroring `race_caption_loader.py`).

**Out:**
- Mid-battle crash recovery (only completed battles produce replays).
- Branching playback / "fork from this tick" (read-only only — confirmed).
- Cross-save replay portability (replays live with the save that produced them).
- Strategy-layer event replay (only battles).
- Migration of older save data.

## Current State Snapshot
**Test baseline:** 15672 / 15672 passed (sharded suite, 56s wall time).
**Budget:** ~31 new tests across 6 phases.

## Key Files
| Component | File Path | Phase |
|-----------|-----------|-------|
| ErraticBehavior RNG plumbing | `game/ai/behaviors.py:330-371` | 1 |
| Battle entry shared codepath | `game/simulation/battle_runner.py` (`start_engine_from_spec`, `run_battle`, `extract_outcome`) | 3 |
| Visual entry codepath | `game/simulation/battle_controller.py` (`start_from_spec`) | 3 |
| Battle Spec DTOs | `game/simulation/battle_spec.py` | 2 |
| Battle Outcome DTOs | `game/simulation/battle_outcome.py` | 2 |
| Boundary types | `game/simulation/combat/boundary.py` | 2 |
| Modifier stack | `game/simulation/combat/modifier_stack.py` | 2 |
| End conditions (already serializable) | `game/simulation/systems/battle_end_conditions.py` | 2 |
| Ship instance serializer (already serializable) | `game/strategy/data/ship_instance_serializer.py` | 2 |
| New: ReplaySpec module | `game/simulation/replay/replay_spec.py` | 2 |
| New: Replay outcome module | `game/simulation/replay/replay_outcome.py` | 2 |
| New: Replay capture | `game/simulation/replay/replay_capture.py` | 3 |
| New: Replay store | `game/strategy/services/replay_store.py` | 4 |
| Replay settings | `output/settings/replay_settings.json` (lazy-init) | 4 |
| Save service hook points | `game/strategy/systems/save_game_service.py` (`save_game`, `load_game`, `delete_save`) | 4 |
| Replay screen | `game/ui/screens/battle_screen.py` (replay-mode flag) | 5 |
| New: Replay browser | `game/ui/screens/event_log_window.py` (Replay button on entries) | 6 |
| Triage source | [findings/fleet_battle_replay.md](findings/fleet_battle_replay.md) | — |

## Phases at a Glance
- **Phase 1 — Determinism Baseline.** Thread RNG through `ErraticBehavior`, add AST guard test, extend the existing seeded-determinism harness with a state-hash regression. Establishes the contract Phase 2+ depends on.
- **Phase 2 — ReplaySpec Serialization.** Add `to_dict` / `from_dict` on every `BattleSpec` / `BattleOutcome` DTO + Boundary + ModifierStack. New `ReplaySpec` data model in `game/simulation/replay/`. Round-trip tests.
- **Phase 3 — Capture Pipeline.** Hook `start_engine_from_spec` to snapshot the spec at entry; hook `run_battle` / `BattleController.start_from_spec` to snapshot the outcome at exit. Telemetry-level pinning. Context-metadata header.
- **Phase 4 — Sidecar Persistence.** `ReplayStore` service writes / lists / loads / evicts replays in `output/saves/<save>/replays/`. `replay_settings.json` ring-buffer cap. Save-lifecycle hooks (create / load / delete).
- **Phase 5 — Replay Player.** Replay-mode flag on `BattleScreen`. Pause / speed / "REPLAY MODE" badge / Exit button. Tick scrubber via re-run-from-zero. Read-only camera + assertions.
- **Phase 6 — Replay Browser UI.** Replay button on each battle event in the Event Log. Click → resolve replay → load → render via Phase 5 player. Graceful skip on corrupt / version-mismatched files.

## Related Documents
- [design.md](design.md) — Architecture analysis, swarm findings, design rationale
- [decisions.md](decisions.md) — Decisions log with user-confirmed answers
- [findings/fleet_battle_replay.md](findings/fleet_battle_replay.md) — Original triage doc

## Verification
- [ ] All phase checklists complete
- [ ] Determinism harness extended; AST guard active and passing
- [ ] Round-trip test for every Replay DTO passes
- [ ] Sharded test suite green (target: 15672 + ~31 new tests)
- [ ] Manual smoke: trigger a battle in strategy → end turn → click Replay on the Event Log entry → battle plays back identical to original
- [ ] Multi-team smoke (3+ teams): replay still produces identical outcome
- [ ] Save delete removes replays/ subfolder
- [ ] Ring buffer cap honored (default 50)
- [ ] User verified
