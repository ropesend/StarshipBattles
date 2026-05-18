"""PROJ-438 Phase 5: typed planet strategic intents.

Replaces the stringly ``IssuePlanetOrderCommand(order_type: str)`` path
with two typed first-class commands: ``ActivatePlanetAbilityCommand`` and
``DeactivatePlanetAbilityCommand``. This file is the TDD contract: it
fails until the typed commands + handlers + facade helpers land, then
pins the new public surface.

Per Phase 5 scope reminder: surgical ~40 contained changes. The old
``IssuePlanetOrderCommand`` + ``IssuePlanetOrderCommandHandler`` +
``dispatch_issue_planet_order`` facade helper are deleted in the same
phase (CLAUDE.md Rule 4: root cause fixes only, no shims).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestTypedPlanetAbilityCommandsExist:
    """The new typed command DTOs must exist with the right field shape."""

    def test_activate_planet_ability_command_importable(self) -> None:
        from game.strategy.engine.commands import ActivatePlanetAbilityCommand
        assert ActivatePlanetAbilityCommand is not None

    def test_deactivate_planet_ability_command_importable(self) -> None:
        from game.strategy.engine.commands import DeactivatePlanetAbilityCommand
        assert DeactivatePlanetAbilityCommand is not None

    def test_activate_command_carries_required_fields(self) -> None:
        from game.strategy.engine.commands import ActivatePlanetAbilityCommand
        cmd = ActivatePlanetAbilityCommand(
            planet_id=1,
            facility_instance_id="fac-1",
            ability_name="shield",
            component_key="OUTER:0:shield",
        )
        assert cmd.planet_id == 1
        assert cmd.facility_instance_id == "fac-1"
        assert cmd.ability_name == "shield"
        assert cmd.component_key == "OUTER:0:shield"

    def test_deactivate_command_carries_required_fields(self) -> None:
        from game.strategy.engine.commands import DeactivatePlanetAbilityCommand
        cmd = DeactivatePlanetAbilityCommand(
            planet_id=1,
            facility_instance_id="fac-1",
            ability_name="shield",
            component_key="OUTER:0:shield",
        )
        assert cmd.planet_id == 1
        assert cmd.facility_instance_id == "fac-1"
        assert cmd.ability_name == "shield"
        assert cmd.component_key == "OUTER:0:shield"

    def test_typed_commands_carry_no_order_type_string_field(self) -> None:
        """The whole point of Phase 5: typed commands do NOT carry a
        stringly ``order_type`` field. The OrderType is implicit in the
        command class."""
        from game.strategy.engine.commands import (
            ActivatePlanetAbilityCommand,
            DeactivatePlanetAbilityCommand,
        )
        for cls in (
            ActivatePlanetAbilityCommand,
            DeactivatePlanetAbilityCommand,
        ):
            fields = {f.name for f in cls.__dataclass_fields__.values()}
            assert "order_type" not in fields, (
                f"{cls.__name__} must NOT carry stringly order_type field"
            )


class TestStringlyIssuePlanetOrderCommandRetired:
    """The stringly ``IssuePlanetOrderCommand`` and its handler must be
    deleted (CLAUDE.md Rule 4: no compat shims)."""

    def test_issue_planet_order_command_is_deleted(self) -> None:
        from game.strategy.engine import commands as commands_module
        assert not hasattr(commands_module, "IssuePlanetOrderCommand"), (
            "Stringly IssuePlanetOrderCommand must be deleted (Phase 5)."
        )

    def test_issue_planet_order_command_handler_is_deleted(self) -> None:
        from game.strategy.engine import planet_command_handlers as mod
        assert not hasattr(mod, "IssuePlanetOrderCommandHandler"), (
            "Stringly handler must be deleted (Phase 5)."
        )


class TestNewHandlersQueueCorrectOrders:
    """Handler integration: each typed command queues the correct
    OrderType on the target planet."""

    def _make_session_with_planet(self, ability_name="shield"):
        from game.strategy.engine.game_session import GameSession
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.data.planet import Planet, PlanetType
        from game.strategy.data.planetary_facility import PlanetaryFacility
        from game.core.hex_math import HexCoord

        config = GameConfig(
            players=[
                PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="B", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=2,
        )
        session = GameSession(config=config)
        active = session.empires[0]
        # Use a real planet from the galaxy (any will do); attach to active
        # empire and patch its validator-friendly shape.
        planet = next(iter(next(iter(session.galaxy.systems.values())).planets))
        planet.owner_id = active.id
        active.colonies.append(planet)
        return session, planet

    def test_activate_handler_queues_activate_ability_order(self) -> None:
        from game.strategy.engine.commands import ActivatePlanetAbilityCommand
        from game.strategy.engine.planet_command_handlers import (
            ActivatePlanetAbilityCommandHandler,
        )
        from game.strategy.data.order_types import OrderType

        session, planet = self._make_session_with_planet()
        cmd = ActivatePlanetAbilityCommand(
            planet_id=planet.id,
            facility_instance_id="fac-1",
            ability_name="shield",
            component_key="OUTER:0:shield",
        )
        # Patch the validator so we don't have to wire up real abilities.
        from game.strategy.validation import planet_order_validator
        original = planet_order_validator.PlanetOrderValidator.validate_activate_ability
        try:
            from game.core.validation import ValidationResult
            planet_order_validator.PlanetOrderValidator.validate_activate_ability = (
                staticmethod(lambda *args, **kw: ValidationResult.success())
            )
            result = ActivatePlanetAbilityCommandHandler().execute(session, cmd)
        finally:
            planet_order_validator.PlanetOrderValidator.validate_activate_ability = (
                staticmethod(original)
            )
        assert result.is_valid, result.message
        assert planet.orders, "Expected at least one order queued"
        assert planet.orders[-1].type is OrderType.ACTIVATE_ABILITY

    def test_deactivate_handler_queues_deactivate_ability_order(self) -> None:
        from game.strategy.engine.commands import DeactivatePlanetAbilityCommand
        from game.strategy.engine.planet_command_handlers import (
            DeactivatePlanetAbilityCommandHandler,
        )
        from game.strategy.data.order_types import OrderType

        session, planet = self._make_session_with_planet()
        cmd = DeactivatePlanetAbilityCommand(
            planet_id=planet.id,
            facility_instance_id="fac-1",
            ability_name="shield",
            component_key="OUTER:0:shield",
        )
        from game.strategy.validation import planet_order_validator
        original = planet_order_validator.PlanetOrderValidator.validate_deactivate_ability
        try:
            from game.core.validation import ValidationResult
            planet_order_validator.PlanetOrderValidator.validate_deactivate_ability = (
                staticmethod(lambda *args, **kw: ValidationResult.success())
            )
            result = DeactivatePlanetAbilityCommandHandler().execute(session, cmd)
        finally:
            planet_order_validator.PlanetOrderValidator.validate_deactivate_ability = (
                staticmethod(original)
            )
        assert result.is_valid, result.message
        assert planet.orders, "Expected at least one order queued"
        assert planet.orders[-1].type is OrderType.DEACTIVATE_ABILITY


class TestNewFacadeHelpersExist:
    """Façade verbs are auto-generated from each CommandSpec's
    ``facade_helper_name`` (prefix-stripped). Post-TD-08 the facade
    exposes verbs via ``facade.commands.<verb>``, not as flat
    ``dispatch_*`` methods. The new typed specs must expose
    ``commands.activate_planet_ability`` /
    ``commands.deactivate_planet_ability``; the legacy
    ``commands.issue_planet_order`` verb must be absent."""

    def _make_facade(self):
        from game.strategy.engine.game_session import GameSession
        from game.strategy.engine.game_config import GameConfig, PlayerConfig
        from game.strategy.facade.strategy_session_facade import (
            StrategySessionFacade,
        )

        session = GameSession(
            config=GameConfig(
                players=[
                    PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
                    PlayerConfig(name="B", theme="Atlantians", color=(0, 255, 0)),
                ],
                system_count=2,
            )
        )
        return StrategySessionFacade(session)

    def test_facade_commands_namespace_exposes_typed_verbs(self) -> None:
        facade = self._make_facade()
        assert hasattr(facade.commands, "activate_planet_ability"), (
            "facade.commands.activate_planet_ability must be exposed"
        )
        assert hasattr(facade.commands, "deactivate_planet_ability"), (
            "facade.commands.deactivate_planet_ability must be exposed"
        )

    def test_facade_commands_namespace_does_not_expose_legacy_verb(
        self,
    ) -> None:
        facade = self._make_facade()
        assert not hasattr(facade.commands, "issue_planet_order"), (
            "Legacy commands.issue_planet_order verb must be removed (Phase 5)."
        )
