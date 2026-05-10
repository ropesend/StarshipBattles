# Phase 3 Deferrals Report — PROJ-393 Review

**Reviewer:** OpenCode (audit agent)
**Date:** 2026-05-09
**Scope:** Phase 3 Tasks 3.2 (fleet_id), 3.5 (BattleScreen vars), 3.6 (asset scan)

---

## Finding 1 — CRITICAL: BattleScreen Combat Lab vars (Task 3.5) — 4 of 6 vars are dead code, not "actively used"

**File:** `game/ui/screens/battle_screen.py:117-125`
**Severity:** CRITICAL

The PROJ-393 agent deferred removal of 5 of 6 Combat Lab instance vars, claiming they are "actively used." This assessment is **wrong for 4 of them**. Only `headless_mode` and `headless_start_time` have legitimate runtime paths. The remaining vars (`test_mode`, `test_scenario`, `test_completed`, `test_tick_count`) are dead code in production.

### Evidence — dead code analysis

| Var | Init value | Set to non-default in production? | Read sites that execute? | Verdict |
|-----|-----------|-----------------------------------|-------------------------|---------|
| `self.headless_mode` | `False` | YES — `start_battle()` line 157: `self.headless_mode = config.headless` | `battle_screen.py:302` (update branch), `run_loop.py:216` (draw skip) | **ACTIVE** |
| `self.headless_start_time` | `None` | Set to `None` only; only read at line 685 within `if self.test_mode:` guard which is always False | Dead | **DEAD** |
| `self.test_mode` | `False` | **NEVER** set to `True` in production. Only in test file `tests/unit/test_lab/test_visual_run.py:452` | `battle_screen.py:490` (`is_battle_over` dead branch), `battle_screen.py:679` (`print_headless_summary` dead branch) | **DEAD** |
| `self.test_scenario` | `None` | **NEVER** set to non-None in production. Cleared at `test_lab/screen.py:362`. The `_switch_to_battle` rewrite (PROJ-270) no longer sets it. | `test_lab/screen.py:335` always reads `None`; `if scenario and ...` at line 337 never executes | **DEAD** |
| `self.test_tick_count` | `0` | **NEVER** incremented in production. Only in test file `test_visual_run.py:515` | `test_lab/screen.py:346` never reached (scenario is None); `battle_screen.py:490` guarded by `test_mode` which is False | **DEAD** |
| `self.test_completed` | `False` | **NEVER** set to `True` in production. Cleared at `test_lab/screen.py:360` | `test_lab/screen.py:337` never reached (scenario is None) | **DEAD** |

### Why this matters

1. The `is_battle_over()` check at `battle_screen.py:490` is a dead branch — the only live battle-over detection is `self._battle_service.is_battle_over()` at line 492.
2. The `print_headless_summary()` guard at `battle_screen.py:679` is a dead branch — headless test mode bypasses this completely.
3. The visual test results capture in `test_lab/screen.py:334-356` (`reset_selection`) is dead — `test_scenario` is always `None`, so test results are never stored from visual test runs via this code path.

The original legacy audit (`LEG-03-023`, see `Projects/active_projects/PROJ-383/findings/bundling_decisions.md:37`) correctly identified these as reclaimable. The PROJ-270 skeptic audit (`unified_entry_exit_skeptic.md:86`) also flagged them: *"this is the exact shape of a PROJ-270 legacy-compat shim."* The PROJ-393 deferral is a **post-hoc rationalization** — headless_mode was the only genuine active runtime feature among these vars.

### Recommendation

Delete `test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, and `headless_start_time` from `battle_screen.py:117-125`. Fix the `is_battle_over()` method (line 487-492) to remove the dead branch. Fix `print_headless_summary()` (line 677-687) to remove the dead guard. Fix `test_lab/screen.py:334-356` to remove the dead result-capture block. The test file `tests/unit/test_lab/test_visual_run.py` (lines 452-453, 480-485, 514-520) may need corresponding updates.

---

## Finding 2 — MAJOR: fleet_id partial fix (Task 3.2) — tag removal reduces clarity without fixing design

**File:** `game/strategy/engine/commands/__init__.py:97-108`
**Severity:** MAJOR

The PROJ-393 agent removed the "Kept for backward compat" tag from `ClearOrdersCommand.fleet_id` and replaced it with a claim that `fleet_id` is "canonical." This is a **cosmetic-only change** that introduces confusion because:

### Evidence

1. **`DeployFleetCommand` and `TransferPassengersCommand` do not exist** in the codebase. The PROJ-393 analysis references these as if they're live commands needing review, but neither exists. They may be pre-rename artifacts.

2. **`ClearOrdersCommand` has exactly 1 production caller** (`game/ui/screens/strategy_windows/orders_window_ctrl.py:73`), not "~20." The "~20" figure in the docstring appears to conflate all commands that happen to have a `fleet_id` field across the entire commands file.

3. **The `entity_id`/`entity_type` pattern already exists** in the same file for construction queue commands (lines 327-328, 349-350, 369-370, 394-395). These use `entity_id: int` + `entity_type: BuildEntityType`. This is the pattern the docstring says "a future project may unify on."

4. **`ClearOrdersCommand` sits in a confused state**: it has `fleet_id: int` AND `entity_type: str = "fleet"`, but the handler (`order_queue.py:97`) only uses `cmd.fleet_id`. The `entity_type` field exists but is a dead weight — the handler never branches on it.

5. **Sibling commands in the same file are inconsistent**:
   - `DeleteOrderCommand` (line 286-293): `fleet_id + entity_type` (same pattern)
   - `ReorderOrderCommand` (line 296-305): `fleet_id + entity_type` (same pattern)  
   - `AddToConstructionQueueCommand` (line 312-333): `entity_id + entity_type` (modern pattern)
   - `RemoveFromConstructionQueueCommand` (line 336-352): `entity_id + entity_type` (modern pattern)

### Why the tag removal makes things worse

The old tag warned developers: "this field is kept for backward compat, don't rely on it." The new tag says: "this IS the canonical field." But in the same file, half the commands use `entity_id` (canonical) and half use `fleet_id` ("also canonical"). A developer reading this would reasonably ask:
- If `fleet_id` is canonical, why does `entity_type` exist?
- If `entity_type` is for future planet support, why doesn't the handler switch on it?
- Why do construction queue commands use `entity_id` while order queue commands use `fleet_id`?

This is NOT an AGENTS.md Rule 3 violation (no new shim/fallback was introduced), but it IS a **regression in documentation honesty**. The old warning gave truthful context; the new label implies stability that doesn't exist.

### Recommendation

Revert the docstring change to the `ClearOrdersCommand` class. Either restore the "Kept for backward compat" tag, or defer the file entirely to a sibling project that actually migrates to `entity_id`/`entity_type` across all affected commands. Do not rename a temporary field as "canonical" when the migration plan named in the same docstring hasn't started.

---

## Finding 3 — MAJOR: `~20 call sites` claim in docstring is unverified and inaccurate

**File:** `game/strategy/engine/commands/__init__.py:105`
**Severity:** MAJOR

The `ClearOrdersCommand` docstring claims *"A future project may unify on entity_id/entity_type and migrate the ~20 call sites."* Spotted counts:

| Command | Production call sites using `fleet_id=` |
|---------|----------------------------------------|
| `ClearOrdersCommand` | 1 (`orders_window_ctrl.py:73`) |
| `DeleteOrderCommand` | 1 (`orders_window_ctrl.py:78`) |
| `ReorderOrderCommand` | 1 (`orders_window_ctrl.py:87`) |
| DeployFleetCommand | **Does not exist** |
| TransferPassengersCommand | **Does not exist** |

The handler code (`order_queue.py:85-105`) reads `cmd.fleet_id` and resolves the fleet — the `entity_type` field is never evaluated. The "~20" number appears to count all commands with a `fleet_id` field, not just `ClearOrdersCommand`. This inflates the perceived migration cost and may discourage cleanup.

### Recommendation

Replace the "~20 call sites" claim with an accurate count, or remove the speculative number entirely. Future-proof: "The 1 caller of ClearOrdersCommand, 1 of DeleteOrderCommand, and 1 of ReorderOrderCommand."

---

## Finding 4 — MINOR: _LEGACY_PATTERN deletion (Task 3.6) — correct conclusion, incomplete directory scan

**File:** `game/ui/renderer/sprites.py:11-12` (line references post-deletion)
**Severity:** MINOR

### What was verified

1. `_LEGACY_PATTERN = re.compile(r'Comp_(\d+)\.\w+$')` — **confirmed deleted**. Zero references remain in the codebase.
2. The `else` branch that tried the legacy pattern was also deleted from `_load_from_directory` (lines 72-75 in old code, now gone).
3. The legacy pattern matched bare `Comp_001.bmp` filenames. No such files exist in any of the 6 resolution subdirectories under `assets/Images/Components/` — all 3,234 files follow the canonical `{resolution}Portrait_Comp_{number}.png` pattern.
4. No `Comp_NNN.` files were found across `assets/`, `data/` (no image assets there), or `tests/fixtures/`.

### Unscanned directories

The following asset subdirectories contain images/sprites but were not explicitly scanned:
- `assets/Images/altcomponents/` (unknown filename convention)
- `assets/Images/Cursor/` (cursor images)
- `assets/Images/Flags/` (flag images)
- `assets/Images/Modifier Icons/`
- `assets/Images/Race Portraits/`
- `assets/Images/Resource Icons/`
- `assets/Images/Resource Portraits/`
- `assets/Images/Stellar Objects/` (multiple subdirs)
- `assets/ShipThemes/` (skin/model images)

This is a **MINOR gap** because the `_LEGACY_PATTERN` regex was only used in `SpriteManager._load_from_directory`, which only loads from the Components directories (resolved via `Paths.COMPONENTS_64_DIR`). The other asset directories are loaded by different managers and would never have been matched by this pattern. The conclusion (pattern is dead) remains correct.

### Recommendation

The deletion itself is correct and safe. No further action needed.

---

## Finding 5 — INFO: `Entity_type` fields are dead weight on ClearOrders/DeleteOrder/ReorderOrder

**File:** `game/strategy/engine/commands/__init__.py:108,293,305`
**Severity:** INFO

All three order-queue commands (`ClearOrdersCommand`, `DeleteOrderCommand`, `ReorderOrderCommand`) carry an `entity_type: str = "fleet"` field with docstring comments like `# "fleet" or "planet" (handler uses fleet path only)`. The handlers use only `cmd.fleet_id` — `entity_type` is never evaluated for branching. This is dead metadata that existed from the PROJ-238 rename (when these were `ClearFleetOrdersCommand` etc.) but was never wired into planet-handling logic.

The PROJ-393 docstring (line 99-106) acknowledges this: "the handler currently only resolves fleet_id." This is a genuine half-baked field, not a compat shim — but it adds noise.

---

## Findings Summary

| # | Severity | Area | File:Line | Summary |
|---|----------|------|-----------|---------|
| 1 | CRITICAL | Task 3.5 | `battle_screen.py:117-125` | 4 of 6 Combat Lab vars are dead code; deferral was a misread |
| 2 | MAJOR | Task 3.2 | `commands/__init__.py:99-106` | Tag removal reduces clarity; doc now labels a transitional field as "canonical" |
| 3 | MAJOR | Task 3.2 | `commands/__init__.py:105` | "~20 call sites" is inaccurate — actual count is 1 per command |
| 4 | MINOR | Task 3.6 | `sprites.py` (post-deletion) | `_LEGACY_PATTERN` deletion was correct but asset scan incomplete |
| 5 | INFO | Task 3.2 | `commands/__init__.py:108,293,305` | `entity_type` field is dead weight on 3 order-queue commands |
