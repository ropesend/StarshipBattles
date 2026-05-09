# Rule 3 Compliance Report — PROJ-393 Deferrals & Pre-existing Pytest Errors

**Review scope:** Focus Area 6 (AGENTS.md Rule 3 compliance) + Focus Area 7 (4 pre-existing pytest-collection errors)
**Branch:** `feat/03c-phase-aware-execution`
**PROJ-393 commits:** 6 commits (a23948b9d through 88a2342ef)

---

## Summary

| Severity | Count | Theme |
|----------|-------|-------|
| MAJOR | 2 | entity_type dead-weight; misleading NOQA comment left uncleaned |
| MINOR | 2 | view=None branch (acknowledged shim); BattleScreen dual-role design |
| INFO | 1 | 4 pytest collection errors confirmed orthogonal |

**Bottom line:** The 3 deferrals (Tasks 3.2, 3.3, 3.5) were scope-managed correctly — none are "compatibility shims in disguise" where real dead code was rationalized away. However, 2 things were missed that should have been cleaned given PROJ-393's stated purpose of "comment cleanups": the misleading NOQA comment on BattleScreen, and unused `entity_type` fields on 3 commands.

---

## MAJOR Findings

### MAJOR-1: `entity_type` dead-weight fields on DeleteOrderCommand and ReorderOrderCommand were not cleaned

**Files:** `game/strategy/engine/commands/__init__.py:293` (DeleteOrderCommand), `:305` (ReorderOrderCommand)
**Also affected:** `:108` (ClearOrdersCommand — the tag was cleaned but the field stayed)

**What was found:**

The PROJ-393 verification report correctly identified that `entity_id` does not exist on any of these 3 command DTOs, and that `fleet_id` IS the canonical field used by all handlers. The implementation (commit 8fa9887d3) removed the misleading `# Kept for backward compat; use entity_id for new code` inline comment from `ClearOrdersCommand` and updated its docstring.

However, the `entity_type: str = "fleet"` **default field** remains on all 3 commands:

| Command | Line | field |
|---------|------|-------|
| `ClearOrdersCommand` | 108 | `entity_type: str = "fleet"  # "fleet" or "planet" (handler uses fleet path only)` |
| `DeleteOrderCommand` | 293 | `entity_type: str = "fleet"` |
| `ReorderOrderCommand` | 305 | `entity_type: str = "fleet"` |

**Evidence that handlers never use `entity_type`:**

- `ClearOrdersCommandHandler.execute()` at `handlers/order_queue.py:94-105` — uses only `cmd.fleet_id` via `self._resolve_player_fleet(session, cmd.fleet_id)`
- `DeleteOrderCommandHandler.execute()` at `handlers/order_queue.py:189-207` — uses only `cmd.fleet_id` and `cmd.order_index`
- `ReorderOrderCommandHandler.execute()` at `handlers/order_queue.py:220-253` — uses only `cmd.fleet_id`, `cmd.order_index`, and `cmd.direction`
- A grep for `cmd.entity_type` across all `game/strategy/engine/handlers/*.py` returns zero hits

**Why this matters (Rule 3):**

This is a PROJ-238 forward-looking field ("future planet support" per the ClearOrdersCommand docstring) that was added to 3 commands but never wired into handlers. It is dead weight that adds no value — exactly the kind of **partial-implementation drift** that Rule 3 prohibits. The field is a compatibility shim not for backward compat, but for a future that never arrived.

The verification report's deferral rationale ("Adding `entity_id` and migrating all callers is a real but separate scope-of-design refactor") addresses the wrong issue: the problem isn't the absence of `entity_id` — it's the presence of an unused `entity_type` field across 3 commands. No migration was needed; the fields could have been deleted outright since no handler reads them and no caller overrides the default value.

**Severity rationale:** 3 dead fields across 3 commands in the command pipeline. Low risk (defaults won't break anything), but this is a missed opportunity in a project whose stated purpose was "legacy removal + comment cleanups." The `entity_type` field IS legacy forward-dead-code.

---

### MAJOR-2: Misleading `# NOQA: legacy-retained` comment on BattleScreen was not cleaned

**File:** `game/ui/screens/battle_screen.py:117`

```python
# NOQA: legacy-retained — Combat Lab instance vars kept for
# back-compat with older visual test scenarios. Removal tracked
# in follow-up to PROJ-270 Phase 10.
self.headless_mode = False
self.headless_start_time = None
self.test_mode = False
self.test_scenario = None
self.test_tick_count = 0
self.test_completed = False
```

**What was found:**

The PROJ-393 verification report (commit 8fa9887d3 message) states: *"The audit misread the NOQA comment."* However, **zero changes were made to `battle_screen.py`** in any PROJ-393 commit (`git diff d605157aa..9321b0692 -- game/ui/screens/battle_screen.py` returns no output).

The verification report acknowledges the comment is misleading but then defers the entire task without even correcting the comment. This is a self-contradiction: PROJ-393 is explicitly a "comment cleanups" project, yet it left an acknowledged-misleading comment in place.

**Evidence the vars are NOT legacy:**

- `headless_mode` — actively read by `battle_screen.py:302` (gates headless update path) and `run_loop.py:216` (gates draw); set from `controller.config.headless` at line `:157`
- `test_completed` — read+written by `test_lab/screen.py:337,348,360`
- `test_tick_count` — read by `test_lab/screen.py:346`
- `test_mode`, `test_scenario` — read by `battle_screen.py:490` in `is_battle_over()`
- PROJ-270 is confirmed archived in `deep_archive/PROJ-251-300/PROJ-270/` — the comment references a dead project

**Why this matters (Rule 3):**

The comment is factually wrong on two counts:
1. "legacy-retained" — these vars are **actively used**, not legacy
2. "Removal tracked in follow-up to PROJ-270 Phase 10" — PROJ-270 is archived; no follow-up exists

The comment already misled the legacy-audit (hence it being flagged as LEG-03-023). Leaving it unchanged means the next audit tool or agent will re-flag it as a false positive. This is a "bug that breeds bugs" — misleading comments cause wasted audit cycles.

**Severity rationale:** MAJOR because (a) PROJ-393 explicitly includes "comment cleanups" in its title, (b) the misdirection has already caused one false positive audit hit, and (c) the fix is trivial (rewrite the 2-line comment).

---

## MINOR Findings

### MINOR-1: `view=None` branch in `format_planet_info` is a transparent, acknowledged compatibility shim

**File:** `game/ui/screens/strategy_detail_fmt.py:253-268`
**Production caller without facade:** `game/ui/screens/planet_selection_window.py:195-202`

**What was found:**

The `elif len(populations) > 0:` branch (lines 253-268) renders a legacy single-line per-species display when `view` is `None`. The docstring at lines 173-176 is honest about this:

> When ``None``, the legacy single-line per-species rendering is preserved for backward compatibility (uncolonized planets, snapshot tests, callers without a facade).

The primary production caller hitting this branch is `PlanetSelectionWindow` at `planet_selection_window.py:195-202`, which constructs `PlanetReportPanel` without `view=`, `empire=`, or `race_registry=` — it has no facade access.

**Is this a compatibility shim?**

Yes, it is a compatibility shim for PROJ-289's incomplete migration. The "proper" design would thread `ColonyDemographicView` through all callers. However:

1. The branch is **transparent** — the docstring clearly labels it as legacy/backward-compat
2. The branch is **functional** — it serves real production callers (`PlanetSelectionWindow`), not just tests
3. The deferral rationale is **legitimate** — threading facade through `PlanetSelectionWindow` requires touching the colonization workflow, `strategy_event_router`, and at least 3 test sites; this is a non-trivial refactor beyond "delete a fallback" scope
4. Uncolonized planets skip the entire population block (`owner_id is None`), so the "defensive for uncolonized planets" rationale in the verification report is partially misleading — but the `view=None` branch does handle colonized planets shown via `PlanetSelectionWindow`

**Rule 3 assessment:** Violates letter (it's a compat shim) but not spirit (honest, documented, with clear migration path). Scope deferral is valid. Severity stays MINOR because the migration path is documented and the branch is not dead code.

---

### MINOR-2: BattleScreen dual-role design (production screen + test harness) is a fallback system

**Files:** `game/ui/screens/battle_screen.py:120-125` (instance vars), `:302` (`headless_mode` gate), `:490` (`test_mode` gate)
**Test harness consumer:** `game/ui/screens/test_lab/screen.py:334-362`

**What was found:**

The 6 Combat Lab instance vars on `BattleScreen` (`headless_mode`, `test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, `headless_start_time`) make `BattleScreen` serve dual roles: production game screen AND test harness. The `is_battle_over()` method at line 487-492 has a `test_mode` branch that short-circuits battle-over detection; the `update()` method at line 302 dispatches to `_update_headless()` vs `_update_visual()` based on `headless_mode`.

**Is deferral legitimate?**

Yes. The verification report correctly states: *"The real refactor (route Combat Lab visual mode through a non-attribute-stuffing mechanism) is non-trivial and out of PROJ-393's scope."* This is a legitimate scope acknowledgment, not a rationalized retreat. The Combat Lab is a fully functional test infrastructure with its own screen (`test_lab/screen.py`), execution engine, and results tracking — extracting the test harness from `BattleScreen` requires architectural work (likely a `BattleTestHarness` class or a `TestableBattleScreen` mixin).

**Rule 3 assessment:** The dual-role design is a form of fallback system (BattleScreen falls back to headless mode when testing). This violates Rule 3's spirit, but the deferral is reasonable because (a) the code is active and functional, not dead/compat, and (b) the fix requires a separate design project. The verification report's recommendation to "file a follow-up PROJ" should be acted on.

**Severity rationale:** MINOR because (a) the code is actively used, not dead weight, (b) the deferral was well-reasoned, and (c) this is an architectural concern beyond a cleanup project's scope. The missing follow-up PROJ is the real gap.

---

## INFO Findings

### INFO-1: 4 pytest collection import-mismatch errors confirmed orthogonal to PROJ-393

**Errors observed:**

```
ERROR tests/unit/ui/screens/builder/test_components.py
  → collides with tests/unit/entities/test_components.py
ERROR tests/unit/ui/widgets/test_panel_factory.py
  → collides with tests/unit/ui/screens/race_setup/test_panel_factory.py
ERROR tests/unit/workshop/test_stat_getters.py
  → collides with tests/unit/ui/screens/builder/test_stat_getters.py
ERROR tests/unit/workshop/test_workshop_data_loader.py
  → collides with tests/unit/ui/screens/test_workshop_data_loader.py
```

Root cause: duplicate module basenames in different test directories cause `__pycache__` import conflicts during pytest collection.

**Orthogonality confirmation:**

| Error | Collision file 1 (branch-added) | Collision file 2 (existing) | PROJ-393 touched? |
|-------|-------------------------------|---------------------------|-------------------|
| test_components | `tests/unit/ui/screens/builder/test_components.py` (02cca7071) | `tests/unit/entities/test_components.py` (on main) | Neither |
| test_panel_factory | `tests/unit/ui/widgets/test_panel_factory.py` (e854472f3) | `tests/unit/ui/screens/race_setup/test_panel_factory.py` (4223460c8) | Neither |
| test_stat_getters | `tests/unit/workshop/test_stat_getters.py` (d47f63f23) | `tests/unit/ui/screens/builder/test_stat_getters.py` (6d4718693) | Neither |
| test_workshop_data_loader | `tests/unit/workshop/test_workshop_data_loader.py` (d47f63f23) | `tests/unit/ui/screens/test_workshop_data_loader.py` (dadf4df1a) | Neither |

- **None of the 8 files** involved in the 4 collisions were created or modified by any PROJ-393 commit.
- 1 collision pair (test_components) involves a file on `main` plus a file added on this branch.
- 3 collision pairs involve both files added on this branch before PROJ-393 (by the commits listed above, all pre-dating PROJ-393).
- These errors would fail identically with or without PROJ-393 changes cherry-picked.

**RCA:** Multiple test directories contain files with identical basenames. pytest's import-collection mechanism reuses `__pycache__` entries across directories, causing the second file's collection to fail with "import file mismatch." The fix is to rename the newer (duplicate) test files to have unique basenames, or to run `find . -type d -name __pycache__ -exec rm -rf {} +` between collection attempts (temporary workaround only).

---

## Focus Area Responses (as requested)

### Task 3.2 (fleet_id field — tag removed but field kept)

**Question:** Is keeping the `fleet_id` field justified, or a Rule 3 violation?

**Answer:** Keeping `fleet_id` is **fully justified**. `fleet_id` is the canonical field used by ALL 3 handlers (`ClearOrdersCommandHandler`, `DeleteOrderCommandHandler`, `ReorderOrderCommandHandler`) via `cmd.fleet_id`. There is no `entity_id` field to migrate to. The `# Kept for backward compat` tag was itself wrong — it was a forward-looking tag placed during PROJ-238 that was superseded by reality (PROJ-238 never completed the `entity_id` design).

**However**, the `entity_type: str = "fleet"` field that remains on all 3 commands IS a Rule 3 violation (see MAJOR-1) — it's forward-dead-code, a partial-implementation shim for a future planet-support design that never arrived. The field could be deleted with zero handler impact since no handler reads `cmd.entity_type`.

### Task 3.5 (BattleScreen Combat Lab vars — deferred)

**Question:** Are the Combat Lab vars a "fallback system" violating Rule 3, or legitimately deferred?

**Answer:** The Combat Lab vars represent a **fallback system** (BattleScreen falls back to headless/test-mode behavior) that violates Rule 3's spirit. However, the **deferral is legitimate** because:
1. The vars are actively used (not dead code)
2. The fix requires architectural refactoring (extracting test harness from production screen)
3. PROJ-393's scope was "delete legacy fallbacks" — these are active, in-use features

The verification report's statement: *"The real refactor is non-trivial"* is a legitimate scope acknowledgment, not a rationalized retreat.

**However**, the misleading `# NOQA: legacy-retained` comment should have been corrected (see MAJOR-2). PROJ-393 is explicitly a comment-cleanup project, yet the comment that misled the audit was left unchanged.

### Task 3.3 (view=None branch — deferred)

**Question:** Is the `view=None` branch a compat shim or legitimate null-handling?

**Answer:** It is a **compatibility shim mixed with legitimate null-handling**:
- It serves real production callers (`PlanetSelectionWindow` at `planet_selection_window.py:195`) that legitimately lack facade access
- It serves as legitimate null-safety for any future caller that can't supply demographic data
- But it's also explicitly labeled as a "legacy" path for incomplete PROJ-289 migration

The deferral is legitimate: threading `ColonyDemographicView` through `PlanetSelectionWindow` requires touching the colonization workflow, `strategy_event_router`, and test sites. This is a refactoring project, not a cleanup.

### Focus Area 7: The 4 pre-existing pytest-collection errors

**Question:** Are these truly orthogonal?

**Answer:** **Yes, confirmed orthogonal.** See INFO-1 above for the full traceability matrix. None of the 8 files involved were created or modified by any PROJ-393 commit. All 4 errors reproduce identically on this branch with or without PROJ-393 changes.

**Important nuance:** 3 of the 4 collision pairs do NOT exist on `main` — both files in those 3 pairs were added in different commits on the `feat/03c-phase-aware-execution` branch before PROJ-393. 1 collision (test_components) involves a `main`-line file. So while they're pre-existing on this branch, they're not all pre-existing on `main`.

---

## Recommendations

1. **Delete `entity_type` from ClearOrdersCommand, DeleteOrderCommand, ReorderOrderCommand** — no handler reads it; it's forward-dead-code. 3-line change across 3 dataclasses.

2. **Fix the misleading `# NOQA: legacy-retained` comment on BattleScreen** — replace with accurate description of active Combat Lab usage. 2-line change.

3. **File the follow-up PROJ for Combat Lab BattleScreen attribute extraction** — as the verification report recommended. The current dual-role design is a Rule 3 violation that will eventually need architectural attention.

4. **Track the `view=None` branch for PROJ-289 completion** — the PlanetSelectionWindow facade-threading work should be captured as a project task rather than remaining as a known-but-undeferred compatibility shim.
