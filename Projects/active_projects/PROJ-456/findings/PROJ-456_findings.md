# PROJ-456 Findings — UI Back-Compat Shim Retirement Sweep

> Consolidated from `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md` (2026-05-18 scan).
> The original scan flagged ~30 findings across UI + Core + Tests. This file extracts the 14 entries
> that PROJ-456 owns. File:line refs re-verified against repo HEAD on 2026-05-19.

## Owned Findings

| ID | Severity | Category | File | Status as of 2026-05-19 |
|----|----------|----------|------|--------------------------|
| F-C-001 | low | obsolete-code | `game/ui/screens/battle_setup_state.py:172` | Open. Shim block confirmed at lines 172-192. `side_0`/`side_1` referenced in 5 prod+test files (re-verified via grep). |
| F-C-002 | low | polish | `game/ui/screens/transfer_dialog.py:412` | Open. `except Exception:` at line 412 still lacks the `# Intentional broad catch: <reason>` marker. Body comment exists but is not the convention-compliant signal. |
| F-C-003 | low | obsolete-code | `game/ui/screens/transfer_dialog.py:279-286` | Open. Three method shims (`_extract_dropdown_value`, `_format_pending`, `_discover_pod_designs`) confirmed at exact lines. |
| F-C-004 | low | obsolete-code | `game/ui/screens/strategy_renderer.py:107-130` | Open. Six cache-attr shims (`_bg_image` / `_bg_scaled` / `_bg_scaled_size` / `_bg_brightness` / `_hex_outline_cache` / `_hex_outline_cache_turn`) confirmed at exact lines. |
| F-C-005 | low | obsolete-code | `game/ui/screens/strategy_render/grid.py:104` | Open. Module-level `draw_grid(r, screen)` confirmed at line 104. Consumed only by `tests/unit/ui/screens/test_strategy_renderer.py` and `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py`. Production callers route through `GridLayer.draw`. |
| F-C-006 | low | obsolete-code | `game/ui/screens/build_queue_screen.py:84-90` | Open. `build_context` legacy positional/keyword preserved alongside `initial_yard` **on the `BuildQueueScreen` constructor only**. Re-verified 2026-05-19 (codex r5 audit): the `BuildQueueController(build_context=...)` constructor at `game/ui/panels/build_queue_controller.py:66-85` is a legitimate, non-legacy API and is OUT OF SCOPE. **In-scope callers:** `game/ui/screens/strategy_build_queue_manager.py:128` (production), `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (~25 test call sites). **Out-of-scope (controller API):** `tests/unit/ui/panels/test_build_queue_controller.py:57-87`, `tests/unit/ui/panels/test_build_queue_catalog_threading.py:20-30`, `tests/unit/strategy/engine/test_production_repro.py:150-157,201-206`, `tests/integration/ui/build_queue_screen/test_controller_multi_queue.py:77-116`. |
| F-C-007 | low | obsolete-code | `game/ui/screens/race_setup/screen.py:277-285` | Open. `_description_controller` property + setter confirmed at exact lines, delegating to `self._controller.description_controller` / `self._controller.attach_description_controller(value)`. |
| F-C-008 | low | obsolete-code | `game/ui/screens/new_game_setup_screen.py:272-321` | Open. Six VM property shims (`player_count`, `galaxy_type`, `system_count`, `player_races`, `active_race_modal`, `race_modal_player_index`) confirmed at exact lines (the comment header is at line 272; first property opens at 275). File LOC: 734 (still over the 500-LOC ceiling). |
| F-C-009 | low | obsolete-code | `game/ui/screens/battle_setup/screen.py:93-205` | Open. 11 shim properties (7 VM + 4 controller) confirmed. **LOC re-measure**: file is 189 LOC at HEAD (vs the bucket-scan's "559 LOC" figure from 2026-05-18). The "shims push file over 500 LOC" framing in the original finding no longer applies; the shims still merit removal for the foot-gun reason (dual paths to same state). |
| F-C-010 | low | obsolete-code | `game/ui/screens/orders_window.py:464-475` | Open. `_get_order_description` shim confirmed at exact lines, delegating to `self._order_describer.describe(order, self.entity)`. |
| F-C-011 | low | obsolete-code | `game/ui/screens/transfer_dialog.py:58-66` | Open. Sentinel re-exports (`MAX_LOAD`, `MAX_DROP`) at lines 58-62, class-level layout constants at lines 64-86. Per the file at HEAD, the layout block is broader than the original `:58-66` range (extends through line 86). |
| F-C-012 | low | obsolete-code | `game/ui/screens/event_log_window.py:113-116` | Open. `empire_name=None` back-compat default + title fallback confirmed at exact lines (within the `__init__` docstring + body). |
| F-C-029 | medium | test-inconsistency | `tests/unit/ui/screens/test_transfer_dialog.py:74-75`, `test_transfer_dialog_enhanced.py:49`, `test_transfer_dialog_characterization.py` (70+ refs) | Open. Concrete grep count: 69 occurrences across 3 test files of `dialog._current_source` / `dialog._current_target` / `dialog._row_data` / `dialog._filter_empty` / `dialog.available_sources` / `dialog.available_targets` / `dialog.pending_transfers`. |
| DI-2026-05-18-002 | low | tech-debt | `game/ui/screens/transfer_dialog.py:1` (file-level) | Open. Re-measured 2026-05-19 at HEAD: **448 LOC** (already under the 500 ceiling). The original DI entry's "23-LOC overflow" framing is stale — LOC dropped via intervening work. Closure motivation is now retiring the shim residue (F-C-003 + F-C-011 + F-C-029 + the dialog-level property shims listed in the DI entry), not LOC enforcement. |

## Cross-References

- **Codex r4 audit redesign**: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (Job 8 = PROJ-456).
- **Original bucket scan (2026-05-18)**: `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`.
- **Codex r4 risk flag**: "Job 8 is still the biggest review burden in the new plan. If the diff starts looking like 'every UI screen changed', cut it into two PRs by feature family, not by old project bucket." → handled by phase ordering (smallest-first; transfer_dialog cluster in Phase 4; biggest-3-cluster Phase 5).
- **Pattern #33 (UIWindow bypass-init)**: `docs/02_PATTERNS.md` §33 — relevant for tests that reach through shims via `bypass_init`; sweep MUST preserve the bypass-init test paths intact (do not delete a shim while it is still a write target from a bypass-init test fixture).
- **DI-2026-05-18-004** (LABEL_ABBREV) — owned by **PROJ-452** (catalog-driven resource surfaces), not by PROJ-456. F-C-015 (the label-side companion) is also out of scope for PROJ-456 even though it touches `stat_rows_dynamic.py`; that file is the `LABEL_ABBREV` site. Coordinator fix 2026-05-19: previous attribution to PROJ-453 was incorrect — PROJ-453 is engine + services polish, PROJ-452 is the catalog/resource-surfaces project.

## Not Owned (Out of Scope)

- F-C-013, F-C-014 — protocol-layer (`IShipInstance.cargo_contents` etc.). Owned by PROJ-449.
- F-C-015 — `stat_rows_dynamic.py` LABEL_ABBREV — owned by **PROJ-452** (corrected 2026-05-19; was incorrectly attributed to PROJ-453).
- F-C-016 — `tests/fixtures/README.md` stale UIWindow doc — pure docs touch; carried forward to PROJ-458 (UIWindow retrofit completion) since the README anchors to that pattern.
- F-C-017 — Deferred UIWindow retrofit (5 windows) — owned by **PROJ-458**.
- F-C-018, F-C-019 — Static guards (DesignLibrary / `_ACTIVATABLE_ABILITIES`) — landed in Stage 2; confirmed in r4 audit.
- F-C-020 — `tests/fixtures/strategy_entities.py` legacy kwargs — owned by PROJ-449 (entity wrapper retirement).
- F-C-021..F-C-026 — test-skip wallpaper findings; out of PROJ-456 scope. Either resolved in Stages 1+2 (F-C-021 done per r4) or carried as separate "test wallpaper" cleanup.
- F-C-027 — UI file LOC overflow (12 files) — owned by **PROJ-457**.
- F-C-028 — `game/core/exceptions.py` split — owned by **PROJ-457**.
- F-C-030 — Protocol `Dict[]`/`List[]` legacy annotations — owned by PROJ-454 (engine/service surface polish) or its sibling.
