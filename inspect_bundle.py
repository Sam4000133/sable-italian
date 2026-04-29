#!/usr/bin/env python3
"""Inspect a Unity bundle: list object types and counts."""
import sys
from collections import Counter
import UnityPy

bundle = sys.argv[1]
env = UnityPy.load(bundle)

types = Counter()
samples = {}
for obj in env.objects:
    types[obj.type.name] += 1
    if obj.type.name not in samples:
        try:
            data = obj.read()
            name = getattr(data, "m_Name", None) or getattr(data, "name", None) or "<no-name>"
            samples[obj.type.name] = str(name)[:80]
        except Exception as e:
            samples[obj.type.name] = f"<read-error: {e}>"

print(f"Bundle: {bundle}")
print(f"Total objects: {sum(types.values())}\n")
print(f"{'Type':<30} {'Count':>6}  Sample name")
print("-" * 80)
for t, c in types.most_common():
    print(f"{t:<30} {c:>6}  {samples.get(t, '')}")
