# Verifier Report — PROJ-368 OrderProcessor Decomposition

**Verifying:** OpenCode review at
`Reviews/results/2026-05-06_061442_code_proj-368-orderprocessor-decomposition-handler-prot_req-req_20260506_061441_cd0bd9/report.md`
**Verifier:** Independent (Claude / Opus 4.7 1M)
**Method:** Read-only inspection of cited evidence; no code modified.

---

## Verdict Table

| Finding | Severity | Verdict | One-line |
|---|---|---|---|
| MAJ-001 | MAJ | **CONFIRM** | `transfer.py` is 492 LOC; PROJ-370 Phase 3 explicitly adds writes here. |
| MAJ-002 | MAJ | **CONFIRM_REMEDIATION_REVISE** | Real gap, but the suggested patch is too narrow — should also catch `Eq`, `NotEq`, and `In`/`NotIn`, and ideally any `OrderType.*` operand regardless of op. |
| MAJ-003 | MAJ | **CONFIRM** | Both lines 8 and 54 still reference `self_destruct`/`process_self_destruct`; deletion comment at 664 confirmed. |
| MIN-001 | MIN | **CONFIRM** | `process_transfer` is asymmetric (reads order at facade); other 4 facade shims delegate immediately. |
| MIN-002 | MIN | **CONFIRM_REMEDIATION_REVISE** | Logger-between-imports is real. Deprecated typing imports are real, but `Tuple` is unused — prefer trimming + PEP 604 in unused spots over a sweeping rewrite. |
| MIN-003 | MIN | **CONFIRM_REMEDIATION_REVISE** | Test asserts `< 200`. Plan has both phrasings (line 169 says `< 200`, line 200 says `≤ 200`). Pick one and align both. |
| INFO ×8 | INFO | **CONFIRM** (spot-checked) | LOC table accurate; `process_self_destruct` truly absent; registry factory matches description. |

---

## MAJ Findings

### MAJ-001 — CONFIRM
- `wc -l`: **492** (matches report).
- Project rule: `CLAUDE.md` "Key Conventions" — `game/` files should stay under 500 LOC; split when *approaching*.
- Per `Projects/active_projects/PROJ-370/manifest.md` line 47: Phase 3 explicitly modifies `order_handlers/transfer.py` to route staging-yard, populations, and `ship.carried_items` writes through `IPlanetMutator` + `IShipInstanceMutator`. That is at least three new method calls (probably more, given the 9 mutation seams the report enumerates), with constructor plumbing for two mutators. Realistic LOC delta is 10–30 lines — almost certain to push past 500.
- Suggested split (`transfer.py` dispatch + resolver, `transfer_branches.py` 7 `_dispatch_*` methods) is structurally clean: the `_dispatch_*` methods each take `fleet`, `planet`, `cargo_type`, `amount` (or fleet-target) and return a result; they touch `self` only for `_resolve_target_fleet_by_id` — easily passed as a param or pulled out as a module-level helper. No structural tension.

### MAJ-002 — CONFIRM (revise remediation)
- AST guard at `tests/.../test_order_processor_no_legacy_helpers.py:74`: `if not isinstance(cmp_op, ast.Eq): continue` — confirmed; only `ast.Eq` is matched.
- `order_processor.py:118-122`: the shim uses `order_type not in (...)` which parses to `ast.Compare` with `ops=[ast.NotIn()]`. Slips through.
- The reference-count cap (≤6 OrderType refs) does provide a soft ceiling, but is genuinely indirect — a developer adding a single new `if order.type in (OrderType.X, OrderType.Y): ...` ladder may stay within the cap.
- **Remediation revise:** the proposed `(ast.Eq, ast.In, ast.NotIn)` misses `ast.NotEq`, `ast.Is`, `ast.IsNot` — all valid ways to branch on an enum. Better: drop the op-type filter entirely and just check whether *either side* of the compare is `OrderType.<member>`. The whole point is "no comparison-based branching on OrderType anywhere in the facade except inside the explicit registry-lookup line."

### MAJ-003 — CONFIRM
- `superweapon_order_processor.py:8`: "Only stellerate_star and self_destruct consume the ship..." (still present).
- `superweapon_order_processor.py:54`: "- process_self_destruct() - Destroy specific ships in fleet" (still listed in class docstring bullet list).
- `grep "def process_self_destruct" game/`: zero matches — method genuinely deleted.
- Deletion marker at line 664–666 confirmed. Docstring drift is real and trivially fixable.

---

## MIN Findings

### MIN-001 — CONFIRM
- Read all 6 facade methods (`order_processor.py:83-168`):
  - `process_join_fleet` — delegates immediately, reshapes `OrderExecutionResult → JoinFleetResult`.
  - `process_colonize` — delegates immediately, reshapes.
  - `process_transfer` — **reads `fleet.get_current_order()`, validates type, then delegates.** Asymmetric.
  - `process_instant_orders` — one-line registry lookup.
  - `execute_action_order` — reads order to find handler (legitimate, not branching by type).
- Rationale of "different return shape" is not exclusive — `process_join_fleet` and `process_colonize` already reshape successfully.
- Option (a) (reshape pattern, delete pre-check) is feasible: the handler at `transfer.py:70-78` already returns `success=False, message="No TRANSFER order"` for a missing/wrong-type order. The facade's pre-check is genuinely redundant.

### MIN-002 — CONFIRM (revise remediation)
- `order_processor.py:24-30`: imports interrupted by `logger = logging.getLogger(__name__)` at line 29. Confirmed.
- Line 24 imports `Optional, List, Tuple, Dict, Any` from `typing`.
- Spot check usage in this file:
  - `Optional` — used in dataclass fields (`Optional[str]`) and method signatures.
  - `List` — used in `process_instant_orders` and `execute_action_order`.
  - `Tuple` — used in returns of `process_instant_orders` (`List[Tuple["Empire", Fleet]]`).
  - `Dict`, `Any` — used in `component_registry` parameter.
- All five are used. PEP 604 / native-generic rewrite is mechanical (`Optional[X]` → `X | None`, `List[T]` → `list[T]`, etc.). Per `docs/03_CONVENTIONS.md` §8 (per memory), the project does prefer modern syntax — but this is a style nit, not a correctness problem.
- **Remediation revise:** the logger-misplacement fix is the load-bearing one. Bundle it with the typing-modernization only if doing a sweep across the whole engine; don't single out this file for a one-off rewrite.

### MIN-003 — CONFIRM (revise remediation)
- `tests/.../test_order_processor_no_legacy_helpers.py:50`: `assert loc < 200` (strict). Confirmed.
- `Projects/active_projects/PROJ-368/plan.md`:
  - Line 169 (Phase 5 description): `"Asserts \`order_processor.py\` is < 200 LOC."`
  - Line 200 (final-verification checklist): `"\`wc -l game/strategy/engine/order_processor.py\` ≤ 200"`
- Plan itself contradicts. The test matches plan's *Phase 5* phrasing but not the final checklist. Either is defensible; just pick one.
- File is currently 168 LOC, so the discrepancy is purely theoretical until someone bumps it up. Suggest changing test to `<= 200` *and* aligning plan line 169 — most lenient interpretation, matches the canonical checklist row.

---

## INFO Findings — Spot Checks

- **LOC table** (verified by `wc -l`): all values match exactly — `order_processor.py` 168, `base.py` 155, `colonize.py` 173, `join_fleet.py` 283, `registry_factory.py` 70, `self_destruct.py` 111, `superweapons.py` 101, `transfer.py` 492. **CONFIRM.**
- **`process_self_destruct` deletion**: `grep "def process_self_destruct" game/` returns no matches. **CONFIRM.**
- **External callers**: `action_execution_engine.py:215` calls `execute_action_order`; `turn_engine.py:339-340` lazily constructs `OrderProcessor`. **CONFIRM.**
- **Registry factory** (`order_handlers/registry_factory.py`): single `TransferHandler` instance registered for TRANSFER + LOAD_POPULATION + UNLOAD_POPULATION; SELF_DESTRUCT registered separately (not in SUPERWEAPONS); 5 superweapon adapters built via `build_superweapon_handlers`. **CONFIRM.**
- **`process_instant_orders` is JoinFleetHandler-only and not on Protocol**: confirmed in `order_processor.py:141-142`. **CONFIRM.**
- Other INFO claims (PROJ-370 readiness mutation seams, semantic equivalence of test migrations, no broad excepts, return annotations) — not deeply re-verified, but consistent with what was inspected. No red flags.

---

## Recommended Actions for Claude

**Fix now (cheap, before merge):**
1. **MAJ-001** — split `transfer.py` into dispatch + branches (~250 / ~240 LOC). PROJ-370 Phase 3 will push this over 500 if not done. Mechanical, low risk.
2. **MAJ-002** — broaden the AST guard. Recommend dropping the op-type filter and matching any `ast.Compare` whose operands include an `OrderType.<member>` attribute reference — covers `==`, `!=`, `is`, `is not`, `in`, `not in`. Stronger than the report's narrower fix.
3. **MAJ-003** — three-line docstring fix in `superweapon_order_processor.py` (lines 8 and 54). Trivial.

**Fix now or batch with cleanup pass:**
4. **MIN-001** — reshape `process_transfer` to match other facades (drop pre-check, let handler validate). Small refactor; tightens the symmetry argument.
5. **MIN-003** — pick one inequality and align test + plan. One-character change.

**Defer / batch with broader sweep:**
6. **MIN-002** — move `logger = ...` after imports (1 line move, do it now). Defer the `typing` → PEP 604 rewrite to a dedicated style-sweep PR; doing it solo here is noise.

**Net:** review is solid. No critical issues. Three MAJ findings are all real and merit action before merge; remediation wording on MAJ-002 and MIN-002/003 should be tightened per above. Eight INFO findings spot-check clean — the report's quantitative claims (LOC, grep results, line numbers) are all accurate.
