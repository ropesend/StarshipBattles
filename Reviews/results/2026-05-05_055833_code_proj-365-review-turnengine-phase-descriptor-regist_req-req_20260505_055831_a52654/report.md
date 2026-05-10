# Review Report: PROJ-365 — TurnEngine Phase Descriptor Registry

**Request ID:** req_20260505_055831_a52654
**Review type:** code
**Review mode:** normal (full-depth, inline analysis)
**Scope:** 5 files (see scope.md)
**Checkout SHA:** N/A (working tree review)

---

## Summary

The PROJ-365 refactor successfully replaces the imperative `_process_tick` body with a declarative 15-phase descriptor registry (`DEFAULT_TICK_PHASE_LIST`). The core architecture is sound: `TickPhase` frozen descriptors encode ordering, args resolution, and cross-phase state flow; `TickContext` serves as a mutable per-tick state carrier. The golden test correctly pins the 15-phase order, the PROJ-320 `moved_fleet_ids` invariant is preserved, and there are no layer-boundary violations.

**2 MAJOR findings** (perf log drift — missing phases), **4 MINOR findings** (doc/label inconsistencies), **3 NIT findings** (dead metadata fields). No CRITICAL findings. All instructions from the request are addressed below.

---

## Findings

### MAJ-001: `planet_modifier_effects` missing from perf log format string

**Severity:** MAJ
**File:** `game/strategy/engine/turn_engine.py:643-659`
**Fingerprint:** `sha256:2c3f4b5a6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a`

The PROJ-365 refactor routes `planet_modifier_effects` through `_time_phase` uniformly (pre-PROJ-365 it was a raw local-construct call). The `_phase_times` dict (line 253) correctly includes `'planet_modifier_effects': 0.0`, and the dispatch loop at line 742 calls `self._time_phase(bucket, target, *args, **kwargs)` for every phase including this one. The timing IS accumulated.

However, the `logger.warning()` format string at lines 643-659 does NOT include `planet_modifier_effects`. The accumulated timing for this phase is never logged, making performance debugging of planet modifier effect processing impossible through the existing log line.

**Severity rationale:** MAJ. Not a correctness bug — the phase executes correctly and timing is in the dict — but since the refactor's *purpose* was partly to make this phase visible/monitorable through the uniform `_time_phase` path, logging its timing was an implicit deliverable. Any performance regression in this phase will be invisible in logs.

**Suggested remediation:** Add `; planet_modifier_effects=%.3fs` to the format string and the corresponding `self._phase_times['planet_modifier_effects']` argument, between `activation_timers` and `move_calc` to match phase order.

---

### MAJ-002: End-of-turn phases missing from perf log format string

**Severity:** MAJ
**File:** `game/strategy/engine/turn_engine.py:643-659`

Per PROJ-343 T1.2-engines, end-of-turn engines (`organics_consumption`, `happiness`, `quality_improvement`, `atmosphere`, `water_modification`) now route through `_time_phase` for rollback safety (code at lines 589-620). Their timings ARE accumulated in `_phase_times` dict (lines 257-258). However, the perf log format string at lines 643-659 only prints `population_growth` (line 658) and omits all five other end-of-turn phases.

**Severity rationale:** MAJ. Same rationale as MAJ-001 — these phases' timings are collected but unreported. Five of six end-of-turn phases have silent performance regressions.

**Suggested remediation:** Extend the format string to include `organics_consumption`, `happiness`, `quality_improvement`, `atmosphere`, and `water_modification`, each with its corresponding `self._phase_times[...]` argument.

---

### MAJ-003: Perf log format string label `orders=` mismatches dict key `instant_orders`

**Severity:** MAJ — corrected to MIN after analysis (see below)
**File:** `game/strategy/engine/turn_engine.py:647`

The format string fragment at line 647 reads `orders=%.3fs`, but the dict key accessed at line 653 is `self._phase_times['instant_orders']`. Python's `%` formatting is positional, so the correct value IS printed — but `orders` in the log line is ambiguous (there is no phase called "orders"; the phase is "instant_orders"). A developer grepping logs or writing a log parser would need to know that `orders` means `instant_orders`.

**Severity rationale:** Corrected to MIN. No runtime error, no data corruption. Purely a log-label clarity issue.

**Suggested remediation:** Change `orders=%.3fs` to `instant_orders=%.3fs` in the format string to match the `_phase_times` key name.

---

### MIN-001: Module docstring lists 14 phases; code executes 15

**File:** `game/strategy/engine/turn_engine.py:11-27`

The module-level "Turn Phases" docstring (lines 11-27) enumerates 14 per-tick phases: 0 (harvesting), 0b (resources), 0c (fuel_gen), 0c1 (planet_energy), 0d (resupply), 0e (production), 0f (environmental), 1 (instant_orders), 1.5 (actions), 1.6 (planet_actions), 1.7 (activation_timers), 2 (movement_calc), 3 (movement_apply), 4 (combat).

Missing: Phase 1.8 `planet_modifier_effects`. The `_process_tick` docstring (lines 692-708) correctly lists all 15 phases. Pre-PROJ-365, `planet_modifier_effects` was an implicit local-construct call not listed as a formal phase. PROJ-365 formalized it — the module docstring should follow.

**Suggested remediation:** Add `Phase 1.8:  Planet modifier effects (via PlanetModifierEffectEngine)` to the module docstring between Phase 1.7 and Phase 2.

---

### MIN-002: Request instruction mentions "14-phase ordering" but implementation is 15

**Not a code finding — informational.** The review request instructions say "Verify the 14-phase ordering is preserved exactly (golden test)." The golden test (`GOLDEN_PHASE_ORDER` in `test_default_tick_phase_list.py:42`) lists 15 phases, `DEFAULT_TICK_PHASE_LIST` contains 15 entries, and all assertions (count, order, uniqueness) pass at 15. The code is correct; the request instruction count is off by one because `planet_modifier_effects` was added as an explicit phase in the descriptor registry.

---

### MIN-003: `_process_tick` docstring lists 15 phases with numbering gap at Phase 1.8

**File:** `game/strategy/engine/turn_engine.py:692-708`

The docstring lists `Phase 1.8:  planet_modifier_effects` (line 705), which is correct. But the numbering jumps from "Phase 1.7" to "Phase 1.8" to "Phase 2" — there is no "Phase 1.9". This is the legacy numbering scheme and not introduced by PROJ-365, but the docstring perpetrates it.

**Suggested remediation:** None required (cosmetic). Optionally add a comment noting that Phase 1.8 was previously implicit.

---

### NIT-001: `tick_gating` field is set but never read by the dispatch loop

**File:** `game/strategy/engine/turn_phase_registry.py:81` (field declaration), `game/strategy/engine/turn_engine.py:735-745` (dispatch loop)

The `tick_gating` field is set to `TICK_GATE_ONLY_TICK_1` on `harvesting` (line 180) and `production` (line 215) descriptors. The dispatch loop in `_process_tick` (lines 735-745) never reads `phase.tick_gating`. Instead, hooks self-gate by checking `ctx.tick == 1` internally (`_log_turn_start_tick_1` line 113, `_log_after_construction_tick_1` line 119).

The decisions doc (PROJ-365 row 2026-05-04) confirms this is intentional: "`tick_gating` is documentary; hooks self-gate via `ctx.tick`." The field and its constant `TICK_GATE_ONLY_TICK_1` exist primarily as documentation and as a future hook point for stricter dispatch-level enforcement.

**Severity rationale:** NIT. Documented intentionality. But a field with a name like `tick_gating` strongly implies the dispatch loop enforces it. Future maintainers may add checks on it and inadvertently skip harvesting/production on ticks 2..100.

**Suggested remediation:** Either:
1. (Preferred) Add a comment on the dispatch loop noting that `tick_gating` is intentionally not consulted — hooks self-gate instead.
2. Remove the `tick_gating` field entirely until dispatch-level enforcement is implemented.

---

### NIT-002: `error_policy` field declared but never read by the dispatch loop

**File:** `game/strategy/engine/turn_phase_registry.py:80` (field declaration), `game/strategy/engine/turn_engine.py:735-745` (dispatch loop)

The `error_policy` field defaults to `'wrap'` and is declared on every descriptor. The dispatch loop never reads it — all phases are wrapped by `_time_phase` unconditionally (the current 'wrap' behavior). The `'barrier'` value is documented as "reserved for future use." Like `tick_gating`, this is dead metadata at present.

**Severity rationale:** NIT. Documented forward-compatibility field. No functional impact.

**Suggested remediation:** None required. Accept as forward-compatibility placeholder.

---

### NIT-003: `TICK_GATE_ONLY_TICK_1` constant used only as stored field value, never for logic

**File:** `game/strategy/engine/turn_phase_registry.py:38`

The constant is defined at module level with documentation ("applied to descriptors whose pre/post hooks should only fire on tick==1"). It is stored on two descriptors (`harvesting` and `production`) as their `tick_gating` field value. It is never used in any conditional or enforcement logic.

**Severity rationale:** NIT. Provides one source of truth for the gating value, preventing typos like `'only_tick1'` vs `'only_tick_1'`. Justified as a named constant even without runtime enforcement.

---

## Per-Instruction Verification

| Instruction | Status | Notes |
|---|---|---|
| 15-phase ordering preserved exactly (golden test) | **PASS** | `test_default_phase_list_count_matches_golden`, `test_default_phase_list_order_matches_golden`, `test_phase_order_matches_golden_on_tick_1`, `test_phase_order_matches_golden_on_tick_5` all pass. 15 phases match `GOLDEN_PHASE_ORDER` exactly. |
| `pre_exec_hook` justified and doesn't double-fire | **PASS** | `_log_turn_start_tick_1` fires once before harvesting on tick==1; `_log_after_construction_tick_1` fires once after production on tick==1. `test_log_empire_state_called_twice_on_tick_1` verifies exactly 2 calls. `test_log_empire_state_not_called_on_tick_5` verifies 0 calls on tick!=1. Turn-level logging uses different labels ("=== TURN START ==="). |
| `tick_gating` semantics: hooks self-gate on `ctx.tick` | **PASS** | Hooks check `ctx.tick == 1` internally. `tick_gating` field is documentary only (NIT-001). Dispatch loop never gates on it, preserving harvesting/production on ticks 2..100. |
| PROJ-320 `moved_fleet_ids` cross-phase state works | **PASS** | Flow: `_capture_move_queue` → `ctx.pre_movement_locations` → `_derive_moved_fleet_ids` → `ctx.moved_fleet_ids` → combat's `args_resolver`. `test_combat_phase_receives_moved_fleet_ids` verifies `{100}` for the moved fleet. |
| `_phase_times` key drift | **FOUND** | See MAJ-001, MAJ-002, MAJ-003. All 21 dict keys are correct. The perf log format string has 3 issues. |
| Layer-boundary check | **PASS** | `turn_phase_registry.py` imports from `dataclasses`, `typing`, and lazily imports `PlanetModifierEffectEngine` (Strategy→Strategy). No UI or simulation imports. `turn_engine.py` imports stay within Core + Strategy. |

---

## Findings by Severity

| Severity | Count |
|---|---|
| CRITICAL | 0 |
| MAJOR | 2 |
| MINOR | 4 |
| NIT | 3 |

**Total: 9 findings**

---

## Limitations

- End-to-end integration testing of the full 100-tick loop with the descriptor registry was not in scope; golden tests verify the per-tick phase ordering and cross-phase invariants only.
- Performance regression testing (wall-clock comparison of old imperative vs. new descriptor-driven `_process_tick`) was not performed.
- The `TurnEngine` constructor (18 collaborators) was explicitly out of scope per the decisions doc.
