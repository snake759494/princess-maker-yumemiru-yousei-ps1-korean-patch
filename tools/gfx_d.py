# -*- coding: utf-8 -*-
"""그래픽 한글화 D: 달력 월(006)/요일(008), HOLIDAY(011), PHASE START/COMPLETE 판(019),
타이틀 메뉴 버튼(016, 025 — gfx_b.py 결과 위에 덮어씀; gfx_b.py 다음에 실행).

python tools/gfx_d.py  ->  gfx/ko/DT0_006_0028c88.png, DT0_008_002d8a8.png, DT0_011_002fa04.png,
                           DT0_019_00b0020.png, DT0_016_0068010.png, DT0_025_0128010.png
모든 작업은 색 인덱스 기준(팔레트 무시).
"""
import os
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(W, 'gfx', 'out')
KO = os.path.join(W, 'gfx', 'ko')
FD = os.path.dirname(W)
GAL7 = os.path.join(W, 'fonts', 'Galmuri7.ttf')
GAL9 = os.path.join(W, 'fonts', 'Galmuri9.ttf')
HV = os.path.join(FD, 'NanumSquareNeo-eHv.ttf')
SEB = os.path.join(FD, 'SeoulHangangEB.ttf')
SS = 8


def load(n, d=OUT):
    im = Image.open(os.path.join(d, n + '.png'))
    return im, np.array(im)


def save(n, ref, a):
    assert a.max() <= 15
    im = Image.fromarray(a.astype(np.uint8), 'P')
    im.putpalette(ref.getpalette())
    os.makedirs(KO, exist_ok=True)
    im.save(os.path.join(KO, n + '.png'))


def pix(text, font=GAL7, size=8):
    F = ImageFont.truetype(font, size)
    im = Image.new('1', (128, 16), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((0, 0), text, 1, font=F)
    return np.array(im.crop(im.getbbox()), bool)


def blocky(text, font, size, sx, sy, gap, shear=0.0):
    """픽셀 폰트 글자별 1bit -> 정수배 확대(sx, sy) 후 gap 간격으로 붙임. 위 정렬은 글꼴 기준선 유지."""
    F = ImageFont.truetype(font, size)
    im = Image.new('1', (128, 24), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((0, 0), text, 1, font=F)
    bb = im.getbbox(); full = np.array(im, bool)[bb[1]:bb[3]]
    parts = []
    x = 0
    for c in text:
        w = int(F.getlength(c))
        seg = full[:, x:x + w]; x += w
        cols = np.nonzero(seg.any(0))[0]
        if len(cols):
            parts.append(seg[:, cols[0]:cols[-1] + 1])
    h = full.shape[0]
    tw = sum(p.shape[1] * sx for p in parts) + gap * (len(parts) - 1)
    m = np.zeros((h * sy, tw), bool); x = 0
    for p in parts:
        m[:, x:x + p.shape[1] * sx] = np.kron(p, np.ones((sy, sx), bool)); x += p.shape[1] * sx + gap
    if shear:
        H = m.shape[0]; o = np.zeros((H, tw + int(shear * H) + 1), bool)
        for y in range(H):
            sh = int(round(shear * (H - 1 - y))); o[y, sh:sh + tw] = m[y]
        m = o
    return m


def render(text, font, h, cw=None, gap=1, shear=0.0, thr=0.5, bx=0):
    """글자별로 잉크 높이 h 에 맞춰 렌더 (cw: 글자당 폭 강제). shear: 이탤릭 기울기(px/px)."""
    F = ImageFont.truetype(font, h * SS * 1.3)
    boxes = [F.getbbox(c) for c in text]
    top = min(b[1] for b in boxes); bot = max(b[3] for b in boxes)
    parts = []
    for c, b in zip(text, boxes):
        im = Image.new('L', (b[2] - b[0] + 4, bot - top + 4), 0)
        ImageDraw.Draw(im).text((2 - b[0], 2 - top), c, 255, font=F)
        im = im.crop((2, 2, 2 + b[2] - b[0], 2 + bot - top))
        w = cw or max(1, round(im.width * h / im.height))
        parts.append(np.array(im.resize((w, h), Image.BOX)) / 255.0)
    tw = sum(p.shape[1] for p in parts) + gap * (len(parts) - 1)
    cov = np.zeros((h, tw)); x = 0
    for p in parts:
        cov[:, x:x + p.shape[1]] = p; x += p.shape[1] + gap
    m = cov >= thr
    for _ in range(bx):   # 가로로 굵게
        m = np.pad(m, ((0, 0), (0, 1))); m[:, 1:] |= m[:, :-1].copy()
    if shear:
        ext = int(abs(shear) * h) + 1
        tw = m.shape[1]; o = np.zeros((h, tw + ext), bool)
        for y in range(h):
            s = int(round(shear * (h - 1 - y)))
            o[y, s:s + tw] = m[y]
        m = o
    return m


def dil(m):
    o = m.copy()
    o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
    return o


# ------------------------------------------------------------- 006 / 008 달력
def calendar(name, ink, labels, bold):
    """PNG는 64폭으로 보이지만 실제 텍스처는 32폭(한 PNG 행 = 실제 2행). 칸 = 32x16."""
    im, a0 = load(name)
    a = a0.reshape(-1, 32).copy()
    for k, t in enumerate(labels):
        c = a[k * 16:k * 16 + 16]
        inkv = max(ink, key=lambda v: (c[2:13, 2:30] == v).sum())
        area = c[1:13, 2:30]
        bgv = Counter(int(v) for v in area.ravel() if v not in ink).most_common(1)[0][0]
        area[:] = bgv
        low = c[13:15, 1:31]; low[np.isin(low, ink)] = bgv
        m = pix(t, GAL9, 10)
        h, w = m.shape
        cx = 2 + (28 - w) // 2
        cy = 2 + (11 - h) // 2
        c[cy:cy + h, cx:cx + w][m] = inkv
    save(name, im, a.reshape(a0.shape))


# ------------------------------------------------------------- 011 HOLIDAY
def vec_mask(text, h, wmax=118, asp=1.9):
    """굵은 고딕(NanumSquareNeo Heavy)을 크게 렌더 후 높이 h 로 줄여 1bit 마스크"""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'NanumSquareNeo-eHv.ttf'), 160)
    bb = f.getbbox(text)
    im = Image.new('L', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), 0)
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), text, 255, font=f)
    im = im.crop(im.getbbox())
    w = round(im.width * h / im.height * asp)
    im = im.resize((min(w, wmax), h), Image.LANCZOS)
    return np.array(im) > 110

def holiday():
    name = 'DT0_011_002fa04'
    im, a = load(name)
    o = a.copy()
    m = vec_mask('휴 일', 14)
    for x0 in (0, 128):
        src = o[0:16, x0:x0 + 128]
        inner = src <= 0xa
        reg = a[0:16, x0:x0 + 128]
        reg[:] = 0xf
        G = np.zeros((16, 128), bool)
        gx = (128 - m.shape[1]) // 2
        G[1:15, gx:gx + m.shape[1]] = m
        reg[dil(G) & ~G] = 0xe
        for y in range(16):
            xs = np.nonzero(inner[y])[0]
            if not len(xs):
                xs = np.nonzero(inner[max(1, min(14, y))])[0]
            for x in np.nonzero(G[y])[0]:
                reg[y, x] = src[y, xs[np.abs(xs - x).argmin()]]
    save(name, im, a)


# ------------------------------------------------------------- 019 PHASE START / COMPLETE
def texture_fill(reg, rows, seed):
    """reg 의 각 열을 rows(글자 없는 행 번호들) 중 하나의 같은 열 값으로 채움(결정적 의사난수)."""
    rng = np.random.RandomState(seed)
    for y in range(reg.shape[0]):
        for x in range(reg.shape[1]):
            xx = min(reg.shape[1] - 1, max(0, x + rng.randint(-3, 4)))
            reg[y, x] = rows[rng.randint(len(rows))][xx]


def paint_rows(dst, G, src, is_ink):
    """G 픽셀을 같은 행에서 가장 가까운 원본 글자 픽셀 색으로."""
    for y in range(G.shape[0]):
        xs = np.nonzero(is_ink[y])[0]
        yy = y
        while not len(xs):
            yy = yy + 1 if yy < G.shape[0] - 1 else 0
            xs = np.nonzero(is_ink[yy])[0]
        for x in np.nonzero(G[y])[0]:
            dst[y, x] = src[yy, xs[np.abs(xs - x).argmin()]]


def phase():
    name = 'DT0_019_00b0020'
    im, a = load(name)
    o = a.copy()
    l1 = vec_mask('페이즈', 9, 84, 1.6)
    l2 = vec_mask('시작', 9, 84, 1.6)
    for X in (0, 128):
        # --- PHASE / START: 판 x0~95, y40~67. 글자 영역 x6~89, y44~63
        P = o[40:68, X:X + 96]
        rows = [P[3], P[24]]                    # y43, y64: 글자 없는 행
        ink = P >= 0xb                          # 밝은 글자(b~f)
        reg = a[44:64, X + 6:X + 90]
        texture_fill(reg, [r[6:90] for r in rows], 19 + X)
        G = np.zeros((20, 84), bool)
        G[0:l1.shape[0], (84 - l1.shape[1]) // 2:][:, :l1.shape[1]] = l1
        G[11:11 + l2.shape[0], (84 - l2.shape[1]) // 2:][:, :l2.shape[1]] = l2
        S = np.zeros_like(G); S[1:, 1:] = G[:-1, :-1]; S &= ~G   # 오른쪽 아래 그림자
        reg[S] = 4
        tmp = reg.copy()
        paint_rows(tmp, G, P[4:24, 6:90], ink[4:24, 6:90])
        reg[G] = tmp[G]
        # --- COMPLETE: 조각 A(x96~127,y40~67) + 조각 B(x0~63,y108~135) 를 이어 붙인 96x28 캔버스
        C = np.concatenate([o[40:68, X + 96:X + 128], o[108:136, X:X + 64]], 1)
        N = C.copy()
        cink = C <= 2
        rows = [C[r] for r in (5, 6, 7, 8, 19, 20, 21, 22, 23)]
        texture_fill(N[7:21, 6:88], [r[6:88] for r in rows], 7 + X)
        t = vec_mask('완 료', 12, 76, 1.7)
        G = np.zeros((28, 96), bool)
        gx = (96 - t.shape[1]) // 2
        G[8:8 + t.shape[0], gx:gx + t.shape[1]] = t
        E = dil(G) & ~G & (np.arange(96)[None, :] >= 6) & (np.arange(96)[None, :] < 88)
        E[:9] = False; E[20:] = False
        tmp = N.copy()
        paint_rows(tmp[8:20], G[8:20], C[8:20], cink[8:20])
        N[G] = tmp[G]
        a[40:68, X + 96:X + 128] = N[:, :32]
        a[108:136, X:X + 64] = N[:, 32:]
    save(name, im, a)


# ------------------------------------------------------------- 016 / 025 타이틀 메뉴 버튼
MENU = [  # (지울 영역 x0,y0,x1,y1), [(줄, 줄 영역 x0,x1,y0)]
    ((5, 130, 58, 167), [('새로', 8, 57, 132), ('시작', 8, 57, 150)]),
    ((60, 130, 114, 167), [('이어서', 64, 113, 132), ('하기', 64, 113, 150)]),
    ((3, 170, 56, 206), [('스태프', 5, 53, 181)]),
    ((57, 168, 114, 206), [('환경', 60, 113, 172), ('설정', 60, 113, 190)]),
]


def title(name):
    src = os.path.join(KO, name + '.png')
    im, a = load(name, KO if os.path.exists(src) else OUT)
    for (x0, y0, x1, y1), lines in MENU:
        r = a[y0:y1, x0:x1]; r[r == 9] = 0xe
        for t, lx0, lx1, ly in lines:
            m = render(t, SEB, 15, gap=2, thr=0.4, bx=1 if len(t) <= 2 else 0)
            hh = 15
            while m.shape[1] > lx1 - lx0:   # 넘치면 글자 크기를 줄임
                hh -= 1; m = render(t, SEB, hh, gap=1, thr=0.4)
            h, w = m.shape
            x = lx0 + (lx1 - lx0 - w) // 2
            ly += (15 - h) // 2
            a[ly:ly + h, x:x + w][m] = 9
    save(name, im, a)


def main():
    calendar('DT0_006_0028c88', (0xc,), ['%d월' % i for i in range(1, 13)], False)
    calendar('DT0_008_002d8a8', (0xe, 0xc), list('월화수목금토일일'), False)
    holiday()
    phase()
    for n in ('DT0_016_0068010', 'DT0_025_0128010'):
        title(n)


if __name__ == '__main__':
    main()
