# PROJ-382 Phase 2: this package's public surface lives in submodules
# (e.g. ``game.simulation.components.component``,
# ``game.simulation.components.abilities``). The empty __init__.py is an
# intentional namespace marker — it does NOT re-export. Importers should
# reach into the submodule that owns the class they need.
