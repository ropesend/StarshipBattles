"""Unit tests for ShipValidatorHelper."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.simulation.entities.ship_validator_helper import ShipValidatorHelper


def _ship_with_registries(registries: object) -> MagicMock:
    ship = MagicMock()
    ship._registries = registries
    ship.mass_limits_ok = True
    return ship


def test_check_validity_uses_ship_registries_and_updates_mass_flag() -> None:
    registries = object()
    ship = _ship_with_registries(registries)
    result = SimpleNamespace(
        is_valid=False,
        errors=["Mass budget exceeded in OUTER layer"],
        warnings=[],
    )

    with patch(
        "game.simulation.entities.ship_validator_helper.get_or_create_validator"
    ) as get_validator:
        validator = MagicMock()
        validator.validate_design.return_value = result
        get_validator.return_value = validator

        assert ShipValidatorHelper(ship).check_validity() is False

    ship.recalculate_stats.assert_called_once_with()
    get_validator.assert_called_once_with(registry_provider=registries)
    validator.validate_design.assert_called_once_with(ship)
    assert ship.mass_limits_ok is False


def test_check_validity_leaves_mass_flag_true_for_non_mass_errors() -> None:
    ship = _ship_with_registries(object())
    result = SimpleNamespace(
        is_valid=False,
        errors=["Missing required bridge"],
        warnings=[],
    )

    with patch(
        "game.simulation.entities.ship_validator_helper.get_or_create_validator"
    ) as get_validator:
        validator = MagicMock()
        validator.validate_design.return_value = result
        get_validator.return_value = validator

        assert ShipValidatorHelper(ship).check_validity() is False

    assert ship.mass_limits_ok is True


def test_get_validation_warnings_returns_validator_warnings() -> None:
    registries = object()
    ship = _ship_with_registries(registries)
    result = SimpleNamespace(is_valid=True, errors=[], warnings=["soft warning"])

    with patch(
        "game.simulation.entities.ship_validator_helper.get_or_create_validator"
    ) as get_validator:
        validator = MagicMock()
        validator.validate_design.return_value = result
        get_validator.return_value = validator

        assert ShipValidatorHelper(ship).get_validation_warnings() == ["soft warning"]

    ship.recalculate_stats.assert_not_called()
    get_validator.assert_called_once_with(registry_provider=registries)
    validator.validate_design.assert_called_once_with(ship)


def test_get_missing_requirements_prefixes_errors_when_invalid() -> None:
    ship = _ship_with_registries(object())
    result = SimpleNamespace(
        is_valid=False,
        errors=["Missing required bridge", "Missing crew support"],
        warnings=[],
    )

    with patch(
        "game.simulation.entities.ship_validator_helper.get_or_create_validator"
    ) as get_validator:
        validator = MagicMock()
        validator.validate_design.return_value = result
        get_validator.return_value = validator

        missing = ShipValidatorHelper(ship).get_missing_requirements()

    assert missing == [
        "\u26a0 Missing required bridge",
        "\u26a0 Missing crew support",
    ]


def test_get_missing_requirements_returns_empty_list_when_valid() -> None:
    ship = _ship_with_registries(object())
    result = SimpleNamespace(is_valid=True, errors=["ignored"], warnings=[])

    with patch(
        "game.simulation.entities.ship_validator_helper.get_or_create_validator"
    ) as get_validator:
        validator = MagicMock()
        validator.validate_design.return_value = result
        get_validator.return_value = validator

        assert ShipValidatorHelper(ship).get_missing_requirements() == []
