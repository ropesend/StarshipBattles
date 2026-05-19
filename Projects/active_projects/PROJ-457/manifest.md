# PROJ-457 File Manifest

> Generated during charter creation 2026-05-19 from Codex r4 audit redesign (job 9) + F-C-027/F-C-028 findings.
> Updated during implementation as Phase 0 re-measurement and per-phase extractions surface additional files.

## Files

### Phase 0 — LOC re-measurement after PROJ-456 ships

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-457/findings/post_proj_456_loc_remeasure.md` | Findings (new) | Records a PowerShell-safe LOC measurement of all 12 F-C-027 files at the start of PROJ-457 (see phase_0_checklist.md Task 0.2 for the PS one-liner). |
| `Projects/active_projects/PROJ-457/decisions.md` | Project | Per `phase_0_checklist.md:54-58`: record rescope rationale (which phase target changed if any of the top-3 dropped under 500) AND the candidate-extraction audit results (Task 0.4 audit of 2-3 cohesive responsibilities per top-3 file). |
| `Projects/active_projects/PROJ-457/plan.md` | Project | Update Quick Status table if rescope is required (any of the top-3 drop under 500 → replace that phase). |

The 12 F-C-027 files to re-measure:
- `game/ui/screens/build_queue_screen.py` (was 961)
- `game/ui/screens/planet_list_window.py` (was 862)
- `game/ui/screens/test_lab/screen.py` (was 744)
- `game/ui/screens/new_game_setup_screen.py` (was 734)
- `game/ui/screens/empire_build_queue_window.py` (was 734)
- `game/ui/screens/event_log_window.py` (was 732)
- `game/ui/panels/race_summary_panel.py` (was 732)
- `game/ui/screens/empire_panel_window.py` (was 724)
- `game/ui/panels/build_queue_controller.py` (was 723)
- `game/ui/panels/system_tree_panel.py` (was 711)
- `game/ui/screens/design_selector_window.py` (was 708)
- `game/ui/screens/strategy_detail_fmt.py` (was 707)

### Phase 1 — Extract one responsibility from `build_queue_screen.py`

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/build_queue_screen.py` | Production | Source of extraction; LOC drops from 846 (HEAD 2026-05-19; was 961 in original scan) → < 500 after extraction. |
| `game/ui/screens/build_queue_<responsibility>.py` | Production (new) | New sibling module containing the extracted responsibility. Exact name decided during Phase 1 read pass — candidates per F-C-027: `build_queue_drag.py`, `build_queue_yard_population.py`, `build_queue_selection.py`, etc. |
| Test files for the new sibling module | Test (new) | Mirror layout: `tests/unit/ui/screens/test_build_queue_<responsibility>.py`. |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | Test | Update imports if the extracted methods were tested through the screen. |
| `tests/unit/ui/panels/test_build_queue_controller.py` | Test | Update imports if affected. |
| `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py` | Test | Update imports if affected. |

### Phase 2 — Extract one responsibility from `planet_list_window.py`

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/planet_list_window.py` | Production | Source of extraction; LOC drops from 746 (HEAD 2026-05-19; was 862) → < 500. |
| `game/ui/screens/planet_list_<responsibility>.py` | Production (new) | Candidates: `planet_list_formatting.py` (extracts `_format_population` + sibling formatters), `planet_list_sidebar_factory.py`, etc. |
| Test files for the new sibling module | Test (new) | Mirror layout: `tests/unit/ui/screens/test_planet_list_<responsibility>.py`. |
| `tests/unit/ui/screens/test_planet_list_window*.py` | Test | Update imports if affected. |
| `tests/unit/ui/screens/planet_list/*.py` | Test | Update imports if affected (if a planet_list test subdirectory exists). |

### Phase 3 — Extract one responsibility from `test_lab/screen.py`

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/test_lab/screen.py` | Production | Source of extraction; LOC drops from 614 (HEAD 2026-05-19; was 744) → < 500. |
| `game/ui/screens/test_lab/<responsibility>.py` | Production (new) | Candidates: `scenario_loader.py`, `test_history_coordinator.py`, etc. The existing `test_lab/` decomposition (viewmodel / renderer / input_handler / panel_manager / test_executor / data_extractor) provides clear precedent for the new module's shape. |
| Test files for the new sibling module | Test (new) | Mirror layout: `tests/unit/ui/screens/test_lab/test_<responsibility>.py`. |
| `tests/unit/ui/screens/test_lab/*.py` | Test | Update imports if affected. |

### Phase 4 — Split `game/core/exceptions.py` by domain with re-export shim

| File | Type | Notes |
|------|------|-------|
| `game/core/exceptions.py` | Production | Re-measured at HEAD 2026-05-19: 411 LOC (already under 500 ceiling; charter's "544" was stale). 31 classes (charter's "27" was stale; phase_4 checklist's domain-split table at lines 65-69 enumerates 31). Becomes a re-export aggregator (~60-80 LOC with explicit imports per convention). Module docstring updated to explain the aggregator role + canonical-submodule guidance. **PHASE 4 PENDING USER DECISION on whether to proceed given the file is already under the ceiling.** |
| `game/core/exceptions_base.py` | Production (new) | 7 classes (~110 LOC): `GameException`, `StateException`, `FrozenStateException`, `ValidationException`, `ResourceException`, `MissingResourceException`, `PersistenceException`. |
| `game/core/exceptions_strategy.py` | Production (new) | 5 classes (~95 LOC): `StrategyException`, `SessionInitializationError`, `EnginePhaseError`, `TurnFailedError`, `BattleResolutionError`. |
| `game/core/exceptions_simulation.py` | Production (new) | 3 classes (~30 LOC): `SimulationException`, `ComponentException`, `FormulaException`. |
| `game/core/exceptions_llm.py` | Production (new) | 8 classes (~85 LOC): `LLMException`, `LLMConfigError`, `LLMNetworkError`, `LLMResponseError`, `LLMRateLimited`, `LLMTimeoutError`, `LLMCancelled`, `LLMUnexpectedError`. |
| `game/core/exceptions_image.py` | Production (new) | 8 classes (~80 LOC): `ImageException`, `ImageConfigError`, `ImageNetworkError`, `ImageResponseError`, `ImageRateLimited`, `ImageTimeoutError`, `ImageCancelled`, `ImageUnexpectedError`. |
| `game/core/__init__.py` | Production | If it re-exports specific exception classes, those exports continue to work through the re-export aggregator. No edits required if the existing `from game.core.exceptions import ...` statements are sufficient. |
| `tests/unit/core/test_exceptions.py` | Test | Existing tests continue to work through the re-export aggregator. Add new tests asserting (a) the canonical submodules are directly importable, (b) the re-export aggregator preserves the public API, (c) every class is exported from exactly one submodule and re-exported once. |
| `tests/static_guards/test_no_legacy_protocol_names.py` (or similar) | Test (new — optional) | Static guard pinning the re-export structure if drift becomes a concern. PROJ-456 / PROJ-457 may not need this; revisit at Phase 4 close. |
| `docs/02_PATTERNS.md` §36 (re-export shim) | Docs | If §36 needs updating to add `exceptions.py` to the documented shim sites, do so during Phase 4. |
| `docs/01_ARCHITECTURE.md` | Docs | The package map references `exceptions.py: 27 exception classes`. Update to **31 classes** (re-verified at HEAD 2026-05-19) + new submodule layout. **Cross-group collision risk: this file is also touched by PROJ-459 (Group 1) and PROJ-460 (Group 3) — see plan.md's Dependencies & Sibling Projects section for the coordinator's serialization decision.** |

### Phase 5 — Document remaining over-ceiling files as "next-touch" rule

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-457/decisions.md` | Project | Append the "F-C-027 follow-up: 9 over-ceiling UI files become a next-touch rule" decision row (template in plan.md Phase 5 section). |
| `CLAUDE.md` | Docs | Optional: one-line cross-reference under "Key Conventions" if the touching-agent guidance belongs there. |
| `AGENTS.md` | Docs | Optional: same one-line cross-reference. |

### Findings file updates (each phase)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-457/findings/PROJ-457_findings.md` | Project | Update F-C-027 / F-C-028 status after each phase. Phase 1-3 close F-C-027 for the touched file (3 of 12); Phase 4 closes F-C-028; Phase 5 documents the remaining 9 as "deferred to next-touch." |

### Decisions log updates

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-457/decisions.md` | Project | Record per-phase decisions: which responsibility was extracted from each UI file; whether Phase 0 surfaced unexpected LOC drops; the Phase 5 next-touch rule (mandatory). |

### Plan + checklist updates

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-457/plan.md` | Project | Update Quick Status table + Current State after each phase. |
| `Projects/active_projects/PROJ-457/phase_<N>_checklist.md` | Project | Check off subtasks as the work progresses; final Phase Completion Checklist closed at phase end. |
