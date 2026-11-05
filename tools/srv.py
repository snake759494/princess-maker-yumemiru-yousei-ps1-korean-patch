# RetroArch 상주 제어 서버: python srv.py <cue> [state] / 클라이언트: python c.py "명령;명령"
import sys,os,socket,time,traceback,shutil
sys.path.insert(0,os.path.dirname(__file__))
from emu import Emu
e=Emu(os.path.abspath(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else None)
s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',2399));s.listen(1)
while True:
    c,_=s.accept();cmd=c.recv(65536).decode();out=''
    try:
        for part in cmd.split(';'):
            a=part.split()
            if not a: continue
            if a[0]=='p':
                for k in a[1:]:
                    if k[0]=='w': time.sleep(float(k[1:]))
                    else: e.key(k,0.12); time.sleep(0.35)
            elif a[0]=='k': e.key(a[1],float(a[2]) if len(a)>2 else 0.15)
            elif a[0]=='kd': e.kev(a[1],0)
            elif a[0]=='ku': e.kev(a[1],1)
            elif a[0]=='w': time.sleep(float(a[1]))
            elif a[0]=='shot': out+=str(e.shot(os.path.abspath(a[1])))+'\n'
            elif a[0]=='rd': out+=e.read(int(a[1],16),int(a[2],16)).hex()+'\n'
            elif a[0]=='wr': e.write(int(a[1],16),bytes.fromhex(a[2]))
            elif a[0]=='ff': e.key('tab',float(a[1]) if len(a)>1 else 1)
            elif a[0]=='save': out+=str(e.save(os.path.abspath(a[1])))+'\n'
            elif a[0]=='kp':
                # 확실한 입력: 패드 버퍼에 눌림이 보일 때까지 keydown 재전송
                for _ in range(8):
                    e.kev(a[1],0); time.sleep(0.12)
                    if e.read(0x800a93a6,2)!=b'\xff\xff': break
                time.sleep(0.08); e.kev(a[1],1); time.sleep(0.25)
            elif a[0]=='regs':
                e.halt(); out+=e.cmd('g')+chr(10); e.cont()
            elif a[0]=='bp':
                e.halt(); e.cmd('Z0,%s,4'%a[1]); e.cont()
            elif a[0]=='bw':
                e.sock.settimeout(float(a[1]))
                try:
                    r=e._recv(); e.sock.settimeout(None); out+='STOP '+str(r)+chr(10)+e.cmd('g')+chr(10)
                    if len(a)>2: out+=e.cmd('m%s,100'%a[2])+chr(10)
                except Exception as ex:
                    e.sock.settimeout(None); out+='timeout'+chr(10); e.halt()
                e.cmd('z0,%s,4'%a[3] if len(a)>3 else 'z0,80010000,4'); e.cont()
            elif a[0]=='rehwnd': e.hwnds=e._find(); out+=str(e.hwnds)+chr(10)
            elif a[0]=='quit': e.close(); c.sendall(b'bye'); c.close(); sys.exit()
    except Exception: out+=traceback.format_exc()
    c.sendall(out.encode() or b'ok');c.close()
