import struct,capstone
b=open('orig/PM3.EXE','rb').read()
def w(a): return struct.unpack_from('<I',b,a-0x80040000+0x800)[0]
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
h=[w(0x8009d058+4*i) for i in range(256)]
def fn(a):
    out=[]
    for x in md.disasm(b[a-0x80040000+0x800:a-0x80040000+0x800+0x4000],a):
        out.append(x)
        if x.mnemonic=='jr' and x.op_str=='$ra': out.append(next(md.disasm(b[x.address+4-0x80040000+0x800:][:4],x.address+4)));break
    return out
res={}
for op in range(0x98):
    a=h[op]; ins=fn(a)
    incs=[];calls=[]
    regs={}
    for x in ins:
        o=x.op_str
        if x.mnemonic=='lw' and o.endswith('-0x4e48($v0)') or (x.mnemonic=='lw' and '-0x4e48(' in o):
            regs[o.split(',')[0]]=0
        elif x.mnemonic=='addiu':
            p=[s.strip() for s in o.split(',')]
            if p[1] in regs: regs[p[0]]=regs[p[1]]+int(p[2],0)
        elif x.mnemonic=='move':
            p=[s.strip() for s in o.split(',')]
            if p[1] in regs: regs[p[0]]=regs[p[1]]
        elif x.mnemonic=='sw' and '-0x4e48($at)' in o:
            r=o.split(',')[0]; incs.append(regs.get(r,'?'))
        elif x.mnemonic=='jal': calls.append(o)
    res[op]=(incs,calls,len(ins))
    print(hex(op),hex(a),len(ins),incs,calls[:6])
