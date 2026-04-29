#!/usr/bin/env python3
"""Extract all property keys from the abstract TextProvider class in dump.cs.

The abstract class lists every UI string slot the game uses. We capture them
with their RVAs so we can later read the binary to recover values.
"""
import re
import sys

dump = open('il2cpp_dump/dump.cs').read()

# Find the TextProvider_EN class block
m = re.search(r'public class TextProvider_EN : TextProvider.*?(?=\npublic |\Z)', dump, re.S)
if not m:
    sys.exit("TextProvider_EN block not found")
block = m.group(0)

# Each getter is preceded by an RVA comment
pat = re.compile(
    r'// RVA: (0x[0-9A-Fa-f]+) Offset: (0x[0-9A-Fa-f]+) VA: (0x[0-9A-Fa-f]+)[^\n]*\n'
    r'\s+public override string (get_\w+)\(\) \{ \}'
)
entries = pat.findall(block)
print(f"Extracted {len(entries)} EN getter entries")

# Dedup by property name (some generated funcs may repeat)
import csv
out = open('en_provider_keys.csv', 'w', newline='', encoding='utf-8')
w = csv.writer(out)
w.writerow(['property', 'rva', 'offset', 'va'])
seen = set()
for rva, off, va, name in entries:
    prop = name[len('get_'):]
    if prop in seen: continue
    seen.add(prop)
    w.writerow([prop, rva, off, va])
out.close()
print(f"Wrote en_provider_keys.csv ({len(seen)} unique properties)")
