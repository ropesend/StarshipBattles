"""Tests for DesignMetadata mass_valid field.

Over-mass designs should have mass_valid=False and be filtered
from build queue listings.
"""
import pytest
from game.strategy.data.design_metadata import DesignMetadata


class TestDesignMetadataMassValid:
    """Test mass_valid field on DesignMetadata."""

    def test_mass_valid_defaults_true(self):
        """mass_valid should default to True for backward compatibility."""
        meta = DesignMetadata(
            design_id="test",
            name="Test Design",
            ship_class="Escort",
            vehicle_type="Ship",
            mass=500,
            combat_power=100,
        )
        assert meta.mass_valid is True

    def test_mass_valid_from_dict_defaults_true(self):
        """from_dict should default mass_valid to True if missing."""
        data = {
            "design_id": "test",
            "name": "Test Design",
        }
        meta = DesignMetadata.from_dict(data)
        assert meta.mass_valid is True

    def test_mass_valid_from_dict_reads_false(self):
        """from_dict should read mass_valid=False when present."""
        data = {
            "design_id": "test",
            "name": "Test Design",
            "mass_valid": False,
        }
        meta = DesignMetadata.from_dict(data)
        assert meta.mass_valid is False

    def test_mass_valid_roundtrip(self):
        """mass_valid should survive to_dict/from_dict roundtrip."""
        meta = DesignMetadata(
            design_id="test",
            name="Test",
            ship_class="Escort",
            vehicle_type="Ship",
            mass=500,
            combat_power=100,
            mass_valid=False,
        )
        data = meta.to_dict()
        restored = DesignMetadata.from_dict(data)
        assert restored.mass_valid is False

    def test_from_design_file_reads_mass_valid(self, tmp_path):
        """from_design_file should read mass_valid from expected_stats."""
        import json
        design_data = {
            "name": "Over Mass Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "expected_stats": {
                "mass": 2000,
                "mass_valid": False,
            },
            "_metadata": {
                "is_obsolete": False,
                "times_built": 0,
            }
        }
        filepath = tmp_path / "test_design.json"
        filepath.write_text(json.dumps(design_data))

        meta = DesignMetadata.from_design_file(str(filepath), "test_design")
        assert meta.mass_valid is False

    def test_from_design_file_defaults_true_when_missing(self, tmp_path):
        """from_design_file should default mass_valid to True if not in expected_stats."""
        import json
        design_data = {
            "name": "Normal Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "expected_stats": {
                "mass": 500,
            },
            "_metadata": {
                "is_obsolete": False,
                "times_built": 0,
            }
        }
        filepath = tmp_path / "normal_design.json"
        filepath.write_text(json.dumps(design_data))

        meta = DesignMetadata.from_design_file(str(filepath), "normal_design")
        assert meta.mass_valid is True
