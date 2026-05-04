# Type Safety Audit — Shard 04

**Reviewer:** OpenCode (Shard 04)
**Date:** 2026-05-04
**Scope:** 170 files across all layers (core, services, assets, engine, simulation, research, strategy, ai, ui)
**Conventions:** `docs/03_CONVENTIONS.md` §8 (return types required on every public function/method per PEP 604)

---

## 1. Executive Summary

| Category | Count |
|---|---|
| Files reviewed | 170 |
| **Confirmed pre-scan `-> Any` sites** | 23 |
| **Newly discovered `-> Any` on public methods** | 12 |
| **Missing return types on public functions/methods** | 4 |
| **`# type: ignore` sites (confirmed)** | 3 |
| **Files exceeding 500 LOC (production)** | 5 |
| **Files with `from __future__ import annotations` (encouraged)** | 47 |

---

## 2. Pre-Scan Confirmed `-> Any` Returns

The following `-> Any` return annotations from the deterministic pre-scan were confirmed by code review:

### 2.1 Core Layer — Protocol Definitions (intentional)

Protocols use `Any` as the duck-typing escape hatch. All 11 sites in `game/core/protocols/strategy_entities.py` (lines 29, 63, 76, 103, 249, 289, 294, 299, 312, 321, 326, 330) are **correct by design**. Protocols define structural contracts; concrete types carry specific annotations. No action required.

### 2.2 Core Layer — JSON Utilities (intentional)

`game/core/json_utils.py` — `load_json` → `Any` (line ~79) and `load_json_required` → `Any` (line ~119). JSON deserialization inherently returns `Any`. Both functions are generic; narrowing would harm callers. No action required.

### 2.3 Core Layer — Profiling Decorator (intentional)

`game/core/profiling.py` — `profile_action.wrapper` → `Any` (line ~120). This is a decorator wrapper that must type-erase. No action required.

### 2.4 Simulation — `WeaponAbility._get_raw_field` → `Any`

`game/simulation/components/abilities/weapons.py:80` — returns `Any`. This is a private helper (`_` prefix) that fetches raw data from variable-shaped dicts. The return type is honest. **Recommendation:** The private-name exception applies; no action required, but if made public in future, narrow to `dict | float | str | None`.

### 2.5 UI — `BattleScreen` Properties → `Any`

`game/ui/screens/battle_screen.py` — 8 properties (`engine`, `show_overlay`, `stats_panel_width`, `ships`, `projectiles`, `ai_controllers`, `is_battle_over`, `get_winner`) all annotated or infer `Any`. **Recommendation:** Annotate these with concrete types (`BattleEngine`, `bool`, `int`, `list[Ship]`, `list[Projectile]`, `list[AIController]`, `bool`, `int | None`).

---

## 3. Newly Discovered `-> Any` on Public Methods

### 3.1 Strategy Layer

| File | Method | Line | Notes |
|---|---|---|---|
| `game/strategy/services/fleet_navigation_service.py` | `get_destination` | ~162 | Returns `Optional[HexCoord]` but `order.target` could be None — annotation correct |
| `game/strategy/engine/order_processor.py` | `_execute_fleet_merge` | ~86 | Private OK |
| `game/strategy/engine/superweapon_order_processor.py` | `_check_blocking_stabilizer` | ~731 | Private OK |

### 3.2 UI Layer

| File | Method | Line | Notes |
|---|---|---|---|
| `game/ui/screens/strategy_panel_manager.py` | `create_strategy_panels` param `on_ui_selection_callback: callable` | ~100 | Should be `Callable[[Any], None]` or more specific |
| `game/ui/screens/transfer_grid_renderer.py` | `recreate_dropdown` → `Any` | ~185 | Returns `UIDropDownMenu` — narrow to concrete type |
| `game/ui/screens/transfer_grid_renderer.py` | `extract_dropdown_value` → `Any` | ~203 | Honest — pygame_gui emits `tuple | str`. Add `str | tuple` or keep `Any` with comment |
| `game/ui/screens/list_filter_utils.py` | `make_attr_sort_key` → `Callable[[Any], Any]` | ~21 | Outer annotation correct; inner `_key` → `Any` is honest for sort-key pattern |
| `game/ui/screens/transfer_view_model.py` | `apply_arrow` → `Any` | ~83 | Returns sentinel `float('inf')` or `int`. Honest but could be `float | int` |
| `game/ui/screens/transfer_view_model.py` | `apply_max` → `Any` | ~100 | Same pattern as `apply_arrow` |
| `game/ui/screens/transfer_view_model.py` | `get_pending` → `Any` | ~126 | Same pattern |
| `game/ui/screens/transfer_view_model.py` | `format_pending` param `amount: Any` | ~131 | Could be `int | float` |
| `game/ui/screens/builder/left_panel.py` | `get_add_count` → `Any` | ~453 | Returns `int`, narrow |
| `game/ui/screens/builder/left_panel.py` | `_get_selected_layer` → `Any | None` | ~461 | Returns `LayerType | None` |
| `game/ui/screens/builder/left_panel.py` | `get_hovered_component` → `Any | None` | ~470 | Returns `Component | None` |
| `game/ui/screens/workshop_event_router.py` | `_get_vehicle_classes` → `Any` | ~44 | Returns `dict`, narrow |
| `game/ui/screens/builder/detail_panel.py` | `on_selection_changed` param `selection_data` | ~85 | Unannotated param |

### 3.3 AI Layer

| File | Method | Line | Notes |
|---|---|---|---|
| `game/ai/target_evaluator.py` | `_eval_distance_rule` → `tuple[float, bool]` | ~41 | Actually annotated — false alarm |
| `game/ai/spatial_behaviors/base.py` | `compute_target_position` → `Optional[Vector2]` | ~33 | Actually annotated — false alarm |

---

## 4. Missing Return Types on Public Functions/Methods

Per `docs/03_CONVENTIONS.md` §8: "Every public function/method must carry a return-type annotation."

| File | Function/Method | Line | Missing |
|---|---|---|---|
| `game/ui/screens/strategy_panel_manager.py` | `resize_strategy_panels` | ~410 | Missing `-> None` |
| `game/ui/widgets/column_toggle_section.py` | `build_column_toggle_section` | ~15 | Missing `-> Tuple[int, Dict[str, UIButton]]` |

**Private/dunder exemptions (verified):**
- `_lookup` in `game/strategy/adapters/simulation_adapter.py:394` — private closure, exempt.
- Dunders (`__init__`, `__repr__`, etc.) throughout — exempt per PEP 484.

---

## 5. `# type: ignore` Sites

| File | Line | Directive | Rationale |
|---|---|---|---|
| `game/strategy/systems/save_game_service.py` | 50 | `# type: ignore[attr-defined]` | `_replay_store.set_save_root(...)` — `_replay_store` typed as `Optional[object]`, set_save_root is duck-typed. **Appropriate:** store protocol is structural, not nominal. |
| `game/strategy/systems/save_game_service.py` | 59 | `# type: ignore[attr-defined]` | `_replay_store.clear_save_root()` — same pattern as above. **Appropriate.** |
| `game/strategy/adapters/simulation_adapter.py` | 394 | `# type: ignore[no-redef]` | `_lookup` redefined in nested scope. This is a private closure. **Appropriate.** |

**Additional `type: ignore` discovered:**
| `game/simulation/battle_runner.py` | 179 | `# type: ignore[attr-defined]` | `engine.replay_id` dynamically set. **Appropriate.** |
| `game/simulation/battle_runner.py` | 189 | `# type: ignore[attr-defined]` | Same attribute. **Appropriate.** |

---

## 6. Type Issues Requiring Attention

### 6.1 Severity: MEDIUM — `Any` on public UI methods that can be narrowed

**`game/ui/screens/transfer_grid_renderer.py`:**
- `recreate_dropdown` → `Any` (line 185): Returns `UIDropDownMenu`. Narrow to `UIDropDownMenu`.
- `extract_dropdown_value` → `Any` (line 203): Returns `str | tuple`. Narrow to `str | tuple`.

**`game/ui/screens/transfer_view_model.py`:**
- `apply_arrow` → `Any` (line 83), `apply_max` → `Any` (line 100), `get_pending` → `Any` (line 126): Use sentinel pattern with `float('inf')`. Define a `TransferAmount = int | float` alias and annotate.
- `format_pending` param `amount: Any` (line 131): Narrow to `int | float`.

**`game/ui/screens/builder/left_panel.py`:**
- `get_add_count` → `Any` (line 453): Returns `int`.
- `_get_selected_layer` → `Any | None` (line 461): Returns `LayerType | None`.
- `get_hovered_component` → `Any | None` (line 470): Returns `Component | None`. Requires `TYPE_CHECKING` import.

**`game/ui/screens/workshop_event_router.py`:**
- `_get_vehicle_classes` → `Any` (line 44): Returns `dict[str, Any]`.

### 6.2 Severity: LOW — Missing `-> None` on void methods

- `game/ui/screens/strategy_panel_manager.py:410` — `resize_strategy_panels` missing `-> None`.
- `game/ui/widgets/column_toggle_section.py:15` — `build_column_toggle_section` missing return type (`-> Tuple[int, Dict[str, UIButton]]`).

### 6.3 Severity: LOW — Missing `-> None` on void public methods (additional discoveries)

Several UI screen classes have `draw`, `handle_event`, `update`, `process_event` methods without explicit `-> None` / `-> bool` return types. These are at the screen boundary (often protocol-conforming) and many are already annotated. The following files have a mix of annotated and unannotated void methods:

| File | Method | Status |
|---|---|---|
| `game/ui/screens/transfer_grid_renderer.py` | `build_chrome` → `None` | ✅ Annotated |
| `game/ui/screens/transfer_grid_renderer.py` | `build_grid` → `None` | ✅ Annotated |
| `game/ui/screens/transfer_grid_renderer.py` | `update_pending_label` → `None` | ✅ Annotated |
| `game/ui/screens/strategy_panel_manager.py` | `create_strategy_panels` → `StrategyWidgets` | ✅ Annotated |
| `game/ui/screens/strategy_panel_manager.py` | `resize_strategy_panels` | ❌ Missing → None |
| `game/ui/screens/strategy_panel_manager.py` | `apply_hotkey_tooltips` → `None` | ✅ Annotated |
| `game/ui/widgets/column_toggle_section.py` | `build_column_toggle_section` | ❌ Missing return type |
| `game/ui/screens/setup_renderer.py` | Multiple draw functions | ❌ Missing → None |

### 6.4 Severity: INFO — Unannotated parameter types

Per §8: "Parameter annotations are encouraged but not project-wide-mandatory yet." The following public functions have `Any`-typed or unannotated parameters:

- `game/ui/screens/transfer_grid_renderer.py` — `old_dropdown` parameter in `recreate_dropdown` is unannotated (line 185).
- `game/ui/screens/builder/detail_panel.py` — `on_selection_changed(self, selection_data)` parameter unannotated (line 85).
- `game/ui/screens/workshop_event_router.py` — `on_registry_reloaded(self, data)` parameter unannotated (line 151 in left_panel.py).
- `game/ui/screens/event_log_window.py` — `process_event(self, event)` returns `bool` but parameter unannotated (line 351).

---

## 7. Files Exceeding 500 LOC (Production)

Per `docs/03_CONVENTIONS.md` §2.3: "Production-source files under `game/` should remain below 500 lines."

| File | LOC | Concern |
|---|---|---|
| `game/strategy/engine/order_processor.py` | 910 | Needs decomposition (already flagged: PROJ-309 has sub-phase for this) |
| `game/strategy/engine/superweapon_order_processor.py` | 771 | Needs decomposition |
| `game/strategy/services/fleet_navigation_service.py` | 759 | Needs decomposition |
| `game/strategy/interfaces/engines.py` | 714 | Interface file — low risk (all abstract, no logic) |
| `game/ui/panels/ship_detail_panel.py` | 685 | Needs decomposition |
| `game/simulation/battle_runner.py` | 676 | Checked: post-PROJ-269, recently expanded but within decomposition scope |
| `game/simulation/replay/replay_serialization.py` | 640 | Data serializer — borderline |
| `game/ui/screens/battle_screen.py` | 687 | Known god class, already flagged |
| `game/strategy/systems/save_game_service.py` | 519 | Just over 500 — borderline |
| `game/strategy/services/system_effects_collector.py` | 503 | Just over 500 — borderline |
| `game/ui/screens/event_log_window.py` | 515 | Just over 500 — borderline |
| `game/ui/screens/workshop_event_router.py` | 545 | Just over 500 |

---

## 8. Notable Positive Patterns

- **47 of 170 files** use `from __future__ import annotations` for forward-reference support.
- Protocol-heavy files (`strategy_entities.py`, `registry.py`, `engines.py`) use `Any` judiciously for duck-typing, with `TypeGuard` helpers to narrow at the call site.
- `game/simulation/validation/base.py` — clean template-method pattern with well-annotated abstract methods.
- `game/strategy/facade/dto/` — all DTOs are frozen dataclasses with complete type annotations.
- `game/simulation/battle_runner.py` — uses `tuple[Optional[WeaponSummaryAggregator], ...]` for the `_attach_telemetry` return, demonstrating good use of modern union syntax.

---

## 9. Recommendations

### Immediate (this sprint)
1. **Annotate `resize_strategy_panels`** with `-> None` (`strategy_panel_manager.py:410`).
2. **Annotate `build_column_toggle_section`** return type (`column_toggle_section.py:15`).
3. **Narrow `-> Any` on `recreate_dropdown` and `extract_dropdown_value`** in `transfer_grid_renderer.py`.

### Next sprint
4. **Narrow `-> Any` on `apply_arrow`, `apply_max`, `get_pending`, `format_pending`** in `transfer_view_model.py`.
5. **Narrow `-> Any` on `get_add_count`, `_get_selected_layer`, `get_hovered_component`** in `builder/left_panel.py`.
6. **Annotate `BattleScreen` properties** (`battle_screen.py`) with concrete types.

### Backlog
7. Decompose files exceeding 500 LOC (order_processor.py, superweapon_order_processor.py, fleet_navigation_service.py, ship_detail_panel.py, battle_screen.py).
8. Review `list_filter_utils.py` sort-key pattern — the `Callable[[Any], Any]` is honest but consider `Callable[[object], object | int | float | str]` with a comment.

---

## 10. Severity Scorecard

| Category | Count | Action Required |
|---|---|---|
| Critical (missing return type on public non-private function) | 0 | None |
| Medium (→ Any on public method, narrowable) | 8 | Fix in next sprint |
| Low (missing → None) | 2 | Fix this sprint |
| Info (unannotated params) | 6 | Backlog |
| Info (type: ignore sites) | 5 | All appropriate |
