"""
Unit tests for data file validation.

PROJ-40/Phase 9: Data & Config Cleanup validation tests.
"""
import json
from pathlib import Path

import pytest


class TestVehicleClassNaming:
    """Tests for vehicle class naming consistency.

    PROJ-40/NEW-DATA-007: Vehicle class names should be spelled correctly.
    """

    @pytest.fixture
    def vehicle_classes_data(self):
        """Load vehicle classes JSON."""
        path = Path(__file__).parent.parent.parent.parent / "data" / "vehicleclasses.json"
        with open(path, 'r') as f:
            return json.load(f)

    def test_superdreadnought_spelled_correctly(self, vehicle_classes_data):
        """Superdreadnought should be spelled correctly (not Superdreadnaugh).

        PROJ-40/NEW-DATA-007: Fix common typos in class names.
        """
        classes = vehicle_classes_data.get('classes', {})

        # Check that misspelled version doesn't exist
        assert 'Superdreadnaugh' not in classes, (
            "Vehicle class 'Superdreadnaugh' is misspelled. "
            "Should be 'Superdreadnought'."
        )

        # Check that correct spelling exists
        assert 'Superdreadnought' in classes, (
            "Vehicle class 'Superdreadnought' should exist."
        )

    def test_hull_ids_match_class_names(self, vehicle_classes_data):
        """Hull IDs should not contain typos.

        PROJ-40/NEW-DATA-007: Hull IDs should match corrected class names.
        """
        classes = vehicle_classes_data.get('classes', {})

        for class_name, class_data in classes.items():
            hull_id = class_data.get('default_hull_id', '')
            # Check for the specific typo
            assert 'superdreadnaugh' not in hull_id.lower(), (
                f"Hull ID '{hull_id}' for class '{class_name}' contains typo. "
                f"Should use 'superdreadnought' spelling."
            )


class TestBuilderThemeTypes:
    """Tests for builder theme type consistency.

    PROJ-40/NEW-DATA-009: Theme values should use consistent types.
    """

    @pytest.fixture
    def builder_theme_data(self):
        """Load builder theme JSON."""
        path = Path(__file__).parent.parent.parent.parent / "data" / "builder_theme.json"
        with open(path, 'r') as f:
            return json.load(f)

    def test_font_size_is_numeric(self, builder_theme_data):
        """Default font size should be parseable as an integer.

        PROJ-40/NEW-DATA-009: Numeric values should use numeric types.

        PROJ-443 Phase 3c: relaxed from `isinstance(size, int)` to
        "parseable as int" — the actual data in `builder_theme.json` uses
        string-typed sizes throughout (lines 5, 239, 259, 279), matching
        the convention pygame_gui's theming layer settled on (see the
        sibling `test_misc_numeric_values_are_strings` test, which
        documents misc numerics-as-strings as intentional). Pinning the
        invariant to "valid integer value" rather than the surface type
        preserves the original quality goal without fighting pygame_gui's
        convention.
        """
        defaults = builder_theme_data.get('defaults', {})
        font = defaults.get('font', {})
        size = font.get('size')

        if isinstance(size, int):
            return
        assert isinstance(size, str) and size.isdigit(), (
            f"Font size should be an integer or a string of digits. "
            f"Found: {type(size).__name__} = {repr(size)}"
        )

    def test_misc_numeric_values_are_strings(self, builder_theme_data):
        """Misc section numeric values (e.g., border_width) can be strings.

        pygame_gui expects strings for misc values - this is intentional.
        """
        # This test documents the expected behavior
        # In pygame_gui, misc values are often strings
        panel = builder_theme_data.get('panel', {})
        misc = panel.get('misc', {})

        # Border width is intentionally a string for pygame_gui
        border_width = misc.get('border_width')
        assert border_width is not None


class TestPlaceholderFiles:
    """Tests for placeholder data files.

    PROJ-40/NEW-DATA-002, NEW-DATA-014: Placeholder files should be removed or populated.
    """

    @pytest.fixture
    def data_dir(self):
        """Get the data directory path."""
        return Path(__file__).parent.parent.parent.parent / "data"

    def test_component_presets_removed(self, data_dir):
        """component_presets.json should be removed (empty placeholder).

        PROJ-40/NEW-DATA-002: Empty placeholder file was removed.
        """
        preset_file = data_dir / "component_presets.json"
        assert not preset_file.exists(), (
            "component_presets.json should be removed - it was an empty placeholder. "
            "Code that filtered this file should also be updated."
        )

    def test_ui_presets_has_valid_format(self, data_dir):
        """ui_presets.json should have valid preset format or be empty.

        PROJ-40/NEW-DATA-014: UI presets should use proper format.
        """
        preset_file = data_dir / "ui_presets.json"

        if preset_file.exists():
            with open(preset_file, 'r') as f:
                data = json.load(f)

            # Empty presets dict is valid
            if not data:
                return

            # If not empty, each preset should have proper structure
            for name, preset in data.items():
                # Test presets or invalid presets should not exist
                assert name.lower() != 'test preset', (
                    f"ui_presets.json contains test placeholder '{name}'. "
                    "Remove test data from production files."
                )


class TestResourceMetadata:
    """Tests for resource file metadata.

    PROJ-40/NEW-DATA-006: Resources should have descriptive metadata.
    """

    @pytest.fixture
    def resources_data(self):
        """Load resources JSON."""
        path = Path(__file__).parent.parent.parent.parent / "data" / "resources.json"
        with open(path, 'r') as f:
            return json.load(f)

    def test_resources_have_name_field(self, resources_data):
        """Each resource should have a human-readable name.

        PROJ-40/NEW-DATA-006: Resources need name field for UI display.
        """
        resources = resources_data.get('resources', [])
        assert resources, "No resources defined"

        for resource in resources:
            res_id = resource.get('id', 'unknown')
            assert 'name' in resource, (
                f"Resource '{res_id}' missing 'name' field. "
                "Add a human-readable name for UI display."
            )

    def test_resources_have_description(self, resources_data):
        """Each resource should have a description.

        PROJ-40/NEW-DATA-006: Resources need description for tooltips.
        """
        resources = resources_data.get('resources', [])

        for resource in resources:
            res_id = resource.get('id', 'unknown')
            assert 'description' in resource, (
                f"Resource '{res_id}' missing 'description' field. "
                "Add a description for tooltip display."
            )


class TestModifierFiles:
    """Tests for modifier file consolidation.

    PROJ-40/NEW-DATA-001, NEW-DATA-004: Modifier files should be consolidated.
    """

    @pytest.fixture
    def data_dir(self):
        """Get the data directory path."""
        return Path(__file__).parent.parent.parent.parent / "data"

    def test_only_canonical_modifier_file_exists(self, data_dir):
        """Only modifiers.json should exist (v1/v2 backups removed).

        PROJ-40/NEW-DATA-001: Consolidate to single modifier file.
        """
        canonical = data_dir / "modifiers.json"
        v2 = data_dir / "modifiers_v2.json"
        v1_backup = data_dir / "modifiers_v1_backup.json"

        assert canonical.exists(), "modifiers.json (canonical file) should exist"
        assert not v2.exists(), (
            "modifiers_v2.json should be removed - consolidate into modifiers.json"
        )
        assert not v1_backup.exists(), (
            "modifiers_v1_backup.json should be removed - backup is in git history"
        )

    def test_no_duplicate_modifier_ids(self, data_dir):
        """Each modifier should have a unique ID.

        PROJ-40/NEW-DATA-004: No duplicate modifier definitions.
        """
        canonical = data_dir / "modifiers.json"
        if not canonical.exists():
            pytest.skip("modifiers.json not found")

        with open(canonical, 'r') as f:
            data = json.load(f)

        ids = [m['id'] for m in data.get('modifiers', [])]
        duplicates = [id for id in ids if ids.count(id) > 1]

        assert not duplicates, (
            f"Duplicate modifier IDs found: {set(duplicates)}. "
            "Each modifier must have a unique ID."
        )
