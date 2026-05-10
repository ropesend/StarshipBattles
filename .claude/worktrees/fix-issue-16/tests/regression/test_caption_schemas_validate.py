"""Regression: shipped caption schemas must be valid JSON and self-consistent.

PROJ-299 Phase 1: ensures the caption schemas in `Tools/captioning/schemas/`
load cleanly and declare the fields the rest of the system expects.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "Tools" / "captioning" / "schemas"

EXPECTED_MOOD_VALUES = {
    "patriotic", "aggressive", "peaceful", "mysterious",
    "unified", "technological", "religious", "naturalistic",
}
EXPECTED_TECH_LEVELS = {
    "primitive", "medieval", "industrial", "advanced", "post-human", "unknown",
}


def _load(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


class TestSchemaFilesExist:
    def test_flag_schema_exists(self):
        assert (SCHEMAS_DIR / "flag.schema.json").exists()

    def test_portrait_schema_exists(self):
        assert (SCHEMAS_DIR / "portrait.schema.json").exists()

    def test_theme_schema_exists(self):
        assert (SCHEMAS_DIR / "theme.schema.json").exists()


class TestSchemaJSONValidity:
    @pytest.mark.parametrize(
        "name", ["flag.schema.json", "portrait.schema.json", "theme.schema.json"]
    )
    def test_schema_is_valid_json(self, name: str):
        _load(name)  # raises if invalid

    @pytest.mark.parametrize(
        "name", ["flag.schema.json", "portrait.schema.json", "theme.schema.json"]
    )
    def test_schema_version_is_1(self, name: str):
        schema = _load(name)
        assert schema.get("schema_version") == 1


class TestFlagSchema:
    def test_has_six_fields(self):
        schema = _load("flag.schema.json")
        # required fields, excluding schema_version
        fields = schema.get("required_fields", [])
        assert set(fields) == {
            "geometry", "color_palette", "symbolism",
            "cultural_hints", "mood", "distinctive_traits",
        }

    def test_mood_enum_values(self):
        schema = _load("flag.schema.json")
        enums = schema.get("enums", {})
        assert set(enums.get("mood", [])) == EXPECTED_MOOD_VALUES


class TestPortraitSchema:
    def test_has_six_fields(self):
        schema = _load("portrait.schema.json")
        fields = schema.get("required_fields", [])
        assert set(fields) == {
            "anatomy", "coloration", "attire_and_adornment",
            "posture_and_expression", "technology_level_hint",
            "distinctive_traits",
        }

    def test_tech_level_enum_values(self):
        schema = _load("portrait.schema.json")
        enums = schema.get("enums", {})
        assert set(enums.get("technology_level_hint", [])) == EXPECTED_TECH_LEVELS


class TestThemeSchema:
    def test_has_six_fields(self):
        schema = _load("theme.schema.json")
        fields = schema.get("required_fields", [])
        assert set(fields) == {
            "hull_geometry", "materials_and_finish", "design_philosophy",
            "color_scheme", "technology_level_hint", "distinctive_traits",
        }

    def test_tech_level_enum_values(self):
        schema = _load("theme.schema.json")
        enums = schema.get("enums", {})
        assert set(enums.get("technology_level_hint", [])) == EXPECTED_TECH_LEVELS
