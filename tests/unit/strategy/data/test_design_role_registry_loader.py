"""Tests for game.strategy.data.design_role_registry — module-level
accessor + layered loading for the gameplay design_role registry (PROJ-278).
"""
from __future__ import annotations

import json

import pytest

from game.core.roles import Role, RoleRegistry
from game.strategy.data.design_role_registry import (
    get_default_design_role_registry,
    reset_default_design_role_registry,
    set_default_design_role_registry,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    """Ensure each test starts with a fresh module state."""
    reset_default_design_role_registry()
    yield
    reset_default_design_role_registry()


class TestDefaultRegistryAccessor:
    """`get_default_design_role_registry()` lazy-constructs a singleton."""

    def test_returns_role_registry_instance(self):
        reg = get_default_design_role_registry()
        assert isinstance(reg, RoleRegistry)

    def test_subsequent_calls_return_same_instance(self):
        reg1 = get_default_design_role_registry()
        reg2 = get_default_design_role_registry()
        assert reg1 is reg2

    def test_default_registry_allows_runtime_add(self):
        reg = get_default_design_role_registry()
        # Should not raise — design_role registry permits player additions
        reg.add_user_role(Role(id="custom", display_name="Custom", description="..."))
        assert "custom" in reg


class TestDefaultRegistryOverride:
    """`set_default_design_role_registry` allows test injection."""

    def test_set_default_overrides_accessor(self):
        custom = RoleRegistry(allow_runtime_add=True)
        custom.add_user_role(Role(id="x", display_name="X", description="x"))

        set_default_design_role_registry(custom)
        assert get_default_design_role_registry() is custom
        assert get_default_design_role_registry().get("x").id == "x"

    def test_reset_clears_override(self):
        custom = RoleRegistry(allow_runtime_add=True)
        set_default_design_role_registry(custom)
        reset_default_design_role_registry()

        # Next call lazy-constructs a fresh registry, NOT the custom one
        fresh = get_default_design_role_registry()
        assert fresh is not custom


class TestProductionDataLoadsCleanly:
    """Smoke test: the actual `data/design_roles.json` file loads without error."""

    def test_default_registry_loads_production_data(self):
        reg = get_default_design_role_registry()
        roles = reg.all()

        assert len(roles) > 0, "Production data file should contain roles"

    def test_known_role_ids_present(self):
        """Spot-check: some known role IDs from the production file."""
        reg = get_default_design_role_registry()
        ids = {r.id for r in reg.all()}

        expected_subset = {
            "general_purpose", "line_combatant", "fleet_escort",
            "interceptor", "carrier", "command_ship", "scout",
            "missile_platform", "raider", "support_ship",
        }
        assert expected_subset.issubset(ids), \
            f"Missing expected roles: {expected_subset - ids}"

    def test_all_roles_have_non_empty_display_name_and_description(self):
        reg = get_default_design_role_registry()
        for role in reg.all():
            assert role.display_name, f"Role {role.id} has empty display_name"
            assert role.description, f"Role {role.id} has empty description"

    def test_general_purpose_allows_all_expected_vehicle_types(self):
        reg = get_default_design_role_registry()
        gp = reg.get("general_purpose")

        for vt in ("Ship", "Fighter", "Satellite", "Planetary Complex", "Drop Pod"):
            assert vt in gp.vehicle_type_filter, \
                f"general_purpose should accept {vt}"

    def test_get_roles_for_vehicle_type_works_with_production_data(self):
        reg = get_default_design_role_registry()
        ship_roles = reg.get_roles_for_vehicle_type("Ship")
        assert len(ship_roles) > 0
        # Result is sorted by display_name
        names = [r.display_name for r in ship_roles]
        assert names == sorted(names)


class TestLayeredLoading:
    """Layered loading: base → mods → user overlay; later overrides earlier."""

    def test_user_overlay_overrides_base(self, tmp_path, monkeypatch):
        """When user_data/design_roles_overlay.json exists, its roles override base."""
        # Build a fake user overlay file
        overlay = tmp_path / "design_roles_overlay.json"
        overlay.write_text(json.dumps({
            "roles": [
                {
                    "id": "general_purpose",
                    "display_name": "General Purpose (USER OVERRIDE)",
                    "description": "Customized by player.",
                    "vehicle_type_filter": ["Ship"],
                },
            ],
        }), encoding="utf-8")

        # Patch the path constant so the loader reads our overlay
        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.USER_DESIGN_ROLES_FILE",
            str(overlay),
        )

        reg = get_default_design_role_registry()
        gp = reg.get("general_purpose")
        assert gp.display_name == "General Purpose (USER OVERRIDE)"

    def test_missing_user_overlay_is_silently_ignored(self, monkeypatch, tmp_path):
        """First-run scenario: overlay file doesn't exist."""
        nonexistent = tmp_path / "does_not_exist.json"
        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.USER_DESIGN_ROLES_FILE",
            str(nonexistent),
        )

        # Should construct cleanly with base roles only
        reg = get_default_design_role_registry()
        assert len(reg.all()) > 0

    def test_mod_overlay_overrides_base(self, tmp_path, monkeypatch):
        """Closure audit gap (PROJ-278): mod-layer loading was previously
        untested. Verify a mod's design_roles.json overrides base roles."""
        # Build a fake mods/ directory with one mod overlay
        mods_dir = tmp_path / "mods"
        mod_dir = mods_dir / "test_mod"
        mod_dir.mkdir(parents=True)
        mod_file = mod_dir / "design_roles.json"
        mod_file.write_text(json.dumps({
            "roles": [
                {
                    "id": "general_purpose",
                    "display_name": "General Purpose (MOD OVERRIDE)",
                    "description": "Mod-level customization.",
                    "vehicle_type_filter": ["Ship"],
                },
            ],
        }), encoding="utf-8")

        # Patch MODS_DIR to our temp dir; ensure user overlay is absent
        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.MODS_DIR",
            str(mods_dir),
        )
        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.USER_DESIGN_ROLES_FILE",
            str(tmp_path / "no_user_overlay.json"),
        )

        reg = get_default_design_role_registry()
        gp = reg.get("general_purpose")
        assert gp.display_name == "General Purpose (MOD OVERRIDE)", (
            "Mod overlay did not override base role"
        )

    def test_user_overlay_overrides_mod_overlay(self, tmp_path, monkeypatch):
        """Precedence: base < mod < user. User overlay wins over mod."""
        mods_dir = tmp_path / "mods"
        mod_dir = mods_dir / "test_mod"
        mod_dir.mkdir(parents=True)
        mod_file = mod_dir / "design_roles.json"
        mod_file.write_text(json.dumps({
            "roles": [
                {
                    "id": "general_purpose",
                    "display_name": "From Mod",
                    "description": "mod",
                },
            ],
        }), encoding="utf-8")

        user_overlay = tmp_path / "user.json"
        user_overlay.write_text(json.dumps({
            "roles": [
                {
                    "id": "general_purpose",
                    "display_name": "From User",
                    "description": "user",
                },
            ],
        }), encoding="utf-8")

        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.MODS_DIR",
            str(mods_dir),
        )
        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.USER_DESIGN_ROLES_FILE",
            str(user_overlay),
        )

        reg = get_default_design_role_registry()
        assert reg.get("general_purpose").display_name == "From User"

    def test_multiple_mods_load_in_sorted_order(self, tmp_path, monkeypatch):
        """Multiple mod overlays load alphabetically; later mod wins on conflict."""
        mods_dir = tmp_path / "mods"
        for mod_name, override_value in [("a_mod", "From A"), ("z_mod", "From Z")]:
            mod_dir = mods_dir / mod_name
            mod_dir.mkdir(parents=True)
            (mod_dir / "design_roles.json").write_text(json.dumps({
                "roles": [{
                    "id": "general_purpose",
                    "display_name": override_value,
                    "description": override_value,
                }],
            }), encoding="utf-8")

        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.MODS_DIR",
            str(mods_dir),
        )
        monkeypatch.setattr(
            "game.strategy.data.design_role_registry.Paths.USER_DESIGN_ROLES_FILE",
            str(tmp_path / "no_user.json"),
        )

        reg = get_default_design_role_registry()
        # Sorted glob → a_mod loads first, z_mod loads second → z_mod wins
        assert reg.get("general_purpose").display_name == "From Z"
