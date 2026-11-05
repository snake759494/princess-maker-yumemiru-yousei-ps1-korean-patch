# PM.EVX 파서: 32KB 블록, 헤더16, 데이터(문자열)+코드. 문자열 참조 = 01 lo hi (블록+16 기준)
import struct,re
OPLEN={0x01:3,0x03:2,0x05:2,0x07:2,0x09:2,0x0a:2,0x0c:3,0x10:3,0x11:3,0x12:3}
SLOT=0x8000
def blocks(d):
    for i in range(len(d)//SLOT):
        b=d[i*SLOT:(i+1)*SLOT]
        if b[:4]!=b'EVX0': yield i,None; continue
        yield i,b
def is_text(s):
    try: t=s.decode('cp932')
    except: return False
    return any(ord(c)>=0x3000 or 0xff61<=ord(c)<=0xff9f for c in t)
def refs(b):
    """블록 내 모든 01 imm16 위치(오프셋)와 값"""
    size=struct.unpack_from('<I',b,4)[0]
    out=[]
    for m in re.finditer(rb'\x01',b[16:size]):
        o=m.start()+16
        out.append((o,struct.unpack_from('<H',b,o+1)[0]))
    return out
BAD=set([0x02,0x08,0x0e,0x13,0x14,0x15,0x16,0x17,0x2a,0x2b]+list(range(0x34,0x3d))+list(range(0x97,0x100)))
def decode(b,start,end):
    o=start;ins=[]
    while o<end:
        op=b[o]
        if op in BAD: return None
        l=OPLEN.get(op,1); ins.append((o,op,b[o+1:o+l])); o+=l
    return ins if o>=end else None
STRB=set([0x0a,0x0d,0x1b,0x09,0x04])|set(range(0x20,0x7f))|set(range(0x80,0xfd))
def code_start(b):
    size=struct.unpack_from('<I',b,4)[0]
    ok=[False]*(size+4); ok[size]=ok[size+1]=ok[size+2]=True
    for o in range(size-1,15,-1):
        op=b[o]
        if op in BAD: continue
        ok[o]=ok[o+OPLEN.get(op,1)]
    o=16
    while o<size:
        e=b.find(b'\x00',o,size)
        if e<0: e=size
        seg=b[o:e]
        if not seg or any(x not in STRB for x in seg):
            return (o,decode(b,o,size)) if ok[o] else (None,None)
        o=e+1
    return None,None
def strings(b,cs):
    out=[];o=16
    while o<cs:
        e=b.index(b'\x00',o); out.append((o,b[o:e])); o=e+1
    return out
STRING_OPS={0x0c,0x1d,0x1e,0x3d,0x41,0x4d,0x4e,0x4f,0x63,0x66,0x71,0x76,0x77,0x84,0x89,0x90,0x91,0x92}
LOADS={0x01,0x03,0x05,0x07}
def stringy(ins,k):
    for o,op,a in ins[k+1:k+8]:
        if op in LOADS: continue
        return op in STRING_OPS
    return False
def ref_map(b,ins):
    """문자열 오프셋 -> 참조 명령 인덱스 목록"""
    m={}
    for k,(o,op,a) in enumerate(ins):
        if op==1: m.setdefault(struct.unpack('<H',a)[0],[]).append(k)
    return m
def reloc_safe(ins,ks):
    if len(ks)==1: return True
    return all(stringy(ins,k) for k in ks)
