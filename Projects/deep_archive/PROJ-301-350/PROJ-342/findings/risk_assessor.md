# Risk Assessor Findings: PROJ-342

**Analyst:** Risk Assessor role (Phase B swarm)
**Date:** 2026-05-04

> The Risk Assessor returned findings as text rather than file. Captured here for the project record.

## Risk Summary

| # | Risk | Probability | Impact | Mitigation Status |
|---|------|-------------|--------|-------------------|
| 1 | Resize race vs `pygame.display.get_surface()` | Medium | Visual glitch | Pre-existing; `_require_display_surface()` adds clarity but not coverage. Document as known. |
| 2 | TestLabScreen positional-arg test breakage | Low-Med | Test breakage | Plan covers via Phase 5; verified no hidden constructors. |
| 3 | `BattleScreen._battle_service` replacement creating stale ref in `_ensure_engine` | Medium | Runtime crash | **Pre-existing**, not introduced by refactor. Sequencing in `TestLabExecutor` ensures `_ensure_engine` runs before `start_battle`, so timing is safe. |
| 4 | `pygame.display.get_surface()` vs `App.screen` lifetime | Low | Visual corruption | No production caller invokes `set_mode` outside `RunLoop`/`app_bootstrap`. Same as current behavior. |
| 5 | Headless test contexts hitting `_render_progress` without display | Low | Test failure | `_require_display_surface()` raises `RuntimeError` with clear message — better diagnostics than current. |
| 6 | Deleted service exports causing `ImportError` | Low | ImportError | Plan covers in Phase 4; no plugin-discovery use. |
| 7 | Persistent data referencing deleted classes | Very Low | Data loss | No serialization of services; combat_lab is a test harness, not a save target. |
| 8 | `BattleStateViewer` resize regression | Already happening | UI glitch | Plan covers explicitly in Phase 2 Task 2.4. |
| 9 | `screen_router` construction-order assumption | Low | TypeError at startup | Type hints catch it; current order is correct. |

## Detailed Findings

(See Risk Assessor agent output transcript for full text.)

### Risk 1 — `pygame.display.get_surface()` resize race

The risk window is inside `RunLoop._on_resize` between `pygame.display.set_mode()` returning a new surface and `BootstrapResult.screen` being updated. During that gap, `pygame.display.get_surface()` returns the new surface (canonical pygame behavior), while `self.boot.screen` is still pointing at the old surface. **In practice this means using `pygame.display.get_surface()` is MORE up-to-date than `self.boot.screen` during a resize**, not less. The risk is over-stated for our use case.

### Risk 3 — Stale `_battle_service` reference

`BattleScreen.start_battle()` at `battle_screen.py:145` replaces `self._battle_service = controller.service`. After that, `self.battle_scene._battle_service` reads the new service. `_ensure_engine` calls `create_battle()` on whatever `_battle_service` resolves to *at the moment of the call* — there's no stale reference because `_battle_service` is read fresh each time via attribute access on `battle_scene`.

The Risk Assessor's concern that "private `_battle_service` access is fragile" is a fair architectural critique, but it's pre-existing and not introduced by PROJ-342. Recommended for follow-up debt.

### Risk 5 — Headless display

`pygame.display.get_surface()` returning `None` is the exact case `_require_display_surface()` is designed to catch. Replacing an opaque `AttributeError: 'NoneType' object has no attribute 'fill'` with `RuntimeError: Display surface not initialized; ...` is a strict diagnostic improvement.

## Recommendations folded into plan

- **Risk 8 (resize forwarding):** already in Phase 2 Task 2.4.
- **Risk 5 (headless display):** already covered by `_require_display_surface()` helper in Phase 2 Task 2.2.
- **Risk 3 (`_ensure_engine` fragility):** documented as follow-up debt; not in scope for PROJ-342 since it's pre-existing.

## Recommendations NOT folded

- **Parameterizing `_ensure_engine` to accept `battle_scene` as argument**: scope creep without clear benefit. The closure capture is fine.
- **Adding a resize-during-batch test in Phase 7**: useful but lower-priority than the existing manual smoke; can be added if Phase 7 surfaces a real concern.
