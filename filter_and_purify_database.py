import json
import re
import sys
import glob
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

MANIFEST_PATH = Path("cikmis_sorular/virtual_db/question_bank_manifest.json")
VIRTUAL_DB = Path("cikmis_sorular/virtual_db")

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

files = sorted(glob.glob("cikmis_sorular/virtual_db/questions_*.json"))
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
        if len(qtext.strip()) < 25:
            purged_log.append((q.get("id"), "Question stem too short (<25 chars)", qtext))
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
            purged_log.append((q.get("id"), "Junk/empty option text", qtext[:60]))
            continue

        # Validation Rule 4: Roman numeral mismatch (premisses missing in stem)
        opt_has_roman = any(v.lower().startswith("yalnız") or re.search(r"\b[iI|ıIİ]{1,3}\s*ve\b", v) for v in opts.values())
        stem_has_roman = bool(re.search(r"\b(I|II|III|IV|V)\.", qtext) or re.search(r"\b(1|2|3)\.\s", qtext))
        if opt_has_roman and not stem_has_roman:
            purged_log.append((q.get("id"), "Premises missing in stem (Roman numeral options)", qtext[:60]))
            continue

        # Validation Rule 5: Swap check if alt question exists
        m_alt = re.search(r'\(?Not:\s*Bu\s*soru[^\)]*şöyle\s*de?\s*sorulabilirdi[:\)]?\s*([^\?\n\r]+\?)', expl, re.IGNORECASE)
        ans_text = opts.get(ans, "")
        if m_alt:
            alt_q = m_alt.group(1).strip()
            if ans_text and len(ans_text) > 3 and re.search(r'\b' + re.escape(ans_text) + r'\b', qtext, re.IGNORECASE):
                if not re.search(r'\b' + re.escape(ans_text) + r'\b', alt_q, re.IGNORECASE):
                    clean_alt = re.sub(r'^[\s\)\:\-\*]+', '', alt_q).strip()
                    new_alt = f"(Not: Bu soru, başka bir hoca tarafından şöyle de sorulabilirdi:) {qtext}"
                    expl = expl.replace(m_alt.group(0), new_alt)
                    qtext = clean_alt

        q["question"] = qtext
        q["explanation"] = expl
        q["options"] = opts
        valid_pool.append(q)

    # Re-index IDs cleanly
    for idx, q in enumerate(valid_pool, 1):
        q["id"] = f"{book_code}_q{idx}"

    total_after += len(valid_pool)

    # Write back clean JSON
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(valid_pool, f, ensure_ascii=False, indent=2)

    print(f"📦 {book_code.capitalize()}: {len(questions)} -> {len(valid_pool)} soru (Temizlendi & Doğrulandı)")

# Update Manifest
if MANIFEST_PATH.exists():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    total_manifest_q = 0
    active_manifest_s = 0
    for fpath in files:
        book_code = Path(fpath).stem.replace("questions_", "")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data)
        total_manifest_q += count
        if count > 0:
            active_manifest_s += 1
        if book_code in manifest.get("subjects", {}):
            manifest["subjects"][book_code]["questionCount"] = count
    
    manifest["totalQuestions"] = total_manifest_q
    if "summary" in manifest:
        manifest["summary"]["activeSubjects"] = active_manifest_s
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"\n==========================================")
print(f"🎉 KALİTE VE TEMİZLİK FİLTRESİ TAMAMLANDI")
print(f"Önceki Havuz: {total_before} soru")
print(f"Doğrulanmış Kusursuz Havuz: {total_after} soru")
print(f"Elenen/Düzeltilen Hatalı Soru: {len(purged_log)} soru")
print(f"==========================================")

with open("scratch_quality_purge_log.txt", "w", encoding="utf-8") as f:
    for item in purged_log:
        f.write(f"{item[0]} | {item[1]} | {item[2]}\n")
