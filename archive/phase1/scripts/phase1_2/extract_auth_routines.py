# -*- coding: utf-8 -*-
"""Phase 1.2 - Extract authorization-related routine/trigger definitions from the catalog snapshot."""
import json, os
inv = json.load(open(r"artifacts\database-discovery\schema_inventory.json", encoding="utf-8"))
out = []
r0 = inv.get("routines", [])[0]
out.append("ROUTINE KEYS: " + str(list(r0.keys()) if isinstance(r0, dict) else type(r0)))
for r in inv.get("routines", []):
    if isinstance(r, dict) and r.get("routine_name") in ("check_user_permission", "get_user_menu_actions", "get_user_menus"):
        out.append("=" * 80)
        out.append(json.dumps(r, indent=1, ensure_ascii=False))
out.append("=" * 80 + "\nTRIGGERS:")
for t in inv.get("triggers", []):
    out.append(json.dumps(t, ensure_ascii=False)[:400])
os.makedirs(r"artifacts\phase1_2", exist_ok=True)
open(r"artifacts\phase1_2\auth_routines.txt", "w", encoding="utf-8").write("\n".join(out))
print("written", len(out))
