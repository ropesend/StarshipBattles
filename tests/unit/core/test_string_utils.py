"""Tests for game.core.string_utils module."""
import pytest

from game.core.string_utils import display_name, slugify


class TestDisplayName:
    """Tests for display_name() utility."""

    def test_underscore_to_space_and_title(self):
        assert display_name("heavy_laser") == "Heavy Laser"

    def test_single_word(self):
        assert display_name("shields") == "Shields"

    def test_already_titled(self):
        assert display_name("Heavy Laser") == "Heavy Laser"

    def test_empty_string(self):
        assert display_name("") == ""

    def test_multiple_underscores(self):
        assert display_name("max_shield_hp") == "Max Shield Hp"

    def test_all_caps(self):
        assert display_name("ECM") == "Ecm"

    def test_mixed_case_underscores(self):
        assert display_name("planet_type_DESERT") == "Planet Type Desert"


class TestSlugify:
    """Tests for slugify() utility."""

    def test_basic_slugify(self):
        assert slugify("Heavy Laser") == "heavy_laser"

    def test_strips_whitespace(self):
        assert slugify("  Heavy Laser  ") == "heavy_laser"

    def test_lowercases(self):
        assert slugify("HELLO") == "hello"

    def test_replaces_spaces_with_underscores(self):
        assert slugify("a b c") == "a_b_c"

    def test_removes_non_alphanumeric(self):
        assert slugify("Hello, World!") == "hello_world"

    def test_collapses_multiple_underscores(self):
        assert slugify("hello   world") == "hello_world"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_already_slug(self):
        assert slugify("heavy_laser") == "heavy_laser"
