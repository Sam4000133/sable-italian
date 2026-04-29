#!/usr/bin/env python3
"""Extract dialog strings from Sable's Ink narrative file.

Ink JSON format: nested arrays where strings prefixed with "^" are content text.
We walk recursively and capture each string with its JSON-pointer-like path so
we can later re-inject translated text at the same locations.
"""
import json
import csv
import sys

src = sys.argv[1] if len(sys.argv) > 1 else 'extracted/sable.bin'

with open(src, encoding='utf-8-sig') as f:
    data = json.load(f)

results = []  # (path_str, original_text)

def walk(node, path):
    if isinstance(node, str):
        if node.startswith('^') and len(node) > 1:
            text = node[1:]
            if text.strip():
                results.append(('/'.join(str(p) for p in path), text))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + (i,))
    elif isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + (k,))

walk(data['root'], ('root',))

print(f"Extracted {len(results)} narrative strings")
print(f"Unique strings: {len(set(t for _, t in results))}")

# Write CSV with: path, en, it (empty)
with open('translations/ink_strings.csv', 'w', newline='', encoding='utf-8') as out:
    w = csv.writer(out, quoting=csv.QUOTE_ALL)
    w.writerow(['path', 'en', 'it'])
    for path, text in results:
        w.writerow([path, text, ''])
print("Wrote translations/ink_strings.csv")

# Stats
lengths = [len(t) for _, t in results]
print(f"\nLength stats: min={min(lengths)} max={max(lengths)} avg={sum(lengths)/len(lengths):.0f}")
print(f"Total chars: {sum(lengths):,}")
