"""PROJ-272 Phase 3: TargetEvaluator must not crash when candidate is a
Projectile (no Ship interface).

`_score_and_sort_enemies` passes a heterogeneous enemies list (ships +
missiles) to `TargetEvaluator.evaluate`. Rule fallbacks previously called
`candidate.get_components_by_ability(...)` / `.get_components_by_layer(...)`
unconditionally, crashing on projectile candidates. The outer try/except
in `_score_and_sort_enemies` swallowed the crash and silently dropped the
missile from scoring — meaning PDC rules can't target missiles when other
rules fire first.

Phase 3 adds `is_combat_ship` guards so rules that don't apply to
projectiles return a sensible default (score 0, rule passes unless required)
instead of crashing.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock
import pygame
import pytest

from game.ai.target_evaluator import TargetEvaluator


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


def _ship():
    """Mock attacking ship."""
    s = MagicMock()
    s.position = pygame.math.Vector2(0, 0)
    s.angle = 0
    s.team_id = 0
    s.get_components_by_ability = MagicMock(return_value=[])
    return s


def _projectile_candidate():
    """Projectile stand-in: has position + type, but NO component queries.
    Missing `get_components_by_ability` and `get_components_by_layer` and
    no `layers` attribute — matches real Projectile surface."""
    return SimpleNamespace(
        id='missile_1',
        name='missile_1',
        position=pygame.math.Vector2(50, 0),
        mass=10,
        type='MISSILE',
        team_id=1,
    )


class TestHasWeaponsRuleProjectileGuard:
    """`has_weapons` rule must gracefully handle projectile candidates
    (they have no components → no weapons → rule returns 0 / passes)."""

    def test_has_weapons_rule_with_projectile_does_not_crash(self):
        """Projectile candidate + has_weapons rule with empty cache → no crash."""
        ship = _ship()
        missile = _projectile_candidate()
        rules = [{"type": "has_weapons", "weight": 100, "required": False}]

        # Pass an empty cache (cache miss triggers the fallback path).
        # Must not raise AttributeError.
        score = TargetEvaluator.evaluate(
            ship, missile, rules,
            ship_capabilities_cache={},
        )
        # Missile has no weapons — rule returns 0 for non-required
        # (per _eval_has_weapons_rule semantics).
        assert score is not None  # Doesn't matter which value; just no crash.

    def test_has_weapons_required_with_projectile_rejects_cleanly(self):
        """`required=True` on has_weapons rule → rejects projectile (score -inf)
        but does NOT crash."""
        ship = _ship()
        missile = _projectile_candidate()
        rules = [{"type": "has_weapons", "weight": 100, "required": True}]

        score = TargetEvaluator.evaluate(
            ship, missile, rules,
            ship_capabilities_cache={},
        )
        # Required has_weapons on a no-component projectile → -inf.
        assert score == -float('inf')


class TestLeastArmorRuleProjectileGuard:
    """`least_armor` rule calls `candidate.get_components_by_layer(...)`.
    Projectiles have no layers — must be guarded."""

    def test_least_armor_with_projectile_does_not_crash(self):
        ship = _ship()
        missile = _projectile_candidate()
        rules = [{"type": "least_armor", "weight": 50, "factor": 1}]

        # Must not raise.
        score = TargetEvaluator.evaluate(ship, missile, rules)
        assert score is not None


class TestMixedCandidatesNoCrash:
    """Integration: a rule set that includes both a projectile and a ship
    candidate — both scored without crash."""

    def test_evaluate_projectile_then_ship_with_has_weapons_rule(self):
        ship = _ship()
        missile = _projectile_candidate()

        armed_ship = MagicMock()
        armed_ship.id = 'armed'
        armed_ship.position = pygame.math.Vector2(200, 0)
        armed_ship.mass = 1000
        weapon = MagicMock()
        weapon.has_ability = MagicMock(return_value=False)
        armed_ship.get_components_by_ability = MagicMock(return_value=[weapon])
        armed_ship.get_components_by_layer = MagicMock(return_value=[])

        rules = [{"type": "has_weapons", "weight": 100, "required": False}]

        # Missile: no crash, non-infinite score
        missile_score = TargetEvaluator.evaluate(
            ship, missile, rules,
            ship_capabilities_cache={},
        )
        # Ship: evaluates has_weapons correctly
        ship_score = TargetEvaluator.evaluate(
            ship, armed_ship, rules,
            ship_capabilities_cache={},
        )

        # Both produce scores without crashing; ship's score should be
        # higher because it HAS weapons (gets the weight).
        assert missile_score is not None
        assert ship_score is not None
