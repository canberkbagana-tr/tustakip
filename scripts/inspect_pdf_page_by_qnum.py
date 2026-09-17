import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open('ss/2023 Mart.pdf')

def find_q(qnum):
    target = f"{qnum}."
    results = []
    for pno in range(len(doc)):
        txt = doc[pno].get_text()
        if re.search(r'(?:^|\n)\s*' + str(qnum) + r'\s*[\.\,\_\-]', txt):
            results.append((pno + 1, txt))
    return results

if __name__ == '__main__':
    qnums = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [22, 66, 68]
    for qn in qnums:
        res = find_q(qn)
        print(f"================ QUESTION {qn} (Found on {len(res)} pages) ================")
        for pno, txt in res:
            print(f"--- Page {pno} ---")
            lines = txt.split('\n')
            for l in lines:
                print(l)
