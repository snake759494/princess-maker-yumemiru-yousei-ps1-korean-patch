# 번역 검사: python tools/tcheck.py NN  (text/src/evx_NN.json 과 text/ko/evx_NN.json 비교)
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
ESC = re.compile(r'\{E\}(?:%[A-Za-z0-9_]+|d\d+,\d+|f\d+|\[\d*|\]|#[0-9A-Fa-f]*|/\d+|s\d+\.?|_\d+|b.|[a-z])')
KANA = re.compile(r'[぀-ヺー-ヿ｡-･ｦ-ﾟ]')


def blen(t):
    n = 0
    t = t.replace('{E}', '\x1b')
    for c in t:
        if '가' <= c <= '힣':
            n += 2
        else:
            n += len(c.encode('cp932'))
    return n


def check(nn):
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'text')
    src = json.load(open(os.path.join(base, 'src', f'evx_{nn}.json'), encoding='utf-8'))
    p = os.path.join(base, 'ko', f'evx_{nn}.json')
    ko = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    errs = []
    for x in src:
        k = str(x['i'])
        if k not in ko:
            errs.append(f'[{k}] 누락'); continue
        t = ko[k]
        if ESC.findall(t) != ESC.findall(x['ja']):
            errs.append(f'[{k}] 제어코드 불일치: {ESC.findall(x["ja"])} -> {ESC.findall(t)}')
        if t.count('\n') != x['ja'].count('\n'):
            errs.append(f'[{k}] 줄바꿈 수 다름 ({x["ja"].count(chr(10))} -> {t.count(chr(10))})')
        try:
            n = blen(t)
        except UnicodeEncodeError as e:
            errs.append(f'[{k}] 쓸 수 없는 문자: {e.object[e.start:e.end]!r}'); continue
        if x['fit'] and n > x['max']:
            errs.append(f'[{k}] 길이 초과(고정 자리) {n}>{x["max"]}: {t}')
        if KANA.search(t.replace('{E}', '')):
            errs.append(f'[{k}] 일본어 가나 남음: {t}')
    return errs, len(src), len(ko)


if __name__ == '__main__':
    for nn in sys.argv[1:]:
        errs, a, b = check(nn)
        print(f'evx_{nn}: 원문 {a}, 번역 {b}, 오류 {len(errs)}')
        for e in errs[:200]:
            print('  ' + e)
