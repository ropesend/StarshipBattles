# Strategy-Layer Panel Load Performance

## Context

Raised by user during QA session `20260510_165332` at 17:00:10:

> "Takes a really long time to load the planets [registry] — we should try to put some optimizations into that."

On follow-up, the user expanded the scope: they want load-time optimizations for **five** strategy-layer panels that all "take remarkably long to load":

1. **Galactic Planet Registry** (planets list)
2. **Galactic Star Registry** (stars list)
3. **Empire Overview** window
4. **Build Queue** UI (referred to as "All Queues" — covers every yard's build queue panel)
5. **Combat / Event Log** window

User direction: bundle as a single project if root causes overlap; split into sub-phases if they diverge after profiling.

## Screenshots

_None — observation was verbal during gameplay._

## Code Investigation Findings

Quick spot checks on the Build Queue path (from QA session log `battle.log`):

- Every `open_for_yard` triggers `DesignLibrary.scan_designs` which loads **47 JSON files** and rebuilds the per-category filter.
- The scan + filter step takes ~1.2 s wall-clock on the user's machine for 47 designs (16:54:00,644 → 16:54:01,825). Repeats on every category change.
- Same scan also fires when the Build Queue is opened for a different empire (player turn-change), even though the designs folder is per-empire and could be cached.

The other four panels were not investigated during triage — they should be profiled in Phase 1.

Likely shared root causes (hypotheses, **not** verified):

- Eager full-load on open instead of lazy / virtualised row rendering.
- Synchronous file I/O on the UI thread (designs, save data, log entries).
- No memoisation across re-opens within a single session.
- Builders that re-construct pygame-gui widgets from scratch every open (related to PROJ-410 virtual table work, which fixed this for one path but not the others).

## Scope Notes

Why this warrants a project rather than five separate bug issues:

1. **Shared symptom + likely shared techniques.** Virtualisation, lazy loading, memoisation, and threaded I/O are repeating tools. Treating each panel as its own bug would result in duplicated review effort and risk inconsistent solutions.
2. **Need to profile first.** "Takes a long time" needs measurement before any of the five can have actionable acceptance criteria. A project structure gives a Phase 1 (profile all five, identify shared vs panel-specific costs) before Phase 2+ (per-panel optimisations).
3. **PROJ-410 precedent.** The Build Queue panel already has virtual-table caching — the same architecture may apply to Planet Registry, Star Registry, Empire Overview, and Log windows. A coordinated project can reuse PROJ-410's hooks (A/B/C invalidation pattern) where appropriate.
4. **Coordination.** If Phase 1 finds that all five share a single I/O bottleneck, the fix is one PR; if they diverge, the project splits into focused phases without re-planning.

### Proposed Phase Sketch (placeholder for `/claude-triage-to-proj`)

- **Phase 1 — Measure.** Profile open-time and refresh-time for each of the five panels at a representative game size. Identify per-panel critical paths.
- **Phase 2 — Shared infrastructure.** Apply / extend virtual-table caching, lazy loading, and async I/O wherever the profile shows it pays off.
- **Phase 3+ — Panel-specific work** for any panel whose bottleneck is not addressed by Phase 2.

### Related but Separate Entries

- `Projects/Triage/turn_processing_performance.md` — compute-bound *turn-processing* time. Different perf concern; the user explicitly kept them separate during triage.
- Issue #10 (startup blocks ~11s in `ensure_component_derivatives`) — startup-time only, also separate.
- Issue #17 (build queue stale rows) — same panel as item 4 above, but a correctness regression, not a perf concern. Fix may touch the same files.

Convert with `/claude-triage-to-proj strategy_panel_load_performance` when ready to plan phases.
