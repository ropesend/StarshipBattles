# FEAT-22: Startup phase profiling — log timings before main menu appears

## Description
The game now takes noticeably long to launch. The user wants to see timing
information for each phase that runs **before** the main menu appears, so the
slow phase(s) can be identified.

The profiling framework already exists at
[game/core/profiling.py](../../../game/core/profiling.py) (`Profiler` class,
`profile_block()` context manager, `profile_action()` decorator) and is wired
into `ApplicationContext`, but the bootstrap phases in
[game/app_bootstrap.py](../../../game/app_bootstrap.py) are not currently
instrumented.

## Required changes
1. Wrap the major bootstrap phases in `app_bootstrap.py:bootstrap()` with
   `profile_block()` (or per-helper `@profile_action()`):
   - `pygame.init()` + display setup
   - font initialization
   - registry loading (components / modifiers / resources / ships)
   - `GameRegistries` build
   - `ensure_component_derivatives()` (component derivative image generation)
   - `sprite_mgr.load_sprites()`
   - input mapper init
2. Print one console line per phase as it completes (so the user sees live
   progress on slow launches): e.g. `[startup] sprites loaded in 1.84s`.
3. Print a final `[startup] total bootstrap: X.XXs` line just before
   `Game.__init__()` returns control to `run()`.
4. Persist the timings via the existing `Profiler.save_history()` path so
   they are queryable from `Paths.PROFILING_HISTORY` after the fact.

## Out of scope
- Optimising any slow phase identified by the timings — that becomes a
  follow-up ticket once we know which phase to target.
- Reordering or parallelising bootstrap phases.
- A UI-level loading screen with live timing display.

## Acceptance
- Launching the game prints a phase-by-phase timing summary to the console
  before the main menu appears.
- The total bootstrap time is reported at the end of the summary.
- Timings are recorded to `Paths.PROFILING_HISTORY` and visible in any
  existing profiler-history tooling.

## Priority
Low (developer ergonomics, not a player-facing bug)

## Status
Pending

## Work Log
- 2026-04-28: Created from QA Session 20260428_052952.
