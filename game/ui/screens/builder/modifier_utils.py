"""Shared modifier utilities for the Design Workshop."""


from __future__ import annotations

def copy_modifiers(source, target) -> None:
    """Copy all modifiers from source component to target component.

    Replaces target's modifiers with clones of source's modifiers,
    preserving definition and value. Recalculates target stats after copy.

    Args:
        source: Component to copy modifiers from.
        target: Component to copy modifiers to.
    """
    target.modifiers = []
    for m in source.modifiers:
        new_m = m.__class__(m.definition, m.value)
        target.modifiers.append(new_m)
    target.recalculate_stats()
