# Phase 6: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remediate 2 small in-scope findings from `findings/audit_verification.md`. Pure text edits; no test changes needed.

Audit source: `AgentCoordination/Scratchpad/Consult/20260523T182413Z_audit-PROJ-499/response.md`
Verification: `Projects/active_projects/PROJ-499/findings/audit_verification.md`

---

## Tasks

### Task 6.1: Add size-modifier scaling clarification (F2) [Simple]
**Files:**
- `Projects/active_projects/PROJ-499/phase_3_checklist.md` (Task 3.3 Notes section, ~line 42-44)
- `Projects/active_projects/PROJ-499/findings/source_review.md` (Section 4, ~line 165-170)
**Tests:** N/A — pure text edits.

Codex Finding F2: The "all new values are 1.0/0.0" wording is inaccurate for the standard_engine_size_* family. simple_size_mount multiplies all `_mult` stats (including the newly-added `launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`) by the size factor. So size_16 adds them at 16.0, size_8 at 8.0, etc. shield_bonus_add (the `_add` key) stays at 0.0 across all files. The diff is still strictly additive (no value drift on pre-existing keys), so the broader conclusion holds; only the wording is imprecise.

- [x] Update `phase_3_checklist.md` Task 3.3 Notes (around line 44, the "additive only: `launch_rate_mult=1.0...` added" lines) to add a clarification: the spot-check files (which were no_modifiers / single-effect baselines) show defaults; the standard_engine_size_* family shows the same keys scaled by simple_size_mount (e.g., size_16 → 16.0). Both are correct additive behavior.
- [x] Update `findings/source_review.md` Section 4 (around line 165-170, the "Implications for Phase 3" section) to add the same clarification: per-file diff bounded to additive `component.stats` keys; values follow the modifier's stat-key derivation rules (defaults from `create_default_stats_dict()` if no modifier touches the key; scaled by simple_size_mount on size_* baselines; etc.).
- [x] Do NOT alter the substantive conclusion: still strictly additive, still no orchestrator-attention trigger.

**Notes:**
- `phase_3_checklist.md` Task 3.2 Notes (the spot-check block — line numbering meant Task 3.2 since 3.3 is just the sharded run; the audit's "Task 3.3 Notes" pointer was to the section about spot-check delta wording, which is Task 3.2's "Notes" body) gained a "WORDING PRECISION (Phase 6 audit F2 remediation)" bullet explaining the size_* family lands the 3 `_mult` keys at the size factor (not 1.0) because `simple_size_mount` multiplies all `_mult` stats, while `shield_bonus_add` stays 0.0 because no modifier touches the `_add` key.
- `findings/source_review.md` Section 4 ("Implications for Phase 3") rewritten to drop the literal "1.0/1.0/1.0/0.0" enumeration and instead describe the per-value content as following the modifier's stat-key derivation rules (defaults from `create_default_stats_dict()` if no modifier touches the key; scaled by `simple_size_mount` on size_* baselines). The substantive "additive only, no value drift on pre-existing keys" claim is preserved.
- No conclusion altered: still strictly additive, no orchestrator-attention trigger.

### Task 6.2: Fix tests/README.md stale line-span reference (F7) [Simple]
**File:** `tests/README.md`
**Tests:** N/A

Codex Finding F7: README at line 555 references `conftest.py:201-217` but `fail_missing_baseline()` currently lives at `conftest.py:210-226`. Trivial doc fix.

- [x] Open `tests/README.md` around line 552-563
- [x] Replace `conftest.py:201-217` with `conftest.py:210-226`
- [x] Verify by reading the surrounding context — no other line-span references are stale

**Notes:**
- `tests/README.md:555` updated: `conftest.py:201-217` → `conftest.py:210-226`. Confirmed against the current source: `fail_missing_baseline()` starts at `tests/regression/modifier_ability_snapshots/conftest.py:210` (the `def` line) and ends at `:226` (the closing `)` of the `pytest.fail(...)` call).
- `Grep conftest\.py:\d+-\d+` over `tests/README.md` returns exactly the one (now-corrected) match. No other stale line spans to fix in the surrounding section.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `validate_phase.py PROJ-499 6` PASSED
- [x] `validate_close_ready.py PROJ-499` PASSED (still)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to reflect project Done
