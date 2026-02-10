import pytest
from game.simulation.systems.resource_manager import ResourceState, ResourceRegistry, ResourceConsumption
from collections import namedtuple

# Mock Component/Ship for Ability testing
MockShip = namedtuple('MockShip', ['resources'])
MockComponent = namedtuple('MockComponent', ['ship', 'ability_instances'])


class TestResourceState:
    def test_consume(self):
        r = ResourceState("fuel", max_value=100, current_value=50)
        assert r.consume(10) is True
        assert r.current_value == 40

        assert r.consume(50) is False  # Not enough
        assert r.current_value == 40  # Unchanged

    def test_regen(self):
        r = ResourceState("energy", max_value=100, current_value=0, regen_rate=10)
        # With new tick based system, we need to loop or change test expectation.
        # Original test expected 1.0s update. Now 1 tick is 0.01s.
        # r.regen_rate is 10/sec. 0.01s -> 0.1 resource per tick.
        # To get 10 resource, we need 100 ticks.
        for _ in range(100):
            r.update()
        assert r.current_value == pytest.approx(10.0)

        # Update enough to cap
        # 9 more seconds = 900 ticks
        for _ in range(900):
            r.update()
        assert r.current_value == pytest.approx(100.0)


class TestResourceRegistry:
    def test_registration(self):
        reg = ResourceRegistry()
        reg.register_storage("fuel", 100)

        r = reg.get_resource("fuel")
        assert r is not None
        assert r.max_value == 100

        # Add more storage
        reg.register_storage("fuel", 50)
        assert r.max_value == 150

    def test_generation_registration(self):
        reg = ResourceRegistry()
        reg.register_generation("energy", 5)

        r = reg.get_resource("energy")
        assert r is not None
        assert r.regen_rate == 5

        reg.register_generation("energy", 10)
        assert r.regen_rate == 15

    def test_get_resource_names_empty(self):
        """get_resource_names returns empty list when no resources registered."""
        reg = ResourceRegistry()
        assert reg.get_resource_names() == []

    def test_get_resource_names_returns_all_registered(self):
        """get_resource_names returns all registered resource names."""
        reg = ResourceRegistry()
        reg.register_storage("fuel", 100)
        reg.register_storage("energy", 50)
        reg.register_generation("ammo", 5)

        names = reg.get_resource_names()
        assert set(names) == {"fuel", "energy", "ammo"}


class TestAbilities:
    def test_consumption_ability(self):
        reg = ResourceRegistry()
        reg.register_storage("ammo", 10)
        reg.get_resource("ammo").current_value = 10

        ship = MockShip(reg)
        comp = MockComponent(ship, [])

        # Activation Trigger
        ability = ResourceConsumption(comp, {"resource": "ammo", "amount": 1, "trigger": "activation"})

        assert ability.check_and_consume() is True
        assert reg.get_resource("ammo").current_value == 9

        # Drain
        reg.get_resource("ammo").current_value = 0
        assert ability.check_and_consume() is False
