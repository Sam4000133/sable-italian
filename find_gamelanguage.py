#!/usr/bin/env python3
"""Find the GameLanguage asset across all bundles."""
import sys
import glob
import os
import UnityPy

bundle_dir = sys.argv[1]
target = sys.argv[2] if len(sys.argv) > 2 else "GameLanguage"

bundles = sorted(glob.glob(os.path.join(bundle_dir, "*.bundle")))
print(f"Scanning {len(bundles)} bundles for class containing '{target}'...\n")

for bundle in bundles:
    try:
        env = UnityPy.load(bundle)
    except Exception:
        continue
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            data = obj.read()
            script = getattr(data, "m_Script", None)
            cls = ""
            if script:
                try:
                    s = script.read()
                    cls = getattr(s, "m_ClassName", "")
                except Exception:
                    pass
            if target in cls:
                name = getattr(data, "m_Name", "") or "<no-name>"
                print(f"  {os.path.basename(bundle)} :: [{cls}] {name} (path_id={obj.path_id})")
        except Exception:
            pass
