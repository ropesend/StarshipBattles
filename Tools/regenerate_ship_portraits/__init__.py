"""Ship-portrait regeneration tool (PROJ-314).

CLI driver and audit utility for backfilling missing ship portraits via
``gpt-image-2`` through :class:`game.ui.services.image.ImageProvider`.

Entry points:

* :mod:`cli` — main CLI (``python -m Tools.regenerate_ship_portraits.cli``).
* :mod:`audit` — non-destructive coverage/casing/size audit.
"""
