# Turn Processing Performance

## Context

Raised by user during QA session `20260510_165332` at 16:59:18:

> "If we could do something to increase processing time for each turn that would be very helpful — we should be looking at that."

This is a broad performance concern about the strategy-layer turn-processing step (the "Processing Turn" overlay shown between turns). The user did not point at a specific subsystem; the request is to investigate and reduce end-to-end turn time.

## Screenshots

_None — no screenshot was captured for this observation._

## Code Investigation Findings

Not investigated in detail during triage — the observation is open-ended ("turn processing is slow") and needs a profiling pass before scoping. Likely contributors based on the strategy-layer architecture:

- Combat resolution for AI-vs-AI auto-resolved combats (see related but distinct issue #8).
- Build queue resolution for every empire each turn (see #17 — virtual table caching; the resolution path itself isn't directly related but is touched on every turn).
- Fleet movement and warp-point traversal.
- Planet/system event processing (population, production, research).
- Per-turn save serialization.

A profiling history file exists in QA sessions (`logs/profiling_history.json`) and could be the starting data set, but interpretation needs to be confirmed against current code.

## Scope Notes

Why this warrants a full project rather than a single bug or feature issue:

1. **Cross-cutting.** Strategy-turn processing spans multiple layers — combat sim, build resolution, fleet AI, economy, save I/O. A single GitHub issue cannot reasonably hold acceptance criteria across all of them.
2. **Profiling-first.** Until the slowest subsystem is identified, "reduce turn processing time" is unfalsifiable. Phase 1 should be measurement; phases 2+ should be subsystem-specific optimization work each with their own acceptance criteria.
3. **Game-size dependent.** Turn time scales with empire count, fleet count, planet count. Acceptance criteria need to be defined in terms of a representative reference scenario (e.g. "8 empires, mid-game, turn N").
4. **Risk of regressions.** Optimizations in this area touch hot paths that combat-related tests already cover; needs a structured plan with checkpoints rather than ad-hoc fixes.

Convert with `/claude-triage-to-proj turn_processing_performance` when ready to plan phases.
