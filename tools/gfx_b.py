# -*- coding: utf-8 -*-
"""그래픽 한글화 (담당 B): 별자리/혈액형/아버지 직업 표(015,016 + 사본 024,025), 상태 화면(027~030).

실행: python tools/gfx_b.py   (work 폴더에서)
입력: gfx/out/<이름>.png (원본 인덱스 PNG)  출력: gfx/ko/<같은 이름>.png
색은 인덱스 기준으로만 다룸(팔레트는 원본 그대로 복사).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(W)
OUT = os.path.join(W, 'gfx', 'out')
KO = os.path.join(W, 'gfx', 'ko')
F_SH_B = os.path.join(ROOT, 'SeoulHangangB.ttf')
F_SH_EB = os.path.join(ROOT, 'SeoulHangangEB.ttf')
F_SH_M = os.path.join(ROOT, 'SeoulHangangM.ttf')
F_G7 = os.path.join(W, 'fonts', 'Galmuri7.ttf')

SS = 8  # 슈퍼샘플 배율
REF = '가나다라마바사아자차카타파하힣긹'


def load(name):
    im = Image.open(os.path.join(OUT, name + '.png'))
    return im, np.array(im)


def save(name, ref_im, arr):
    assert arr.shape == np.array(ref_im).shape and arr.max() <= 15
    im = Image.fromarray(arr.astype(np.uint8), 'P')
    im.putpalette(ref_im.getpalette())
    os.makedirs(KO, exist_ok=True)
    im.save(os.path.join(KO, name + '.png'))


def cover_line(text, font_path, h, max_w, wscale=1.0):
    """한 줄을 높이 h 픽셀(한글 글자 몸통 기준)로 렌더 -> 커버리지(0~1) 배열.
    폭이 max_w 를 넘으면 가로로 압축."""
    size = h * SS * 1.25
    f = ImageFont.truetype(font_path, int(size))
    ref = f.getbbox(REF)
    top, bot = ref[1], ref[3]
    bb = f.getbbox(text)
    w = bb[2] - bb[0]
    img = Image.new('L', (w + 4 * SS, bot - top), 0)
    ImageDraw.Draw(img).text((-bb[0] + 2 * SS, -top), text, font=f, fill=255)
    a = np.array(img)
    xs = np.where(a.max(0) > 0)[0]
    a = a[:, xs.min():xs.max() + 1]
    tw = a.shape[1] * h / a.shape[0] * wscale
    tw = max(1, int(round(min(tw, max_w))))
    img = Image.fromarray(a).resize((tw, h), Image.BOX)
    return np.array(img) / 255.0


def cover(lines, font_path, h, max_w, gap=2, align='c', wscale=1.0):
    cs = [cover_line(t, font_path, h, max_w, wscale) for t in lines]
    W_ = max(c.shape[1] for c in cs)
    H_ = sum(c.shape[0] for c in cs) + gap * (len(cs) - 1)
    out = np.zeros((H_, W_))
    y = 0
    for c in cs:
        x = (W_ - c.shape[1]) // 2 if align == 'c' else 0
        out[y:y + c.shape[0], x:x + c.shape[1]] = c
        y += c.shape[0] + gap
    return out


def paste_binary(arr, cov, x, y, fg, thr=0.2):
    m = cov >= thr
    sub = arr[y:y + cov.shape[0], x:x + cov.shape[1]]
    sub[m[:sub.shape[0], :sub.shape[1]]] = fg


# 상태 화면 글자 계조: 진한(획 중심) -> 옅은(외곽) 순. 원본 글자 픽셀의 배경 인접도 통계로 정렬.
RAMP = [5, 3, 10, 12, 13, 4, 2, 8, 9, 11, 14, 7, 6, 1]


def paste_ramp(arr, cov, x, y, bg=15, lo=0.06):
    h, w = cov.shape
    sub = arr[y:y + h, x:x + w]
    c = cov[:sub.shape[0], :sub.shape[1]]
    n = len(RAMP)
    for (yy, xx), v in np.ndenumerate(c):
        if v < lo:
            continue
        k = int((1 - v) * n * 0.95)  # v=1 -> RAMP[0]
        k = min(max(k, 0), n - 1)
        sub[yy, xx] = RAMP[k]


# --------------------------------------------------------------- 015 / 016
ZOD = [['양자리', '황소자리', '쌍둥이자리'],
       ['게자리', '사자자리', '처녀자리'],
       ['천칭자리', '전갈자리', '사수자리'],
       ['염소자리', '물병자리', '물고기자리']]
BLOOD = ['A형', 'B형', 'O형', 'AB형']
JOB = {(4, 0): ['상인'], (4, 1): ['유랑', '예인'], (4, 2): ['은퇴', '기사'], (4, 3): ['방랑자'],
       (5, 0): ['떠돌이', '승려'], (5, 1): ['몰락', '귀족']}
FG, BG = 9, 14


def build_015():
    im, a = load('DT0_015_0060000')
    a = a.copy()
    # 표 영역(x<224, y<240)의 글자를 모두 지움
    a[:240, :224][a[:240, :224] == FG] = BG
    for r in range(4):
        for c in range(3):
            t = ZOD[r][c]
            cov = cover([t], F_SH_EB, 15, 50)
            x0 = c * 56 + 3
            x = x0 + (50 - cov.shape[1]) // 2
            paste_binary(a, cov, x, r * 40 + 11, FG)
        cov = cover([BLOOD[r]], F_SH_EB, 24, 54)
        paste_binary(a, cov, 168 + 1 + (54 - cov.shape[1]) // 2, r * 40 + 9, FG)
    for (r, c), lines in JOB.items():
        x0 = c * 56 + 3
        if len(lines) == 1:
            cov = cover(lines, F_SH_EB, 16, 50)
            y = r * 40 + 12
        else:
            cov = cover(lines, F_SH_EB, 16, 50, gap=5)
            y = r * 40 + 1 + (38 - cov.shape[0]) // 2
        paste_binary(a, cov, x0 + (50 - cov.shape[1]) // 2, y, FG)
    return im, a


def build_copy(orig015, ko015, name):
    """015 의 부분 사본: 행 단위로 원본 015와 완전히 같은 구간만 한글판으로 교체."""
    im, b = load(name)
    out = b.copy()
    H = b.shape[0]
    o = orig015[:H]
    k = ko015[:H]
    # 라벨 칸(56x40)을 폭 8px 세로띠로 나눠, 칸 아래쪽 끝까지 원본 015와 연속으로 같은
    # 행들(=잘린 사본 부분)만 복사. 위쪽이 다른 그림(타이틀 버튼 등)이면 그 부분은 그대로.
    for r in range(6):
        y1 = min(r * 40 + 40, H)
        for x0 in range(0, 224, 8):
            xs = slice(x0, x0 + 8)
            lim = r * 40
            if x0 < 112:  # 타이틀 영어 버튼(NEW GAME 등) 영역(y<206)은 절대 건드리지 않음
                lim = max(lim, 206)
            y0 = y1
            while y0 > lim and (b[y0 - 1, xs] == o[y0 - 1, xs]).all():
                y0 -= 1
            out[y0:y1, xs] = k[y0:y1, xs]
    return im, out


# --------------------------------------------------------------- 상태 화면
def clear(a, x0, y0, x1, y1, bg=15):
    a[y0:y1 + 1, x0:x1 + 1] = bg


def put(a, text, x, y, h=16, max_w=200, font=F_SH_EB, wscale=1.0):
    cov = cover([text], font, h, max_w, wscale=wscale)
    cov = np.clip(cov * 1.6, 0, 1) ** 0.8  # 획을 원본만큼 진하게
    paste_ramp(a, cov, x, y)
    return x + cov.shape[1]


def put_small(a, text, x, y, fg=5):
    f = ImageFont.truetype(F_G7, 8)
    img = Image.new('L', (40, 16), 0)
    ImageDraw.Draw(img).text((0, 0), text, font=f, fill=255)
    m = np.array(img) > 127
    ys, xs = np.where(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sub = a[y:y + m.shape[0], x:x + m.shape[1]]
    sub[m[:sub.shape[0], :sub.shape[1]]] = fg


def build_027():
    im, a = load('DT0_027_0140000')
    a = a.copy()
    rows = [(55, '키'), (78, '체중'), (102, '가슴'), (127, '허리'), (150, '엉덩이')]
    for y, t in rows:
        clear(a, 14, y - 1, 58, y + 19)
        put(a, t, 16, y + 1, max_w=48)
    clear(a, 148, 102, 246, 122)
    put(a, '아버지의 직업', 149, 104, max_w=100)
    return im, a


def build_028():
    im, a = load('DT0_028_014603c')
    a = a.copy()
    left = [(55, '체력'), (79, '지력'), (103, '기력'), (127, '자존심'), (153, '도덕')]
    right = [(7, '기품'), (30, '성품'), (56, '센스'), (79, '매력'), (103, '스트레스'), (127, '무용'), (151, '신뢰도')]
    for y, t in left:
        clear(a, 14, y - 1, 67, y + 19)
        put(a, t, 16, y + 1, max_w=66)
    for y, t in right:
        clear(a, 142, y - 1, 208, y + 19)
        put(a, t, 144, y + 1, max_w=66)
    return im, a


def build_029(name, cat):
    im, a = load(name)
    o = a
    a = a.copy()
    paw = o[119:137, 41:59].copy()
    clear(a, 0, 54, 127, 73)
    put(a, '최다 아르바이트', 1, 56)
    clear(a, 0, 87, 114, 105)
    put(a, '최다 훈련', 1, 89)
    if cat:
        clear(a, 0, 118, 115, 137)
        x = put(a, '아기 고양이', 1, 120)
        sub = a[119:137, x + 4:x + 22]
        m = paw != 15
        sub[m] = paw[m]
        put(a, '이름', x + 25, 120)
    clear(a, 0, 150, 59, 168)
    put(a, '소지금', 1, 152)
    for y in (63, 95):
        clear(a, 247, y - 1, 255, y + 9)
        put_small(a, '회', 248, y + 1)
    return im, a


def main():
    im15, o15 = load('DT0_015_0060000')
    _, k15 = build_015()
    save('DT0_015_0060000', im15, k15)
    save('DT0_024_0120000', im15, k15)  # 015 와 동일한 사본
    for n in ('DT0_016_0068010', 'DT0_025_0128010'):
        im, b = build_copy(o15, k15, n)
        save(n, im, b)
    im, a = build_027(); save('DT0_027_0140000', im, a)
    im, a = build_028(); save('DT0_028_014603c', im, a)
    im, a = build_029('DT0_029_014c078', True); save('DT0_029_014c078', im, a)
    im, a = build_029('DT0_030_01520b4', False); save('DT0_030_01520b4', im, a)


if __name__ == '__main__':
    main()
