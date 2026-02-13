import pytest
import math

from game.simulation.components.component import load_components, create_component, load_modifiers
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


@pytest.fixture
def loaded_data(fresh_registries):
    """Provide fresh_registries for tests."""
    return fresh_registries


class TestScalingLogic:
    def test_consumption_scaling_linear(self, loaded_data):
        """Test linear consumption scaling."""
        engine = create_component('standard_engine', registries=loaded_data)

        # Get base consumption
        base_cons = 0
        from game.simulation.components.abilities.resources import ResourceConsumption
        for ab in engine.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'fuel':
                base_cons = ab.amount
                break

        engine.add_modifier('efficiency_mount', 0.8)  # 0.8x consumption multiplier
        engine.recalculate_stats()

        new_cons = 0
        for ab in engine.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'fuel':
                new_cons = ab.amount
                break

        assert new_cons == pytest.approx(base_cons * 0.8), "Fuel cost should scale linearly with size"

        # 2. Railgun - Ammo Cost
        rg = create_component("railgun", registries=loaded_data)
        base_ammo = 0
        for ab in rg.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'ammo':
                base_ammo = ab.amount
                break

        rg.add_modifier("simple_size_mount", 2.0)
        rg.recalculate_stats()

        new_ammo = 0
        for ab in rg.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'ammo':
                new_ammo = ab.amount
                break

        assert new_ammo == pytest.approx(base_ammo * 2), "Ammo cost should scale linearly with size"

        # 3. Laser Cannon - Energy Cost
        lc = create_component("laser_cannon", registries=loaded_data)
        base_energy = 0
        for ab in lc.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                base_energy = ab.amount
                break

        lc.add_modifier("simple_size_mount", 2.0)
        lc.recalculate_stats()

        new_energy = 0
        for ab in lc.ability_instances:
            if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                new_energy = ab.amount
                break

        assert new_energy == pytest.approx(base_energy * 2), "Energy cost should scale linearly with size"

    def _get_crew_req(self, comp):
        ab = comp.get_ability("CrewRequired")
        if ab: return ab.amount
        return comp.abilities.get("CrewRequired", 0)

    def test_crew_requirement_scaling_size_mount(self, loaded_data):
        """
        Verify Crew Required scales with sqrt(mass) for Size Mount.
        Size Mount x4 -> Mass x4 -> Sqrt(4) = 2x Crew Req.
        """
        # Railgun has CrewRequired: 5
        rg = create_component("railgun", registries=loaded_data)
        base_crew = self._get_crew_req(rg)
        assert base_crew == 5, "Base Railgun Crew Req should be 5"

        # Add Size Mount x4
        rg.add_modifier("simple_size_mount", 4.0)
        rg.recalculate_stats()

        expected_crew = int(math.ceil(base_crew * math.sqrt(4.0)))  # 5 * 2 = 10
        current_crew = self._get_crew_req(rg)

        assert current_crew == expected_crew, f"Crew Req should scale with sqrt(mass). Expected {expected_crew}, got {current_crew}"

    def test_crew_requirement_scaling_range_mount(self, loaded_data):
        """
        Verify Crew Required scales with sqrt(mass) for Range Mount.
        Range Mount Level 1 -> Mass x3.5 -> Sqrt(3.5).
        """
        # Railgun CrewReq: 5
        rg = create_component("railgun", registries=loaded_data)
        base_crew = self._get_crew_req(rg)

        rg.add_modifier("range_mount", 1.0)
        rg.recalculate_stats()

        mass_mult = 3.5 ** 1.0
        expected_crew = int(math.ceil(base_crew * math.sqrt(mass_mult)))
        current_crew = self._get_crew_req(rg)

        assert current_crew == expected_crew, f"Crew Req should scale with sqrt(mass_mult) for Range Mount. Expected {expected_crew}, Got {current_crew}"

    def test_crew_requirement_scaling_combined(self, loaded_data):
        """
        Verify scaling works if multiple modifiers affect mass.
        """
        # Use simple size x2 and Range Mount x1
        rg = create_component("railgun", registries=loaded_data)
        base_crew = self._get_crew_req(rg)

        rg.add_modifier("simple_size_mount", 2.0)
        rg.add_modifier("range_mount", 1.0)
        rg.recalculate_stats()

        # Mass Mults accumulate multiplicatively in current logic?
        # range_mount: stats['mass_mult'] *= 3.5^level
        # simple_size: stats['mass_mult'] *= scale

        total_mass_mult = 2.0 * 3.5
        expected_crew = int(math.ceil(base_crew * math.sqrt(total_mass_mult)))
        current_crew = self._get_crew_req(rg)

        assert current_crew == expected_crew, "Crew Req should scale with sqrt of total mass multiplier"
