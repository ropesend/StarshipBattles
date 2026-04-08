"""
Test Framework

Framework for running automated tests on the combat simulation system.
Provides scenario registration, test execution, and result tracking.
"""

from .registry import TestRegistry
from .test_history import TestHistory
from .runner import TestRunner
from .scenario import CombatScenario

__all__ = [
    'TestRegistry',
    'TestHistory',
    'TestRunner',
    'CombatScenario'
]
