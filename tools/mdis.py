import sys,capstone
def load(f):
    b=open(f,'rb').read(); base=int.from_bytes(b[0x18:0x1c],'little'); return b,base
def dis(f,addr,n=40):
    b,base=load(f); md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
    off=addr-base+0x800
    for i in md.disasm(b[off:off+n*4],addr): print(f'{i.address:08x} {i.mnemonic} {i.op_str}')
if __name__=='__main__':
    dis(sys.argv[1],int(sys.argv[2],16),int(sys.argv[3]) if len(sys.argv)>3 else 40)
