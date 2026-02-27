import os
import re
from collections import defaultdict

count_per_file = defaultdict(int)
total = 0
matches = defaultdict(list)
pattern = re.compile(r'\b(hasattr|getattr)\b')

search_dir = r'c:\Dev\Starship Battles\game'

for root, dirs, files in os.walk(search_dir):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    for i, line in enumerate(file):
                        if pattern.search(line):
                            count_per_file[path] += 1
                            total += 1
                            matches[path].append(f'  L{i+1}: {line.strip()[:150]}')
            except Exception as e:
                pass

sorted_files = sorted(count_per_file.items(), key=lambda x: x[1], reverse=True)
print(f'Total instances: {total}')
for f, c in sorted_files:
    rel_path = os.path.relpath(f, search_dir)
    print(f'\n{rel_path}: {c} instances')
    for m in matches[f]:
        print(m)
