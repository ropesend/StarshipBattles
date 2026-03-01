# PROJ-209: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-27_211154_general_cyclomatic-complexity-deep-dive](../../Reviews/results/2026-02-27_211154_general_cyclomatic-complexity-deep-dive/)
- **Type:** General Review (Complexity Focus)
- **Date:** 2026-02-27
- **Report:** [View Full Report](../../Reviews/results/2026-02-27_211154_general_cyclomatic-complexity-deep-dive/report.md)

## Initial Analysis
- **Functions targeted:** 4 (all Radon Rank D)
- **Combined CC:** 101 (27 + 26 + 26 + 22)
- **Target CC:** Each orchestrator <= 10, each helper <= 8
- **Review findings:** 95 validated (7 Critical, 35 Major, 37 Minor, 16 Info)
- **Selected for remediation:** 42 (all Critical + Major)

---

## Decomposition Strategy Per Function

### Phase 1: SaveGameService.load_game (CC=26 -> ~6)

**Current structure:** Linear pipeline of load-validate-reconstruct with 14 except clauses.

**Strategy:** Extract 3 phase-based helpers + 1 shared JSON loader.

| Extracted Method | Lines | CC | Pure? |
|---|---|---|---|
| `_load_json_safe(path, description)` | shared | ~2 | Yes (I/O but deterministic error handling) |
| `_load_save_metadata(save_path)` | 124-159 | ~5 | Yes |
| `_load_turn_data(save_path, metadata)` | 162-191 | ~4 | Yes |
| `_reconstruct_game_session(game_state, save_path)` | 194-208 | ~3 | No (creates GameSession) |
| **Orchestrator** | remaining | **~6** | -- |

**Key insight:** 14 of 25 CC points come from exception handlers. `_load_json_safe` eliminates 8 CC points by consolidating duplicate 4-exception patterns.

---

### Phase 2: ProductionEngine._process_queue_tick_dynamic (CC=27 -> ~7)

**Current structure:** 130-line while loop with interleaved validation, calculation, mutation, and completion.

**Strategy:** Fix bug first, then extract 5 focused helpers (revised from original 3).

| Extracted Method | Lines | CC | Pure? |
|---|---|---|---|
| `_validate_queue_item(item, colony_or_fleet, galaxy, is_complex_only)` | 226-249 | ~5 | Yes (returns tri-state) |
| `_calculate_tick_expenditure(item, tick_capacity, production_rate)` | 262-316 | ~6 | **Yes** (highest value) |
| `_check_affordability(empire, cost_this_step)` | 318-320 | ~1 | Yes |
| `_apply_resource_consumption(empire, item, cost_this_step)` | 323-326 | ~2 | No (mutates empire + item) |
| `_check_item_completion(item, total_cost)` | 341-350 | ~2 | Yes |
| **Orchestrator** | while loop | **~7** | -- |

**Key insight:** The original proposed `_apply_production_progress` conflated 3 concerns (DS-001). Splitting into affordability + consumption + completion gives cleaner boundaries.

**Pre-requisite:** Fix the broken `_calculate_design_cost(item)` fallback (AR-01/CQ-002) -- replace with explicit error handling.

---

### Phase 3: FleetNavigationService.project_path (CC=22 -> ~10)

**Current structure:** While loop mixing action order handling, movement projection, and tick management with 5 mutable variables.

**Strategy:** Extract action order handling + introduce shared tick consumption helper.

| Extracted Method | Lines | CC | Pure? |
|---|---|---|---|
| `_consume_ticks(moves_left, current_turn, moves_per_turn, max_turns, ticks)` | 481-488, 558-560 | ~2 | **Yes** (reused in 2 places) |
| `_project_action_order(state, order, ...)` | 470-499 | ~5 | No (uses fleet + registry) |
| `_resolve_path_for_order(state, order, galaxy)` | 501-519 | ~4 | No (pathfinding) |
| **Orchestrator** | while loop | **~10** | -- |

**Key insight:** The proposed `_advance_tick` was too broad (DS-015). Keep segment creation inline; extract only tick consumption as a reusable pure function.

**Pre-adjustment:** Handle `first_order_progress` before the main loop to eliminate `is_first_order` flag (DS-016).

---

### Phase 4: ShipStatsCalculator.calculate_stats (CC=26 -> ~8)

**Current structure:** 136-line for-loop processing 8 ability types sequentially.

**Strategy:** Extract per-ability accumulator methods. WarpJump first (31% of CC).

| Extracted Method | Lines | CC | Pure? |
|---|---|---|---|
| `_accumulate_warp_stats(abilities, comp_id, ...)` | 252-284 | ~5 | Yes |
| `_accumulate_resource_storage(abilities, ...)` | 200-210 | ~3 | No (mutates dict) |
| `_accumulate_cargo_storage(abilities, ...)` | 213-222 | ~3 | No (mutates dict) |
| `_accumulate_consumption(abilities, ...)` | 234-249 | ~3 | No (mutates dicts) |
| `_accumulate_movement(abilities, ...)` | 225-228 | ~2 | Yes |
| **Orchestrator loop** | remaining | **~8** | -- |

**Key insight:** The proposed `_accumulate_component_stats` would just relocate CC~20 (DS-005). Per-ability methods actually decompose the complexity.

**Rejected approach:** Policy/Registry pattern (DS-007) -- overengineered for a fixed, known set of ability types. Simple private methods achieve the same CC reduction.

---

## Cross-Cutting Concerns

### Named Constants (AR-13, CX-015)
Define during Phase 2 for production engine:
- `TICKS_PER_TURN = 100`
- `TICK_CAPACITY_EPSILON = 0.0001`
- `COMPLETION_EPSILON = 0.001`
- `MAX_QUEUE_ITERATIONS = 10`

### Test Preservation Strategy
- **Preserve all existing tests** as regression suite -- do not modify unless directly broken
- **Fill gaps BEFORE decomposing** -- each phase starts with test gap tasks
- **Add targeted tests AFTER extracting** -- each new method gets its own tests
- **Integration/consistency tests are the safety net** -- never modify these

### `dataclasses.replace()` for NavigationState (CQ-026)
Apply in Phase 3 to eliminate 3 copies of manual NavigationState construction.

---

## Dependencies & Risks
1. **Phase 1 has no dependencies** -- can start immediately
2. **Phase 2 requires AR-01 bug fix first** -- do not decompose with broken fallback
3. **Phase 3 benefits from confidence built in Phases 1-2** -- tests and patterns established
4. **Phase 4 is highest risk** -- most test coverage to validate against, most extraction targets

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
