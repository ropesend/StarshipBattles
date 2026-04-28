"""Food Allocation Editor — per-colony per-species slider UI (PROJ-284 Phase 4).

One row per species currently living on the colony. Each row has a
slider (0.0..5.0, step 0.05) and a text input that accepts any
non-negative value (the slider is a convenience; typed input is the
escape hatch for over-allocation > 5.0). Apply writes to
`planet.get_species_config(race_id).food_allocation`.

The label is data-driven: title reads
`{resource.name} Allocation — {planet.name}` where `resource` comes from
`ResourceCatalog.get(economy_config.primary_resource)`. Swap
`data/economy.json`'s first `population_consumption` entry to `"metals"`
and the title auto-relabels to "Metals Allocation — Earth" — the whole
point of PROJ-284's data-driven food resource.

Design parallels `gravity_target_editor.py` (single-slider + ideal/
match/clear/apply) adapted for multi-row layout. UI-construction helpers
are separated from row-data gathering and apply logic so the business
logic is testable without pygame_gui.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UILabel, UIButton, UIHorizontalSlider, UITextEntryLine

from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.config.economy_config import EconomyConfig
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)

# Slider range. Typed input can exceed MAX_SLIDER for user-override.
MIN_SLIDER: float = 0.0
MAX_SLIDER: float = 5.0
SLIDER_STEP: float = 0.05
DEFAULT_ALLOCATION: float = 1.0

ROW_HEIGHT: int = 70  # two-line: name+input, slider
WINDOW_PADDING: int = 10


@dataclass
class FoodAllocationRowData:
    """Pure data describing one species row — no pygame types.

    Separated from the UI widgets so row gathering is testable without
    a live pygame display surface.
    """
    race_id: str
    race_name: str
    population_count: int
    current_allocation: float


def gather_rows(
    planet: 'Planet',
    race_resolver: Optional[Callable[[str], Optional[Any]]] = None,
) -> List[FoodAllocationRowData]:
    """Build row data for each species on the colony.

    Args:
        planet: Planet with `populations` and `species_configs`.
        race_resolver: Optional `race_id -> RaceConfig` lookup. Used
            only for the display name. Missing / None -> fall back to
            the `race_id` string.

    Returns:
        One `FoodAllocationRowData` per entry in `planet.populations`.
    """
    rows: List[FoodAllocationRowData] = []
    for pop in planet.populations:
        cfg = planet.get_species_config(pop.race_id)
        display_name = pop.race_id
        if race_resolver is not None:
            race = race_resolver(pop.race_id)
            if race is not None:
                # Prefer race_name (species-level) if set; fall back to name.
                display_name = getattr(race, "race_name", None) or getattr(race, "name", None) or pop.race_id
        rows.append(FoodAllocationRowData(
            race_id=pop.race_id,
            race_name=display_name,
            population_count=pop.count,
            current_allocation=cfg.food_allocation,
        ))
    return rows


def resolve_food_resource_name(
    economy_config: 'EconomyConfig',
    resource_catalog: Any,
) -> str:
    """Return the display name for the configured food resource.

    Falls back to the raw resource id if the catalog doesn't know the
    resource (modders may ship an economy.json referencing a resource
    not in their installed resources.json — UI should still show
    something rather than crash).
    """
    resource_id = economy_config.primary_resource
    if resource_catalog is None:
        return resource_id
    try:
        definition = resource_catalog.get(resource_id)
    except (KeyError, AttributeError):
        return resource_id
    if definition is None:
        return resource_id
    return getattr(definition, "name", None) or resource_id


def compute_consumption_preview(
    population: int,
    allocation: float,
    population_consumption: Dict[str, float],
) -> Dict[str, float]:
    """Return the expected per-turn drain for one species, keyed by resource.

    PROJ-291 C2: post-PROJ-286 `EconomyConfig` declares multiple
    resources in `population_consumption`; the editor preview must show
    every resource the player's colony will drain. Mirrors
    `OrganicsConsumptionEngine._process_colony`:
        needed = pop.count * allocation * per_pop_rate.

    Negative allocation is clamped to 0.0 per-resource so a typo in the
    text entry doesn't flip the sign on the preview.
    """
    safe_allocation = max(0.0, allocation)
    return {
        resource: population * safe_allocation * rate
        for resource, rate in population_consumption.items()
    }


def apply_allocations(
    planet: 'Planet',
    allocations: Dict[str, float],
) -> None:
    """Write each (race_id -> allocation) entry to the colony config.

    Clamps negatives to 0.0 — `ColonySpeciesConfig.__post_init__`
    rejects negatives via `ValidationException`, and silently clamping
    is preferable to the editor raising from a typo.
    """
    for race_id, value in allocations.items():
        safe_value = max(0.0, float(value))
        cfg = planet.get_species_config(race_id)
        cfg.food_allocation = safe_value


class FoodAllocationEditor(StrategyModalWindow):
    """pygame_gui window with one row per species on a colony.

    PROJ-313: Migrated to StrategyModalWindow base class. Auto-registers
    with the window manager for modal tracking — clicks inside the editor
    no longer leak through to the strategy map.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        planet: 'Planet',
        economy_config: 'EconomyConfig',
        resource_catalog: Any = None,
        race_resolver: Optional[Callable[[str], Optional[Any]]] = None,
        *,
        window_manager: "StrategyWindowManager | None" = None,
        on_apply_callback: Optional[Callable[[int, Dict[str, float]], None]] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        self._resource_display_name = resolve_food_resource_name(economy_config, resource_catalog)
        super().__init__(
            rect, manager,
            window_display_title=f"{self._resource_display_name} Allocation — {planet.name}",
            resizable=False,
            window_manager=window_manager,
        )

        self.planet = planet
        self._economy = economy_config
        self._race_resolver = race_resolver
        self.on_apply_callback = on_apply_callback
        self.on_close_callback = on_close_callback

        self._rows: List[FoodAllocationRowData] = gather_rows(planet, race_resolver)
        # race_id -> (slider, text_entry, preview_label)
        self._row_widgets: Dict[str, tuple] = {}
        self._widgets: List[Any] = []

        self._build_ui()

    def _build_ui(self) -> None:
        container = self.get_container()
        container_w = container.get_rect().width
        container_h = container.get_rect().height
        y = WINDOW_PADDING

        if not self._rows:
            UILabel(
                relative_rect=pygame.Rect(WINDOW_PADDING, y, container_w - 2 * WINDOW_PADDING, 25),
                text="No populations on this colony.",
                manager=self.ui_manager,
                container=container,
            )
        else:
            for row in self._rows:
                self._build_row(row, y, container_w, container)
                y += ROW_HEIGHT

        # Bottom buttons
        btn_y = container_h - 45
        btn_w = 120

        self.btn_cancel = UIButton(
            relative_rect=pygame.Rect(WINDOW_PADDING, btn_y, btn_w, 35),
            text="Cancel",
            manager=self.ui_manager,
            container=container,
        )
        self.btn_apply = UIButton(
            relative_rect=pygame.Rect(container_w - btn_w - WINDOW_PADDING, btn_y, btn_w, 35),
            text="Apply",
            manager=self.ui_manager,
            container=container,
        )

    def _build_row(
        self,
        row: FoodAllocationRowData,
        y: int,
        container_w: int,
        container: Any,
    ) -> None:
        # Line 1: race name label + text entry + preview label
        name_w = 180
        entry_w = 80
        preview_w = container_w - name_w - entry_w - 3 * WINDOW_PADDING
        UILabel(
            relative_rect=pygame.Rect(WINDOW_PADDING, y, name_w, 25),
            text=f"{row.race_name}  (pop {row.population_count})",
            manager=self.ui_manager,
            container=container,
        )
        entry = UITextEntryLine(
            relative_rect=pygame.Rect(WINDOW_PADDING + name_w, y, entry_w, 25),
            manager=self.ui_manager,
            container=container,
            initial_text=f"{row.current_allocation:.2f}",
        )
        preview = UILabel(
            relative_rect=pygame.Rect(
                WINDOW_PADDING + name_w + entry_w + WINDOW_PADDING, y, preview_w, 25,
            ),
            text=self._preview_text(row.population_count, row.current_allocation),
            manager=self.ui_manager,
            container=container,
        )
        # Line 2: slider
        slider_w = container_w - 2 * WINDOW_PADDING
        slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(WINDOW_PADDING, y + 30, slider_w, 25),
            start_value=min(MAX_SLIDER, max(MIN_SLIDER, row.current_allocation)),
            value_range=(MIN_SLIDER, MAX_SLIDER),
            manager=self.ui_manager,
            container=container,
            click_increment=SLIDER_STEP,
        )
        self._row_widgets[row.race_id] = (slider, entry, preview)

    def _preview_text(self, pop: int, allocation: float) -> str:
        """PROJ-291 C2: render one preview segment per resource in
        `economy.population_consumption`. Single-resource economies look
        identical to the pre-migration UI; multi-resource economies
        surface every drain the engine will apply."""
        consumption = compute_consumption_preview(
            pop, allocation, self._economy.population_consumption,
        )
        if not consumption:
            return "Preview: (no resources declared)/turn"
        segments = [
            f"{amount:.3f} {resource.lower()}"
            for resource, amount in consumption.items()
        ]
        return "Preview: " + ", ".join(segments) + "/turn"

    def collect_allocations(self) -> Dict[str, float]:
        """Harvest one float per row. Prefers the typed entry when
        parseable; falls back to the slider value otherwise.

        Exposed as a public method so tests can drive the editor state
        without pygame-event plumbing.
        """
        result: Dict[str, float] = {}
        for row in self._rows:
            slider, entry, _ = self._row_widgets.get(row.race_id, (None, None, None))
            value = row.current_allocation
            if entry is not None:
                try:
                    value = float(entry.get_text().strip())
                except (ValueError, AttributeError):
                    # Fall back to slider on bad input.
                    if slider is not None:
                        value = slider.get_current_value()
            elif slider is not None:
                value = slider.get_current_value()
            result[row.race_id] = max(0.0, value)
        return result

    def update(self, time_delta: float) -> None:
        """Refresh preview labels as sliders move."""
        super().update(time_delta)
        for row in self._rows:
            slider, entry, preview = self._row_widgets.get(row.race_id, (None, None, None))
            if slider is None or preview is None:
                continue
            if slider.has_moved_recently:
                val = slider.get_current_value()
                if entry is not None:
                    entry.set_text(f"{val:.2f}")
                preview.set_text(self._preview_text(row.population_count, val))

    def process_event(self, event: pygame.event.Event) -> bool:
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_apply:
                self._on_apply()
                return True
            if event.ui_element == self.btn_cancel:
                self._on_cancel()
                return True

        if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self:
            if self.on_close_callback:
                self.on_close_callback()
            return True

        return handled

    def _on_apply(self) -> None:
        allocations = self.collect_allocations()
        logger.info(
            "Applying food allocations for %s: %s",
            self.planet.name, allocations,
        )
        if self.on_apply_callback:
            self.on_apply_callback(self.planet.id, allocations)
        self.kill()

    def _on_cancel(self) -> None:
        logger.debug("Food allocation edit cancelled for %s", self.planet.name)
        self.kill()
