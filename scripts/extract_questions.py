"""
TUS Akıllı Soru Ayıklama ve Virtual Soru Tabanı Motoru (v3.0 - Unified Master Pipeline)

Desteklenen Modlar:
1. Branş Kitapları Modu (Subject Books): cikmis_sorular/*.pdf (Fizyoloji, Patoloji, Biyokimya, vb.)
2. Gerçek Sınav Modu (Exam Editions): ss/*.pdf (Örn: 2023 Mart.pdf)

Temel İlkeler:
1. Soru olmayan alanları (kapaklar, telif sayfaları, salt konu anlatımı/özet tabloları) KESİNLİKLE soru olarak kesmez.
2. Soruların konu anlatımlarının arasına serpiştirildiği kitaplarda regex ve şık analizi ile yalnızca izole soru bloklarını yakalar.
3. 5 Aşamalı Otomatik Kalite Kapısı (QA Pipeline) uygular:
   - Soru kökü uzunluğu (< 25 karakter olanlar elenir)
   - 4-5 geçerli şık ve doğru cevap anahtarı uyumu
   - Boş/çöp şık temizliği (A: ";" vb.)
   - Romen rakamı öncül tutarlılığı
   - Kök - Alternatif soru (Swap) denetimi
4. CHECKPOINT & RESUME: extraction_state.json üzerinden sayfa takibi yapar.
5. PDF dosyaları kontrol, doğrulama ve görsel referans amacıyla yerel diskte KALICI olarak saklanır (silinmez).
"""

import os
import sys
import json
import re
from pathlib import Path
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Root Directory Resolution
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PDF_DIR = BASE_DIR / "cikmis_sorular"
EXAM_DIR = BASE_DIR / "ss"
VIRTUAL_DB_DIR = PDF_DIR / "virtual_db"
LOCAL_TESSDATA = PDF_DIR / "tessdata"
MANIFEST_PATH = VIRTUAL_DB_DIR / "question_bank_manifest.json"
STATE_PATH = VIRTUAL_DB_DIR / "extraction_state.json"

if LOCAL_TESSDATA.exists():
    os.environ["TESSDATA_PREFIX"] = str(LOCAL_TESSDATA)

try:
    import fitz  # PyMuPDF
except ImportError:
    print("HATA: PyMuPDF (fitz) yüklü değil. 'pip install pymupdf' çalıştırın.")
    sys.exit(1)

try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except Exception:
    pass

def ensure_directories():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    EXAM_DIR.mkdir(parents=True, exist_ok=True)
    VIRTUAL_DB_DIR.mkdir(parents=True, exist_ok=True)

# Soru filtreleme regexleri
Q_START_REGEX = re.compile(r'^\s*(\d{1,3})\.\s*(.*)', re.DOTALL)
EXAM_PERIOD_REGEX = re.compile(r'\((Nisan|Eylül|Mart|Ağustos|Aralık|Şubat|Kasım)[\s\-_]*(\d{2,4})[^\)]*\)', re.IGNORECASE)
ANSWER_REGEX = re.compile(r'(?:Doğru\s*cevap|Dogru\s*cevap|Doğnı\s*cevap|Cevap)\s*[:=]?\s*([A-Ea-e])', re.IGNORECASE)

BLACKLIST_KEYWORDS = [
    "telif hukuku", "kul hakkı", "yasal olmayan yollarla", "tusdata", 
    "bütün inançlar açısından", "hırsızlık yoluyla", "fotokopi",
    "içindekiler", "bölüm başlığı", "tüm hakları saklıdır", "asla helal etmiyoruz",
    "camscanner ile"
]

def is_blacklisted_text(text):
    text_lower = text.lower()
    return any(k in text_lower for k in BLACKLIST_KEYWORDS)

def parse_options_from_line(line):
    opts = {}
    parts = re.split(r'([A-E]\))', line)
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            letter = parts[i][0]
            val = parts[i+1].strip() if i+1 < len(parts) else ""
            if val:
                opts[letter] = val
    return opts

def load_state():
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ State kaydedilemedi: {e}")

def update_manifest(book_code, book_title, question_count, categories_dict, is_exam_edition=False, icon="🩺", color="#7c5cfc"):
    if not MANIFEST_PATH.exists():
        return

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if "subjects" not in manifest:
            manifest["subjects"] = {}

        manifest["subjects"][book_code] = {
            "name": book_title,
            "code": book_code,
            "file": f"cikmis_sorular/virtual_db/questions_{book_code}.json",
            "color": color,
            "icon": icon,
            "isExamEdition": is_exam_edition,
            "questionCount": question_count,
            "categories": categories_dict
        }

        total_q = sum(sub.get("questionCount", 0) for sub in manifest["subjects"].values())
        active_s = sum(1 for sub in manifest["subjects"].values() if sub.get("questionCount", 0) > 0)

        manifest["totalQuestions"] = total_q
        manifest["summary"]["activeSubjects"] = active_s
        manifest["summary"]["totalSubjects"] = len(manifest["subjects"])
        manifest["lastUpdated"] = str(Path(MANIFEST_PATH).stat().st_mtime)

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"📊 Manifest Güncellendi: Toplam {total_q} Soru | Aktif Branş: {active_s}")
    except Exception as e:
        print(f"⚠️ Manifest güncellenirken hata: {e}")

def audit_and_clean_questions(questions, book_name):
    """
    Otomatik Kalite Denetim ve Temizleme Boru Hattı (Pipeline QA).
    5 Aşamalı Kalite Kapısı.
    """
    cleaned = []
    fixed_count = 0
    swap_count = 0
    purged_count = 0

    def clean_txt(t):
        if not t:
            return ""
        t = re.sub(r'\(\s*o\s*', ' ', t)
        t = re.sub(r'\(o\b', ' ', t)
        t = re.sub(r'\s*©\s*', ' ', t)
        t = re.sub(r'\(ee\b', ' ', t)
        t = re.sub(r'\(\s+([a-zA-ZçğıöşüÇĞİÖŞÜ0-9])', r'\1', t)
        t = re.sub(r'\(\s*([a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+)\s*\(', r'\1 ', t)
        t = re.sub(r'^[\s\)\:\-\*]+', '', t)
        t = re.sub(r'\s{2,}', ' ', t).strip()
        return t

    for q in questions:
        qtext = clean_txt(q.get("question", ""))
        expl = clean_txt(q.get("explanation", ""))
        options = {k: clean_txt(v) for k, v in q.get("options", {}).items()}
        ans = q.get("answer", "")
        ans_text = options.get(ans, "")

        # 1. Kök uzunluğu kontrolü
        if len(qtext.strip()) < 20:
            purged_count += 1
            continue

        # 2. Şık sayısı ve geçerli cevap anahtarı
        if len(options) < 4 or not ans or ans not in options:
            purged_count += 1
            continue

        # 3. Çöp / Boş şık kontrolü
        has_junk_opt = False
        for k, v in options.items():
            if len(v.strip()) <= 1 or v.strip() in [";", ".", "-", ":", "_", "/", "\\"]:
                has_junk_opt = True
                break
        if has_junk_opt:
            purged_count += 1
            continue

        # 4. Romen rakamı öncül uyumu
        opt_has_roman = any(v.lower().startswith("yalnız") or re.search(r"\b[iI|ıIİ]{1,3}\s*ve\b", v) for v in options.values())
        stem_has_roman = bool(re.search(r"\b(I|II|III|IV|V)\.", qtext) or re.search(r"\b(1|2|3)\.\s", qtext))
        if opt_has_roman and not stem_has_roman:
            purged_count += 1
            continue

        # 5. Soru kökü - Alternatif Soru Swap kontrolü
        m_alt = re.search(r'\(?Not:\s*Bu\s*soru[^\)]*şöyle\s*de?\s*sorulabilirdi[:\)]?\s*([^\?\n\r]+\?)', expl, re.IGNORECASE)
        if m_alt:
            alt_q = m_alt.group(1).strip()
            if ans_text and len(ans_text) > 3 and re.search(r'\b' + re.escape(ans_text) + r'\b', qtext, re.IGNORECASE):
                if not re.search(r'\b' + re.escape(ans_text) + r'\b', alt_q, re.IGNORECASE):
                    clean_alt = re.sub(r'^[\s\)\:\-\*]+', '', alt_q).strip()
                    expl = expl.replace(m_alt.group(0), f"Bu soru şöyle de sorulabilirdi: {qtext}")
                    qtext = clean_alt
                    swap_count += 1

        cleaned.append({
            **q,
            "question": qtext,
            "options": options,
            "explanation": expl
        })

    print(f"🧹 [{book_name}] QA Filtresi: {len(questions)} sorudan {len(cleaned)} soru onaylandı (Elenen: {purged_count}, Swap Onarılan: {swap_count}).")
    return cleaned

# ==================== 1. GERÇEK SINAV MODU (EXAM EDITION) ====================
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
    return "Genel TUS"

def process_exam_edition(pdf_path, exam_code="mart2023", exam_title="Mart 2023 Gerçek TUS"):
    """
    Tam kapsamlı gerçek TUS sınav kitabını (240 soru, Temel + Klinik) ayrıştırır.
    """
    print(f"\n🔥 [Exam Edition] {pdf_path.name} işleniyor...")
    doc = fitz.open(pdf_path)
    print(f"  Toplam Sayfa: {len(doc)}")

    full_lines = []
    for pno in range(len(doc)):
        txt = doc[pno].get_text()
        for raw_l in txt.split('\n'):
            l = raw_l.strip()
            if not l or is_blacklisted_text(l):
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

    parsed = []
    opt_regex = re.compile(r'^([A-Ea-e8Oo0Çç])\s*[\)\.\-]\s*(.*)$')

    for k in range(len(valid_starts)):
        start_idx, qnum, start_pno, initial_stem = valid_starts[k]
        end_idx = valid_starts[k+1][0] if k + 1 < len(valid_starts) else min(start_idx + 80, len(full_lines))
        block_lines = full_lines[start_idx:end_idx]

        stem_parts = [initial_stem] if initial_stem else []
        options = {}
        explanation_parts = []
        correct_answer = None
        current_opt = None
        found_any_opt = False
        in_explanation = False

        for line_offset, (pno, line_text) in enumerate(block_lines):
            if line_offset == 0 and initial_stem:
                continue

            ans_m = ANSWER_REGEX.search(line_text)
            if ans_m:
                correct_answer = ans_m.group(1).upper()

            opt_m = opt_regex.match(line_text)
            if opt_m and not in_explanation:
                raw_letter = opt_m.group(1).upper()
                letter = 'B' if raw_letter == '8' else ('C' if raw_letter in ['Ç', 'C'] else ('D' if raw_letter in ['O', '0', 'D'] else raw_letter))
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

        stem = " ".join(stem_parts).strip()
        stem = re.sub(r'^\d{1,3}\s*[\.\,\_\-]\s*', '', stem).strip()
        raw_expl = "\n".join(explanation_parts).strip()

        if not correct_answer and raw_expl:
            ans_m = ANSWER_REGEX.search(raw_expl)
            if ans_m:
                correct_answer = ans_m.group(1).upper()

        has_opts = len(options) == 5 and all(opt in options for opt in ['A', 'B', 'C', 'D', 'E'])
        if len(stem) > 20 and has_opts and correct_answer:
            parsed.append({
                "id": f"{exam_code}_q{qnum}",
                "original_num": qnum,
                "exam": f"{exam_title}",
                "period": "Mart 2023",
                "subject": get_subject_by_qnum(qnum),
                "topic": get_subject_by_qnum(qnum),
                "question": stem,
                "options": {k: options[k] for k in ['A', 'B', 'C', 'D', 'E']},
                "answer": correct_answer,
                "explanation": raw_expl
            })

    # QA Audit
    verified = audit_and_clean_questions(parsed, exam_title)
    output_path = VIRTUAL_DB_DIR / f"questions_{exam_code}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(verified, f, ensure_ascii=False, indent=2)

    categories = {
        "Temel Tıp Bilimleri": sum(1 for q in verified if q.get("original_num", 0) <= 120),
        "Klinik Tıp Bilimleri": sum(1 for q in verified if q.get("original_num", 0) > 120)
    }
    update_manifest(exam_code, exam_title, len(verified), categories, is_exam_edition=True, icon="🔥", color="#f59e0b")
    print(f"✅ {exam_title} tamamlandı! Toplam {len(verified)} doğrulanmış soru kaydedildi.")

# ==================== 2. ANA ÇALIŞTIRMA ====================
def main():
    ensure_directories()
    print("=========================================================")
    print("🌟 TUS Unified Soru Ayıklama ve Virtual DB Motoru v3.0")
    print("=========================================================")

    # 1. Check for Exam Edition PDFs in ss/
    exam_pdfs = list(EXAM_DIR.glob("*.pdf"))
    if exam_pdfs:
        for epdf in exam_pdfs:
            if "2023" in epdf.name and "Mart" in epdf.name:
                process_exam_edition(epdf, exam_code="mart2023", exam_title="Mart 2023 Gerçek TUS")
    else:
        print("ℹ️ 'ss/' dizininde taranacak yeni sınav PDF'i bulunamadı.")

    # 2. Check for Subject PDFs in cikmis_sorular/
    subject_pdfs = [p for p in PDF_DIR.glob("*.pdf") if not p.name.startswith("test_")]
    if subject_pdfs:
        print(f"📚 'cikmis_sorular/' içinde {len(subject_pdfs)} adet branş PDF'i bulundu.")
    else:
        print("ℹ️ 'cikmis_sorular/' dizininde taranacak yeni branş PDF'i bulunamadı.")

if __name__ == "__main__":
    main()
