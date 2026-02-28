# PROJ-162: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Baseline:** 11,959 passed, 12 failed, 2 skipped, 11 warnings

12 tests fail across 5 test files in `tests/unit/ui/screens/`. Root causes fall into 4 categories:

### Category A: MagicMock as UIManager (2 failures)
`test_cargo_quick_dialog_issuance.py` uses `MagicMock()` instead of `pygame_gui.UIManager((800,600))`.
When `CargoQuickDialog.__init__` calls `super().__init__()`, pygame_gui does numeric comparisons on mock objects → `TypeError`.

### Category B: Stale TransferDialog Tests (3 failures)
`test_transfer_dialog.py` is out of sync with production code:
- `_update_cargo_list()` now requires 2 args (source, target); test passes 1
- Source count assertion wrong (4 sources now, test expects 3 — uncolonized planets now included)
- `_get_inventory_items()` does `passengers > 0` on MagicMock

### Category C: camera.zoom MagicMock Comparison (6 failures)
`test_strategy_input_handler_core.py` (3) + `test_strategy_input_handler_transfer.py` (3).
`_resolve_click_target()` accesses `self.scene.camera.zoom >= 0.5` — MagicMock has no numeric value.

### Category D: Missing get_cargo_capacity Mock (1 failure)
`test_fleet_report_filters.py::test_sort_by_transport` — `make_mock_ship()` doesn't mock `get_cargo_capacity()`.
Sort function calls `ship.get_cargo_capacity('passengers')` which returns MagicMock → comparison fails.

## Swarm Findings Summary

### Architecture
- **Service layer** (`game/strategy/services/`) contains stateless utility classes: `FleetCargoProjector`, `FleetSpeedCalculator`, `ShipStatsCalculator`
- UI already imports services directly (not through facade): `FleetSpeedCalculator` and `ShipStatsCalculator` in `column_manager.py` and `fleet_report_filters.py`
- Facade is for command dispatch (writes), not query utilities (reads)
- **CargoTransferService fits naturally in `game/strategy/services/`** and should be imported directly by UI

### Key Patterns to Reuse
- **FleetCargoProjector**: `game/strategy/services/fleet_cargo_projector.py` — static methods, no UI dependency, pure logic
- **Bypass-init test pattern**: `tests/unit/ui/screens/test_event_log_window.py:43-79` — `__new__()` with patched `__init__`
- **Real UIManager pattern**: `tests/unit/ui/screens/test_cargo_quick_dialog.py:22-24` — `pygame_gui.UIManager((800,600))`

### Dependencies & Risks
1. **TransferDialog accesses `facade._session` directly** (line 144) — breaks encapsulation. Out of scope to fix but noted.
2. **Fleet object vs FleetInfo DTO inconsistency** — dialogs receive raw fleet but also query facade for FleetInfo. Out of scope.
3. **No circular dependency risk** — service reads from DTOs and facade, never imports UI or engines.

### Opportunities Discovered
- `_populate_load_items()` and `_populate_unload_items()` logic in CargoQuickDialog duplicates `_get_inventory_items()` in TransferDialog
- 18 DIAG log statements in `cargo_quick_dialog.py` are leftover debug noise
- TransferDialog has debug label (`lbl_debug`) that should also be cleaned up (out of scope)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
