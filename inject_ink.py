#!/usr/bin/env python3
"""Build a translated copy of sable.bin by walking the Ink AST and substituting
strings whose EN value has an IT translation in the CSV.

Strings that don't have an IT translation are left as EN (graceful fallback).
"""
import json
import csv
import sys

src_ink = sys.argv[1] if len(sys.argv) > 1 else 'extracted/sable.bin'
csv_path = sys.argv[2] if len(sys.argv) > 2 else 'translations/ink_strings.csv'
out_ink = sys.argv[3] if len(sys.argv) > 3 else 'translations/sable_it.bin'

# Load EN→IT map (path-agnostic; one EN string maps to one IT translation, last wins)
en_to_it = {}
translated = 0
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        en, it = r['en'], r['it']
        if it.strip():
            en_to_it[en] = it
            translated += 1
print(f"EN→IT pairs in CSV: {translated} (unique EN: {len(en_to_it)})")

# Load Ink JSON
with open(src_ink, encoding='utf-8-sig') as f:
    data = json.load(f)

substitutions = 0
def walk(node):
    global substitutions
    if isinstance(node, list):
        for i in range(len(node)):
            v = node[i]
            if isinstance(v, str) and v.startswith('^') and len(v) > 1:
                en = v[1:]
                if en in en_to_it:
                    node[i] = '^' + en_to_it[en]
                    substitutions += 1
            else:
                walk(v)
    elif isinstance(node, dict):
        for k in node:
            walk(node[k])

walk(data['root'])
print(f"Substitutions made in AST: {substitutions}")

# Re-serialize. The Ink format uses UTF-8 with BOM; we mirror that.
with open(out_ink, 'w', encoding='utf-8') as f:
    f.write('﻿')  # BOM
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

import os
print(f"Wrote {out_ink} ({os.path.getsize(out_ink):,} bytes)")
