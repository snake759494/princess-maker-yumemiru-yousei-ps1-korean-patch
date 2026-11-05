import sys,struct,subprocess
o=subprocess.run(['python','tools/c.py','regs'],capture_output=True,text=True).stdout.split()[0]
r=struct.unpack('<38I',bytes.fromhex(o[:38*8]))
n='zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra sr lo hi bad cause pc'.split()
print(' '.join(f'{a}={v:08x}' for a,v in zip(n,r) if a in ('pc','ra','sp','v0','a0','a1','s0','fp')))
