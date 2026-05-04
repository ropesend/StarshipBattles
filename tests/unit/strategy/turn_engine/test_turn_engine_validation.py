"""
PROJ-332 — Characterization test for `TurnEngine.validate_colonize_order`.

Pins:
- `validate_colonize_order` constructs / invokes `ColonizeValidator.validate`
  with positional args `(galaxy, fleet, target_planet, registries.components)`.
- The validator's return value is passed through unchanged.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.validation import ValidationResult
from game.strategy.engine.turn_engine import TurnEngine


class TestValidateColonizeOrder:
    """Pin the delegation contract from TurnEngine to ColonizeValidator."""

    def test_validate_colonize_order_constructs_validator_with_registries_fleet_planet_and_returns_result_unchanged(
        self, fresh_registries, mock_fleet, mock_galaxy, mock_planet
    ):
        """`validate_colonize_order` must:

        1. Call `ColonizeValidator.validate(galaxy, fleet, target_planet,
           component_registry)` with the registries' `components` field as
           the fourth positional arg.
        2. Return the validator's `ValidationResult` unchanged (same object).

        Patches the `ColonizeValidator` symbol on the `game.strategy.validation`
        package — that's the import site `validate_colonize_order` reads from
        via `from game.strategy.validation import ColonizeValidator`.
        """
        engine = TurnEngine(registries=fresh_registries, ai_factory=MagicMock())

        sentinel_result = ValidationResult.success()

        with patch(
            'game.strategy.validation.ColonizeValidator'
        ) as mock_validator_cls:
            mock_validator_cls.validate.return_value = sentinel_result

            returned = engine.validate_colonize_order(
                mock_galaxy, mock_fleet, mock_planet
            )

        # Pin pass-through return: same object (not a copy / repackage).
        assert returned is sentinel_result

        # Pin call shape: positional (galaxy, fleet, target_planet,
        # registries.components). registries.components is sourced from the
        # engine's `_registries` slot.
        mock_validator_cls.validate.assert_called_once_with(
            mock_galaxy, mock_fleet, mock_planet, fresh_registries.components
        )
