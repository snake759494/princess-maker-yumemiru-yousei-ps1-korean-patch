# 이름 입력 문자표(PM3.EXE)의 히라가나·가타카나 칸을 이름용 한글 음절로 교체
import struct
B = 0x80040000 - 0x800
HIRA = 0x800a0e94
KATA = 0x800a12b4
SYL = sorted(set("""가 강 건 경 고 관 광 구 국 규 근 기 길 나 남 내 니 노 다 단 달 대 도 동 두 드 라 란 래 레 려 련 령
로 루 류 르 리 린 림 마 만 메 명 모 목 무 문 미 민 바 박 배 백 베 별 보 봄 부 비 빈 빛 사 산 상 새 서 석 선 설 성 세 소 솔 송
수 순 슬 스 승 시 신 실 아 안 애 야 양 에 여 연 영 예 오 옥 온 완 요 용 우 운 원 위 유 윤 율 은 을 음 의 이 인 일 임 자 장
재 전 정 제 조 종 주 준 지 진 차 찬 창 채 천 철 초 치 카 케 크 키 타 태 테 토 트 티 파 페 피 하 한 해 향 현 형 혜 호 홍 화
환 효 후 희""".split()))
LABELS = {'英': '영', 'ｶﾀｶﾅ': '다음', 'ﾋﾗｶﾞﾅ': '이전'}


def entries(d, start):
    a = start
    while True:
        c, pos, p1, p2 = struct.unpack_from('<HHII', d, a - B)
        if not (0x800a0000 <= p1 < 0x800b0000):
            return
        o = p1 - B
        o2 = p2 - B
        yield c, p1, d[o:d.index(b'\0', o)], p2, d[o2:d.index(b'\0', o2)]
        a += 12


def chars():
    return SYL + ['영', '다음', '이전']


def patch(exe, enc):
    d = bytearray(exe)
    it = iter(SYL)
    for start in (HIRA, KATA):
        for c, p1, s, p2, s2 in list(entries(bytes(d), start)):
            t = s.decode('cp932')
            o = p1 - B
            if c >= 0x80 and t not in ('～', '・', 'ー'):
                k = next(it)
            elif t in LABELS:
                k = LABELS[t]
            else:
                continue
            e = enc(k)
            assert len(e) <= len(s) or len(e) <= 2, (t, k)
            d[o:o + len(s)] = e + b'\0' * (len(s) - len(e))
            if len(e) > len(s):
                d[o:o + len(e) + 1] = e + b'\0'
            if c >= 0x80 and s2.startswith(b'\x1b:'):
                # 작은 글씨용 문자열(ESC: 반각 ESC:)에도 한글 코드를 넣는다
                e2 = b'\x1b:' + e + b'\x1b:'
                assert len(e2) <= len(s2) + 1, (t, s2)
                o2 = p2 - B
                d[o2:o2 + len(e2) + 1] = e2 + b'\0'
    rest = list(it)
    assert not rest, f'남은 음절 {len(rest)}'
    return bytes(d)
