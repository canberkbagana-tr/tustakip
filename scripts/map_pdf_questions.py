import fitz
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open('ss/2023 Mart.pdf')

pages_data = []
for pno in range(len(doc)):
    page_text = doc[pno].get_text()
    pages_data.append((pno + 1, page_text))

print(f"Total pages: {len(pages_data)}")

# Let's inspect the first 25 pages to see questions 1 to 25
for pno, txt in pages_data[:25]:
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    q_lines = [l for l in lines if re.match(r'^\d{1,3}\s*[\.\,\_\-]', l)]
    ans_lines = [l for l in lines if re.search(r'cevap', l, re.I)]
    print(f"Page {pno}: Qs={q_lines} | Ans={ans_lines}")
