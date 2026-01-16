"""
Battle setup screen rendering functions.

Pure rendering functions for drawing the setup screen UI elements.
"""
import pygame
from game.ai.controller import StrategyManager


def draw_title(screen, sw):
    """Draw the battle setup title."""
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("BATTLE SETUP", True, (200, 200, 255))
    screen.blit(title, (sw // 2 - title.get_width() // 2, 30))


def draw_available_ships(screen, col_x, available_designs, available_formations, label_font, item_font):
    """
    Draw the available ships and formations list.

    Args:
        screen: Pygame screen surface
        col_x: X position of the column
        available_designs: List of ship design dicts
        available_formations: List of formation dicts
        label_font: Font for labels
        item_font: Font for items

    Returns:
        Y position where ships section ends (for formation positioning)
    """
    lbl = label_font.render("Ships (L/R click)", True, (150, 150, 200))
    screen.blit(lbl, (col_x, 110))

    ships_end_y = 150
    for i, design in enumerate(available_designs):
        y = 150 + i * 40
        ships_end_y = y + 40
        text = item_font.render(f"{design['name']} ({design['ship_class']})", True, (200, 200, 200))
        pygame.draw.rect(screen, (40, 45, 55), (col_x, y, 250, 35))
        pygame.draw.rect(screen, (80, 80, 100), (col_x, y, 250, 35), 1)
        screen.blit(text, (col_x + 10, y + 8))

    # Formations section
    form_header_y = ships_end_y + 10
    lbl_form = label_font.render("Formations", True, (150, 200, 150))
    screen.blit(lbl_form, (col_x, form_header_y))

    form_start_y = form_header_y + 35
    for i, form in enumerate(available_formations):
        y = form_start_y + i * 40
        text = item_font.render(f"{form['name']}", True, (200, 255, 200))
        pygame.draw.rect(screen, (35, 50, 35), (col_x, y, 250, 35))
        pygame.draw.rect(screen, (80, 120, 80), (col_x, y, 250, 35), 1)
        screen.blit(text, (col_x + 10, y + 8))

    return ships_end_y


def draw_load_save_buttons(screen, btn_y, label_font):
    """Draw load and save buttons."""
    # Load button
    pygame.draw.rect(screen, (60, 60, 80), (50, btn_y, 120, 50))
    pygame.draw.rect(screen, (100, 100, 150), (50, btn_y, 120, 50), 2)
    lid_text = label_font.render("LOAD", True, (200, 200, 255))
    screen.blit(lid_text, (50 + 60 - lid_text.get_width() // 2, btn_y + 12))

    # Save button
    pygame.draw.rect(screen, (60, 60, 80), (180, btn_y, 120, 50))
    pygame.draw.rect(screen, (100, 100, 150), (180, btn_y, 120, 50), 2)
    sav_text = label_font.render("SAVE", True, (200, 200, 255))
    screen.blit(sav_text, (180 + 60 - sav_text.get_width() // 2, btn_y + 12))


def draw_team(screen, display_list, col_x, title_text, color, label_font, item_font):
    """
    Draw a team column with ships and formations.

    Args:
        screen: Pygame screen surface
        display_list: List of display items from get_team_display_groups()
        col_x: X position of the column
        title_text: Team title ("Team 1" or "Team 2")
        color: Title color tuple
        label_font: Font for labels
        item_font: Font for items
    """
    lbl = label_font.render(title_text, True, color)
    screen.blit(lbl, (col_x, 110))

    for i, item in enumerate(display_list):
        y = 150 + i * 35
        name = item['name']
        strategy = item['strategy']
        strat_name = StrategyManager.instance().strategies.get(strategy, {}).get('name', strategy)[:12]

        is_formation = (item['type'] == 'formation')

        # Determine colors based on type and team
        if is_formation:
            bg_color = (30, 60, 50)
            border_color = (100, 200, 150)
        elif "Team 1" in title_text:
            bg_color = (30, 50, 70)
            border_color = (100, 150, 200)
        else:
            bg_color = (70, 30, 30)
            border_color = (200, 100, 100)

        # Draw item background
        pygame.draw.rect(screen, bg_color, (col_x, y, 350, 30))
        pygame.draw.rect(screen, border_color, (col_x, y, 350, 30), 1)

        # Draw name
        name_text = item_font.render(name[:25], True, (255, 255, 255))
        screen.blit(name_text, (col_x + 5, y + 5))

        # Draw AI strategy dropdown button
        ai_btn_x = col_x + 150
        pygame.draw.rect(screen, (40, 60, 90), (ai_btn_x, y + 2, 130, 26))
        pygame.draw.rect(screen, (80, 120, 180), (ai_btn_x, y + 2, 130, 26), 1)
        ai_text = item_font.render(strat_name + " ▼", True, (150, 200, 255))
        screen.blit(ai_text, (ai_btn_x + 5, y + 5))

        # Draw remove button
        x_text = item_font.render("[X]", True, (255, 100, 100))
        screen.blit(x_text, (col_x + 315, y + 5))


def draw_action_buttons(screen, sw, btn_y, has_teams, label_font):
    """
    Draw the main action buttons.

    Args:
        screen: Pygame screen surface
        sw: Screen width
        btn_y: Y position for buttons
        has_teams: Whether both teams have ships
        label_font: Font for button text
    """
    # Begin Battle button
    btn_color = (50, 150, 50) if has_teams else (50, 50, 50)
    pygame.draw.rect(screen, btn_color, (sw // 2 - 100, btn_y, 200, 50))
    pygame.draw.rect(screen, (100, 200, 100), (sw // 2 - 100, btn_y, 200, 50), 2)
    btn_text = label_font.render("BEGIN BATTLE", True, (255, 255, 255))
    screen.blit(btn_text, (sw // 2 - btn_text.get_width() // 2, btn_y + 12))

    # Return button
    pygame.draw.rect(screen, (80, 80, 80), (sw // 2 + 120, btn_y, 120, 50))
    pygame.draw.rect(screen, (150, 150, 150), (sw // 2 + 120, btn_y, 120, 50), 2)
    ret_text = label_font.render("RETURN", True, (200, 200, 200))
    screen.blit(ret_text, (sw // 2 + 180 - ret_text.get_width() // 2, btn_y + 12))

    # Clear All button
    pygame.draw.rect(screen, (120, 50, 50), (sw // 2 - 300, btn_y, 120, 50))
    pygame.draw.rect(screen, (200, 100, 100), (sw // 2 - 300, btn_y, 120, 50), 2)
    clr_text = label_font.render("CLEAR ALL", True, (255, 200, 200))
    screen.blit(clr_text, (sw // 2 - 240 - clr_text.get_width() // 2, btn_y + 12))

    # Quick Battle button
    quick_color = (80, 50, 120) if has_teams else (40, 40, 40)
    pygame.draw.rect(screen, quick_color, (sw // 2 + 260, btn_y, 140, 50))
    pygame.draw.rect(screen, (150, 100, 200), (sw // 2 + 260, btn_y, 140, 50), 2)
    quick_text = label_font.render("QUICK BATTLE", True, (220, 200, 255))
    screen.blit(quick_text, (sw // 2 + 330 - quick_text.get_width() // 2, btn_y + 12))


def draw_ai_dropdown(screen, ai_strategies, team_idx, display_idx, col2_x, col3_x, item_font):
    """
    Draw AI strategy dropdown overlay.

    Args:
        screen: Pygame screen surface
        ai_strategies: List of strategy IDs
        team_idx: Team index (1 or 2)
        display_idx: Index of the display item
        col2_x: X position of team 1 column
        col3_x: X position of team 2 column
        item_font: Font for dropdown items
    """
    col_x = col2_x if team_idx == 1 else col3_x
    ship_y = 150 + display_idx * 35 + 30
    col_x = col_x + 150

    dropdown_w = 180
    dropdown_h = len(ai_strategies) * 22

    # Background
    pygame.draw.rect(screen, (30, 30, 40), (col_x, ship_y, dropdown_w, dropdown_h))
    pygame.draw.rect(screen, (100, 100, 150), (col_x, ship_y, dropdown_w, dropdown_h), 1)

    # Options
    for idx, strat_id in enumerate(ai_strategies):
        strat_name = StrategyManager.instance().strategies.get(strat_id, {}).get('name', strat_id)
        opt_y = ship_y + idx * 22
        text_color = (220, 220, 220)
        opt_text = item_font.render(strat_name, True, text_color)
        screen.blit(opt_text, (col_x + 5, opt_y + 3))
