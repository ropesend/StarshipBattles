# PROJ-209: Decisions Log

## Decision 1: Phase by function, not severity
**Date:** 2026-02-27
**Context:** Auto-generated project grouped findings by severity (Critical -> Phase 1, Major -> Phase 2). This doesn't work for a decomposition project where each function is a self-contained unit of work.
**Decision:** Reorganize into 4 phases, one per function, ordered by risk: load_game -> production_engine -> fleet_navigation -> ship_stats_calculator.
**Rationale:** All 5 review agents agreed on this ordering. load_game is lowest risk with natural phase boundaries. calculate_stats is highest risk with the most extraction targets.

## Decision 2: Reject Policy/Registry pattern for calculate_stats
**Date:** 2026-02-27
**Context:** Original proposal included a Registry of Policy objects (MassCalculator, HpCalculator, etc.) for calculate_stats.
**Decision:** Use simple private method extraction instead.
**Rationale:** DS-007 (validated): the ability set is fixed and known, the code is called from one place, and the pattern introduces abstraction overhead with zero reuse benefit. Simple methods achieve the same CC reduction.

## Decision 3: Split `_apply_production_progress` into 3 methods
**Date:** 2026-02-27
**Context:** Original proposal had a single `_apply_production_progress(item, ticks_to_spend, production_rate)`.
**Decision:** Split into `_check_affordability`, `_apply_resource_consumption`, `_check_item_completion`.
**Rationale:** DS-001 (validated): the original conflated 3 concerns and its proposed signature was missing 5+ required parameters. Three focused methods have cleaner boundaries and each is independently testable.

## Decision 4: Reject `_accumulate_component_stats` extraction
**Date:** 2026-02-27
**Context:** Original proposal included `_accumulate_component_stats(components, modifiers, damage)` as a single extraction for the entire loop body.
**Decision:** Replace with per-ability accumulator methods.
**Rationale:** DS-005 (validated, unanimous across agents): moving CC~20 into a new method just relocates complexity without decomposing it. Per-ability methods (5-7 of them) each have CC 2-5.

## Decision 5: Keep `_advance_tick` inline, extract `_consume_ticks` instead
**Date:** 2026-02-27
**Context:** Original proposal for project_path included `_advance_tick(state)` covering segment creation + state update + turn advancement.
**Decision:** Keep segment creation and state update inline (simple, ~15 lines). Extract only `_consume_ticks` as a reusable pure function.
**Rationale:** DS-015 (validated): `_advance_tick` was too broad with 3 distinct outputs. `_consume_ticks` is reusable (action orders + movement), pure, and independently testable.

## Decision 6: Fix AR-01 bug before decomposing production engine
**Date:** 2026-02-27
**Context:** Lines 253-260 have a broken fallback that calls `_calculate_design_cost(item)` with wrong argument type, followed by bare `pass`. This is a latent free-spawn bug.
**Decision:** Fix this as Task 2.1 before any decomposition work on production engine.
**Rationale:** AR-01, CQ-002, CX-007, DS-003 (all validated): 4 of 5 agents flagged this independently. Decomposing around a known bug risks propagating it into extracted methods.
