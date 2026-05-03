"""
Tests for superweapon stabilizer blocking plumbing.

PROJ-277: Stabilizer blocking is routed through
`StabilizerRegistry.find_blocking_stabilizer` (data-driven) called from
`SuperweaponOrderProcessor._check_blocking_stabilizer`. Each handler
threads `component_registry` all the way down — without it, real facility
designs (bare `{"id": "..."}`) can't resolve abilities in the scanner and
every stabilizer is silently ineffective.

These tests mock `find_blocking_stabilizer` to cover plumbing shape only.
End-to-end coverage (real scanner + real registry lookup) lives in
`tests/integration/strategy/test_stabilizer_blocks_superweapon.py`.
"""
from unittest.mock import MagicMock, patch

import pytest

from game.strategy.data.order_types import OrderType
from game.strategy.services.stabilizer_registry import StabilizerSpec


@pytest.fixture
def processor():
    from game.strategy.engine.superweapon_order_processor import (
        SuperweaponOrderProcessor,
    )
    return SuperweaponOrderProcessor()


class TestCheckBlockingStabilizer:
    """`_check_blocking_stabilizer` delegates to StabilizerRegistry."""

    def test_returns_spec_when_registry_reports_block(self, processor):
        """If the registry returns a spec, the helper returns it verbatim."""
        planet = MagicMock()
        galaxy = MagicMock()
        empire = MagicMock()
        registry = {"stellar_stabilizer": {"abilities": {}}}
        stub_spec = StabilizerSpec(
            ability_name="StellarStabilizer",
            scopes=("sector", "system"),
            blocks=(OrderType.STELLERATE_STAR,),
        )

        with patch(
            "game.strategy.services.stabilizer_registry.find_blocking_stabilizer",
            return_value=stub_spec,
        ) as mock_find:
            result = processor._check_blocking_stabilizer(
                OrderType.STELLERATE_STAR, planet, galaxy, [empire], registry
            )

        assert result is stub_spec
        mock_find.assert_called_once_with(
            OrderType.STELLERATE_STAR, planet, galaxy, [empire], registry
        )

    def test_returns_none_when_registry_reports_no_block(self, processor):
        """Passthrough of None from the registry."""
        with patch(
            "game.strategy.services.stabilizer_registry.find_blocking_stabilizer",
            return_value=None,
        ):
            result = processor._check_blocking_stabilizer(
                OrderType.IMPLODE_PLANET,
                reference_planet=MagicMock(),
                galaxy=MagicMock(),
                empires=[MagicMock()],
                component_registry={},
            )
        assert result is None

    def test_threads_component_registry_argument(self, processor):
        """Must forward the component_registry unchanged — forgetting this
        was the whole PROJ-277 bug."""
        sentinel = object()
        with patch(
            "game.strategy.services.stabilizer_registry.find_blocking_stabilizer",
            return_value=None,
        ) as mock_find:
            processor._check_blocking_stabilizer(
                OrderType.CLOSE_WARP_POINT,
                reference_planet=MagicMock(),
                galaxy=MagicMock(),
                empires=[],
                component_registry=sentinel,
            )
        # PROJ-322 Task 3.11 (S03-CAT6-001): accept either positional
        # or keyword passing — the documented intent is just "forwarded
        # unchanged", not "passed positionally".
        args, kwargs = mock_find.call_args
        assert sentinel in args or sentinel in kwargs.values(), (
            f"sentinel not forwarded; args={args}, kwargs={kwargs}"
        )
