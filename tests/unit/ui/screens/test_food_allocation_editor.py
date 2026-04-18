"""Unit tests for `FoodAllocationEditor` (PROJ-284 Phase 4 Task 4.3).

Tests split into:
- Pure-function tests (no pygame): `gather_rows`, `resolve_food_resource_name`,
  `compute_consumption_preview`, `apply_allocations`.
- Class-construction tests: `FoodAllocationEditor` with UI internals
  patched out, following the testing pattern used by other UIWindow
  classes (`test_build_queue_list_window.py`, etc).

Manual smoke testing (Task 4.6) is the authoritative sign-off for
integration with live pygame_gui; the unit layer guards the business
logic and title/label derivation.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.core.hex_math import HexCoord
from game.strategy.config.economy_config import EconomyConfig
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation


def _planet_with(
    populations,
    *,
    species_configs=None,
    name: str = "Earth",
    planet_id: int = 7,
) -> Planet:
    return Planet(
        name=name,
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        atmosphere={"N2": 78000, "O2": 21000},
        planet_type=PlanetType.CONTINENTAL,
        populations=populations,
        species_configs=species_configs or {},
        id=planet_id,
    )


# ---------------------------------------------------------------------------
# Pure-function tests (no pygame)
# ---------------------------------------------------------------------------

class TestGatherRows:
    def test_single_species_uses_race_id_as_fallback_name(self):
        """No resolver -> race_id is displayed."""
        from game.ui.screens.food_allocation_editor import gather_rows
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _planet_with([pop])
        rows = gather_rows(planet)
        assert len(rows) == 1
        assert rows[0].race_id == "human"
        assert rows[0].race_name == "human"
        assert rows[0].population_count == 1000
        assert rows[0].current_allocation == 1.0  # default

    def test_resolver_provides_display_name(self):
        """When a resolver returns a race config, use race_name."""
        from game.ui.screens.food_allocation_editor import gather_rows
        pop = SpeciesPopulation(race_id="rossarian", count=500, happiness=0.5)
        planet = _planet_with([pop])
        fake_race = MagicMock(race_name="Rossarians", name="Rossarian Empire")
        rows = gather_rows(planet, race_resolver=lambda rid: fake_race)
        assert rows[0].race_name == "Rossarians"

    def test_resolver_falls_back_to_name_then_race_id(self):
        from game.ui.screens.food_allocation_editor import gather_rows
        pop = SpeciesPopulation(race_id="xenomorph", count=1, happiness=0.0)
        planet = _planet_with([pop])
        # race_name empty but name set.
        # NB: MagicMock's `name` kwarg is reserved (sets the mock's
        # name attr, not `.name`), so set it via attribute assignment.
        race_name_missing = MagicMock(race_name="")
        race_name_missing.name = "Xenos"
        rows = gather_rows(planet, race_resolver=lambda rid: race_name_missing)
        assert rows[0].race_name == "Xenos"

    def test_multi_species_one_row_each(self):
        from game.ui.screens.food_allocation_editor import gather_rows
        planet = _planet_with([
            SpeciesPopulation(race_id="human", count=100, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=50, happiness=0.7),
        ])
        rows = gather_rows(planet)
        assert [r.race_id for r in rows] == ["human", "alien"]

    def test_current_allocation_reflects_existing_config(self):
        """Pre-set allocation surfaces via `Planet.get_species_config` lazy-load."""
        from game.ui.screens.food_allocation_editor import gather_rows
        pop = SpeciesPopulation(race_id="human", count=100, happiness=0.5)
        planet = _planet_with(
            [pop],
            species_configs={"human": ColonySpeciesConfig(food_allocation=2.5)},
        )
        rows = gather_rows(planet)
        assert rows[0].current_allocation == 2.5


class TestResolveFoodResourceName:
    def test_catalog_provides_display_name(self):
        from game.ui.screens.food_allocation_editor import resolve_food_resource_name
        catalog = MagicMock()
        catalog.get.return_value = MagicMock(name="Organics")
        # MagicMock treats .name specially — assign via attrs:
        definition = MagicMock()
        definition.name = "Organics"
        catalog.get.return_value = definition
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        assert resolve_food_resource_name(economy, catalog) == "Organics"

    def test_unknown_resource_falls_back_to_id(self):
        """Missing catalog entry -> show the id string."""
        from game.ui.screens.food_allocation_editor import resolve_food_resource_name
        catalog = MagicMock()
        catalog.get.return_value = None
        economy = EconomyConfig(population_food_resource="ectoplasm", food_per_pop_per_turn=0.001)
        assert resolve_food_resource_name(economy, catalog) == "ectoplasm"

    def test_none_catalog_falls_back_to_id(self):
        from game.ui.screens.food_allocation_editor import resolve_food_resource_name
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        assert resolve_food_resource_name(economy, None) == "organics"

    def test_catalog_raising_falls_back_to_id(self):
        from game.ui.screens.food_allocation_editor import resolve_food_resource_name
        catalog = MagicMock()
        catalog.get.side_effect = KeyError("boom")
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        assert resolve_food_resource_name(economy, catalog) == "organics"


class TestConsumptionPreview:
    def test_linear_scaling_with_allocation(self):
        from game.ui.screens.food_allocation_editor import compute_consumption_preview
        assert compute_consumption_preview(100, 1.0, 0.001) == pytest.approx(0.1)
        assert compute_consumption_preview(100, 2.0, 0.001) == pytest.approx(0.2)
        assert compute_consumption_preview(100, 0.0, 0.001) == pytest.approx(0.0)

    def test_negative_allocation_clamped_to_zero(self):
        from game.ui.screens.food_allocation_editor import compute_consumption_preview
        assert compute_consumption_preview(100, -1.0, 0.001) == 0.0


class TestApplyAllocations:
    def test_writes_each_allocation_to_colony_species_config(self):
        from game.ui.screens.food_allocation_editor import apply_allocations
        planet = _planet_with([
            SpeciesPopulation(race_id="human", count=100, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=50, happiness=0.5),
        ])
        apply_allocations(planet, {"human": 2.0, "alien": 0.25})
        assert planet.get_species_config("human").food_allocation == 2.0
        assert planet.get_species_config("alien").food_allocation == 0.25

    def test_negative_input_clamped_to_zero(self):
        """ColonySpeciesConfig rejects negatives at construction via
        ValidationException; clamping in the UI prevents a runtime crash
        from a typo."""
        from game.ui.screens.food_allocation_editor import apply_allocations
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        apply_allocations(planet, {"human": -0.5})
        assert planet.get_species_config("human").food_allocation == 0.0

    def test_over_five_allocation_preserved(self):
        """Typed-input escape-hatch lets users exceed the UI slider cap."""
        from game.ui.screens.food_allocation_editor import apply_allocations
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        apply_allocations(planet, {"human": 10.0})
        assert planet.get_species_config("human").food_allocation == 10.0


# ---------------------------------------------------------------------------
# FoodAllocationEditor class construction (UI internals mocked out)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_editor_internals():
    """Patch the UIWindow base + `_build_ui` so we can instantiate the
    editor without a live pygame display. Tests then exercise the
    non-UI methods (`collect_allocations`, title-derivation)."""
    with patch('game.ui.screens.food_allocation_editor.UIWindow.__init__', return_value=None):
        with patch.object(
            # patch `_build_ui` so the constructor doesn't touch widgets.
            # The tests access `._rows` + `._row_widgets` directly.
            __import__('game.ui.screens.food_allocation_editor', fromlist=['FoodAllocationEditor']).FoodAllocationEditor,
            '_build_ui'
        ):
            yield


class TestFoodAllocationEditorConstruction:
    def test_constructs_for_planet_with_one_species(self, mock_editor_internals):
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _planet_with([pop])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
        )
        assert len(editor._rows) == 1
        assert editor._rows[0].race_id == "human"

    def test_constructs_for_planet_with_multiple_species(self, mock_editor_internals):
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([
            SpeciesPopulation(race_id="human", count=100, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=50, happiness=0.5),
        ])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
        )
        assert len(editor._rows) == 2

    def test_title_uses_resource_catalog_display_name(self, mock_editor_internals):
        """Title = '{ResourceName} Allocation — {planet.name}'."""
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        catalog = MagicMock()
        definition = MagicMock()
        definition.name = "Organics"
        catalog.get.return_value = definition

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
            resource_catalog=catalog,
        )
        assert editor._resource_display_name == "Organics"

    def test_title_relabels_when_food_resource_swapped(self, mock_editor_internals):
        """Swap to 'metals' -> title shows 'Metals'. This is the whole
        point of PROJ-284's data-driven food-resource config."""
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        economy = EconomyConfig(population_food_resource="metals", food_per_pop_per_turn=0.001)
        catalog = MagicMock()
        definition = MagicMock()
        definition.name = "Metals"
        catalog.get.return_value = definition

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
            resource_catalog=catalog,
        )
        assert editor._resource_display_name == "Metals"


class TestFoodAllocationEditorCollectAndApply:
    def test_collect_allocations_reads_typed_input_over_slider(self, mock_editor_internals):
        """Typed input wins when parseable; slider is the fallback."""
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
        )

        slider = MagicMock(); slider.get_current_value.return_value = 1.0
        entry = MagicMock(); entry.get_text.return_value = "2.5"
        preview = MagicMock()
        editor._row_widgets["human"] = (slider, entry, preview)

        allocations = editor.collect_allocations()
        assert allocations == {"human": 2.5}

    def test_collect_allocations_accepts_values_over_five(self, mock_editor_internals):
        """Typed input can exceed the slider's 5.0 cap."""
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
        )
        slider = MagicMock(); slider.get_current_value.return_value = 5.0
        entry = MagicMock(); entry.get_text.return_value = "12.0"
        editor._row_widgets["human"] = (slider, entry, MagicMock())

        assert editor.collect_allocations() == {"human": 12.0}

    def test_collect_allocations_falls_back_to_slider_on_bad_input(self, mock_editor_internals):
        """Non-numeric text -> use slider value."""
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
        )
        slider = MagicMock(); slider.get_current_value.return_value = 3.0
        entry = MagicMock(); entry.get_text.return_value = "not-a-number"
        editor._row_widgets["human"] = (slider, entry, MagicMock())

        assert editor.collect_allocations() == {"human": 3.0}

    def test_apply_button_writes_all_rows_and_fires_callback(self, mock_editor_internals):
        """Simulate Apply: `_on_apply` writes via callback and kills self."""
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([
            SpeciesPopulation(race_id="human", count=100, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=50, happiness=0.5),
        ])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        on_apply = MagicMock()
        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
            on_apply_callback=on_apply,
        )
        # Seed widget mocks.
        for rid, value in (("human", 2.0), ("alien", 0.5)):
            slider = MagicMock(); slider.get_current_value.return_value = value
            entry = MagicMock(); entry.get_text.return_value = str(value)
            editor._row_widgets[rid] = (slider, entry, MagicMock())

        with patch.object(editor, 'kill') as mock_kill:
            editor._on_apply()
            mock_kill.assert_called_once()

        on_apply.assert_called_once()
        planet_id, allocations = on_apply.call_args[0]
        assert planet_id == 7
        assert allocations == {"human": 2.0, "alien": 0.5}

    def test_cancel_does_not_fire_apply_callback(self, mock_editor_internals):
        from game.ui.screens.food_allocation_editor import FoodAllocationEditor
        planet = _planet_with([SpeciesPopulation(race_id="human", count=100, happiness=0.5)])
        economy = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)

        on_apply = MagicMock()
        editor = FoodAllocationEditor(
            rect=pygame.Rect(0, 0, 600, 400),
            manager=MagicMock(),
            planet=planet,
            economy_config=economy,
            on_apply_callback=on_apply,
        )
        with patch.object(editor, 'kill'):
            editor._on_cancel()
        on_apply.assert_not_called()
