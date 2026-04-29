#!/usr/bin/env python3
"""Scan bundles for Unity Localization StringTable assets."""
import sys
import glob
import os
import UnityPy

bundle_dir = sys.argv[1]
filter_kw = sys.argv[2] if len(sys.argv) > 2 else None

bundles = sorted(glob.glob(os.path.join(bundle_dir, "*.bundle")))
if filter_kw:
    bundles = [b for b in bundles if filter_kw in os.path.basename(b)]

print(f"Scanning {len(bundles)} bundles for StringTable / TextAsset / Localization assets...\n")

for bundle in bundles:
    try:
        env = UnityPy.load(bundle)
    except Exception as e:
        print(f"  [skip] {os.path.basename(bundle)} — {e}")
        continue
    hits = []
    for obj in env.objects:
        if obj.type.name in ("MonoBehaviour",):
            try:
                data = obj.read()
                script = getattr(data, "m_Script", None)
                script_name = ""
                if script:
                    try:
                        s = script.read()
                        script_name = getattr(s, "m_ClassName", "") or getattr(s, "name", "")
                    except Exception:
                        pass
                name = getattr(data, "m_Name", "") or "<no-name>"
                if any(k in script_name for k in ("String", "Localiz", "Table", "Asset")):
                    hits.append((script_name, name))
            except Exception:
                pass
        elif obj.type.name == "TextAsset":
            try:
                data = obj.read()
                name = getattr(data, "m_Name", "") or "<no-name>"
                hits.append(("TextAsset", name))
            except Exception:
                pass
    if hits:
        print(f"\n=== {os.path.basename(bundle)} ===")
        for script, name in hits:
            print(f"  [{script}] {name}")
