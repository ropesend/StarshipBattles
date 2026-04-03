"""
Visual hit effects for battle rendering.

Timer-based geometric effects that render at ship positions when
combat events occur. Each effect fades over its duration using
per-pixel alpha surfaces.

Effect types:
- Shield hit: 2-3 concentric expanding cyan circles
- Armor hit: Expanding orange circle + radiating lines
- Component destroyed: Larger version of armor hit
- Ship destroyed: White flash + expanding orange ring
"""
import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple

import pygame


class HitEffectType(Enum):
    """Types of visual hit effects."""
    SHIELD_HIT = auto()
    ARMOR_HIT = auto()
    COMPONENT_DESTROYED = auto()
    SHIP_DESTROYED = auto()


# Effect configuration
_EFFECT_CONFIG = {
    HitEffectType.SHIELD_HIT: {
        'duration': 0.20,
        'color': (0, 255, 255),
        'radius_scale': 1.6,
    },
    HitEffectType.ARMOR_HIT: {
        'duration': 0.15,
        'color': (255, 160, 0),
        'radius_scale': 0.5,
    },
    HitEffectType.COMPONENT_DESTROYED: {
        'duration': 0.25,
        'color': (255, 120, 0),
        'radius_scale': 0.8,
    },
    HitEffectType.SHIP_DESTROYED: {
        'duration': 0.40,
        'color': (255, 100, 0),
        'radius_scale': 2.5,
    },
}

MAX_ACTIVE_EFFECTS = 40


@dataclass(slots=True)
class HitEffect:
    """A timer-based visual effect at a world position."""
    effect_type: HitEffectType
    world_x: float
    world_y: float
    ship_radius: float
    duration: float
    elapsed: float = 0.0

    @property
    def progress(self) -> float:
        """0.0 at start, 1.0 at end."""
        return min(self.elapsed / self.duration, 1.0) if self.duration > 0 else 1.0

    @property
    def is_alive(self) -> bool:
        return self.elapsed < self.duration

    def update(self, dt: float) -> None:
        self.elapsed += dt


def create_hit_effect(effect_type: HitEffectType, ship) -> HitEffect:
    """Create a HitEffect from a ship's current position and radius."""
    config = _EFFECT_CONFIG[effect_type]
    return HitEffect(
        effect_type=effect_type,
        world_x=ship.position.x,
        world_y=ship.position.y,
        ship_radius=ship.radius,
        duration=config['duration'],
    )


def update_effects(effects: List[HitEffect], dt: float) -> List[HitEffect]:
    """Update all effects and remove expired ones."""
    for effect in effects:
        effect.update(dt)
    return [e for e in effects if e.is_alive]


def draw_effects(effects: List[HitEffect], screen: pygame.Surface, camera) -> None:
    """Draw all active hit effects."""
    for effect in effects:
        screen_pos = camera.world_to_screen(
            pygame.math.Vector2(effect.world_x, effect.world_y)
        )
        t = effect.progress
        alpha = int(255 * (1.0 - t))

        if alpha <= 0:
            continue

        if effect.effect_type == HitEffectType.SHIELD_HIT:
            _draw_shield_hit(screen, screen_pos, effect, t, alpha, camera.zoom)
        elif effect.effect_type == HitEffectType.ARMOR_HIT:
            _draw_armor_hit(screen, screen_pos, effect, t, alpha, camera.zoom)
        elif effect.effect_type == HitEffectType.COMPONENT_DESTROYED:
            _draw_component_destroyed(screen, screen_pos, effect, t, alpha, camera.zoom)
        elif effect.effect_type == HitEffectType.SHIP_DESTROYED:
            _draw_ship_destroyed(screen, screen_pos, effect, t, alpha, camera.zoom)


def _draw_shield_hit(
    screen: pygame.Surface, pos: Tuple, effect: HitEffect,
    t: float, alpha: int, zoom: float
) -> None:
    """2-3 expanding concentric circle outlines, cyan."""
    base_r = effect.ship_radius * zoom
    size = int(base_r * 3.5) + 4
    if size < 4:
        return

    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    center = (size, size)

    for i, scale in enumerate([1.0, 1.3, 1.6]):
        r = int(base_r * scale * (0.8 + 0.4 * t))
        if r < 1:
            continue
        ring_alpha = max(0, alpha - i * 40)
        color = (0, 255, 255, ring_alpha)
        width = max(1, int(2 * (1.0 - t)))
        pygame.draw.circle(surf, color, center, r, width)

    screen.blit(surf, (int(pos[0]) - size, int(pos[1]) - size))


def _draw_armor_hit(
    screen: pygame.Surface, pos: Tuple, effect: HitEffect,
    t: float, alpha: int, zoom: float
) -> None:
    """Expanding circle + 6 radiating lines, orange."""
    config = _EFFECT_CONFIG[HitEffectType.ARMOR_HIT]
    max_r = effect.ship_radius * config['radius_scale'] * zoom
    r = int(max_r * t)
    if r < 1:
        return

    size = int(max_r) + 4
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    center = (size, size)

    color = (255, 160, 0, alpha)
    pygame.draw.circle(surf, color, center, r, max(1, int(2 * (1 - t))))

    # 6 radiating lines
    line_color = (255, 200, 50, alpha)
    line_len = r * 1.3
    for angle_deg in range(0, 360, 60):
        angle = math.radians(angle_deg)
        end = (int(center[0] + math.cos(angle) * line_len),
               int(center[1] + math.sin(angle) * line_len))
        pygame.draw.line(surf, line_color, center, end, 1)

    screen.blit(surf, (int(pos[0]) - size, int(pos[1]) - size))


def _draw_component_destroyed(
    screen: pygame.Surface, pos: Tuple, effect: HitEffect,
    t: float, alpha: int, zoom: float
) -> None:
    """Larger expanding circle + 8 radiating lines, deep orange."""
    config = _EFFECT_CONFIG[HitEffectType.COMPONENT_DESTROYED]
    max_r = effect.ship_radius * config['radius_scale'] * zoom
    r = int(max_r * t)
    if r < 1:
        return

    size = int(max_r) + 4
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    center = (size, size)

    color = (255, 120, 0, alpha)
    pygame.draw.circle(surf, color, center, r, max(1, int(3 * (1 - t))))

    # 8 radiating lines
    line_color = (255, 200, 50, alpha)
    line_len = r * 1.4
    for angle_deg in range(0, 360, 45):
        angle = math.radians(angle_deg)
        end = (int(center[0] + math.cos(angle) * line_len),
               int(center[1] + math.sin(angle) * line_len))
        pygame.draw.line(surf, line_color, center, end, 2)

    screen.blit(surf, (int(pos[0]) - size, int(pos[1]) - size))


def _draw_ship_destroyed(
    screen: pygame.Surface, pos: Tuple, effect: HitEffect,
    t: float, alpha: int, zoom: float
) -> None:
    """White flash (first 30%) + expanding orange ring."""
    config = _EFFECT_CONFIG[HitEffectType.SHIP_DESTROYED]
    max_r = effect.ship_radius * config['radius_scale'] * zoom
    r = int(max_r * t)
    if r < 1:
        return

    size = int(max_r) + 4
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    center = (size, size)

    # Flash (bright in first 30% of duration)
    if t < 0.3:
        flash_alpha = int(255 * (1.0 - t / 0.3))
        flash_r = int(effect.ship_radius * zoom * 1.5)
        if flash_r > 0:
            pygame.draw.circle(surf, (255, 255, 200, flash_alpha), center, flash_r)

    # Expanding ring
    ring_color = (255, 100, 0, alpha)
    width = max(1, int(3 * (1 - t)))
    pygame.draw.circle(surf, ring_color, center, r, width)

    screen.blit(surf, (int(pos[0]) - size, int(pos[1]) - size))
