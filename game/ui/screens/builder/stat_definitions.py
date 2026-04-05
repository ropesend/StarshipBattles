"""StatDefinition class for declarative stat display configuration.

Each stat row in the ship builder UI is described by a StatDefinition that maps
a label to a ship attribute (via dynamic lookup or callable getter), with
optional formatting, unit display, and validation.
"""


class StatDefinition:
    """
    Defines a single stat row for the ship builder UI.

    INTENTIONAL DYNAMIC DISPATCH PATTERN:
    The `get_value()` method uses `getattr(ship, self.attr_key, 0)` intentionally.
    This is the core mechanism for declaratively mapping stat names to ship attributes
    via JSON configuration (stats_layout.json). The attr_key is a runtime string that
    cannot be replaced with typed access.

    DO NOT refactor get_value() to use direct attribute access - it must remain dynamic.
    """

    def __init__(self, id, label, key=None, getter=None, formatter="{:.0f}", unit="", validator=None):
        self.key = id  # Unique ID for the row map
        self.attr_key = key if key is not None else id  # Attribute on ship object
        self.label = label
        self.getter = getter
        self.formatter = formatter
        self.unit = unit
        self.validator = validator  # func(ship, value) -> (is_ok, status_text)

    def get_value(self, ship):
        """Get stat value from ship using configured getter or dynamic attr lookup."""
        if self.getter:
            if callable(self.getter):
                return self.getter(ship)
            return getattr(ship, self.getter, 0)
        # INTENTIONAL: Dynamic attribute lookup - see class docstring
        return getattr(ship, self.attr_key, 0)

    def format_value(self, val):
        if callable(self.formatter):
            return self.formatter(val)
        return self.formatter.format(val)

    def get_display_unit(self, ship, val):
        if callable(self.unit):
            return self.unit(ship, val)
        return self.unit

    def get_status(self, ship, val):
        if self.validator:
            return self.validator(ship, val)
        return (True, "")
