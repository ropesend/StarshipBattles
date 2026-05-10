"""
Tests for new stat getters added in Phase 2 of stats panel redesign.

Tests weapon, strategic movement, cargo, and superweapon getters
using real Ship objects with real components.
"""
import pytest

from game.core.constants import LayerType
from game.core.registry import GameRegistries, get_default_registry_provider


@pytest.fixture(scope="module")
def getter_module_setup():
    """Module-level setup: load game data."""
    from game.simulation.entities.ship_loader import initialize_ship_data
    from game.simulation.components.component import load_components, load_modifiers
    from tests.fixtures.paths import get_project_root, get_data_dir

    provider = get_default_registry_provider()
    initialize_ship_data(str(get_project_root()), registry_provider=provider)
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    load_modifiers(str(data_dir / "modifiers.json"), registry_provider=provider)

    yield


@pytest.fixture
def registries(getter_module_setup):
    """Create GameRegistries with real data."""
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


@pytest.fixture
def escort_ship(registries):
    """Create a bare Escort ship."""
    from game.simulation.entities.ship import Ship
    ship = Ship("Test Escort", 0, 0, (255, 255, 255), ship_class="Escort", registries=registries)
    ship.recalculate_stats()
    return ship


class TestWeaponGetters:
    """Tests for weapon-related stat getters."""

    def test_weapon_count_empty_ship(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_weapon_count
        assert get_weapon_count(escort_ship) == 0

    def test_weapon_count_with_weapons(self, escort_ship, registries):
        from game.simulation.components.component import create_component
        from game.ui.screens.builder.stat_getters import get_weapon_count

        gun = create_component('railgun', registries=registries)
        escort_ship.add_component(gun, LayerType.OUTER)
        escort_ship.recalculate_stats()

        assert get_weapon_count(escort_ship) >= 1

    def test_total_dps_empty_ship(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_total_dps
        assert get_total_dps(escort_ship) == 0

    def test_max_range_empty_ship(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_max_range
        assert get_max_range(escort_ship) == 0

    def test_dps_duration_no_weapons(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_dps_duration
        # No weapons means infinite duration (nothing to consume)
        result = get_dps_duration(escort_ship)
        assert result >= 0


class TestStrategicMovementGetters:
    """Tests for strategic movement stat getters."""

    def test_warp_capable_no_drive(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_warp_capable
        assert get_warp_capable(escort_ship) == 0.0

    def test_warp_jumps_no_drive(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_warp_jumps
        assert get_warp_jumps(escort_ship) == 0

    def test_fuel_per_hex_empty(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_fuel_per_hex
        assert get_fuel_per_hex(escort_ship) == 0

    def test_hex_range_no_fuel(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_hex_range
        result = get_hex_range(escort_ship)
        assert result == 0


class TestCargoGetters:
    """Tests for cargo and transport stat getters."""

    def test_cargo_capacity_empty(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_cargo_capacity
        assert get_cargo_capacity(escort_ship) == 0

    def test_pod_storage_empty(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_pod_storage
        assert get_pod_storage(escort_ship) == 0

    def test_colony_types_none(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_colony_types
        assert get_colony_types(escort_ship) == 'None'


class TestMiscGetters:
    """Tests for miscellaneous stat getters."""

    def test_command_status_has_bridge(self, escort_ship, registries):
        from game.simulation.components.component import create_component
        from game.ui.screens.builder.stat_getters import get_command_status

        bridge = create_component('bridge', registries=registries)
        escort_ship.add_component(bridge, LayerType.OUTER)
        escort_ship.recalculate_stats()

        assert get_command_status(escort_ship) == 1.0

    def test_command_status_no_bridge(self, registries):
        from game.simulation.entities.ship import Ship
        from game.ui.screens.builder.stat_getters import get_command_status

        ship = Ship("No Bridge", 0, 0, (255, 255, 255), ship_class="Escort", registries=registries)
        ship.recalculate_stats()
        assert get_command_status(ship) == 0.0

    def test_repair_rate_empty(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_repair_rate
        assert get_repair_rate(escort_ship) == 0

    def test_superweapon_summary_none(self, escort_ship):
        from game.ui.screens.builder.stat_getters import get_superweapon_summary
        assert get_superweapon_summary(escort_ship) == 'None'


class TestFormatters:
    """Tests for new formatters."""

    def test_fmt_yes_no(self):
        from game.ui.screens.builder.stat_getters import fmt_yes_no
        assert fmt_yes_no(1.0) == "Yes"
        assert fmt_yes_no(0.0) == "No"

    def test_fmt_int(self):
        from game.ui.screens.builder.stat_getters import fmt_int
        assert fmt_int(42.7) == "42"

    def test_fmt_text(self):
        from game.ui.screens.builder.stat_getters import fmt_text
        assert fmt_text("hello") == "hello"
        assert fmt_text("") == "None"
