"""
Ship Detail Panel - Displays detailed ship information with damage tracking.

PROJ-03 Phase 4: Wraps DesignReportPanel for ShipInstance display with
component damage visualization.

PROJ-315: Replaced the always-hidden-on-healthy-ships "COMPONENT DAMAGE"
section with an always-rendered "COMPONENT STATUS" section that lists every
component grouped by layer, with collapsible groups for identical
components and per-instance damage tier rendering.

Cross-layer imports (acceptable for UI display):
- ShipInstance: TYPE_CHECKING - used for type hints only
- LayerType: Runtime - iterates ship layers for component display
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIScrollingContainer, UIImage

logger = logging.getLogger(__name__)

from game.core.component_state import ComponentInstanceView
from game.core.constants import CombatConstants
from game.core.string_utils import display_name
from game.ui.assets import get_default_ship_theme_manager
from game.ui.colors import (
    BAR_BG,
    BAR_BORDER,
    HP_CRITICAL,
    HP_DESTROYED,
    MUTED_GREY,
)
from game.ui.utils.formatters import get_damage_color as _formatters_get_damage_color

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


# --- Module-level grouping helpers (PROJ-315) -------------------------------
# Pure-function colocation precedent: planet_report_panel.py has the same
# shape (`_projection_grid_rows`, `_qty_cell`, etc.) above its panel class.

LAYER_ORDER: Tuple[str, ...] = ('CORE', 'INNER', 'OUTER', 'ARMOR')
"""Layer iteration order for COMPONENT STATUS — matches Workshop's
`builder/layer_panel.py` (HULL excluded by user decision)."""


@dataclass(frozen=True)
class InstanceDamage:
    """One component instance's rendered state."""

    instance_index: int
    damage_pct: float
    is_active: bool
    is_damage_induced_inactive: bool


@dataclass(frozen=True)
class ComponentGroup:
    """A collapsible group of identical-component-id instances."""

    component_id: str
    display_name: str
    total: int
    functional: int
    avg_damage_pct: float
    instances: Tuple[InstanceDamage, ...]


def group_components_by_id(
    instances: List[ComponentInstanceView],
    damage_threshold_lookup: Callable[[str], float],
) -> List[ComponentGroup]:
    """Group `ComponentInstanceView`s by `component_id`, preserving order.

    Pure function. No pygame deps. The lookup is injected so tests can
    stub it without instantiating the registry.

    `damage_pct` = `0.0 if max_hp == 0 else (1.0 - current_hp/max_hp)` —
    division-by-zero guarded for legacy save data.

    `is_damage_induced_inactive` = `(not is_active) and (current_hp <
    max_hp * threshold)` — used by the panel to render damage-induced
    inactive components in red+strike vs manually-disabled in muted grey.
    """
    grouped: Dict[str, List[ComponentInstanceView]] = {}
    order: List[str] = []
    for view in instances:
        if view.component_id not in grouped:
            order.append(view.component_id)
            grouped[view.component_id] = []
        grouped[view.component_id].append(view)

    result: List[ComponentGroup] = []
    for comp_id in order:
        comp_views = grouped[comp_id]
        threshold = damage_threshold_lookup(comp_id)
        damages: List[InstanceDamage] = []
        for view in comp_views:
            if view.max_hp <= 0:
                damage_pct = 0.0
            else:
                damage_pct = 1.0 - (view.current_hp / view.max_hp)
            is_damage_induced_inactive = (
                (not view.is_active)
                and view.current_hp < view.max_hp * threshold
            )
            damages.append(
                InstanceDamage(
                    instance_index=view.instance_index,
                    damage_pct=damage_pct,
                    is_active=view.is_active,
                    is_damage_induced_inactive=is_damage_induced_inactive,
                )
            )
        avg_damage_pct = sum(d.damage_pct for d in damages) / len(damages)
        functional = sum(1 for d in damages if d.is_active)
        result.append(
            ComponentGroup(
                component_id=comp_id,
                display_name=display_name(comp_id),
                total=len(damages),
                functional=functional,
                avg_damage_pct=avg_damage_pct,
                instances=tuple(damages),
            )
        )
    return result


# --- ShipDetailPanel --------------------------------------------------------


class ShipDetailPanel:
    """
    Panel displaying detailed ship information with damage tracking.

    Designed to work with ShipInstance from the strategy layer,
    showing current HP/resources vs max, and component status.
    """

    def __init__(self, manager, rect: pygame.Rect, container=None,
                 on_remove_ship=None):
        """
        Initialize ship detail panel.

        Args:
            manager: pygame_gui UIManager
            rect: Panel dimensions and position
            container: Optional parent container
            on_remove_ship: Optional callback(ShipInstance) when remove button clicked
        """
        self.manager = manager
        self.rect = rect
        self.container = container
        self.current_ship: Optional[ShipInstance] = None
        self.on_remove_ship = on_remove_ship

        # PROJ-315: collapsible state — per-ship (recomputed in update_ship,
        # auto-expand re-fires every selection per Phase C decision).
        self.expanded_layers: Dict[str, bool] = {layer: False for layer in LAYER_ORDER}
        self.expanded_groups: Dict[Tuple[str, str], bool] = {}

        # UI elements
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            container=container
        )

        # Scrolling container for content
        content_rect = pygame.Rect(0, 0, rect.width - 10, rect.height - 10)
        self.scroll_container = UIScrollingContainer(
            relative_rect=content_rect,
            manager=manager,
            container=self.panel
        )

        # Dynamic UI elements
        self.ui_elements: List = []
        self.layer_buttons: Dict[str, UIButton] = {}
        self.group_buttons: Dict[Tuple[str, str], UIButton] = {}
        self.btn_remove: Optional[UIButton] = None

        # Show placeholder initially
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        """Show placeholder when no ship selected."""
        self._clear_elements()

        placeholder = UILabel(
            relative_rect=pygame.Rect(10, 10, self.rect.width - 40, 30),
            text="Select a ship to view details",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(placeholder)

    def _clear_elements(self) -> None:
        """Clear all dynamic UI elements."""
        for element in self.ui_elements:
            element.kill()
        self.ui_elements.clear()
        self.layer_buttons.clear()
        self.group_buttons.clear()

    def _get_scaled_image(self, raw_surf: Optional[pygame.Surface], target_size: int) -> pygame.Surface:
        """
        Scale an image to fit within a square target size while preserving aspect ratio.

        Args:
            raw_surf: Source surface, or None for placeholder
            target_size: Target width/height in pixels

        Returns:
            Scaled surface centered on a target_size x target_size background
        """
        result = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
        result.fill(BAR_BG)  # Dark background

        if raw_surf:
            w, h = raw_surf.get_size()
            scale = min(target_size / w, target_size / h) * 0.9  # 90% to leave margin
            new_w, new_h = int(w * scale), int(h * scale)
            scaled = pygame.transform.smoothscale(raw_surf, (new_w, new_h))

            # Center on result
            x_off = (target_size - new_w) // 2
            y_off = (target_size - new_h) // 2
            result.blit(scaled, (x_off, y_off))
        else:
            pygame.draw.rect(result, BAR_BORDER, (10, 10, target_size - 20, target_size - 20), 2)
            center = target_size // 2
            pygame.draw.polygon(result, BAR_BORDER, [
                (center, 20),
                (center + 30, target_size - 30),
                (center - 30, target_size - 30)
            ])

        return result

    def update_ship(self, ship_instance: Optional[ShipInstance]) -> None:
        """
        Update display for a ship instance.

        Args:
            ship_instance: ShipInstance to display, or None to show placeholder
        """
        self.current_ship = ship_instance

        if ship_instance is None:
            self._show_placeholder()
            return

        self._compute_initial_expand_state(ship_instance)
        self._clear_elements()
        self._build_ship_display(ship_instance)

    def _compute_initial_expand_state(self, ship: ShipInstance) -> None:
        """Reset expand state and auto-expand layers with destroyed components.

        Per the PROJ-315 Phase C user decision, this re-fires on every
        ship selection — manual collapse does NOT persist across reselects.
        """
        self.expanded_layers = {layer: False for layer in LAYER_ORDER}
        self.expanded_groups = {}
        try:
            views_by_layer = ship.iter_all_components_by_layer()
        except AttributeError:
            return
        for layer, views in views_by_layer.items():
            if layer not in self.expanded_layers:
                continue
            if any(v.current_hp == 0 and v.max_hp > 0 for v in views):
                self.expanded_layers[layer] = True

    def _build_ship_display(self, ship: ShipInstance) -> None:
        """Build the full ship display."""
        y = 10
        width = self.rect.width - 40

        image_size = 120
        image_spacing = 10
        total_images_width = image_size * 2 + image_spacing
        images_x = (self.rect.width - total_images_width) // 2 - 10  # Center the images

        theme_id = ship.design_data.get('theme_id', 'Federation')
        ship_class = ship.design_data.get('ship_class', 'Unknown')
        logger.debug(f"ShipDetailPanel: building display for theme_id='{theme_id}', ship_class='{ship_class}'")
        theme_mgr = get_default_ship_theme_manager()

        portrait_surf = self._get_scaled_image(
            theme_mgr.get_portrait_image(theme_id, ship_class),
            image_size
        )
        portrait_img = UIImage(
            relative_rect=pygame.Rect(images_x, y, image_size, image_size),
            image_surface=portrait_surf,
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(portrait_img)

        topdown_surf = self._get_scaled_image(
            theme_mgr.load_image(theme_id, ship_class),
            image_size
        )
        topdown_img = UIImage(
            relative_rect=pygame.Rect(images_x + image_size + image_spacing, y, image_size, image_size),
            image_surface=topdown_surf,
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(topdown_img)

        y += image_size + 10

        display_id = ship.get_display_id() or ship.instance_id[:8]
        header = UILabel(
            relative_rect=pygame.Rect(10, y, width, 30),
            text=display_id,
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(header)
        y += 35

        design_name = ship.design_data.get('name', ship.design_id)
        if ship.name != design_name:
            name_label = UILabel(
                relative_rect=pygame.Rect(10, y, width, 25),
                text=f'"{ship.name}"',
                manager=self.manager,
                container=self.scroll_container
            )
            self.ui_elements.append(name_label)
            y += 28

        # --- Status Section ---
        y = self._add_section_header("STATUS", 10, y, width)

        status_text = ship.get_status_text()
        hp_display = ship.get_hp_display()
        hp_pct = ship.get_hp_percentage()

        status_label = UILabel(
            relative_rect=pygame.Rect(10, y, width, 25),
            text=f"Status: {status_text}",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(status_label)
        y += 25

        hp_label = UILabel(
            relative_rect=pygame.Rect(10, y, width, 25),
            text=f"HP: {hp_display} ({hp_pct * 100:.0f}%)",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(hp_label)
        y += 30

        # --- Resources Section ---
        y = self._add_section_header("RESOURCES", 10, y, width)

        for resource in ["fuel", "energy", "ammo"]:
            display = ship.get_resource_display(resource)
            if display != "N/A":
                pct = ship.get_resource_percentage(resource)
                label = UILabel(
                    relative_rect=pygame.Rect(10, y, width, 22),
                    text=f"{resource.capitalize()}: {display} ({pct * 100:.0f}%)",
                    manager=self.manager,
                    container=self.scroll_container
                )
                self.ui_elements.append(label)
                y += 24
        y += 5

        # --- Component Status Section (PROJ-315) ---
        y = self._add_section_header("COMPONENT STATUS", 10, y, width)
        y = self._build_component_section(ship, 10, y, width)

        # --- Combat Stats Section ---
        y = self._add_section_header("COMBAT RECORD", 10, y, width)

        stats_text = [
            f"Battles Survived: {ship.battles_survived}",
            f"Kills: {ship.kills}",
            f"Experience: {ship.experience}",
        ]
        for text in stats_text:
            label = UILabel(
                relative_rect=pygame.Rect(10, y, width, 22),
                text=text,
                manager=self.manager,
                container=self.scroll_container
            )
            self.ui_elements.append(label)
            y += 24

        # --- Remove from Fleet button ---
        if self.on_remove_ship:
            y += 10
            self.btn_remove = UIButton(
                relative_rect=pygame.Rect(10, y, width, 30),
                text="Remove from Fleet",
                manager=self.manager,
                container=self.scroll_container,
                object_id="#btn_remove_ship"
            )
            self.ui_elements.append(self.btn_remove)
            y += 40

        self.scroll_container.set_scrollable_area_dimensions((width, y + 20))

    def _add_section_header(self, title: str, x: int, y: int, width: int) -> int:
        """Add a section header and return new y position."""
        header = UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text=f"── {title} ──",
            manager=self.manager,
            container=self.scroll_container
        )
        self.ui_elements.append(header)
        return y + 28

    def _resolve_threshold_lookup(self) -> Callable[[str], float]:
        """Build the per-component damage threshold lookup.

        Production wires through the registry provider; the lookup falls
        back to `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` when the
        component is unknown or the registry is unavailable in test
        contexts.
        """
        default = CombatConstants.DEFAULT_DAMAGE_THRESHOLD

        try:
            # Late import to keep module import cheap and to avoid pulling
            # the simulation registry into UI-only test fixtures.
            from game.core.registry import get_default_registry_provider
            provider = get_default_registry_provider()
            components: Dict[str, Any] = provider.get_components()
        except Exception:  # Intentional broad catch: UI tests run without ApplicationContext
            return lambda _comp_id: default

        def lookup(comp_id: str) -> float:
            comp = components.get(comp_id)
            if comp is None:
                return default
            if isinstance(comp, dict):
                return float(comp.get('damage_threshold', default))
            return float(getattr(comp, 'damage_threshold', default))

        return lookup

    def _build_component_section(self, ship: ShipInstance, x: int, y: int, width: int) -> int:
        """PROJ-315: always-rendering layer-grouped component status display.

        Walks `iter_all_components_by_layer()` in `LAYER_ORDER`, groups
        identical components, renders layer headers + collapsed group
        rows + per-instance rows when expanded.
        """
        try:
            views_by_layer = ship.iter_all_components_by_layer()
        except AttributeError:
            views_by_layer = {}

        if not any(views_by_layer.get(layer) for layer in LAYER_ORDER):
            no_components = UILabel(
                relative_rect=pygame.Rect(x, y, width, 22),
                text="No components",
                manager=self.manager,
                container=self.scroll_container,
            )
            self.ui_elements.append(no_components)
            return y + 25

        threshold_lookup = self._resolve_threshold_lookup()

        for layer in LAYER_ORDER:
            views = views_by_layer.get(layer, [])
            if not views:
                continue
            groups = group_components_by_id(views, threshold_lookup)
            y = self._build_layer_block(x, y, width, layer, groups)

        return y + 5

    def _build_layer_block(
        self, x: int, y: int, width: int, layer: str, groups: List[ComponentGroup]
    ) -> int:
        """Render one layer header + (if expanded) its group rows."""
        is_expanded = self.expanded_layers.get(layer, False)
        expand_char = "▼" if is_expanded else "▶"
        total = sum(g.total for g in groups)
        functional = sum(g.functional for g in groups)
        layer_avg = sum(g.avg_damage_pct * g.total for g in groups) / max(total, 1)

        layer_btn = UIButton(
            relative_rect=pygame.Rect(x, y, width - 10, 24),
            text=(
                f"{expand_char} {layer}  {functional}/{total} functional  "
                f"·  {layer_avg * 100:.0f}% avg damage"
            ),
            manager=self.manager,
            container=self.scroll_container,
            object_id=f"#layer_{layer}",
        )
        self.ui_elements.append(layer_btn)
        self.layer_buttons[layer] = layer_btn
        y += 26

        if is_expanded:
            for group in groups:
                y = self._build_group_block(x, y, width, layer, group)
            y += 4

        return y

    def _build_group_block(
        self, x: int, y: int, width: int, layer: str, group: ComponentGroup
    ) -> int:
        """Render one component group header + (if expanded) instance rows."""
        key = (layer, group.component_id)
        is_expanded = self.expanded_groups.get(key, False)
        chevron = "▼" if is_expanded else "▶"

        row_text = (
            f"  {chevron} {group.display_name} × {group.total}  "
            f"{group.functional}/{group.total}  "
            f"{group.avg_damage_pct * 100:.0f}%"
        )
        group_btn = UIButton(
            relative_rect=pygame.Rect(x + 10, y, width - 25, 22),
            text=row_text,
            manager=self.manager,
            container=self.scroll_container,
            object_id=f"#group_{layer}_{group.component_id}",
        )
        self.ui_elements.append(group_btn)
        self.group_buttons[key] = group_btn
        y += 24

        if is_expanded:
            for inst in group.instances:
                y = self._build_instance_row(x, y, width, group, inst)
        return y

    def _build_instance_row(
        self, x: int, y: int, width: int, group: ComponentGroup, inst: InstanceDamage
    ) -> int:
        """Render a single component instance row with colour + strike rules."""
        hp_pct = max(0.0, 1.0 - inst.damage_pct)
        is_destroyed = inst.damage_pct >= 1.0

        if is_destroyed:
            color = HP_DESTROYED
            strike = True
        elif inst.is_damage_induced_inactive:
            color = HP_CRITICAL
            strike = True
        elif not inst.is_active:
            color = MUTED_GREY
            strike = False
        else:
            color = _formatters_get_damage_color(hp_pct)
            strike = False

        text = (
            f"      • {group.display_name} #{inst.instance_index + 1}  "
            f"{int(round(hp_pct * 100))}%"
        )
        label = UILabel(
            relative_rect=pygame.Rect(x + 25, y, width - 40, 22),
            text=text,
            manager=self.manager,
            container=self.scroll_container,
        )
        # UILabel does not support HTML styling in this pygame_gui version,
        # so apply the chosen tier directly and rebuild the drawable shape.
        label.text_colour = pygame.Color(*color)
        label.rebuild()
        # Tag the label with the chosen tier so tests can introspect.
        label._proj315_color = color  # type: ignore[attr-defined]
        label._proj315_strike = strike  # type: ignore[attr-defined]
        self.ui_elements.append(label)

        if strike:
            self._apply_strikethrough(label, color)

        return y + 24

    def _apply_strikethrough(self, label: UILabel, color: Tuple[int, int, int]) -> None:
        """Overlay a horizontal line across `label` to convey strike.

        pygame_gui has no native ``<s>`` rich-text. Pattern mirrors
        `game/ui/screens/test_lab/dialogs.py`. The overlay is a
        `UIImage` inside the same scroll container so it scrolls with
        the label and gets cleaned up via `ui_elements`.

        If pygame_gui adds `<s>` support in a future release, prefer
        that and remove this helper.
        """
        rect = label.relative_rect
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        line_y = rect.height // 2
        pygame.draw.line(
            surf,
            color,
            (4, line_y),
            (rect.width - 4, line_y),
            1,
        )
        overlay = UIImage(
            relative_rect=rect.copy(),
            image_surface=surf,
            manager=self.manager,
            container=self.scroll_container,
        )
        self.ui_elements.append(overlay)

    def toggle_layer(self, layer_name: str) -> None:
        """Toggle a layer's expanded/collapsed state."""
        if layer_name in self.expanded_layers:
            self.expanded_layers[layer_name] = not self.expanded_layers[layer_name]
            if self.current_ship:
                self._clear_elements()
                self._build_ship_display(self.current_ship)

    def toggle_group(self, layer: str, component_id: str) -> None:
        """Toggle a component group's expanded/collapsed state."""
        key = (layer, component_id)
        self.expanded_groups[key] = not self.expanded_groups.get(key, False)
        if self.current_ship:
            self._clear_elements()
            self._build_ship_display(self.current_ship)

    def process_event(self, event) -> bool:
        """
        Process UI events.

        Args:
            event: pygame event

        Returns:
            True if event was handled
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.btn_remove and event.ui_element == self.btn_remove:
                if self.on_remove_ship and self.current_ship:
                    self.on_remove_ship(self.current_ship)
                return True
            for layer_name, button in self.layer_buttons.items():
                if event.ui_element == button:
                    self.toggle_layer(layer_name)
                    return True
            for (layer, comp_id), button in self.group_buttons.items():
                if event.ui_element == button:
                    self.toggle_group(layer, comp_id)
                    return True
        return False

    def kill(self) -> None:
        """Clean up all UI elements."""
        self._clear_elements()
        if self.panel:
            self.panel.kill()


def get_damage_color(hp_pct: float, is_active: bool = True) -> Tuple[int, int, int]:
    """Re-export of `game.ui.utils.formatters.get_damage_color`.

    Kept for backward-compat; some callers and tests still import it
    from this module. New code should import from `formatters`.
    """
    return _formatters_get_damage_color(hp_pct, is_active=is_active)
