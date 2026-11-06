# PM3.EXE 한글 폰트 훅: Krom2RawAdd(SJIS) 호출을 가로채 0x889F 이상 코드에 한글 글리프(16x15)를 돌려준다.
# 폰트 영역은 EXE 끝에 붙여 두고 시작 스텁이 0x80010000으로 복사한다.
import keystone, struct

KS = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
REGION = 0x80010000
REGION_END = 0x80040000
CODE_SIZE = 0x200
WW_SITES = (0x80054568, 0x80054ddc)   # lw $a1,0x30($fp) : 줄바꿈 판정 폭
FONT = REGION + CODE_SIZE
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


def build_region(big):
    code = asm(hook_src(len(big)), REGION)
    code = code.ljust(0x80, b'\0') + asm(WW_SRC, REGION + 0x80)
    assert len(code) <= CODE_SIZE
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
    return attach(bytes(e), build_region(big))
