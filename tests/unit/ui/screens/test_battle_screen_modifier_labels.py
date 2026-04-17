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
        # PROJ-272 Phase 11: `_mult` keys format as "Nx" (e.g. "1.25x"), not
        # "+1.25" (which would look positive when the value is a nerf < 1.0).
        assert any(
            "T0" in line and "shield_capacity_mult" in line and "1.25x" in line
            for line in labels
        ), f"Missing team 0 booster label; got: {labels}"
        assert any(
            "T1" in line and "damage_mult" in line and "0.80x" in line
            for line in labels
        ), f"Missing team 1 suppressor label; got: {labels}"


class TestPhase11FormatSemantics:
    """PROJ-272 Phase 11: `_mult` / `_add` / other keys format distinctly."""

    def _make_labels(self, bonuses_for_team_0):
        screen = _make_screen()
        aura = MagicMock()
        aura.get_active_bonuses.side_effect = lambda tid: bonuses_for_team_0 if tid == 0 else []
        ship = SimpleNamespace(team_id=0)
        engine = SimpleNamespace(ships=[ship], aura_manager=aura)
        service = MagicMock()
        service.get_engine.return_value = engine
        screen._controller = SimpleNamespace(_service=service)
        return screen.get_active_modifier_labels()

    def test_mult_key_uses_x_suffix_no_sign(self):
        """Suppressor 0.75x should read as '0.75x', not '+0.75' (green/positive)."""
        labels = self._make_labels([
            {'ability': 'damage_mult', 'value': 0.75, 'source': 'Suppressor', 'scope': 'external', 'active': True},
        ])
        assert len(labels) == 1
        assert "0.75x" in labels[0]
        assert "+0.75" not in labels[0]

    def test_add_key_uses_signed_format(self):
        """`_add` keys show explicit sign so users know direction."""
        labels = self._make_labels([
            {'ability': 'shield_bonus_add', 'value': 50.0, 'source': 'Projector', 'scope': 'external', 'active': True},
        ])
        assert "+50.00" in labels[0]

    def test_add_key_negative_signed(self):
        labels = self._make_labels([
            {'ability': 'accuracy_add', 'value': -0.25, 'source': 'Jammer', 'scope': 'external', 'active': True},
        ])
        assert "-0.25" in labels[0]

    def test_non_numeric_value_skipped_not_crash(self):
        """PROJ-272 Phase 11: non-numeric value from a future aura
        should skip the entry with a logger warning, not crash the HUD."""
        labels = self._make_labels([
            {'ability': 'shield_capacity_mult', 'value': "oops", 'source': 'Buggy', 'scope': 'external', 'active': True},
            {'ability': 'damage_mult', 'value': 1.5, 'source': 'OK', 'scope': 'external', 'active': True},
        ])
        # Buggy entry dropped; OK entry present.
        assert len(labels) == 1
        assert "1.50x" in labels[0]
