import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('cikmis_sorular/virtual_db/questions_mart2023.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print(f"Total questions in Mart 2023: {len(questions)}")

for i, q in enumerate(questions):
    q_num = q.get('original_num', i + 1)
    sub = q.get('subject', '')
    top = q.get('topic', '')
    q_text = q.get('question', '').replace('\n', ' ')
    ans = q.get('answer', '')
    opts = q.get('options', {})
    opt_keys = list(opts.keys())
    
    # Check suspicious issues
    issues = []
    if len(opt_keys) != 5:
        issues.append(f"options={opt_keys}")
    if any(c in q_text for c in ['~', 'µ', '!', 'Ç<>', 'Jidaki', 'oroıı']):
        issues.append("corrupt_chars")
    if 'CamScanner' in q_text or 'CamScanner' in q.get('explanation', ''):
        issues.append("camscanner_watermark")
    if 'kul hak' in q_text or 'yayınımızın' in q_text:
        issues.append("copyright_junk")
    
    if issues or i < 10:
        print(f"[{i+1}] Soru {q_num} ({sub}): {q_text[:70]}... | Issues: {issues}")
