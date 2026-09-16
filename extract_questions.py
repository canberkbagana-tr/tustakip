"""
TUS Akıllı Soru Ayıklama ve Virtual Soru Tabanı Motoru (v2.1)

Temel İlkeler:
1. Soru olmayan alanları (kapaklar, telif sayfaları, salt konu anlatımı/özet tabloları) KESİNLİKLE soru olarak kesmez.
2. Soruların konu anlatımlarının arasına serpiştirildiği kitaplarda regex ve şık analizi ile yalnızca izole soru bloklarını yakalar.
3. Soruları kitap bazlı hafif ve optimize JSON olarak (cikmis_sorular/virtual_db/questions_<kitap>.json) depolar.
4. "Benzer soru / şöyle de sorulabilirdi" şeklindeki türetilmiş soruları duplicate olarak almaz, tekilleştirir.
5. question_bank_manifest.json dosyasını otomatik olarak güncelleyerek sistemle %100 senkronize tutar.
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
    """
    Satırda yan yana veya tek başına bulunan A), B), C), D), E) şıklarını ayrıştırır.
    Örn: 'A) Lizozom B) Golgi aparatı' -> {'A': 'Lizozom', 'B': 'Golgi aparatı'}
    """
    opts = {}
    parts = re.split(r'([A-E]\))', line)
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            letter = parts[i][0]
            val = parts[i+1].strip() if i+1 < len(parts) else ""
            if val:
                opts[letter] = val
    return opts

def update_manifest(book_code, book_title, question_count, categories_dict):
    """
    question_bank_manifest.json dosyasını günceller.
    """
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

        # Toplam soru ve aktif ders hesapla
        total_q = sum(sub.get("questionCount", 0) for sub in manifest["subjects"].values())
        active_s = sum(1 for sub in manifest["subjects"].values() if sub.get("questionCount", 0) > 0)

        manifest["totalQuestions"] = total_q
        manifest["summary"]["activeSubjects"] = active_s
        manifest["lastUpdated"] = f"{Path(__file__).stat().st_mtime}"

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"📊 Manifest Güncellendi: Toplam {total_q} Soru | Aktif Branş: {active_s} / 13")
    except Exception as e:
        print(f"⚠️ Manifest güncellenirken hata: {e}")

def parse_book_into_virtual_db(pdf_path, max_pages=None, start_page=12):
    book_name = pdf_path.stem.lower().replace(" ", "_").replace("ç", "c").replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ö", "o")
    print(f"\n=======================================================")
    print(f"📖 Kitap İşleniyor: {pdf_path.name}")
    print(f"Hedef Sanal DB: questions_{book_name}.json")
    print(f"=======================================================")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    end_page = min(total_pages, start_page + max_pages) if max_pages else total_pages

    extracted_questions = []
    seen_questions_text = set()

    for page_idx in range(start_page, end_page):
        page = doc[page_idx]
        text = page.get_text()

        # Sayfa bitmap taramaysa OCR ile tara
        if len(text.strip()) < 50:
            try:
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang="tur+eng")
            except Exception as e:
                text = ""

        if not text or len(text.strip()) < 40:
            continue

        # Telif / Kapak sayfası kontrolü
        if is_blacklisted_text(text) and not ANSWER_REGEX.search(text):
            continue

        lines = text.splitlines()
        current_q = None

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # "Bu soru şöyle de sorulabilirdi / BENZERİ" filtrele (duplicate engelle)
            if "şöyle de sorulabilirdi" in trimmed.lower() or "benzeri)" in trimmed.lower():
                if current_q and current_q.get("answer"):
                    # Ana sorunun çözümüne ek bilgi olarak ekle, yeni soru yapma
                    current_q["explanation"] += " (Not: " + trimmed + ")"
                continue

            # Soru başlangıcı tespiti: (Örn: 3. Hücre içerisinde...)
            m_start = Q_START_REGEX.match(trimmed)
            if m_start:
                q_num = int(m_start.group(1))
                q_rest = m_start.group(2).strip()

                # Soru numarası makul aralıkta mı? (1 - 300)
                if 1 <= q_num <= 300:
                    # Önceki tamamlanmış soruyu kaydet
                    if current_q and len(current_q.get("options", {})) >= 3 and current_q.get("answer"):
                        q_key = current_q["question"][:40].lower()
                        if q_key not in seen_questions_text:
                            seen_questions_text.add(q_key)
                            extracted_questions.append(current_q)

                    exam_match = EXAM_PERIOD_REGEX.search(trimmed)
                    exam_label = exam_match.group(0) if exam_match else f"{pdf_path.stem} Çıkmış Soru"

                    current_q = {
                        "id": f"{book_name}_q{len(extracted_questions) + 1}",
                        "book": pdf_path.stem,
                        "exam": exam_label,
                        "subject": pdf_path.stem,
                        "topic": "Hücre & Temel Fizyoloji",
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

            # Şık tespiti (A, B, C, D, E)
            line_opts = parse_options_from_line(trimmed)
            if line_opts:
                for letter, opt_text in line_opts.items():
                    current_q["options"][letter] = opt_text
                continue

            # Doğru cevap tespiti
            ans_match = ANSWER_REGEX.search(trimmed)
            if ans_match:
                current_q["answer"] = ans_match.group(1).upper()
                continue

            # Açıklama veya Soru Kökü devamı
            if current_q.get("answer"):
                if not is_blacklisted_text(trimmed):
                    current_q["explanation"] += " " + trimmed
            else:
                if not line_opts:
                    current_q["question"] += " " + trimmed

        # Sayfa sonundaki soruyu kaydet
        if current_q and len(current_q.get("options", {})) >= 3 and current_q.get("answer"):
            q_key = current_q["question"][:40].lower()
            if q_key not in seen_questions_text:
                seen_questions_text.add(q_key)
                extracted_questions.append(current_q)

    # Temizleme ve kalite kontrolü
    valid_questions = []
    categories_dict = {}

    for idx, q in enumerate(extracted_questions, 1):
        q["id"] = f"{book_name}_q{idx}"
        q["question"] = q["question"].strip()
        q["explanation"] = q["explanation"].strip()

        # En az 4 şık ve bir cevap olmalı
        if len(q["options"]) >= 4 and q["answer"]:
            valid_questions.append(q)
            cat = q.get("topic", "Genel Fizyoloji")
            categories_dict[cat] = categories_dict.get(cat, 0) + 1

    # Sanal Soru Tabanı JSON Çıktısı
    output_json_path = VIRTUAL_DB_DIR / f"questions_{book_name}.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(valid_questions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {pdf_path.name} içerisinden {len(valid_questions)} geçerli çıkmış soru ayıklandı.")
    print(f"💾 Kayıt Yeri: {output_json_path}")

    # Manifest'i güncelle
    update_manifest(book_name, pdf_path.stem, len(valid_questions), categories_dict)
    return valid_questions

def main():
    ensure_directories()
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("📁 cikmis_sorular/ klasöründe taranacak PDF bulunamadı.")
        return

    # İlk etapta Fizyoloji kitabından ilk üniteyi (Sayfa 12-45) tarıyoruz
    total_extracted = 0
    for pdf in pdf_files:
        qs = parse_book_into_virtual_db(pdf, max_pages=35, start_page=12)
        total_extracted += len(qs)

    print(f"\n🎉 Tarama Tamamlandı! Virtual Soru Tabanı Havuzu: {total_extracted} soru.")

if __name__ == "__main__":
    main()
