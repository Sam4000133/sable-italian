#!/usr/bin/env python3
"""Parse Cpp2IL method dump to extract property → English string mapping.

The pseudocode section contains entries like:
    System.String get_ClothingScreen_Name()
        return "Clothing"
"""
import re
import csv
import sys

src = sys.argv[1]
text = open(src, encoding='utf-8', errors='replace').read()

# Pattern: System.String get_X()\n\t\treturn "Y" — capture the property and string
pat = re.compile(
    r'System\.String get_(\w+)\(\)\s*\n\s*return "((?:[^"\\]|\\.)*)"',
    re.M
)
results = []
for m in pat.finditer(text):
    prop, val = m.group(1), m.group(2)
    # Unescape common sequences
    val = val.encode('utf-8').decode('unicode_escape')
    results.append((prop, val))

# Dedup by property (keep first occurrence)
seen = {}
for prop, val in results:
    if prop not in seen:
        seen[prop] = val

print(f"Extracted {len(seen)} unique property→string mappings (from {len(results)} hits)")

# Write CSV
out_path = sys.argv[2] if len(sys.argv) > 2 else 'en_strings.csv'
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(['property', 'en'])
    for prop in sorted(seen):
        w.writerow([prop, seen[prop]])
print(f"Wrote {out_path}")

# Show menu/title sample
sample_keys = [k for k in seen if k.startswith(('TitleScreen_', 'SettingsScreen_', 'ButtonPrompt_', 'MapScreen_'))]
print(f"\nSample menu/UI strings ({len(sample_keys)}):")
for k in sorted(sample_keys)[:25]:
    print(f"  {k}: {seen[k]!r}")
