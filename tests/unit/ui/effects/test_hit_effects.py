"""Characterization tests for hit_effects (PROJ-340).

Pins observed behavior of the visual hit-effect helpers at
``game/ui/effects/hit_effects.py``: HitEffect dataclass properties,
``update_effects``, ``draw_effects``, the four ``_draw_*`` dispatch
branches' early-return guards, and ``create_hit_effect``.

Camera is mocked; ``screen`` is a real ``pygame.Surface`` so blits do
not require a display.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.effects.hit_effects import (
    HitEffect,
    HitEffectType,
    create_hit_effect,
    draw_effects,
    update_effects,
)


def _camera(*, zoom: float = 1.0, screen_pos: tuple = (50, 50)):
    """Build a Mock camera with world_to_screen + zoom."""
    cam = MagicMock()
    cam.zoom = zoom
    cam.world_to_screen.return_value = screen_pos
    return cam


def _screen(size: tuple = (200, 200)) -> pygame.Surface:
    """Real SRCALPHA surface — no display needed."""
    return pygame.Surface(size, pygame.SRCALPHA)


# ----------------------------------------------------------------------------
# HitEffect dataclass: progress / is_alive
# ----------------------------------------------------------------------------


class TestHitEffectProperties:
    def test_progress_clamps_at_one_when_elapsed_exceeds_duration(self):
        e = HitEffect(
            effect_type=HitEffectType.ARMOR_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=10.0,
            duration=0.5, elapsed=10.0,
        )
        assert e.progress == 1.0

    def test_progress_returns_one_when_duration_is_zero(self):
        e = HitEffect(
            effect_type=HitEffectType.ARMOR_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=10.0,
            duration=0.0, elapsed=0.0,
        )
        # Production short-circuits to 1.0 when duration <= 0.
        assert e.progress == 1.0

    def test_is_alive_flips_false_when_elapsed_meets_duration(self):
        e = HitEffect(
            effect_type=HitEffectType.ARMOR_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=10.0,
            duration=0.5, elapsed=0.4,
        )
        assert e.is_alive is True
        e.elapsed = 0.5
        assert e.is_alive is False


# ----------------------------------------------------------------------------
# update_effects: advance + drop expired
# ----------------------------------------------------------------------------


class TestUpdateEffects:
    def test_update_effects_drops_expired_and_advances_remaining(self):
        live = HitEffect(
            effect_type=HitEffectType.ARMOR_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=10.0,
            duration=1.0, elapsed=0.0,
        )
        about_to_expire = HitEffect(
            effect_type=HitEffectType.ARMOR_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=10.0,
            duration=0.05, elapsed=0.0,
        )

        survivors = update_effects([live, about_to_expire], dt=0.1)

        # ``about_to_expire`` is expired (0.0 + 0.1 >= 0.05); ``live`` advances.
        assert survivors == [live]
        assert live.elapsed == pytest.approx(0.1)


# ----------------------------------------------------------------------------
# draw_effects + early-return guards in the _draw_* helpers
# ----------------------------------------------------------------------------


class TestDrawEffects:
    def test_draw_effects_skips_when_alpha_is_zero(self):
        """alpha = int(255 * (1.0 - t)) <= 0 when t >= 1.0 -> _draw_* branch
        skipped via the ``continue`` at hit_effects.py:108-109. Pin two
        observable consequences: world_to_screen IS called (it precedes
        the alpha check) AND the screen surface is unchanged (no _draw_*
        helper ran, so no inner surface was blitted).

        PROJ-346 strengthening: was a "does not raise" test that only
        verified ``cam.world_to_screen.called``. Now also pin screen-pixel
        invariance, so a regression that drops the alpha-skip continue
        (and runs the helper anyway) fails this test.
        """
        e = HitEffect(
            effect_type=HitEffectType.ARMOR_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=10.0,
            duration=1.0, elapsed=1.0,  # progress -> 1.0, alpha -> 0
        )
        cam = _camera()
        screen = _screen()
        before = bytes(screen.get_buffer())

        draw_effects([e], screen, cam)

        # world_to_screen IS called (it precedes the alpha check).
        assert cam.world_to_screen.called
        # The _draw_* branch was skipped, so the screen is bit-identical.
        after = bytes(screen.get_buffer())
        assert before == after, (
            "alpha<=0 branch must skip the _draw_* helper; screen pixels "
            "should be unchanged"
        )

    def test_draw_shield_early_returns_when_size_is_below_threshold(self):
        """_draw_shield_hit: ``size = int(base_r * 3.5) + 4``; if size < 4
        return. Pin the early-return branch by choosing inputs such that
        size == 1 (i.e. base_r * 3.5 < 0). The screen surface MUST be
        unchanged because the inner SRCALPHA Surface and blit are skipped.

        PROJ-346 fix: previous inputs (ship_radius=0, zoom=0) produced
        ``int(0*3.5)+4 = 4``, so the guard ``4 < 4`` was False and the
        branch never fired — the test passed for the wrong reason. Use
        ship_radius=-1.0, zoom=1.0 -> base_r=-1.0, int(-3.5)=-3, size=1
        -> guard fires.
        """
        e = HitEffect(
            effect_type=HitEffectType.SHIELD_HIT,
            world_x=0.0, world_y=0.0,
            ship_radius=-1.0,  # negative -> base_r = -1, size = 1 < 4
            duration=1.0, elapsed=0.1,
        )
        cam = _camera(zoom=1.0)

        screen = _screen()
        before = bytes(screen.get_buffer())
        draw_effects([e], screen, cam)
        after = bytes(screen.get_buffer())

        # Early return -> no inner Surface allocated, no blit -> screen
        # bit-identical.
        assert before == after, (
            "size<4 early-return branch in _draw_shield_hit must leave "
            "the screen surface unchanged"
        )

    def test_draw_armor_or_component_early_returns_when_radius_below_one(self):
        """_draw_armor_hit / _draw_component_destroyed:
            r = int(max_r * t); if r < 1: return
        With ship_radius=0 -> max_r=0 -> r=0 -> early return.

        PROJ-346 strengthening: was a "no exception" test. Now also pin
        screen-pixel invariance so a regression that removes the r<1
        guard (and tries to draw a 0-radius circle) fails here rather
        than only at runtime.
        """
        for et in (HitEffectType.ARMOR_HIT,
                   HitEffectType.COMPONENT_DESTROYED):
            e = HitEffect(
                effect_type=et,
                world_x=0.0, world_y=0.0,
                ship_radius=0.0,
                duration=1.0, elapsed=0.5,
            )
            screen = _screen()
            before = bytes(screen.get_buffer())
            draw_effects([e], screen, _camera())
            after = bytes(screen.get_buffer())
            assert before == after, (
                f"r<1 early-return branch in _draw helper for {et!r} must "
                "leave the screen surface unchanged"
            )


# ----------------------------------------------------------------------------
# Ship-destroyed flash window
# ----------------------------------------------------------------------------


class TestShipDestroyedFlash:
    def test_ship_destroyed_flash_active_only_during_first_third_of_duration(
        self,
    ):
        """Production: flash branch fires only when ``t < 0.3``
        (hit_effects.py:222). Pin this boundary by spying on
        ``pygame.draw.circle`` and counting calls inside vs. outside
        the flash window.

        At t=0.1 (inside) the function draws TWO circles: the bright
        flash + the expanding ring. At t=0.5 (outside) it draws ONE
        circle: just the ring. The delta is the observable signature
        of the t<0.3 branch.

        PROJ-346 strengthening: previously a "neither call raises"
        test. Now pin the call-count delta, which actually fails if
        the t<0.3 guard regresses.
        """
        from game.ui.effects import hit_effects as he_module
        from game.ui.effects.hit_effects import _draw_ship_destroyed
        from unittest.mock import patch

        screen = _screen()
        e = HitEffect(
            effect_type=HitEffectType.SHIP_DESTROYED,
            world_x=0.0, world_y=0.0,
            ship_radius=20.0,
            duration=1.0, elapsed=0.1,
        )

        with patch.object(he_module.pygame.draw, "circle") as mock_circle:
            _draw_ship_destroyed(screen, (50, 50), e, t=0.1, alpha=200, zoom=1.0)
            inside_calls = mock_circle.call_count

        with patch.object(he_module.pygame.draw, "circle") as mock_circle:
            _draw_ship_destroyed(screen, (50, 50), e, t=0.5, alpha=120, zoom=1.0)
            outside_calls = mock_circle.call_count

        # Inside flash window draws BOTH the flash circle and the ring.
        # Outside, only the ring is drawn. The flash branch contributes
        # exactly one extra circle.
        assert inside_calls == 2, (
            f"Inside flash window (t=0.1) expected 2 circle draws "
            f"(flash + ring); got {inside_calls}"
        )
        assert outside_calls == 1, (
            f"Outside flash window (t=0.5) expected 1 circle draw "
            f"(ring only); got {outside_calls}"
        )


# ----------------------------------------------------------------------------
# create_hit_effect
# ----------------------------------------------------------------------------


class TestCreateHitEffect:
    def test_create_hit_effect_snapshots_position_and_radius_from_ship(self):
        ship = MagicMock()
        ship.position.x = 12.5
        ship.position.y = -7.0
        ship.radius = 4.0

        e = create_hit_effect(HitEffectType.ARMOR_HIT, ship)

        assert e.effect_type is HitEffectType.ARMOR_HIT
        assert e.world_x == 12.5
        assert e.world_y == -7.0
        assert e.ship_radius == 4.0
        # duration comes from the type's _EFFECT_CONFIG entry.
        assert e.duration == pytest.approx(0.15)
        assert e.elapsed == 0.0
