# PROJ-456 Phase 3: BattleSetupState `side_0` / `side_1` cluster (2 production + 5 test files)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-456 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** None (write scope disjoint from Phases 1-2).
**Review Mode:** standard
**Objective:** Retire the `BattleSetupState.side_0` / `side_1` read/write property pair surviving from PROJ-275 Phase 4+5 N-team migration. Sweep 77 references across 5 test files + 2 production files; replace with `state.sides[i]` / `state.get_side(team_id)`. Then delete the property/setter block.

**Source-of-truth finding:** F-C-001 in [`findings/PROJ-456_findings.md`](findings/PROJ-456_findings.md).

**Caller surface (verified 2026-05-19):**

| File | Type | Refs |
|------|------|------|
| `game/ui/screens/battle_setup_state.py` | Production | self-defines + properties (delete block) |
| `game/ui/screens/battle_setup/controller.py` | Production | (count via grep before starting) |
| `tests/unit/ui/screens/test_battle_setup_state.py` | Test | 13 |
| `tests/unit/ui/screens/battle_setup/test_controller.py` | Test | 37 |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` | Test | 22 |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py` | Test | 5 |
| `tests/integration/strategy/combat/test_suppressor_effects.py` | Test | 4 |

Total: 77 test refs + production reads to migrate.

---

## Tasks

### Task 3.1: Audit migration pattern [Simple]
**Files:** `game/ui/screens/battle_setup_state.py:172-192`, `game/ui/screens/battle_setup/controller.py`
**Tests:** none yet — read-only audit.

- [x] Read `BattleSetupState.side_0` / `side_1` property + setter block at battle_setup_state.py:172-192.
- [x] Read `BattleSetupState.sides` (the canonical list at line ~155 — find via `rg`) and `BattleSetupState.get_side(team_id)` accessor (line ~196).
- [x] Read `battle_setup/controller.py` and use `rg -n "\.side_0|\.side_1" game/ui/screens/battle_setup/controller.py` to find call sites. Note each read-vs-write to plan the migration.
- [x] Decide per call site: prefer `state.get_side(team_id)` when the test/code is doing team-id-oriented work (the natural read), use `state.sides[i]` (literal index) when the test is explicitly two-side-and-array-positional.

### Task 3.2: Migrate production callers [Simple]
**File:** `game/ui/screens/battle_setup/controller.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py -q`

- [x] **RED**: For each `.side_0` / `.side_1` read or write in `controller.py`, replace with `state.sides[0]` / `state.sides[1]` (or `state.get_side(team_id=...)` if the team-id index is the natural read). Confirm the test_controller suite still has all 37 refs to migrate (the test changes come in Task 3.3).
- [x] Run targeted tests; expect failures until Task 3.3 lands the test-side migrations. If tests pass already, great — the production migration was self-contained.

### Task 3.3: Migrate test callers [Simple]
**Files:** the 5 test files listed above.
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py tests/unit/ui/screens/battle_setup/test_controller.py tests/unit/ui/screens/battle_setup/test_spec_compiler.py tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py tests/integration/strategy/combat/test_suppressor_effects.py -q`

- [x] `tests/unit/ui/screens/test_battle_setup_state.py` (13 refs) — mechanical sweep `state.side_0` → `state.sides[0]`, `state.side_1` → `state.sides[1]` (and write variants). Run test file; assertions hold.
- [x] `tests/unit/ui/screens/battle_setup/test_controller.py` (37 refs) — same pattern. Note: if any test asserts on the property setter triggering side-effects on the canonical list, those should still pass (the setter and the array index point to the same slot per the source's `self.sides[0] = value` semantic).
- [x] `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` (22 refs) — same pattern.
- [x] `tests/unit/ui/screens/battle_setup/test_spec_compiler_formation.py` (5 refs) — same pattern.
- [x] `tests/integration/strategy/combat/test_suppressor_effects.py` (4 refs) — same pattern.
- [x] Run all 5 test files; expect green.
- [x] **Verify (PowerShell-safe)**: `rg -n "\.side_0|\.side_1" tests` returns 0 hits.
- [x] **Verify production (PowerShell-safe)**: `rg -n "\.side_0|\.side_1" game --glob="!battle_setup_state.py"` returns 0 hits.

### Task 3.4: Delete the shim block [Simple]
**File:** `game/ui/screens/battle_setup_state.py:172-192`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_state.py -q`

- [x] **GREEN**: Delete the comment block at lines 172-176 and the property/setter pair at 178-192 (~21 lines total).
- [x] Run targeted tests; sharded suite green.
- [x] **Verify (PowerShell-safe)**: `rg -n "\.side_0|\.side_1" game tests` returns 0 hits (the property block is the only remaining match before this step).

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [x] F-C-001 flipped to `Status: resolved` in `findings/PROJ-456_findings.md`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-456 3` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 4.
- [x] Commit message: `PROJ-456 Phase 3: retire BattleSetupState side_0/side_1 shims (F-C-001; 81 refs migrated across 5 test + 2 prod files)`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
