# PROJ-311 Phase 3 — Wave Order

**Decided:** 2026-04-27
**Source:** [`baseline_summary.md`](baseline_summary.md)
**Goal:** Split the 1408-function backfill across waves that can each be done by a single parallel agent without merge conflicts and without overwhelming review.

## Wave-sizing principles

- A wave should be ~100–250 functions. Bigger than that, review breaks down.
- Waves are scoped to a directory subtree so agents working in parallel don't collide.
- `game/ui/screens/` (966 unannotated) is too big for one wave — split it.
- The 'other' bucket (mostly `game/<top-level>` files at 42 unann) is small enough to fold into Wave A as foundation work.

## Recommended wave order

| Wave | Scope | Unannotated | Notes |
|------|-------|------------:|-------|
| **A** | `game/core/` + `game/ai/` + `game/<top-level>` + `game/assets/` + `game/engine/` (the 'other' subdirs) | **88** | Foundational. Small. Quick win + builds reviewer confidence. |
| **B** | `game/simulation/` | **109** | Self-contained. Engine code; correct annotations matter most here. |
| **C** | `game/strategy/` | **57** | Already 95% covered — tiny clean-up wave. |
| **D1** | `game/ui/panels/` + `game/ui/widgets/` + `game/ui/research/` + `game/ui/assets/` + `game/ui/renderer/` + `game/ui/services/` + `game/ui/utils/` (everything in `game/ui/` EXCEPT `screens/`) | **188** | All non-screen UI surface. Mostly callbacks → `-> None`. |
| **D2** | `game/ui/screens/` — first half (alphabetical, files A–M) | **~480** | Split alphabetically to give two D-wave agents non-overlapping file sets. |
| **D3** | `game/ui/screens/` — second half (alphabetical, files N–Z) | **~480** | Same. |

**Total:** 88 + 109 + 57 + 188 + ~480 + ~480 ≈ 1402 (matches the 1408 audit total within rounding from the alphabetical split).

## Why this split

- **A and C are small** so the parallel-execution overhead is justified — short feedback loops, hard to get wrong.
- **B (simulation)** is medium-sized and risk-sensitive (combat math): give it to a careful agent and give it room.
- **D1 (UI non-screens)** is one bucket because no individual subdir except `panels/` exceeds 134 functions; combining them keeps the parallel slot count low.
- **D2/D3 (UI screens)** is the brute-force half. Alphabetical split is the simplest non-overlapping cut. Concrete file split should be made by the agent picking up D2 (e.g., produce two CSV slices from `unannotated.csv` filtered to `game/ui/screens/` and bisect by file count).

## Dependencies and ordering

- Waves can run in **any order** — annotations are local to each function. There is no cross-wave dependency.
- **A is recommended first** purely because foundation files (`game/core/`, `game/context.py`, `game/app.py`) are imported everywhere and a regression there is loudest. Doing them first surfaces problems before propagating.
- **D2 and D3 should run in parallel**, not sequentially.
- Coordinate with **PROJ-309 (file decomposition)** — its current sub-phase touches some of these files. The plan.md Current State of PROJ-309 should be checked before each wave starts; touch the conflicting files LAST in this project's wave for that subsystem.

## Per-wave verification

After each wave:
1. Run `python Projects/active_projects/PROJ-311/findings/annotation_audit.py` — confirm the unannotated count for that subsystem dropped to ~0
2. Run the relevant slice of the test suite (`pytest tests/unit/<subsystem>/ -n 12`)
3. Update `findings/baseline_summary.md` with the new coverage figures
4. Commit with message: `feat(PROJ-311): Phase 3 Wave <X> — annotate <subsystem>`

## Out of scope for these waves

- Test files (`tests/`)
- Parameter annotations (return-type only)
- Migrating `Optional[X]` → `X | None` in already-annotated functions (separate clean-up if desired)
- Type-checker correctness (`mypy --strict`) — that's a different project entirely
