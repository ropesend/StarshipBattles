"""Orders management window for fleets and planets.

PROJ-238: Generalized from FleetOrdersWindow to work with any IOrderable entity.
PROJ-313: Migrated to ``StrategyModalWindow`` base class.
PROJ-328 Phase A Task A.3: Two-stage construction pattern. Order
descriptions are produced by a pure ``OrderDescriber``; widget
construction lives behind ``OrdersWindowUiBuilder`` /
``OrdersListRenderer`` so tests can swap in
``Null{...}UiBuilder`` / ``Mock{...}UiBuilder`` from
``tests/fixtures/orders_ui_builder.py``.

Cross-layer imports (acceptable for UI):
- OrderType: Runtime - displays and filters order types
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional

import pygame
import pygame_gui
from pygame_gui.windows import UIConfirmationDialog

from game.ui.config import UIConfig
from game.core.hex_math import HexCoord
from game.core.input_actions import InputAction
from game.core.protocols import is_planet, is_fleet
from game.strategy.data.order_types import OrderType
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.ui.screens.strategy_window_manager import StrategyWindowManager
    from typing import Callable

EDITABLE_ORDER_TYPES = frozenset({
    OrderType.MOVE,
    OrderType.TRANSFER,
    OrderType.LOAD_POPULATION,
    OrderType.UNLOAD_POPULATION,
})


@dataclass(frozen=True)
class OrderRowDescription:
    """Pure-data description of one order row.

    Carries the index, the human-readable text, the editability flag,
    and a back-pointer to the underlying order so the renderer/handlers
    can wire button object_ids and edit callbacks without re-deriving
    state.
    """

    index: int
    text: str
    is_editable: bool
    order: Any


class OrderDescriber:
    """Builds ``OrderRowDescription`` instances for an entity's orders.

    Pure: no pygame_gui widgets, no display. Construct + call freely
    in tests without ``bypass_init``. The describer needs the entity
    only for the BUILD-order branch which reads ``construction_queue``
    length.
    """

    def describe_all(self, entity) -> List[OrderRowDescription]:
        return [
            OrderRowDescription(
                index=i,
                text=self.describe(order, entity),
                is_editable=order.type in EDITABLE_ORDER_TYPES,
                order=order,
            )
            for i, order in enumerate(entity.orders)
        ]

    def describe(self, order, entity) -> str:
        """Get human-readable description for an order."""
        if order.type == OrderType.MOVE:
            t = order.target
            if isinstance(t, HexCoord):
                return f"MOVE ({t.q}, {t.r})"
            return f"MOVE {t}"
        elif order.type == OrderType.COLONIZE:
            t = order.target
            if isinstance(t, dict):
                planet_obj = t.get('planet')
                p_name = planet_obj.name if planet_obj else 'Any Planet'
            elif is_planet(t):
                p_name = t.name
            else:
                p_name = 'Unknown'
            return f"COLONIZE {p_name}"
        elif order.type == OrderType.MOVE_TO_FLEET:
            f_id = order.target.id if is_fleet(order.target) else "?"
            return f"INTERCEPT Fleet {f_id}"
        elif order.type == OrderType.JOIN_FLEET:
            f_id = order.target.id if is_fleet(order.target) else "?"
            return f"JOIN Fleet {f_id}"
        elif order.type == OrderType.BUILD:
            if hasattr(entity, 'construction_queue'):
                queue_size = len(entity.construction_queue)
                return f"BUILDING ({queue_size} items)"
            return "BUILDING"
        elif order.type in (OrderType.TRANSFER, OrderType.LOAD_POPULATION,
                            OrderType.UNLOAD_POPULATION):
            if isinstance(order.target, dict):
                direction = order.target.get('direction', '?')
                if order.type == OrderType.LOAD_POPULATION:
                    return "load cargo"
                elif order.type == OrderType.UNLOAD_POPULATION:
                    return "drop cargo"
                else:
                    return "load cargo" if direction == "load" else "drop cargo"
            return "TRANSFER"
        elif order.type == OrderType.ACTIVATE_ABILITY:
            ability = order.target.get('ability_name', 'ability') if isinstance(order.target, dict) else 'ability'
            return f"ACTIVATE {ability.upper()}"
        elif order.type == OrderType.DEACTIVATE_ABILITY:
            ability = order.target.get('ability_name', 'ability') if isinstance(order.target, dict) else 'ability'
            return f"DEACTIVATE {ability.upper()}"
        else:
            return f"{order.type.name}"


class OrdersListRenderer:
    """Builds the row widgets inside ``screen.list_container``.

    Owns the per-row layout (description label + edit/up/down/del
    buttons). Production widget construction; tests use
    ``MockOrdersUiBuilder`` instead, which fakes the widgets.
    """

    BTN_SIZE = 30
    BTN_GAP = 5

    def render(self, screen: "OrdersWindow") -> None:
        # Tear down any previous rows.
        for row in screen.rows:
            for key, element in row.items():
                if key not in ('order_ref', 'description'):
                    element.kill()
        screen.rows.clear()

        descriptions = screen._order_describer.describe_all(screen.entity)
        gap = 5
        row_height = UIConfig.ROW_HEIGHT_STANDARD
        y_offset = 5

        total_h = len(descriptions) * (row_height + gap) + 10
        screen.list_container.set_scrollable_area_dimensions(
            (screen.list_container.rect.width - 20, total_h))

        content_width = screen.list_container.get_container().get_rect().width
        btn_size = self.BTN_SIZE
        btn_gap = self.BTN_GAP
        btn_del_x = content_width - btn_size - btn_gap
        btn_down_x = btn_del_x - btn_size - btn_gap
        btn_up_x = btn_down_x - btn_size - btn_gap
        btn_edit_x = btn_up_x - btn_size - btn_gap
        desc_x = 40
        desc_width = btn_edit_x - desc_x - btn_gap

        last_idx = len(descriptions) - 1
        for desc_row in descriptions:
            i = desc_row.index
            row_y = y_offset + i * (row_height + gap)

            lbl_idx = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(5, row_y, 30, row_height),
                text=str(i + 1),
                manager=screen.ui_manager,
                container=screen.list_container,
            )

            lbl_desc = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(desc_x, row_y, desc_width, row_height),
                text=desc_row.text,
                manager=screen.ui_manager,
                container=screen.list_container,
            )

            row_dict: dict = {
                'idx': lbl_idx,
                'desc': lbl_desc,
                'description': desc_row,
                'order_ref': desc_row.order,
            }

            if desc_row.is_editable:
                btn_edit = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(btn_edit_x, row_y, btn_size, row_height),
                    text="E",
                    manager=screen.ui_manager,
                    container=screen.list_container,
                    object_id=f"#edit_{i}",
                )
                row_dict['edit'] = btn_edit

            btn_up = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_up_x, row_y, btn_size, row_height),
                text="^",
                manager=screen.ui_manager,
                container=screen.list_container,
                object_id=f"#up_{i}",
            )
            if i == 0:
                btn_up.disable()
            row_dict['up'] = btn_up

            btn_down = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_down_x, row_y, btn_size, row_height),
                text="v",
                manager=screen.ui_manager,
                container=screen.list_container,
                object_id=f"#down_{i}",
            )
            if i == last_idx:
                btn_down.disable()
            row_dict['down'] = btn_down

            btn_del = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_del_x, row_y, btn_size, row_height),
                text="X",
                manager=screen.ui_manager,
                container=screen.list_container,
                object_id=f"#del_{i}",
            )
            row_dict['del'] = btn_del

            screen.rows.append(row_dict)


class OrdersWindowUiBuilder:
    """Production UI builder. Creates the scrolling container, the
    Clear-All button, and seeds the initial row layout via
    ``OrdersListRenderer``.
    """

    def build(self, screen: "OrdersWindow") -> None:
        rect = screen._initial_rect
        container_rect = pygame.Rect(0, 0, rect.width - 32, rect.height - 100)
        screen.list_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=container_rect,
            manager=screen.ui_manager,
            container=screen,
            anchors={'left': 'left', 'right': 'right',
                     'top': 'top', 'bottom': 'bottom'},
        )

        screen.btn_clear = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-110, -40, 100, 30),
            text="Clear All",
            manager=screen.ui_manager,
            container=screen,
            anchors={'left': 'right', 'right': 'right',
                     'top': 'bottom', 'bottom': 'bottom'},
        )

        screen.rebuild_list()
        screen._apply_tooltips()


class OrdersWindow(StrategyModalWindow):
    """Window to manage an entity's order queue (fleet or planet).

    PROJ-238: Generalized from FleetOrdersWindow.
    PROJ-313: Migrated to ``StrategyModalWindow`` base class.
    PROJ-328 Phase A Task A.3: Two-stage construction. Order
    description logic split into ``OrderDescriber`` (pure data),
    widget construction split into ``OrdersListRenderer`` +
    ``OrdersWindowUiBuilder``. Tests pass a ``MockOrdersUiBuilder`` to
    populate the widget slots without a live pygame display.
    """

    def __init__(
        self,
        rect,
        manager,
        entity,
        *,
        window_manager: "StrategyWindowManager | None",
        entity_type: str = "fleet",
        input_mapper: Optional['InputMapper'] = None,
        clear_orders_callback: Optional['Callable[[int], None]'] = None,
        delete_order_callback: Optional['Callable[[int, int], None]'] = None,
        reorder_order_callback: Optional['Callable[[int, int, int], None]'] = None,
        edit_order_callback: Optional['Callable[[int, int, object], None]'] = None,
        ui_builder: Optional[OrdersWindowUiBuilder] = None,
        list_renderer: Optional[OrdersListRenderer] = None,
        order_describer: Optional[OrderDescriber] = None,
    ):
        """Initialize the Orders Window.

        Args:
            rect: Window position and size.
            manager: pygame_gui UIManager.
            entity: IOrderable entity (Fleet or Planet) to display orders for.
            entity_type: "fleet" or "planet" — affects title and descriptions.
            input_mapper: Optional InputMapper for hotkey tooltips.
            clear_orders_callback: Callback(entity_id) to clear all orders.
            delete_order_callback: Callback(entity_id, order_index) to delete an order.
            reorder_order_callback: Callback(entity_id, order_index, direction) to reorder.
            edit_order_callback: Callback(entity_id, order_index, order) to edit.
            ui_builder: PROJ-328 — UI builder seam. Defaults to
                ``OrdersWindowUiBuilder``. Tests pass
                ``NullOrdersUiBuilder`` / ``MockOrdersUiBuilder``.
            list_renderer: PROJ-328 — list-renderer seam. Defaults to
                ``OrdersListRenderer``.
            order_describer: PROJ-328 — describer seam. Defaults to
                ``OrderDescriber``.
        """
        # ---- Stage 1: cheap state ----
        self.entity = entity
        self.entity_type = entity_type
        self._mapper = input_mapper
        self._clear_orders_callback = clear_orders_callback
        self._delete_order_callback = delete_order_callback
        self._reorder_order_callback = reorder_order_callback
        self._edit_order_callback = edit_order_callback
        self._initial_rect = rect

        self._order_describer = order_describer or OrderDescriber()
        self._list_renderer = list_renderer or OrdersListRenderer()

        self.rows: List[dict] = []
        self.list_container = None
        self.btn_clear = None
        self._last_order_count = len(entity.orders)

        # ---- Stage 2: shell ----
        if entity_type == "planet":
            title = f"Orders: {entity.name}"
        else:
            title = f"Orders: {entity.name}"

        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=title,
            element_id='orders_window',
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or OrdersWindowUiBuilder()).build(self)

    def update(self, dt) -> None:
        super().update(dt)
        if len(self.entity.orders) != self._last_order_count:
            self._last_order_count = len(self.entity.orders)
            self.rebuild_list()

    def rebuild_list(self) -> None:
        """Clear and rebuild the order list rows via the list renderer."""
        self._list_renderer.render(self)

    def _apply_tooltips(self) -> None:
        if not self._mapper or self.btn_clear is None:
            return
        clear_hint = self._mapper.get_display_text(InputAction.FLEET_ORDERS_CLEAR)
        if clear_hint:
            self.btn_clear.set_tooltip(f"Clear All ({clear_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["fleet_orders"])
        if action == InputAction.FLEET_ORDERS_CLEAR:
            self.show_clear_confirmation()
            return True
        return False

    def process_event(self, event) -> bool:
        handled = super().process_event(event)

        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return True

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_clear:
                self.show_clear_confirmation()
                handled = True
            else:
                obj_id = event.ui_element.object_ids[-1]
                if obj_id:
                    if obj_id.startswith("#up_"):
                        idx = int(obj_id.split("_")[1])
                        self.move_order(idx, -1)
                        handled = True
                    elif obj_id.startswith("#down_"):
                        idx = int(obj_id.split("_")[1])
                        self.move_order(idx, 1)
                        handled = True
                    elif obj_id.startswith("#edit_"):
                        idx = int(obj_id.split("_")[1])
                        self.edit_order(idx)
                        handled = True
                    elif obj_id.startswith("#del_"):
                        idx = int(obj_id.split("_")[1])
                        self.delete_order(idx)
                        handled = True

        return handled

    def move_order(self, index, direction) -> None:
        if not self._reorder_order_callback:
            return
        new_index = index + direction
        if 0 <= new_index < len(self.entity.orders):
            self._reorder_order_callback(self.entity.id, index, direction)
            self.rebuild_list()

    def edit_order(self, index) -> None:
        if not self._edit_order_callback:
            return
        if 0 <= index < len(self.entity.orders):
            order = self.entity.orders[index]
            self._edit_order_callback(self.entity.id, index, order)

    def delete_order(self, index) -> None:
        if not self._delete_order_callback:
            return
        if 0 <= index < len(self.entity.orders):
            self._delete_order_callback(self.entity.id, index)
            self.rebuild_list()

    def show_clear_confirmation(self) -> None:
        entity_label = self.entity.name if self.entity_type == "planet" else f"fleet {self.entity.id}"
        confirm_rect = pygame.Rect(
            0, 0, UIConfig.CONFIRM_DIALOG_WIDTH, UIConfig.CONFIRM_DIALOG_HEIGHT
        )
        confirm_rect.center = (self.rect.centerx, self.rect.centery)
        UIConfirmationDialog(
            rect=confirm_rect,
            manager=self.ui_manager,
            action_long_desc=f"Are you sure you want to clear ALL orders for {entity_label}?",
            window_title="Confirm Clear",
            action_short_name="Clear",
            blocking=True,
            object_id='#confirm_clear_orders',
        )

    def handle_global_event(self, event) -> bool:
        """Handle events from the wider application (like dialog confirmations)."""
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element.object_ids[-1] == '#confirm_clear_orders':
                if self._clear_orders_callback:
                    self._clear_orders_callback(self.entity.id)
                    self.rebuild_list()
                    return True
        return False

    # ------------------------------------------------------------------
    # Backwards-compat shim
    # ------------------------------------------------------------------

    def _get_order_description(self, order) -> str:
        """PROJ-328: Pre-refactor public-ish API. Tests / callers that
        used to call ``screen._get_order_description(order)`` get the
        same answer; the implementation now lives on ``OrderDescriber``.
        """
        return self._order_describer.describe(order, self.entity)
