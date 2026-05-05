"""Tests for shared race-config resolution."""

from dataclasses import dataclass

from game.strategy.services.race_resolver import resolve_race_config


@dataclass
class _RaceConfig:
    race_id: str


@dataclass
class _Empire:
    race_config: _RaceConfig | None


class _RaceRegistry:
    def __init__(self, races: dict[str, _RaceConfig]) -> None:
        self._races = races

    def get_race(self, race_id: str) -> _RaceConfig | None:
        return self._races.get(race_id)


def test_resolve_race_config_prefers_registry_hit():
    primary = _RaceConfig("primary")
    resident = _RaceConfig("resident")
    registry = _RaceRegistry({"resident": resident})

    assert resolve_race_config("resident", _Empire(primary), registry) is resident


def test_resolve_race_config_falls_back_to_matching_primary_race():
    primary = _RaceConfig("primary")
    registry = _RaceRegistry({})

    assert resolve_race_config("primary", _Empire(primary), registry) is primary


def test_resolve_race_config_without_registry_uses_matching_primary_race():
    primary = _RaceConfig("primary")

    assert resolve_race_config("primary", _Empire(primary), None) is primary


def test_resolve_race_config_returns_none_for_unknown_non_primary_race():
    primary = _RaceConfig("primary")
    registry = _RaceRegistry({})

    assert resolve_race_config("resident", _Empire(primary), registry) is None


def test_resolve_race_config_returns_none_when_empire_has_no_primary_race():
    registry = _RaceRegistry({})

    assert resolve_race_config("resident", _Empire(None), registry) is None
