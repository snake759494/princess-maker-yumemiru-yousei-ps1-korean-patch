# 빌드 준비: 원본 디스크에서 파일 추출 -> 원문 목록 생성 -> 원본 그림 추출 -> 한글 그림 생성
#   python tools/prepare.py "../Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin"
import os, sys, subprocess
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(W)
def run(*a):
    print('>', ' '.join(a), flush=True)
    subprocess.run([sys.executable, *a], check=True)
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(W), 'Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin')
if not os.path.exists('orig/PM.EVX'):
    run('tools/extract.py', src, 'orig')
run('tools/mkchunks.py')                                  # text/src/evx_NN.json (원문, 배포 안 함)
run('tools/gfx.py', 'export', 'orig/PM.DT0', 'gfx/out')   # 원본 그림 (배포 안 함)
for s in 'abcd':                                          # 순서 중요: b 결과 위에 d 가 덧그림
    run('tools/gfx_%s.py' % s)
print('준비 완료. 이제 python build.py')
