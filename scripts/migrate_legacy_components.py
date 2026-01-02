#!/usr/bin/env python
"""
Migration script for Starship Battles Component Refactor - Phase 6
Migrates legacy weapon attributes into ability dictionaries and removes redundant engine/thruster attributes.
"""

import json
import argparse
import sys
from pathlib import Path
from copy import deepcopy

# Weapon attributes to migrate into ability dicts
WEAPON_ATTRS = ['damage', 'range', 'reload', 'projectile_speed', 'firing_arc', 'facing_angle',
                'base_accuracy', 'accuracy_falloff', 'endurance', 'turn_rate', 'to_hit_defense']

# Ability type mapping based on weapon type or abilities dict
WEAPON_ABILITY_MAPPING = {
    'ProjectileWeapon': 'ProjectileWeaponAbility',
    'BeamWeapon': 'BeamWeaponAbility',
    'SeekerWeapon': 'SeekerWeaponAbility',
}

# Legacy attributes to remove from engines/thrusters (already in abilities)
REDUNDANT_ENGINE_ATTRS = ['thrust_force']
REDUNDANT_THRUSTER_ATTRS = ['turn_speed']


def detect_weapon_ability_type(comp):
    """Determine the appropriate weapon ability type from component data."""
    comp_type = comp.get('type', '')
    abilities = comp.get('abilities', {})
    
    # Check type field first
    if comp_type in WEAPON_ABILITY_MAPPING:
        return WEAPON_ABILITY_MAPPING[comp_type]
    
    # Check abilities dict for weapon flags
    for flag in ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']:
        if flag in abilities:
            return WEAPON_ABILITY_MAPPING[flag]
    
    return None


def migrate_weapon(comp, dry_run=False):
    """Migrate weapon root attributes into ability dict. Returns (modified_comp, changes_list)."""
    changes = []
    ability_type = detect_weapon_ability_type(comp)
    
    if not ability_type:
        return comp, []
    
    # Collect weapon attributes at root level
    weapon_data = {}
    attrs_to_remove = []
    
    for attr in WEAPON_ATTRS:
        if attr in comp:
            weapon_data[attr] = comp[attr]
            attrs_to_remove.append(attr)
    
    if not weapon_data:
        return comp, []
    
    if dry_run:
        return comp, [f"Would migrate {attrs_to_remove} to {ability_type}"]
    
    # Deep copy to avoid mutation
    new_comp = deepcopy(comp)
    
    # Remove the old flag (e.g., "ProjectileWeapon": true) and create proper ability dict
    old_flag = ability_type.replace('Ability', '')  # e.g., ProjectileWeaponAbility -> ProjectileWeapon
    if old_flag in new_comp.get('abilities', {}):
        del new_comp['abilities'][old_flag]
    
    # Add the new ability with weapon data
    new_comp['abilities'][ability_type] = weapon_data
    
    # Remove root-level weapon attributes
    for attr in attrs_to_remove:
        del new_comp[attr]
    
    changes.append(f"Migrated {attrs_to_remove} to abilities.{ability_type}")
    return new_comp, changes


def remove_redundant_engine_attrs(comp, dry_run=False):
    """Remove redundant thrust_force from engines that already have CombatPropulsion ability."""
    changes = []
    abilities = comp.get('abilities', {})
    
    # Only process if CombatPropulsion ability exists
    if 'CombatPropulsion' not in abilities:
        return comp, []
    
    attrs_to_remove = [attr for attr in REDUNDANT_ENGINE_ATTRS if attr in comp]
    
    if not attrs_to_remove:
        return comp, []
    
    if dry_run:
        return comp, [f"Would remove redundant: {attrs_to_remove}"]
    
    new_comp = deepcopy(comp)
    for attr in attrs_to_remove:
        del new_comp[attr]
    
    changes.append(f"Removed redundant: {attrs_to_remove}")
    return new_comp, changes


def remove_redundant_thruster_attrs(comp, dry_run=False):
    """Remove redundant turn_speed from thrusters that already have ManeuveringThruster ability."""
    changes = []
    abilities = comp.get('abilities', {})
    
    # Only process if ManeuveringThruster ability exists
    if 'ManeuveringThruster' not in abilities:
        return comp, []
    
    attrs_to_remove = [attr for attr in REDUNDANT_THRUSTER_ATTRS if attr in comp]
    
    if not attrs_to_remove:
        return comp, []
    
    if dry_run:
        return comp, [f"Would remove redundant: {attrs_to_remove}"]
    
    new_comp = deepcopy(comp)
    for attr in attrs_to_remove:
        del new_comp[attr]
    
    changes.append(f"Removed redundant: {attrs_to_remove}")
    return new_comp, changes


def migrate_components(data, dry_run=False):
    """Process all components and apply migrations. Returns (new_data, report)."""
    report = {
        'weapons_migrated': 0,
        'engines_cleaned': 0,
        'thrusters_cleaned': 0,
        'details': []
    }
    
    new_components = []
    
    for comp in data.get('components', []):
        comp_id = comp.get('id', 'unknown')
        comp_changes = []
        
        # Apply weapon migration
        comp, weapon_changes = migrate_weapon(comp, dry_run)
        if weapon_changes:
            report['weapons_migrated'] += 1
            comp_changes.extend(weapon_changes)
        
        # Apply engine cleanup
        comp, engine_changes = remove_redundant_engine_attrs(comp, dry_run)
        if engine_changes:
            report['engines_cleaned'] += 1
            comp_changes.extend(engine_changes)
        
        # Apply thruster cleanup
        comp, thruster_changes = remove_redundant_thruster_attrs(comp, dry_run)
        if thruster_changes:
            report['thrusters_cleaned'] += 1
            comp_changes.extend(thruster_changes)
        
        if comp_changes:
            report['details'].append({
                'id': comp_id,
                'name': comp.get('name', comp_id),
                'changes': comp_changes
            })
        
        new_components.append(comp)
    
    new_data = deepcopy(data)
    new_data['components'] = new_components
    
    return new_data, report


def print_report(report, dry_run=False):
    """Print migration report."""
    mode = "DRY RUN" if dry_run else "MIGRATION"
    print(f"\n{'='*60}")
    print(f" {mode} REPORT")
    print(f"{'='*60}")
    print(f"  Weapons migrated: {report['weapons_migrated']}")
    print(f"  Engines cleaned:  {report['engines_cleaned']}")
    print(f"  Thrusters cleaned: {report['thrusters_cleaned']}")
    print(f"{'='*60}")
    
    if report['details']:
        print("\nDetailed Changes:")
        for item in report['details']:
            print(f"\n  [{item['id']}] {item['name']}")
            for change in item['changes']:
                print(f"    - {change}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description='Migrate legacy component attributes to ability system')
    parser.add_argument('input', help='Input components.json file')
    parser.add_argument('-o', '--output', help='Output file (default: overwrite input)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed changes')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Load data
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Run migration
    new_data, report = migrate_components(data, dry_run=args.dry_run)
    
    # Print report
    if args.verbose or args.dry_run:
        print_report(report, args.dry_run)
    else:
        print(f"Migrated: {report['weapons_migrated']} weapons, "
              f"cleaned: {report['engines_cleaned']} engines, "
              f"{report['thrusters_cleaned']} thrusters")
    
    # Write output
    if not args.dry_run:
        output_path = Path(args.output) if args.output else input_path
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
        print(f"Wrote: {output_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
