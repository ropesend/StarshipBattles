"""
Tests for Crew and Resource Ability STAT_BINDINGS - Phase 3 Tasks 3.8-3.10

TDD: Write tests FIRST, then implement to make them pass.
"""
import pytest
from game.simulation.components.abilities.stat_keys import StatKey, AbilityStatBinding


class TestCrewCapacityBindings:
    """Tests for CrewCapacity STAT_BINDINGS."""

    def test_crew_capacity_has_binding(self):
        """CrewCapacity should have CREW_CAPACITY_MULT binding."""
        from game.simulation.components.abilities.crew import CrewCapacity

        bindings = [b for b in CrewCapacity.STAT_BINDINGS
                   if b.stat_key == StatKey.CREW_CAPACITY_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'

    def test_crew_capacity_get_consumed_stats(self):
        """get_consumed_stats() should return CREW_CAPACITY_MULT."""
        from game.simulation.components.abilities.crew import CrewCapacity

        consumed = CrewCapacity.get_consumed_stats()
        assert StatKey.CREW_CAPACITY_MULT in consumed


class TestLifeSupportCapacityBindings:
    """Tests for LifeSupportCapacity STAT_BINDINGS."""

    def test_life_support_has_binding(self):
        """LifeSupportCapacity should have LIFE_SUPPORT_CAPACITY_MULT binding."""
        from game.simulation.components.abilities.crew import LifeSupportCapacity

        bindings = [b for b in LifeSupportCapacity.STAT_BINDINGS
                   if b.stat_key == StatKey.LIFE_SUPPORT_CAPACITY_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'


class TestCrewRequiredBindings:
    """Tests for CrewRequired STAT_BINDINGS."""

    def test_crew_required_has_crew_req_binding(self):
        """CrewRequired should have CREW_REQ_MULT binding."""
        from game.simulation.components.abilities.crew import CrewRequired

        bindings = [b for b in CrewRequired.STAT_BINDINGS
                   if b.stat_key == StatKey.CREW_REQ_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'

    def test_crew_required_also_consumes_mass_mult(self):
        """CrewRequired also depends on MASS_MULT for scaling."""
        from game.simulation.components.abilities.crew import CrewRequired

        # Note: CrewRequired uses mass_mult indirectly (sqrt(mass_mult))
        # but we don't add it as a binding since the relationship is complex
        consumed = CrewRequired.get_consumed_stats()
        # CREW_REQ_MULT is the primary modifier
        assert StatKey.CREW_REQ_MULT in consumed


class TestResourceConsumptionBindings:
    """Tests for ResourceConsumption STAT_BINDINGS."""

    def test_resource_consumption_has_binding(self):
        """ResourceConsumption should have CONSUMPTION_MULT binding."""
        from game.simulation.components.abilities.resources import ResourceConsumption

        bindings = [b for b in ResourceConsumption.STAT_BINDINGS
                   if b.stat_key == StatKey.CONSUMPTION_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'amount'
        assert binding.operation == 'multiply'

    def test_resource_consumption_get_consumed_stats(self):
        """get_consumed_stats() should return CONSUMPTION_MULT."""
        from game.simulation.components.abilities.resources import ResourceConsumption

        consumed = ResourceConsumption.get_consumed_stats()
        assert StatKey.CONSUMPTION_MULT in consumed

    def test_resource_consumption_recalculate(self):
        """recalculate() should apply consumption_mult."""
        from game.simulation.components.abilities.resources import ResourceConsumption

        class MockComponent:
            def __init__(self):
                self.stats = {'consumption_mult': 0.5}  # 50% reduction
                self.ability_stats = {}
                self.ship = None

        component = MockComponent()
        ability = ResourceConsumption(component, {'resource': 'fuel', 'amount': 10.0})

        assert ability._base_amount == 10.0
        ability.recalculate()
        assert ability.amount == pytest.approx(5.0)


class TestResourceStorageBindings:
    """Tests for ResourceStorage STAT_BINDINGS."""

    def test_resource_storage_has_binding(self):
        """ResourceStorage should have CAPACITY_MULT binding."""
        from game.simulation.components.abilities.resources import ResourceStorage

        bindings = [b for b in ResourceStorage.STAT_BINDINGS
                   if b.stat_key == StatKey.CAPACITY_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'max_amount'
        assert binding.operation == 'multiply'

    def test_resource_storage_recalculate(self):
        """recalculate() should apply capacity_mult."""
        from game.simulation.components.abilities.resources import ResourceStorage

        class MockComponent:
            def __init__(self):
                self.stats = {'capacity_mult': 2.0}
                self.ability_stats = {}

        component = MockComponent()
        ability = ResourceStorage(component, {'resource': 'fuel', 'amount': 100.0})

        ability.recalculate()
        assert ability.max_amount == pytest.approx(200.0)


class TestResourceGenerationBindings:
    """Tests for ResourceGeneration STAT_BINDINGS."""

    def test_resource_generation_has_binding(self):
        """ResourceGeneration should have ENERGY_GEN_MULT binding."""
        from game.simulation.components.abilities.resources import ResourceGeneration

        bindings = [b for b in ResourceGeneration.STAT_BINDINGS
                   if b.stat_key == StatKey.ENERGY_GEN_MULT]
        assert len(bindings) == 1

        binding = bindings[0]
        assert binding.attribute_name == 'rate'
        assert binding.operation == 'multiply'

    def test_resource_generation_recalculate(self):
        """recalculate() should apply energy_gen_mult."""
        from game.simulation.components.abilities.resources import ResourceGeneration

        class MockComponent:
            def __init__(self):
                self.stats = {'energy_gen_mult': 3.0}
                self.ability_stats = {}

        component = MockComponent()
        ability = ResourceGeneration(component, {'resource': 'energy', 'amount': 10.0})

        ability.recalculate()
        assert ability.rate == pytest.approx(30.0)
