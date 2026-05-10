# PROJ-398 File Manifest

> Populated during PROJ-406 reconciliation from implementation commits
> `c6e0113ec`, `e14d7f1ce`, `6744b44e1`.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_strategy_colonization.py` | Test (new) | FND-017 — `TestHandleColonizeDesignation` (4 tests covering fleet=None, no-system, no-colonizable, unowned-planet-prompt) |
| `tests/unit/ui/test_camera.py` | Test | FND-012 — `TestCameraHexAtScreen` (3 tests exercising real `screen_to_world -> pixel_to_hex` chain) |
| `game/ui/screens/strategy_click_dispatcher.py` | Production | FND-031 / FND-032 — extract `_handle_dialog_mode_click(mx, my, button, dialog_method_name, *extra_args)`; collapse TRANSFER / DROP_CARGO / LOAD_CARGO to one-line delegations |
| `tests/unit/ui/screens/test_strategy_click_dispatcher.py` | Test | FND-031 / FND-032 — 4 new tests covering all three modes + cancel branch |
| `game/strategy/services/ability_iterator.py` | Production | FND-041 — `_star_provider` collapses 26 LOC -> 5-line delegation to `_iter_hex_filtered_sources` |
| `game/strategy/services/ability_sources/star.py` | Production | FND-041 — `affects_hex` widened to return True for system-shaped scopes; `_has_system_scope_ability()` helper added |

**No production / test code was modified by PROJ-406.** PROJ-406 only updates the manifest table to reflect the actually-shipped change set.
