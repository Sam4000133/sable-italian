#!/usr/bin/env python3
"""Extract all items from _ItemDatabase JSON with their EN texts."""
import json
import csv

with open('extracted/_ItemDatabase.bin', encoding='utf-8-sig') as f:
    items = json.load(f)

# Filter to items that have real EN content (non-placeholder)
def is_real(it):
    n = it.get('Name_EN', '') or ''
    d = it.get('Description_EN', '') or ''
    return n.strip() and n.strip().lower() != 'name'

real = [it for it in items if is_real(it)]
print(f"Items with real EN content: {len(real)} / {len(items)}")

with open('translations/items_en.csv', 'w', newline='', encoding='utf-8') as out:
    w = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    w.writerow(['Name', 'Category', 'Rarity', 'Name_EN', 'Description_EN', 'ShopDescription_EN'])
    for it in real:
        w.writerow([
            it.get('Name', ''),
            it.get('Category', ''),
            it.get('Rarity', ''),
            it.get('Name_EN', ''),
            it.get('Description_EN', ''),
            it.get('ShopDescription_EN', ''),
        ])
print("Wrote translations/items_en.csv")

# Group by category
by_cat = {}
for it in real:
    by_cat.setdefault(it.get('Category', 'Unknown'), []).append(it)
print(f"\nBy category:")
for cat, lst in sorted(by_cat.items(), key=lambda x: -len(x[1])):
    print(f"  {cat:20} {len(lst):>3}")
