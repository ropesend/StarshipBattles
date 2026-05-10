"""Transfer Dialog - Grid-based resource and cargo transfer between fleets and planets.

Shows all resource types and species in a grid with arrow buttons for
adjusting pending transfer amounts. Confirm issues batch transfer
orders.

PROJ-313: migrated to ``StrategyModalWindow`` base class.
PROJ-328 Phase C: deep MVVM split. Pending-transfer state, row data,
and pure formatting live on ``TransferViewModel``. Facade queries +
``IssueTransferCommand`` emission live on ``TransferController``.
Pygame_gui widget construction lives behind ``TransferGridRenderer``
+ ``TransferDialogUiBuilder``. Tests can swap in
``Mock{...}UiBuilder`` / ``Null{...}UiBuilder`` from
``tests/fixtures/transfer_ui_builder.py``.

The dialog itself is a thin shell: it owns the two-stage ``__init__``,
the event-routing loop, and the legacy public attribute names that
existing tests / callers depend on.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pygame
import pygame_gui

from game.core.input_actions import InputAction
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.screens.transfer_controller import TransferController
from game.ui.screens.transfer_grid_renderer import (
    ARROW_INCREMENTS_DROP,
    ARROW_INCREMENTS_LOAD,
    ARROW_LABELS_DROP,
    ARROW_LABELS_LOAD,
    TransferDialogUiBuilder,
    TransferGridRenderer,
)
from game.ui.screens.transfer_view_model import (
    RESOURCE_DISPLAY_NAMES,
    RESOURCE_TYPES,
    TransferViewModel,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class TransferDialog(StrategyModalWindow):
    """Grid-based resource transfer dialog.

    PROJ-328 Phase C: two-stage construction. Cheap state (view
    model, controller, renderer) is built in Stage 1 BEFORE the
    UIWindow shell so tests under ``bypass_init`` get a usable
    instance with the delegate graph populated. Widget construction
    is delegated to a swap-able ``ui_builder``.
    """

    # Sentinels — re-exported on the class for back-compat with
    # callers that read ``TransferDialog.MAX_LOAD`` directly. The
    # canonical home is ``TransferViewModel``.
    MAX_LOAD = TransferViewModel.MAX_LOAD
    MAX_DROP = TransferViewModel.MAX_DROP

    # Layout constants kept on the class for back-compat with any
    # caller reading them; renderer owns the real values.
    ROW_HEIGHT = TransferGridRenderer.ROW_HEIGHT
    NAME_X = TransferGridRenderer.NAME_X
    NAME_W = TransferGridRenderer.NAME_W
    SOURCE_AMT_X = TransferGridRenderer.SOURCE_AMT_X
    SOURCE_AMT_W = TransferGridRenderer.SOURCE_AMT_W
    MAX_LOAD_X = TransferGridRenderer.MAX_LOAD_X
    MAX_LOAD_W = TransferGridRenderer.MAX_LOAD_W
    LOAD_ARROWS_X = TransferGridRenderer.LOAD_ARROWS_X
    ARROW_W = TransferGridRenderer.ARROW_W
    ARROW_GAP = TransferGridRenderer.ARROW_GAP
    ARROW_COUNT = TransferGridRenderer.ARROW_COUNT
    PENDING_X = TransferGridRenderer.PENDING_X
    PENDING_W = TransferGridRenderer.PENDING_W
    ZERO_BTN_X = TransferGridRenderer.ZERO_BTN_X
    ZERO_BTN_W = TransferGridRenderer.ZERO_BTN_W
    DROP_ARROWS_X = TransferGridRenderer.DROP_ARROWS_X
    MAX_DROP_X = TransferGridRenderer.MAX_DROP_X
    MAX_DROP_W = TransferGridRenderer.MAX_DROP_W
    TARGET_AMT_X = TransferGridRenderer.TARGET_AMT_X
    TARGET_AMT_W = TransferGridRenderer.TARGET_AMT_W

    def __init__(
        self,
        relative_rect,
        manager,
        source_fleet,
        hex_coord,
        scene,
        *,
        window_manager: "StrategyWindowManager | None",
        input_mapper: Optional["InputMapper"] = None,
        view_model: Optional[TransferViewModel] = None,
        controller: Optional[TransferController] = None,
        renderer: Optional[TransferGridRenderer] = None,
        ui_builder: Optional[TransferDialogUiBuilder] = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            relative_rect: Window position + size.
            manager: pygame_gui UIManager.
            source_fleet: Fleet that initiated the transfer.
            hex_coord: Hex coordinate context for source/target
                discovery.
            scene: Strategy scene (for facade + session access).
            window_manager: StrategyWindowManager (or None when
                opened outside the strategy screen).
            input_mapper: Optional InputMapper for hotkey tooltips.
            view_model / controller / renderer / ui_builder:
                PROJ-328 Phase C delegate seams. Defaults instantiate
                the production implementations; tests pass
                ``MockTransferUiBuilder`` / ``NullTransferUiBuilder``.
        """
        # ---- Stage 1: cheap state + delegates ----
        self.source_fleet = source_fleet
        self.hex_coord = hex_coord
        self.scene = scene
        self.facade = scene.facade
        self._mapper = input_mapper

        # Delegates (cheap; no pygame_gui in any constructor).
        self._renderer = renderer or TransferGridRenderer()
        self.view_model = view_model or TransferViewModel()
        self._controller = controller or TransferController(
            self.facade, self.view_model,
        )

        # Pod design discovery is a side-effecting query — do it now
        # so the view model has its baseline pod-name list before
        # any row build. Falls back to [] on I/O / schema error.
        self.view_model.all_pod_names = self._controller.discover_pod_designs(scene)

        # Widget reference placeholders. Populated by the renderer in
        # Stage 3 (production) or by ``MockTransferUiBuilder`` (tests).
        self._init_widget_refs()

        # ---- Stage 2: UIWindow shell ----
        super().__init__(
            relative_rect, manager,
            window_display_title="Resource Transfer",
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        # Bypass branch (test): only invoke an *explicitly supplied*
        # ui_builder so MockTransferUiBuilder can populate widget
        # slots; otherwise leave them at the placeholder.
        # (PROJ-325 PoC finding 2.)
        if getattr(self, "_window_init_bypassed", False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or TransferDialogUiBuilder()).build(self)

    # ------------------------------------------------------------------
    # Stage-1 helpers
    # ------------------------------------------------------------------

    def _init_widget_refs(self) -> None:
        """Populate widget slots with explicit placeholders so the
        bypassed object is honest: cheap delegates present, widget
        tree absent."""
        self.drop_source = None
        self.drop_target = None
        self.btn_filter = None
        self.btn_confirm = None
        self.btn_cancel = None
        self.btn_clear_all = None
        self.grid_container = None
        self._grid_top_y = 0

        # Per-row mappings for event routing.
        self._arrow_buttons: Dict[int, Tuple[str, int]] = {}
        self._max_buttons: Dict[int, Tuple[str, str]] = {}
        self._zero_buttons: Dict[int, str] = {}
        self._pending_labels: Dict[str, Any] = {}
        self._grid_widgets: List[Any] = []

    # ------------------------------------------------------------------
    # Back-compat property shims for legacy attribute names. Existing
    # tests and any external callers reach into these directly; the
    # canonical state lives on ``view_model``.
    # ------------------------------------------------------------------

    @property
    def available_sources(self) -> List[dict]:
        return self.view_model.available_sources

    @available_sources.setter
    def available_sources(self, value: List[dict]) -> None:
        self.view_model.available_sources = value

    @property
    def available_targets(self) -> List[dict]:
        return self.view_model.available_targets

    @available_targets.setter
    def available_targets(self, value: List[dict]) -> None:
        self.view_model.available_targets = value

    @property
    def pending_transfers(self) -> Dict[str, Any]:
        return self.view_model.pending_transfers

    @pending_transfers.setter
    def pending_transfers(self, value: Dict[str, Any]) -> None:
        self.view_model.pending_transfers = value

    @property
    def _row_data(self) -> List[dict]:
        return self.view_model.row_data

    @_row_data.setter
    def _row_data(self, value: List[dict]) -> None:
        self.view_model.row_data = value

    @property
    def _filter_empty(self) -> bool:
        return self.view_model.filter_empty

    @_filter_empty.setter
    def _filter_empty(self, value: bool) -> None:
        self.view_model.filter_empty = value

    @property
    def _current_source(self) -> Optional[dict]:
        return self.view_model.current_source

    @_current_source.setter
    def _current_source(self, value: Optional[dict]) -> None:
        self.view_model.current_source = value

    @property
    def _current_target(self) -> Optional[dict]:
        return self.view_model.current_target

    @_current_target.setter
    def _current_target(self, value: Optional[dict]) -> None:
        self.view_model.current_target = value

    @property
    def _all_pod_names(self) -> List[str]:
        return self.view_model.all_pod_names

    @_all_pod_names.setter
    def _all_pod_names(self, value: List[str]) -> None:
        self.view_model.all_pod_names = value

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def populate_initial_data(self) -> None:
        """Find fleets and planets at the hex and populate
        dropdowns. Also seeds ``_current_source`` / ``_current_target``
        and rebuilds the grid."""
        sources = self._controller.collect_sources_and_targets(
            self.source_fleet, self.hex_coord,
        )
        self.view_model.set_sources(sources)

        # Default: select the source_fleet if present.
        starting = ""
        if self.source_fleet is not None:
            for s in sources:
                if s["type"] == "fleet" and s["id"] == self.source_fleet.id:
                    starting = s["label"]
                    break

        labels = self.view_model.source_labels()
        if self.drop_source is not None:
            self.drop_source = self._renderer.recreate_dropdown(
                self, self.drop_source, labels, starting,
            )
            self._on_source_changed(self.drop_source.selected_option)

    # ------------------------------------------------------------------
    # Pure helpers (kept as public method shims for back-compat with
    # tests that exercise them directly).
    # ------------------------------------------------------------------

    def _extract_dropdown_value(self, value: Any) -> Any:
        return TransferGridRenderer.extract_dropdown_value(value)

    def _format_pending(self, amount: Any) -> str:
        return self.view_model.format_pending(amount)

    def _get_amounts(self, info_obj) -> Dict[str, int]:
        return self.view_model.get_amounts(info_obj)

    def _discover_pod_designs(self) -> List[str]:
        return self._controller.discover_pod_designs(self.scene)

    def _add_pod_rows(self, source_obj, target_obj) -> None:
        # Append pod rows to the existing row_data (matches the old
        # in-place behaviour the characterization tests pin).
        self.view_model.row_data.extend(
            self.view_model._build_pod_rows(source_obj, target_obj)
        )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_source_changed(self, label) -> None:
        label = self._extract_dropdown_value(label)
        source = self.view_model.select_source(label)
        if source is None:
            return

        target_labels = self.view_model.target_labels()
        if self.drop_target is not None:
            self.drop_target = self._renderer.recreate_dropdown(
                self, self.drop_target, target_labels,
                target_labels[0] if target_labels else "",
            )
            target_label = self._extract_dropdown_value(self.drop_target.selected_option)
            self.view_model.select_target(target_label)

        self._reset_and_build_grid()

    def _on_target_changed(self, label) -> None:
        label = self._extract_dropdown_value(label)
        self.view_model.select_target(label)
        self._reset_and_build_grid()

    def _reset_and_build_grid(self) -> None:
        self.view_model.reset_pending()
        self._build_grid()

    def _build_grid(self) -> None:
        """Rebuild ``view_model.row_data`` from current source/target
        DTOs, then ask the renderer to materialize the grid."""
        source_obj = self._controller.fetch_dto(self.view_model.current_source)
        target_obj = self._controller.fetch_dto(self.view_model.current_target)
        self.view_model.build_row_data(source_obj, target_obj)
        if self.grid_container is not None:
            self._renderer.build_grid(self)

    def _on_arrow_click(self, cargo_key: str, delta: int) -> None:
        self.view_model.apply_arrow(cargo_key, delta)
        self._update_pending_label(cargo_key)

    def _on_max_click(self, cargo_key: str, direction: str) -> None:
        self.view_model.apply_max(cargo_key, direction)
        self._update_pending_label(cargo_key)

    def _update_pending_label(self, cargo_key: str) -> None:
        self._renderer.update_pending_label(self, cargo_key)

    def _on_filter_toggle(self) -> None:
        new_state = self.view_model.toggle_filter_empty()
        self._renderer.set_filter_button_text(self, new_state)
        self._build_grid()

    def _on_clear_all(self) -> None:
        self.view_model.clear_all_pending()
        for key in self._pending_labels:
            self._update_pending_label(key)
        logger.info("TransferDialog: Cleared all pending transfers")

    def _on_confirm(self) -> None:
        # PROJ-321..328 audit S1.2: guarantee window teardown on dispatch
        # failure (catastrophic exception path).
        # PROJ-343 T1.4: do NOT kill the dialog on user-correctable validation
        # aborts (no source/target, both endpoints non-fleet, all pending
        # zero). The pre-S1.2 behavior had three early-returns that kept the
        # dialog open for correction; the always-kill `try/finally` from S1.2
        # broke that UX. The controller now returns a ConfirmResult that
        # distinguishes the cases.
        try:
            result = self._controller.confirm_pending()
        except Exception:
            # Catastrophic dispatch failure — close the modal so it can't
            # leak; let the exception propagate to the caller.
            self.kill()
            raise
        if not result.aborted_for_correction:
            self.kill()

    # ------------------------------------------------------------------
    # Tooltips + keyboard
    # ------------------------------------------------------------------

    def _apply_tooltips(self) -> None:
        if not self._mapper:
            return
        confirm_hint = self._mapper.get_display_text(InputAction.TRANSFER_CONFIRM)
        if confirm_hint and self.btn_confirm is not None:
            self.btn_confirm.set_tooltip(f"Confirm All ({confirm_hint})")
        cancel_hint = self._mapper.get_display_text(InputAction.TRANSFER_CANCEL)
        if cancel_hint and self.btn_cancel is not None:
            self.btn_cancel.set_tooltip(f"Cancel ({cancel_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["transfer"])
        if action == InputAction.TRANSFER_CONFIRM:
            self._on_confirm()
            return True
        if action == InputAction.TRANSFER_CANCEL:
            self.kill()
            return True
        return False

    def process_event(self, event) -> bool:
        super().process_event(event)

        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.drop_source:
                self._on_source_changed(event.text)
            elif event.ui_element == self.drop_target:
                self._on_target_changed(event.text)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            btn = event.ui_element
            if btn == self.btn_cancel:
                self.kill()
            elif btn == self.btn_confirm:
                self._on_confirm()
            elif btn == self.btn_filter:
                self._on_filter_toggle()
            elif id(btn) in self._arrow_buttons:
                cargo_key, delta = self._arrow_buttons[id(btn)]
                self._on_arrow_click(cargo_key, delta)
            elif id(btn) in self._max_buttons:
                cargo_key, direction = self._max_buttons[id(btn)]
                self._on_max_click(cargo_key, direction)
            elif id(btn) in self._zero_buttons:
                cargo_key = self._zero_buttons[id(btn)]
                self.view_model.set_pending_zero(cargo_key)
                self._update_pending_label(cargo_key)
            elif btn == self.btn_clear_all:
                self._on_clear_all()

    def handle_external_selection(self, obj) -> None:
        """Update target selection based on an external selection."""
        from game.core.protocols import is_fleet, is_planet

        target_label = None
        if is_fleet(obj):
            target_label = f"Fleet {obj.id}"
        elif is_planet(obj):
            if obj.owner_id is not None:
                target_label = f"Colony: {obj.name}"
            else:
                target_label = f"Planet: {obj.name}"

        if not target_label:
            return

        if target_label in self.view_model.target_labels():
            updated_labels = self.view_model.target_labels()
            if self.drop_target is not None:
                self.drop_target = self._renderer.recreate_dropdown(
                    self, self.drop_target, updated_labels, target_label,
                )
            self._on_target_changed(target_label)


# Re-exports for back-compat with importers that did
# ``from game.ui.screens.transfer_dialog import RESOURCE_TYPES`` etc.
__all__ = [
    "TransferDialog",
    "RESOURCE_TYPES",
    "RESOURCE_DISPLAY_NAMES",
    "ARROW_INCREMENTS_LOAD",
    "ARROW_INCREMENTS_DROP",
    "ARROW_LABELS_LOAD",
    "ARROW_LABELS_DROP",
]
