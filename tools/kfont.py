# 한글 16x15 1bpp(BIOS Krom 형식, 행당 2바이트 MSB 우선) 글리프 생성
from PIL import Image,ImageDraw,ImageFont
import os
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT=os.path.join(ROOT,'NanumSquareNeo-bRg.ttf')
_ft={}
def font(size,path=FONT):
    k=(path,size)
    if k not in _ft: _ft[k]=ImageFont.truetype(path,size)
    return _ft[k]
def render_old(ch,size=15,thr=110,path=FONT,w=16,h=15,dx=0,dy=0):
    ft=font(size,path)
    im=Image.new('L',(w*2,h*2),0); d=ImageDraw.Draw(im)
    bb=d.textbbox((0,0),ch,font=ft)
    gw=bb[2]-bb[0]; gh=bb[3]-bb[1]
    # 가로 가운데, 세로는 셀 높이 기준 정렬
    x=(w-gw)//2-bb[0]+dx
    asc,desc=ft.getmetrics()
    y=(h-(asc+desc))//2+dy
    d.text((x,y),ch,font=ft,fill=255)
    return im.crop((0,0,w,h)).point(lambda v:255 if v>=thr else 0)
def encode(im):
    out=bytearray()
    w,h=im.size
    for y in range(h):
        r=0
        for x in range(16):
            if x<w and im.getpixel((x,y)): r|=0x8000>>x
        out+=r.to_bytes(2,'big')
    return bytes(out)

GALMURI7 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'Galmuri7.ttf')


def render_small(ch, size=8, dx=0, dy=0):
    """소형 한글: 8x8 칸(16x15 비트맵의 좌상단)에 갈무리7 (잉크 경계 기준 가운데)"""
    ft = font(size, GALMURI7)
    im = Image.new('L', (32, 32), 0); d = ImageDraw.Draw(im)
    d.text((8, 8), ch, font=ft, fill=255)
    im = im.point(lambda v: 255 if v >= 128 else 0)
    bb = im.getbbox()
    out = Image.new('L', (16, 15), 0)
    if bb:
        g = im.crop(bb)
        x = max(0, (8 - g.width) // 2) + dx
        y = max(0, (8 - g.height + 1) // 2) + dy
        out.paste(g.crop((0, 0, min(g.width, 8), min(g.height, 8))), (x, y))
    return out


def small_vblock(chars, cols=32, rows=6):
    """FONT8 스타일(행 그라데이션 3/2/1, 그림자 4, 투명 5) 8x8 4bpp 블록(64x48 hw) 생성"""
    W, H = cols * 8, rows * 8
    pix = [[5] * W for _ in range(H)]
    for k, ch in enumerate(chars):
        cx, cy = (k % cols) * 8, (k // cols) * 8
        ft = font(8, GALMURI7)
        im = Image.new('L', (32, 32), 0); ImageDraw.Draw(im).text((8, 8), ch, font=ft, fill=255)
        im = im.point(lambda v: 255 if v >= 128 else 0)
        bb = im.getbbox()
        on = [[False] * 8 for _ in range(8)]
        if bb:
            gw, gh = bb[2] - bb[0], bb[3] - bb[1]
            ox = max(0, (7 - gw) // 2); oy = max(0, (7 - gh) // 2)
            for y in range(min(gh, 7)):
                for x in range(min(gw, 7)):
                    if im.getpixel((bb[0] + x, bb[1] + y)):
                        on[oy + y][ox + x] = True
        # 7x7 안에 맞추고(그림자 1px 확보) 그림자
        for y in range(8):
            for x in range(8):
                if on[y][x] and x < 7 and y < 7:
                    pix[cy + y][cx + x] = 3 if y == 0 else 2 if y <= 2 else 1
        for y in range(8):
            for x in range(8):
                if pix[cy + y][cx + x] == 5 and x > 0 and y > 0 and on[y - 1][x - 1] and x - 1 < 7 and y - 1 < 7:
                    pix[cy + y][cx + x] = 4
    out = bytearray()
    for y in range(H):
        for x in range(0, W, 2):
            out.append(pix[y][x] | (pix[y][x + 1] << 4))
    return bytes(out)


def ankfont_ext(vblock, cols=32, rows=6):
    """64x48hw 4bpp 블록 -> ANKFONT.DAT 추가분(인덱스 256~351, 블록당 32바이트 x2)"""
    out = bytearray()
    rowbytes = cols * 8 // 2          # 128바이트/행
    for i in range(16 * rows):
        r, c = i // 16, i % 16
        for half in (0, 1):
            cell = c * 2 + half
            for y in range(8):
                o = (r * 8 + y) * rowbytes + cell * 4
                out += vblock[o:o + 4]
    return bytes(out)



def tac8_cells(tim_data, w_hw, cells):
    """전술 8x8 글꼴 TIM(4bpp, 투명0/글자2/그림자1) 데이터에 {코드:글자} 셀을 그려 넣음"""
    d = bytearray(tim_data)
    def put(x, y, v):
        o = y * w_hw * 2 + x // 2
        sh = (x & 1) * 4
        d[o] = (d[o] & ~(15 << sh)) | (v << sh)
    ft = font(8, GALMURI7)
    for code, ch in cells.items():
        cx, cy = (code & 31) * 8, (code >> 5) * 8
        im = Image.new('L', (32, 32), 0); ImageDraw.Draw(im).text((8, 8), ch, font=ft, fill=255)
        im = im.point(lambda v: 255 if v >= 128 else 0)
        bb = im.getbbox()
        on = [[False] * 8 for _ in range(8)]
        if bb:
            gw, gh = min(bb[2] - bb[0], 7), min(bb[3] - bb[1], 7)
            ox = (7 - gw) // 2; oy = 1
            for y in range(gh):
                for x in range(gw):
                    if im.getpixel((bb[0] + x, bb[1] + y)) and oy + y < 8:
                        on[oy + y][ox + x] = True
        for y in range(8):
            for x in range(8):
                v = 2 if on[y][x] else (1 if (x > 0 and on[y][x - 1]) or (y > 0 and on[y - 1][x]) else 0)
                put(cx + x, cy + y, v)
    return bytes(d)


GALMURI14 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'Galmuri14.ttf')


def render(ch, w=16, h=15):
    """본문 한글: 갈무리14 원래 크기(15px) 비트맵 그대로, 확대·축소·안티에일리어스 없음"""
    ft = font(15, GALMURI14)
    im = Image.new('1', (w, h), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    gw = d.textlength(ch, font=ft)
    d.text(((w - int(gw)) // 2, -1), ch, 1, font=ft)
    return im.convert('L')
