#!/usr/bin/env python3
"""Dump all MonoBehaviour script class names from a bundle."""
import sys
from collections import Counter
import UnityPy

bundle = sys.argv[1]
env = UnityPy.load(bundle)

scripts = Counter()
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        try:
            data = obj.read()
            script = getattr(data, "m_Script", None)
            class_name = "<unknown>"
            if script:
                try:
                    s = script.read()
                    class_name = getattr(s, "m_ClassName", "") or "<no-class>"
                except Exception:
                    pass
            scripts[class_name] += 1
        except Exception:
            scripts["<read-error>"] += 1

print(f"Bundle: {bundle.split('/')[-1]}")
print(f"MonoBehaviour total: {sum(scripts.values())}\n")
for cls, count in scripts.most_common():
    print(f"  {count:>5}  {cls}")
