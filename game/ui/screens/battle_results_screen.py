"""
Battle Results Screen

Full-screen IScene showing post-battle statistics: ship HP bars,
weapon accuracy, team summaries, and navigation buttons.
"""
import pygame
import logging
from typing import Optional

from game.ui.fonts import get_font
from game.ui.colors import (
    BG_BATTLE, WHITE, TEAM_1_TEXT, TEAM_2_TEXT,
    TEAM_1_BANNER_BG, TEAM_2_BANNER_BG,
    HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, HP_DESTROYED,
    BTN_VICTORY_BG, BTN_VICTORY_BORDER, HUD_TEXT,
    TEXT_ITEM,
)
from game.ui.screens.battle_results_data import BattleResults, ShipResult

logger = logging.getLogger(__name__)

# Layout constants
HEADER_HEIGHT = 160
FOOTER_HEIGHT = 80
COLUMN_GAP = 20
SHIP_CARD_HEIGHT = 90
SHIP_CARD_PADDING = 8
SCROLL_SPEED = 30


def _hp_color(percent: float):
    """Get HP bar color based on percentage."""
    if percent <= 0:
        return HP_DESTROYED
    elif percent < 20:
        return HP_CRITICAL
    elif percent < 50:
        return HP_DAMAGED
    return HP_HEALTHY


class BattleResultsScreen:
    """Full-screen battle results display (IScene protocol).

    Shows ship-by-ship statistics in a two-column layout with
    team summaries and weapon accuracy tables.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        results: BattleResults,
        scene_callback=None,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.results = results
        self.scene_callback = scene_callback

        # Scroll state per column
        self._scroll_offset_0 = 0
        self._scroll_offset_1 = 0

        # Button rect (computed in draw)
        self._return_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Fonts
        self._title_font = get_font(48)
        self._subtitle_font = get_font(28)
        self._header_font = get_font(22)
        self._body_font = get_font(18)
        self._small_font = get_font(14)

    def handle_event(self, event):
        """Handle input events (IScene protocol)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self._return_btn_rect.collidepoint(event.pos):
                    self._trigger_return()
            elif event.button == 4:  # Scroll up
                self._handle_scroll(-SCROLL_SPEED, event.pos[0])
            elif event.button == 5:  # Scroll down
                self._handle_scroll(SCROLL_SPEED, event.pos[0])
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_scroll(-event.y * SCROLL_SPEED, pygame.mouse.get_pos()[0])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                self._trigger_return()

    def _handle_scroll(self, delta: int, mouse_x: int):
        """Scroll the column under the mouse cursor."""
        mid = self.screen_width // 2
        if mouse_x < mid:
            self._scroll_offset_0 = max(0, self._scroll_offset_0 + delta)
        else:
            self._scroll_offset_1 = max(0, self._scroll_offset_1 + delta)

    def _trigger_return(self):
        if self.scene_callback:
            if self.results.is_test_mode:
                self.scene_callback("return_to_test_lab")
            else:
                self.scene_callback("return_to_setup")

    def update(self, dt: float):
        """Update (IScene protocol). No animations needed."""
        pass

    def handle_resize(self, width, height):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height

    def draw(self, screen: pygame.Surface):
        """Draw the results screen (IScene protocol)."""
        screen.fill(BG_BATTLE)
        w, h = self.screen_width, self.screen_height

        # === Header ===
        self._draw_header(screen, w)

        # === Two-column body ===
        body_top = HEADER_HEIGHT
        body_bottom = h - FOOTER_HEIGHT
        body_h = body_bottom - body_top
        col_w = (w - COLUMN_GAP * 3) // 2

        # Team 0 column (left)
        team0_ships = [s for s in self.results.ships if s.team_id == 0]
        team0_summary = self.results.teams[0] if len(self.results.teams) > 0 else None
        self._draw_team_column(
            screen, COLUMN_GAP, body_top, col_w, body_h,
            team0_ships, team0_summary, 0, self._scroll_offset_0
        )

        # Team 1 column (right)
        team1_ships = [s for s in self.results.ships if s.team_id == 1]
        team1_summary = self.results.teams[1] if len(self.results.teams) > 1 else None
        self._draw_team_column(
            screen, COLUMN_GAP * 2 + col_w, body_top, col_w, body_h,
            team1_ships, team1_summary, 1, self._scroll_offset_1
        )

        # === Footer ===
        self._draw_footer(screen, w, h)

    def _draw_header(self, screen: pygame.Surface, w: int):
        """Draw title and winner text."""
        # Title
        title_surf = self._title_font.render("BATTLE RESULTS", True, WHITE)
        title_rect = title_surf.get_rect(centerx=w // 2, y=20)
        screen.blit(title_surf, title_rect)

        # Winner + duration
        r = self.results
        if r.winner == 0:
            winner_text = "Team 1 Victory"
            winner_color = TEAM_1_TEXT
        elif r.winner == 1:
            winner_text = "Team 2 Victory"
            winner_color = TEAM_2_TEXT
        else:
            winner_text = "Draw"
            winner_color = TEXT_ITEM

        mins = int(r.duration_seconds) // 60
        secs = int(r.duration_seconds) % 60
        duration_text = f"{mins}m {secs:02d}s ({r.tick_count:,} ticks)"

        info_text = f"{winner_text}  \u00b7  Duration: {duration_text}"
        info_surf = self._subtitle_font.render(info_text, True, winner_color)
        info_rect = info_surf.get_rect(centerx=w // 2, y=80)
        screen.blit(info_surf, info_rect)

    def _draw_team_column(
        self, screen, x, y, w, h,
        ships, summary, team_id, scroll_offset
    ):
        """Draw one team's column with summary and ship cards."""
        team_color = TEAM_1_TEXT if team_id == 0 else TEAM_2_TEXT
        team_bg = TEAM_1_BANNER_BG if team_id == 0 else TEAM_2_BANNER_BG

        # Team header
        header_rect = pygame.Rect(x, y, w, 40)
        pygame.draw.rect(screen, team_bg, header_rect)
        pygame.draw.rect(screen, team_color, header_rect, 1)

        team_label = f"TEAM {team_id + 1}"
        if summary:
            team_label += f"  ({summary.ships_alive}/{summary.total_ships} survived)"
        header_surf = self._header_font.render(team_label, True, team_color)
        screen.blit(header_surf, (x + 10, y + 8))

        # Clip area for ship cards
        cards_y = y + 45
        cards_h = h - 45
        clip_rect = pygame.Rect(x, cards_y, w, cards_h)

        # Create subsurface for clipping
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        # Draw ship cards
        card_y = cards_y - scroll_offset
        for ship in ships:
            if card_y + SHIP_CARD_HEIGHT > cards_y and card_y < cards_y + cards_h:
                self._draw_ship_card(screen, x + 5, card_y, w - 10, ship)
            card_y += SHIP_CARD_HEIGHT + SHIP_CARD_PADDING

        screen.set_clip(old_clip)

    def _draw_ship_card(self, screen, x, y, w, ship: ShipResult):
        """Draw a single ship's result card."""
        # Background
        bg_color = (30, 35, 50) if ship.is_alive else (25, 20, 20)
        pygame.draw.rect(screen, bg_color, (x, y, w, SHIP_CARD_HEIGHT), border_radius=4)
        pygame.draw.rect(screen, (60, 60, 80), (x, y, w, SHIP_CARD_HEIGHT), 1, border_radius=4)

        # Ship name + status
        if not ship.is_alive:
            status = "DESTROYED"
            status_color = HP_DESTROYED
        elif ship.is_derelict:
            status = "DERELICT"
            status_color = HP_DAMAGED
        else:
            status = "ALIVE"
            status_color = HP_HEALTHY

        name_surf = self._body_font.render(ship.name, True, WHITE)
        screen.blit(name_surf, (x + 8, y + 5))

        status_surf = self._small_font.render(status, True, status_color)
        screen.blit(status_surf, (x + w - status_surf.get_width() - 8, y + 8))

        # HP bar
        bar_x = x + 8
        bar_y = y + 28
        bar_w = min(200, w // 2 - 20)
        bar_h = 14
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * ship.hp_percent / 100)
        if fill_w > 0:
            pygame.draw.rect(screen, _hp_color(ship.hp_percent), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (80, 80, 100), (bar_x, bar_y, bar_w, bar_h), 1)

        hp_text = f"HP: {ship.hp_percent:.0f}%"
        hp_surf = self._small_font.render(hp_text, True, HUD_TEXT)
        screen.blit(hp_surf, (bar_x + bar_w + 5, bar_y))

        # Weapon accuracy (compact table)
        weapon_x = x + 8
        weapon_y = y + 48
        for i, wp in enumerate(ship.weapons[:3]):  # Show up to 3 weapons
            acc_text = f"{wp.accuracy * 100:.0f}%" if wp.shots_fired > 0 else "--"
            line = f"{wp.name[:20]:20s}  {wp.shots_hit}/{wp.shots_fired}  {acc_text}"
            line_surf = self._small_font.render(line, True, HUD_TEXT)
            screen.blit(line_surf, (weapon_x, weapon_y + i * 14))

    def _draw_footer(self, screen, w, h):
        """Draw the return button."""
        btn_text = "Return to Combat Lab" if self.results.is_test_mode else "Return to Battle Setup"
        btn_w = 320
        btn_h = 45
        btn_x = (w - btn_w) // 2
        btn_y = h - FOOTER_HEIGHT + 15

        self._return_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, BTN_VICTORY_BG, self._return_btn_rect, border_radius=6)
        pygame.draw.rect(screen, BTN_VICTORY_BORDER, self._return_btn_rect, 2, border_radius=6)

        btn_surf = self._header_font.render(btn_text, True, WHITE)
        btn_rect = btn_surf.get_rect(center=self._return_btn_rect.center)
        screen.blit(btn_surf, btn_rect)
