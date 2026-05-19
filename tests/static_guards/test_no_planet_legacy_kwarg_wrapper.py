"""PROJ-449 Phase 3 deletion guard.

Pins the absence of the PROJ-436 Phase 4f legacy-kwarg constructor
wrapper and the matching ``@setter`` shims on
:class:`game.strategy.data.planet.Planet`.

Companion to ``test_no_legacy_storage_fields.py``, which pins the
absence of the dataclass field names. After PROJ-449 Phase 3:

* ``_planet_init_with_legacy_kwargs`` is gone (the wrapper that
  translated public kwargs ``stockpile=`` / ``max_stockpile=`` /
  ``staging_yard=`` to their underscore-prefixed dataclass spellings).
* The ``stockpile`` / ``max_stockpile`` / ``staging_yard`` ``@setter``
  shims that allowed ``planet.stockpile = {...}`` rebinding are gone.
* The matching ``@property`` GETTERS survive as read-only attribute
  views over the private fields — see Planet docstring. The original
  PROJ-449 plan called for getter+setter deletion together, but the
  Phase-0 audit missed extensive production read sites
  (16 game/ files + 50+ test files read ``planet.stockpile`` /
  ``.staging_yard`` / ``.max_stockpile``). Removing only the setters
  closes the mutable-rebinding seam that F-A-004 cared about, while
  the read-only view keeps existing readers stable. PROJ-450 will
  refine the ``staging_yard`` getter's return type when widening the
  substrate; that is its concern, not PROJ-449's. See PROJ-449
  decisions.md row 2026-05-18 "Phase 3 scope adjustment".
"""
from __future__ import annotations

import game.strategy.data.planet as planet_module
from game.strategy.data.planet import Planet


def test_planet_module_has_no_legacy_kwargs_wrapper() -> None:
    """``planet`` module MUST NOT define ``_planet_init_with_legacy_kwargs``.

    PROJ-449 Phase 3 deletion guard. The PROJ-436 Phase 4f wrapper
    that translated public kwarg names is gone; ``Planet.__init__`` is
    the unmodified dataclass-generated ``__init__`` accepting only
    private (underscore-prefixed) field names.
    """
    assert not hasattr(planet_module, "_planet_init_with_legacy_kwargs"), (
        "planet module still defines `_planet_init_with_legacy_kwargs` "
        "(PROJ-449 Phase 3 deletion guard). The wrapper was retired; "
        "all callers must pass `_stockpile=` / `_max_stockpile=` / "
        "`_staging_yard=` directly."
    )


def _property_has_setter(cls: type, name: str) -> bool:
    """Return True iff ``cls.<name>`` is a descriptor with an ``fset``.

    Plain attributes and dataclass fields return False. Read-only
    ``@property`` accessors (no ``@setter``) return False.
    """
    descriptor = getattr(cls, name, None)
    if not isinstance(descriptor, property):
        return False
    return descriptor.fset is not None


def test_planet_stockpile_has_no_setter() -> None:
    """``Planet.stockpile`` MUST be read-only (no ``@setter``).

    PROJ-449 Phase 3 deletion guard. The setter shim that allowed
    ``planet.stockpile = {...}`` rebinding is gone. Writes route
    through ``add_to_stockpile`` / ``consume_from_stockpile`` /
    ``IPlanetMutator.set_stockpile_amount``.
    """
    assert not _property_has_setter(Planet, "stockpile"), (
        "Planet.stockpile still has an @setter "
        "(PROJ-449 Phase 3 deletion guard). The setter shim allowing "
        "`planet.stockpile = {...}` rebinding was retired."
    )


def test_planet_max_stockpile_has_no_setter() -> None:
    """``Planet.max_stockpile`` MUST be read-only (no ``@setter``).

    PROJ-449 Phase 3 deletion guard. Writes route through
    ``IPlanetMutator.set_max_stockpile``.
    """
    assert not _property_has_setter(Planet, "max_stockpile"), (
        "Planet.max_stockpile still has an @setter "
        "(PROJ-449 Phase 3 deletion guard)."
    )


def test_planet_staging_yard_has_no_setter() -> None:
    """``Planet.staging_yard`` MUST be read-only (no ``@setter``).

    PROJ-449 Phase 3 deletion guard. Writes route through
    ``add_to_staging_yard`` / ``remove_from_staging_yard`` /
    ``IPlanetMutator``. PROJ-450 will refine the getter's return type
    to a typed substrate; the absence of a setter is the durable
    contract.
    """
    assert not _property_has_setter(Planet, "staging_yard"), (
        "Planet.staging_yard still has an @setter "
        "(PROJ-449 Phase 3 deletion guard)."
    )
