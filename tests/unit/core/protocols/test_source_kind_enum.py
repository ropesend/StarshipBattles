"""ENUM-001 (PROJ-470): typed ``SourceKind`` discriminator for IAbilitySource.

The ``source_kind`` discriminator was previously an untyped ``str`` with the
7 valid values living only in a docstring. This pins the typed ``StrEnum``
so adding an 8th kind without updating the enum is a type error, and verifies
the enum stays string-compatible for the existing ``== 'storm'`` /
``!= 'star'`` / f-string consumers (StrEnum members ARE str).
"""
from __future__ import annotations

from enum import StrEnum
from types import SimpleNamespace

import pytest

from game.core.protocols.strategy_entities import SourceKind


EXPECTED_KINDS = {
    "facility",
    "storm",
    "planet",
    "star",
    "warp_point",
    "system",
    "fleet",
}


def test_source_kind_is_strenum() -> None:
    """SourceKind must be a StrEnum so members compare equal to their str
    value — the existing provider-dict consumers compare with raw strings
    (`provider.get('source_kind') == 'storm'`, `!= 'star'`, f-strings)."""
    assert issubclass(SourceKind, StrEnum)


def test_source_kind_has_exactly_the_seven_known_kinds() -> None:
    assert {member.value for member in SourceKind} == EXPECTED_KINDS


def test_source_kind_members_are_string_compatible() -> None:
    assert SourceKind.STORM == "storm"
    assert SourceKind.STAR != "storm"
    assert f"sector:{SourceKind.STORM}" == "sector:storm"


@pytest.mark.parametrize(
    "module_name, cls_name, kwargs, expected",
    [
        ("storm", "StormAbilitySource", {"storm": SimpleNamespace(name="S", abilities={})}, "storm"),
        ("planet_intrinsic", "PlanetIntrinsicAbilitySource", {"planet": SimpleNamespace(), "system": SimpleNamespace()}, "planet"),
        ("star", "StarAbilitySource", {"star": SimpleNamespace(), "system": SimpleNamespace()}, "star"),
        ("system_archetype", "SystemAbilitySource", {"system": SimpleNamespace()}, "system"),
        ("warp_point", "WarpPointAbilitySource", {"warp_point": SimpleNamespace(), "system": SimpleNamespace()}, "warp_point"),
    ],
)
def test_adapters_return_typed_source_kind_equal_to_raw_string(
    module_name: str, cls_name: str, kwargs: dict, expected: str
) -> None:
    """Instantiate the REAL adapter and assert its ``source_kind`` is the typed
    enum member AND remains equal to the legacy raw string (StrEnum). Pins that
    the typing change did not alter the value the universal-collector payload
    carries."""
    import importlib

    mod = importlib.import_module(
        f"game.strategy.services.ability_sources.{module_name}"
    )
    adapter = getattr(mod, cls_name)(**kwargs)
    assert isinstance(adapter.source_kind, SourceKind)
    assert adapter.source_kind == expected  # StrEnum compares equal to its str


def test_source_kind_payload_survives_consumer_comparisons_and_serialization() -> None:
    """ENUM-001 characterization: the value a real adapter emits into the
    PROJ-300 universal-collector payload (``{'source_kind': source.source_kind,
    ...}`` in system_effects_collector.py) must still satisfy every existing
    raw-string consumer AND round-trip through JSON unchanged.

    Consumers pinned (live code):
      - conflict_resolution_engine.py: ``provider.get('source_kind') == 'storm'``
      - system_tree_panel.py:          ``provider.get('source_kind') != 'star'``
      - strategy_modifier_stack_builder.py: ``f"sector:{source_kind}"``
    """
    import json

    from game.strategy.services.ability_sources.storm import StormAbilitySource

    source = StormAbilitySource(storm=SimpleNamespace(name="Ion Front", abilities={}))
    # Mirror the collector payload field.
    provider = {"source_kind": source.source_kind}

    # conflict_resolution_engine.py:130
    assert provider.get("source_kind") == "storm"
    # system_tree_panel.py:21 (a storm is not a star)
    assert provider.get("source_kind") != "star"
    # strategy_modifier_stack_builder.py:120/133
    assert f"sector:{provider['source_kind']}" == "sector:storm"

    # The payload must JSON-serialize to the bare string (StrEnum -> str),
    # so any save/transport that stringifies it is unchanged.
    assert json.dumps(provider) == '{"source_kind": "storm"}'
