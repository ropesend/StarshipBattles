"""Cross-registry contract tests for ``AbilityMetadataRegistry`` (PROJ-429).

This file is incrementally populated:

* **Phase 1** (initial state): smoke test that the unified registry is
  importable.
* **Phase 4**: ``test_every_command_action_ability_name_exists_in_registry``
  — every ``CommandSpec.action_ability_name`` has a metadata entry.
* **Phase 6**: stabilizer + superweapon ``ability_name`` -> kind-tag
  parity, build-rate-booster parity.

Splitting the contracts across phases lets each consumer migration land
its own contract test alongside its consumer code change.
"""
from __future__ import annotations

import pytest

from game.strategy.engine.commands.registry import (
    command_registry,
    seed_default_commands,
)
from game.strategy.services.ability_metadata import (
    StrategicKind,
    ability_has_kind_tag,
    get_ability_metadata,
)


def test_registry_smoke() -> None:
    """Phase 1 smoke: the unified registry is importable and answers at
    least one known query."""
    assert get_ability_metadata("ShieldModifier") is not None


# ---------------------------------------------------------------------------
# Phase 4 — every CommandSpec.action_ability_name has a registry entry.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _seeded_registry():
    """Ensure the command registry is seeded before each test."""
    if len(command_registry) == 0:
        seed_default_commands(command_registry)
    yield


def test_every_command_action_ability_name_exists_in_registry() -> None:
    """Every ``CommandSpec.action_ability_name`` (when set) must have a
    matching entry in ``AbilityMetadataRegistry``.

    This is an ENFORCED relationship — adding a new command-spec with a
    new action ability name now requires either:

    1. The ability to already exist in ``ability_metadata.py``, OR
    2. A new entry to be added to ``ability_metadata.py`` in the same
       change.

    Without this contract, the two truth surfaces could silently drift.
    """
    missing: list[str] = []
    for spec in command_registry.all():
        name = spec.action_ability_name
        if name is None:
            continue
        if get_ability_metadata(name) is None:
            missing.append(name)
    assert not missing, (
        f"CommandSpec.action_ability_name entries with no matching "
        f"AbilityMetadataRegistry entry: {sorted(set(missing))}. Add "
        f"metadata to game/strategy/services/ability_metadata.py."
    )


# ---------------------------------------------------------------------------
# Phase 6 — stabilizer / superweapon / build-rate-booster contracts.
# (Populated in the Phase 6 commit.)
# ---------------------------------------------------------------------------


def test_every_stabilizer_ability_name_has_stabilizer_kind_tag() -> None:
    """Phase 6: every ``STABILIZERS[*].ability_name`` is tagged
    ``StrategicKind.STABILIZER`` in the unified registry."""
    from game.strategy.services.stabilizer_registry import STABILIZERS

    missing: list[str] = []
    for spec in STABILIZERS:
        if not ability_has_kind_tag(spec.ability_name, StrategicKind.STABILIZER):
            missing.append(spec.ability_name)
    assert not missing, (
        f"STABILIZERS ability_name entries missing STABILIZER kind tag: "
        f"{sorted(missing)}"
    )


def test_every_superweapon_ability_name_has_superweapon_kind_tag() -> None:
    """Phase 6: every non-None ``SUPERWEAPONS[*].ability_name`` is
    tagged ``StrategicKind.SUPERWEAPON`` in the unified registry.

    ``ability_name is None`` is allowed (STELLERATE_STAR dispatches via
    system_destroyer rather than ability-ship lookup); those rows skip
    the contract.
    """
    from game.strategy.services.superweapon_registry import SUPERWEAPONS

    missing: list[str] = []
    for spec in SUPERWEAPONS:
        if spec.ability_name is None:
            continue
        if not ability_has_kind_tag(spec.ability_name, StrategicKind.SUPERWEAPON):
            missing.append(spec.ability_name)
    assert not missing, (
        f"SUPERWEAPONS ability_name entries missing SUPERWEAPON kind tag: "
        f"{sorted(missing)}"
    )


def test_build_rate_booster_has_kind_tag() -> None:
    """Phase 6: ``BuildRateBooster`` carries the BUILD_RATE_BOOSTER kind tag."""
    assert ability_has_kind_tag("BuildRateBooster", StrategicKind.BUILD_RATE_BOOSTER)
