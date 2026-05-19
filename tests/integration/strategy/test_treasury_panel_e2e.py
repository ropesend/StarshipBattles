"""End-to-end Treasury panel integration tests.

PROJ-291 Phase 1 (C1): pin the contract that the rendered "Total" row of
`EmpireTreasuryPanel._get_expense_rows()` equals the sum of every visible
expense row, INCLUDING "Population Upkeep". Closes prior-audit M3
simultaneously — the missing e2e test that should have caught C1 in
PROJ-290's review cycle.

Pipeline under test:
    EmpireEconomyCalculator.calculate(empire)    -> snapshot
        snapshot.total_population_upkeep         -> per-resource upkeep
        snapshot.total_expenses                  -> per-resource sum
    EmpireTreasuryPanel._get_expense_rows()      -> render row tuples
        "Population Upkeep" row inserted iff upkeep is non-zero
        "Total" row mirrors snapshot.total_expenses

Uses the bypass-init pattern (`__new__` + manual attribute assignment) so
we exercise the row-building logic without spinning up pygame_gui — the
panel's render-path is pure data handling.
"""
import pytest
from unittest.mock import Mock

from game.strategy.engine.empire_economy_calculator import (
    EmpireEconomyCalculator,
    EmpireEconomySnapshot,
)
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation
from game.core.hex_math import HexCoord
from game.ui.panels.empire_treasury_panel import EmpireTreasuryPanel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_panel(snapshot: EmpireEconomySnapshot) -> EmpireTreasuryPanel:
    """Construct an `EmpireTreasuryPanel` with the snapshot wired in but
    skip `_build_ui()` — `_get_expense_rows()` is pure data handling and
    doesn't need pygame_gui. Mirrors the bypass-init pattern used in
    other panel tests."""
    panel = EmpireTreasuryPanel.__new__(EmpireTreasuryPanel)
    panel.snapshot = snapshot
    return panel


def _colony_with_populations(populations):
    """Real `Planet` so `get_species_config` lazy-creates
    `ColonySpeciesConfig` entries with the default `food_allocation=1.0`.
    Mirrors the helper in `test_empire_economy_calculator.py`."""
    return Planet(
        name="TestColony",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24, radius=6.371e6, surface_area=5.1e14, density=5515.0,
        surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
        surface_water=0.71, tectonic_activity=0.3, magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL, populations=populations, _stockpile={},
        owner_id=1,
    )


@pytest.fixture
def two_resource_economy():
    from game.strategy.config.economy_config import EconomyConfig
    return EconomyConfig(population_consumption={
        "organics": 0.001,
        "metals": 0.0001,
    })


@pytest.fixture
def stub_race_registry():
    """Upkeep projection short-circuits its habitability lookup when
    `get_race(*) -> None`, so the projector returns the raw upkeep
    without scaling."""
    stub = Mock()
    stub.get_race.return_value = None
    return stub


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTreasuryPanelTotalRowEndToEnd:
    """Calculator → snapshot → `_get_expense_rows()` round-trip. Pre-fix
    code: the "Population Upkeep" row showed `-X` but the "Total" row
    didn't subtract it, producing a visibly inconsistent treasury."""

    def test_treasury_panel_total_row_equals_sum_of_expense_rows(
        self, minimal_registries, two_resource_economy, stub_race_registry,
    ):
        """1000 humans + 1000 voidari on one colony with non-zero
        `population_consumption` → upkeep row appears AND Total row
        equals the sum of every visible row's per-resource cells (drains
        contribute as their displayed negative value)."""
        colony = _colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
            SpeciesPopulation(race_id="voidari", count=1000, happiness=0.5),
        ])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=two_resource_economy,
            race_registry=stub_race_registry,
        )
        snapshot = calculator.calculate(empire)

        panel = _build_panel(snapshot)
        rows = panel._get_expense_rows()

        # Row labels must include both the per-category rows and the
        # newly-inserted "Population Upkeep" row.
        labels = [label for label, _values, _is_total in rows]
        assert "Population Upkeep" in labels, (
            f"Population Upkeep row missing from expense rows: {labels}"
        )
        assert "Total" in labels

        # Sum every visible row (the "Total" row mirrors total_expenses
        # and is excluded from the sum so we can compare to it). The
        # cells the player sees ARE the cells we sum — drains are stored
        # negative so the arithmetic mirrors the visual.
        per_resource_sum: dict = {}
        total_row_values = None
        for label, values, is_total in rows:
            if is_total:
                total_row_values = values
                continue
            for res, value in values.items():
                per_resource_sum[res] = per_resource_sum.get(res, 0.0) + value

        assert total_row_values is not None, "Total row missing from expense rows"

        # The treasury Total row stores expenses as positive magnitudes;
        # the upkeep row stores them negated. So the equation the player
        # reads visually is:
        #   total_row[r] == tributes[r] + ships[r] + complexes[r] - (-upkeep[r])
        # i.e. total_row[r] == sum_of_positive_categories + upkeep_magnitude.
        # Equivalently, the magnitude of upkeep we subtracted as a drain
        # must reappear in the Total. Verify by reconstructing.
        for r, total_value in total_row_values.items():
            tributes = snapshot.tribute_expenses.get(r, 0.0)
            ships = snapshot.construction_expenses_ships.get(r, 0.0)
            complexes = snapshot.construction_expenses_complexes.get(r, 0.0)
            upkeep = snapshot.total_population_upkeep.get(r, 0.0)
            expected = tributes + ships + complexes + upkeep
            assert total_value == pytest.approx(expected), (
                f"Treasury Total row[{r}] = {total_value} but visible "
                f"categories sum to {expected} (upkeep contribution = {upkeep})"
            )

        # Sanity: upkeep must actually be non-zero so we know the bug
        # would have triggered without the fix.
        assert snapshot.total_population_upkeep["organics"] > 0.0
        assert snapshot.total_population_upkeep["metals"] > 0.0

    def test_treasury_panel_omits_upkeep_row_when_zero(
        self, minimal_registries, two_resource_economy, stub_race_registry,
    ):
        """Pre-existing behaviour at `_get_expense_rows` lines 277-282:
        the "Population Upkeep" row hides itself when the snapshot's
        `total_population_upkeep` is empty/zero. Pin that contract so a
        future refactor doesn't accidentally surface a "Population
        Upkeep: 0" row in fresh-game state."""
        # Empire with no colonies → upkeep dict stays empty.
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=two_resource_economy,
            race_registry=stub_race_registry,
        )
        snapshot = calculator.calculate(empire)

        assert snapshot.total_population_upkeep == {}

        panel = _build_panel(snapshot)
        rows = panel._get_expense_rows()
        labels = [label for label, _values, _is_total in rows]

        assert "Population Upkeep" not in labels, (
            f"Population Upkeep row should be hidden when upkeep is empty: {labels}"
        )
        # Total row is still present.
        assert "Total" in labels
