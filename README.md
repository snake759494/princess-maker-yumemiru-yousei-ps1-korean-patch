# 프린세스 메이커 ~꿈꾸는 요정~ PS1 한글패치

PS1 일본판 **プリンセスメーカー ゆめみる妖精 (SCPS-10032)**용 비공식 한국어 패치입니다. **이벤트 대사·나레이션·선택지·메뉴·상점·능력치 표·아이템 설명·세이브 안내 등 게임 안의 문장 전체**를 한국어로 바꿨습니다. **타이틀 메뉴·메인 메뉴 버튼·스케줄 항목표·달력(월·요일)·휴일·페이즈 배너·상태 화면·별자리·아이템 이름 같은 그림 글자**도 한글로 다시 그렸고, **이름 입력판**은 한글 음절표로 바꿨습니다. 현재 배포판은 **v1.3 (2026-11-08)**입니다.

[패치 다운로드](https://github.com/snake759494/princess-maker-yumemiru-yousei-ps1-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 한글패치 **PrincessMaker_YumemiruYousei_PS1_KO_v1.3.xdelta**뿐입니다. 저장소에는 제작 소스와 한국어 번역만 공개합니다. 원본·완성 디스크 이미지, 추출한 게임 파일·그림, 일본어 원문, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『프린세스 메이커 ~꿈꾸는 요정~』은 가이낙스 원작의 육성 시뮬레이션 『프린세스 메이커』 시리즈의 PS1 작품입니다(1997년, 소니 컴퓨터 엔터테인먼트). 아버지가 되어 요정 여왕에게서 맡은 딸을 10살부터 18살까지 키우며, 집사 요정 우즈의 도움을 받아 공부·아르바이트·수확제 등을 거쳐 딸의 장래를 만들어 갑니다.

이 패치는 **PS1 일본판 SCPS-10032의 BIN/CUE 이미지(2트랙: 데이터 MODE2/2352 + CD-DA 음악)**에만 적용됩니다. 패치하는 것은 **Track 1(데이터) BIN 하나**이고, Track 2(음악) BIN은 원본을 그대로 씁니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SCPS-10032 |
| 원본 형식 | 수정되지 않은 일본판 BIN/CUE (트랙 2개, BIN 2개) |
| 원본 Track 1 BIN 크기 | 435,703,296 바이트 |
| **원본 Track 1 BIN MD5** | `50a5a6ee60075e34ae02744db3de085b` |
| 원본 Track 1 BIN SHA-1 | `82ba324dbefe52c2c56917797e5c964915c7fd43` |
| 원본 Track 1 BIN SHA-256 | `29236fa820092e3b4bae64b2d7b0831331dd555ff08269e84bb359f59cc1f9a2` |
| 원본 Track 2 BIN (변경 없음) | 44,793,840 바이트, MD5 `09dd6a556287ede17ef474aa385c34fb` |
| xdelta 파일 크기 | 1,337,743 바이트 |
| xdelta SHA-256 | `2956e0091280381fe4d208bb4091921e33bc2f48e7cf82878ac20a3b7a6834d5` |
| 적용 결과 Track 1 BIN 크기 | 436,239,552 바이트 (원본보다 536,256 바이트 큼) |
| 적용 결과 Track 1 BIN SHA-1 | `f6486d8a1e62a1e5cd9550b59a1f89547d1d04f0` |
| 적용 결과 Track 1 BIN SHA-256 | `0f3f170f818ac64aef5158c11fc01648cff8e39c5225db69caa3e5b0c0bec1b1` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, PBP, ECM, 압축 이미지, 트랙을 하나로 합친 BIN에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `PrincessMaker_YumemiruYousei_PS1_KO_v1.3.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 **Track 1** `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Princess Maker - Yumemiru Yousei (Korean) (Track 1).bin`).
5. 원본 `.cue`를 복사해 이름을 바꾸고, 첫 번째 `FILE "..."` 줄만 결과 BIN 이름으로 고칩니다. 두 번째 줄(Track 2)은 원본 음악 BIN을 그대로 가리키게 둡니다.

```
FILE "Princess Maker - Yumemiru Yousei (Korean) (Track 1).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
FILE "Princess Maker - Yumemiru Yousei (Japan) (Track 2).bin" BINARY
  TRACK 02 AUDIO
    INDEX 00 00:00:00
    INDEX 01 00:02:00
```

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin' '.\PrincessMaker_YumemiruYousei_PS1_KO_v1.3.xdelta' '.\Princess Maker - Yumemiru Yousei (Korean) (Track 1).bin'
```

해시를 자동으로 검사하고 CUE까지 만들어 주는 도구도 있습니다. Python 3과 xdelta3가 필요하며, 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다. Track 2 BIN은 원본 Track 1과 같은 폴더에 있어야 합니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Princess Maker - Yumemiru Yousei (Japan) (Track 1).bin' --patch '.\PrincessMaker_YumemiruYousei_PS1_KO_v1.3.xdelta' --output '.\Princess Maker - Yumemiru Yousei (Korean) (Track 1).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(실행파일과 데이터가 다릅니다). 메모리 카드 세이브는 원본판과 같은 형식이지만, 원본판에서 만든 세이브의 이름(딸 이름 등)은 일본어로 남습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 이벤트 스크립트 | `PM.EVX`의 고유 문자열 8,144개 전체: 대사·나레이션·선택지·메뉴·상점·능력치 표·이벤트·엔딩 |
| 실행파일 문자열 | `PM3.EXE` 102개: 세이브 제목·안내, 아버지 신분, 아이템·과자 설명, 병원·잔고 안내 등 |
| 글꼴 | 16×15 칸에 한글 1,032자(갈무리11 원래 크기 12px), BIOS 한자 글꼴 호출을 가로채 공급 |
| 이름 입력 | 히라가나·가타카나 표를 이름용 한글 음절 161자로 교체, 전환 버튼 「영·다음·이전」 |
| 그림 글자 | `PM.DT0` 그림 21장: 타이틀 메뉴, 메인 메뉴 버튼, 스케줄 항목표, 달력(월·요일), 페이즈·일, 휴일 배너, 페이즈 시작·완료 배너, 별자리·혈액형·아버지 신분 표, 상태 화면, 선물·아이템·요리·그림 이름 |
| 영어 표기 | 메뉴·달력·배너의 영어(NEW GAME, JAN~DEC, SUN~SAT, HOLIDAY, PHASE START 등)도 한글로 |

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다(`docs/TRANSLATION_GUIDE.md`).
- 우즈는 주인님(아버지)께 공손한 존댓말, 딸은 아빠에게 반말로 옮겼습니다.
- 딸 이름 등 변수 뒤 조사는 `을(를)`, `은(는)`, `이(가)`, `와(과)`로 통일했습니다.
- 능력치 표는 게임이 정해진 자리에 숫자를 써 넣기 때문에 라벨 길이를 원문과 똑같이 맞췄습니다(예: 「피로도」).

### 번역하지 않은 것

- 타이틀 로고(PRINCESS MAKER / FAERY TALES COME TRUE)와 저작권 표기
- 오프닝 동영상 속 세로쓰기 시구
- 하트·땀 같은 아이콘 기호
- 음성(대사 음성은 일본어 그대로)

## 알려진 한계

- 모든 화면을 직접 확인하지는 못했습니다. 타이틀·환경 설정·인트로·딸 정보 입력·메인 메뉴·상태 화면·상점·옷 갈아입기·대화·세이브·학교·휴일 배너는 에뮬레이터로 확인했지만, 모든 이벤트·엔딩과 페이즈 시작·완료 배너, 바뀐 달력 칸은 게임 화면으로 끝까지 보지 못했습니다.
- 스태프 크레딧(타이틀의 「스태프」)은 에뮬레이터 화면을 찍을 수 없어 확인하지 못했습니다.
- 인게임 확인은 DuckStation으로 했습니다. 실기에서의 동작은 확인하지 못했습니다. 칸을 넘치거나 어긋난 문구가 있으면 이슈로 알려 주세요.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `build.py` | 전체 빌드(코드표·글꼴 훅, PM.EVX 재배치, 실행파일 문자열, 이름 입력표, 그림 삽입) |
| `tools/prepare.py` | 빌드 준비(디스크 추출, 원문 목록, 원본 그림 추출, 한글 그림 생성) |
| `tools/` | `evx.py` 스크립트 파서, `hook.py` 글꼴 훅, `kfont.py` 글리프, `namein.py` 이름 입력, `gfx.py`·`gfx_a~d.py` 그림 글자, `iso.py`·`disc.py`·`cdsec.py` 디스크, `apply_release.py` 해시 검사 후 적용, `tcheck.py`·`survey.py` 검사, `emu.py`·`srv.py`·`c.py` DuckStation 테스트 조작 |
| `text/ko/evx_NN.json` | `PM.EVX` 번역. `{"번호": "한국어"}` (번호는 빌드 준비 때 만드는 원문 목록과 짝) |
| `text/ko/exe.json` | 실행파일 문자열 번역. `{"주소": "한국어"}` |
| `text/exe_index.json` | 실행파일 문자열의 주소·오프셋·최대 길이 |
| `fonts/` | (저장소에 없음) 갈무리 글꼴을 두는 곳 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처, 번역 지침 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
