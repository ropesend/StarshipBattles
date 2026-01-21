#!/usr/bin/env python3
"""Check TestRegistry discovery of resource scenarios."""

from test_framework.registry import TestRegistry

# Create registry
r = TestRegistry()

print(f'Total scenarios: {len(r.scenarios)}')
print()

# Get resource tests
resource_tests = r.get_by_category('Resource System')
print(f'Resource System tests: {len(resource_tests)}')
for test_id in sorted(resource_tests.keys()):
    metadata = resource_tests[test_id]['metadata']
    print(f'  - {test_id}: {metadata.name}')

print()

# Show all categories
categories = r.get_categories()
print(f'All categories: {categories}')
