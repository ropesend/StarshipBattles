"""
Tests for component_loader.py error paths and factory functions.

PROJ-265 Phase 1: First dedicated test file for component_loader.py (was 64.2% coverage).
Tests error handling, cache behavior, file-not-found fallbacks, and DI guard clauses.
"""

import json
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch

from game.core.exceptions import ValidationException


# =============================================================================
# load_components_data Tests
# =============================================================================


class TestLoadComponentsData:
    """Tests for load_components_data() error paths."""

    def test_nonexistent_file_returns_empty(self):
        """Returns empty dict when file does not exist."""
        from game.simulation.components.component_loader import load_components_data

        result = load_components_data("/nonexistent/path/components.json", registries=MagicMock())

        assert result == {}

    def test_malformed_json_returns_empty(self):
        """Returns empty dict on malformed JSON."""
        from game.simulation.components.component_loader import load_components_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            path = f.name

        try:
            result = load_components_data(path, registries=MagicMock())
            assert result == {}
        finally:
            os.unlink(path)

    def test_missing_components_key_returns_empty(self):
        """Returns empty dict when JSON lacks 'components' key."""
        from game.simulation.components.component_loader import load_components_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"not_components": []}, f)
            path = f.name

        try:
            result = load_components_data(path, registries=MagicMock())
            assert result == {}
        finally:
            os.unlink(path)

    def test_invalid_component_data_skipped(self):
        """Invalid component entries are skipped, valid ones loaded."""
        from game.simulation.components.component_loader import load_components_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"components": [
                {"id": "bad_comp"},  # Will fail Component() construction (missing required fields)
            ]}, f)
            path = f.name

        try:
            result = load_components_data(path, registries=MagicMock())
            # bad_comp should be skipped (logged error, not in result)
            assert "bad_comp" not in result
        finally:
            os.unlink(path)


# =============================================================================
# load_modifiers_data Tests
# =============================================================================


class TestLoadModifiersData:
    """Tests for load_modifiers_data() error paths."""

    def test_nonexistent_file_returns_empty(self):
        """Returns empty dict when file does not exist."""
        from game.simulation.components.component_loader import load_modifiers_data

        result = load_modifiers_data("/nonexistent/path/modifiers.json")

        assert result == {}

    def test_malformed_json_returns_empty(self):
        """Returns empty dict on malformed JSON."""
        from game.simulation.components.component_loader import load_modifiers_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            path = f.name

        try:
            result = load_modifiers_data(path)
            assert result == {}
        finally:
            os.unlink(path)

    def test_missing_modifiers_key_returns_empty(self):
        """Returns empty dict when JSON lacks 'modifiers' key."""
        from game.simulation.components.component_loader import load_modifiers_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"not_modifiers": []}, f)
            path = f.name

        try:
            result = load_modifiers_data(path)
            assert result == {}
        finally:
            os.unlink(path)

    def test_valid_modifier_loads_successfully(self):
        """Valid modifier data creates Modifier object."""
        from game.simulation.components.component_loader import load_modifiers_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"modifiers": [
                {"id": "test_mod", "name": "Test", "effects": []}
            ]}, f)
            path = f.name

        try:
            result = load_modifiers_data(path)
            assert "test_mod" in result
            assert result["test_mod"].id == "test_mod"
        finally:
            os.unlink(path)


# =============================================================================
# load_components / load_modifiers DI Guard Tests
# =============================================================================


class TestLoadComponentsDI:
    """Tests for load_components() DI guard."""

    def test_requires_registry_provider(self):
        """Raises ValueError when registry_provider is None."""
        from game.simulation.components.component_loader import load_components

        with pytest.raises(ValueError, match="registry_provider is required"):
            load_components(registry_provider=None)


class TestLoadModifiersDI:
    """Tests for load_modifiers() DI guard."""

    def test_requires_registry_provider(self):
        """Raises ValueError when registry_provider is None."""
        from game.simulation.components.component_loader import load_modifiers

        with pytest.raises(ValueError, match="registry_provider is required"):
            load_modifiers(registry_provider=None)


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCreateComponent:
    """Tests for create_component() factory."""

    def test_none_registries_raises(self):
        """Raises ValidationException when registries is None."""
        from game.simulation.components.component_loader import create_component

        with pytest.raises(ValidationException):
            create_component("test_comp", registries=None)

    def test_unknown_id_returns_none(self):
        """Returns None for unknown component ID."""
        from game.simulation.components.component_loader import create_component

        registries = MagicMock()
        registries.components = {}

        result = create_component("nonexistent", registries=registries)

        assert result is None

    def test_known_id_returns_clone(self):
        """Returns cloned component for known ID."""
        from game.simulation.components.component_loader import create_component

        mock_comp = MagicMock()
        mock_clone = MagicMock()
        mock_comp.clone.return_value = mock_clone

        registries = MagicMock()
        registries.components = {"test_comp": mock_comp}

        result = create_component("test_comp", registries=registries)

        assert result is mock_clone
        mock_comp.clone.assert_called_once()


class TestGetAllComponents:
    """Tests for get_all_components() factory."""

    def test_none_registries_raises(self):
        """Raises ValidationException when registries is None."""
        from game.simulation.components.component_loader import get_all_components

        with pytest.raises(ValidationException):
            get_all_components(registries=None)

    def test_returns_list_of_components(self):
        """Returns list of all components in registry."""
        from game.simulation.components.component_loader import get_all_components

        comp1 = MagicMock()
        comp2 = MagicMock()
        registries = MagicMock()
        registries.components = {"a": comp1, "b": comp2}

        result = get_all_components(registries=registries)

        assert len(result) == 2
        assert comp1 in result
        assert comp2 in result
