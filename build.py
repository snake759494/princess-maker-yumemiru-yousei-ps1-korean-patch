# 프린세스 메이커 ~꿈꾸는 요정~ 한글 패치 빌드
#   python build.py [출력.bin]
import sys, os, json, shutil, struct, glob
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools'))
from evx import blocks, code_start, strings, is_text, SLOT, ref_map, reloc_safe
import hook, kfont, namein, gfx
from disc import Writer

GAME = os.path.dirname(HERE)
SRC_BIN = os.environ.get('PM_SRC') or os.path.join(GAME, 'Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin')
ORIG = os.path.join(HERE, 'orig')


def load_ko():
    """text/src/evx_NN.json(원문) + text/ko/evx_NN.json(번역) -> {원문: 번역}"""
    ko = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'text', 'src', 'evx_*.json'))):
        src = json.load(open(f, encoding='utf-8'))
        p = os.path.join(HERE, 'text', 'ko', os.path.basename(f))
        if not os.path.exists(p):
            continue
        tr = json.load(open(p, encoding='utf-8'))
        for x in src:
            t = tr.get(str(x['i']))
            if t:
                ko[x['ja'].replace('{E}', '\x1b')] = t.replace('{E}', '\x1b')
    return ko


class Charset:
    def __init__(s, texts):
        chars = set()
        for t in texts:
            chars.update(c for c in t if '가' <= c <= '힣')
        s.chars = sorted(chars)
        s.code = {c: hook.code_for_index(i) for i, c in enumerate(s.chars)}

    def enc(s, text):
        out = bytearray()
        for c in text:
            if c in s.code:
                out += s.code[c].to_bytes(2, 'big')
            else:
                out += c.encode('cp932')
        return bytes(out)


def glyphs(chars):
    return [kfont.encode(kfont.render(c)) for c in chars]


def layout_block(i, b, ko, cs, skip):
    c0, ins = code_start(b)
    rm = ref_map(b, ins)
    size = struct.unpack_from('<I', b, 4)[0]
    blk = bytearray(b)
    free, pend, bad, fail = [], [], [], []
    n_in = n_mv = 0
    for o, s in strings(b, c0):
        if not is_text(s) or o in skip:
            continue
        ja = s.decode('cp932')
        if ja not in ko:
            continue
        e = cs.enc(ko[ja])
        if not os.environ.get('NOAGG') and reloc_safe(ins, rm.get(o, [])) and rm.get(o):
            pend.append((o, s, e))
        elif len(e) <= len(s):
            blk[o:o + len(s) + 1] = e + b'\0' * (len(s) + 1 - len(e))
            if len(s) - len(e) >= 2:
                free.append((o + len(e) + 1, o + len(s) + 1))
            n_in += 1
        elif reloc_safe(ins, rm.get(o, [])):
            pend.append((o, s, e))
        else:
            bad.append((f'{i:03d}_{o:04x}', len(e) - len(s), ja, ko[ja]))
    for o, s, e in pend:
        blk[o:o + len(s) + 1] = b'\0' * (len(s) + 1)
        free.append((o, o + len(s) + 1))
    free.append(((size + 0x20 + 3) & ~3, SLOT))
    free.sort()
    m = []
    for a, z in free:
        if m and a <= m[-1][1]:
            m[-1] = (m[-1][0], max(z, m[-1][1]))
        else:
            m.append((a, z))
    free = m
    pend.sort(key=lambda x: -len(x[2]))
    for o, s, e in pend:
        need = len(e) + 1
        free.sort(key=lambda x: x[1] - x[0])
        for k, (a, z) in enumerate(free):
            if z - a >= need:
                break
        else:
            fail.append((o, s, e))
            continue
        blk[a:a + need] = e + b'\0'
        free[k] = (a + need, z)
        for kk in rm[o]:
            struct.pack_into('<H', blk, ins[kk][0] + 1, a)
        n_mv += 1
    return blk, bad, fail, n_in, n_mv


def build_evx(ko, cs, report):
    """제자리에 들어가면 그대로, 넘치면 빈 공간(줄어든 문자열의 남는 자리·블록 꼬리)으로 옮기고 참조(push16)를 고친다.
    공간이 모자라면 가장 덜 늘어나는 것부터 원문으로 남긴다."""
    d = bytearray(open(os.path.join(ORIG, 'PM.EVX'), 'rb').read())
    bad, lack = [], {}
    N_in = N_mv = 0
    for i, b in blocks(bytes(d)):
        if b is None:
            continue
        skip = set()
        while True:
            blk, bd, fail, n_in, n_mv = layout_block(i, b, ko, cs, skip)
            if not fail:
                break
            o, s, e = min(fail, key=lambda x: len(x[2]) - len(x[1]))
            skip.add(o)
            lack.setdefault(i, []).append(s.decode('cp932'))
        bad += bd
        N_in += n_in; N_mv += n_mv
        d[i * SLOT:(i + 1) * SLOT] = blk
    report.append(f'EVX: 제자리 {N_in}, 재배치 {N_mv}, 고정자리 초과 {len(bad)}, 공간부족 원문유지 {sum(map(len, lack.values()))}')
    for i, v in lack.items():
        report.append(f'  블록 {i}: 공간부족 {len(v)}개')
    json.dump({str(k): v for k, v in lack.items()}, open(os.path.join(HERE, 'text', 'lack.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return bytes(d), bad


def load_exe_ko():
    src = json.load(open(os.path.join(HERE, 'text', 'exe_index.json'), encoding='utf-8'))
    p = os.path.join(HERE, 'text', 'ko', 'exe.json')
    tr = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    out = []
    for x in src:
        a = x['addr'] if isinstance(x['addr'], str) else hex(x['addr'])
        if a in tr:
            out.append((x, tr[a].replace('{E}', '\x1b')))
    return out


def patch_exe_text(exe, items, cs, report):
    e = bytearray(exe)
    n = 0
    for x, ko in items:
        b = cs.enc(ko)
        if len(b) + 1 > x['max'] + 0:
            report.append(f'  EXE 초과 {x["addr"]} {len(b)}>{x["max"]}: {ko}')
            continue
        o = x['off']
        e[o:o + x['max']] = b + b'\0' * (x['max'] - len(b))
        n += 1
    report.append(f'EXE 문자열 {n}/{len(items)}')
    return bytes(e)


def build_dt0(report):
    """gfx/ko/*.png (한글 그림)를 PM.DT0 에 같은 자리로 삽입"""
    import re
    from PIL import Image
    d = bytearray(open(os.path.join(ORIG, 'PM.DT0'), 'rb').read())
    ch = {o: (t, l) for o, t, l in gfx.walk(d)}
    pngs = sorted(glob.glob(os.path.join(HERE, 'gfx', 'ko', 'DT0_*.png')))
    for p in pngs:
        o = int(re.search(r'_([0-9a-f]{7})\.png$', p).group(1), 16)
        t, l = ch[o]
        bpp, w, h, po, _ = gfx.geom(d, o, t, l)
        im = Image.open(p)
        assert im.mode == 'P' and im.size == (w, h), p
        raw = gfx.encode(im.tobytes(), bpp)
        d[po:po + len(raw)] = raw
    report.append(f'DT0 그림 {len(pngs)}장')
    return bytes(d)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GAME, 'Princess Maker - Yumemiru Yousei (Japan) (Track 1) [KR].bin')
    ko = load_ko()
    exe_items = [] if os.environ.get('NOEXE') else load_exe_ko()
    if os.environ.get('EXER'):
        a, z = map(int, os.environ['EXER'].split(':')); exe_items = exe_items[a:z]
    if os.environ.get('NOEVX'): ko = {}
    cs = Charset(list(ko.values()) + [t for _, t in exe_items] + namein.chars())
    report = [f'번역 {len(ko)}개, 한글 음절 {len(cs.chars)}자']
    evx, over = build_evx(ko, cs, report)
    for x in over[:50]:
        report.append('  초과 %s +%d: %r -> %r' % x)
    exe0 = patch_exe_text(open(os.path.join(ORIG, 'PM3.EXE'), 'rb').read(), exe_items, cs, report)
    exe0 = namein.patch(exe0, cs.enc)
    exe = hook.patch_exe(exe0, glyphs(cs.chars))
    tmp = out + '.tmp'
    shutil.copyfile(SRC_BIN, tmp)
    w = Writer(tmp)
    w.replace('/PM.EVX', evx, allow_move=False)
    w.replace('/PM3.EXE', exe)
    w.replace('/PM.DT0', build_dt0(report), allow_move=False)
    w.f.close()
    os.replace(tmp, out)
    print('\n'.join(report))


if __name__ == '__main__':
    main()
