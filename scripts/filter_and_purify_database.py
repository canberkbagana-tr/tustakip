"""
TUS Soru Tabanı Evrensel Kalite Filtresi ve Arındırma Motoru (v2.0)
Konum: scripts/filter_and_purify_database.py

Tüm virtual_db/questions_*.json dosyalarını denetler, 5 aşamalı kalite kapısını uygular,
hatalı şıkları ve bozuk soru köklerini ayıklar, manifest'i otomatik günceller.
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
MANIFEST_PATH = VIRTUAL_DB / "question_bank_manifest.json"

def clean_ocr(text):
    if not text:
        return ""
    text = re.sub(r'\(\s*o\s*', ' ', text)
    text = re.sub(r'\(o\b', ' ', text)
    text = re.sub(r'\s*©\s*', ' ', text)
    text = re.sub(r'\(ee\b', ' ', text)
    text = re.sub(r'\(\s+([a-zA-ZçğıöşüÇĞİÖŞÜ0-9])', r'\1', text)
    text = re.sub(r'\(\s*([a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+)\s*\(', r'\1 ', text)
    text = re.sub(r'^[\s\)\:\-\*]+', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

files = sorted(glob.glob(str(VIRTUAL_DB / "questions_*.json")))
total_before = 0
total_after = 0
purged_log = []

for fpath in files:
    book_code = Path(fpath).stem.replace("questions_", "")
    with open(fpath, "r", encoding="utf-8") as f:
        questions = json.load(f)

    total_before += len(questions)
    valid_pool = []

    for q in questions:
        qtext = clean_ocr(q.get("question", ""))
        expl = clean_ocr(q.get("explanation", ""))
        raw_opts = q.get("options", {})
        opts = {k: clean_ocr(v) for k, v in raw_opts.items()}
        ans = q.get("answer", "")

        # Validation Rule 1: Question Stem length
        if len(qtext.strip()) < 20:
            purged_log.append((q.get("id"), "Question stem too short (<20 chars)", qtext))
            continue

        # Validation Rule 2: Must have at least 4 options and valid answer key
        if len(opts) < 4 or not ans or ans not in opts:
            purged_log.append((q.get("id"), "Missing options or invalid answer key", qtext[:60]))
            continue

        # Validation Rule 3: No empty/junk single-char options (like Option A: ";")
        has_junk_opt = False
        for k, v in opts.items():
            if len(v.strip()) <= 1 or v.strip() in [";", ".", "-", ":", "_", "/", "\\"]:
                has_junk_opt = True
                break
        if has_junk_opt:
            purged_log.append((q.get("id"), "Junk/empty option", str(opts)))
            continue

        # Validation Rule 4: Roman numeral premise consistency
        opt_has_roman = any(v.lower().startswith("yalnız") or re.search(r"\b[iI|ıIİ]{1,3}\s*ve\b", v) for v in opts.values())
        stem_has_roman = bool(re.search(r"\b(I|II|III|IV|V)\.", qtext) or re.search(r"\b(1|2|3)\.\s", qtext))
        if opt_has_roman and not stem_has_roman:
            purged_log.append((q.get("id"), "Roman numeral premise missing in stem", qtext[:60]))
            continue

        # Validation Rule 5: Swap repair
        m_alt = re.search(r'\(?Not:\s*Bu\s*soru[^\)]*şöyle\s*de?\s*sorulabilirdi[:\)]?\s*([^\?\n\r]+\?)', expl, re.IGNORECASE)
        if m_alt:
            alt_q = m_alt.group(1).strip()
            ans_text = opts.get(ans, "")
            if ans_text and len(ans_text) > 3 and re.search(r'\b' + re.escape(ans_text) + r'\b', qtext, re.IGNORECASE):
                if not re.search(r'\b' + re.escape(ans_text) + r'\b', alt_q, re.IGNORECASE):
                    clean_alt = clean_ocr(alt_q)
                    expl = expl.replace(m_alt.group(0), f"Bu soru şöyle de sorulabilirdi: {qtext}")
                    qtext = clean_alt

        valid_pool.append({
            **q,
            "question": qtext,
            "options": opts,
            "explanation": expl
        })

    total_after += len(valid_pool)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(valid_pool, f, ensure_ascii=False, indent=2)

    print(f"[{book_code.upper()}] Önce: {len(questions)} -> Sonra: {len(valid_pool)} (Elenen: {len(questions) - len(valid_pool)})")

# Update Manifest
if MANIFEST_PATH.exists():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for fpath in files:
        bcode = Path(fpath).stem.replace("questions_", "")
        with open(fpath, "r", encoding="utf-8") as f:
            qs = json.load(f)
        if bcode in manifest["subjects"]:
            manifest["subjects"][bcode]["questionCount"] = len(qs)

    manifest["totalQuestions"] = sum(s.get("questionCount", 0) for s in manifest["subjects"].values())
    manifest["summary"]["activeSubjects"] = sum(1 for s in manifest["subjects"].values() if s.get("questionCount", 0) > 0)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

print("\n================ ÖZET ================")
print(f"Toplam Başlangıç Sorusu: {total_before}")
print(f"Toplam Onaylanan Soru  : {total_after}")
print(f"Arındırılan/Elenen Soru : {len(purged_log)}")
print(f"Güncel Manifest Toplamı: {manifest.get('totalQuestions')}")
