import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('cikmis_sorular/virtual_db/questions_mart2023.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end = int(sys.argv[2]) if len(sys.argv) > 2 else 20

for i in range(start, min(end, len(questions))):
    q = questions[i]
    print(f"=== INDEX {i} | ID: {q.get('id')} | Soru {q.get('original_num')} ({q.get('subject')}) ===")
    print("Q:", q.get('question'))
    print("Opts:", json.dumps(q.get('options'), ensure_ascii=False))
    print("Ans:", q.get('answer'))
    print("Expl:", q.get('explanation')[:200] + ("..." if len(q.get('explanation', '')) > 200 else ""))
    print()
