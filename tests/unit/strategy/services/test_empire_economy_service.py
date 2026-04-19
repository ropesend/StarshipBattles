"""Unit tests for `EmpireEconomyService` (PROJ-292 Phase 2 M1).

The service is a thin read-only facade over `EmpireEconomyCalculator`
that keeps the engine class out of the UI-layer import surface (per
docs/01_ARCHITECTURE.md layer rules). The facade exposes ONE method —
`get_snapshot(empire)` — and re-exports `EmpireEconomySnapshot` so UI
typing doesn't need to reach into the engine module.
"""
from __future__ import annotations

from unittest.mock import Mock


class TestEmpireEconomyServiceShape:
    """The service must produce the same snapshot as the underlying
    calculator (it's a facade, not a new implementation)."""

    def test_service_get_snapshot_returns_same_shape_as_calculator(
        self, minimal_registries,
    ):
        from game.strategy.engine.empire_economy_calculator import (
            EmpireEconomyCalculator,
        )
        from game.strategy.services.empire_economy_service import (
            EmpireEconomyService,
        )
        from game.strategy.data.empire import Empire

        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        # Service facade.
        service = EmpireEconomyService(registries=minimal_registries)
        service_snapshot = service.get_snapshot(empire)

        # Reference: direct engine-layer call.
        calc = EmpireEconomyCalculator(registries=minimal_registries)
        calc_snapshot = calc.calculate(empire)

        # All documented fields must match.
        for field in (
            "colony_production", "ship_production", "trade_production",
            "tribute_production", "mining_production", "total_production",
            "tribute_expenses", "construction_expenses_ships",
            "construction_expenses_complexes", "total_expenses",
            "total_population_upkeep", "net_resources",
            "current_storage", "max_storage",
        ):
            assert getattr(service_snapshot, field) == getattr(calc_snapshot, field), (
                f"Service snapshot diverged from calculator on field {field!r}"
            )

    def test_service_re_exports_snapshot_dataclass(self):
        """UI code should import `EmpireEconomySnapshot` from the
        service module, not the engine module. The re-export keeps the
        UI-facing import surface entirely within
        `game.strategy.services.*`."""
        from game.strategy.services.empire_economy_service import (
            EmpireEconomySnapshot as ServiceSnapshot,
        )
        from game.strategy.engine.empire_economy_calculator import (
            EmpireEconomySnapshot as EngineSnapshot,
        )

        # Same class (re-exported, not copied).
        assert ServiceSnapshot is EngineSnapshot

    def test_service_does_not_export_calculator_in_all(self):
        """`EmpireEconomyCalculator` is an engine-layer implementation
        detail. The service's `__all__` must NOT expose it so linters
        can catch accidental UI→engine imports via the service."""
        from game.strategy.services import empire_economy_service

        assert hasattr(empire_economy_service, "__all__"), (
            "The service module must declare __all__ so the UI layer's "
            "allowed import surface is explicit."
        )
        assert "EmpireEconomyCalculator" not in empire_economy_service.__all__, (
            f"__all__ must NOT expose the engine-layer calculator; found: "
            f"{empire_economy_service.__all__}"
        )
        assert "EmpireEconomyService" in empire_economy_service.__all__
        assert "EmpireEconomySnapshot" in empire_economy_service.__all__

    def test_service_accepts_full_kwarg_set(self, minimal_registries):
        """The service's constructor must pass through every kwarg the
        engine-layer calculator accepts, so existing UI call sites can
        migrate with identical argument shape."""
        from game.strategy.services.empire_economy_service import (
            EmpireEconomyService,
        )
        from game.strategy.config.economy_config import EconomyConfig
        from game.strategy.data.empire import Empire

        economy = EconomyConfig(population_consumption={"organics": 0.001})
        stub_registry = Mock()
        stub_registry.get_race.return_value = None

        service = EmpireEconomyService(
            registries=minimal_registries,
            economy_config=economy,
            race_registry=stub_registry,
        )

        # Smoke: get_snapshot still works with all three deps wired.
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}
        snapshot = service.get_snapshot(empire)
        # total_population_upkeep is populated (empty dict for a
        # colony-less empire, but the code path is exercised).
        assert snapshot.total_population_upkeep == {}
