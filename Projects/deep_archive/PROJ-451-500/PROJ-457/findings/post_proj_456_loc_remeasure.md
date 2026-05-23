# PROJ-457 Phase 0: Post-PROJ-456 LOC re-measurement

**Measured:** 2026-05-19, post-PROJ-456 merge to main (`244c1fa16`).
**Method:** `Path(f).read_text().splitlines()` count (PowerShell `Get-Content | Measure-Object -Line` returns identical values; `wc.exe` unreliable on this checkout per codex r5 audit).

## All 12 F-C-027 files

| File | Pre-PROJ-456 LOC (plan) | Post-PROJ-456 LOC | Δ | Over 500? |
|------|------------------------:|------------------:|---:|:---------:|
| `game/ui/screens/build_queue_screen.py` | 961 | 958 | −3 | yes |
| `game/ui/screens/planet_list_window.py` | 862 (plan); 746 (HEAD pre-PROJ-456) | 862 | 0 / +116 | yes |
| `game/ui/screens/test_lab/screen.py` | 744 (plan); 614 (HEAD pre-PROJ-456) | 744 | 0 / +130 | yes |
| `game/ui/screens/new_game_setup_screen.py` | 734 | 684 | −50 | yes |
| `game/ui/screens/empire_build_queue_window.py` | 734 | 734 | 0 | yes |
| `game/ui/screens/event_log_window.py` | 732 | 735 | +3 | yes |
| `game/ui/panels/race_summary_panel.py` | 732 | 732 | 0 | yes |
| `game/ui/screens/empire_panel_window.py` | 724 | 724 | 0 | yes |
| `game/ui/panels/build_queue_controller.py` | 723 | 723 | 0 | yes |
| `game/ui/panels/system_tree_panel.py` | 711 | 711 | 0 | yes |
| `game/ui/screens/design_selector_window.py` | 708 | 708 | 0 | yes |
| `game/ui/screens/strategy_detail_fmt.py` | 707 | 707 | 0 | yes |

## Top-3 (Phase 1-3 targets) verdict

All three top-3 targets remain OVER 500 LOC post-PROJ-456. No rescope needed:

- **`build_queue_screen.py`** 958 — needs ~460 LOC extracted (Phase 1).
- **`planet_list_window.py`** 862 — needs ~365 LOC extracted (Phase 2).
- **`test_lab/screen.py`** 744 — needs ~245 LOC extracted (Phase 3).

The plan's "861 HEAD" figure for planet_list_window and "614 HEAD" figure for test_lab/screen were the wrong values; the live HEAD figures are 862 and 744 respectively (matching the original bucket scan). Plan figures came from a stale measurement.

## Phase 4 — `exceptions.py` (F-C-028)

`game/core/exceptions.py` was 411 LOC pre-PROJ-456 and is unchanged post-PROJ-456 (no PROJ-456 work touched it). The file remains UNDER the 500 ceiling. The Phase 4 work is justified by architectural rationale only — 31 exception classes across 5 domains warrant a per-domain split for import locality + clarity. **User decision pending** per Phase 0 Task 0.3 escalation gate semantics.

## Phase 0 conclusion

No rescope to Phases 1-3. Phase 4 still requires a user decision before starting (file is below ceiling).
