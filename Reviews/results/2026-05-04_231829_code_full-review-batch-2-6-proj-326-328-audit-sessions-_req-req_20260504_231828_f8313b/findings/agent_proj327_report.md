# PROJ-327 Review Report — Runtime Retraction & Compositional Construction

**Date:** 2026-05-04
**Review scope:** Question 2 (runtime reduction retraction) + Question 3 (Compositional Construction, Pattern §32)

---

## Findings

### CRITICAL FND-327-01: Scorecard still presents -3.9s as definitive wall-clock delta after retraction

**File:** `Projects/active_projects/PROJ-327/decisions.md:31`
**Description:** The Per-technique scorecard's Wall-clock delta column for Phase 1 reads `**~3.9 s** suite-level (~30 ms file-level)` with no retraction qualifier and no note that this figure is inside the noise envelope. Audit commit `7f94a0c94` (S2.9) added a separate "Code-quality impact" column and a prefatory note about column interpretation, but **did not correct or remove the 3.9s wall-clock delta figure itself**. The prefatory note says "the two columns can disagree" but never states the 3.9s is unreliable or retracted.

Meanwhile, `findings/runtime_delta.md:11` carries the explicit headline retraction: "PROJ-327 did not establish a causal suite-level runtime reduction … should not be cited as reclaimed time." This creates a direct contradiction: the decisions.md scorecard (the canonical "what was achieved" reference) still cites 3.9s as the runtime achievement, while runtime_delta.md says the same figure was retracted.

**Recommendation:** Append a `[†]` dagger after the 3.9s value in the scorecard with a footnote: "Observed -3.9s is within the 15.3s pre-baseline noise envelope; per audit S2.7, this delta is not citable as reclaimed time." Alternatively, replace the figure with `~0 s (retracted)` and note the file-level 30ms verifiable delta in the Verdict column.

---

### CRITICAL FND-327-02: `virtual_table_runtime.md` claims disproven amplification mechanism with no retraction

**File:** `Projects/active_projects/PROJ-327/findings/virtual_table_runtime.md:25-27`
**Description:** Lines 25-27 present the 3.9s as a definitive suite delta with an explanatory mechanism:

> "Suite delta: ~3.9 s wall reduction … The slowest-shard delta (3.9 s) is roughly the per-test reclaim (~30 ms × 16 tests = ~0.5 s) amplified by the fact that other tests in the same shard depend on this file's runtime budget — when the file is faster, the shard finishes earlier and pulls the rest of its test list along."

This is the precise mechanism that audit S2.7 disproved in `runtime_delta.md:62`:

> "30 ms file-level delta cannot produce 3.9 s suite-level delta. `test_virtual_table.py` runs on exactly one shard and finishes in 1.03 s (0.8 % of a shard's budget). Saving 30 ms from one file saves 30 ms from its shard's wall-clock — not 3.9 s."

The sharded runner uses greedy bin-packing; one file completing slightly faster does not "pull along" other tests. The file was NOT updated by audit commit `7f94a0c94` and still carries the uncorrected claim.

**Recommendation:** Add a "RETRACTED 2026-05-04 (audit-remediation S2.7)" banner at the top of `virtual_table_runtime.md` and remove or cross-out lines 25-27's amplification mechanism. Reference `runtime_delta.md` for the full retraction analysis.

---

### MAJOR FND-327-03: Mock's populate() idempotency check catches a different failure mode than documented

**File:** `tests/fixtures/strategy_screen_composition.py:115-134`
**Description:** The `populate()` docstring (lines 115-121) claims the check detects:

> "Calling populate() on the same screen with a *different* MockStrategyScreenComposition instance is a programming error … Detect that case and fail loudly."

But the code at lines 123-134 only guards against a different scenario:

```python
screen_id = id(screen)
if self._populated_screen_id is not None and self._populated_screen_id != screen_id:
    raise AssertionError(...)
```

This detects **"same composition reused across two different screens"** — not "same screen populated with two different compositions." For a fresh composition (`_populated_screen_id` is `None`), calling `populate()` on an already-populated screen passes silently. The code actually catches a useful scenario (preventing mock identity leaks when one composition is shared across tests), but the comment/documentation claims a different scenario that goes undetected.

Additionally, neither the success nor the error-raising path of the idempotency check is tested — `test_strategy_screen_composition.py` has no test that exercises `populate()` called twice on the same or different screens.

**Recommendation:** (a) Fix the docstring to accurately describe what the check catches (same composition on two different screens). (b) Add two tests: one confirming repeated `populate(same_screen)` on the same composition is allowed, and one confirming `populate(different_screen)` raises `AssertionError`.

---

### MAJOR FND-327-04: No structural conformance test between Protocol, Factory, and Mock

**File:** `tests/unit/ui/screens/test_strategy_screen_composition.py`
**Description:** The smoke tests verify:
- `StrategyScreenCompositionFactory` returns correct production types (8 `isinstance` checks)
- `MockStrategyScreenComposition` returns pre-stored mocks per slot (8 parametrized checks)
- `populate()` wires all 8 slots (1 test)

Missing: a test that the Mock structurally conforms to the Protocol. If a developer adds `make_planet_view(self, screen) -> PlanetView` to the Protocol and Factory but forgets to add it to `MockStrategyScreenComposition`, the existing tests (which iterate over `MockStrategyScreenComposition._SLOTS` — separately editable) would not catch the omission. No test passes `MockStrategyScreenComposition()` where `StrategyScreenComposition` is expected at a type-checking boundary.

This is a real risk: the `_SLOTS` tuple (line 54) is the single source of truth for 8 `make_*` → attribute-name mappings, but nothing verifies it stays in sync with the Protocol's method set. The smoke test comments say "Adding a new sub-object … should fail one of these tests" — but this is only true if the developer also updates `_SLOTS`.

**Recommendation:** Add a test that iterates over the Protocol's method names (e.g., via `typing.get_type_hints(StrategyScreenComposition)`) and verifies every method has a matching attribute-name entry in `MockStrategyScreenComposition._SLOTS`. Alternatively, add a simple call-site test where `StrategyScreen.__init__`'s `composition` parameter accepts `MockStrategyScreenComposition()` and all 8 slots are populated correctly.

---

### MAJOR FND-327-05: Stale -3.9s claims litter phase_5_checklist task notes

**File:** `Projects/active_projects/PROJ-327/phase_5_checklist.md:27,44,56,83`
**Description:** Four separate task notes in phase_5_checklist.md cite `-3.9 s` as the achievement delta without any retraction qualifier:
- Line 27: `Delta: -3.9 s / ~3.0% reclaim`
- Line 44: `Cumulative: -3.9 s median wall (127.8 → 123.9 s)`
- Line 56: `Honest cumulative reclaim called out as -3.9 s median wall`
- Line 83: `~3.9 s suite-level reclaim from 80 patches collapsed`

Audit commit `7f94a0c94` did not touch phase_5_checklist.md. These notes are the historical close-out record, so casual readers will see 3.9s as the definitive result. While less severe than the reference-document stale claims (FND-327-01/02), this contributes to the same pattern: a reader who starts at the checklist gets an incorrect conclusion.

`phase_1_checklist.md:92` also carries `~3.9 s wall reclaim` without qualification.

**Recommendation:** Append `(retracted per audit S2.7; see findings/runtime_delta.md)` to each uncaveated -3.9s mention in phase_5_checklist.md and phase_1_checklist.md. Or better: replace the quantitative claim with a pointer to `runtime_delta.md` and its verified file-level deltas.

---

## Additional Observations (not findings)

- **Protocol/Factory/Mock method alignment:** All 8 `make_*` methods match between `StrategyScreenComposition` (Protocol), `StrategyScreenCompositionFactory`, and `MockStrategyScreenComposition`. Signature shapes are structurally compatible. No missing or extra methods. The Factory correctly pulls `screen._facade` and `screen.input_mapper` for sub-objects that need them (fleet_ops, colonization, superweapons, input_handler). The Mock correctly ignores those dependencies (it always returns pre-stored mocks).

- **Pattern §32 documentation:** `docs/02_PATTERNS.md:1676-1731` is accurate and well cross-referenced. The "Why" section's claim that pre-PROJ-327 tests used `patch.object(screen, '_init_layout')`-style private patching is slightly inaccurate (Phase 4 Task 4.1 audited and confirmed zero `_init_layout` patches existed; the brittleness was the `__init__` monkey-patch). But the pattern document correctly focuses on the benefit ("Editing 50+ tests") rather than the specific patch style.

- **Return-type annotations:** All public methods on `StrategyScreenComposition` (Protocol) and `StrategyScreenCompositionFactory` carry return-type annotations. `MockStrategyScreenComposition.make_*` methods return `Any` rather than the specific sub-object types — acceptable for a mock fixture. `populate()` declares `-> None`. All convention-compliant.

- **LOC ceiling:** `strategy_screen_composition.py` (114 LOC), `tests/fixtures/strategy_screen_composition.py` (146 LOC), `test_strategy_screen_composition.py` (124 LOC) — all well under 500.

---

## Overall Verdict

**PROJ-327: Partial remediation — two critical stale-claim documents remain uncorrected.**

The audit S2.7 retraction correctly landed in `runtime_delta.md` (headline + analysis section) and `plan.md` (Phase 5 close-out text + verification checkbox). However, the remediation stopped short of two critical reference documents:

1. **`decisions.md` scorecard** — The canonical performance summary still reports 3.9s as the Phase 1 wall-clock delta with no retraction qualifier (FND-327-01). This is the primary document a future project planner would consult, and it's wrong.

2. **`findings/virtual_table_runtime.md`** — The per-phase runtime detail document still asserts the 3.9s claim with the disproven amplification mechanism and carries no retraction mention (FND-327-02). If a future agent reads only this file (plausible — it's the specific Phase 1 delta document), they'd reach the wrong conclusion.

The Compositional Construction pattern (Question 3) is well-designed with accurate Protocol/Factory alignment. The Mock fixture has a documented-but-misaligned idempotency check (FND-327-03 — the docs claim it catches scenario X but it catches scenario Y) and lacks a structural conformance test (FND-327-04). Neither issue is a production behavior regression. Both are test-infrastructure accuracy gaps that reduce future maintainer confidence in the seam.
