# Verifier Report — PROJ-369 Code Review

**Verifier:** Claude (independent)
**Verifying:** OpenCode review at `report.md` (same directory)
**Branch / HEAD:** `feat/03c-phase-aware-execution` @ `82b5cbc20`
**Verification date:** 2026-05-05

---

## Verdict Summary

| Finding | Severity | Verdict |
|---|---|---|
| MAJ-001 — `build_test_turn_engine` mutates frozen config in place | MAJ | CONFIRM_REMEDIATION_REVISE (downgrade-worthy: severity is MIN at most) |
| MIN-001 — `TickContext` dual-use w/ `tick=0` sentinel | MIN | CONFIRM |
| MIN-002 — Narrow AST-guard import-pattern match | MIN | CONFIRM |
| MIN-003 — `interfaces/engines.py` 778 LOC splittable | MIN | CONFIRM |
| INFO-001 — `_NullBattleResolver` deletion clean | INFO | confirm (passing AST guard observed) |
| INFO-002 — `create_default()` construction order correct | INFO | confirm (OrderProcessor → ActionExecutionEngine spot-checked at lines 165 + 182) |
| INFO-003 — Test migration soundness | INFO | confirm (not re-spot-checked beyond report claims) |
| INFO-004 — `_run_phases` unification | INFO | confirm (AST guard `test_run_phases_called_exactly_twice_in_process_turn` passes) |
| INFO-005 — 7 AST guards pass | INFO | confirm (executed: `7 passed in 1.24s`) |
| INFO-006 — Workshop test errors don't reproduce | INFO | confirm (executed: `137 passed`) |
| INFO-007 — `turn_engine.py` 700 LOC splittable | INFO | confirm (read-only — not re-counted) |
| INFO-008 — `create_default_turn_engine` factory deleted | INFO | confirm (not separately re-checked) |

**Counts:** 0 REJECT, 0 UNCERTAIN, 1 CONFIRM_REMEDIATION_REVISE (MAJ-001), 11 CONFIRM.

---

## MAJ-001 — `build_test_turn_engine` mutates frozen config in place

**Verdict:** `CONFIRM_REMEDIATION_REVISE` — the *fact* is correct, but the **MAJ severity overstates the risk**. Reads more like MIN.

**Evidence read:**
- `tests/fixtures/turn_engine.py:91-118` (full function body verified)
- `game/strategy/engine/turn_engine_config.py:42-201` (frozen=True confirmed at line 42; `ConflictResolutionEngine(...)` constructed fresh per-call at line 173)
- AST guard `test_NullBattleResolver_symbol_absent` passing

**Analysis of OpenCode's claims:**
1. `TurnEngineConfig(frozen=True)` — **confirmed** at `turn_engine_config.py:42`.
2. `cfg.conflict_engine._battle_resolver = battle_resolver` mutates the original instance — **confirmed**. Frozen blocks reassigning fields on the dataclass; it does not block mutating attributes of held objects.
3. "If `dataclasses.replace` is called after, the clone carries the mutated `conflict_engine`" — **confirmed**. `dataclasses.replace` shallow-copies; the same `conflict_engine` instance is reused. This is *intentional and required* for `engine._battle_resolver is mock_resolver` (test at `test_dependency_injection.py:229`) to pass.
4. **Cross-test leak risk:** `ConflictResolutionEngine(...)` is constructed fresh on every `create_default()` call (line 173). Each `build_test_turn_engine` call therefore gets a new `conflict_engine`, so mutation of `_battle_resolver` is **scoped to one test**. There is **no cross-test leak**. OpenCode's report acknowledges this (the only described risk is that an exception between lines 104 and 107 leaves the original mutated — but the original is not reachable because lines 104-107 are adjacent and there is no other reference).

**Severity revision:** Per OpenCode's own description ("Low practical risk since lines 104-107 are adjacent, but the pattern is fragile") this is a code-style / readability concern, not a Major correctness issue. **MIN is the correct severity.**

**Remediation assessment:** OpenCode's "add `battle_resolver` field to `TurnEngineConfig`" is the cleanest fix because then `dataclasses.replace(cfg, battle_resolver=mock)` would Just Work and the conflict_engine would read it at construction time. But this requires reworking `ConflictResolutionEngine` to read `battle_resolver` from a config object rather than be passed it positionally — non-trivial. The fallback ("document the mutation-order invariant in the docstring") is sufficient for the actual risk level.

**Recommended action:** Defer (add docstring note now, structural fix as a future low-priority ticket).

---

## MIN-001 — `TickContext` dual-use with `tick=0` sentinel

**Verdict:** `CONFIRM` (the report's own remediation is appropriately marked non-blocking).

**Evidence read:**
- `game/strategy/engine/turn_phase_registry.py:42-69` — `TickContext` dataclass with `move_queue`, `pre_movement_locations`, `moved_fleet_ids` mid-tick scratch fields
- `DEFAULT_END_OF_TURN_PHASE_LIST` at lines 338-379 — all 6 descriptors confirmed to use `args_resolver=lambda ctx: ((ctx.empires,), {})` or `((ctx.empires, ctx.galaxy), {})`. None reference `move_queue` / `pre_movement_locations` / `moved_fleet_ids`.

The dual-use is real but the current end-of-turn descriptors don't touch the mid-tick fields. The risk is purely future-regression — a new descriptor reading `ctx.move_queue` during end-of-turn would silently see `None`. The proposed `PhaseContext` base-class split is a clean refactor with no invariants that would break (the 5 shared fields are all immutable per-descriptor-call; the 3 scratch fields are only written by tick-loop hooks).

**Recommended action:** Defer to a follow-up ticket. Non-blocking.

---

## MIN-002 — Narrow AST-guard import-pattern match

**Verdict:** `CONFIRM`.

**Evidence read:**
- `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py:91-116` — match is `module.startswith("game.strategy.engine.") and module.endswith("_engine")`.
- All 18 current engine modules (verified via `turn_engine_config.py:122-151`) end with `_engine` (e.g. `fleet_movement_engine`, `production_engine`, `order_processor` — note: `order_processor` does NOT end with `_engine`!).

**Critical observation OpenCode missed:** `OrderProcessor` is imported from `game.strategy.engine.order_processor` (`turn_engine_config.py:124`) — that module name does **not** end with `_engine`. If a future regression reintroduces a function-local `from game.strategy.engine.order_processor import OrderProcessor` inside a `TurnEngine` method, the current AST guard would **not** flag it. This makes MIN-002's concern more concrete than the report describes.

OpenCode's remediation (broaden filter to `module.startswith("game.strategy.engine.")` without `endswith` requirement, or use a positive allowlist) is correct and low-cost.

**Recommended action:** Fix now — small change (one-line broadening or adding allowlist), and `order_processor.py` is a real pre-existing miss in the guard. Suitable for a follow-up commit on this branch.

---

## MIN-003 — `interfaces/engines.py` 778 LOC splittable

**Verdict:** `CONFIRM`.

**Evidence read:**
- `wc -l` confirms 778 LOC.
- Spot-grep confirms 18 ABC classes (no implementation) and `__all__` declaration at lines 29-50.
- No cross-references between Q/A/W engines and the other 15 — the proposed `_engines_terraforming.py` for IQualityEngine / IAtmosphereEngine / IWaterEngine would be cleanly separable.

This is genuinely a "stylistic" miss given `decisions.md` documented the interfaces-only exception. The split is purely cosmetic/maintainability.

**Recommended action:** Defer. The exception is documented; the file is pure interface; LOC ceiling for interface files is debatable.

---

## INFO Spot-Checks

- **INFO-002 (construction order):** Verified at `turn_engine_config.py:165` (`OrderProcessor` constructed) → `:182-185` (`ActionExecutionEngine(order_processor=order_processor, ...)`). Sequencing correct. CONFIRM.
- **INFO-005 (7 AST guards):** Ran `pytest tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py -v` → `7 passed in 1.24s`. All seven by-name match the report. CONFIRM.
- **INFO-006 (workshop tests):** Ran `pytest tests/unit/workshop/ -q` → `137 passed`. Errors do not reproduce. CONFIRM.

---

## Recommended Actions for Claude

**Fix now (one small commit on this branch):**
1. **MIN-002** — Broaden the AST-guard match in `test_no_lazy_fallback_init.py:108-110`. Drop the `endswith("_engine")` constraint, or use the explicit 18-module allowlist. The miss is concrete: `order_processor` module name does not match the current pattern, and a future function-local `from game.strategy.engine.order_processor import OrderProcessor` would slip past.

**Defer to follow-up tickets:**
2. **MAJ-001** — Severity should be **MIN, not MAJ**. The factual claim is correct but cross-test leak is not real (fresh `conflict_engine` per `create_default` call). Add a docstring note at `tests/fixtures/turn_engine.py:102` explaining the mutation-order invariant. Structural fix (add `battle_resolver` field to `TurnEngineConfig`) is a future cleanup, not blocking.
3. **MIN-001** — `PhaseContext` base-class extraction; non-blocking, future ticket.
4. **MIN-003** — Optional cosmetic split of `interfaces/engines.py`; documented exception applies.
5. **INFO-007** — `turn_engine.py` 700 LOC follow-up split (extract `_time_phase` + `_run_phases` + property mixin). Follow-up ticket.

**No further action:**
- All other INFO findings: confirmed clean. No verification gap found.

**Net assessment:** OpenCode's review is substantively correct. The one severity miscalibration (MAJ-001 should be MIN) and one missed-coverage detail (`order_processor` slips past MIN-002's guard pattern) are the only callouts. PROJ-369 is in good shape; only MIN-002 warrants a same-branch fix.
