"""PROJ-438 Phase 7: order persistence + metadata convergence.

Per the prompt's D3 default LOCKED stance, ``IMPLICIT_ACTION_ORDER_TYPES``,
mission decomposition, and the ``JOIN_FLEET`` instant path are acceptable
specialized behavior unless the implementation audit proves blocking
leakage. The audit found no blocking leakage; the hardcoded 9-branch
target serialization in ``Order.to_dict()`` works fine and doesn't *block*
anything. The remaining metadata convergence step is to surface the
existing-but-unused ``CommandSpec.serializer_codec`` field through the
live registry view so a future project can drive ``Order.to_dict()`` and
``OrderSerializer._deserialize_target`` from metadata rather than from
inline ``isinstance`` branches.

This file pins:

1. ``CommandRegistry`` exposes ``serializer_codec_for(order_type)`` →
   the registered codec name (or ``None``).
2. ``OrderMetadataView`` exposes the same lookup via the canonical lazy
   facade pattern (no caching, cycle-safe).
3. The codec names declared on each CommandSpec match the discriminator
   strings that ``OrderSerializer._deserialize_target`` already
   understands (``hex_coord``, ``fleet_ref``, ``planet_ref``, ``transfer``,
   ``warp_params``, ``ship_id_list``, ``dict``). Drift between the two
   surfaces breaks this test.
"""
from __future__ import annotations

import pytest

from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata
from game.strategy.engine.commands.registry import (
    command_registry,
    seed_default_commands,
)


# Codec names that ``OrderSerializer._deserialize_target`` already handles
# verbatim (see ``game/strategy/data/order_serializer.py:99-152``). New
# CommandSpec.serializer_codec values introduced after Phase 7 must either
# extend this set AND the deserializer, or document why the codec is
# write-only.
KNOWN_DESERIALIZABLE_CODECS = frozenset({
    "hex_coord",
    "fleet_ref",
    "planet_ref",
    "transfer",
    "warp_params",
    "ship_id_list",
    "dict",
    # Special-case codecs handled by their own branches in to_dict:
    "colonize_params",
    "raw",
})


@pytest.fixture(autouse=True)
def _seeded_registry():
    if len(command_registry) == 0:
        seed_default_commands(command_registry)
    yield


class TestCommandRegistryExposesSerializerCodec:
    """Pin that the registry can answer 'what codec serializes this OrderType?'"""

    def test_registry_has_serializer_codec_for_method(self) -> None:
        assert hasattr(command_registry, "serializer_codec_for"), (
            "CommandRegistry must expose serializer_codec_for(order_type)"
        )

    def test_serializer_codec_for_move_is_hex_coord(self) -> None:
        # IssueMoveCommand declares serializer_codec='hex_coord'.
        codec = command_registry.serializer_codec_for(OrderType.MOVE)
        assert codec == "hex_coord", (
            f"OrderType.MOVE codec must be 'hex_coord', got {codec!r}"
        )

    def test_serializer_codec_for_transfer_is_transfer(self) -> None:
        codec = command_registry.serializer_codec_for(OrderType.TRANSFER)
        assert codec == "transfer"

    def test_serializer_codec_for_implode_planet_is_planet_ref(self) -> None:
        codec = command_registry.serializer_codec_for(OrderType.IMPLODE_PLANET)
        assert codec == "planet_ref"


class TestOrderMetadataViewExposesSerializerCodec:
    """Pin the matching lookup on the lazy view facade."""

    def test_view_exposes_serializer_codec_for(self) -> None:
        assert hasattr(order_metadata, "serializer_codec_for"), (
            "OrderMetadataView must expose serializer_codec_for(order_type)"
        )

    def test_view_returns_same_codec_as_registry(self) -> None:
        for order_type in (
            OrderType.MOVE,
            OrderType.TRANSFER,
            OrderType.IMPLODE_PLANET,
        ):
            assert (
                order_metadata.serializer_codec_for(order_type)
                == command_registry.serializer_codec_for(order_type)
            )


class TestCodecVocabularyConsistency:
    """Pin that every declared serializer_codec value is either understood
    by the deserializer or documented as a special-case."""

    def test_every_registered_codec_is_in_known_set(self) -> None:
        """Drift detector: every distinct codec value across the registry
        must be in ``KNOWN_DESERIALIZABLE_CODECS``. A new codec without
        matching deserializer plumbing breaks this test."""
        codecs = set()
        for spec in command_registry.all():
            codec = spec.serializer_codec
            if codec is not None:
                codecs.add(codec)
        unknown = codecs - KNOWN_DESERIALIZABLE_CODECS
        assert not unknown, (
            f"CommandSpec.serializer_codec contains unknown codec(s): "
            f"{sorted(unknown)}. Either extend "
            "OrderSerializer._deserialize_target or add to "
            "KNOWN_DESERIALIZABLE_CODECS with rationale."
        )

    def test_specs_sharing_order_type_declare_same_codec(self) -> None:
        """Authority-strength ratchet (PROJ-438 Phase 9 / Codex consult 2026-05-18).

        ``CommandRegistry.serializer_codec_for(order_type)`` resolves the
        first matching spec when multiple commands map to the same
        OrderType (e.g., ``ActivatePlanetAbilityCommand`` and
        ``DeactivatePlanetAbilityCommand`` both emit
        ``ACTIVATE_ABILITY``/``DEACTIVATE_ABILITY`` respectively; no
        OrderType-sharing example exists in production today, but the
        guard must fire before one slips in with inconsistent codecs).

        If multiple specs share an OrderType, they MUST declare the same
        ``serializer_codec`` — otherwise the lookup is ambiguous and
        any future ``Order.to_dict()`` flip to metadata-driven dispatch
        would silently pick the wrong codec. This test is the gate that
        must pass before that flip is attempted.
        """
        codec_by_order_type: dict[OrderType, set[str | None]] = {}
        for spec in command_registry.all():
            if spec.order_type is None:
                continue
            codec_by_order_type.setdefault(spec.order_type, set()).add(
                spec.serializer_codec
            )
        ambiguous = {
            ot: codecs
            for ot, codecs in codec_by_order_type.items()
            if len(codecs) > 1
        }
        assert not ambiguous, (
            f"Multiple CommandSpecs share an OrderType but declare "
            f"different serializer_codec values: {ambiguous}. "
            "serializer_codec_for() raises ValueError on this drift; "
            "align the codecs or narrow the OrderType-sharing."
        )

    def test_serializer_codec_for_raises_on_multi_spec_ambiguity(self) -> None:
        """PROJ-445 Phase 2 (DI-2026-05-18-002): the runtime guard on
        ``CommandRegistry.serializer_codec_for(order_type)``.

        The class-level
        :meth:`test_specs_sharing_order_type_declare_same_codec` ratchet
        pins the production registry shape, but it can only see specs
        present at the time the test runs. A future overlay, mod, or
        dynamic registration that violates the contract would otherwise
        bypass the ratchet and silently mis-route the codec at the
        first-match call site. The hardened lookup raises
        :class:`ValueError` on any multi-spec / multi-codec mismatch
        instead of returning a first-match guess.

        We exercise it against a fresh local registry so the production
        singleton is unaffected.
        """
        from game.strategy.engine.commands.registry import (
            CommandRegistry,
            CommandSpec,
        )

        class _DummyCommandA:
            pass

        class _DummyCommandB:
            pass

        class _DummyHandler:
            pass

        local_registry = CommandRegistry()
        local_registry.register(
            CommandSpec(
                command_class=_DummyCommandA,
                order_type=OrderType.MOVE,
                handler_class=_DummyHandler,
                category='action',
                execution_model='action',
                serializer_codec='hex_coord',
            )
        )
        local_registry.register(
            CommandSpec(
                command_class=_DummyCommandB,
                order_type=OrderType.MOVE,
                handler_class=_DummyHandler,
                category='action',
                execution_model='action',
                serializer_codec='fleet_ref',  # intentional drift
            )
        )

        with pytest.raises(ValueError, match="Ambiguous serializer_codec"):
            local_registry.serializer_codec_for(OrderType.MOVE)

    def test_serializer_codec_for_accepts_multiple_specs_with_same_codec(self) -> None:
        """PROJ-445 Phase 2 (DI-2026-05-18-002) companion: multi-spec
        registration on the same OrderType with *matching* codecs is
        unambiguous and must still resolve cleanly (rather than raising
        because the registry returned >1 row)."""
        from game.strategy.engine.commands.registry import (
            CommandRegistry,
            CommandSpec,
        )

        class _DummyCommandA:
            pass

        class _DummyCommandB:
            pass

        class _DummyHandler:
            pass

        local_registry = CommandRegistry()
        local_registry.register(
            CommandSpec(
                command_class=_DummyCommandA,
                order_type=OrderType.MOVE,
                handler_class=_DummyHandler,
                category='action',
                execution_model='action',
                serializer_codec='hex_coord',
            )
        )
        local_registry.register(
            CommandSpec(
                command_class=_DummyCommandB,
                order_type=OrderType.MOVE,
                handler_class=_DummyHandler,
                category='action',
                execution_model='action',
                serializer_codec='hex_coord',  # matches
            )
        )

        assert local_registry.serializer_codec_for(OrderType.MOVE) == 'hex_coord'
