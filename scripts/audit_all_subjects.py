"""
TUS Soru Tabanı Hızlı Denetim Aracı
Konum: scripts/audit_all_subjects.py
"""

import json
import re
import sys
import glob
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
VIRTUAL_DB = BASE_DIR / "cikmis_sorular" / "virtual_db"

files = sorted(glob.glob(str(VIRTUAL_DB / "questions_*.json")))
report = {}

for fpath in files:
    name = Path(fpath).stem
    with open(fpath, "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    bad_options = 0
    short_q = 0
    roman_mismatch = 0
    clean_q = 0

    for q in questions:
        qtext = q.get("question", "")
        options = q.get("options", {})
        
        has_bad_opt = False
        for k, v in options.items():
            if len(v.strip()) <= 1 or v.strip() in [";", ".", "-", ":"]:
                has_bad_opt = True
        
        opt_has_roman = any("yalnız" in v.lower() or re.search(r"\b[iI|ıIİ]{1,3}\s*ve\b", v) for v in options.values())
        stem_has_roman = bool(re.search(r"\b(I|II|III|IV|V)\.", qtext))
        is_roman_mismatch = opt_has_roman and not stem_has_roman

        if len(qtext.strip()) < 20:
            short_q += 1
        elif has_bad_opt:
            bad_options += 1
        elif is_roman_mismatch:
            roman_mismatch += 1
        else:
            clean_q += 1

    report[name] = {
        "total": len(questions),
        "clean": clean_q,
        "bad_options": bad_options,
        "short_q": short_q,
        "roman_mismatch": roman_mismatch
    }

print(json.dumps(report, ensure_ascii=False, indent=2))
