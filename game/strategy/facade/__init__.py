"""Strategy Session Facade module.

Provides a strict facade for UI-to-engine communication using CQRS-lite pattern.
All state mutations go through Commands, all reads return immutable DTOs.
"""
