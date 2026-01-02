import json
import os

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def check_consistency():
    filepath = r"c:\Dev\Starship Battles\data\components.json"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    data = load_json(filepath)
    components = data.get("components", [])
    
    issues = []
    
    stats = {
        "weapons": {"total": 0, "tag_only": 0, "migrated_data": 0, "mismatch": 0, "missing_ability": 0},
        "engines": {"total": 0, "migrated_data": 0, "mismatch": 0, "missing_ability": 0},
        "thrusters": {"total": 0, "migrated_data": 0, "mismatch": 0, "missing_ability": 0},
        "shields": {"total": 0, "migrated_data": 0, "mismatch": 0, "missing_ability": 0, "legacy_remaining": 0},
    }

    for comp in components:
        cid = comp.get("id")
        ctype = comp.get("type")
        cname = comp.get("name")
        abilities = comp.get("abilities", {})
        
        # Check Weapons
        if comp.get("major_classification") == "Weapons" or ctype in ["ProjectileWeapon", "BeamWeapon", "SeekerWeapon", "Weapon"]:
            stats["weapons"]["total"] += 1
            has_weapon_ability = any(k in abilities for k in ["ProjectileWeapon", "BeamWeapon", "SeekerWeapon", "WeaponAbility"])
            if not has_weapon_ability:
                issues.append(f"[MISSING_ABILITY] Weapon '{cid}' ({cname}) missing WeaponAbility definition.")
                stats["weapons"]["missing_ability"] += 1
            else:
                # Check migration state
                is_tag_only = True
                for ab_name in ["ProjectileWeapon", "BeamWeapon", "SeekerWeapon", "WeaponAbility"]:
                    if ab_name in abilities:
                        ab_data = abilities[ab_name]
                        if isinstance(ab_data, dict):
                            is_tag_only = False
                            # Check basic stats
                            for field in ["damage", "range", "reload", "firing_arc"]:
                                legacy_val = comp.get(field)
                                ability_val = ab_data.get(field)
                                
                                if legacy_val is not None and ability_val is not None:
                                    if legacy_val != ability_val:
                                        issues.append(f"[MISMATCH] '{cid}' {field}: Legacy={legacy_val}, Ability={ability_val}")
                                        stats["weapons"]["mismatch"] += 1
                                elif legacy_val is not None and ability_val is None:
                                    # Legacy exists, ability data missing (but ability dict exists)
                                    pass
                
                if is_tag_only:
                    stats["weapons"]["tag_only"] += 1
                else:
                    stats["weapons"]["migrated_data"] += 1
        
        # Check Engines
        if ctype == "Engine":
            stats["engines"]["total"] += 1
            if "CombatPropulsion" not in abilities:
                issues.append(f"[MISSING_ABILITY] Engine '{cid}' missing CombatPropulsion.")
                stats["engines"]["missing_ability"] += 1
            else:
                legacy_thrust = comp.get("thrust_force")
                ab_thrust = abilities["CombatPropulsion"]
                # CombatPropulsion value is the thrust
                if legacy_thrust is not None:
                    if legacy_thrust != ab_thrust:
                        issues.append(f"[MISMATCH] '{cid}' thrust_force: Legacy={legacy_thrust}, Ability={ab_thrust}")
                        stats["engines"]["mismatch"] += 1
                    else:
                        stats["engines"]["migrated_data"] += 1
        
        # Check Thrusters
        if ctype == "Thruster":
            stats["thrusters"]["total"] += 1
            if "ManeuveringThruster" not in abilities:
                issues.append(f"[MISSING_ABILITY] Thruster '{cid}' missing ManeuveringThruster.")
                stats["thrusters"]["missing_ability"] += 1
            else:
                legacy_turn = comp.get("turn_speed")
                ab_turn = abilities["ManeuveringThruster"]
                if legacy_turn is not None:
                    if legacy_turn != ab_turn:
                        issues.append(f"[MISMATCH] '{cid}' turn_speed: Legacy={legacy_turn}, Ability={ab_turn}")
                        stats["thrusters"]["mismatch"] += 1
                    else:
                        stats["thrusters"]["migrated_data"] += 1

        # Check Shields
        if ctype == "Shield":
            stats["shields"]["total"] += 1
            if "ShieldProjection" not in abilities:
                issues.append(f"[MISSING_ABILITY] Shield '{cid}' missing ShieldProjection.")
                stats["shields"]["missing_ability"] += 1
            else:
                stats["shields"]["migrated_data"] += 1 # Assumed migrated since it exists
                
            if "shield_capacity" in comp or "capacity" in comp:
                 stats["shields"]["legacy_remaining"] += 1

            
    # Print results
    print(f"Checked {len(components)} components.")
    
    print("\n--- Summary ---")
    print(f"Weapons: {stats['weapons']['total']} total")
    print(f"  - Tag Only (Need Data Migration): {stats['weapons']['tag_only']}")
    print(f"  - Fully Migrated (Has Data): {stats['weapons']['migrated_data']}")
    print(f"  - Mismatches: {stats['weapons']['mismatch']}")
    print(f"  - Missing Abilities: {stats['weapons']['missing_ability']}")

    print(f"\nEngines: {stats['engines']['total']} total")
    print(f"  - Fully Migrated (Consistent): {stats['engines']['migrated_data']}")
    print(f"  - Mismatches: {stats['engines']['mismatch']}")
    
    print(f"\nThrusters: {stats['thrusters']['total']} total")
    print(f"  - Fully Migrated (Consistent): {stats['thrusters']['migrated_data']}")
    print(f"  - Mismatches: {stats['thrusters']['mismatch']}")

    print(f"\nShields: {stats['shields']['total']} total")
    print(f"  - Migrated Ability: {stats['shields']['migrated_data']}")
    print(f"  - Legacy Keys Remaining: {stats['shields']['legacy_remaining']}")

    if issues:
        print("\n--- Issues ---")
        for issue in issues:
            print(issue)

if __name__ == "__main__":
    check_consistency()
