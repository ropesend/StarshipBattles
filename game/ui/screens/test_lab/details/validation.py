"""Validation results renderer for the test-run-details panel.

PROJ-309 sub-phase 3.6 — extracted verbatim from `test_run_details.py`.

CRITICAL UI CONTRACT (per `feedback_combat_lab_ui.md`):
    * Phase headers (DATA / PRECONDITION / OUTCOME) in correct phase colors.
    * Each check shows V or X glyph in pass/fail color, with name color-coded.
    * Expected / Actual / Difference rows when values are present.
    * `EXACT MATCH` formatting for diff < 1e-9.
    * `essentially exact` formatting for sub-0.01% diff.
    * `±` percentage formatting for everything else.
    * `p-value:` row for statistical tests.
    * `Detail:` row for tolerance / TOST info.
    * Subtle separator between check items.

NO LOGIC CHANGES from the original. This file relocates the four methods
`_draw_validation_results`, `_draw_single_validation`,
`_draw_numeric_difference` (and the inline phase-grouping constants) into
module-level functions. The visible output is byte-equivalent.
"""
from __future__ import annotations

import pygame

from game.ui.screens.test_lab import theme
from game.ui.screens.test_lab.formatting_utils import format_value

from .draw_context import DetailsDrawContext

# Phase grouping (was inline in `_draw_validation_results`)
_PHASE_ORDER = ['data', 'precondition', 'outcome']
_PHASE_LABELS = {
    'data': 'DATA CHECKS',
    'precondition': 'PRECONDITION CHECKS',
    'outcome': 'OUTCOME CHECKS',
}


def _phase_color(phase: str) -> tuple[int, int, int]:
    """Resolve the per-phase header color from `theme`. Done at call time so
    test patches of `theme` are honoured."""
    return {
        'data': theme.PHASE_DATA,
        'precondition': theme.PHASE_PRECONDITION,
        'outcome': theme.PHASE_OUTCOME,
    }[phase]


def draw_validation_results(
    ctx: DetailsDrawContext,
    run_record,
    y_offset: int,
) -> int:
    """Draw validation results section grouped by phase with expected/actual/status.

    Checks are grouped into DATA, PRECONDITION, and OUTCOME phases.
    Each check shows a green/red indicator, name, expected, actual, and detail.

    Returns updated y_offset.
    """
    surface = ctx.surface
    if not run_record.validation_results:
        return y_offset

    val_title = ctx.header_font.render("VALIDATION RESULTS", True, ctx.header_color)
    surface.blit(val_title, (ctx.x + 10, y_offset))
    y_offset += 25

    # Draw separator line
    pygame.draw.line(surface, theme.SEPARATOR_LINE,
                   (ctx.x + 10, y_offset), (ctx.x + ctx.width - 20, y_offset))
    y_offset += 8

    grouped: dict[str, list] = {p: [] for p in _PHASE_ORDER}
    for vr in run_record.validation_results:
        phase = vr.get('phase', 'outcome')
        if phase not in grouped:
            phase = 'outcome'
        grouped[phase].append(vr)

    for phase in _PHASE_ORDER:
        checks = grouped[phase]
        if not checks:
            continue

        # Phase header
        phase_label = _PHASE_LABELS[phase]
        phase_color = _phase_color(phase)
        phase_surf = ctx.body_font.render(phase_label, True, phase_color)
        surface.blit(phase_surf, (ctx.x + 15, y_offset))
        y_offset += 22

        # Individual checks
        for vr in checks:
            y_offset = draw_single_validation(ctx, vr, y_offset)

        y_offset += 5  # Space between phase groups

    return y_offset


def draw_single_validation(
    ctx: DetailsDrawContext,
    vr,
    y_offset: int,
) -> int:
    """Draw a single validation result item.

    Returns updated y_offset.
    """
    surface = ctx.surface
    status = vr.get('status', 'PASS')
    name = vr.get('name', '')
    expected = vr.get('expected')
    actual = vr.get('actual')
    detail = vr.get('detail')
    p_value = vr.get('p_value')

    # Determine colors based on status
    if status == 'PASS':
        status_color = ctx.pass_color
        symbol = "V"
        actual_color = ctx.pass_color
    elif status == 'FAIL':
        status_color = ctx.fail_color
        symbol = "X"
        actual_color = ctx.fail_color
    else:
        status_color = theme.STATUS_WARNING
        symbol = "!"
        actual_color = theme.STATUS_WARNING

    # Validation name with symbol (color-coded)
    val_line = f"{symbol} {name}"
    val_surf = ctx.small_font.render(val_line, True, status_color)
    surface.blit(val_surf, (ctx.x + 20, y_offset))
    y_offset += 18

    # Define layout constants
    label_color = theme.TEXT_LABEL
    expected_color = theme.TEXT_EXPECTED
    indent = 30
    label_width = 75

    # Show expected value (if present)
    if expected is not None:
        exp_str = format_value(expected, precision="full")
        exp_label = ctx.small_font.render("Expected:", True, label_color)
        exp_value = ctx.small_font.render(exp_str, True, expected_color)
        surface.blit(exp_label, (ctx.x + indent, y_offset))
        surface.blit(exp_value, (ctx.x + indent + label_width, y_offset))
        y_offset += 16

    # Show actual value (color-coded green/red based on status)
    if actual is not None:
        act_str = format_value(actual, precision="full")
        act_label = ctx.small_font.render("Actual:", True, label_color)
        act_value = ctx.small_font.render(act_str, True, actual_color)
        surface.blit(act_label, (ctx.x + indent, y_offset))
        surface.blit(act_value, (ctx.x + indent + label_width, y_offset))
        y_offset += 16

    # Show difference/percentage (if both values are numeric)
    if expected is not None and actual is not None:
        y_offset = draw_numeric_difference(
            ctx, expected, actual, status, y_offset, indent, label_width
        )

    # P-value (for statistical tests)
    if p_value is not None:
        label_color = theme.TEXT_LABEL
        p_color = ctx.pass_color if p_value < 0.05 else ctx.fail_color
        p_str = f"{p_value:.6f}"
        if p_value < 0.05:
            p_str += " (proven equivalent)"
        else:
            p_str += " (not proven equivalent)"
        p_label = ctx.small_font.render("p-value:", True, label_color)
        p_value_surf = ctx.small_font.render(p_str, True, p_color)
        surface.blit(p_label, (ctx.x + indent, y_offset))
        surface.blit(p_value_surf, (ctx.x + indent + label_width, y_offset))
        y_offset += 16

    # Detail string (e.g. TOST info, tolerance)
    if detail:
        detail_label = ctx.small_font.render("Detail:", True, label_color)
        detail_value = ctx.small_font.render(str(detail), True, theme.TEXT_MUTED)
        surface.blit(detail_label, (ctx.x + indent, y_offset))
        surface.blit(detail_value, (ctx.x + indent + label_width, y_offset))
        y_offset += 16

    y_offset += 10  # Space between validation items

    # Draw subtle separator between validation items
    pygame.draw.line(surface, theme.SEPARATOR_SUBTLE,
                   (ctx.x + 20, y_offset - 5), (ctx.x + ctx.width - 30, y_offset - 5))

    return y_offset


def draw_numeric_difference(
    ctx: DetailsDrawContext,
    expected,
    actual,
    status: str,
    y_offset: int,
    indent: int,
    label_width: int,
) -> int:
    """Draw the difference/percentage line for numeric values.

    Returns updated y_offset.
    """
    if not (isinstance(expected, (int, float)) and isinstance(actual, (int, float))):
        return y_offset
    # Skip difference for boolean checks — True/False are int subclasses
    # but computing "1000 vs True = +99900%" is meaningless
    if isinstance(expected, bool) or isinstance(actual, bool):
        return y_offset

    surface = ctx.surface
    label_color = theme.TEXT_LABEL
    diff = actual - expected
    abs_diff = abs(diff)

    if expected != 0:
        pct_diff = (diff / expected) * 100
        abs_pct_diff = abs(pct_diff)

        if abs_pct_diff < 1e-9:
            diff_str = "EXACT MATCH"
            diff_color = ctx.pass_color
        elif abs_pct_diff < 0.01:
            diff_str = f"{pct_diff:+.6f}% (essentially exact)"
            diff_color = ctx.pass_color
        else:
            diff_str = f"{pct_diff:+.4f}%"
            diff_color = ctx.pass_color if status == 'PASS' else ctx.fail_color
    else:
        if abs_diff < 1e-9:
            diff_str = "EXACT MATCH"
            diff_color = ctx.pass_color
        else:
            diff_str = f"Diff: {diff:+.6f}"
            diff_color = ctx.pass_color if status == 'PASS' else ctx.fail_color

    diff_label = ctx.small_font.render("Difference:", True, label_color)
    diff_value = ctx.small_font.render(diff_str, True, diff_color)
    surface.blit(diff_label, (ctx.x + indent, y_offset))
    surface.blit(diff_value, (ctx.x + indent + label_width, y_offset))
    y_offset += 16

    return y_offset
