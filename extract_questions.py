"""
TUS Akıllı Soru Ayıklama ve Virtual Soru Tabanı Motoru (v2.0)

Temel İlkeler:
1. Soru olmayan alanları (kapaklar, telif sayfaları, salt konu anlatımı/özet tabloları) KESİNLİKLE soru olarak kesmez.
2. Soruların konu anlatımlarının arasına serpiştirildiği kitaplarda regex ve şık analizi ile yalnızca izole soru bloklarını yakalar.
3. Soruları kitap bazlı hafif ve optimize JSON olarak (cikmis_sorular/virtual_db/questions_<kitap>.json) depolar.
4. Gereksiz devasa PNG kırpmalarından kaçınır; salt metinli soruları JSON'da tutarak diski ve Firebase'i korur.
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

BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR / "cikmis_sorular"
VIRTUAL_DB_DIR = PDF_DIR / "virtual_db"
OUTPUT_IMG_DIR = BASE_DIR / "assets" / "questions"

def ensure_directories():
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    VIRTUAL_DB_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)

# Soru filtreleme regexleri
Q_START_REGEX = re.compile(r'(?:^|\n)\s*(\d{1,3})\.\s*([^\n]+)', re.MULTILINE)
EXAM_PERIOD_REGEX = re.compile(r'\((Nisan|Eylül|Mart|Ağustos|Aralık)[\s\-_]*(\d{2,4})\)', re.IGNORECASE)
OPTIONS_REGEX = re.compile(r'([A-E])\)\s*([^\n]+)')
ANSWER_REGEX = re.compile(r'(?:Doğru\s*cevap|Dogru\s*cevap|Cevap)\s*[:=]\s*([A-E])', re.IGNORECASE)

# Soru olmayan sayfaları / blokları filtreleme kara listesi
BLACKLIST_KEYWORDS = [
    "telif hukuku", "kul hakkı", "yasal olmayan yollarla", "tusdata", 
    "bütün inançlar açısından", "hırsızlık yoluyla", "fotokopi",
    "içindekiler", "bölüm başlığı", "tüm hakları saklıdır"
]

def is_blacklisted_text(text):
    text_lower = text.lower()
    return any(k in text_lower for k in BLACKLIST_KEYWORDS)

def parse_book_into_virtual_db(pdf_path):
    book_name = pdf_path.stem.lower().replace(" ", "_").replace("ç", "c").replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ö", "o")
    print(f"\n=======================================================")
    print(f"📖 Kitap İşleniyor: {pdf_path.name}")
    print(f"Hedef Sanal DB: questions_{book_name}.json")
    print(f"=======================================================")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    extracted_questions = []

    for page_idx in range(total_pages):
        page = doc[page_idx]
        text = page.get_text()

        # Eğer sayfa bitmap taramaysa (text boşsa) OCR ile tara
        if len(text.strip()) < 50 and 'pytesseract' in sys.modules:
            try:
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
            except Exception as e:
                text = ""

        if not text or len(text.strip()) < 30:
            continue

        # Telif / Kapak sayfası kontrolü
        if is_blacklisted_text(text) and not ANSWER_REGEX.search(text):
            # Soru olmayan saf telif/kapak sayfası -> ATLA
            continue

        # Soru ve cevap bloklarını tespit et
        lines = text.splitlines()
        current_q = None

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Soru başlangıcı tespiti (Örn: 1. Kromozomlar...)
            m_start = re.match(r'^(\d{1,3})\.\s*(.*)', trimmed)
            if m_start:
                q_num = int(m_start.group(1))
                if 1 <= q_num <= 200:
                    if current_q and len(current_q.get("options", {})) >= 3 and current_q.get("answer"):
                        extracted_questions.append(current_q)

                    exam_match = EXAM_PERIOD_REGEX.search(trimmed)
                    exam_label = exam_match.group(0) if exam_match else f"{pdf_path.stem} Çıkmış Soru"

                    current_q = {
                        "id": f"{book_name}_q{q_num}",
                        "book": pdf_path.stem,
                        "exam": exam_label,
                        "subject": pdf_path.stem,
                        "topic": "Genel TUS",
                        "question": m_start.group(2).strip(),
                        "hasImage": false if 'false' in globals() else False,
                        "image": None,
                        "options": {},
                        "answer": None,
                        "explanation": ""
                    }
                    continue

            if not current_q:
                continue

            # Şık tespiti (A, B, C, D, E)
            opt_matches = OPTIONS_REGEX.findall(trimmed)
            if opt_matches:
                for letter, opt_text in opt_matches:
                    current_q["options"][letter] = opt_text.strip()
                continue

            # Doğru cevap tespiti
            ans_match = ANSWER_REGEX.search(trimmed)
            if ans_match:
                current_q["answer"] = ans_match.group(1).upper()
                continue

            # Açıklama metni ekleme
            if current_q.get("answer"):
                if not is_blacklisted_text(trimmed):
                    current_q["explanation"] += " " + trimmed
            else:
                # Soru kökünün devamı
                if not opt_matches:
                    current_q["question"] += " " + trimmed

        if current_q and len(current_q.get("options", {})) >= 3 and current_q.get("answer"):
            extracted_questions.append(current_q)

    # Temizleme ve kalite kontrolü
    valid_questions = []
    seen_ids = set()
    for q in extracted_questions:
        if q["id"] in seen_ids:
            continue
        seen_ids.add(q["id"])
        q["question"] = q["question"].strip()
        q["explanation"] = q["explanation"].strip()
        if len(q["options"]) >= 4 and q["answer"]:
            valid_questions.append(q)

    # Sanal Soru Tabanı JSON Çıktısı
    output_json_path = VIRTUAL_DB_DIR / f"questions_{book_name}.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(valid_questions, f, ensure_ascii=False, indent=2)

    print(f"✅ {pdf_path.name} içerisinden {len(valid_questions)} geçerli soru ayıklandı.")
    print(f"💾 Sanal Soru Tabanı Dosyası: {output_json_path}")
    return valid_questions

def main():
    ensure_directories()
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("📁 cikmis_sorular/ klasöründe taranacak PDF bulunamadı.")
        return

    total_extracted = 0
    for pdf in pdf_files:
        qs = parse_book_into_virtual_db(pdf)
        total_extracted += len(qs)

    print(f"\n🎉 Tüm kitaplar tarandı! Toplam Virtual Soru Tabanı Havuzu: {total_extracted} soru.")

if __name__ == "__main__":
    main()
