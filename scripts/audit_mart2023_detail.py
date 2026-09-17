import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('cikmis_sorular/virtual_db/questions_mart2023.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

print(f"Total questions: {len(questions)}")

# Regex for bad patterns
bad_chars_re = re.compile(r'[~µ_~§#|><\\{}]')
broken_words_re = re.compile(r'(?:h0cre|erltro|slto|ONA\b|blz|etkfl|bylyn|oroıın|lenfold|nmus|Befinc|yanhıt|Mitoük|dOOOm|çlrkln|batvun|CamScanner|kul hak|yayınımızın)')

bad_count = 0
for idx, q in enumerate(questions):
    issues = []
    qtext = q.get('question', '')
    expl = q.get('explanation', '')
    opts = q.get('options', {})
    ans = q.get('answer', '')
    
    # 1. Stem issues
    if len(qtext) < 30:
        issues.append(f"short_stem({len(qtext)})")
    if 'CamScanner' in qtext or 'kul hak' in qtext:
        issues.append("watermark_in_stem")
    if broken_words_re.search(qtext):
        issues.append("broken_stem_words")
    if bad_chars_re.search(qtext):
        issues.append("bad_chars_stem")
        
    # 2. Options issues
    if len(opts) != 5:
        issues.append(f"opts_count({len(opts)})")
    for k, v in opts.items():
        if len(v) < 2:
            issues.append(f"empty_opt_{k}")
        if broken_words_re.search(v) or bad_chars_re.search(v):
            issues.append(f"bad_opt_{k}")
            
    # 3. Answer issues
    if not ans or ans not in opts:
        issues.append(f"invalid_ans({ans})")
        
    # 4. Explanation issues
    if len(expl) < 30:
        issues.append(f"short_expl({len(expl)})")
    if 'CamScanner' in expl:
        issues.append("camscanner_in_expl")
    if broken_words_re.search(expl):
        issues.append("broken_expl_words")
        
    if issues:
        bad_count += 1
        print(f"[{idx+1}] ID: {q.get('id')} (Q{q.get('original_num')}, {q.get('subject')}): Issues={issues}")
        print(f"   Q: {qtext[:80]}...")
        if 'short_expl' in str(issues) or 'bad_chars_stem' in str(issues) or 'broken_stem_words' in str(issues):
            print(f"   Opts: {opts}")
            print(f"   Expl: {expl[:120]}...")
        print("-" * 50)

print(f"\nTotal questions with issues: {bad_count} / {len(questions)}")
