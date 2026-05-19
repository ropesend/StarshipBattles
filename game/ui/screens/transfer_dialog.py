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
from game.ui.screens.transfer_view_model import TransferViewModel

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
        # PROJ-437 Phase 2: mass-remaining preview labels (one per side,
        # below their dropdowns). Refresh on every pending mutation.
        self.lbl_source_remaining = None
        self.lbl_target_remaining = None

        # Per-row mappings for event routing.
        self._arrow_buttons: Dict[int, Tuple[str, int]] = {}
        self._max_buttons: Dict[int, Tuple[str, str]] = {}
        self._zero_buttons: Dict[int, str] = {}
        self._pending_labels: Dict[str, Any] = {}
        self._grid_widgets: List[Any] = []

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
    # Event handlers
    # ------------------------------------------------------------------

    def _on_source_changed(self, label) -> None:
        label = TransferGridRenderer.extract_dropdown_value(label)
        source = self.view_model.select_source(label)
        if source is None:
            return

        target_labels = self.view_model.target_labels()
        if self.drop_target is not None:
            self.drop_target = self._renderer.recreate_dropdown(
                self, self.drop_target, target_labels,
                target_labels[0] if target_labels else "",
            )
            target_label = TransferGridRenderer.extract_dropdown_value(self.drop_target.selected_option)
            self.view_model.select_target(target_label)

        self._reset_and_build_grid()

    def _on_target_changed(self, label) -> None:
        label = TransferGridRenderer.extract_dropdown_value(label)
        self.view_model.select_target(label)
        self._reset_and_build_grid()

    def _reset_and_build_grid(self) -> None:
        self.view_model.reset_pending()
        self._build_grid()

    def _build_grid(self) -> None:
        """Rebuild ``view_model.row_data`` from the current source/target
        Container snapshots, then ask the renderer to materialize the grid.

        PROJ-437 Phase 3b cutover. Reads Container snapshots off the
        Phase-1b ``containers`` field attached by
        ``collect_sources_and_targets``; the row builder walks
        ``ContainerSnapshotInfo.entries`` directly via
        :func:`game.ui.screens.transfer_container_rows.build_row_data_from_containers`
        (the Phase-3a substrate). The legacy ``vm.build_row_data(source_obj,
        target_obj)`` DTO path is dead code from this commit forward —
        Phase 4 deletes it along with ``_build_pod_rows`` / ``get_amounts``
        / ``all_pod_names`` and the dialog's back-compat property shims.
        """
        source_containers = (self.view_model.current_source or {}).get(
            "containers", (),
        )
        target_containers = (self.view_model.current_target or {}).get(
            "containers", (),
        )
        # MagicMock-friendly: in characterization tests the facade is a
        # MagicMock and `get_containers(id)` returns a MagicMock too.
        # MagicMock iterates as empty by default, so the row builder
        # produces the canonical-8 zero-zero resource rows — same UX
        # as the legacy DTO path with empty FleetInfo / PlanetInfo.
        self.view_model.row_data = TransferViewModel.build_row_data_from_containers(
            source_containers,
            target_containers,
            filter_empty=self.view_model.filter_empty,
        )
        if self.grid_container is not None:
            self._renderer.build_grid(self)
        self._refresh_mass_preview()

    def _on_arrow_click(self, cargo_key: str, delta: int) -> None:
        self.view_model.apply_arrow(cargo_key, delta)
        self._update_pending_label(cargo_key)
        self._refresh_mass_preview()

    def _on_max_click(self, cargo_key: str, direction: str) -> None:
        self.view_model.apply_max(cargo_key, direction)
        self._update_pending_label(cargo_key)
        self._refresh_mass_preview()

    def _update_pending_label(self, cargo_key: str) -> None:
        self._renderer.update_pending_label(self, cargo_key)

    def _refresh_mass_preview(self) -> None:
        """Recompute + render the source/target mass-remaining indicators.

        PROJ-437 Phase 2 (OD3 = (a) per-input granularity). Pulls
        Container snapshots off the currently-selected source/target
        dropdown entries (attached by Phase 1b), computes the
        ``MassPreview`` via the view model, and asks the renderer to
        update the chrome labels. No-ops cleanly under bypass-init
        tests where the renderer or labels are absent.
        """
        if self.lbl_source_remaining is None and self.lbl_target_remaining is None:
            return
        source_containers = (self.view_model.current_source or {}).get(
            "containers", (),
        )
        target_containers = (self.view_model.current_target or {}).get(
            "containers", (),
        )
        preview = TransferViewModel.compute_mass_preview(
            source_containers, target_containers,
            self.view_model.pending_transfers,
        )
        self._renderer.update_mass_preview(self, preview)

    def _on_filter_toggle(self) -> None:
        new_state = self.view_model.toggle_filter_empty()
        self._renderer.set_filter_button_text(self, new_state)
        self._build_grid()

    def _on_clear_all(self) -> None:
        self.view_model.clear_all_pending()
        for key in self._pending_labels:
            self._update_pending_label(key)
        self._refresh_mass_preview()
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
        except Exception:  # Intentional broad catch: dialog-level catastrophic failure must not leak; kill modal then re-raise.
            # Catastrophic dispatch failure — close the modal so it can't
            # leak; let the exception propagate to the caller.
            self.kill()
            raise
        # QA Obs 5 follow-up (2026-05-16): when every dispatched command
        # was rejected by the facade, surface the first rejection to the
        # user so "Confirm All" does not appear to silently no-op. The
        # dialog stays open for correction. Guard chain falls through
        # cleanly on bypass-init test dialogs (no ``scene``) and scenes
        # without ``ui.show_error_message``.
        if result.rejection_message:
            scene = getattr(self, "scene", None)
            shower = getattr(getattr(scene, "ui", None), "show_error_message", None)
            if shower is not None:
                shower(f"Transfer failed: {result.rejection_message}")
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
                self._refresh_mass_preview()
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


__all__ = [
    "TransferDialog",
    "ARROW_INCREMENTS_LOAD",
    "ARROW_INCREMENTS_DROP",
    "ARROW_LABELS_LOAD",
    "ARROW_LABELS_DROP",
]
