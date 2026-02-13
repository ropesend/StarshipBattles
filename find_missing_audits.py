import os
import csv

csv_path = r'C:\Dev\Starship Battles\audit_results_C.csv'
simulation_dir = r'C:\Dev\Starship Battles\tests\unit\simulation'
strategy_dir = r'C:\Dev\Starship Battles\tests\unit\strategy'

audited_files = set()
if os.path.exists(csv_path):
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            audited_files.add(row['TestFilePath'].replace('/', '\\'))

all_tests = []
for root_dir in [simulation_dir, strategy_dir]:
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, r'C:\Dev\Starship Battles')
                all_tests.append(rel_path)

missing = [t for t in all_tests if t.replace('/', '\\') not in audited_files]
print("MISSING TESTS:")
for m in missing:
    print(m)
