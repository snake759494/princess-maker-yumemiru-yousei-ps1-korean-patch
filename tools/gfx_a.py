# -*- coding: utf-8 -*-
"""그래픽 한글화 A: 스케줄 항목표(018), 메인 메뉴 버튼(022=001), 페이즈/일(023, 002).

python tools/gfx_a.py  ->  gfx/ko/DT0_018_00a8010.png, DT0_022_0100000.png, DT0_001_0020000.png,
                           DT0_023_0104010.png, DT0_002_0024010.png
모든 작업은 색 번호(인덱스) 기준. 원본 PNG(gfx/out) 의 팔레트/크기/모드는 그대로 유지.
"""
import os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'gfx', 'out')
KO = os.path.join(ROOT, 'gfx', 'ko')
FD = os.path.dirname(ROOT)
NANUM_EB = os.path.join(FD, 'NanumSquareNeo-dEb.ttf')
NANUM_HV = os.path.join(FD, 'NanumSquareNeo-eHv.ttf')
NANUM_BD = os.path.join(FD, 'NanumSquareNeo-cBd.ttf')
GAL7 = os.path.join(ROOT, 'fonts', 'Galmuri7.ttf')
SS = 8  # 슈퍼샘플 배율


def load(n):
    return Image.open(os.path.join(OUT, n + '.png'))


def save(im, n):
    os.makedirs(KO, exist_ok=True)
    im.save(os.path.join(KO, n + '.png'))


# ---------------------------------------------------------------- 렌더링
def cover(text, font, size, w, h, spacing=0.0, sx=1.0):
    """text 한 줄을 커버리지 맵(dict (x,y)->0..1)과 실제 폭으로. sx: 가로 압축비."""
    F = ImageFont.truetype(font, size * SS)
    glyphs = []
    for ch in text:
        if ch == ' ':
            glyphs.append(None); continue
        bb = F.getbbox(ch)
        glyphs.append(bb)
    # 글자 폭 = advance 대신 잉크 폭 기준(+간격)
    big_w = 0; pos = []
    for ch, bb in zip(text, glyphs):
        if bb is None:
            big_w += size * SS * 0.3; pos.append(None); continue
        pos.append(big_w - bb[0]); big_w += (bb[2] - bb[0]) + spacing * SS
    big_w -= spacing * SS
    asc_top = min(bb[1] for bb in glyphs if bb); asc_bot = max(bb[3] for bb in glyphs if bb)
    im = Image.new('L', (int(big_w) + 2, asc_bot - asc_top + 2), 0)
    d = ImageDraw.Draw(im)
    for ch, p in zip(text, pos):
        if p is not None:
            d.text((p, -asc_top), ch, 255, font=F)
    tw = max(1, round(im.width / SS * sx)); th = max(1, round(im.height / SS))
    sm = im.resize((tw, th), Image.BOX)
    return sm


def blit_bin(px, sm, x0, y0, ink, thr=0.42, clip=None):
    for y in range(sm.height):
        for x in range(sm.width):
            if sm.getpixel((x, y)) / 255 >= thr:
                X, Y = x0 + x, y0 + y
                if clip and not (clip[0] <= X < clip[2] and clip[1] <= Y < clip[3]):
                    continue
                px[X, Y] = ink


def pixfont(text, font=GAL7, size=8):
    """픽셀 폰트를 무보간 1bit 로 -> set of (x,y), (w,h)"""
    F = ImageFont.truetype(font, size)
    im = Image.new('1', (64, 16), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((0, 0), text, 1, font=F)
    bb = im.getbbox(); im = im.crop(bb)
    return {(x, y) for x in range(im.width) for y in range(im.height) if im.getpixel((x, y))}, im.size


# ---------------------------------------------------------------- 1. 스케줄 항목표
SCHED = [  # (열, 행, 줄들)  격자 56x32, 용어는 text/ko/exe.json 과 맞춤
    (0, 0, ['농장']), (1, 0, ['시장']), (2, 0, ['메이드']), (3, 0, ['광산']),
    (0, 1, ['목수']), (1, 1, ['가정', '교사']), (2, 1, ['보모']), (3, 1, ['왕궁']),
    (0, 2, ['경호원']), (1, 2, ['가사', '돕기']), (2, 2, ['술집']), (3, 2, ['호스티스']),
    (0, 3, ['학교']), (1, 3, ['무술', '도장']), (2, 3, ['댄스', '교실']), (3, 3, ['자유', '행동']),
    (0, 4, ['요리', '교실']), (1, 4, ['음악', '교실']), (2, 4, ['미술', '교실']), (3, 4, ['집에서', '쉼']),
    (0, 5, ['예절', '견습']), (1, 5, ['교회']), (2, 5, ['단식', '도장']), (3, 5, ['입원']),
    (2, 6, ['고양이', '간호']), (3, 6, ['바캉스']),
]
S_BG, S_INK = 14, 9


def do_sched():
    n = 'DT0_018_00a8010'
    im = load(n).copy(); px = im.load()
    for c, r, lines in SCHED:
        x0, y0 = c * 56, r * 32
        for y in range(y0, y0 + 32):
            for x in range(x0, x0 + 56):
                if px[x, y] == S_INK:
                    px[x, y] = S_BG
        if len(lines) == 1:
            t = lines[0]
            sp = {2: 8, 3: 2, 4: 0}[len(t)]
            sm = cover(t, NANUM_EB, 17, 54, 18, spacing=sp, sx=1.0 if len(t) < 4 else 0.86)
            blit_bin(px, sm, x0 + (56 - sm.width) // 2, y0 + (32 - sm.height) // 2, S_INK, thr=0.38,
                     clip=(x0, y0, x0 + 56, y0 + 32))
        else:
            sms = [cover(t, NANUM_EB, 15, 54, 14, spacing=1, sx=1.0 if len(t) < 3 else 0.9) for t in lines]
            hh = sum(s.height for s in sms) + 1
            yy = y0 + (32 - hh) // 2
            wmax = max(s.width for s in sms)
            for i, s in enumerate(sms):
                # 원본처럼 둘째 줄을 오른쪽으로 비켜 씀
                if i == 0:
                    xx = x0 + max(1, (56 - wmax) // 2 - 4)
                else:
                    xx = x0 + min(56 - 1 - s.width, (56 - wmax) // 2 + 4 + (wmax - s.width))
                blit_bin(px, s, xx, yy, S_INK, thr=0.40, clip=(x0, y0, x0 + 56, y0 + 32))
                yy += s.height + 1
    save(im, n)


# ---------------------------------------------------------------- 2. 메인 메뉴 버튼
BTN_W = 72            # 버튼 폭(왼쪽 x0, 오른쪽 x72 - 128 에서 잘림)
NORM_ROWS = [32, 56, 80]
SEL_ROWS = [104, 128, 152]
BTN = [  # (행 번호 0..2, 왼/오른, 글)
    (0, 0, '스케줄'), (0, 1, '실행'),
    (1, 0, '쇼핑'), (1, 1, '갈아입기'),
    (2, 0, '대화'), (2, 1, '상태'),
]


def btn_template(px, rows):
    """빈 버튼 바탕 추정: 같은 모양 버튼 여러 개의 다수결. 확신 없는 칸은 그 줄의 최빈값."""
    T = {}
    for dy in range(24):
        sure = {}
        for dx in range(BTN_W):
            v = [px[ox + dx, y0 + dy] for y0 in rows for ox in (0, 72) if ox + dx < 128]
            val, cnt = Counter(v).most_common(1)[0]
            if cnt >= 4 or cnt == len(v):
                sure[dx] = val
        mode = Counter(sure[dx] for dx in range(20, 56) if dx in sure).most_common(1)[0][0]
        for dx in range(BTN_W):
            T[dx, dy] = sure.get(dx, mode)
    return T


def draw_button(px, T, ox, y0, text, sel):
    # 글자 영역(원본 글자가 있던 범위): dy 3..20, 왼쪽 버튼 x8..63 / 잘린 오른쪽 버튼 x80..127
    tx0, tx1 = ox + 8, (ox + 64 if ox == 0 else 128)
    for dy in range(3, 21):
        for x in range(tx0, tx1):
            px[x, y0 + dy] = T[x - ox, dy]
    n = len(text)
    size = {2: 16, 3: 16, 4: 14}[n]
    sp = {2: 10, 3: 3, 4: 0.5}[n]
    sx = {2: 1, 3: 1, 4: 0.92}[n]
    sm = cover(text, NANUM_EB, size, 0, 0, spacing=sp, sx=sx)
    aw = tx1 - tx0 - (2 if ox else 0)
    bx = tx0 + (aw - sm.width) // 2
    by = y0 + 3 + (18 - sm.height) // 2
    cov = {(bx + x, by + y): sm.getpixel((x, y)) / 255
           for x in range(sm.width) for y in range(sm.height)}
    g = lambda X, Y: cov.get((X, Y), 0)
    for Y in range(y0 + 3, y0 + 21):
        for X in range(tx0, tx1):
            c = g(X, Y)
            if not sel:
                # 일반: 어두운 글자 + 오른쪽 아래 밝은 하이라이트(음각 느낌)
                if c >= 0.6: px[X, Y] = 2
                elif c >= 0.38: px[X, Y] = 4
                elif c >= 0.2: px[X, Y] = 8
                elif max(g(X - 1, Y - 1), g(X - 1, Y), g(X, Y - 1)) >= 0.5: px[X, Y] = 14
            else:
                # 선택: 어두운 바탕 위 밝은 글자 + 검은 테두리
                nb = max(g(X + a, Y + b) for a in (-1, 0, 1) for b in (-1, 0, 1))
                if c >= 0.6: px[X, Y] = 14
                elif c >= 0.38: px[X, Y] = 13
                elif c >= 0.2: px[X, Y] = 11
                elif nb >= 0.45: px[X, Y] = 0


SMALL = [  # 하단 작은 글자줄 y208..222 (1bit, 글자색 0 / 바탕 15)
    # (지울 영역 x0,y0,x1,y1, 그릴 글, 글꼴 종류, 위치)
]


def tall(rows):
    return {(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == '#'}


# 원본 큰 글자(15px) 자리에 맞춘 손 도트
G_SE = tall([  # 세 (歳 자리 15x15)
    '.....#......#.#',
    '.....#......#.#',
    '.....#......#.#',
    '.....#......#.#',
    '....#.#.....#.#',
    '....#.#.....#.#',
    '...#...#..###.#',
    '...#...#....#.#',
    '..#.....#...#.#',
    '.#.......#..#.#',
    '#.........#.#.#',
    '............#.#',
    '............#.#',
    '............#.#',
])
G_WOL = tall([  # 월 (月 자리 9x15)
    '..###..#.',
    '.#...#.#.',
    '.#...#.#.',
    '..###..#.',
    '.......#.',
    '######.#.',
    '...#...#.',
    '...#####.',
    '.......#.',
    '#######..',
    '......#..',
    '#######..',
    '#........',
    '#######..',
])
G_NYEON = tall([  # 년 (年 자리 8x15)
    '#.....#.',
    '#.....#.',
    '#...###.',
    '#.....#.',
    '#.....#.',
    '#...###.',
    '#####.#.',
    '......#.',
    '......#.',
    '#.......',
    '#.......',
    '#.......',
    '#.......',
    '#######.',
])
G_IL = tall([  # 일 (日 자리 6x15)
    '.##..#',
    '#..#.#',
    '#..#.#',
    '#..#.#',
    '.##..#',
    '.....#',
    '......',
    '######',
    '.....#',
    '.....#',
    '######',
    '#.....',
    '#.....',
    '######',
])


def put(px, pts, x0, y0, ink):
    for x, y in pts:
        px[x0 + x, y0 + y] = ink


def do_menu():
    src = 'DT0_022_0100000'
    im = load(src).copy(); px = im.load()
    Tn = btn_template(px, NORM_ROWS)
    Ts = btn_template(px, SEL_ROWS)
    for row, side, text in BTN:
        draw_button(px, Tn, side * 72, NORM_ROWS[row], text, False)
        draw_button(px, Ts, side * 72, SEL_ROWS[row], text, True)
    # 하단 작은 글자: 원본 글자 영역만 지우고 다시 그림 (0=글자, 15=바탕)
    def clear(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if px[x, y] == 0: px[x, y] = 15
    clear(48, 208, 62, 222); put(px, G_SE, 48, 208, 0)            # 歳 -> 세
    clear(64, 215, 71, 222)                                        # ヶ -> 개 (작은 글자 자리)
    pts, (w, h) = pixfont('개'); put(px, pts, 64, 222 - h + 1, 0)
    clear(73, 208, 81, 222); put(px, G_WOL, 73, 209, 0)           # 月 -> 월
    clear(88, 208, 96, 222); put(px, G_NYEON, 88, 209, 0)         # 年 -> 년
    clear(97, 208, 102, 222)                                       # 目 -> 비움(1년 05월)
    # 上旬 / 下旬 (위아래 두 칸) -> 상/순, 하/순
    clear(104, 208, 111, 222); clear(112, 208, 121, 222)
    pts, _ = pixfont('상'); put(px, pts, 105, 208, 0)
    pts, _ = pixfont('순'); put(px, pts, 105, 216, 0)
    pts, _ = pixfont('하'); put(px, pts, 114, 208, 0)
    pts, _ = pixfont('순'); put(px, pts, 114, 216, 0)
    clean_caps(px)
    save(im, src)
    save(im, 'DT0_001_0020000')


def clean_caps(px):
    """오른쪽 버튼 끝 조각(16x24, 일반 3개·선택 3개)에 남은 일본어 꼬리 제거:
    같은 종류 3개의 다수결, 정해지지 않은 칸은 오른쪽 이웃 값(일반은 바탕 7)."""
    from collections import Counter
    for kind, cs in (('N', [(0, 176), (16, 176), (0, 200)]), ('S', [(32, 176), (16, 200), (32, 200)])):
        m = [[None] * 16 for _ in range(24)]
        for dy in range(24):
            for dx in range(16):
                v, c = Counter(px[x + dx, y + dy] for x, y in cs).most_common(1)[0]
                m[dy][dx] = v if c >= 2 else None
            for dx in range(15, -1, -1):
                if m[dy][dx] is None:
                    m[dy][dx] = 7 if kind == 'N' else m[dy][dx + 1]
            # 왼쪽 4열은 버튼 몸통과 이어지는 부분: 남은 글자 꼬리를 바탕으로
            if kind == 'N' and 1 <= dy <= 21:
                for dx in range(4):
                    m[dy][dx] = 7
            if kind == 'S' and 4 <= dy <= 19:
                for dx in (1, 0):
                    m[dy][dx] = m[dy][dx + 1]
        for x, y in cs:
            for dy in range(24):
                for dx in range(16):
                    px[x + dx, y + dy] = m[dy][dx]


# ---------------------------------------------------------------- 3. フェーズ / 日
def do_phase(n):
    im = load(n).copy(); px = im.load()
    for y in range(152, 159):          # フェーズ (x97..111)
        for x in range(96, 112):
            if px[x, y] == 3: px[x, y] = 15
    for y in range(160, 167):          # 日 (x97..102)
        for x in range(96, 104):
            if px[x, y] == 3: px[x, y] = 15
    pts, (w, h) = pixfont('단계'); put(px, pts, 97, 152, 3)
    pts, (w, h) = pixfont('일'); put(px, pts, 97, 160, 3)
    save(im, n)


if __name__ == '__main__':
    do_sched()
    do_menu()
    do_phase('DT0_023_0104010')
    do_phase('DT0_002_0024010')
    print('ok')
