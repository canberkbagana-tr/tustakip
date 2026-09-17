import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('cikmis_sorular/virtual_db/questions_mart2023.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [1, 2, 3, 4, 6, 7, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22]

for q in questions:
    if q.get('original_num') in targets:
        print(f"=== Q{q.get('original_num')} ({q.get('subject')}) ===")
        print("STEM:", q.get('question'))
        print("OPTS:", q.get('options'))
        print("ANS:", q.get('answer'))
        print("EXPL:", q.get('explanation')[:300])
        print()
