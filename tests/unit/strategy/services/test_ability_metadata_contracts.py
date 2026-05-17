"""Cross-registry contract tests for ``AbilityMetadataRegistry`` (PROJ-429).

This file is incrementally populated:

* **Phase 1** (this file's initial state): smoke test that the unified
  registry is importable.
* **Phase 4**: ``test_every_command_action_ability_name_exists_in_registry``
  — every ``CommandSpec.action_ability_name`` has a metadata entry.
* **Phase 6**: stabilizer + superweapon ``ability_name`` -> kind-tag
  parity, build-rate-booster parity.

Splitting the contracts across phases lets each consumer migration land
its own contract test alongside its consumer code change.
"""
from __future__ import annotations

from game.strategy.services.ability_metadata import get_ability_metadata


def test_registry_smoke() -> None:
    """Phase 1 smoke: the unified registry is importable and answers at
    least one known query."""
    assert get_ability_metadata("ShieldModifier") is not None
