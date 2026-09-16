"""
Mart 2023 Gerçek TUS Sınavı Soruları Ayıklama Motoru
Kaynak: ss/2023 Mart.pdf
Hedef: cikmis_sorular/virtual_db/questions_mart2023.json

İlkeler:
1. Kesinlikle PDF silinmez; yerel diskte doğrulamak üzere kalıcı kalır.
2. Sadece 5 şıkkı (A-E), soru kökü ve doğru cevabı eksiksiz olan kaliteli sorular Virtual DB'ye eklenir.
3. Açıklamalar temizlenir, telif uyarıları ve OCR gürültüleri ayıklanır.
4. TUS branşları (Anatomi, Fizyoloji, Biyokimya, vb.) ÖSYM soru numarası sırasına göre otomatik etiketlenir.
"""

import fitz
import sys
import re
import json
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).parent
PDF_PATH = BASE_DIR / "ss" / "2023 Mart.pdf"
OUTPUT_PATH = BASE_DIR / "cikmis_sorular" / "virtual_db" / "questions_mart2023.json"
MANIFEST_PATH = BASE_DIR / "cikmis_sorular" / "virtual_db" / "question_bank_manifest.json"

if not PDF_PATH.exists():
    print(f"HATA: PDF bulunamadı: {PDF_PATH}")
    sys.exit(1)

doc = fitz.open(PDF_PATH)
print(f"[Mart 2023] PDF açıldı: {len(doc)} sayfa.")

def get_subject_by_qnum(qnum):
    if 1 <= qnum <= 14:
        return "Anatomi"
    elif 15 <= qnum <= 22:
        return "Histoloji ve Embriyoloji"
    elif 23 <= qnum <= 32:
        return "Fizyoloji"
    elif 33 <= qnum <= 54:
        return "Biyokimya"
    elif 55 <= qnum <= 76:
        return "Mikrobiyoloji"
    elif 77 <= qnum <= 98:
        return "Patoloji"
    elif 99 <= qnum <= 120:
        return "Farmakoloji"
    elif 121 <= qnum <= 150:
        return "Dahiliye"
    elif 151 <= qnum <= 180:
        return "Pediatri"
    elif 181 <= qnum <= 205:
        return "Genel Cerrahi"
    elif 206 <= qnum <= 223:
        return "Kadın Hastalıkları ve Doğum"
    elif 224 <= qnum <= 240:
        return "Küçük Stajlar"
    return "TUS Mart 2023"

BLACKLIST_PHRASES = [
    "ASLA HELAL ETMiYORUZ", "kul hakkı", "yasal olmayan yollarla", "TUSDATA", 
    "bütün inançlar açısından", "hırsızlık yoluyla", "fotokopi",
    "tüm hakları saklıdır", "mülkiyet haklarına", "CamScanner ile", "TUS-DATA"
]

def clean_explanation_text(text):
    lines = []
    for l in text.split('\n'):
        l_strip = l.strip()
        if not l_strip:
            continue
        l_lower = l_strip.lower()
        if any(bp.lower() in l_lower for bp in BLACKLIST_PHRASES):
            break  # Usually copyright text is at the bottom of the page
        # Skip random OCR noise lines like '~~-.,~~•ıl•'
        if re.match(r'^[\~\-\.\,\•\:\'\"\_]+$', l_strip):
            continue
        if len(l_strip) <= 2 and not l_strip.isalnum():
            continue
        lines.append(l_strip)
    return "\n".join(lines).strip()

# Clean page stream
full_lines = []
for pno in range(len(doc)):
    txt = doc[pno].get_text()
    for raw_l in txt.split('\n'):
        l = raw_l.strip()
        if not l:
            continue
        if re.search(r'CamScanner\s+ile\s+taran', l, re.I):
            continue
        if re.search(r'N[İI]SAN\s*2023\s*TUS\s*SORULAR', l, re.I):
            continue
        if re.search(r'TUSDATA\b', l, re.I):
            continue
        full_lines.append((pno + 1, l))

def is_q_start(line, next_line=""):
    l = line.strip()
    if l.startswith("1e."):
        return 16, l[3:].strip()
    
    m = re.match(r'^(\d{1,3})\s*[\.\,\_\-]\s*(.*)$', l)
    if m:
        qnum = int(m.group(1))
        rest = m.group(2).strip()
        if 1 <= qnum <= 240:
            if not re.match(r'^(?:derece|gün|ay|yıl|hafta|saat|dakika|mg|ml|cm|mm|evresi|tip)\b', rest, re.I):
                return qnum, rest
                
    m_num = re.match(r'^(\d{1,3})$', l)
    if m_num and next_line:
        qnum = int(m_num.group(1))
        if 1 <= qnum <= 240:
            m_dot = re.match(r'^[\.\,\_\-]\s*([A-Za-zçğıöşüÇĞİÖŞÜ].*)$', next_line.strip())
            if m_dot:
                return qnum, m_dot.group(1).strip()
                
    return None, None

raw_starts = []
for i in range(len(full_lines)):
    pno, l = full_lines[i]
    next_l = full_lines[i+1][1] if i+1 < len(full_lines) else ""
    qnum, rest = is_q_start(l, next_l)
    if qnum is not None:
        raw_starts.append((i, qnum, pno, rest))

valid_starts = []
last_qnum = 0
for idx, qnum, pno, rest in raw_starts:
    if qnum > last_qnum and (qnum - last_qnum <= 15):
        valid_starts.append((idx, qnum, pno, rest))
        last_qnum = qnum

parsed_questions = []

OPT_REGEX = re.compile(r'^([A-Ea-e8Oo0Çç])\s*[\)\.\-]\s*(.*)$')
ANS_REGEX = re.compile(r'(?:Doğru\s*cevap|Dogru\s*cevap|Doğnı\s*cevap|Cevap)\s*[:=]?\s*([A-Ea-e])', re.I)

for k in range(len(valid_starts)):
    start_idx, qnum, start_pno, initial_stem = valid_starts[k]
    end_idx = valid_starts[k+1][0] if k + 1 < len(valid_starts) else min(start_idx + 80, len(full_lines))
    
    block_lines = full_lines[start_idx:end_idx]
    
    stem_parts = []
    if initial_stem:
        stem_parts.append(initial_stem)
        
    options = {}
    explanation_parts = []
    correct_answer = None
    
    current_opt = None
    found_any_opt = False
    in_explanation = False
    
    for line_offset, (pno, line_text) in enumerate(block_lines):
        if line_offset == 0 and initial_stem:
            continue
            
        ans_m = ANS_REGEX.search(line_text)
        if ans_m:
            correct_answer = ans_m.group(1).upper()
            
        opt_m = OPT_REGEX.match(line_text)
        if opt_m and not in_explanation:
            raw_letter = opt_m.group(1).upper()
            if raw_letter == '8':
                letter = 'B'
            elif raw_letter in ['Ç', 'C']:
                letter = 'C'
            elif raw_letter in ['O', '0', 'D']:
                letter = 'D'
            elif raw_letter in ['A', 'B', 'E']:
                letter = raw_letter
            else:
                letter = None
                
            if letter in ['A', 'B', 'C', 'D', 'E']:
                found_any_opt = True
                current_opt = letter
                options[current_opt] = opt_m.group(2).strip()
                continue
                
        if current_opt and not in_explanation:
            if 'E' in options and (len(options) >= 4 or opt_m is None):
                in_explanation = True
                explanation_parts.append(line_text)
                current_opt = None
            else:
                options[current_opt] = (options[current_opt] + " " + line_text).strip()
        elif in_explanation:
            explanation_parts.append(line_text)
        elif not found_any_opt:
            stem_parts.append(line_text)
            
    # Clean stem
    stem = " ".join(stem_parts).strip()
    stem = re.sub(r'^\d{1,3}\s*[\.\,\_\-]\s*', '', stem).strip()
    
    raw_explanation = "\n".join(explanation_parts).strip()
    explanation = clean_explanation_text(raw_explanation)
    
    if not correct_answer and explanation:
        ans_m = ANS_REGEX.search(explanation)
        if ans_m:
            correct_answer = ans_m.group(1).upper()
            
    has_opts = len(options) == 5 and all(opt in options for opt in ['A', 'B', 'C', 'D', 'E'])
    opts_valid = has_opts and all(len(v) >= 1 and not re.match(r'^[;\.,\:\-]+$', v) for v in options.values())
    
    if len(stem) > 20 and opts_valid and correct_answer:
        # Standardized question schema matching quiz.js
        parsed_questions.append({
            "id": f"mart2023_q{qnum}",
            "original_num": qnum,
            "exam": "Mart 2023 TUS",
            "period": "Mart 2023",
            "subject": get_subject_by_qnum(qnum),
            "topic": get_subject_by_qnum(qnum),
            "question": stem,
            "options": {k: options[k] for k in ['A', 'B', 'C', 'D', 'E']},
            "answer": correct_answer,
            "explanation": explanation
        })

print(f"[Mart 2023] {len(parsed_questions)} adet soru doğrulandı ve hazırlandı.")

# Save to questions_mart2023.json
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(parsed_questions, f, ensure_ascii=False, indent=2)
print(f"[Mart 2023] Kaydedildi: {OUTPUT_PATH}")

# Update question_bank_manifest.json
if MANIFEST_PATH.exists():
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
        manifest["subjects"]["mart2023"] = {
            "name": "Mart 2023 Gerçek TUS",
            "code": "mart2023",
            "file": "cikmis_sorular/virtual_db/questions_mart2023.json",
            "color": "#f59e0b",
            "icon": "🔥",
            "isExamEdition": True,
            "questionCount": len(parsed_questions),
            "categories": {
                "Temel Tıp Bilimleri": sum(1 for q in parsed_questions if q["original_num"] <= 120),
                "Klinik Tıp Bilimleri": sum(1 for q in parsed_questions if q["original_num"] > 120)
            }
        }
        
        # Recalculate total questions
        total_q = sum(s.get("questionCount", 0) for s in manifest["subjects"].values())
        manifest["totalQuestions"] = total_q
        manifest["summary"]["activeSubjects"] = sum(1 for s in manifest["subjects"].values() if s.get("questionCount", 0) > 0)
        manifest["summary"]["totalSubjects"] = len(manifest["subjects"])
        manifest["lastUpdated"] = str(Path(OUTPUT_PATH).stat().st_mtime)
        
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            
        print(f"[Manifest] Güncellendi! Toplam soru: {total_q}, Aktif branşlar: {manifest['summary']['activeSubjects']}")
    except Exception as e:
        print(f"[Manifest] Güncellenirken hata: {e}")
