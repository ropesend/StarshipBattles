"""Tests for Tools/captioning/validate_captions.py (PROJ-299 Phase 1)."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Make the validator importable.
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from validate_captions import (  # noqa: E402
    Status,
    SidecarReport,
    validate_caption_dict,
    validate_sidecar_path,
    load_schema,
)


SCHEMAS_DIR = THIS_DIR / "schemas"


def _good_flag_caption() -> dict:
    return {
        "schema_version": 1,
        "geometry": "Vertical bicolour with central emblem.",
        "color_palette": "Crimson and gold.",
        "symbolism": "Predatory eagle clutching swords.",
        "cultural_hints": "Imperial society organised around martial nobility.",
        "mood": "aggressive",
        "distinctive_traits": "Sword-shaped wing feathers.",
    }


def _good_portrait_caption() -> dict:
    return {
        "schema_version": 1,
        "anatomy": "Bipedal reptilian, ~2m tall.",
        "coloration": "Teal scales, ochre belly.",
        "attire_and_adornment": "Bronze breastplate, jade ear-cuffs.",
        "posture_and_expression": "Upright, gaze steady, jaw set.",
        "technology_level_hint": "industrial",
        "distinctive_traits": "Four eyes in a vertical column.",
    }


def _good_theme_caption() -> dict:
    return {
        "schema_version": 1,
        "hull_geometry": "Arrowhead silhouette, bilateral symmetry.",
        "materials_and_finish": "Matte charcoal composite, brushed seams.",
        "design_philosophy": "Speed and stealth optimisation.",
        "color_scheme": "Charcoal with scarlet accents.",
        "technology_level_hint": "advanced",
        "distinctive_traits": "Twin knife-thin nacelles, forked bow.",
    }


# ============================================================================
# load_schema
# ============================================================================


class TestLoadSchema:
    def test_loads_flag_schema(self):
        schema = load_schema("flag")
        assert schema["asset_type"] == "flag"
        assert "geometry" in schema["required_fields"]

    def test_loads_portrait_schema(self):
        schema = load_schema("portrait")
        assert schema["asset_type"] == "portrait"

    def test_loads_theme_schema(self):
        schema = load_schema("theme")
        assert schema["asset_type"] == "theme"

    def test_unknown_asset_type_raises(self):
        with pytest.raises(ValueError):
            load_schema("nonexistent")


# ============================================================================
# validate_caption_dict
# ============================================================================


class TestValidateCaptionDict:
    def test_good_flag_caption_validates(self):
        ok, errors = validate_caption_dict(_good_flag_caption(), "flag")
        assert ok
        assert errors == []

    def test_good_portrait_caption_validates(self):
        ok, errors = validate_caption_dict(_good_portrait_caption(), "portrait")
        assert ok

    def test_good_theme_caption_validates(self):
        ok, errors = validate_caption_dict(_good_theme_caption(), "theme")
        assert ok

    def test_missing_required_field_fails(self):
        bad = _good_flag_caption()
        del bad["mood"]
        ok, errors = validate_caption_dict(bad, "flag")
        assert not ok
        assert any("mood" in e for e in errors)

    def test_invalid_enum_value_fails(self):
        bad = _good_flag_caption()
        bad["mood"] = "ridiculous"
        ok, errors = validate_caption_dict(bad, "flag")
        assert not ok
        assert any("mood" in e and "ridiculous" in e for e in errors)

    def test_wrong_schema_version_fails(self):
        bad = _good_flag_caption()
        bad["schema_version"] = 2
        ok, errors = validate_caption_dict(bad, "flag")
        assert not ok
        assert any("schema_version" in e for e in errors)


# ============================================================================
# validate_sidecar_path
# ============================================================================


class TestValidateSidecarPath:
    @pytest.fixture
    def tmp_sidecar(self, tmp_path: Path):
        path = tmp_path / "asset.caption.json"
        return path

    def test_missing_sidecar_returns_missing(self, tmp_sidecar: Path):
        report = validate_sidecar_path(tmp_sidecar, "flag")
        assert report.status == Status.MISSING
        assert report.path == tmp_sidecar

    def test_malformed_sidecar_returns_malformed(self, tmp_sidecar: Path):
        tmp_sidecar.write_text("{not valid json", encoding="utf-8")
        report = validate_sidecar_path(tmp_sidecar, "flag")
        assert report.status == Status.MALFORMED

    def test_invalid_sidecar_returns_invalid(self, tmp_sidecar: Path):
        bad = _good_flag_caption()
        del bad["mood"]
        tmp_sidecar.write_text(json.dumps(bad), encoding="utf-8")
        report = validate_sidecar_path(tmp_sidecar, "flag")
        assert report.status == Status.INVALID
        assert any("mood" in d for d in report.details)

    def test_good_sidecar_returns_ok(self, tmp_sidecar: Path):
        tmp_sidecar.write_text(json.dumps(_good_flag_caption()), encoding="utf-8")
        report = validate_sidecar_path(tmp_sidecar, "flag")
        assert report.status == Status.OK
        assert report.details == []
