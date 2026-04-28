# PROJ-317: PROJ-315 Remediation — Damage Display Correctness and Audit Readiness

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-317` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-317 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Correctness fixes (R1, R2, R3, R4) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Hygiene (R5, R6) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Test seam strengthen (R7) | Deferred | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-28
**Active Phase:** Complete - awaiting user verification (Phase 3 deferred)
**Last Action:** Implemented R1-R4 correctness fixes, R5-R6 hygiene fixes, and verified full sharded suite: 16004 passed / 0 failed.
**Next Action:** User to review PROJ-317 remediation and manually smoke Fleet Report component status on a shared-component ship.
**Blockers:** None

## Overview

Five post-merge audit findings against the PROJ-315 implementation,
all independently re-verified against `main` HEAD `348bceef0` on
2026-04-28. The shipped code passes its 35 PROJ-315 tests but the test
seam asserts on `_proj315_color` / `_proj315_strike` private attributes,
not rendered output. Several visible-to-the-player defects sailed
through:

- **Damage tier colours are computed but never applied to the rendered
  label** — every instance row shows in the default theme colour
  regardless of damage state. (R2)
- **Cross-layer instance-index counter resets per layer** in
  `iter_all_components_by_layer`, but the authoritative
  `_build_full_hp_components_from_design` uses a ship-wide counter.
  Ships with the same `component_id` in multiple layers (e.g.
  `qs_battleship` has `battery` in CORE+INNER) silently alias the
  second-layer instance state to the first-layer key. (R1)
- **Threshold lookup imports `get_default_registry_provider` from
  `game.context`** where it doesn't exist (lives in
  `game.core.registry`) and calls a non-existent
  `get_component_registry()` method. The broad-catch swallows both
  errors and production uses
  `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` (0.5) for every
  component. (R3)
- **Missing-state fallback emits `current_hp = max_hp = 0`** when a
  component has no `ComponentState` entry, rendering as "100% of 0 HP".
  The Phase 1 checklist required a registry-derived fallback. (R4)
- **Project metadata blocks the audit gate** —
  `validate_audit_ready.py PROJ-315` reports 4 errors because the
  `## Phases` section bodies in `plan.md` still say "Not Started" and
  the `Blockers:` field misparses. (R5)

Plus two minor hygiene items (R6 trailing whitespace, R7 test-seam
strengthen) and one deferred convention note (R8 — already in PROJ-315
`decisions.md` for a future PROJ-309 sweep).

## Goals

- Per-component-instance state lookup is correct for ships with shared
  `component_id` across layers — keys match the canonical scheme used
  to seed `ComponentState`.
- Damage-tier colours visibly affect the rendered label text on the
  COMPONENT STATUS panel (verified by reading rendered output, not
  tagged test attributes).
- Per-component `damage_threshold` from `data/components.json` (and
  any modded threshold) flows through the panel; UI tests run cleanly
  without `ApplicationContext` and fall back to the project default.
- A ship loaded from a legacy save with missing `ComponentState` keys
  renders with registry-derived full HP, never "100% of 0 HP". A
  registry-unaware caller skips the instance.
- `validate_audit_ready.py PROJ-315` and `validate_audit_ready.py
  PROJ-317` both exit 0.
- `git diff --check` clean across the project's commit chain.
- (Optional) Test seam upgraded so future colour-rendering regressions
  are caught.

## Scope

**In:**
- Fix R1: lift `per_id_index` out of the layer loop in
  `iter_all_components_by_layer`.
- Fix R2: apply chosen colour to the rendered label via pygame_gui's
  rich-text wrap (preferred) or `set_text_colour()` API; tint the
  strikethrough overlay to match the chosen tier.
- Fix R3: correct the threshold-lookup import path and method name;
  optionally narrow the broad-catch.
- Fix R4: registry-derived `max_hp` fallback for missing
  `ComponentState`; skip the instance entirely on dual-miss.
- Fix R5: edit `Projects/active_projects/PROJ-315/plan.md` lines 25,
  241, 248, 254.
- Fix R6: trim EOF whitespace in
  `tests/unit/ui/panels/test_ship_detail_panel.py`.
- Fix R7 (Phase 3, optional): replace `_proj315_color` /
  `_proj315_strike` test reads with assertions on rendered output.
- New regression tests for each defect — must fail pre-fix and pass
  post-fix.

**Out:**
- R8 (`ship_detail_panel.py` size split). Deferred to a future
  PROJ-309 sweep per existing `decisions.md` row 32.
- Any change to the COMPONENT STATUS visual layout (column order,
  group row format, chevron characters). The defects are
  correctness, not redesign.
- Facade DTO + slice query (already out of scope per PROJ-315
  decisions).

## Key Files

| Component | File Path | Notes |
|-----------|-----------|-------|
| Iterator with R1 + R4 defects | [game/strategy/data/ship_instance.py](../../../game/strategy/data/ship_instance.py) | `iter_all_components_by_layer` at lines 573–604; authoritative scheme at lines 45–94 (`_build_full_hp_components_from_design`). |
| Panel with R2 + R3 defects | [game/ui/panels/ship_detail_panel.py](../../../game/ui/panels/ship_detail_panel.py) | `_resolve_threshold_lookup` at 443–461; `_build_instance_row` at 556–596; `_apply_strikethrough` at 598–625. |
| PROJ-315 audit-blocker text | [Projects/active_projects/PROJ-315/plan.md](../../active_projects/PROJ-315/plan.md) | Lines 25 (Blockers), 241 / 248 / 254 (Phase status bodies). |
| Test file with EOF whitespace | [tests/unit/ui/panels/test_ship_detail_panel.py](../../../tests/unit/ui/panels/test_ship_detail_panel.py) | Two trailing CRLF blank lines at line 980. |
| Registry helper home | [game/core/registry.py](../../../game/core/registry.py) | `get_default_registry_provider` at line 456; `DefaultRegistryProvider` at 356 with `get_components()` method. |
| Strategy data tests | [tests/unit/strategy/test_ship_instance_damage.py](../../../tests/unit/strategy/test_ship_instance_damage.py) | Existing iterator tests; add R1 + R4 regressions. |
| Widget tests | [tests/unit/ui/panels/test_ship_detail_panel.py](../../../tests/unit/ui/panels/test_ship_detail_panel.py) | Existing widget tests use `_proj315_*` seam; add R2 + R3 regressions; Phase 3 retires the seam. |
| Audit script | [Projects/scripts/validate_audit_ready.py](../../scripts/validate_audit_ready.py) | Verifies phase-row text and `Blockers:` field — pin compliance for both PROJ-315 and PROJ-317. |
| Origin findings | [findings/remediation_audit_2026-04-28.md](findings/remediation_audit_2026-04-28.md) | Independent agent's audit + initial remediation plan. |

## Related Documents
- [design.md](design.md) — Architecture analysis and design rationale.
- [decisions.md](decisions.md) — Decisions log.
- [findings/remediation_audit_2026-04-28.md](findings/remediation_audit_2026-04-28.md) — Source of the eight findings.

## Initial Analysis

### How the audit findings were verified

Each claim was re-checked against source HEAD `348bceef0`:
1. **R1 (cross-layer collision):** read both
   `iter_all_components_by_layer` (line 573) and
   `_build_full_hp_components_from_design` (line 45). Confirmed
   `per_id_index = {}` is per-layer in the former and ship-wide in
   the latter. The scheme divergence corrupts state lookup whenever a
   `component_id` appears in more than one layer.
2. **R2 (colours not rendered):** read `_build_instance_row` lines
   556–596. The chosen `color` tuple is stored on the label as
   `label._proj315_color` (test attribute) but never set via
   `UILabel.set_text_colour()`, HTML wrap, or theme override. The
   strike overlay is rendered but uses hard-coded
   `(220, 220, 220)`.
3. **R3 (threshold lookup wiring):** `from game.context import
   get_default_registry_provider` — checked `game/context.py`, the
   symbol does not exist there. `DefaultRegistryProvider` in
   `game/core/registry.py` exposes `get_components()` (returns dict),
   not `get_component_registry()`. Both errors silently swallowed by
   `except Exception`.
4. **R4 (missing-state fallback):** lines 591–594 emit `max_hp = 0`,
   `current_hp = 0`. Phase 1 checklist Task 1.2 explicitly required:
   "fall back to a registry lookup if available, else `0`". Registry
   path was never written.
5. **R5 (audit gate):** ran `validate_audit_ready.py PROJ-315` —
   reports 4 errors against `plan.md` lines 25, 241, 248, 254.
6. **R6 (whitespace):** ran `git diff --check e26f00f74..348bceef0`
   — `tests/unit/ui/panels/test_ship_detail_panel.py:980: new blank
   line at EOF`. `cat -A` showed two `^M$` blank lines at file end.

## Risks Identified

1. **R1 ordering risk.** Lifting the counter out of the layer loop
   only matches the authoritative scheme if both iterators visit
   layers in the same order. The authoritative path uses
   `ship.layers.items()` (Ship object's layer dict);
   `iter_all_components_by_layer` uses `design_data['layers'].items()`
   (raw dict from the design JSON). Pin a regression test that
   compares the key sets across both paths for a representative
   shared-component design.
2. **R2 rendering API uncertainty.** The fix-of-choice depends on
   whether pygame_gui's `UILabel` accepts `<font color>` rich text in
   this codebase's version. If not, fall back to `set_text_colour()`
   or `UITextBox`. Spike before committing to one path.
3. **R7 risk.** Replacing the `_proj315_*` seam with rendered-output
   reads may reveal that pygame_gui's surface state is hard to
   inspect without pixel sampling. If pixel sampling proves brittle,
   fall back to a documented "intent + minimal render check" pattern
   that avoids the false-positive R2 hid behind.
4. **PROJ-313 / PROJ-314 / PROJ-316 parallel run.** This project
   touches `ship_instance.py`, `ship_detail_panel.py`, and one
   PROJ-315 plan/test file. Cross-checked against active project
   manifests:
   - PROJ-313 modal base class — touches `fleet_report_window.py`
     (R7's parent), no overlap with our files.
   - PROJ-314 ship theme schema — no overlap.
   - PROJ-316 (PROJ-313 remediation) — no overlap.
   Safe to run in parallel.

---

## Phases

### Phase 1: Correctness fixes (R1 + R2 + R3 + R4) [Medium]
**Objective:** Eliminate the four functional defects. Each defect
ships with a regression test that fails pre-fix and passes post-fix.
Block on full sharded suite green before flipping to Phase 2.
**Status:** Complete

### Phase 2: Hygiene (R5 + R6) [Simple]
**Objective:** Make `validate_audit_ready.py PROJ-315` and
`validate_audit_ready.py PROJ-317` pass. Trim EOF whitespace.
**Status:** Complete

### Phase 3: Test seam strengthen (R7) [Medium] (optional)
**Objective:** Retire `_proj315_color` / `_proj315_strike` private
test attributes; assert against rendered output. Optional — can ship
later as its own follow-up if Phase 1+2 are green.
**Status:** Deferred

---

## Verification Checklist

### Project Start (REQUIRED — done as part of planning)
- [x] Read PROJ-315 audit findings.
- [x] Re-verify each claim against current `main` source.
- [x] Establish current sharded baseline: 15994 / 15994 passing.

### After Each Phase
- [x] Run affected pytest suites - all affected tests pass.
- [x] Phase 1 specifically: full sharded run green.
- [x] Update Current State block.

### Final Verification
- [x] R1 regression: cross-layer iterator key set equals
  `_build_full_hp_components_from_design` key set on a
  shared-component design fixture (e.g. `qs_battleship`).
- [x] R2 regression: damage-tier colour visible in rendered output;
  test does NOT rely on `_proj315_color`.
- [x] R3 regression: threshold lookup returns registry-stored value
  for a known component, default for unknown, default for the
  no-registry path.
- [x] R4 regression: missing-state instance gets registry-derived
  full HP; dual-miss skips the instance entirely.
- [x] R5: `python Projects/scripts/validate_audit_ready.py PROJ-315`
  exits 0.
- [x] R6: `git diff --check <pre-PROJ-317>..HEAD` clean.
- [ ] (R7 if shipped) Widget tests no longer reference
  `_proj315_color` or `_proj315_strike`.
- [ ] Manual smoke: open Fleet Report on a ship with a shared
  component across layers (e.g. `qs_battleship` with `battery` in
  CORE+INNER); damage one battery in the inner layer via save edit;
  confirm the panel shows damage on the correct layer's instance —
  not aliased to the first-layer battery.
- [x] Run `python Tools/test_sharded/test_sharded.py` - full suite
  green; baseline 15994 + new R1–R4 (and R7 if shipped) tests, 0
  failed.

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 0 | 2026-04-28 | Independent agent flagged R1–R8 against PROJ-315 post-merge | Verified all five P1/P2 claims; spawned PROJ-317 |
| 1 | 2026-04-28 | R1-R6 implemented and verified; Phase 3 deferred | Full sharded suite green: 16004 passed / 0 failed. PROJ-315 and PROJ-317 audit-readiness scripts exit 0. |

## Completion Checklist
- [x] Phase 1 complete.
- [x] Phase 2 complete.
- [x] Phase 3 complete (or explicitly deferred).
- [x] All new regression tests passing.
- [ ] User verified.
