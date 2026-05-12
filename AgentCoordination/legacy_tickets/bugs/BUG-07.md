# BUG-07: Crash Adding Component

## Description
The game crashed when I was adding a component.  here is the console output:

PS C:\Dev\Starship Battles> python launcher.py
pygame-ce 2.5.6 (SDL 2.32.10, Python 3.10.11)
Loaded 5 layer configurations from vehiclelayers.json.
Loaded 30 vehicle classes.
Loading sprites from C:\Dev\Starship Battles\assets\Images\Components\Tiles
SUCCESS: Loaded 242 sprites from directory (max index 241)
C:\Users\rossr\AppData\Local\Programs\Python\Python310\lib\site-packages\pygame_gui\core\ui_font_dictionary.py:405: UserWarning: Finding font with id: noto_sans_bold_aa_14 that is not already loaded.
Preload this font with {'name': 'noto_sans', 'point_size': 14, 'style': 'bold', 'antialiased': '1'}
  warnings.warn(warning_string, UserWarning)
Traceback (most recent call last):
  File "C:\Dev\Starship Battles\launcher.py", line 9, in <module>
    main()
  File "C:\Dev\Starship Battles\game\app.py", line 516, in main
    game.run()
  File "C:\Dev\Starship Battles\game\app.py", line 221, in run
    self._update_and_draw(frame_time, events)
  File "C:\Dev\Starship Battles\game\app.py", line 291, in _update_and_draw
    self.builder_scene.draw(self.screen)
  File "C:\Dev\Starship Battles\game\ui\screens\builder_screen.py", line 835, in draw
    self.weapons_report_panel.draw(screen)
  File "C:\Dev\Starship Battles\ui\builder\weapons_panel.py", line 921, in draw
    self._draw_beam_weapon_bar(screen, weapon, ship, bar_y, start_x, bar_width, weapon_bar_width, weapon_range, damage)
  File "C:\Dev\Starship Battles\ui\builder\weapons_panel.py", line 674, in _draw_beam_weapon_bar
    attack_score = ship.get_total_sensor_score()
  File "C:\Dev\Starship Battles\game\simulation\entities\ship.py", line 588, in get_total_sensor_score
    total_score += ab.value
AttributeError: 'ToHitAttackModifier' object has no attribute 'value'
PS C:\Dev\Starship Battles> 

## Status
[Pending]

## Work Log
- [2026-01-03 17:15] Reproduction: Confirmed using `tests/repro_issues/test_bug_07_crash.py`.
    - Error: `AttributeError: 'ToHitAttackModifier' object has no attribute 'value'`
    - Root Cause: `ToHitAttackModifier` class uses `self.amount` but `ship.py` accesses `ab.value`.
- [2026-01-03 17:25] Fix: Renamed `amount` to `value` in `ToHitAttackModifier` and `ToHitDefenseModifier` classes in `game/simulation/components/abilities.py` to match API expectation.
    - Verified with `tests/repro_issues/test_bug_07_crash.py` (Passed).
    - Verified no regressions in `tests/unit/test_ship_stats.py` (Passed).
