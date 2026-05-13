"""Tests for PerPlayerUiState (issue #28).

The container partitions per-window UI view-state (column visibility,
sort selection, expanded tab indices, scroll positions) by empire id so
hot-seat players do not inherit each other's view choices.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def state():
    from game.ui.screens.per_player_ui_state import PerPlayerUiState
    return PerPlayerUiState()


class TestSaveLoad:
    def test_load_returns_none_for_unknown_empire(self, state):
        assert state.load(empire_id=0, slot="planet_list") is None

    def test_save_then_load_round_trips(self, state):
        snapshot = {"columns": [{"id": "name", "visible": True}]}
        state.save(empire_id=0, slot="planet_list", snapshot=snapshot)
        assert state.load(empire_id=0, slot="planet_list") == snapshot

    def test_load_returns_none_when_slot_missing(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={"a": 1})
        assert state.load(empire_id=0, slot="star_list") is None

    def test_load_returns_none_when_empire_present_but_slot_missing(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={"a": 1})
        assert state.load(empire_id=0, slot="empire_panel") is None

    def test_save_overwrites_prior_snapshot(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={"v": 1})
        state.save(empire_id=0, slot="planet_list", snapshot={"v": 2})
        assert state.load(empire_id=0, slot="planet_list") == {"v": 2}


class TestKeyIsolation:
    def test_empires_do_not_share_slots(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={"v": 0})
        state.save(empire_id=1, slot="planet_list", snapshot={"v": 1})
        assert state.load(empire_id=0, slot="planet_list") == {"v": 0}
        assert state.load(empire_id=1, slot="planet_list") == {"v": 1}

    def test_slots_within_one_empire_do_not_share(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={"v": "p"})
        state.save(empire_id=0, slot="star_list", snapshot={"v": "s"})
        assert state.load(empire_id=0, slot="planet_list") == {"v": "p"}
        assert state.load(empire_id=0, slot="star_list") == {"v": "s"}


class TestHas:
    def test_has_false_when_empty(self, state):
        assert state.has(empire_id=0, slot="planet_list") is False

    def test_has_true_after_save(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={})
        assert state.has(empire_id=0, slot="planet_list") is True


class TestDiscard:
    def test_discard_unknown_empire_is_noop(self, state):
        state.discard(empire_id=999)  # no raise

    def test_discard_removes_all_slots_for_empire(self, state):
        state.save(empire_id=0, slot="planet_list", snapshot={"a": 1})
        state.save(empire_id=0, slot="star_list", snapshot={"b": 2})
        state.save(empire_id=1, slot="planet_list", snapshot={"c": 3})

        state.discard(empire_id=0)

        assert state.load(empire_id=0, slot="planet_list") is None
        assert state.load(empire_id=0, slot="star_list") is None
        assert state.load(empire_id=1, slot="planet_list") == {"c": 3}
