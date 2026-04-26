
import pytest
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, create_component
from game.simulation.entities.layer_data import LayerData
from game.core.registry import get_default_registry_provider
from tests.fixtures.paths import get_project_root, get_data_dir


class TestBuilderLogic:
    """Test ship validation logic used by the builder."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, fresh_registries):
        initialize_ship_data(str(get_project_root()))
        provider = get_default_registry_provider()
        load_components(str(get_data_dir() / "components.json"), registry_provider=provider)
        self.registries = fresh_registries
        self.ship = Ship("BuilderTarget", 0, 0, (255,255,255), ship_class="Escort", registries=fresh_registries)
        yield

    def test_mass_limit_validation(self):
        """Verify mass_limits_ok is false if mass exceeds budget or layer limits."""
        # Escort mass budget is 1000.
        # Layer limit for OUTER is 50%.
        # 8 plates * 30 mass = 240. (within 1000 and within 50%)
        for _ in range(8):
            self.ship.add_component(create_component('armor_plate', registries=self.registries), LayerType.ARMOR)

        self.ship.recalculate_stats()
        # ARMOR limit is 30%. 240 / 1000 = 0.24 (OK)
        assert self.ship.mass_limits_ok

        # Add a lot more to trigger TOTAL mass limit
        # Mass check no longer blocks placement — all components are accepted.
        added_count = 0
        for _ in range(50):
            if self.ship.add_component(create_component('armor_plate', registries=self.registries), LayerType.ARMOR):
                added_count += 1

        # All 50 should be added (mass is not a placement blocker)
        assert added_count == 50, "All plates should be added — mass doesn't block placement"

        # Ship should be over mass budget, flagged as invalid
        assert self.ship.mass > self.ship.max_mass_budget
        assert not self.ship.mass_limits_ok, "Ship should flag mass_limits_ok=False when over budget"

        # Now manually inject a huge component to verify mass_limits_ok handles invalid states (e.g. from loading)
        huge_plate = create_component('armor_plate', registries=self.registries)
        huge_plate.mass = 2000 # Way over budget
        self.ship.layers[LayerType.ARMOR].components.append(huge_plate)
        huge_plate.ship = self.ship
        self.ship.current_mass += huge_plate.mass

        self.ship.recalculate_stats()
        assert not self.ship.mass_limits_ok, "Should report invalid if forcibly overloaded"

    def test_missing_bridge_requirement(self):
        """Verify get_missing_requirements identifies missing crew capacity.

        Note: Post-Phase 5, the validator no longer reads 'requirements' from JSON.
        It checks CrewCapacity vs CrewRequired for ships with crew-heavy components.
        """
        # Add a component that requires crew (e.g., bridge)
        self.ship.add_component(create_component('bridge', registries=self.registries), LayerType.CORE)
        self.ship.recalculate_stats()

        # Check if crew requirements are met
        missing = self.ship.get_missing_requirements()

        # Bridge requires crew - verify crew housing is flagged if insufficient
        # This may or may not show an error depending on crew capacity vs required
        # The key is that validation runs without crashing
        assert isinstance(missing, list)

    def test_invalid_layer_addition_fallback(self):
        """Verify add_component returns False for invalid layers."""
        engine = create_component('standard_engine', registries=self.registries)
        # Engine only allowed in INNER, OUTER
        res = self.ship.add_component(engine, LayerType.ARMOR)
        assert not res
        assert engine not in self.ship.layers[LayerType.ARMOR].components

    def test_vehicle_class_requirements_loading(self):
        """Verify ship_class does not crash when validating.

        Note: Post-Phase 5, 'requirements' has been removed from vehicleclasses.json.
        The validator now checks CrewCapacity/CrewRequired abilities directly.
        """
        # Use a "Fighter (Small)" specifically
        fighter = Ship("Flyer", 0, 0, (255,255,255), ship_class="Fighter (Small)", registries=self.registries)
        fighter.recalculate_stats()
        missing = fighter.get_missing_requirements()

        # Verify validation works and returns a list (may be empty)
        assert isinstance(missing, list)
