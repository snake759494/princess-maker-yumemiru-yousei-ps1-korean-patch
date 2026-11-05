# 고유 문자열을 블록 순서대로 청크로 나눔 -> text/src/evx_NN.json  [{i, ja, max, fit}]
import sys,os,json;sys.path.insert(0,os.path.dirname(__file__))
from evx import *
d=open('orig/PM.EVX','rb').read()
seen={};order=[]
for i,b in blocks(d):
    if b is None: continue
    cs,ins=code_start(b); rm=ref_map(b,ins)
    for o,s in strings(b,cs):
        if not is_text(s): continue
        ja=s.decode('cp932'); safe=reloc_safe(ins,rm.get(o,[]))
        if ja not in seen:
            seen[ja]={'ja':ja,'max':len(s),'fit':not safe,'blk':i}; order.append(ja)
        elif not safe: seen[ja]['fit']=True
N=int(sys.argv[1]) if len(sys.argv)>1 else 16
os.makedirs('text/src',exist_ok=True)
per=(len(order)+N-1)//N
for c in range(N):
    part=order[c*per:(c+1)*per]
    out=[{'i':c*per+k,'ja':seen[j]['ja'].replace('\x1b','{E}'),'max':seen[j]['max'],'fit':seen[j]['fit']} for k,j in enumerate(part)]
    json.dump(out,open(f'text/src/evx_{c:02d}.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(c,len(out),sum(len(x['ja']) for x in out),'blocks',seen[part[0]]['blk'],'-',seen[part[-1]]['blk'])
