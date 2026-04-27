# PROJ-311: Design Document

## Initial Analysis

The 2026-04-26 code review claimed 59.5% return-type coverage / 2145 unannotated functions. **Independent verification (2026-04-26):** actual coverage is **71.4%** (3522 annotated of 4930 total, dunders excluded), so **1408 functions** lack return annotations. The codebase is in better shape than the review suggested, but 1408 is still a lot of work.

Python 3.13+ is the baseline (PROJ-295). Modern syntax available:
- `int | None` instead of `Optional[int]`
- `list[int]` instead of `List[int]`
- `dict[str, int]` instead of `Dict[str, int]`
- `Callable[[int], str]` is fine; PEP 695 generics if helpful

## Methodology

### Phase 2: baseline measurement
Build an AST script that:
- Walks `game/**/*.py`
- For each function/method, records: file, function name, has-return-annotation, is-dunder, is-public (no leading underscore)
- Outputs CSV
- Reports: total, annotated, unannotated, coverage %, by-subsystem breakdown

### Phase 3: backfill in waves, by subsystem
Don't backfill all 1408 functions in one pass — that's a 5000-line PR with merge-conflict risk. Wave by subsystem:

1. **Wave A — Core** (`game/core/`): foundation; small surface; quick win
2. **Wave B — Simulation** (`game/simulation/`): well-typed in places, less so in others
3. **Wave C — Strategy** (`game/strategy/`): largest layer
4. **Wave D — AI** (`game/ai/`)
5. **Wave E — UI** (`game/ui/`): largest absolute volume; likely many `-> None` callbacks

Each wave gets its own commit/PR. After each, re-run the audit and document the new coverage figure.

### Annotation guidelines

- **Return None:** if the function has no `return` statement, or only `return` with no value, annotate `-> None`
- **Single return type:** the obvious common case — annotate the actual type
- **Union of types:** use `T1 | T2 | None` (modern syntax, Python 3.10+)
- **Forward references:** use `from __future__ import annotations` at the top of the file if forward refs are needed (or use string literals in the annotation)
- **Generics:** use `list[X]`, `dict[K, V]` etc. directly
- **Callables:** `Callable[[A, B], C]` from `typing` (or `collections.abc`)
- **Protocols:** if a function returns "anything that has a .foo() method," annotate with the relevant Protocol from `game.core.protocols`
- **Don't lie:** if the function actually returns `Any`, annotate `Any`. Don't make up a more specific type that's not enforced

### Don't break tests
Annotations are runtime-evaluated by default. Wrong annotations can cause runtime errors via `inspect.signature`, `dataclasses.field`, `pydantic`, etc. Each wave runs full tests after annotation.

## Architecture

### Why the convention update before backfill
If we backfill 1408 functions and CLAUDE.md still doesn't require annotations on new code, the gap reopens within months. Phase 1 closes the door first.

### Why a CI gate is optional (Phase 4)
A strict CI gate (`mypy --strict` or `pyright`) is the right end state, but introducing it during this project conflates "backfill annotations" with "make the type-checker happy." A simple coverage gate (`% of functions with return annotation`) is the minimal protection; full strictness can be a separate project.

## Dependencies & Risks

1. **Risk: wrong annotations cause runtime errors.**
   `from __future__ import annotations` makes all annotations strings, eliminating runtime evaluation issues. Recommend turning this on in every file we annotate, IF NOT ALREADY ON.
   **Mitigation:** Phase 3 includes a check that adds the `__future__` import if missing.

2. **Risk: PROJ-309 (file decomposition) moves code around while PROJ-311 is annotating it.**
   Merge conflicts.
   **Mitigation:** sequence carefully. Per-wave check: any files in PROJ-309's active sub-phase get touched LAST in this project's wave for that subsystem. Coordination via plan.md Current State updates.

3. **Risk: dunder methods waste reviewer attention.**
   `__init__` doesn't need an annotation per PEP 484. Other dunders are usually fine without.
   **Mitigation:** AST tool excludes dunders from the count. Backfill skips them by default.

4. **Risk: Callbacks and event handlers have wide signatures hard to annotate.**
   Some UI callbacks accept "anything pygame_gui throws at them" and the type is messy.
   **Mitigation:** annotate `-> None` (the universal fallback). If the parameters are messy, leave them — this project is RETURNS only.

5. **Risk: 1408 changes is a lot of diff.**
   Reviewers can't sanity-check 5000-line PRs.
   **Mitigation:** waves by subsystem. Each wave a manageable PR.

## Key Patterns to Reuse
- The AST tool from PROJ-310 may share code with this project's audit tool. Reuse if helpful.
- Modern Python type syntax (PEP 604 unions, native generics) — already used elsewhere in `game/core/protocols.py` and `game/strategy/data/order_types.py`.

## Opportunities Discovered
- Once Phase 4 ships a coverage gate, parameter-annotation coverage becomes a natural follow-up project.
- `mypy --strict` (real type-checking, not just coverage) is a long-term goal. Out of scope.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
