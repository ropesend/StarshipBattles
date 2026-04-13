"""PROJ-271 Phase 8 Task 8.2: BattleScreen active-modifier HUD labels.

`BattleScreen.get_active_modifier_labels()` pulls active bonuses from
`FleetAuraManager.get_active_bonuses(team_id)` for each team in battle
and formats them for HUD display. Previously the aura manager's
`get_active_bonuses` had zero UI consumers — the effects existed in the
engine but were invisible to users."""
from types import SimpleNamespace
from unittest.mock import MagicMock


def _make_screen():
    """Build a BattleScreen-like stand-in to unit-test the helper.

    We bypass `__init__` via `__new__` because the full constructor
    requires pygame/render state we don't need. The helper only reads
    `self._controller` — a bare instance is enough."""
    from game.ui.screens.battle_screen import BattleScreen
    screen = BattleScreen.__new__(BattleScreen)
    screen._controller = None
    return screen


class TestGetActiveModifierLabels:
    """The helper must return a list of strings describing active
    external modifiers keyed by team_id."""

    def test_returns_empty_when_no_controller(self):
        screen = _make_screen()
        screen._controller = None
        assert screen.get_active_modifier_labels() == []

    def test_returns_empty_when_no_service(self):
        screen = _make_screen()
        screen._controller = SimpleNamespace()  # no service/_service
        assert screen.get_active_modifier_labels() == []

    def test_returns_empty_when_no_engine(self):
        screen = _make_screen()
        service = MagicMock()
        service.get_engine.return_value = None
        screen._controller = SimpleNamespace(_service=service)
        assert screen.get_active_modifier_labels() == []

    def test_returns_empty_when_no_aura_manager(self):
        screen = _make_screen()
        engine = SimpleNamespace(ships=[], aura_manager=None)
        service = MagicMock()
        service.get_engine.return_value = engine
        screen._controller = SimpleNamespace(_service=service)
        assert screen.get_active_modifier_labels() == []

    def test_formats_active_bonuses_for_each_team(self):
        screen = _make_screen()

        # Fake aura manager returning distinct bonuses per team.
        def fake_get_active_bonuses(team_id):
            if team_id == 0:
                return [
                    {'ability': 'shield_capacity_mult', 'value': 1.25, 'source': 'Shield Booster (Planet X)', 'scope': 'external', 'active': True},
                ]
            elif team_id == 1:
                return [
                    {'ability': 'damage_mult', 'value': 0.8, 'source': 'Damage Suppressor (Planet Y)', 'scope': 'external', 'active': True},
                ]
            return []

        aura = MagicMock()
        aura.get_active_bonuses.side_effect = fake_get_active_bonuses

        ship_t0 = SimpleNamespace(team_id=0)
        ship_t1 = SimpleNamespace(team_id=1)
        engine = SimpleNamespace(ships=[ship_t0, ship_t1], aura_manager=aura)

        service = MagicMock()
        service.get_engine.return_value = engine
        screen._controller = SimpleNamespace(_service=service)

        labels = screen.get_active_modifier_labels()
        assert len(labels) == 2
        # Team 0's booster
        assert any(
            "T0" in line and "shield_capacity_mult" in line and "1.25" in line
            for line in labels
        ), f"Missing team 0 booster label; got: {labels}"
        # Team 1's suppressor
        assert any(
            "T1" in line and "damage_mult" in line and "0.80" in line
            for line in labels
        ), f"Missing team 1 suppressor label; got: {labels}"
