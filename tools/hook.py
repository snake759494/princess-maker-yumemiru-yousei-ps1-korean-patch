# PM3.EXE 한글 폰트 훅: Krom2RawAdd(SJIS) 호출을 가로채 0x889F 이상 코드에 한글 글리프(16x15)를 돌려준다.
# 폰트 영역은 EXE 끝에 붙여 두고 시작 스텁이 0x80010000으로 복사한다.
import keystone, struct

KS = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
REGION = 0x80010000
REGION_END = 0x80040000
CODE_SIZE = 0x800
WW_SITES = (0x80054568, 0x80054ddc)   # lw $a1,0x30($fp) : 줄바꿈 판정 폭
FONT = REGION + CODE_SIZE
# 변수 치환(ESC %name)은 복귀 위치(0x80176db0)·변수 번호(0x80157304)·값 버퍼(0x80101534)를 전역 하나로 쓴다.
# 상태 화면처럼 두 창이 동시에 찍히면 한 창의 치환 중에 다른 창이 치환을 시작해 복귀 위치가 상대 창 문장으로 바뀐다.
# 번역으로 글자 수가 달라져 이 겹침이 생기므로, 창(텍스트 객체)마다 복귀 위치와 값 버퍼를 따로 둔다.
VAR_CODE = REGION + 0x200
SLOTS = REGION + 0x600          # 8칸 x (객체 4 + 복귀 위치 4 + 버퍼 48)
SLOT_RR = SLOTS - 4
N_SLOTS, SLOT_SIZE = 8, 0x38
VAR_START = 0x80056710           # lw v0,0x34(fp) / lui v1,0x8010 : obj->ptr = 값 버퍼
VAR_END = 0x80057c30             # sw zero,0x10(fp) / j 0x80057c58 : 각 변수 처리 뒤
VAR_RESTORE = 0x800546cc         # lui v0,0x8015 : 치환 끝 복귀 위치 계산
VAR_PEEK = 0x80054d1c            # lui v0,0x8015 : 줄바꿈 판정용 복귀 위치 계산
KROM_CALL_SITE = 0x80058b4c      # jal 0x80084a08 (Krom2RawAdd 래퍼)
KROM_WRAPPER = 0x80084a08


def asm(src, addr):
    enc, _ = KS.asm('.set noreorder\n' + src, addr)
    return bytes(enc)


def hook_src(n_big):
    # a0 = SJIS 코드 -> v0 = 글리프 포인터. 한글 영역이 아니면 원래 함수로.
    return f"""
    andi $t0,$a0,0xffff
    srl $t1,$t0,8
    andi $t4,$t0,0xff
    sltiu $t5,$t4,0x80
    xori $t5,$t5,1
    subu $t4,$t4,$t5
    addiu $t4,$t4,-0x40
    addiu $t2,$t1,-0xf0
    sltiu $t3,$t2,13
    beq $t3,$zero,orig
    addiu $t6,$zero,188
    multu $t2,$t6
    mflo $t6
    addu $t6,$t6,$t4
    sltiu $t7,$t6,{n_big}
    beq $t7,$zero,orig
    sll $t7,$t6,5
    sll $t8,$t6,1
    subu $t7,$t7,$t8
    lui $v0,{FONT >> 16:#x}
    ori $v0,$v0,{FONT & 0xffff:#x}
    jr $ra
    addu $v0,$v0,$t7
orig:
    j {KROM_WRAPPER:#x}
    nop
"""


WW_SRC = """
    lw $a1,0x30($fp)
    lw $t0,0x48($fp)
    nop
    lw $t1,0x20($t0)
    nop
    lbu $t2,0($t1)
    addiu $t3,$zero,0x20
    beq $t2,$t3,zero
    addiu $t5,$zero,0x1b
    beq $t2,$t5,zero
    nop
    beq $t2,$zero,zero
    addiu $t5,$zero,0x2e
    beq $t2,$t5,zero
    addiu $t5,$zero,0x2c
    beq $t2,$t5,zero
    addiu $t5,$zero,0x21
    beq $t2,$t5,zero
    addiu $t5,$zero,0x3f
    beq $t2,$t5,zero
    nop
    b notsp
    nop
zero:
    jr $ra
    move $a1,$zero
notsp:
    lbu $t2,-1($t1)
    nop
    bne $t2,$t3,done
    nop
    move $t4,$zero
loop:
    lbu $t2,0($t1)
    nop
    beq $t2,$zero,end
    nop
    beq $t2,$t3,end
    addiu $t5,$zero,0x0a
    beq $t2,$t5,end
    addiu $t5,$zero,0x1b
    beq $t2,$t5,end
    sltiu $t5,$t2,0x81
    bne $t5,$zero,one
    sltiu $t5,$t2,0xa0
    bne $t5,$zero,two
    sltiu $t5,$t2,0xe0
    bne $t5,$zero,one
    sltiu $t5,$t2,0xfd
    beq $t5,$zero,one
    nop
two:
    addiu $t4,$t4,16
    b loop
    addiu $t1,$t1,2
one:
    addiu $t5,$zero,0x2e
    beq $t2,$t5,punc
    addiu $t5,$zero,0x2c
    beq $t2,$t5,punc
    addiu $t5,$zero,0x21
    beq $t2,$t5,punc
    addiu $t5,$zero,0x3f
    beq $t2,$t5,punc
    nop
    addiu $t4,$t4,8
punc:
    b loop
    addiu $t1,$t1,1
end:
    addiu $t4,$t4,24
    lhu $t6,8($t0)
    nop
    slt $t7,$t4,$t6
    beq $t7,$zero,done
    slt $t7,$a1,$t4
    beq $t7,$zero,done
    nop
    move $a1,$t4
done:
    jr $ra
    nop
"""


def _hi(a):
    return (a + 0x8000) >> 16 & 0xffff


def _lo(a):
    return a - ((a + 0x8000) >> 16 << 16)


VAR_FIND, VAR_S, VAR_E, VAR_R, VAR_P = (VAR_CODE + i * 0xc0 for i in range(5))

# 원래의 전역 복귀 위치 계산(슬롯이 없을 때)
ORIG_RESTORE = """
    lui $v0,0x8015
    lw $v0,0x7304($v0)
    lui $t0,0x800a
    sll $v0,$v0,3
    addu $t0,$t0,$v0
    lw $a0,-0x3ed4($t0)
    jal 0x800768cc
    nop
    addiu $v1,$v0,2
    lui $a0,0x8017
    lw $a0,0x6db0($a0)
    nop
    addu $v1,$a0,$v1
"""

VAR_SRCS = {
    # a0 = 객체, a1 = 1이면 없을 때 새로 잡음 -> v0 = 슬롯(없으면 0)
    VAR_FIND: f"""
    lui $t0,{_hi(SLOTS):#x}
    addiu $t0,$t0,{_lo(SLOTS)}
    addiu $t1,$zero,{N_SLOTS}
    move $t2,$zero
floop:
    lw $t3,0($t0)
    nop
    beq $t3,$a0,found
    nop
    bne $t3,$zero,fnext
    nop
    bne $t2,$zero,fnext
    nop
    move $t2,$t0
fnext:
    addiu $t1,$t1,-1
    bne $t1,$zero,floop
    addiu $t0,$t0,{SLOT_SIZE}
    beq $a1,$zero,none
    nop
    bne $t2,$zero,take
    nop
    lui $t4,{_hi(SLOT_RR):#x}
    lw $t5,{_lo(SLOT_RR)}($t4)
    nop
    addiu $t5,$t5,1
    andi $t5,$t5,{N_SLOTS - 1}
    sw $t5,{_lo(SLOT_RR)}($t4)
    sll $t6,$t5,6
    sll $t5,$t5,3
    subu $t6,$t6,$t5
    lui $t2,{_hi(SLOTS):#x}
    addiu $t2,$t2,{_lo(SLOTS)}
    addu $t2,$t2,$t6
take:
    sw $a0,0($t2)
    jr $ra
    move $v0,$t2
found:
    jr $ra
    move $v0,$t0
none:
    jr $ra
    move $v0,$zero
""",
    # 치환 시작: 복귀 위치 = obj->ptr + strlen(이름) + 2 를 객체 슬롯에 저장
    VAR_S: f"""
    lw $a0,0x34($fp)
    jal {VAR_FIND:#x}
    addiu $a1,$zero,1
    lw $t0,0x34($fp)
    lw $t2,0x14($fp)
    lw $t1,0x20($t0)
    sll $t2,$t2,3
    lui $t3,0x800a
    addu $t3,$t3,$t2
    lw $t3,-0x3ed4($t3)
    move $t4,$zero
sl:
    addu $t5,$t3,$t4
    lbu $t6,0($t5)
    nop
    bne $t6,$zero,sl
    addiu $t4,$t4,1
    addu $t1,$t1,$t4
    addiu $t1,$t1,1
    sw $t1,4($v0)
    lui $v1,0x8010
    addiu $v1,$v1,0x1534
    sw $v1,0x20($t0)
    j 0x80056720
    nop
""",
    # 변수 처리 뒤: 값 버퍼를 객체 슬롯으로 복사해 그 사본을 그리게 함
    VAR_E: f"""
    lw $a0,0x34($fp)
    jal {VAR_FIND:#x}
    move $a1,$zero
    beq $v0,$zero,out
    nop
    lw $t0,0x34($fp)
    lui $t2,0x8010
    lw $t1,0x20($t0)
    addiu $t2,$t2,0x1534
    bne $t1,$t2,out
    addiu $t3,$v0,8
    addiu $t4,$zero,{SLOT_SIZE - 9}
cp:
    lbu $t5,0($t2)
    addiu $t2,$t2,1
    sb $t5,0($t3)
    beq $t5,$zero,cpd
    addiu $t3,$t3,1
    addiu $t4,$t4,-1
    bne $t4,$zero,cp
    nop
    sb $zero,0($t3)
cpd:
    addiu $t3,$v0,8
    sw $t3,0x20($t0)
out:
    sw $zero,0x10($fp)
    j 0x80057c58
    nop
""",
    # 치환 끝: 객체 슬롯의 복귀 위치로 돌아가고 슬롯을 비움
    VAR_R: f"""
    lw $a0,0x48($fp)
    jal {VAR_FIND:#x}
    move $a1,$zero
    beq $v0,$zero,orig
    nop
    lw $v1,4($v0)
    b store
    sw $zero,0($v0)
orig:
{ORIG_RESTORE}
store:
    lw $v0,0x48($fp)
    nop
    sw $v1,0x20($v0)
    j 0x80054718
    nop
""",
    # 줄바꿈 판정의 앞보기: 같은 복귀 위치를 씀(슬롯은 비우지 않음)
    VAR_P: f"""
    lw $a0,0x48($fp)
    jal {VAR_FIND:#x}
    move $a1,$zero
    beq $v0,$zero,orig
    nop
    lw $v1,4($v0)
    b store
    nop
orig:
{ORIG_RESTORE}
store:
    sw $v1,0x38($fp)
    j 0x80054d60
    nop
""",
}

# 원래 명령 확인용(패치 위치, 기대 바이트)
VAR_SITES = {
    VAR_START: ('3400c28f', VAR_S),
    VAR_END: ('1000c0af', VAR_E),
    VAR_RESTORE: ('1580023c', VAR_R),
    VAR_PEEK: ('1580023c', VAR_P),
}


def build_region(big):
    code = asm(hook_src(len(big)), REGION)
    code = code.ljust(0x80, b'\0') + asm(WW_SRC, REGION + 0x80)
    assert len(code) <= VAR_CODE - REGION
    code = code.ljust(VAR_CODE - REGION, b'\0')
    for a in sorted(VAR_SRCS):
        part = asm(VAR_SRCS[a], a)
        assert len(part) <= 0xc0, (hex(a), len(part))
        code = code.ljust(a - REGION, b'\0') + part
    assert len(code) <= SLOT_RR - REGION
    assert SLOTS + N_SLOTS * SLOT_SIZE <= REGION + CODE_SIZE
    data = code.ljust(CODE_SIZE, b'\0') + b''.join(big)
    assert REGION + len(data) <= REGION_END, hex(REGION + len(data))
    return data.ljust((len(data) + 3) & ~3, b'\0')


def jal(t):
    return struct.pack('<I', 0x0C000000 | ((t >> 2) & 0x3ffffff))


def code_for_index(i):
    """한글 순번 i -> SJIS 코드 (사용자 정의 영역 0xF040부터, 트레일 0x7F 제외)"""
    lead = 0xF0 + i // 188; t = i % 188
    return (lead << 8) | (0x40 + t + (1 if t >= 0x3F else 0))


def attach(exe, region):
    """EXE 끝에 [복사 스텁 + 영역]을 붙이고 엔트리를 스텁으로 변경"""
    e = bytearray(exe)
    pc0, = struct.unpack_from('<I', e, 0x10)
    taddr, tsize = struct.unpack_from('<II', e, 0x18)
    body = e[0x800:0x800 + tsize]
    stub_addr = taddr + tsize
    src = stub_addr + 0x40
    n = len(region)
    stub = asm(f"""
    lui $t0,{src >> 16:#x}
    ori $t0,$t0,{src & 0xffff:#x}
    lui $t1,{REGION >> 16:#x}
    ori $t1,$t1,{REGION & 0xffff:#x}
    lui $t2,{(n // 4) >> 16:#x}
    ori $t2,$t2,{(n // 4) & 0xffff:#x}
loop:
    lw $t3,0($t0)
    addiu $t0,$t0,4
    sw $t3,0($t1)
    addiu $t2,$t2,-1
    bne $t2,$zero,loop
    addiu $t1,$t1,4
    j {pc0:#x}
    nop
""", stub_addr)
    assert len(stub) <= 0x40
    add = stub.ljust(0x40, b'\0') + region
    add = add.ljust((len(add) + 0x7ff) // 0x800 * 0x800, b'\0')
    out = e[:0x800] + body + add
    struct.pack_into('<I', out, 0x10, stub_addr)
    struct.pack_into('<I', out, 0x1c, tsize + len(add))
    return bytes(out)


def patch_exe(exe, big):
    e = bytearray(exe)
    off = KROM_CALL_SITE - 0x80040000 + 0x800
    assert e[off:off + 4] == jal(KROM_WRAPPER)
    e[off:off + 4] = jal(REGION)
    for a in WW_SITES:
        o = a - 0x80040000 + 0x800
        assert e[o:o + 4] == bytes.fromhex('3000c58f'), e[o:o+4].hex()
        e[o:o + 4] = jal(REGION + 0x80)
    for a, (want, dst) in VAR_SITES.items():
        o = a - 0x80040000 + 0x800
        assert e[o:o + 4] == bytes.fromhex(want), (hex(a), e[o:o + 4].hex())
        e[o:o + 8] = struct.pack('<I', 0x08000000 | ((dst >> 2) & 0x3ffffff)) + b'\0' * 4
    return attach(bytes(e), build_region(big))
