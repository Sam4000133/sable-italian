#!/usr/bin/env python3
"""Extract TextMeshPro text content from a bundle.

Sable uses TMP_Text MonoBehaviours. The text lives in the typetree field
'm_text' (TMPro) or 'm_Text' (UGUI Text).
"""
import sys
import json
import UnityPy

bundle = sys.argv[1]
env = UnityPy.load(bundle)

results = []
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    try:
        tree = obj.read_typetree()
    except Exception:
        continue
    text = tree.get("m_text") or tree.get("m_Text")
    if not text or not isinstance(text, str) or not text.strip():
        continue
    # Resolve owning GameObject name if possible
    go_name = ""
    go_ref = tree.get("m_GameObject", {})
    if isinstance(go_ref, dict) and go_ref.get("m_PathID"):
        try:
            go_obj = env.get(go_ref["m_PathID"])
            if go_obj:
                go_data = go_obj.read()
                go_name = getattr(go_data, "m_Name", "") or ""
        except Exception:
            pass
    # Resolve script class name
    cls = ""
    script_ref = tree.get("m_Script", {})
    if isinstance(script_ref, dict) and script_ref.get("m_PathID"):
        try:
            s_obj = env.get(script_ref["m_PathID"])
            if s_obj:
                s_data = s_obj.read()
                cls = getattr(s_data, "m_ClassName", "") or ""
        except Exception:
            pass
    results.append({
        "path_id": obj.path_id,
        "class": cls,
        "go": go_name,
        "text": text,
    })

print(f"Bundle: {bundle.split('/')[-1]}")
print(f"Found {len(results)} text entries\n")
for r in results:
    text_oneline = r["text"].replace("\n", "\\n")[:200]
    print(f"[{r['class']}] go='{r['go']}' :: {text_oneline}")
