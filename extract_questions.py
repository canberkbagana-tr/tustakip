"""
TUS Akıllı Soru Ayıklama ve Virtual Soru Tabanı Motoru (v2.2 - Checkpoint & Resume)

Temel İlkeler:
1. Soru olmayan alanları (kapaklar, telif sayfaları, salt konu anlatımı/özet tabloları) KESİNLİKLE soru olarak kesmez.
2. Soruların konu anlatımlarının arasına serpiştirildiği kitaplarda regex ve şık analizi ile yalnızca izole soru bloklarını yakalar.
3. Soruları kitap bazlı hafif ve optimize JSON olarak (cikmis_sorular/virtual_db/questions_<kitap>.json) depolar.
4. "Benzer soru / şöyle de sorulabilirdi" şeklindeki türetilmiş soruları duplicate olarak almaz, tekilleştirir.
5. CHECKPOINT & RESUME: extraction_state.json üzerinden kalınan sayfayı hatırlar, her çalıştırmada kaldığı yerden devam eder.
6. Mevcut soruları silmez; yeni soruları mevcut listeye ekler (append & dedup).
7. Kitap tamamen bittiğinde (304/304 sayfa) isCompleted: true işaretler ve PDF'in güvenle silinebileceğini bildirir.
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

BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR / "cikmis_sorular"
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
    VIRTUAL_DB_DIR.mkdir(parents=True, exist_ok=True)

# Soru filtreleme regexleri
Q_START_REGEX = re.compile(r'^\s*(\d{1,3})\.\s*(.*)', re.DOTALL)
EXAM_PERIOD_REGEX = re.compile(r'\((Nisan|Eylül|Mart|Ağustos|Aralık|Şubat|Kasım)[\s\-_]*(\d{2,4})[^\)]*\)', re.IGNORECASE)
ANSWER_REGEX = re.compile(r'(?:Doğru\s*cevap|Dogru\s*cevap|Cevap)\s*[:=]\s*([A-E])', re.IGNORECASE)

# Kara liste: Soru olmayan sayfalar ve dipnotlar
BLACKLIST_KEYWORDS = [
    "telif hukuku", "kul hakkı", "yasal olmayan yollarla", "tusdata", 
    "bütün inançlar açısından", "hırsızlık yoluyla", "fotokopi",
    "içindekiler", "bölüm başlığı", "tüm hakları saklıdır", "asla helal etmiyoruz"
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

def update_manifest(book_code, book_title, question_count, categories_dict):
    if not MANIFEST_PATH.exists():
        return

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if "subjects" not in manifest:
            manifest["subjects"] = {}

        if book_code in manifest["subjects"]:
            manifest["subjects"][book_code]["questionCount"] = question_count
            manifest["subjects"][book_code]["categories"] = categories_dict
        else:
            manifest["subjects"][book_code] = {
                "name": book_title,
                "code": book_code,
                "file": f"cikmis_sorular/virtual_db/questions_{book_code}.json",
                "color": "#ef4444",
                "icon": "🩺",
                "questionCount": question_count,
                "categories": categories_dict
            }

        total_q = sum(sub.get("questionCount", 0) for sub in manifest["subjects"].values())
        active_s = sum(1 for sub in manifest["subjects"].values() if sub.get("questionCount", 0) > 0)

        manifest["totalQuestions"] = total_q
        manifest["summary"]["activeSubjects"] = active_s

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"📊 Manifest Güncellendi: Toplam {total_q} Soru | Aktif Branş: {active_s} / 13")
    except Exception as e:
        print(f"⚠️ Manifest güncellenirken hata: {e}")

def parse_book_into_virtual_db(pdf_path, batch_pages=45):
    book_name = pdf_path.stem.lower().replace(" ", "_").replace("ç", "c").replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ö", "o")
    output_json_path = VIRTUAL_DB_DIR / f"questions_{book_name}.json"

    # 1. Mevcut soruları oku (ezmemek ve dedup için)
    existing_questions = []
    seen_questions_text = set()
    if output_json_path.exists():
        try:
            with open(output_json_path, "r", encoding="utf-8") as f:
                existing_questions = json.load(f)
                for q in existing_questions:
                    q_key = q.get("question", "")[:40].lower().strip()
                    if q_key:
                        seen_questions_text.add(q_key)
        except Exception:
            existing_questions = []

    # 2. State dosyasından kalınan sayfayı belirle
    state = load_state()
    book_state = state.get(book_name, {
        "lastProcessedPage": 12,
        "totalPages": 0,
        "totalExtracted": len(existing_questions),
        "isCompleted": False
    })

    if book_state.get("isCompleted"):
        print(f"✅ {pdf_path.name} zaten %100 tamamlanmış durumda! ({book_state.get('totalExtracted')} soru)")
        return existing_questions

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    book_state["totalPages"] = total_pages

    start_page = book_state.get("lastProcessedPage", 12)
    end_page = min(total_pages, start_page + batch_pages)

    print(f"\n=======================================================")
    print(f"📖 Kitap: {pdf_path.name} (Toplam {total_pages} sayfa)")
    print(f"📍 Kaldığı Sayfa: {start_page} ➔ Taranacak Aralık: Sayfa {start_page + 1} - {end_page}")
    print(f"📦 Mevcut Havuz: {len(existing_questions)} soru")
    print(f"=======================================================")

    extracted_new_questions = []

    for page_idx in range(start_page, end_page):
        page = doc[page_idx]
        text = page.get_text()

        if len(text.strip()) < 50:
            try:
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang="tur+eng")
            except Exception as e:
                text = ""

        if not text or len(text.strip()) < 40:
            continue

        if is_blacklisted_text(text) and not ANSWER_REGEX.search(text):
            continue

        lines = text.splitlines()
        current_q = None

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            if "şöyle de sorulabilirdi" in trimmed.lower() or "benzeri)" in trimmed.lower():
                if current_q and current_q.get("answer"):
                    current_q["explanation"] += " (Not: " + trimmed + ")"
                continue

            m_start = Q_START_REGEX.match(trimmed)
            if m_start:
                q_num = int(m_start.group(1))
                q_rest = m_start.group(2).strip()

                if 1 <= q_num <= 300:
                    if current_q and len(current_q.get("options", {})) >= 3 and current_q.get("answer"):
                        q_key = current_q["question"][:40].lower().strip()
                        if q_key not in seen_questions_text:
                            seen_questions_text.add(q_key)
                            extracted_new_questions.append(current_q)

                    exam_match = EXAM_PERIOD_REGEX.search(trimmed)
                    exam_label = exam_match.group(0) if exam_match else f"{pdf_path.stem} Çıkmış Soru"

                    current_q = {
                        "id": f"{book_name}_q{len(existing_questions) + len(extracted_new_questions) + 1}",
                        "book": pdf_path.stem,
                        "exam": exam_label,
                        "subject": pdf_path.stem,
                        "topic": "Temel & Klinik Fizyoloji",
                        "question": q_rest,
                        "hasImage": False,
                        "image": None,
                        "options": {},
                        "answer": None,
                        "explanation": ""
                    }
                    continue

            if not current_q:
                continue

            line_opts = parse_options_from_line(trimmed)
            if line_opts:
                for letter, opt_text in line_opts.items():
                    current_q["options"][letter] = opt_text
                continue

            ans_match = ANSWER_REGEX.search(trimmed)
            if ans_match:
                current_q["answer"] = ans_match.group(1).upper()
                continue

            if current_q.get("answer"):
                if not is_blacklisted_text(trimmed):
                    current_q["explanation"] += " " + trimmed
            else:
                if not line_opts:
                    current_q["question"] += " " + trimmed

        if current_q and len(current_q.get("options", {})) >= 3 and current_q.get("answer"):
            q_key = current_q["question"][:40].lower().strip()
            if q_key not in seen_questions_text:
                seen_questions_text.add(q_key)
                extracted_new_questions.append(current_q)

    # Geçerli yeni soruları filtrele
    valid_new = []
    for q in extracted_new_questions:
        q["question"] = q["question"].strip()
        q["explanation"] = q["explanation"].strip()
        if len(q["options"]) >= 4 and q["answer"]:
            valid_new.append(q)

    # Mevcut havuzla birleştir ve ID'leri yeniden sırala
    all_combined = existing_questions + valid_new
    for idx, q in enumerate(all_combined, 1):
        q["id"] = f"{book_name}_q{idx}"

    # Kategorileri hesapla
    categories_dict = {}
    for q in all_combined:
        cat = q.get("topic", "Genel Fizyoloji")
        categories_dict[cat] = categories_dict.get(cat, 0) + 1

    # JSON'a kaydet
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(all_combined, f, ensure_ascii=False, indent=2)

    # State'i güncelle
    book_state["lastProcessedPage"] = end_page
    book_state["totalExtracted"] = len(all_combined)
    book_state["isCompleted"] = (end_page >= total_pages)
    state[book_name] = book_state
    save_state(state)

    print(f"\n✅ Bu turda {len(valid_new)} yeni soru eklendi!")
    print(f"📈 Toplam Havuz: {len(all_combined)} soruya ulaştı.")
    print(f"📍 Kaldığımız Sayfa: {end_page} / {total_pages}")

    if book_state["isCompleted"]:
        print(f"🎉 TEBRİKLER! {pdf_path.name} %100 tarandı ve tamamlandı!")
        print(f"🗑️ PDF dosyası ({pdf_path.name}) artık yer kaplamaması için güvenle silinebilir.")

    # Manifest'i güncelle
    update_manifest(book_name, pdf_path.stem, len(all_combined), categories_dict)
    return all_combined

def main():
    ensure_directories()
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("📁 cikmis_sorular/ klasöründe taranacak PDF bulunamadı.")
        return

    # Fizyoloji PDF'inden 45 sayfalık yeni dilim işle
    for pdf in pdf_files:
        parse_book_into_virtual_db(pdf, batch_pages=45)

if __name__ == "__main__":
    main()
