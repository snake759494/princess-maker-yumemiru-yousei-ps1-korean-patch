# 재빌드

## 준비물

빌드 스크립트는 저장소 폴더를 작업 폴더로 쓰고, **그 상위 폴더**에서 원본 디스크와 큰 글꼴을 찾습니다.

```
<상위 폴더>/
  Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin   ← README의 해시와 일치해야 함
  NanumSquareNeo-cBd.ttf  NanumSquareNeo-dEb.ttf  NanumSquareNeo-eHv.ttf
  SeoulHangangM.ttf  SeoulHangangB.ttf  SeoulHangangEB.ttf
  <이 저장소>/
    fonts/Galmuri7.ttf  fonts/Galmuri9.ttf  fonts/Galmuri14.ttf
```

- Python 3.13, `numpy`, `Pillow`, `keystone-engine`
- 글꼴 출처는 `docs/FONT_CREDITS.md`
- xdelta3 (배포 파일을 만들 때만)

## 빌드

저장소 폴더에서 실행합니다.

```powershell
python tools/prepare.py "../Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin"
python build.py
```

`prepare.py`는 다음을 차례로 합니다(결과물은 모두 배포하지 않는 원본 유래 파일).

1. `tools/extract.py`: 디스크 파일 → `orig/`
2. `tools/mkchunks.py`: `PM.EVX` 원문 목록 → `text/src/evx_NN.json` (번역 파일의 번호와 짝)
3. `tools/gfx.py export`: `PM.DT0` 그림 → `gfx/out/`
4. `tools/gfx_a.py`~`gfx_d.py`: 한글 그림 → `gfx/ko/` (이 순서대로)

결과는 상위 폴더의 `Princess Maker - Yumemiru Yousei (Japan) (Track 1) [KR].bin`입니다. 원본이 다른 곳에 있으면 `PM_SRC` 환경 변수로 지정하고, 출력 경로는 `python build.py <출력.bin>`으로 바꿀 수 있습니다. 결과 BIN의 SHA-256이 `release_manifest.json`의 `output_bin_sha256`과 같아야 합니다.

## 배포 파일

```powershell
xdelta3 -e -0 -S none -A -s "Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin" "Princess Maker - Yumemiru Yousei (Japan) (Track 1) [KR].bin" PrincessMaker_YumemiruYousei_PS1_KO_v1.0.xdelta
```

## 번역 수정

`docs/TRANSLATION_GUIDE.md`를 참고하세요. 빌드가 자리가 모자란 문자열을 `공간부족 원문유지`, 실행파일 칸을 넘는 문자열을 `EXE 초과`로 알려 줍니다.
