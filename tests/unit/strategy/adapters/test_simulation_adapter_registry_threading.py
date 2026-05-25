"""PROJ-361 regression: SimulationBattleResolver must thread an injected
``GameRegistries`` through to ``run_battle.registry_provider`` instead of
silently falling back to ``get_default_registry_provider()``.

Source review finding: Reviews/results/2026-05-05_strategy-layer-tech-debt-review/
report.md (finding #1). Before this regression test, ``simulation_adapter.py``
called ``run_battle(..., registry_provider=get_default_registry_provider())``
unconditionally — dropping any explicitly injected registries during ship
materialization. PROJ-361 closes that gap while preserving the PROJ-306
fallback when the caller passes ``registries=None``.
"""

from unittest.mock import MagicMock, patch


class _MockShipInstance:
    """Minimal ShipInstance-like stand-in matching the existing
    test_simulation_adapter.py shape so the spec compiler is satisfied.

    PROJ-361 audit (TC-02): ``to_ship`` mirrors the real
    ``ShipInstance.to_ship`` signature — ``registries`` is keyword-only and
    has no default. A permissive ``registries=None`` default would mask
    ``None``-passing bugs (CQ-01) in the production adapter.
    """

    def __init__(self, instance_id="i", combat_capable=True):
        self.instance_id = instance_id
        self.design_id = f"design-{instance_id}"
        self.design_data = {"theme_id": "Federation"}
        self.name = f"Ship-{instance_id}"
        self.components = {}
        self._combat_capable = combat_capable
        # PROJ-361 audit (TC-01): capture the registries argument so tests
        # can assert that ``_instances_to_ships`` threads the injected
        # registries through to ``ShipInstance.to_ship``.
        self.last_registries: object = None

    def is_combat_capable(self):
        return self._combat_capable

    def to_ship(self, pos, team_id=0, *, registries):  # noqa: D401
        self.last_registries = registries
        ship = MagicMock()
        ship.instance_id = self.instance_id
        return ship


def _make_adapter_fleet(fleet_id, ships):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.ships = ships
    fleet.task_forces = []
    return fleet


def _make_outcome(winner_team_id=0, duration=100, replay_id=None):
    from game.simulation.battle_outcome import ShipStatus

    outcome = MagicMock()
    outcome.duration_ticks = duration
    outcome.replay_id = replay_id

    team0 = MagicMock()
    team0.team_id = 0
    team1 = MagicMock()
    team1.team_id = 1

    def _team_ships(is_alive):
        ship = MagicMock()
        ship.status = ShipStatus.SURVIVED if is_alive else ShipStatus.DESTROYED
        return [ship]

    team0.ships = _team_ships(winner_team_id == 0)
    team1.ships = _team_ships(winner_team_id == 1)
    outcome.teams = (team0, team1)
    return outcome


class TestRegistryThreadingToRunBattle:
    """PROJ-361: ``registries`` argument must reach ``run_battle.registry_provider``."""

    def test_resolve_battle_threads_injected_registries(self, fresh_registries):
        """When the caller injects registries, those exact registries reach
        ``run_battle.registry_provider`` (identity, not equality)."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        # Marker mutation: change a unique sentinel into the components dict
        # so that any default-provider lookup of this key would miss it. The
        # threading test uses identity (`is`), but the marker also documents
        # *why* the injection matters end-to-end.
        fresh_registries.components["__PROJ361_MARKER__"] = {
            "id": "__PROJ361_MARKER__",
            "name": "PROJ-361 sentinel",
            "category": "special",
        }

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        ship_a = _MockShipInstance("a")
        ship_b = _MockShipInstance("b")
        fleet1 = _make_adapter_fleet(1, [ship_a])
        fleet2 = _make_adapter_fleet(2, [ship_b])

        captured = {}

        def _fake_run_battle(
            spec, *, ai_factory, registry_provider, capture_context,
            event_bus=None, pre_tick_loop_callback=None,
        ):
            captured["registry_provider"] = registry_provider
            captured["event_bus"] = event_bus
            captured["pre_tick_loop_callback"] = pre_tick_loop_callback
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle(
                [fleet1, fleet2], registries=fresh_registries
            )

        assert captured["registry_provider"] is fresh_registries, (
            "Injected GameRegistries was not threaded to run_battle.registry_provider; "
            "the resolver silently fell back to the default provider."
        )

        # PROJ-426 Phase 6 (Codex consult follow-up): the adapter must
        # thread the assembly's composed pre-tick callback into
        # `run_battle.pre_tick_loop_callback`. With two real combat fleets
        # the reboard setup registers and `composed_callback()` returns a
        # callable — not None. Calling it must install a ReboardTracker
        # on the engine, matching the runtime contract.
        pre_tick_cb = captured["pre_tick_loop_callback"]
        assert pre_tick_cb is not None, (
            "pre_tick_loop_callback must be non-None when combat fleets "
            "are present — the assembly's reboard setup should have "
            "registered into the PreTickBattleSetupRegistry."
        )
        assert callable(pre_tick_cb)

        # Exercise the callback against a fake engine to confirm it
        # reaches the actual integration surface (not a stale closure
        # that captures pre-Phase-4 side-channel attributes).
        from types import SimpleNamespace
        fake_engine = SimpleNamespace(mine_resolvers=[])
        pre_tick_cb(fake_engine)
        assert getattr(fake_engine, "reboard_tracker", None) is not None, (
            "Composed pre-tick callback did not install reboard_tracker on "
            "the engine — the reboard setup is not wired through the "
            "assembly seam."
        )

        # PROJ-361 audit (TC-01): the same injected registries must reach
        # ``_instances_to_ships`` → ``ShipInstance.to_ship``. A future
        # change that threads registries to ``run_battle`` but drops them
        # for post-battle ship conversion would otherwise pass silently.
        for ship_instance in (ship_a, ship_b):
            assert ship_instance.last_registries is fresh_registries, (
                "Injected GameRegistries was not threaded to "
                "_instances_to_ships → ShipInstance.to_ship."
            )

    def test_resolve_battle_falls_back_to_default_when_no_registries(self):
        """PROJ-306 fallback: when ``registries=None``, the resolver still
        calls ``get_default_registry_provider()`` — strategy layer is the
        only place that boundary is permitted."""
        from game.core.registry import get_default_registry_provider
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        ship_a = _MockShipInstance("a")
        ship_b = _MockShipInstance("b")
        fleet1 = _make_adapter_fleet(1, [ship_a])
        fleet2 = _make_adapter_fleet(2, [ship_b])

        captured = {}

        def _fake_run_battle(
            spec, *, ai_factory, registry_provider, capture_context,
            event_bus=None, pre_tick_loop_callback=None,
        ):
            captured["registry_provider"] = registry_provider
            captured["event_bus"] = event_bus
            captured["pre_tick_loop_callback"] = pre_tick_loop_callback
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle([fleet1, fleet2], registries=None)

        default_provider = get_default_registry_provider()
        assert captured["registry_provider"] is default_provider

        # PROJ-361 audit (CQ-01): the fallback default registries must
        # also reach ``_instances_to_ships``. Previously the shortcut and
        # post-battle ship-conversion paths passed raw ``None`` to
        # ``ShipInstance.to_ship``, crashing in ``ShipSerializer``.
        for ship_instance in (ship_a, ship_b):
            assert ship_instance.last_registries is default_provider, (
                "Default GameRegistries fallback did not reach "
                "_instances_to_ships → ShipInstance.to_ship."
            )

    def test_sole_survivor_shortcut_threads_registries_to_instances(
        self, fresh_registries
    ):
        """PROJ-361 audit (CQ-01): the ``shortcut_sole_survivor`` branch
        previously passed raw ``registries`` (possibly ``None``) directly
        to ``_instances_to_ships``. After remediation, the centralized
        ``_resolve_registries`` fallback runs first, so this branch
        must thread the resolved (non-None) registries through to
        ``ShipInstance.to_ship``."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        # Team 0 has a combat-capable ship; team 1 has none. This triggers
        # the sole-survivor shortcut without invoking ``run_battle``.
        ship_a = _MockShipInstance("a", combat_capable=True)
        ship_b = _MockShipInstance("b", combat_capable=False)
        fleet1 = _make_adapter_fleet(1, [ship_a])
        fleet2 = _make_adapter_fleet(2, [ship_b])

        result = resolver.resolve_battle(
            [fleet1, fleet2], registries=fresh_registries
        )

        assert result.winner == 0
        # Only the surviving team's ships are materialized — ship_a only.
        assert ship_a.last_registries is fresh_registries

    def test_sole_survivor_shortcut_uses_default_when_registries_none(self):
        """PROJ-361 audit (CQ-01): the sole-survivor shortcut must not
        crash when the caller follows the ``IBattleResolver`` default
        contract (``registries=None``). The centralized fallback must
        resolve a real ``GameRegistries`` before ``ShipInstance.to_ship``
        is called."""
        from game.core.registry import get_default_registry_provider
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        ship_a = _MockShipInstance("a", combat_capable=True)
        ship_b = _MockShipInstance("b", combat_capable=False)
        fleet1 = _make_adapter_fleet(1, [ship_a])
        fleet2 = _make_adapter_fleet(2, [ship_b])

        result = resolver.resolve_battle([fleet1, fleet2], registries=None)

        assert result.winner == 0
        assert ship_a.last_registries is get_default_registry_provider()
