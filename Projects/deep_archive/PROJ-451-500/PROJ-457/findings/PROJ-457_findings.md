# PROJ-457 Findings — UI structural debt extractions

> Consolidated from `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md` (2026-05-18 scan).
> The original scan flagged 30 findings across UI + Core + Tests. This file extracts the 2 entries
> that PROJ-457 owns. File:line refs re-verified against repo HEAD on 2026-05-19.

## Owned Findings

### F-C-027 — Production file size overflow: 12 UI files over the 500-LOC ceiling

- **Severity**: medium
- **Category**: polish
- **File**: 12 UI files (re-measured 2026-05-19 against repo HEAD):

| File | LOC (HEAD) | Original scan (2026-05-18) |
|------|-----------:|---------------------------:|
| `game/ui/screens/build_queue_screen.py` | 961 | 961 |
| `game/ui/screens/planet_list_window.py` | 862 | 862 |
| `game/ui/screens/test_lab/screen.py` | 744 | 744 |
| `game/ui/screens/new_game_setup_screen.py` | 734 | 734 |
| `game/ui/screens/empire_build_queue_window.py` | (re-measure) | 734 |
| `game/ui/screens/event_log_window.py` | 732 | 732 |
| `game/ui/panels/race_summary_panel.py` | (re-measure) | 732 |
| `game/ui/screens/empire_panel_window.py` | (re-measure) | 724 |
| `game/ui/panels/build_queue_controller.py` | (re-measure) | 723 |
| `game/ui/panels/system_tree_panel.py` | (re-measure) | 711 |
| `game/ui/screens/design_selector_window.py` | (re-measure) | 708 |
| `game/ui/screens/strategy_detail_fmt.py` | (re-measure) | 707 |

- **Symbol**: file-level (the 500-LOC ceiling per `docs/03_CONVENTIONS.md` "File Size")
- **Source refactor**: cumulative
- **What survived**: 12 production UI files exceed the 500-LOC ceiling. `build_queue_screen.py` is at 961 (almost 2x), `planet_list_window.py` at 862. Multiple other files in the 500-700 range.
- **Why it's a problem**: Convention is "should stay below 500 LOC. ... If a production file approaches or exceeds 500 LOC, split by cohesive responsibility." Several of these files (`build_queue_screen.py`, `event_log_window.py`) were recently touched by major refactors that left them over the ceiling.
- **Suggested action**: Pick the worst offender (`build_queue_screen.py`) and extract a responsibility (yard population, queue selection, drag handling) into a sibling module. Same pattern as the existing `build_queue_*` family split.
- **Effort**: medium per file (project-shaped, not single-pass)

**Status as of 2026-05-19: open.**

**PROJ-457 disposition (per Codex r4 redesign):**

PROJ-457 explicitly scopes the **top 3 worst offenders** (`build_queue_screen.py` 961, `planet_list_window.py` 862, `test_lab/screen.py` 744) — same-recipe extractions, one per Phase 1 / 2 / 3. The remaining 9 over-ceiling files become a `decisions.md` "next-touch" rule (Phase 5): when any of those 9 is touched for an unrelated reason, the touching agent does an extract-by-responsibility pass before merging.

**Codex r4 also flagged a re-measurement risk:** PROJ-456 (shim retirement) retires hundreds of LOC of property/method shims across `new_game_setup_screen.py`, `battle_setup/screen.py`, `transfer_dialog.py`, and others. After PROJ-456 ships, some of the 12 files may drop under 500 naturally. **Phase 0 of PROJ-457 re-measures all 12 files** before starting structural extractions, so we don't extract from a file that no longer over-runs the ceiling.

---

### F-C-028 — `game/core/exceptions.py` re-measured: 411 LOC + 31 classes (originally claimed 544 LOC over ceiling — stale)

- **Severity**: low
- **Category**: polish (architectural cleanup — NOT ceiling enforcement post-2026-05-19 re-measurement)
- **File**: `game/core/exceptions.py:1` (file-level; **411 LOC at HEAD, 31 classes** — re-verified 2026-05-19 Group 2 pre-execution review)
- **Symbol**: `game.core.exceptions` module
- **Source refactor**: PROJ-45 (Error Handling)
- **What survived**: 31 exception classes in one ~400 LOC module. Original F-C-028 framing said 544 LOC + 27 classes; both numbers were stale at HEAD (Group 2 pre-execution review caught the drift). **The file is already UNDER the 500-LOC ceiling.** The motivation for splitting is now architectural (clear domain boundaries / import locality) rather than ceiling enforcement.
- **Why it's a problem (post-drift framing)**: 31 classes in a single module mixes 5 distinct concerns (base / strategy / simulation / LLM / image). Imports become semantically noisy: e.g., a strategy-layer module importing `StrategyException` pulls from the same module name as LLM error types. Domain submodules + a re-export aggregator improves both authorship clarity and (more importantly) makes the domain ownership explicit.
- **Suggested action**: Split by domain — `exceptions_base.py`, `exceptions_strategy.py`, `exceptions_simulation.py`, `exceptions_llm.py`, `exceptions_image.py` — with the top-level `exceptions.py` re-exporting for back-compat (a re-export shim is allowed per the convention "Preserve public API with a re-export shim only when many callers exist"). 250+ caller files justify the shim.
- **Effort**: small (still small even with the architectural framing — the LOC delta is the same; only the motivation framing changed).

**Status as of 2026-05-19: open. PENDING USER DECISION on whether the architectural-cleanup rationale is sufficient to justify Phase 4 going forward.**

**PROJ-457 disposition:** Phase 4 (PENDING USER DECISION). The 31 exception classes split into clear domains based on existing class hierarchy:
- **Base + State + Validation + Resource + Persistence** → keep in `exceptions.py` or split into `exceptions_base.py` (`GameException`, `StateException`, `FrozenStateException`, `ValidationException`, `ResourceException`, `MissingResourceException`, `PersistenceException` — 7 classes, ~110 LOC).
- **Strategy** → `exceptions_strategy.py` (`StrategyException`, `SessionInitializationError`, `EnginePhaseError`, `TurnFailedError`, `BattleResolutionError` — 5 classes, ~95 LOC).
- **Simulation** → `exceptions_simulation.py` (`SimulationException`, `ComponentException`, `FormulaException` — 3 classes, ~30 LOC).
- **LLM** → `exceptions_llm.py` (`LLMException`, `LLMConfigError`, `LLMNetworkError`, `LLMResponseError`, `LLMRateLimited`, `LLMTimeoutError`, `LLMCancelled`, `LLMUnexpectedError` — 8 classes, ~85 LOC).
- **Image** → `exceptions_image.py` (`ImageException`, `ImageConfigError`, `ImageNetworkError`, `ImageResponseError`, `ImageRateLimited`, `ImageTimeoutError`, `ImageCancelled`, `ImageUnexpectedError` — 8 classes, ~80 LOC).

Total 31 classes across 5 submodules; the existing `exceptions.py` becomes a re-export aggregator (~60-80 LOC of explicit `from ... import X, Y, Z` lines + `__all__` declaration — explicit imports preferred over `import *` per convention). All 250+ caller files keep working unchanged.

---

## Cross-References

- **Codex r4 audit redesign**: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (Job 9 = PROJ-457).
- **Original bucket scan (2026-05-18)**: `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`.
- **Codex r4 dependency note**: "Sequential. Depends on: 8" → PROJ-457 depends on PROJ-456 (LOC drops after shim retirement; Phase 0 re-measures before starting).
- **Re-export shim pattern**: `docs/02_PATTERNS.md` §36 — guidance for the `exceptions.py` re-export aggregator in Phase 4.
- **File size convention**: `docs/03_CONVENTIONS.md` "File Size" — "Production files under `game/` should stay below 500 LOC. ... Preserve public API with a re-export shim only when many callers exist; migrate callers directly when few."

## Not Owned (Out of Scope)

- F-C-001..F-C-012, F-C-029 — UI back-compat shim clusters. Owned by PROJ-456.
- F-C-013, F-C-014 — protocol-layer residue. Owned by PROJ-449.
- F-C-015 — `stat_rows_dynamic.py` `LABEL_ABBREV`. Owned by PROJ-453.
- F-C-016 — `tests/fixtures/README.md` stale UIWindow doc. Carried to PROJ-458.
- F-C-017 — UIWindow retrofit (5 windows). Owned by PROJ-458.
- F-C-018, F-C-019 — static guards. Landed Stages 1+2.
- F-C-020 — `tests/fixtures/strategy_entities.py` legacy kwargs. Owned by PROJ-449.
- F-C-021..F-C-026 — test-skip wallpaper findings. Out of PROJ-457 scope.
- F-C-030 — protocol `Dict[]` / `List[]` annotations. Owned by PROJ-454.
- DI-2026-05-18-002 — `transfer_dialog.py` LOC overflow. Owned by PROJ-456 (Phase 4 natural close).
- DI-2026-05-18-004 — `LABEL_ABBREV` IDs side. Owned by PROJ-453.

The other 9 over-ceiling UI files from F-C-027 (`empire_build_queue_window.py`, `event_log_window.py`, `race_summary_panel.py`, `empire_panel_window.py`, `build_queue_controller.py`, `system_tree_panel.py`, `design_selector_window.py`, `strategy_detail_fmt.py`, `new_game_setup_screen.py`) become a documented "next-touch" rule in `decisions.md` (Phase 5) — when one of them is touched for an unrelated reason, the touching agent does an extract-by-responsibility pass before merging. Codex r4: "Keep the other 10 over-ceiling simulation files as 'next touch', not inline scope" — same principle applies to the UI side.
