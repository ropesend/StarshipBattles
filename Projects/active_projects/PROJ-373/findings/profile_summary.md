# PROJ-373 — Originating profile evidence

**Captured:** 2026-05-05 — pyinstrument 5.1.2, sampling interval 1ms.
**Repro:** Launched the game under `python Tools/profile_game/profile_game.py`, opened the build queue for the home planet 3 times in a row, then quit normally.
**Session:** 57.80s wall, 38,673 samples, 57.02s CPU.

The original HTML report (22 MB) lives in
`AgentCoordination/Scratchpad/reports/profiles/profile_20260505T191424.html`
(gitignored). The session JSON was extracted to
`AgentCoordination/Scratchpad/tmp/session.json` for analysis.

---

## Per-click cost (3 clicks)

| Click | Wall time | Notes |
|-------|----------:|-------|
| 1 | 6.83s | identical breakdown across all three |
| 2 | 6.82s | |
| 3 | 6.96s | |
| **Total** | **20.61s** | 35.7% of the 58s session |

Every click goes `_handle_button_press` → `strategy_screen.on_build_yard_click` →
`strategy_build_queue_manager.on_build_yard_click` (line 71) →
`BuildQueueScreen.__init__` ([build_queue_screen.py:48](../../../../game/ui/screens/build_queue_screen.py#L48)).

Each `__init__` rebuilds the entire UI tree from scratch. Per-click breakdown:

```
6.9s  BuildQueueScreen.__init__
├─ 4.4s  create_all_panels                                 (build_queue_panel_factory.py:136)
│  ├─ 2.8s  _create_build_queue_panel                      (build_queue_panel_factory.py:338)
│  │  ├─ 2.0s  VirtualTable.__init__                       (virtual_table.py:58)
│  │  │  ├─ 1.5s  _rebuild_row_pool                        (virtual_table.py:143)   ← single biggest leaf
│  │  │  └─ 0.4s  _build_containers (panel + rounded rect)
│  │  └─ 0.4s × 2  sub-panels (rounded rect rebuild each)
│  └─ 0.9s  _create_background                             (build_queue_panel_factory.py:192)
└─ 2.4s  _refresh_items_list                               (build_queue_screen.py:362)
   └─ 2.2s  load_designs_by_category                       (build_queue_controller.py:137)
      └─ 2.2s  _validate_designs                           (build_queue_controller.py:193)
         └─ N × validate                                   (design_validator.py:53)
            └─ Ship.from_dict → ship_serialization._load_components
```

All `pygame_gui` panel construction time funnels into
`rounded_rect_drawable_shape.redraw_state` re-rasterizing surfaces from theme
data. The same designs are re-deserialized and re-validated every click.

---

## What this profile does NOT cover

- Other slow interactions in the game (every project should run its own
  reproduction profile).
- First-time vs. repeat opens: all three samples were repeats. First-open
  cost is presumably similar but unmeasured.
- Different build yards: the user opened the same yard three times. State
  unique to a yard (vs. shared UI shell) is inferred from code, not measured.

---

## Optimization targets — ranked by ROI

| # | Target | Saves/click | Phase |
|---|--------|------------:|-------|
| 1 | Cache `_validate_designs` results | ~2.2s | Phase 1 |
| 2 | Reuse `BuildQueueScreen` instance across opens | ~3.5s+ | Phase 2 |
| 3 | Pool/lazy-build VirtualTable rows | ~1.5s (subsumed if Phase 2 lands) | Phase 3 |
| 4 | Reduce rounded-rect drawable cost (theme/pre-bake) | ~3s residual | Phase 4 |

#1 and #2 together drop a 6.9s click to well under 1s; #3 and #4 finish the
job and benefit any other panel-heavy UI in the game.
