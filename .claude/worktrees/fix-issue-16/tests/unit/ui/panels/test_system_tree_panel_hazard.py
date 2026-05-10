"""PROJ-302 D8: hostile-system hazard hint formatter tests."""
from game.ui.panels.system_tree_panel import _format_star_hazard_hints


def _star_provider(label, ability_data):
    return {
        'source_kind': 'star',
        'source_label': label,
        'source_id': f'star:{label}',
        'is_active': True,
        'ability_data': ability_data,
    }


def _effect(ability_name, providers):
    return {'ability_name': ability_name, 'providers': providers}


def test_no_effects_yields_empty_hints():
    assert _format_star_hazard_hints([]) == []


def test_benign_main_sequence_star_yields_no_hint():
    """Sun-like star with no abilities should produce no hazard hint."""
    assert _format_star_hazard_hints([]) == []


def test_pulsar_shield_modifier_renders_hazard():
    """PROJ-302 D7: a pulsar with ShieldModifier 0.7 system-scope is HOSTILE."""
    effects = [_effect('ShieldModifier', [
        _star_provider('Pulsar X-1 (Pulsar)', {'multiplier': 0.7, 'scope': 'system'}),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 1
    assert 'Pulsar X-1' in hints[0]
    assert '-30%' in hints[0]
    assert 'shields' in hints[0].lower()


def test_neutron_star_environmental_damage_renders_hazard():
    effects = [_effect('EnvironmentalDamage', [
        _star_provider('Cyg X-3 (Neutron Star)', {
            'rate': 0.3, 'damage_type': 'radiation', 'scope': 'system',
        }),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 1
    assert 'radiation' in hints[0]
    assert '0.30' in hints[0]


def test_black_hole_thrust_modifier_renders_hazard():
    effects = [_effect('ThrustModifier', [
        _star_provider('Sgr A* (Black Hole)', {'multiplier': 0.5, 'scope': 'system'}),
    ])]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 1
    assert 'thrust' in hints[0].lower()
    assert '-50%' in hints[0]


def test_facility_provider_does_not_render_hazard_hint():
    """Hazard hints are STAR-specific (D8 — only system-scope hostile stars)."""
    facility_provider = {
        'source_kind': 'facility',
        'source_label': 'Shield Generator',
        'is_active': True,
        'ability_data': {'multiplier': 0.5, 'scope': 'system'},
    }
    effects = [_effect('ShieldModifier', [facility_provider])]
    assert _format_star_hazard_hints(effects) == []


def test_storm_provider_does_not_render_hazard_hint():
    """Storms are sector-scope, not system-scope hostile stars."""
    storm_provider = {
        'source_kind': 'storm',
        'source_label': 'Ion Storm Alpha',
        'is_active': True,
        'ability_data': {'multiplier': 0.5, 'scope': 'sector'},
    }
    effects = [_effect('ShieldModifier', [storm_provider])]
    assert _format_star_hazard_hints(effects) == []


def test_buff_shield_modifier_does_not_render_hazard():
    """A friendly system-wide shield buff (>= 1.0) is not a hazard."""
    effects = [_effect('ShieldModifier', [
        _star_provider('Friendly Aura Star', {'multiplier': 1.25, 'scope': 'system'}),
    ])]
    assert _format_star_hazard_hints(effects) == []


def test_multiple_hazards_all_rendered():
    """Pulsar + neutron-star binary in same system: both hazards visible."""
    effects = [
        _effect('ShieldModifier', [
            _star_provider('Star A (Pulsar)', {'multiplier': 0.7, 'scope': 'system'}),
        ]),
        _effect('EnvironmentalDamage', [
            _star_provider('Star B (Neutron Star)', {
                'rate': 0.4, 'damage_type': 'radiation', 'scope': 'system',
            }),
        ]),
    ]
    hints = _format_star_hazard_hints(effects)
    assert len(hints) == 2
    assert any('Pulsar' in h for h in hints)
    assert any('Neutron' in h for h in hints)
