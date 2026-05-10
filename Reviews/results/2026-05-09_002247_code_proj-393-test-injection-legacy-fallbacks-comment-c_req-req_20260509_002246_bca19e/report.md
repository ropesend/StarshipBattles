# Review Report: PROJ-393 — Test-injection legacy fallbacks + comment cleanups

**Review Type:** code
**Request ID:** req_20260509_002246_bca19e
**Reviewer:** OpenCode (ocode-review-request)
**Date:** 2026-05-09
**Branch:** feat/03c-phase-aware-execution (5 commits: a23948b9d → 9321b0692)
**Review Mode:** Full code review with 4 parallel agents

**Scope:** 18 production files across 3 phases. Phase 1 (comment-only deletions), Phase 2 (test-injection fallback removal), Phase 3 (backward-compat fields + misc legacy paths).

**Limitations:** Review inspects resulting code state, not incremental diffs. Full sharded test suite not executed (deferred to orchestrator stage boundary). Asset scan coverage gap noted (see F-04).

## Verification Matrix

| Deferral | Status | Notes |
|---|---|---|
| Task 3.2 (fleet_id tag) | Partial regr. | Tag removal introduced confusion (F-02, F-03); entity_type dead-weight missed (F-04) |
| Task 3.3 (view=None) | Legitimate deferral | Real production callers lack facade; scope management correct |
| Task 3.5 (Combat Lab vars) | **Regressed** | 4 of 6 vars are dead code; audit was correct, deferral was wrong (F-01) |

---

## Findings

### CRITICAL

**F-01 — 4 of 6 Combat Lab BattleScreen vars are dead code, not "actively used"**

*File:* `game/ui/screens/battle_screen.py:117–125`
*Severity:* CRITICAL

The PROJ-393 agent deferred removal of Combat Lab instance vars, claiming they are "actively used by production code." Only `headless_mode` and `headless_start_time` have legitimate runtime paths. The remaining 4 vars are dead code in production:

| Var | Init | Set to non-default in production? | Reads that execute in production? |
|-----|------|-----------------------------------|----------------------------------|
| `test_mode` | `False` | **NEVER** | `:490` (dead `is_battle_over` branch) |
| `test_scenario` | `None` | **NEVER** — `_switch_to_battle` no longer sets it | `test_lab/screen.py:335` always reads `None` |
| `test_tick_count` | `0` | **NEVER** | `test_lab/screen.py:346` never reached |
| `test_completed` | `False` | **NEVER** | `test_lab/screen.py:337` never reached |
| `headless_mode` | `False` | YES (`:157` from `config.headless`) | `:302`, `run_loop.py:216` — **ACTIVE** |
| `headless_start_time` | `None` | Set to `None` only; only read at `:685` inside `if self.test_mode:` (dead) | **DEAD** |

The `is_battle_over()` check at `:490` is a dead branch — the live battle-over detection is `self._battle_service.is_battle_over()` at `:492`. The visual test results capture in `test_lab/screen.py:334–356` is dead — `test_scenario` is always `None`.

The original legacy audit (LEG-03-023) correctly identified these as reclaimable. The PROJ-270 skeptic audit also flagged them. The deferral is a post-hoc rationalization — `headless_mode` was the only genuine active feature among these 6 vars.

**Recommendation:** Delete `test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, and `headless_start_time`. Fix `is_battle_over()` (line 487–492) and `print_headless_summary()` (line 677–687) to remove dead branches. Fix `test_lab/screen.py:334–356` dead result-capture block.

---

### MAJOR

**F-02 — fleet_id tag removal reduces clarity: doc now labels a transitional field as "canonical"**

*File:* `game/strategy/engine/commands/__init__.py:99–106`
*Severity:* MAJOR

The PROJ-393 agent removed the "Kept for backward compat" tag from `ClearOrdersCommand.fleet_id` and replaced it with a label stating `fleet_id` is "canonical." This is a cosmetic-only change that introduces confusion:

1. `ClearOrdersCommand` has both `fleet_id: int` AND `entity_type: str = "fleet"`, but the handler (`order_queue.py:97`) only uses `cmd.fleet_id`. The handler never branches on `entity_type`. Having both fields with the comment that `fleet_id` is "canonical" while `entity_type` points to future planet support is self-contradictory.
2. Sibling commands in the SAME file are inconsistent: construction queue commands (`AddToConstructionQueueCommand`, `RemoveFromConstructionQueueCommand`) use `entity_id: int` + `entity_type: BuildEntityType` (modern pattern), while order queue commands use `fleet_id: int` + `entity_type: str`.
3. The old tag truthfully warned developers the field was transitional. The new label implies stability and canonical status that doesn't exist (no migration plan has started).

**Recommendation:** Revert the docstring change to `ClearOrdersCommand`. Either restore the backward-compat warning or defer the entire file to a sibling project that actually migrates to `entity_id`/`entity_type` across all affected commands.

---

**F-03 — "~20 call sites" claim in ClearOrdersCommand docstring is false**

*File:* `game/strategy/engine/commands/__init__.py:105`
*Severity:* MAJOR

The docstring claims "A future project may unify on entity_id/entity_type and migrate the ~20 call sites." Spot-checked counts:

| Command | Production call sites using `fleet_id=` |
|---------|----------------------------------------|
| `ClearOrdersCommand` | 1 (`orders_window_ctrl.py:73`) |
| `DeleteOrderCommand` | 1 (`orders_window_ctrl.py:78`) |
| `ReorderOrderCommand` | 1 (`orders_window_ctrl.py:87`) |
| DeployFleetCommand | **Does not exist** |
| TransferPassengersCommand | **Does not exist** |

The "~20" appears to count all commands with `fleet_id` fields across the file, not just `ClearOrdersCommand`. This inflates the perceived migration cost.

**Recommendation:** Replace with an accurate count or remove the speculative number entirely.

---

**F-04 — `entity_type` dead-weight fields on 3 order-queue commands not cleaned**

*File:* `game/strategy/engine/commands/__init__.py:108,293,305`
*Severity:* MAJOR

`ClearOrdersCommand`, `DeleteOrderCommand`, and `ReorderOrderCommand` all carry `entity_type: str = "fleet"` with comments like `# "fleet" or "planet" (handler uses fleet path only)`. No handler in `game/strategy/engine/handlers/` reads `cmd.entity_type` — the field is never evaluated for branching. This is forward-dead-code from a PROJ-238 partial implementation that was never completed.

The PROJ-393 verification report addressed `fleet_id` but missed that `entity_type` itself is dead weight. Deleting these 3 fields would have zero handler impact since no handler reads them and no caller overrides the default.

**Recommendation:** Delete `entity_type` from all 3 command dataclasses. This is a 3-line change with zero handler impact.

---

**F-05 — No test ever calls EmpireBuildQueueWindow() through the real constructor**

*File:* `tests/unit/ui/screens/test_empire_build_queue_window.py:63–65`
*Severity:* MAJOR

The entire test suite bypasses `EmpireBuildQueueWindow.__init__`. All tests either:
1. Patch `__init__` with a lambda no-op and call `__new__` (`test_empire_build_queue_window.py:63–65`)
2. Patch the entire class with `MagicMock()`

The static guard (`test_facade_bypass_guard.py:38`) only checks for `session=` text references — it does not validate that `facade` is a required parameter. If someone reverts `facade` from required to optional (`facade: Any = None`), no test would catch it. The constructor parameter validation is completely unverified by the test suite.

**Recommendation:** Add a `test_constructor_requires_facade` test that asserts `TypeError` when `EmpireBuildQueueWindow` is instantiated without `facade=`. Optionally add an integration test that constructs the window through its real `__init__`.

---

**F-06 — Misleading "# NOQA: legacy-retained" comment on BattleScreen left uncleaned**

*File:* `game/ui/screens/battle_screen.py:117`
*Severity:* MAJOR

The comment at line 117:
```python
# NOQA: legacy-retained — Combat Lab instance vars kept for
# back-compat with older visual test scenarios. Removal tracked
# in follow-up to PROJ-270 Phase 10.
```

The PROJ-393 verification report acknowledges this comment is misleading ("The audit misread the NOQA comment"), yet zero changes were made to `battle_screen.py` in any PROJ-393 commit. The comment is wrong on two counts:
1. "legacy-retained" — these vars are actively used (not legacy)
2. "Removal tracked in follow-up to PROJ-270 Phase 10" — PROJ-270 is archived in `deep_archive/`; no follow-up exists

This comment already misled the legacy audit (LEG-03-023). Leaving it unchanged means the next audit tool will re-flag it as a false positive. For a project explicitly titled "comment cleanups," this is a self-contradiction.

**Recommendation:** Rewrite the comment to accurately describe the Combat Lab usage. Trivial 2-line fix.

---

**F-07 — Five additional production files with unconverted ResourceCatalog.from_json() module-level pattern**

*Files:* `game/ui/screens/planet_list_window.py:24`, `game/strategy/data/planet_gen.py:17`, `game/strategy/engine/empire_economy_calculator.py:16`, `game/strategy/engine/construction_forecast.py:18`, `game/ui/panels/empire_treasury_panel.py:20`
*Severity:* MAJOR

Task 3.4 fixed the `ResourceCatalog.from_json()` module-level anti-pattern (Pattern 12 violation — I/O at import time) in `build_queue_helpers.py` and `strategy_ui.py`. The exact same pattern exists in 5 other production files. Three of these are in the Strategy layer where import-time I/O has broader consequences for test isolation.

The scope was deliberately limited to the 2 target files, but the spirit of the cleanup was "eliminate import-time ResourceCatalog.from_json() calls."

**Recommendation:** Create a follow-up PROJ (or expand a sibling project's scope) to apply the `@lru_cache(maxsize=1)` lazy-init pattern to the remaining files.

---

### MINOR

**F-08 — Vestigial `with_remove_callback` kwarg in `_make_handler` test helper**

*File:* `tests/unit/ui/panels/test_build_queue_drag_handler.py:69`
*Severity:* MINOR

The `_make_handler` helper accepts `with_remove_callback: bool = True` but its body unconditionally creates and passes `on_remove=MagicMock()`. The kwarg has no effect on behavior — it's dead API surface in a test helper. The docstring acknowledges this but the kwarg should be removed since it misleads readers into thinking there's still a no-callback path.

---

**F-09 — Test fake-facade is an inline mock that reimplements command handler logic**

*File:* `tests/unit/ui/screens/test_empire_build_queue_window.py:110–132`
*Severity:* MINOR

The `_fake_handle_command` closure reimplements `AddToConstructionQueueCommand` handler logic — it knows about `cmd.queue_id`, `cmd.entity_id`, `cmd.category`, and mutates `src.construction_queue` in-place. This tightly couples the test to `AddToConstructionQueueCommand` internals. Standard unit-test mock practice, but the coupling is worth noting.

---

**F-10 — Type contract mismatch between command dataclass and validator**

*File:* `game/strategy/engine/commands/__init__.py:421` vs `game/strategy/validation/planet_order_validator.py:31`
*Severity:* MINOR

`IssuePlanetOrderCommand.component_key` is `Optional[str] = None`, but `PlanetOrderValidator.validate_activate_ability(component_key: str)` requires non-optional `str`. The command handler guards (`planet_command_handlers.py:74–75, 83–84`) prevent runtime errors, but a future direct call bypassing the handler guard would pass mypy strict-mode (since `Optional[str]` is compatible with `str` at the call site) but fail at runtime if `component_key` happens to be `None`.

---

**F-11 — `_LEGACY_PATTERN` asset scan methodology gap**

*File:* `game/ui/renderer/sprites.py` (post-deletion)
*Severity:* MINOR

The `_LEGACY_PATTERN` deletion was correct, and the conclusion (pattern is dead code) is valid. However, the asset scan covered only `assets/Images/Components/` directories. Other asset subdirectories (`assets/Images/altcomponents/`, `Cursor/`, `Flags/`, `Stellar Objects/`, `ShipThemes/`, etc.) were not scanned. This is a minor gap because the pattern was only used in `SpriteManager._load_from_directory`, which only loads from Components directories. The conclusion remains correct.

---

**F-12 — `view=None` branch in `format_planet_info` is a transparent, acknowledged compatibility shim**

*File:* `game/ui/screens/strategy_detail_fmt.py:253–268`
*Severity:* MINOR

The `view is None` branch serves real production callers (`PlanetSelectionWindow` at `planet_selection_window.py:195`) that lack facade access. The docstring honestly labels it as backward-compat for incomplete PROJ-289 migration. The deferral is legitimate: threading `ColonyDemographicView` through `PlanetSelectionWindow` requires touching the colonization workflow, `strategy_event_router`, and multiple test sites.

---

**F-13 — BattleScreen dual-role design (production screen + test harness) is a fallback system**

*File:* `game/ui/screens/battle_screen.py:120–125,302,490`
*Severity:* MINOR

The Combat Lab instance vars make `BattleScreen` serve dual roles: production game screen AND test harness. This is a fallback system (violates Rule 3's spirit), but deferral is reasonable because the code is active (not dead), and the fix requires architectural refactoring (extracting test harness from production screen). The verification report's recommendation to "file a follow-up PROJ" should be acted on.

---

**F-14 — Overly verbose historical comment block in `spec_compiler.py`**

*File:* `game/strategy/combat/spec_compiler.py:446–457`
*Severity:* MINOR

A 12-line comment documents deleted kwargs from PROJ-271 Phase 9 and PROJ-272 Phase 7. While legitimate architecture documentation, historical-change comments of this density accumulate over time. A 2-line summary referencing the relevant PROJ docs would serve the same purpose.

---

**F-15 — Unexplained compatibility comment in `save_game_service.py`**

*File:* `game/strategy/systems/save_game_service.py:128`
*Severity:* MINOR

```python
'turn_number': game_session.turn_number,  # For compatibility
```
The `# For compatibility` comment does not explain what it's compatible with. If intentional forward-compatibility, the comment should clarify.

---

### INFO

**F-16 — `update_input` is not part of the IScene protocol (documented design choice)**

*File:* `game/run_loop.py:203–208` vs `game/core/protocols/ui.py:9–31`
*Severity:* INFO

`IScene` mandates `handle_event`, `update`, `draw`, `handle_resize`. `run_loop.py:208` calls `router.active_scene.update_input(frame_time, events)` which is not in the protocol. The comment at line 203 documents this as intentional. Both `ResearchTreeScene` and `GalaxyTestScreen` implement `update_input`. A new scene without `update_input` used in these states would crash.

---

**F-17 — 4 pytest-collection import-mismatch errors confirmed orthogonal to PROJ-393**

*Severity:* INFO

4 test files with duplicate basenames in different directories cause `__pycache__` import conflicts during pytest collection:
- `tests/unit/ui/screens/builder/test_components.py` collides with `tests/unit/entities/test_components.py`
- `tests/unit/ui/widgets/test_panel_factory.py` collides with `tests/unit/ui/screens/race_setup/test_panel_factory.py`
- `tests/unit/workshop/test_stat_getters.py` collides with `tests/unit/ui/screens/builder/test_stat_getters.py`
- `tests/unit/workshop/test_workshop_data_loader.py` collides with `tests/unit/ui/screens/test_workshop_data_loader.py`

None of the 8 files were created or modified by any PROJ-393 commit. These are pre-existing branch errors (some files on `main`, some added earlier on this branch). The agent's claim that they are orthogonal is correct.

---

**F-18 — Uncached `ResourceCatalog.from_json()` inside builder UI function**

*File:* `game/ui/screens/builder/stat_rows_dynamic.py:177`
*Severity:* INFO

`get_construction_rows()` calls `ResourceCatalog.from_json()` on every invocation. Not a module-level violation, but should cache or receive the catalog as a parameter. Low priority — builder UI is not a hot path.

---

**F-19 — "legacy" used correctly as behavioral descriptor in `formation.py`**

*File:* `game/simulation/combat/formation.py:326`
*Severity:* INFO

The word "legacy" at line 326 describes preserved behavior (byte-identical output), not stale/dead code. Correct usage. No action needed.

---

## Phase 1 & 3 Completed Task Verification

| Task | Target | Verdict |
|------|--------|---------|
| LEG-03-002 | `formation.py:357` snap comment | PASS |
| LEG-03-003 | `spec_compiler.py:462` env effects comment | PASS |
| LEG-02-005 | `save_game_service.py:68` legacy comment | PASS |
| LEG-02-017 | `context.py:13` PROJ-258 tag | PASS |
| Task 2.1 | IScene migration (run_loop + 2 scenes) | PASS |
| Task 2.2/2.3 | PlanetOrderValidator fallbacks | PASS |
| Task 2.4 | BuildQueueDragHandler fallback | PASS |
| Task 2.5 | EmpireBuildQueueWindow fallback | PASS |
| Task 3.1 | PlanetActionEngine shield fallback | PASS |
| Task 3.4 | ResourceCatalog lazy init (target files) | PASS |
| Task 3.6 | `_LEGACY_PATTERN` deletion | PASS |
| Task 3.7 | TransferBranches first-species fallback | PASS |

All 12 completed tasks are verified correct. No regressions at changed sites.

## Reviewer's Assessment

**The 3 deferrals require re-evaluation:**

1. **Task 3.5 (Combat Lab vars) — REJECTED.** 4 of 6 vars are dead code. The deferral was based on a misread of which vars are "actively used." Only `headless_mode` is genuinely active. This should be reimplemented to delete the dead vars.

2. **Task 3.2 (fleet_id tag) — PARTIAL REGRESSION.** Removing the backward-compat warning was the wrong direction. The tag should either be restored or the field should be renamed to `entity_id` across all affected commands in a sibling project. The current doc misleads readers about the field's transitional status. Additionally, `entity_type` dead-weight fields on 3 commands were missed entirely.

3. **Task 3.3 (view=None) — LEGITIMATE.** The deferral is well-reasoned scope management. `PlanetSelectionWindow` lacks facade access; threading it through requires architectural refactoring.

**Two "comment cleanup" items contradict PROJ-393's stated purpose:**  
- The misleading NOQA comment on BattleScreen was acknowledged as wrong but left unchanged (F-06).  
- The `entity_type` dead-weight comment-fields on 3 commands were not cleaned despite being in scope (F-04).
