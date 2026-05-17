"""Tests for layer-inspection helpers on ``component_inspector`` (PROJ-425 Phase 2).

Phase 2 of TD-06 moves the per-instance layer-view helpers off
``ShipInstance`` into the existing ``component_inspector`` module:

- ``iter_components_by_layer(ship)`` -> Dict[layer, List[ComponentInstanceView]]
- ``damaged_components_by_layer(ship)`` -> Dict[layer, List[(key, current_hp)]]
- ``count_damaged_components(ship)`` -> int
"""
from game.core.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.services import component_inspector


def _make_design():
    return {
        "name": "TestShip",
        "ship_class": "Escort",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "INNER": [{"id": "laser_cannon"}, {"id": "laser_cannon"}],
            "HULL": [{"id": "hull_plate"}],  # filtered out
        },
    }


def _make_ship(components: dict | None = None) -> ShipInstance:
    ship = ShipInstance(
        instance_id="ship-1",
        design_id="TestDesign",
        name="Test",
        owner_id=0,
        design_data=_make_design(),
    )
    if components is not None:
        ship.components = components
    return ship


def _cs(comp_id: str, idx: int, current: float, mx: float, active: bool = True) -> ComponentState:
    return ComponentState(
        component_id=comp_id,
        instance_index=idx,
        current_hp=current,
        max_hp=mx,
        is_active=active,
    )


class TestIterComponentsByLayer:
    def test_walks_design_layers_filters_hull(self):
        ship = _make_ship(
            components={
                component_state_key("bridge", 0): _cs("bridge", 0, 100, 100),
                component_state_key("laser_cannon", 0): _cs("laser_cannon", 0, 50, 80),
                component_state_key("laser_cannon", 1): _cs("laser_cannon", 1, 80, 80),
            }
        )

        result = component_inspector.iter_components_by_layer(ship)

        assert "HULL" not in result
        assert set(result.keys()) == {"CORE", "INNER"}
        assert len(result["CORE"]) == 1
        assert result["CORE"][0].component_id == "bridge"
        assert len(result["INNER"]) == 2
        # Per-instance index disambiguation
        assert result["INNER"][0].instance_index == 0
        assert result["INNER"][0].current_hp == 50
        assert result["INNER"][1].instance_index == 1
        assert result["INNER"][1].current_hp == 80

    def test_missing_state_with_unknown_component_skipped(self):
        """Unknown component with no per-instance state is skipped.

        When the component is not in the registry, the fallback returns
        None and the helper omits that instance from the result instead
        of emitting a meaningless 0/0 HP view.
        """
        ship = ShipInstance(
            instance_id="ship-1",
            design_id="TestDesign",
            name="Test",
            owner_id=0,
            design_data={
                "name": "TestShip",
                "ship_class": "Escort",
                "layers": {
                    "CORE": [{"id": "_does_not_exist_anywhere_"}],
                },
            },
        )

        result = component_inspector.iter_components_by_layer(ship)

        assert result == {"CORE": []}


class TestDamagedComponentsByLayer:
    def test_returns_damaged_grouped_by_layer(self):
        ship = _make_ship(
            components={
                component_state_key("bridge", 0): _cs("bridge", 0, 100, 100),  # not damaged
                component_state_key("laser_cannon", 0): _cs("laser_cannon", 0, 30, 80),  # damaged
                component_state_key("laser_cannon", 1): _cs("laser_cannon", 1, 80, 80),  # not damaged
            }
        )

        result = component_inspector.damaged_components_by_layer(ship)

        assert "CORE" not in result
        assert "INNER" in result
        assert len(result["INNER"]) == 1
        key, current_hp = result["INNER"][0]
        assert key == component_state_key("laser_cannon", 0)
        assert current_hp == 30

    def test_empty_when_no_damage(self):
        ship = _make_ship(
            components={
                component_state_key("bridge", 0): _cs("bridge", 0, 100, 100),
            }
        )
        assert component_inspector.damaged_components_by_layer(ship) == {}


class TestCountDamagedComponents:
    def test_counts_damaged_instances(self):
        ship = _make_ship(
            components={
                component_state_key("bridge", 0): _cs("bridge", 0, 100, 100),
                component_state_key("laser_cannon", 0): _cs("laser_cannon", 0, 30, 80),
                component_state_key("laser_cannon", 1): _cs("laser_cannon", 1, 10, 80),
            }
        )
        assert component_inspector.count_damaged_components(ship) == 2

    def test_zero_when_none_damaged(self):
        ship = _make_ship(
            components={
                component_state_key("bridge", 0): _cs("bridge", 0, 100, 100),
            }
        )
        assert component_inspector.count_damaged_components(ship) == 0
