# 남은 일본어 텍스트 전수조사: python tools/survey.py
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, 'tools')); sys.path.insert(0, HERE)
from evx import blocks, code_start, strings, is_text
import build

JP = re.compile('[぀-ヿ一-鿿]')


def sjis_runs(d, minlen=4):
    """SJIS 2바이트 문자 연속 구간 찾기"""
    out = []; i = 0; n = len(d)
    while i < n - 1:
        j = i; cnt = 0
        while j < n - 1:
            a, b = d[j], d[j + 1]
            if (0x81 <= a <= 0x9f or 0xe0 <= a <= 0xef) and 0x40 <= b <= 0xfc and b != 0x7f:
                j += 2; cnt += 1
            elif 0x20 <= a < 0x7f or 0xa1 <= a <= 0xdf or a in (0x0a, 0x1b):
                j += 1
            else:
                break
        if cnt >= 1 and cnt * 2 * 2 >= j - i and j < n and d[j] == 0 and (i == 0 or d[i - 1] == 0):
            s = d[i:j].decode('cp932', 'replace')
            if JP.search(s):
                out.append((i, s))
            i = j
        else:
            i += 1
    return out


ko = build.load_ko()
miss = []
d = open(os.path.join(HERE, 'orig', 'PM.EVX'), 'rb').read()
for i, b in blocks(d):
    if b is None: continue
    c0, _ = code_start(b)
    for o, s in strings(b, c0):
        if not is_text(s): continue
        t = s.decode('cp932', 'replace')
        if JP.search(t) and t not in ko:
            miss.append((i, o, t))
print('EVX 미번역:', len(miss))
for x in miss[:80]: print(' ', x)
exe_done = {int(x['addr'], 16) if isinstance(x['addr'], str) else x['addr'] for x, _ in build.load_exe_ko()}
B = 0x80040000 - 0x800
for f in ('PM3.EXE', 'STFR.EXE', 'SCPS_100.32'):
    d = open(os.path.join(HERE, 'orig', f), 'rb').read()
    r = sjis_runs(d)
    if f == 'PM3.EXE':
        r = [(o, s) for o, s in r if not any(a - B <= o < a - B + 64 for a in exe_done)]
    print(f, len(r))
    for o, s in r: print('  %06x %s' % (o, s[:60].replace('\n', '/').replace('\x1b', '{E}')))
