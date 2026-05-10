"""Focused coverage for the species selector race-resolution helpers."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.ui.screens import species_selector_mixin as selector


class TestGetSelectedRaceId:
    def test_none_dropdown_returns_none(self):
        assert selector.get_selected_race_id(None) is None

    def test_string_selected_option_maps_to_race_id(self):
        dropdown = SimpleNamespace(
            selected_option="Humans (10M)",
            _race_id_map={"Humans (10M)": "human"},
        )

        assert selector.get_selected_race_id(dropdown) == "human"

    def test_tuple_selected_option_uses_first_value(self):
        dropdown = SimpleNamespace(
            selected_option=("Voidari (2M)", "ignored"),
            _race_id_map={"Voidari (2M)": "voidari"},
        )

        assert selector.get_selected_race_id(dropdown) == "voidari"


class TestLoadRaceConfig:
    def test_blank_race_id_returns_none_without_loading_library(self):
        with patch(
            "game.strategy.systems.race_library.RaceLibrary"
        ) as race_library:
            assert selector.load_race_config("") is None

        race_library.assert_not_called()

    def test_returns_race_from_library(self):
        race_config = object()
        race_library = MagicMock()
        race_library.get_race.return_value = race_config

        with patch(
            "game.strategy.systems.race_library.RaceLibrary",
            return_value=race_library,
        ):
            assert selector.load_race_config("human") is race_config

        race_library.get_race.assert_called_once_with("human")

    def test_race_library_exception_returns_none(self):
        with patch(
            "game.strategy.systems.race_library.RaceLibrary",
            side_effect=OSError("bad races folder"),
        ):
            assert selector.load_race_config("broken") is None


class TestRaceConfigResolverMixin:
    def _resolver(self):
        class Resolver(selector.RaceConfigResolverMixin):
            pass

        return Resolver()

    def test_selected_dropdown_race_wins_over_default_and_fallback(self):
        selected_config = object()
        resolver = self._resolver()
        resolver._species_dropdown = SimpleNamespace(
            selected_option="Selected",
            _race_id_map={"Selected": "selected"},
        )
        resolver._default_race_id = "default"
        resolver.race_config = object()

        with patch.object(
            selector,
            "load_race_config",
            return_value=selected_config,
        ) as load_race_config:
            assert resolver._get_active_race_config() is selected_config

        load_race_config.assert_called_once_with("selected")

    def test_default_race_used_when_dropdown_selection_does_not_resolve(self):
        default_config = object()
        resolver = self._resolver()
        resolver._species_dropdown = SimpleNamespace(
            selected_option="Selected",
            _race_id_map={"Selected": "selected"},
        )
        resolver._default_race_id = "default"
        resolver.race_config = object()

        def load_race_config(race_id):
            return {"default": default_config}.get(race_id)

        with patch.object(
            selector,
            "load_race_config",
            side_effect=load_race_config,
        ) as load_race_config_mock:
            assert resolver._get_active_race_config() is default_config

        assert [call.args[0] for call in load_race_config_mock.call_args_list] == [
            "selected",
            "default",
        ]

    def test_existing_race_config_used_when_library_paths_do_not_resolve(self):
        fallback_config = object()
        resolver = self._resolver()
        resolver._species_dropdown = None
        resolver._default_race_id = "default"
        resolver.race_config = fallback_config

        with patch.object(
            selector,
            "load_race_config",
            return_value=None,
        ) as load_race_config:
            assert resolver._get_active_race_config() is fallback_config

        load_race_config.assert_called_once_with("default")
