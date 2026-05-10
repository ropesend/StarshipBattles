# Fleet Battle Replay System

## Context
Captured during QA Session 20260427_151244 at 16:05.

The user wants a battle replay capability: capture every battle's initial
conditions (ship rosters, positions, fleet compositions, modifiers, RNG seed)
and final conditions (winner, survivors, telemetry), persist them, and offer
a Replay button on the strategy screen that opens the combat view and
replays the saved battle deterministically.

User's exact ask (cleaned):
> "We need a fleet battle replay option. Basically what I need to be able to
> do is capture and save all of the initial conditions and the random number;
> we should also be capturing all the final conditions. I should be able to
> click on a Replay button and have the combat view / combat-by-option show
> up, and basically it should show the combat that happens at a sector."

## Code Investigation Findings
Replays require **deterministic re-execution** of the battle simulator from
saved initial state. Relevant areas:

- **RNG plumbing** — PROJ-301-304 already plumbs a seeded RNG through
  intrinsic ability rolls (commit `8f5c2a863 fix(PROJ-301/302/303/304):
  plumb seeded RNG through intrinsic ability rolls`). Battle-time RNG (hit
  rolls, damage variance, AI tie-breakers, target selection, projectile
  spread) likely flows through the same seeded provider but requires audit
  to confirm there are no fallback `random.*` calls anywhere on the battle
  hot path.
- **Battle entry/exit** — PROJ-269/270 unified the battle simulator entry
  point (`run_battle` / `BattleController.start_from_spec`) and the exit
  callback (`_on_battle_ended`). This is the natural place to:
  - Snapshot the input `BattleSpec` + RNG seed at entry.
  - Snapshot the result `BattleResult` at exit.
- **N-team support** — PROJ-275 finalised 2–8 team battles; replay must
  support all team counts already produced by `build_strategy_battle_spec`.
- **Persistence** — Replays would live alongside saves (or in a separate
  store) and survive save round-trips.

## Scope Notes — Why a Project, not a Feature
1. **Determinism audit** — every RNG consumer in the battle layer must use
   the seeded provider. Any `random.*` import or unseeded call breaks
   replays. This is multi-file work and requires a regression guard.
2. **Persistence format design** — JSON vs binary, schema versioning,
   retention policy (per-save? unbounded? capped count?), location (in-save
   vs sidecar). Each is a design decision.
3. **Capture path** — hook into the unified entry point at PROJ-269/270 to
   snapshot input + seed + final state without slowing the live path.
4. **Replay player UX** — open the existing combat renderer in a "replay
   mode" with timeline scrubbing, playback speed, and a clearly marked
   "this is a replay" indicator. May need a new screen or a mode flag on
   the battle renderer.
5. **Replay browser UI** — list past battles by sector / turn / participants,
   filter, delete. Likely a new window in the strategy screen.
6. **Save migration** — old saves have no replays; new saves accumulate
   them.

A focused implementation plan (Phases 1–5) and architecture review need to
be written before code lands.

## Suggested Phasing (initial guess for project plan)
- **Phase 1:** Determinism audit — verify every battle-layer RNG consumer
  uses the seeded provider; ban direct `random.*` imports via lint or AST
  guard.
- **Phase 2:** Capture path — snapshot `BattleSpec` + seed at entry,
  `BattleResult` at exit, write to disk in a versioned schema.
- **Phase 3:** Replay loader + player — read snapshot, re-run with same
  seed, render via existing combat view in "replay mode".
- **Phase 4:** UI — Replay button entry point (event log? sector context?
  battle outcome panel?), replay browser window.
- **Phase 5:** Polish — playback controls (speed, scrub), retention policy,
  documentation.
