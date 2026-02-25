### FONT INITIALIZATIONS
game\app.py:76 - self.font_small = pygame.font.SysFont("arial", 12)
game\app.py:77 - self.font_med = pygame.font.SysFont("arial", 20)
game\app.py:78 - self.font_large = pygame.font.SysFont("arial", 32)
game\ui\config.py:36 - # Font sizes (pygame.font.Font None-font sizes)
game\ui\panels\battle_panels.py:103 - font_title = pygame.font.Font(None, UIConfig.FONT_TITLE)
game\ui\panels\battle_panels.py:104 - font_name = pygame.font.Font(None, UIConfig.FONT_NAME)
game\ui\panels\battle_panels.py:105 - font_stat = pygame.font.Font(None, UIConfig.FONT_STAT)
game\ui\panels\battle_panels.py:311 - font_title = pygame.font.Font(None, 28)
game\ui\panels\battle_panels.py:312 - font_name = pygame.font.Font(None, 22)
game\ui\panels\battle_panels.py:313 - font_stat = pygame.font.Font(None, 18)
game\ui\panels\battle_panels.py:518 - win_font = pygame.font.Font(None, 72)
game\ui\panels\battle_panels.py:523 - btn_font = pygame.font.Font(None, 36)
game\ui\panels\battle_panels.py:541 - btn_font = pygame.font.Font(None, 24)
game\ui\panels\design_report_panel.py:249 - font_large = pygame.font.SysFont("arial", int(18 * font_scale), bold=True)
game\ui\panels\design_report_panel.py:250 - font_small = pygame.font.SysFont("arial", int(14 * font_scale))
game\ui\panels\modifier_impact_grid.py:83 - self.font = pygame.font.SysFont("Arial", 15)
game\ui\panels\modifier_impact_grid.py:84 - self.header_font = pygame.font.SysFont("Arial", 14)
game\ui\panels\modifier_impact_grid.py:85 - self.net_font = pygame.font.SysFont("Arial", 15, bold=True)
game\ui\panels\planet_report_panel.py:225 - font = pygame.font.SysFont("arial", 16, bold=True)
game\ui\panels\strategy_widgets.py:56 - font = pygame.font.SysFont("arial", 8)
game\ui\panels\strategy_widgets.py:115 - font = pygame.font.SysFont("arial", 12)
game\ui\panels\strategy_widgets.py:138 - font = pygame.font.SysFont("arial", 8)
game\ui\research\research_renderer.py:75 - def _get_font(self, size: int) -> pygame.font.Font:
game\ui\research\research_renderer.py:84 - self._font_cache[quantized_size] = pygame.font.SysFont("Arial", quantized_size)
game\ui\screens\battle_screen.py:593 - self._hud_font = pygame.font.SysFont("arial", 20)
game\ui\screens\battle_state_viewer.py:80 - self.header_font = pygame.font.SysFont(FONT_MAIN, 24)
game\ui\screens\battle_state_viewer.py:81 - self.button_font = pygame.font.SysFont(FONT_MAIN, 16)
game\ui\screens\battle_state_viewer.py:82 - self.legend_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\battle_ui.py:247 - font = pygame.font.SysFont("Arial", 28, bold=True)
game\ui\screens\battle_ui.py:253 - complete_font = pygame.font.SysFont("Arial", 56, bold=True)
game\ui\screens\battle_ui.py:290 - result_font = pygame.font.SysFont("Arial", 48, bold=True)
game\ui\screens\design_image_helper.py:98 - font = pygame.font.SysFont("arial", int(size * 0.5), bold=True)
game\ui\screens\keybindings_scene.py:410 - font = pygame.font.SysFont("arial", 28)
game\ui\screens\setup_renderer.py:15 - title_font = pygame.font.Font(None, 64)
game\ui\screens\setup_screen.py:371 - label_font = pygame.font.Font(None, 36)
game\ui\screens\setup_screen.py:372 - item_font = pygame.font.Font(None, 28)
game\ui\screens\strategy_renderer.py:62 - self._font_cache[key] = pygame.font.SysFont("arial", size, bold=bold)
game\ui\screens\strategy_ui.py:316 - font = pygame.font.SysFont("arial", 20)
game\ui\screens\workshop_screen.py:511 - font = pygame.font.SysFont("Arial", 18)
game\ui\screens\builder\detail_panel.py:262 - font = pygame.font.SysFont("Arial", 14)
game\ui\screens\builder\schematic_view.py:99 - font = pygame.font.SysFont("Arial", 10)
game\ui\screens\builder\schematic_view.py:175 - font = pygame.font.SysFont("Arial", 10)
game\ui\screens\builder\weapons_renderer.py:106 - self.font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_NORMAL)
game\ui\screens\builder\weapons_renderer.py:107 - self.small_font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_SMALL)
game\ui\screens\builder\weapons_renderer.py:108 - self.target_font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_NORMAL)
game\ui\screens\formation\renderer.py:260 - font = pygame.font.SysFont("Arial", 14, bold=True)
game\ui\screens\galaxy_test\system_mode.py:530 - font = pygame.font.SysFont("arial", 12)
game\ui\screens\galaxy_test\system_mode.py:561 - font = pygame.font.SysFont("arial", 10)
game\ui\screens\test_lab\component_dropdown.py:35 - self.font = pygame.font.SysFont(FONT_MAIN, 16)
game\ui\screens\test_lab\dialogs.py:41 - self.title_font = pygame.font.SysFont(FONT_MAIN, 24)
game\ui\screens\test_lab\dialogs.py:42 - self.body_font = pygame.font.SysFont('Courier New', 14)  # Monospace for JSON
game\ui\screens\test_lab\dialogs.py:150 - self.title_font = pygame.font.SysFont(FONT_MAIN, 24)
game\ui\screens\test_lab\dialogs.py:151 - self.body_font = pygame.font.SysFont(FONT_MAIN, 16)
game\ui\screens\test_lab\dialogs.py:152 - self.small_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\test_lab\json_viewer.py:44 - self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\test_lab\json_viewer.py:45 - self.title_font = pygame.font.SysFont(FONT_MAIN, 18)
game\ui\screens\test_lab\renderer.py:42 - self.title_font = pygame.font.SysFont(FONT_MAIN, 48)
game\ui\screens\test_lab\renderer.py:43 - self.header_font = pygame.font.SysFont(FONT_MAIN, 24)
game\ui\screens\test_lab\renderer.py:44 - self.body_font = pygame.font.SysFont(FONT_MAIN, 18)
game\ui\screens\test_lab\renderer.py:45 - self.small_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\test_lab\results_panel.py:38 - self.title_font = pygame.font.SysFont(FONT_MAIN, 20)
game\ui\screens\test_lab\results_panel.py:39 - self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\test_lab\results_panel.py:40 - self.small_font = pygame.font.SysFont(FONT_MAIN, 12)
game\ui\screens\test_lab\screen.py:380 - header_font = pygame.font.SysFont("consolas", 24)
game\ui\screens\test_lab\screen.py:381 - body_font = pygame.font.SysFont("consolas", 18)
game\ui\screens\test_lab\screen.py:382 - small_font = pygame.font.SysFont("consolas", 14)
game\ui\screens\test_lab\ship_panels.py:74 - self.tab_font = pygame.font.SysFont(FONT_MAIN, 12)
game\ui\screens\test_lab\ship_panels.py:75 - self.header_font = pygame.font.SysFont(FONT_MAIN, 16)
game\ui\screens\test_lab\test_run_card.py:50 - self.title_font = pygame.font.SysFont(FONT_MAIN, 16)
game\ui\screens\test_lab\test_run_card.py:51 - self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\test_lab\test_run_card.py:52 - self.small_font = pygame.font.SysFont(FONT_MAIN, 12)
game\ui\screens\test_lab\test_run_details.py:33 - self.title_font = pygame.font.SysFont(FONT_MAIN, 20)
game\ui\screens\test_lab\test_run_details.py:34 - self.header_font = pygame.font.SysFont(FONT_MAIN, 16)
game\ui\screens\test_lab\test_run_details.py:35 - self.body_font = pygame.font.SysFont(FONT_MAIN, 14)
game\ui\screens\test_lab\test_run_details.py:36 - self.small_font = pygame.font.SysFont(FONT_MAIN, 12)
game\ui\widgets\scrollable_json_panel.py:67 - self.title_font = pygame.font.SysFont(FONT_MAIN, 18)
game\ui\widgets\scrollable_json_panel.py:68 - self.content_font = pygame.font.SysFont(FONT_MONO, 13)
scripts\visual_test_galaxy.py:228 - s_font = pygame.font.SysFont("arial", 10)
scripts\visual_test_galaxy.py:261 - p_font = pygame.font.SysFont("arial", 10)
scripts\visual_test_galaxy.py:301 - font = pygame.font.SysFont("arial", 12)
scripts\visual_test_galaxy.py:310 - font = pygame.font.SysFont("arial", 20)

Total Fonts: 81

### COLOR DEFINITIONS
scan_dupes.py:33 - # Colors: looking for variables assigned to RGB tuples, or pygame.Color
scan_dupes.py:34 - # Examples: WHITE = (255, 255, 255), color=(255,0,0)
scan_dupes.py:37 - 'pygame.Color' in line:
game\app.py:53 - BG_COLOR = (10, 10, 20)
game\strategy\data\stars.py:277 - color = (255, 60, 60)
game\strategy\data\stars.py:281 - color = (255, 100, 100)
game\strategy\data\stars.py:291 - color = (20, 0, 40)
game\strategy\data\stars.py:297 - color = (200, 200, 255)
game\strategy\data\stars.py:302 - color = (220, 220, 255)
game\ui\colors.py:7 - WHITE = (255, 255, 255)
game\ui\colors.py:8 - BLACK = (0, 0, 0)
game\ui\colors.py:48 - LAYER_ARMOR = (100, 100, 100)     # Gray
game\ui\colors.py:49 - LAYER_OUTER = (200, 50, 50)       # Red
game\ui\colors.py:50 - LAYER_INNER = (50, 50, 200)       # Blue
game\ui\colors.py:51 - LAYER_CORE = (220, 220, 220)      # Light gray
game\ui\colors.py:54 - PROJECTILE_STANDARD = (255, 200, 50)   # Golden yellow
game\ui\colors.py:55 - PROJECTILE_MISSILE = (255, 50, 50)     # Red
game\ui\colors.py:56 - PROJECTILE_BEAM = (100, 200, 255)      # Light blue
game\ui\colors.py:59 - HP_HEALTHY = (0, 255, 0)         # Bright green (>50%)
game\ui\colors.py:60 - HP_DAMAGED = (255, 200, 0)       # Yellow (20-50%)
game\ui\colors.py:61 - HP_CRITICAL = (255, 50, 50)      # Red (<20%)
game\ui\colors.py:62 - HP_DESTROYED = (100, 100, 100)   # Gray (0%)
game\ui\colors.py:65 - RESOURCE_FUEL = (255, 165, 0)    # Orange
game\ui\colors.py:66 - RESOURCE_ENERGY = (100, 200, 255)  # Light blue
game\ui\colors.py:67 - RESOURCE_AMMO = (200, 200, 100)  # Yellowish
game\ui\colors.py:68 - RESOURCE_SHIELD = (0, 200, 255)  # Cyan
game\ui\colors.py:71 - RESEARCH_LOCKED = (80, 80, 90)       # Gray
game\ui\colors.py:72 - RESEARCH_AVAILABLE = (50, 100, 180)  # Blue
game\ui\colors.py:73 - RESEARCH_COMPLETED = (50, 140, 60)   # Green
game\ui\colors.py:74 - RESEARCH_SELECTED = (200, 180, 50)   # Gold
game\ui\colors.py:75 - RESEARCH_LINE_UNMET = (60, 65, 75)   # Dark gray
game\ui\colors.py:76 - RESEARCH_LINE_MET = (80, 120, 80)    # Muted green
game\ui\colors.py:77 - RESEARCH_LINE_NEGATED = (180, 80, 80)    # Red
game\ui\colors.py:78 - RESEARCH_LINE_NEGATED_MET = (100, 60, 60)  # Dark red
game\ui\colors.py:79 - RESEARCH_TEXT = (220, 220, 230)      # Off-white
game\ui\colors.py:80 - RESEARCH_CHANCE = (255, 220, 100)    # Gold/yellow
game\ui\colors.py:81 - RESEARCH_ALLOCATION = (255, 255, 0)  # Bright yellow
game\ui\colors.py:84 - TEST_PASS = (80, 255, 120)      # Bright green
game\ui\colors.py:85 - TEST_FAIL = (255, 80, 80)       # Bright red
game\ui\colors.py:88 - BG_BATTLE = (10, 10, 20)        # Nearly black (battle + app)
game\ui\colors.py:89 - BG_GALAXY = (15, 20, 30)        # Deep dark blue
game\ui\colors.py:90 - BG_MENU = (20, 20, 30)          # Dark blue-gray
game\ui\colors.py:93 - SHIP_CLASS_FIGHTER = (255, 150, 50)   # Orange
game\ui\colors.py:94 - SHIP_CLASS_CORVETTE = (100, 200, 100)  # Green
game\ui\colors.py:95 - SHIP_CLASS_ESCORT = (100, 150, 255)   # Light blue
game\ui\colors.py:96 - SHIP_CLASS_DESTROYER = (255, 100, 100)  # Red
game\ui\colors.py:97 - SHIP_CLASS_CRUISER = (200, 100, 255)  # Purple
game\ui\colors.py:98 - SHIP_CLASS_BATTLESHIP = (255, 200, 50)  # Yellow
game\ui\colors.py:99 - SHIP_CLASS_CARRIER = (150, 255, 200)  # Cyan-green
game\ui\colors.py:100 - SHIP_CLASS_DEFAULT = (150, 150, 150)  # Gray
game\ui\components\table\virtual_table.py:30 - SELECTED_COLOR = pygame.Color(60, 80, 120)  # Blue tint
game\ui\components\table\virtual_table.py:31 - UNSELECTED_COLOR = pygame.Color(35, 35, 35)  # Dark grey
game\ui\components\table\virtual_table.py:225 - row["bg"].background_colour = pygame.Color(*highlight)
game\ui\components\table\virtual_table.py:312 - row["bg"].background_colour = pygame.Color(*highlight)
game\ui\panels\battle_panels.py:152 - color = (200, 200, 200)
game\ui\panels\battle_panels.py:154 - color = (100, 100, 100)
game\ui\panels\battle_panels.py:156 - color = (255, 165, 0)
game\ui\panels\battle_panels.py:355 - color = (50, 255, 50)
game\ui\panels\battle_panels.py:357 - bg_color = (40, 40, 40)
game\ui\panels\battle_panels.py:359 - color = (150, 150, 150)
game\ui\panels\battle_panels.py:361 - bg_color = (40, 40, 40)
game\ui\panels\battle_panels.py:363 - color = (255, 50, 50)
game\ui\panels\battle_panels.py:365 - bg_color = (40, 40, 40)
game\ui\panels\battle_panels.py:367 - color = (255, 255, 100)
game\ui\panels\battle_panels.py:369 - bg_color = (50, 50, 60)
game\ui\panels\modifier_impact_grid.py:40 - COLOR_HEADER_BG = (40, 40, 50)
game\ui\panels\modifier_impact_grid.py:41 - COLOR_ROW_BG = (30, 30, 40)
game\ui\panels\modifier_impact_grid.py:42 - COLOR_ROW_ALT_BG = (35, 35, 45)
game\ui\panels\modifier_impact_grid.py:43 - COLOR_FOOTER_BG = (50, 50, 60)
game\ui\panels\modifier_impact_grid.py:44 - COLOR_TEXT = (200, 200, 200)
game\ui\panels\modifier_impact_grid.py:45 - COLOR_BUFF = (100, 255, 100)  # Green for positive
game\ui\panels\modifier_impact_grid.py:46 - COLOR_DEBUFF = (255, 100, 100)  # Red for negative
game\ui\panels\modifier_impact_grid.py:47 - COLOR_NEUTRAL = (180, 180, 180)  # Gray for neutral
game\ui\panels\planet_report_panel.py:216 - base_color = (100, 100, 100)
game\ui\panels\ship_stats_renderer.py:58 - status_color = (200, 200, 200)
game\ui\panels\ship_stats_renderer.py:64 - status_color = (255, 50, 50)
game\ui\panels\ship_stats_renderer.py:67 - status_color = (255, 165, 0)
game\ui\panels\ship_stats_renderer.py:70 - status_color = (255, 255, 0)
game\ui\panels\ship_stats_renderer.py:73 - status_color = (255, 100, 0)
game\ui\panels\ship_stats_renderer.py:151 - c_color = (200, 200, 200) if comp.is_active else (150, 50, 50)
game\ui\panels\ship_stats_renderer.py:153 - c_color = (255, 100, 100)
game\ui\panels\ship_stats_renderer.py:200 - color = (150, 150, 150)
game\ui\panels\ship_stats_renderer.py:204 - color = (100, 50, 50)
game\ui\panels\ship_stats_renderer.py:205 - bar_color = (100, 50, 50)
game\ui\panels\ship_stats_renderer.py:312 - crew_color = (180, 180, 180)
game\ui\panels\ship_stats_renderer.py:314 - crew_color = (255, 100, 100)
game\ui\panels\strategy_widgets.py:6 - def __init__(self, width, height, bg_color=(20, 24, 30)):
game\ui\renderer\game_renderer.py:147 - color = (200, 200, 200)
game\ui\renderer\game_renderer.py:148 - if comp.has_ability('WeaponAbility'): color = (255, 50, 50)
game\ui\renderer\game_renderer.py:149 - elif comp.has_ability('CombatPropulsion'): color = (50, 255, 100)
game\ui\renderer\game_renderer.py:150 - elif comp.has_ability('ArmorAbility') or comp.major_classification == 'Armor': color = (100, 100, 100)
game\ui\screens\battle_screen.py:620 - speed_color = (255, 100, 100) if self.sim_paused else (200, 200, 200)
game\ui\screens\battle_screen.py:622 - speed_color = (255, 200, 100)
game\ui\screens\battle_screen.py:624 - speed_color = (100, 255, 100)
game\ui\screens\battle_state_viewer.py:86 - self.header_color = (255, 255, 255)
game\ui\screens\battle_state_viewer.py:87 - self.button_color = (80, 80, 100)
game\ui\screens\battle_state_viewer.py:88 - self.button_hover_color = (100, 100, 130)
game\ui\screens\battle_ui.py:138 - grid_color = (30, 30, 50)
game\ui\screens\battle_ui.py:186 - color = (0, 100, 255)
game\ui\screens\battle_ui.py:242 - color = (0, 150, 200) if is_hovered else (0, 100, 150)
game\ui\screens\battle_ui.py:259 - complete_color = (80, 255, 120)  # Green
game\ui\screens\battle_ui.py:262 - complete_color = (255, 80, 80)  # Red
game\ui\screens\battle_ui.py:265 - complete_color = (255, 200, 100)  # Yellow
game\ui\screens\battle_ui.py:279 - result_color = (255, 255, 255)
game\ui\screens\battle_ui.py:282 - result_color = (0, 255, 0)
game\ui\screens\battle_ui.py:285 - result_color = (0, 255, 0)
game\ui\screens\battle_ui.py:288 - result_color = (255, 255, 0)
game\ui\screens\menu_scene.py:22 - BG_COLOR = (20, 20, 30)
game\ui\screens\new_game_setup_screen.py:202 - self.error_label.text_colour = pygame.Color(255, 100, 100)
game\ui\screens\setup_renderer.py:104 - bg_color = (30, 60, 50)
game\ui\screens\setup_renderer.py:105 - border_color = (100, 200, 150)
game\ui\screens\setup_renderer.py:107 - bg_color = (30, 50, 70)
game\ui\screens\setup_renderer.py:108 - border_color = (100, 150, 200)
game\ui\screens\setup_renderer.py:110 - bg_color = (70, 30, 30)
game\ui\screens\setup_renderer.py:111 - border_color = (200, 100, 100)
game\ui\screens\setup_renderer.py:145 - btn_color = (50, 150, 50) if has_teams else (50, 50, 50)
game\ui\screens\setup_renderer.py:164 - quick_color = (80, 50, 120) if has_teams else (40, 40, 40)
game\ui\screens\setup_renderer.py:199 - text_color = (220, 220, 220)
game\ui\screens\strategy_renderer.py:710 - color = (255, 255, 0)
game\ui\screens\strategy_renderer.py:742 - color = (0, 255, 100)
game\ui\screens\strategy_renderer.py:745 - color = (255, 50, 50)
game\ui\screens\workshop_viewmodel.py:338 - color=(100, 100, 255)
game\ui\screens\builder\structure_list_items.py:48 - self.panel.background_colour = pygame.Color(ctx.config.BG_COLOR_INDIVIDUAL)
game\ui\screens\builder\structure_list_items.py:153 - color = pygame.Color(config.TREE_LINE_COLOR)
game\ui\screens\builder\structure_list_items.py:228 - self.panel.background_colour = pygame.Color(ctx.config.BG_COLOR_GROUP)
game\ui\screens\builder\weapons_renderer.py:66 - BEAM_BAR_COLOR = (40, 80, 40)
game\ui\screens\builder\weapons_renderer.py:67 - PROJECTILE_BAR_COLOR = (80, 60, 40)
game\ui\screens\builder\weapons_renderer.py:68 - SEEKER_BAR_COLOR = (80, 40, 80)
game\ui\screens\builder\weapons_renderer.py:72 - COLOR_DAMAGE_LABEL = (200, 200, 100)
game\ui\screens\builder\weapons_renderer.py:81 - COLOR_ACC_HIGH = (0, 200, 0)
game\ui\screens\builder\weapons_renderer.py:82 - COLOR_ACC_MEDIUM = (200, 100, 0)
game\ui\screens\builder\weapons_renderer.py:83 - COLOR_ACC_LOW = (200, 50, 50)
game\ui\screens\builder\weapons_renderer.py:209 - COLOR_BG = (30, 30, 40)
game\ui\screens\builder\weapons_renderer.py:210 - COLOR_OUTLINE = (100, 100, 120)
game\ui\screens\builder\weapons_renderer.py:211 - COLOR_ARC = (200, 150, 50)
game\ui\screens\builder\weapons_renderer.py:212 - COLOR_ARROW = (255, 255, 255)
game\ui\screens\test_lab\component_dropdown.py:36 - self.bg_color = (50, 50, 60)
game\ui\screens\test_lab\component_dropdown.py:37 - self.selected_bg_color = (70, 70, 85)
game\ui\screens\test_lab\component_dropdown.py:38 - self.hover_bg_color = (60, 60, 75)
game\ui\screens\test_lab\component_dropdown.py:39 - self.text_color = (255, 255, 255)
game\ui\screens\test_lab\component_dropdown.py:40 - self.border_color = (100, 100, 120)
game\ui\screens\test_lab\json_viewer.py:48 - self.bg_color = (30, 30, 35)
game\ui\screens\test_lab\json_viewer.py:49 - self.title_bg_color = (45, 45, 50)
game\ui\screens\test_lab\json_viewer.py:50 - self.text_color = (220, 220, 220)
game\ui\screens\test_lab\json_viewer.py:51 - self.title_color = (255, 255, 255)
game\ui\screens\test_lab\json_viewer.py:52 - self.border_color = (100, 100, 120)
game\ui\screens\test_lab\renderer.py:31 - BG_COLOR = (20, 20, 25)
game\ui\screens\test_lab\renderer.py:32 - PANEL_BG = (25, 25, 30)
game\ui\screens\test_lab\renderer.py:33 - BORDER_COLOR = (80, 80, 90)
game\ui\screens\test_lab\renderer.py:34 - TEXT_COLOR = (220, 220, 220)
game\ui\screens\test_lab\renderer.py:35 - HEADER_COLOR = (100, 200, 255)
game\ui\screens\test_lab\renderer.py:36 - SELECTED_COLOR = (0, 100, 200)
game\ui\screens\test_lab\renderer.py:37 - HOVER_COLOR = (150, 150, 150)
game\ui\screens\test_lab\renderer.py:38 - CATEGORY_BG = (35, 35, 40)
game\ui\screens\test_lab\renderer.py:160 - bg_color = (40, 80, 120)
game\ui\screens\test_lab\renderer.py:161 - border_color = (80, 140, 200)
game\ui\screens\test_lab\renderer.py:162 - text_color = (200, 220, 255)
game\ui\screens\test_lab\renderer.py:164 - bg_color = (50, 50, 60)
game\ui\screens\test_lab\renderer.py:165 - border_color = (100, 100, 110)
game\ui\screens\test_lab\renderer.py:170 - text_color = (150, 150, 150)
game\ui\screens\test_lab\renderer.py:191 - seed_color = (100, 100, 100)
game\ui\screens\test_lab\renderer.py:202 - seed_color = (100, 140, 100)
game\ui\screens\test_lab\renderer.py:206 - seed_color = (100, 180, 255)
game\ui\screens\test_lab\renderer.py:209 - seed_color = (180, 140, 100)
game\ui\screens\test_lab\renderer.py:253 - color = (50, 50, 60)
game\ui\screens\test_lab\renderer.py:272 - color = (50, 50, 60)
game\ui\screens\test_lab\renderer.py:329 - bg_color = (100, 40, 40)  # Red for excluded
game\ui\screens\test_lab\renderer.py:330 - border_color = (180, 80, 80)
game\ui\screens\test_lab\renderer.py:331 - text_color = (255, 150, 150)
game\ui\screens\test_lab\renderer.py:334 - bg_color = (40, 80, 40)  # Green for active
game\ui\screens\test_lab\renderer.py:335 - border_color = (80, 150, 80)
game\ui\screens\test_lab\renderer.py:336 - text_color = (150, 255, 150)
game\ui\screens\test_lab\renderer.py:339 - bg_color = (50, 50, 60)
game\ui\screens\test_lab\renderer.py:340 - border_color = (100, 100, 110)
game\ui\screens\test_lab\renderer.py:346 - text_color = (180, 180, 180)
game\ui\screens\test_lab\renderer.py:425 - btn_color = (80, 80, 50)
game\ui\screens\test_lab\renderer.py:427 - text_color = (255, 255, 150)
game\ui\screens\test_lab\renderer.py:430 - btn_color = (60, 80, 60) if btn_hover else (40, 60, 40)
game\ui\screens\test_lab\renderer.py:433 - text_color = (150, 200, 150)
game\ui\screens\test_lab\renderer.py:480 - color = (40, 40, 50)
game\ui\screens\test_lab\renderer.py:482 - color = (30, 30, 35)
game\ui\screens\test_lab\renderer.py:567 - run_test_color = (70, 100, 70) if run_test_hover else (50, 80, 50)
game\ui\screens\test_lab\renderer.py:582 - run_headless_color = (70, 70, 100) if run_headless_hover else (50, 50, 80)
game\ui\screens\test_lab\renderer.py:871 - summary_color = (255, 200, 80)  # Yellow/Orange (unique)
game\ui\screens\test_lab\renderer.py:899 - status_color = (255, 200, 80)
game\ui\screens\test_lab\renderer.py:902 - status_color = (120, 120, 200)
game\ui\screens\test_lab\renderer.py:932 - p_color = (100, 255, 150)  # Green - proven equivalent (PASS)
game\ui\screens\test_lab\renderer.py:934 - p_color = (255, 100, 100)  # Red - not proven equivalent (FAIL)
game\ui\screens\test_lab\renderer.py:957 - button_color = (60, 120, 200)  # Blue
game\ui\screens\test_lab\renderer.py:958 - button_hover_color = (80, 140, 220)
game\ui\screens\test_lab\renderer.py:1002 - color = (100, 100, 100)
game\ui\screens\test_lab\renderer.py:1015 - color = (255, 200, 80)  # Yellow/Orange (unique)
game\ui\screens\test_lab\renderer.py:1036 - color = (255, 100, 100) if "ERROR" in msg else (150, 150, 150)
game\ui\screens\test_lab\results_panel.py:43 - self.bg_color = (30, 30, 35)
game\ui\screens\test_lab\results_panel.py:44 - self.border_color = (100, 100, 120)
game\ui\screens\test_lab\results_panel.py:45 - self.title_color = (255, 255, 255)
game\ui\screens\test_lab\results_panel.py:46 - self.button_color = (60, 120, 200)
game\ui\screens\test_lab\results_panel.py:47 - self.button_hover_color = (80, 140, 220)
game\ui\screens\test_lab\ship_panels.py:78 - self.bg_color = (30, 30, 35)
game\ui\screens\test_lab\ship_panels.py:79 - self.border_color = (80, 80, 90)
game\ui\screens\test_lab\ship_panels.py:80 - self.header_color = (150, 200, 255)
game\ui\screens\test_lab\ship_panels.py:81 - self.tab_color = (40, 40, 50)
game\ui\screens\test_lab\ship_panels.py:82 - self.tab_selected_color = (60, 80, 120)
game\ui\screens\test_lab\ship_panels.py:83 - self.tab_hover_color = (50, 50, 60)
game\ui\screens\test_lab\ship_panels.py:84 - self.text_color = (220, 220, 220)
game\ui\screens\test_lab\test_run_card.py:37 - self.bg_color = (35, 35, 40)
game\ui\screens\test_lab\test_run_card.py:38 - self.bg_hover_color = (45, 45, 50)
game\ui\screens\test_lab\test_run_card.py:39 - self.bg_selected_color = (55, 100, 150)  # Blue tint for selected
game\ui\screens\test_lab\test_run_card.py:40 - self.latest_bg_color = (40, 45, 50)  # Slightly different for latest
game\ui\screens\test_lab\test_run_card.py:43 - self.text_color = (220, 220, 220)
game\ui\screens\test_lab\test_run_card.py:44 - self.border_color = (100, 100, 120)
game\ui\screens\test_lab\test_run_card.py:47 - self.border_selected_color = (100, 150, 255)
game\ui\screens\test_lab\test_run_card.py:310 - vel_color = (255, 200, 100) if test_id == 'RESOURCE-002' else self.fail_color
game\ui\screens\test_lab\test_run_details.py:23 - self.bg_color = (30, 30, 35)
game\ui\screens\test_lab\test_run_details.py:24 - self.border_color = (80, 80, 90)
game\ui\screens\test_lab\test_run_details.py:25 - self.text_color = (220, 220, 220)
game\ui\screens\test_lab\test_run_details.py:28 - self.header_color = (150, 200, 255)
game\ui\screens\test_lab\test_run_details.py:29 - self.button_color = (60, 100, 160)
game\ui\screens\test_lab\test_run_details.py:30 - self.button_hover_color = (80, 120, 180)
game\ui\screens\test_lab\test_run_details.py:364 - status_color = (255, 200, 100)
game\ui\screens\test_lab\test_run_details.py:366 - actual_color = (255, 200, 100)
game\ui\screens\test_lab\test_run_details.py:375 - label_color = (140, 140, 160)
game\ui\screens\test_lab\test_run_details.py:376 - expected_color = (180, 200, 255)
game\ui\screens\test_lab\test_run_details.py:406 - label_color = (140, 140, 160)
game\ui\screens\test_lab\test_run_details.py:435 - label_color = (140, 140, 160)
game\ui\screens\test_lab\test_run_details.py:494 - label_color = (140, 140, 160)
game\ui\screens\test_lab\test_run_details.py:495 - value_color = (180, 200, 255)
game\ui\screens\test_lab\test_run_details.py:496 - highlight_color = (255, 220, 100)
game\ui\screens\test_lab\test_run_details.py:576 - vel_color = (255, 200, 100)
game\ui\screens\test_lab\test_run_details.py:604 - energy_color = (255, 200, 100)
game\ui\screens\test_lab\test_run_details.py:666 - ammo_color = (255, 200, 100)
game\ui\screens\test_lab\test_run_details.py:734 - label_color = (140, 140, 160)
game\ui\screens\test_lab\test_run_details.py:735 - value_color = (180, 200, 255)
game\ui\screens\test_lab\test_run_details.py:736 - highlight_color = (255, 220, 100)
game\ui\widgets\scrollable_json_panel.py:71 - self.bg_color = (25, 25, 30)
game\ui\widgets\scrollable_json_panel.py:72 - self.border_color = (80, 80, 100)
game\ui\widgets\scrollable_json_panel.py:73 - self.title_bg_color = (40, 40, 50)
game\ui\widgets\scrollable_json_panel.py:74 - self.title_color = (220, 220, 255)
game\ui\widgets\scrollable_json_panel.py:75 - self.text_color = (200, 200, 200)
game\ui\widgets\scrollable_json_panel.py:78 - self.key_color = (156, 220, 254)      # Light blue for keys
game\ui\widgets\scrollable_json_panel.py:79 - self.string_color = (206, 145, 120)   # Orange-brown for strings
game\ui\widgets\scrollable_json_panel.py:80 - self.number_color = (181, 206, 168)   # Green for numbers
game\ui\widgets\scrollable_json_panel.py:81 - self.bool_color = (86, 156, 214)      # Blue for booleans
game\ui\widgets\scrollable_json_panel.py:82 - self.null_color = (86, 156, 214)      # Blue for null
game\ui\widgets\scrollable_json_panel.py:83 - self.bracket_color = (180, 180, 180)  # Gray for brackets
game\ui\widgets\scrollable_json_panel.py:410 - thumb_color = (100, 100, 120) if not self.scrollbar_dragging else (120, 120, 140)
scripts\galaxy_screenshot.py:206 - line_color = (40, 60, 80)
scripts\galaxy_screenshot.py:210 - line_color = (255, 80, 80)  # Bright red for inter-region
scripts\galaxy_screenshot.py:213 - line_color = (50, 50, 100)
scripts\galaxy_screenshot.py:232 - color = (200, 200, 100)
scripts\galaxy_screenshot.py:241 - legend_color = (100, 200, 100) if show_warp_lines else (200, 100, 100)
scripts\visual_test_galaxy.py:92 - grid_color = (30, 30, 40)
test_framework\scenario.py:85 - color = (0, 0, 255) if team_id == 1 else (255, 0, 0)

Total Colors: 253

### VALIDATION RESULT BOILERPLATE
game\core\validation.py:38 - result = ValidationResult()
game\core\validation.py:158 - return ValidationResult(is_valid=True)
game\core\validation.py:179 - return ValidationResult(is_valid=False, errors=[message], error_code=error_code_value)
game\core\validation.py:196 - return ValidationResult(is_valid=False, errors=list(messages))
simulation_tests\data\schema_validator.py:185 - return ValidationResult(data_file, True, ["jsonschema not available - validation skipped"])
simulation_tests\data\schema_validator.py:190 - return ValidationResult(data_file, False, [f"Schema {schema_file} not found"])
simulation_tests\data\schema_validator.py:195 - return ValidationResult(data_file, False, [f"Data file not found: {data_path}"])
simulation_tests\data\schema_validator.py:201 - return ValidationResult(data_file, False, [f"Invalid JSON: {e}"])
simulation_tests\data\schema_validator.py:207 - return ValidationResult(data_file, False, [version_error])
simulation_tests\data\schema_validator.py:209 - return ValidationResult(data_file, False, [f"Version validation error: {e}"])
simulation_tests\data\schema_validator.py:214 - return ValidationResult(data_file, True)
simulation_tests\data\schema_validator.py:219 - return ValidationResult(data_file, False, [error_msg])
simulation_tests\data\schema_validator.py:221 - return ValidationResult(data_file, False, [f"Schema error: {e.message}"])
simulation_tests\scenarios\validation.py:212 - return ValidationResult(
simulation_tests\scenarios\validation.py:221 - return ValidationResult(
simulation_tests\scenarios\validation.py:290 - return ValidationResult(
simulation_tests\scenarios\validation.py:300 - return ValidationResult(
simulation_tests\scenarios\validation.py:341 - return ValidationResult(
simulation_tests\scenarios\validation.py:429 - return ValidationResult(
simulation_tests\scenarios\validation.py:459 - return ValidationResult(
simulation_tests\scenarios\validation.py:474 - return ValidationResult(
simulation_tests\scenarios\validation.py:539 - return ValidationResult(
simulation_tests\scenarios\validation.py:551 - return ValidationResult(
simulation_tests\scenarios\validation.py:561 - return ValidationResult(
simulation_tests\scenarios\validation.py:634 - results.append(ValidationResult(

Total ValidationResults: 25
