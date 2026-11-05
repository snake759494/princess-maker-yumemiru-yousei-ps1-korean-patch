# PM.EVX 텍스트 추출 -> text/ja/evx.json  [{id, blk, off, ja}]
import sys,json,os;sys.path.insert(0,os.path.dirname(__file__))
from evx import *
d=open('orig/PM.EVX','rb').read()
out=[]
for i,b in blocks(d):
    if b is None: continue
    cs,ins=code_start(b)
    for o,s in strings(b,cs):
        if is_text(s):
            out.append({'id':f'{i:03d}_{o:04x}','blk':i,'off':o,'len':len(s),'ja':s.decode('cp932')})
os.makedirs('text/ja',exist_ok=True)
json.dump(out,open('text/ja/evx.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
u={}
for x in out: u.setdefault(x['ja'],[]).append(x['id'])
print(len(out),'unique',len(u),'bytes',sum(x['len'] for x in out),'unique bytes',sum(len(k.encode('cp932')) for k in u))
