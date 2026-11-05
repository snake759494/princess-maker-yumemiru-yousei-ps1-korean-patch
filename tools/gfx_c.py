# -*- coding: utf-8 -*-
"""DT0 013/014/032/033 (선물·아이템·요리·그림 이름 라벨) 그래픽 한글화.
실행: python tools/gfx_c.py   (work 폴더에서)  ->  gfx/ko/<원본 파일명>.png
원본 라벨은 1색 비트맵 글씨(인덱스 9) + 단색 배경(13/14: 15, 032/033: 14), 그리드 칸 단위.
각 칸(인덱스 0 영역 제외)을 배경으로 지우고 갈무리 픽셀 폰트(1bit)로 다시 그린다.
"""
import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(W, 'gfx', 'out')
KO = os.path.join(W, 'gfx', 'ko')
F9 = ImageFont.truetype(os.path.join(W, 'fonts', 'Galmuri9.ttf'), 10)
F7 = ImageFont.truetype(os.path.join(W, 'fonts', 'Galmuri7.ttf'), 8)
BIG = os.path.join(os.path.dirname(W), 'NanumSquareNeo-eHv.ttf')
FG = 9

# 칸별 라벨('/' = 줄바꿈)
T013 = [
    ['봉제인형', '시집', '부케', '진수성찬'],
    ['활동복', '호화/드레스', '멋진 옷', '스마일'],
    ['어둠의 옷', '남국의/드레스', '토끼 옷', '요정의 꿀'],
    ['지혜의/열매', '영광의/과실', '질서의/씨앗', '고귀한/샘물'],
]
T014 = [
    ['찻잔', '새 구두', '양말', '손수건'],
    ['주판', '수첩', '만년필', '하모니카'],
    ['펠트 모자', '피리', '탁발/주머니', '염주'],
    ['법의', '망토', '가문/식탁보', '깃털장식'],
    ['단검', '칼자루/장식', '방패', '하얀 기타'],
    ['검은 가죽/점퍼', '빨간/네커치프', '상냥함의/빗', '예술의 엿'],
    ['매혹의/향수', '무신의 검', '평상복', '시원한 옷'],
    ['따뜻한 옷', '고양이 옷', '불량배 옷', None],
]
T032 = [
    ['계란/프라이', '주먹밥', '삶은 달걀', '햄 샐러드'],
    ['스파게티', '카레라이스', '햄버그', '중화/국수/수프'],
    ['흑돼지/커틀릿', '연어/뫼니에르', '청둥오리/포토푀', '필레미뇽/스테이크'],
    ['송아지/오렌지/소스', '보리새우/새콤달콤/버터소테', '농어/피카타/소악마풍', '혀가자미/파이 감싸기/왕조풍'],
    ['청둥오리/와인 조림/해안풍', '아귀/활어회', '꽃', '꽃병의 꽃'],
    ['새해 일출', '산악 풍경', '달리는 말', '요정과 꽃밭'],
]


def _mask(text, font):
    m = font.getmask(text, mode='1')
    return np.array(m, dtype=np.uint8).reshape(m.size[1], m.size[0]) > 0


def glyph_mask(text, font, bold=False, gap=3):
    """단어 사이 간격을 gap px 로 좁혀 렌더. bold 면 오른쪽 1px 겹쳐 굵게."""
    ws = [_mask(w, font) for w in text.split(' ')]
    h = max(m.shape[0] for m in ws)
    a = np.zeros((h, sum(m.shape[1] for m in ws) + gap * (len(ws) - 1) + (1 if bold else 0)), bool)
    x = 0
    for m in ws:
        a[h - m.shape[0]:, x:x + m.shape[1]] |= m
        x += m.shape[1] + gap
    if bold:
        a[:, 1:] |= a[:, :-1].copy()
    return a


def draw_label(a, x0, y0, cw, ch, text, bg, pad=1, bold=False):
    # 칸 지우기 (인덱스 0 = 미사용 영역은 보존)
    reg = a[y0:y0 + ch, x0:x0 + cw]
    reg[reg != 0] = bg
    if text is None:
        return
    lines = text.split('/')
    opts = ((F9, 12, True), (F9, 12, False), (F7, 9, False)) if bold else ((F9, 12, False), (F7, 9, False))
    for font, lh, bd in opts:
        ms = [glyph_mask(l, font, bd) for l in lines]
        tw = max(m.shape[1] for m in ms)
        if tw <= cw - 2 * pad and lh * len(lines) <= ch - 2:
            break
    else:
        raise SystemExit('too long: ' + text)
    gh = ms[0].shape[0]
    total = lh * (len(lines) - 1) + gh
    y = y0 + (ch - total + 1) // 2
    for m in ms:
        x = x0 + (cw - m.shape[1] + 1) // 2
        h, w = m.shape
        sub = a[y:y + h, x:x + w]
        sub[m] = FG
        y += lh


def grid(a, table, cw, ch, bg, bold=False):
    for r, row in enumerate(table):
        for c, t in enumerate(row):
            draw_label(a, c * cw, r * ch, cw, ch, t, bg, bold=bold)


def load(n):
    return Image.open(os.path.join(OUT, n + '.png'))


def save(a, ref, n):
    im = Image.fromarray(a.astype(np.uint8), 'P')
    im.putpalette(ref.getpalette())
    im.save(os.path.join(KO, n + '.png'))


def main():
    os.makedirs(KO, exist_ok=True)
    n = 'DT0_013_0047e1c'; im = load(n); a = np.array(im)
    grid(a, T013, 56, 32, 15); save(a, im, n)

    n = 'DT0_014_004be58'; im = load(n); a = np.array(im)
    grid(a, T014, 56, 32, 15); save(a, im, n)

    n = 'DT0_032_0167e1c'; im = load(n); a32o = np.array(im); a = a32o.copy()
    grid(a, T032, 56, 40, 14); save(a, im, n)

    # 033: 032 윗부분 128줄 사본 + 왼쪽 위 'お金' 칸(배경 15)
    n2 = 'DT0_033_016fe58'; im2 = load(n2); o33 = np.array(im2)
    b = a[:128].copy()
    diff = o33 != a32o[:128]
    b[diff] = o33[diff]
    b[0:32, 0:56] = 15
    # 큰 글자 '돈' (원본 お金: 높이 약 22px)
    S = 8
    big = Image.new('L', (56 * S, 32 * S), 0)
    ImageDraw.Draw(big).text((28 * S, 17 * S), '돈', font=ImageFont.truetype(BIG, 24 * S), fill=255, anchor='mm')
    m = np.array(big.resize((56, 32), Image.BOX)) >= 110
    b[0:32, 0:56][m] = FG
    save(b, im2, n2)


if __name__ == '__main__':
    main()
