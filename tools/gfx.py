# -*- coding: utf-8 -*-
"""PM.DT0 / PM.PCC / PM.MAP 그래픽 추출/재삽입 도구.

파일 형식 (리틀엔디언, 압축 없음):
  파일 = 청크의 나열. 청크 그룹은 0x800(섹터) 경계에서 시작하며 그 사이는 0 패딩.
  청크 = u32 type(상위 바이트 0x80) + u32 len + body[len]
    0x80000004  8bpp 이미지   body = u16 x,y,w,h (x,y=VRAM 좌표(hword), w,h=픽셀) + w*h 바이트
    0x80000014  4bpp 이미지   body = u16 x,y,w,h (w=픽셀) + w*h/2 바이트 (하위 니블=왼쪽 픽셀)
    0x80000016  4bpp 타일셋   body = u16 x,y + u8 bw,h,count,flag + count*(bw*h) 바이트
                               (타일 하나 = 폭 bw*2 픽셀 x h, 4bpp)
    0x80000007  MAP 전용 속성맵(16px 셀당 1바이트) -> 이미지 아님
    0x80000006  CLUT          body = u16 index,count + count*u16 (PS1 15bit BGR)
    0x80000005  타일맵(MAP), 0x18/0x1a 스프라이트 조립 데이터(PCC), 0x24(DT0) -> 이미지 아님
사용법:
  python tools/gfx.py list   orig/PM.DT0
  python tools/gfx.py export orig/PM.DT0 gfx/out            -> DT0_NNN_<offset>.png
  python tools/gfx.py import orig/PM.DT0 수정본.DT0 a.png b.png ...
     (파일명의 _<offset> 으로 위치를 찾음. PNG 는 export 때와 같은 크기의 인덱스(P) PNG,
      4bpp 는 인덱스 0~15만. 팔레트 자체는 무시되고 인덱스만 기록 -> 바이트 길이 불변)
"""
import struct, sys, os, re
from PIL import Image

IMG_TYPES = (0x80000004, 0x80000014, 0x80000016)


def walk(d):
    o = 0; out = []
    while o + 8 <= len(d):
        t, l = struct.unpack_from('<II', d, o)
        if t >> 24 != 0x80 or o + 8 + l > len(d):
            o = (o + 0x800) & ~0x7ff
            continue
        out.append((o, t, l)); o += 8 + l
    return out


def c15(v):
    return ((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31)


def geom(d, o, t, l):
    """-> (bpp, width, height, pixel_offset, info)"""
    b = o + 8
    if t == 0x80000016:
        x, y, bw, h, n, fl = struct.unpack_from('<HHBBBB', d, b)
        return 4, bw * 2, h * n, b + 8, 'x=%d y=%d tile=%dx%d n=%d' % (x, y, bw * 2, h, n)
    x, y, w, h = struct.unpack_from('<4H', d, b)
    bpp = 4 if t == 0x80000014 else 8
    return bpp, w, h, b + 8, 'x=%d y=%d' % (x, y)


def palettes(d, chunks):
    """각 이미지 청크에 같은 그룹(0x20000 블록 이전 패딩까지)의 CLUT 추정 배정."""
    res = {}
    groups = []; cur = []; last = -1
    for c in chunks:
        if last >= 0 and c[0] != last:
            groups.append(cur); cur = []
        cur.append(c); last = c[0] + 8 + c[2]
    groups.append(cur)
    for g in groups:
        cl = []
        for o, t, l in g:
            if t == 0x80000006:
                i, n = struct.unpack_from('<HH', d, o + 8)
                cl.append([c15(v) for v in struct.unpack_from('<%dH' % n, d, o + 12)])
        for o, t, l in g:
            if t not in IMG_TYPES:
                continue
            bpp = geom(d, o, t, l)[0]
            p = None
            if bpp == 8:
                big = [c for c in cl if len(c) >= 256]
                if big: p = big[0][:256]
            else:
                sm = [c for c in cl if len(c) == 16]
                if sm: p = sm[0]
            if p is None:
                k = 256 if bpp == 8 else 16
                p = [(i * 255 // (k - 1),) * 3 for i in range(k)]
            res[o] = p
    return res


def decode(d, o, t, l):
    bpp, w, h, po, _ = geom(d, o, t, l)
    if bpp == 8:
        return bytes(d[po:po + w * h]), w, h
    raw = d[po:po + w * h // 2]
    px = bytearray(w * h)
    for i, v in enumerate(raw):
        px[2 * i] = v & 15; px[2 * i + 1] = v >> 4
    return bytes(px), w, h


def encode(px, bpp):
    if bpp == 8:
        return bytes(px)
    if max(px) > 15:
        raise ValueError('4bpp 이미지에 16 이상 인덱스')
    return bytes(px[i] | (px[i + 1] << 4) for i in range(0, len(px), 2))


def tag(path):
    return os.path.basename(path).split('.')[-1].upper()


def cmd_list(path):
    d = open(path, 'rb').read()
    for n, (o, t, l) in enumerate(c for c in walk(d) if c[1] in IMG_TYPES):
        bpp, w, h, po, info = geom(d, o, t, l)
        print('%3d off=%07x type=%02x %dbpp %dx%d %s' % (n, o, t & 0xff, bpp, w, h, info))


def cmd_export(path, outdir):
    d = open(path, 'rb').read(); os.makedirs(outdir, exist_ok=True)
    ch = walk(d); pal = palettes(d, ch)
    for n, (o, t, l) in enumerate(c for c in ch if c[1] in IMG_TYPES):
        px, w, h = decode(d, o, t, l)
        im = Image.frombytes('P', (w, h), px)
        flat = [v for c in pal[o] for v in c]
        im.putpalette(flat + [0] * (768 - len(flat)))
        im.save(os.path.join(outdir, '%s_%03d_%07x.png' % (tag(path), n, o)))


def cmd_import(src, dst, pngs):
    d = bytearray(open(src, 'rb').read())
    ch = {o: (t, l) for o, t, l in walk(d)}
    for p in pngs:
        m = re.search(r'_([0-9a-f]{7})\.png$', p, re.I)
        o = int(m.group(1), 16); t, l = ch[o]
        bpp, w, h, po, _ = geom(d, o, t, l)
        im = Image.open(p)
        if im.mode != 'P' or im.size != (w, h):
            raise SystemExit('%s: 인덱스(P) PNG, 크기 %dx%d 이어야 함' % (p, w, h))
        raw = encode(im.tobytes(), bpp)
        d[po:po + len(raw)] = raw
        print('삽입', p, hex(o))
    assert len(d) == os.path.getsize(src)
    open(dst, 'wb').write(d)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'list': cmd_list(a[1])
    elif a[0] == 'export': cmd_export(a[1], a[2])
    elif a[0] == 'import': cmd_import(a[1], a[2], a[3:])
