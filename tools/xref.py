import sys,struct,capstone
b=open('orig/PM3.EXE','rb').read();base=0x80040000
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
ins=list(md.disasm(b[0x800:],base))
tg=[int(x,16) for x in sys.argv[1:]]
for i,x in enumerate(ins):
    if x.mnemonic=='lui':
        hi=int(x.op_str.split(',')[1],0);r=x.op_str.split(',')[0]
        for y in ins[i+1:i+6]:
            if r in y.op_str and y.mnemonic in('addiu','lw','sw','lh','lhu','sh','lbu','sb','lb'):
                imm=y.op_str.split(',')[-1].strip()
                imm=imm.split('(')[0]
                try: v=((hi<<16)+int(imm,0))&0xffffffff
                except: continue
                if v in tg: print(hex(v),hex(y.address),y.mnemonic,y.op_str)
                break
