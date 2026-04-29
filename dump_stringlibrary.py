#!/usr/bin/env python3
"""Dump StringLibrary MonoBehaviours from a bundle as raw typetree."""
import sys
import json
import UnityPy

bundle = sys.argv[1]
target_class = sys.argv[2] if len(sys.argv) > 2 else "StringLibrary"

env = UnityPy.load(bundle)

count = 0
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
        if cls != target_class:
            continue
    except Exception:
        continue
    count += 1
    name = getattr(data, "m_Name", "") or "<no-name>"
    print(f"\n=== Object #{count}: {cls} '{name}' (path_id={obj.path_id}) ===")
    try:
        tree = obj.read_typetree()
        print(json.dumps(tree, indent=2, ensure_ascii=False, default=str)[:8000])
    except Exception as e:
        print(f"typetree read failed: {e}")
        # fallback: try generic .read() and dir()
        attrs = [a for a in dir(data) if not a.startswith("_")]
        for a in attrs[:30]:
            try:
                v = getattr(data, a)
                if not callable(v):
                    print(f"  {a} = {str(v)[:200]}")
            except Exception:
                pass

print(f"\nTotal {target_class} found: {count}")
