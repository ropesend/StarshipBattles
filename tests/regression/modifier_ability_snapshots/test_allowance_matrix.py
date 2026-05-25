"""Data-driven modifier x component allowance matrix (PROJ-498 Phase 3).

For every (modifier, component) pair in `data/modifiers.json` x
`data/components.json` we assert that
``ModifierService.is_modifier_allowed`` matches the canonical intersection
rule applied at parametrize-collection time from the raw JSON:

* If the modifier declares ``restrictions.allow_types``, the component's
  ``type`` must be in that list.
* If the modifier declares ``restrictions.deny_types``, the component's
  ``type`` must NOT be in that list.
* If the modifier declares ``restrictions.allow_abilities``, the
  component's ``abilities`` dict must contain at least one of those keys.
* ``restrictions.deny_abilities`` is INTENTIONALLY IGNORED. The live
  service does not enforce it (see
  `docs/guides/modifier_system.md` restrictions caveat and
  `Projects/active_projects/PROJ-498/decisions.md`, Codex mid-project
  review Q5). Folding it into the expected rule here would silently
  expand semantics.

No override pairs. The user explicitly chose "rules are ground truth" at
plan time (`plan.md` User Decision Points). Future divergence is a real
data or service bug, not a permitted exception.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from game.simulation.services.modifier_service import ModifierService
from game.simulation.components.component import create_component


_REPO_ROOT = Path(__file__).resolve().parents[3]
_MODIFIERS_PATH = _REPO_ROOT / "data" / "modifiers.json"
_COMPONENTS_PATH = _REPO_ROOT / "data" / "components.json"


def _load_modifiers() -> list[dict]:
    with _MODIFIERS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["modifiers"]


def _load_components() -> list[dict]:
    with _COMPONENTS_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["components"]


def _expected_allowed(modifier: dict, component: dict) -> bool:
    """Canonical intersection rule, derived purely from raw JSON.

    Mirrors ``ModifierService.check_allowance`` exactly (minus the
    ``UNKNOWN_MODIFIER_ID`` branch, which cannot fire here because every
    pair is constructed from the registry). ``deny_abilities`` is
    intentionally ignored — see module docstring.
    """
    restrictions = modifier.get("restrictions") or {}

    if not restrictions:
        return True

    comp_type = component.get("type", "")
    comp_abilities = (component.get("abilities") or {}).keys()

    if "allow_types" in restrictions:
        if comp_type not in restrictions["allow_types"]:
            return False

    if "deny_types" in restrictions:
        if comp_type in restrictions["deny_types"]:
            return False

    if "allow_abilities" in restrictions:
        required = restrictions["allow_abilities"]
        if not any(abil in comp_abilities for abil in required):
            return False

    return True


_MODIFIERS = _load_modifiers()
_COMPONENTS = _load_components()


def _matrix_cases():
    """Cartesian product of (modifier, component) with expected bool.

    Generated once at module-collection time. ID format
    ``"{modifier_id}__{component_id}"`` so a failing pair is greppable.
    """
    cases = []
    for mod in _MODIFIERS:
        mod_id = mod["id"]
        for comp in _COMPONENTS:
            comp_id = comp["id"]
            cases.append(
                pytest.param(
                    mod_id,
                    comp_id,
                    _expected_allowed(mod, comp),
                    id=f"{mod_id}__{comp_id}",
                )
            )
    return cases


@pytest.mark.parametrize("mod_id, comp_id, expected", _matrix_cases())
def test_modifier_allowance_matrix(
    mod_id: str, comp_id: str, expected: bool, fresh_registries
) -> None:
    """Each (modifier, component) pair matches the canonical intersection rule.

    Failure here means EITHER a real data drift the user needs to know
    about, OR a regression in ``ModifierService``. Triage to the user;
    do not silently mark expected (see Task 3.2 notes in
    ``phase_3_checklist.md``).
    """
    comp = create_component(comp_id, registries=fresh_registries)
    service = ModifierService(modifier_registry=fresh_registries.modifiers)

    actual = service.is_modifier_allowed(mod_id, comp)
    assert actual is expected, (
        f"Pair '{mod_id}__{comp_id}': service returned {actual}, "
        f"canonical rule said {expected}. "
        f"This is either a data drift or a service regression — triage."
    )


def test_matrix_collection_sanity() -> None:
    """Pin the collection count so silent additions/removals are noticed."""
    cases = _matrix_cases()
    assert len(cases) == len(_MODIFIERS) * len(_COMPONENTS), (
        f"Expected {len(_MODIFIERS)} mods x {len(_COMPONENTS)} components "
        f"= {len(_MODIFIERS) * len(_COMPONENTS)} pairs; got {len(cases)}"
    )
    # Post-PROJ-497 surface: 13 modifiers x 169 components = 2197 pairs.
    # If this number changes, surface the change to the user; the project
    # plan documents 14 mods x 169 components (~2366) but the actual
    # shipped count is 13 modifiers because ``efficient_engines`` was
    # deleted in PROJ-497.
    assert len(cases) == 13 * 169, (
        f"Matrix size ({len(cases)}) drifted from the locked post-PROJ-497 "
        "surface (13 x 169). Surface to the user before relaxing this."
    )
