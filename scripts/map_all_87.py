import fitz
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open('ss/2023 Mart.pdf')

with open('cikmis_sorular/virtual_db/questions_mart2023.json', 'r', encoding='utf-8') as f:
    current_questions = json.load(f)

print(f"Loaded {len(current_questions)} questions from questions_mart2023.json")

# Build a map of question number -> page in PDF
pdf_pages = []
for pno in range(len(doc)):
    pdf_pages.append((pno + 1, doc[pno].get_text()))

def extract_q_context(qnum):
    matches = []
    for pno, txt in pdf_pages:
        # Match question start
        m = re.search(r'(?:^|\n)\s*' + str(qnum) + r'\s*[\.\,\_\-]\s*(.*)', txt)
        if m:
            matches.append((pno, txt))
    return matches

output = {}
for q in current_questions:
    qnum = q.get('original_num')
    qid = q.get('id')
    ctx = extract_q_context(qnum)
    output[qnum] = {
        'id': qid,
        'qnum': qnum,
        'subject': q.get('subject'),
        'current_q': q.get('question'),
        'current_ans': q.get('answer'),
        'pdf_matches': [(pno, len(txt)) for pno, txt in ctx]
    }

print("Question to PDF mapping completed.")
for qnum, info in list(output.items())[:15]:
    print(f"Q{qnum} ({info['subject']}): PDF pages = {[p for p, _ in info['pdf_matches']]}")
