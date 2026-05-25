"""PROJ-497 Phase 2 Task 2.2: mini_capital_missile retype to SeekerWeaponAbility.

The user decided (Decision 2) to retype `mini_capital_missile` from
`BeamWeaponAbility` to `SeekerWeaponAbility` to align name + type +
ability-payload key with game-design intent (it is a "mini" variant of
the seeker missile `capital_missile`).

Per the Codex mid-project-review caveat captured in
`Projects/active_projects/PROJ-497/phase_2_checklist.md::Task 2.2`, the live
allowance service (`ModifierService.is_modifier_allowed`) keys on
`component.abilities` payload keys, NOT on the `type` field, so the retype
must edit BOTH:
  - the top-level `type` field, AND
  - the ability-payload key (`abilities.BeamWeaponAbility` ->
    `abilities.SeekerWeaponAbility` with a seeker-shaped payload).

Cascade verified against `data/modifiers.json` (live-rule, no
`deny_abilities` enforcement):
  - `seeker_endurance` / `seeker_damage` / `seeker_armored` / `seeker_stealth`
    gain `mini_capital_missile` (1 -> 2 each).
  - `range_mount` loses `mini_capital_missile` (6 -> 5) because seekers are
    not in its allow list (`ProjectileWeaponAbility` + `BeamWeaponAbility`
    only).
  - `precision_mount` loses `mini_capital_missile` (5 -> 4) because it is
    `BeamWeaponAbility`-only (accuracy_add stat is beam-only per
    `game/simulation/components/abilities/weapons.py:275-279`).
  - `turret_mount`, `facing`, `rapid_fire` keep `mini_capital_missile`
    because all three include `SeekerWeaponAbility` in their allow lists.
"""

from __future__ import annotations

import json
import os
from typing import Any

import pytest


def _load_components_by_id() -> dict[str, Any]:
    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "..", "..", "data", "components.json")
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    by_id: dict[str, Any] = {}
    for comp in data.get("components", []):
        by_id[comp["id"]] = comp
    return by_id


def _load_modifiers_by_id() -> dict[str, Any]:
    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "..", "..", "data", "modifiers.json")
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    by_id: dict[str, Any] = {}
    for mod in data.get("modifiers", []):
        by_id[mod["id"]] = mod
    return by_id


COMPONENTS_BY_ID = _load_components_by_id()
MODIFIERS_BY_ID = _load_modifiers_by_id()


def _is_allowed_static(mod_id: str, comp_id: str) -> bool:
    """Mirror `ModifierService.is_modifier_allowed` rules against raw JSON.

    Only `allow_types`, `deny_types`, `allow_abilities` are enforced (see
    `game/simulation/services/modifier_service.py:79-106`). `deny_abilities`
    is declared by some rows (e.g., `hardened_mount`) but NOT enforced by
    the live service; this helper matches the live behavior.
    """
    mod = MODIFIERS_BY_ID[mod_id]
    comp = COMPONENTS_BY_ID[comp_id]
    restrictions = mod.get("restrictions") or {}
    allow_types = restrictions.get("allow_types") or []
    deny_types = restrictions.get("deny_types") or []
    allow_abilities = restrictions.get("allow_abilities") or []

    ctype = comp.get("type", "")
    abilities = set((comp.get("abilities") or {}).keys())

    if allow_types and ctype not in allow_types:
        return False
    if deny_types and ctype in deny_types:
        return False
    if allow_abilities and not any(a in abilities for a in allow_abilities):
        return False
    return True


class TestMiniCapitalMissileType:
    """The top-level `type` must mirror `capital_missile`'s SeekerWeaponAbility."""

    def test_type_is_seeker_weapon_ability(self) -> None:
        comp = COMPONENTS_BY_ID["mini_capital_missile"]
        assert comp.get("type") == "SeekerWeaponAbility", (
            "PROJ-497 Decision 2: mini_capital_missile must be typed as "
            "SeekerWeaponAbility to align with its parent variant."
        )


class TestMiniCapitalMissileAbilityPayload:
    """The ability-payload key must be SeekerWeaponAbility, not BeamWeaponAbility."""

    def test_ability_payload_uses_seeker_key(self) -> None:
        comp = COMPONENTS_BY_ID["mini_capital_missile"]
        abilities = comp.get("abilities") or {}
        assert "SeekerWeaponAbility" in abilities, (
            "PROJ-497 Decision 2: the ability-payload key must be "
            "SeekerWeaponAbility so ModifierService.is_modifier_allowed "
            "matches seeker_* modifiers. A type-only edit is a no-op."
        )
        assert "BeamWeaponAbility" not in abilities, (
            "PROJ-497 Decision 2: the old BeamWeaponAbility payload key "
            "must be removed to avoid double-matching modifier allow lists."
        )

    def test_seeker_payload_has_required_fields(self) -> None:
        """The seeker payload must include the fields SeekerWeaponAbility consumes.

        Required by `game/simulation/components/abilities/weapons.py:343-368`:
            damage, reload, firing_arc, projectile_speed, endurance,
            turn_rate, to_hit_defense.
        """
        comp = COMPONENTS_BY_ID["mini_capital_missile"]
        payload = (comp.get("abilities") or {}).get("SeekerWeaponAbility")
        assert isinstance(payload, dict), "SeekerWeaponAbility payload must be a dict"
        for key in (
            "damage",
            "reload",
            "firing_arc",
            "projectile_speed",
            "endurance",
            "turn_rate",
            "to_hit_defense",
        ):
            assert key in payload, (
                f"PROJ-497 Decision 2: SeekerWeaponAbility payload missing "
                f"required field '{key}' (used by SeekerWeaponAbility.__init__)"
            )


class TestMiniCapitalMissileModifierCascade:
    """Verify the static allow-cascade after the retype matches the design call.

    See decisions.md row "Decision 2 cascade" for the expected matrix.
    """

    @pytest.mark.parametrize("mod_id", [
        "seeker_endurance",
        "seeker_damage",
        "seeker_armored",
        "seeker_stealth",
    ])
    def test_seeker_modifiers_now_allow_mini_capital_missile(self, mod_id: str) -> None:
        assert _is_allowed_static(mod_id, "mini_capital_missile"), (
            f"PROJ-497 Decision 2 cascade: {mod_id} must allow "
            f"mini_capital_missile after the retype."
        )

    @pytest.mark.parametrize("mod_id", ["range_mount", "precision_mount"])
    def test_beam_only_modifiers_no_longer_allow_mini_capital_missile(
        self, mod_id: str
    ) -> None:
        assert not _is_allowed_static(mod_id, "mini_capital_missile"), (
            f"PROJ-497 Decision 2 cascade: {mod_id} (beam-only) must NOT "
            f"allow mini_capital_missile after the retype to SeekerWeaponAbility."
        )

    @pytest.mark.parametrize("mod_id", ["turret_mount", "facing", "rapid_fire"])
    def test_seeker_inclusive_modifiers_still_allow_mini_capital_missile(
        self, mod_id: str
    ) -> None:
        assert _is_allowed_static(mod_id, "mini_capital_missile"), (
            f"PROJ-497 Decision 2 cascade: {mod_id} (Beam+Seeker allow list) "
            f"must still allow mini_capital_missile after the retype."
        )


class TestMiniCapitalMissileEffectiveRange:
    """Phase 4 Task 4.1 — Codex audit F1 remediation.

    The retype dropped the explicit `range: 200` from the old BeamWeaponAbility
    payload. `SeekerWeaponAbility.__init__` (`game/simulation/components/abilities/weapons.py:369-373`)
    defaults `range` to `int(projectile_speed * endurance * 0.8)` when no
    explicit range is given. With `projectile_speed=6000` and the original
    `endurance=3.0`, that defaulted to 14400 — a 72x range jump the user did
    not approve.

    User decision (2026-05-23, verbatim): "reduce the endurance of the mini,
    so that it comes in at close to a 200 range."

    Choice: `endurance = 0.05` -> range = int(6000 * 0.05 * 0.8) = 240. Clean
    round value, "close to 200" per user's direction. Alternative
    `endurance = 0.04` -> range = 192 (exact) was considered; 0.05 was picked
    for the rounder lifetime number and a slight buffer over 200.

    Side-effect (intentional): `endurance` also controls projectile lifetime
    in seeker physics (`game/simulation/combat/families/seeker.py:69-70`),
    so a low endurance also means the missile dies quickly — consistent with
    "short-range mini" semantics. The mini missile is a Fighter-mounted
    seeker; a long-burn 14400-range projectile is inconsistent with that
    role.
    """

    EXPECTED_ENDURANCE = 0.05
    EXPECTED_RANGE = 240  # int(6000 * 0.05 * 0.8)

    def test_endurance_payload_value(self) -> None:
        """The raw payload endurance must be the chosen post-audit value."""
        comp = COMPONENTS_BY_ID["mini_capital_missile"]
        payload = (comp.get("abilities") or {}).get("SeekerWeaponAbility") or {}
        assert payload.get("endurance") == pytest.approx(self.EXPECTED_ENDURANCE), (
            f"PROJ-497 Phase 4 Task 4.1: mini_capital_missile "
            f"SeekerWeaponAbility.endurance must be {self.EXPECTED_ENDURANCE} "
            f"(yielding range {self.EXPECTED_RANGE}); user wanted range "
            f"close to 200."
        )

    def test_effective_range_matches_decision(self, session_registries) -> None:
        """Instantiated SeekerWeaponAbility must compute range ~= 240.

        Uses live (session) registries because mini_capital_missile is not
        in tests/fixtures/test_components.json; stable_component_registries
        only overrides railgun/laser_cannon/thruster.
        """
        from game.simulation.components.component import create_component

        comp = create_component("mini_capital_missile", registries=session_registries)
        comp.recalculate_stats()
        seeker = comp.get_ability("SeekerWeaponAbility")
        assert seeker is not None, (
            "mini_capital_missile must expose a SeekerWeaponAbility instance "
            "after creation (see Decision 2 retype)."
        )
        # SeekerWeaponAbility.__init__ stores int(speed * endurance * 0.8),
        # but `recalculate()` rebinds range as base_range * range_mult (float).
        # Accept either int or float forms via pytest.approx.
        assert seeker.range == pytest.approx(self.EXPECTED_RANGE), (
            f"PROJ-497 Phase 4 Task 4.1: SeekerWeaponAbility.range computed "
            f"as {seeker.range}, expected {self.EXPECTED_RANGE} "
            f"(int(projectile_speed=6000 * endurance="
            f"{self.EXPECTED_ENDURANCE} * 0.8)). The retype originally "
            f"defaulted to 14400 — Codex audit F1."
        )


class TestMiniCapitalMissileResourceConsumptionPreserved:
    """Defensive: the ammo binding from PROJ-449/QA-Obs-4 must not regress."""

    def test_still_consumes_ammo_per_activation(self) -> None:
        comp = COMPONENTS_BY_ID["mini_capital_missile"]
        rc = (comp.get("abilities") or {}).get("ResourceConsumption", [])
        if isinstance(rc, dict):
            rc = [rc]
        activation = [e for e in rc if e.get("trigger") == "activation"]
        assert len(activation) == 1
        assert activation[0].get("resource") == "ammo"
        # Half of parent capital_missile's 5.0 per shot (per existing
        # test_mini_capital_missile_consumes_ammo_half_of_parent).
        assert activation[0].get("amount") == pytest.approx(2.5)
