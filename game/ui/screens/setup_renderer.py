"""
Battle setup screen rendering functions.

Pure rendering functions for drawing the setup screen UI elements.

"""
import pygame
from game.ui.fonts import get_default_font
from game.ui.colors import (
    TEXT_LIGHT, TEXT_ITEM, WHITE,
    SETUP_TITLE, SETUP_LABEL_SHIPS, SETUP_LABEL_FORMATIONS,
    FORMATION_TEXT, FORMATION_BG, FORMATION_BORDER,
    FORMATION_TEAM_BG, FORMATION_TEAM_BORDER,
    ITEM_BG, ITEM_BORDER,
    TEAM_1_BG, TEAM_1_BORDER, TEAM_2_BG, TEAM_2_BORDER,
    BTN_NEUTRAL_BG, BTN_NEUTRAL_BORDER, BTN_NEUTRAL_TEXT,
    BTN_PRIMARY_BG, BTN_PRIMARY_BORDER, BTN_DISABLED_BG,
    BTN_CLEAR_BG, BTN_CLEAR_BORDER, BTN_CLEAR_TEXT,
    BTN_QUICK_BG, BTN_QUICK_BORDER, BTN_QUICK_TEXT,
    DROPDOWN_BG, DROPDOWN_BUTTON_BG, DROPDOWN_BUTTON_BORDER, DROPDOWN_BUTTON_TEXT,
    HP_CRITICAL,
)


def draw_title(screen, sw):
    """Draw the battle setup title."""
    title_font = get_default_font(64)
    title = title_font.render("BATTLE SETUP", True, SETUP_TITLE)
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
    lbl = label_font.render("Ships (L/R click)", True, SETUP_LABEL_SHIPS)
    screen.blit(lbl, (col_x, 110))

    ships_end_y = 150
    for i, design in enumerate(available_designs):
        y = 150 + i * 40
        ships_end_y = y + 40
        text = item_font.render(f"{design['name']} ({design['ship_class']})", True, TEXT_ITEM)
        pygame.draw.rect(screen, ITEM_BG, (col_x, y, 250, 35))
        pygame.draw.rect(screen, ITEM_BORDER, (col_x, y, 250, 35), 1)
        screen.blit(text, (col_x + 10, y + 8))

    # Formations section
    form_header_y = ships_end_y + 10
    lbl_form = label_font.render("Formations", True, SETUP_LABEL_FORMATIONS)
    screen.blit(lbl_form, (col_x, form_header_y))

    form_start_y = form_header_y + 35
    for i, form in enumerate(available_formations):
        y = form_start_y + i * 40
        text = item_font.render(f"{form['name']}", True, FORMATION_TEXT)
        pygame.draw.rect(screen, FORMATION_BG, (col_x, y, 250, 35))
        pygame.draw.rect(screen, FORMATION_BORDER, (col_x, y, 250, 35), 1)
        screen.blit(text, (col_x + 10, y + 8))

    return ships_end_y


def draw_load_save_buttons(screen, btn_y, label_font):
    """Draw load and save buttons."""
    # Load button
    pygame.draw.rect(screen, BTN_NEUTRAL_BG, (50, btn_y, 120, 50))
    pygame.draw.rect(screen, BTN_NEUTRAL_BORDER, (50, btn_y, 120, 50), 2)
    lid_text = label_font.render("LOAD", True, BTN_NEUTRAL_TEXT)
    screen.blit(lid_text, (50 + 60 - lid_text.get_width() // 2, btn_y + 12))

    # Save button
    pygame.draw.rect(screen, BTN_NEUTRAL_BG, (180, btn_y, 120, 50))
    pygame.draw.rect(screen, BTN_NEUTRAL_BORDER, (180, btn_y, 120, 50), 2)
    sav_text = label_font.render("SAVE", True, BTN_NEUTRAL_TEXT)
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
        strat_name = strategy[:12]

        is_formation = (item['type'] == 'formation')

        # Determine colors based on type and team
        if is_formation:
            bg_color = FORMATION_TEAM_BG
            border_color = FORMATION_TEAM_BORDER
        elif "Team 1" in title_text:
            bg_color = TEAM_1_BG
            border_color = TEAM_1_BORDER
        else:
            bg_color = TEAM_2_BG
            border_color = TEAM_2_BORDER

        # Draw item background
        pygame.draw.rect(screen, bg_color, (col_x, y, 350, 30))
        pygame.draw.rect(screen, border_color, (col_x, y, 350, 30), 1)

        # Draw name
        name_text = item_font.render(name[:25], True, WHITE)
        screen.blit(name_text, (col_x + 5, y + 5))

        # Draw AI strategy dropdown button
        ai_btn_x = col_x + 150
        pygame.draw.rect(screen, DROPDOWN_BUTTON_BG, (ai_btn_x, y + 2, 130, 26))
        pygame.draw.rect(screen, DROPDOWN_BUTTON_BORDER, (ai_btn_x, y + 2, 130, 26), 1)
        ai_text = item_font.render(strat_name + " ▼", True, DROPDOWN_BUTTON_TEXT)
        screen.blit(ai_text, (ai_btn_x + 5, y + 5))

        # Draw remove button
        x_text = item_font.render("[X]", True, HP_CRITICAL)
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
    btn_color = BTN_PRIMARY_BG if has_teams else BTN_DISABLED_BG
    pygame.draw.rect(screen, btn_color, (sw // 2 - 100, btn_y, 200, 50))
    pygame.draw.rect(screen, BTN_PRIMARY_BORDER, (sw // 2 - 100, btn_y, 200, 50), 2)
    btn_text = label_font.render("BEGIN BATTLE", True, WHITE)
    screen.blit(btn_text, (sw // 2 - btn_text.get_width() // 2, btn_y + 12))

    # Return button
    pygame.draw.rect(screen, BTN_NEUTRAL_BG, (sw // 2 + 120, btn_y, 120, 50))
    pygame.draw.rect(screen, BTN_NEUTRAL_BORDER, (sw // 2 + 120, btn_y, 120, 50), 2)
    ret_text = label_font.render("RETURN", True, TEXT_ITEM)
    screen.blit(ret_text, (sw // 2 + 180 - ret_text.get_width() // 2, btn_y + 12))

    # Clear All button
    pygame.draw.rect(screen, BTN_CLEAR_BG, (sw // 2 - 300, btn_y, 120, 50))
    pygame.draw.rect(screen, BTN_CLEAR_BORDER, (sw // 2 - 300, btn_y, 120, 50), 2)
    clr_text = label_font.render("CLEAR ALL", True, BTN_CLEAR_TEXT)
    screen.blit(clr_text, (sw // 2 - 240 - clr_text.get_width() // 2, btn_y + 12))

    # Quick Battle button
    quick_color = BTN_QUICK_BG if has_teams else BTN_DISABLED_BG
    pygame.draw.rect(screen, quick_color, (sw // 2 + 260, btn_y, 140, 50))
    pygame.draw.rect(screen, BTN_QUICK_BORDER, (sw // 2 + 260, btn_y, 140, 50), 2)
    quick_text = label_font.render("QUICK BATTLE", True, BTN_QUICK_TEXT)
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
    pygame.draw.rect(screen, DROPDOWN_BG, (col_x, ship_y, dropdown_w, dropdown_h))
    pygame.draw.rect(screen, BTN_NEUTRAL_BORDER, (col_x, ship_y, dropdown_w, dropdown_h), 1)

    # Options
    for idx, strat_id in enumerate(ai_strategies):
        strat_name = strat_id
        opt_y = ship_y + idx * 22
        text_color = TEXT_LIGHT
        opt_text = item_font.render(strat_name, True, text_color)
        screen.blit(opt_text, (col_x + 5, opt_y + 3))
