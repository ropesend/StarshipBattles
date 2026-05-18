"""PROJ-438 Phase 6: issuer-aware execution contract.

Replaces ``ActionExecutionEngine._execute_planet_action``'s private
``OrderProcessor._handler_registry`` reach-in + ``TypeError`` fallback
with one explicit unified contract:

- ``IOrderHandler`` declares ``execute_for_issuer`` with a single
  canonical 5-kwarg signature (``issuer``, ``order_owner``, ``empire``,
  ``galaxy``, ``registries``).
- Recovery handlers accept the extra kwargs (and ignore them) so the
  ActionExecutionEngine can call once without try/except.
- ``OrderProcessor`` exposes ``get_handler(order_type)`` as a public
  accessor so callers no longer reach into the underscore-prefixed
  ``_handler_registry`` attribute.

This file pins the unified shape so the reach-in + TypeError fallback
cannot creep back.
"""
from __future__ import annotations

import inspect

import pytest


class TestUnifiedIOrderHandlerSignature:
    """Pin the unified 5-kwarg ``execute_for_issuer`` signature."""

    def test_protocol_declares_execute_for_issuer(self) -> None:
        from game.strategy.engine.order_handlers.base import IOrderHandler

        assert hasattr(IOrderHandler, "execute_for_issuer"), (
            "IOrderHandler protocol must declare execute_for_issuer"
        )

    def test_recover_fighters_signature_accepts_galaxy_and_registries(self) -> None:
        from game.strategy.engine.order_handlers.recover_fighters import (
            RecoverFightersOrderHandler,
        )
        sig = inspect.signature(RecoverFightersOrderHandler.execute_for_issuer)
        # Must accept galaxy and registries kwargs (may ignore them).
        assert "galaxy" in sig.parameters, (
            "RecoverFightersOrderHandler.execute_for_issuer must accept galaxy kwarg"
        )
        assert "registries" in sig.parameters, (
            "RecoverFightersOrderHandler.execute_for_issuer must accept registries kwarg"
        )

    def test_recover_satellites_signature_accepts_galaxy_and_registries(self) -> None:
        from game.strategy.engine.order_handlers.recover_satellites import (
            RecoverSatellitesOrderHandler,
        )
        sig = inspect.signature(RecoverSatellitesOrderHandler.execute_for_issuer)
        assert "galaxy" in sig.parameters
        assert "registries" in sig.parameters

    def test_launch_fighters_signature_unchanged(self) -> None:
        """Launch handlers already had the 5-kwarg signature; preserve it."""
        from game.strategy.engine.order_handlers.launch_fighters import (
            LaunchFightersOrderHandler,
        )
        sig = inspect.signature(LaunchFightersOrderHandler.execute_for_issuer)
        for kw in ("issuer", "order_owner", "empire", "galaxy", "registries"):
            assert kw in sig.parameters, (
                f"LaunchFightersOrderHandler.execute_for_issuer missing {kw}"
            )

    def test_launch_satellites_signature_accepts_galaxy_and_registries(self) -> None:
        """PROJ-445 Phase 1 parity-gap fix — the original PROJ-438 ratchet
        omitted ``LaunchSatellitesOrderHandler``. The handler already had
        the 5-kwarg shape; this ratchet pins it so the next refactor that
        narrows the signature is caught here, not in production."""
        from game.strategy.engine.order_handlers.launch_satellites import (
            LaunchSatellitesOrderHandler,
        )
        sig = inspect.signature(LaunchSatellitesOrderHandler.execute_for_issuer)
        for kw in ("issuer", "order_owner", "empire", "galaxy", "registries"):
            assert kw in sig.parameters, (
                f"LaunchSatellitesOrderHandler.execute_for_issuer missing {kw}"
            )

    def test_lay_mines_signature_accepts_galaxy_and_registries(self) -> None:
        """PROJ-445 Phase 1 (F-B-001) — the original PROJ-438 ratchet also
        omitted ``LayMinesOrderHandler``, which is exactly how the
        ``registries`` kwarg drift slipped through PROJ-438's audit and
        sat unobserved until the post-refactor residue review. Pinning
        the 5-kwarg shape here is the prophylactic test for F-B-001."""
        from game.strategy.engine.order_handlers.lay_mines import (
            LayMinesOrderHandler,
        )
        sig = inspect.signature(LayMinesOrderHandler.execute_for_issuer)
        for kw in ("issuer", "order_owner", "empire", "galaxy", "registries"):
            assert kw in sig.parameters, (
                f"LayMinesOrderHandler.execute_for_issuer missing {kw}"
            )


class TestOrderProcessorPublicGetHandler:
    """Pin that ``OrderProcessor`` exposes a public ``get_handler`` accessor
    so callers don't reach into the private ``_handler_registry``."""

    def test_order_processor_has_public_get_handler(self) -> None:
        from game.strategy.engine.order_processor import OrderProcessor
        assert hasattr(OrderProcessor, "get_handler"), (
            "OrderProcessor must expose public get_handler(order_type)"
        )

    def test_get_handler_returns_registered_handler(self) -> None:
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.data.order_types import OrderType

        proc = OrderProcessor()
        # Every OrderType registered in the default handler registry must
        # resolve through the public accessor.
        handler = proc.get_handler(OrderType.RECOVER_FIGHTERS)
        assert handler is not None
        assert hasattr(handler, "execute_for_issuer")


class TestActionExecutionEngineHasNoReachInOrFallback:
    """Pin that ``ActionExecutionEngine._execute_planet_action`` no longer
    reaches into ``_handler_registry`` directly and no longer wraps the
    handler call in a TypeError-recovery try/except."""

    def test_no_private_handler_registry_reach_in(self) -> None:
        import inspect as _inspect
        from game.strategy.engine import action_execution_engine as mod

        src = _inspect.getsource(mod)
        # The old reach-in pattern: ``getattr(self._order_processor, "_handler_registry", ...)``
        assert "_handler_registry" not in src, (
            "ActionExecutionEngine must not reach into "
            "OrderProcessor._handler_registry; use the public get_handler accessor."
        )

    def test_no_typeerror_fallback_in_execute_planet_action(self) -> None:
        import inspect as _inspect
        from game.strategy.engine import action_execution_engine as mod

        src = _inspect.getsource(mod._execute_planet_action if hasattr(mod, "_execute_planet_action") else mod.ActionExecutionEngine._execute_planet_action)
        # The unified signature removes the need for a TypeError-recovery
        # fallback. If this assertion fires after Phase 6, the fallback
        # crept back in.
        assert "except TypeError" not in src, (
            "ActionExecutionEngine._execute_planet_action must not wrap the "
            "handler call in `except TypeError:` — the unified "
            "execute_for_issuer signature removes the need for it."
        )
