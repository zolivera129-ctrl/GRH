"""Versão em grade: personagens de 16x32 px (um tile de largura, dois de
altura), vistos de frente, para cenários em tiles de 16x16.

Cada sprite é um desenho em texto, uma letra por pixel. O contorno escuro
de fora é posto automaticamente em volta da silhueta.
"""
from PIL import Image
from px import rgb, mix

W16, H16 = 16, 32


def render(rows, pal, outline, tex=None, overlay=None):
    assert len(rows) == H16, f'{len(rows)} linhas'
    for i, r in enumerate(rows):
        assert len(r) == W16, f'linha {i} com {len(r)}: {r!r}'
    grid = [list(r) for r in rows]
    if overlay:
        for (x, y), ch in overlay.items():
            grid[y][x] = ch
    im = Image.new('RGBA', (W16, H16), (0, 0, 0, 0))
    filled = set()
    for y in range(H16):
        for x in range(W16):
            ch = grid[y][x]
            if ch == '.':
                continue
            c = pal[ch]
            if tex and ch in tex:
                c = tex[ch](x, y) or c
            im.putpixel((x, y), c + (255,))
            filled.add((x, y))
    for y in range(H16):
        for x in range(W16):
            if (x, y) in filled:
                continue
            if any((x + dx, y + dy) in filled for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                im.putpixel((x, y), outline + (255,))
    return im


def curl_tex(base, dark, light):
    def f(x, y):
        k = (x + 2 * y) % 5
        if k == 0:
            return light
        if (x * 3 + y) % 4 == 0:
            return dark
        return base
    return f


def strand_tex(base, dark, light):
    def f(x, y):
        if (x * 2 + y) % 6 == 0:
            return light
        if (x + y * 3) % 7 == 0:
            return dark
        return base
    return f


# ------------------------------------------------------------- Guilherme
GUILHERME = [
    "................",
    "...hh.hhhh.hh...",
    "..hhhhhhhhhhhh..",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    ".hhhhhhhhhhhhhh.",
    "..HshhsshhshsH..",
    "..HsHHssssHHsH..",
    "..HsggssssggsH..",
    "..sgseggggesgs..",
    "..ssggssssggss..",
    "...ssssSSssss...",
    "...ssmttttmss...",
    "....ssHHHHss....",
    "...cccSSSSccc...",
    ".cCcccCCCCcccCc.",
    ".cCcc333cccccCc.",
    ".cCc11111111cCc.",
    ".cCcc211112ccCc.",
    ".ssccc1cc1cccss.",
    ".44ccccccccccss.",
    ".ssCCCCCCCCCCss.",
    ".SSppppppppppSS.",
    ".SSppppPPppppSS.",
    "...ppppPPpppp...",
    "...ppppPPpppp...",
    "...pppP..Pppp...",
    "..fffff..fffff..",
    "..FFFFF..FFFFF..",
    "................",
]


def guilherme16():
    pal = dict(
        h=rgb('#33231A'), H=rgb('#1B120D'), s=rgb('#C98D5F'), S=rgb('#AD7249'),
        g=rgb('#202024'), w=rgb('#FFFFFF'), e=rgb('#1A1210'), m=rgb('#6B2E22'),
        t=rgb('#FFFFFF'), c=rgb('#F7F7F3'), C=rgb('#D3D5DC'),
        **{'1': rgb('#3EA8E6'), '2': rgb('#1C5FA8'), '3': rgb('#F59CC6'),
           '4': rgb('#5AC9F0')},
        p=rgb('#96BCE0'), P=rgb('#6F96C2'), f=rgb('#27272E'), F=rgb('#EDEDEB'),
        b=rgb('#1E1E23'), B=rgb('#4A4A55'),
    )
    ov = {}
    # alça transversal e a bolsa preta no quadril
    for x, y in ((11, 17), (10, 18), (9, 19), (8, 20), (7, 21), (6, 22)):
        ov[(x, y)] = 'b'
    for y in range(22, 25):
        for x in range(2, 6):
            ov[(x, y)] = 'b'
    ov[(3, 22)] = 'B'
    ov[(4, 22)] = 'B'
    return render(GUILHERME, pal, rgb('#1A1418'),
                  tex={'h': curl_tex(pal['h'], pal['H'], rgb('#62432F'))}, overlay=ov)


# --------------------------------------------------------------- Gabriel
GABRIEL = [
    "................",
    "................",
    ".....kkkkkk.....",
    "...kkkkkkkkkk...",
    "..kkkkkKkkkkkk..",
    "..kkkkwwwwkkkk..",
    "..kkkkkkkkkkkk..",
    ".KKKKKKKKKKKKKK.",
    "..HSSSSSSSSSSH..",
    "..HsHHssssHHsH..",
    "..HggggggggggH..",
    "..sGseGssGesGs..",
    "..rHGGssssGGHr..",
    "...HHsHHHHsHH...",
    "...HHHmttmHHH...",
    "....HHHHHHHH....",
    "...ccHHHHHHcc...",
    ".cCcccCCCCcccCc.",
    ".cCcccc11ccccCc.",
    ".cCc3c1111c3cCc.",
    ".cCcc444444ccCc.",
    ".ssc22222222css.",
    ".55ccccccccccbb.",
    ".ssCCCCCCCCCCss.",
    ".SSppppppppppSS.",
    ".SSppppPPppppSS.",
    "...ppppPPpppp...",
    "...pppP..Pppp...",
    "...PPPP..PPPP...",
    "..fFFff..ffFFf..",
    "..FFFFF..FFFFF..",
    "................",
]


def gabriel16():
    pal = dict(
        k=rgb('#202024'), K=rgb('#3A3A44'), w=rgb('#EDEDED'), H=rgb('#3E2819'),
        s=rgb('#F1C9A8'), S=rgb('#D9A684'), g=rgb('#141416'), G=rgb('#7C7C86'),
        e=rgb('#2A1A12'), m=rgb('#6E3A2C'), t=rgb('#FFFFFF'), r=rgb('#8A2A30'),
        c=rgb('#4B4346'), C=rgb('#383134'),
        **{'1': rgb('#7563D6'), '2': rgb('#7FA9F0'), '3': rgb('#F4C04F'),
           '4': rgb('#E7E3EE'), '5': rgb('#F4F4F4')},
        b=rgb('#151517'), p=rgb('#76653C'), P=rgb('#5A4C2C'),
        f=rgb('#1D1D20'), F=rgb('#F2F2F0'),
    )
    tex = {'H': strand_tex(pal['H'], rgb('#26170E'), rgb('#5C3D2A'))}
    ov = {(5, 5): 'w', (4, 4): 'k'}
    return render(GABRIEL, pal, rgb('#141016'), tex=tex, overlay=ov)


# -------------------------------------------------------------- Saldanha
SALDANHA = [
    "................",
    "................",
    "................",
    "....hhhhhhhh....",
    "...hhhhhhhhhh...",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..hssssssssssh..",
    "..hsHHssssHHsh..",
    "..hggggssggggh..",
    "..sgseggggesgs..",
    "..sGGGGssGGGGs..",
    "...ssssSSssss...",
    "...ssBBmmBBss...",
    "....sBBBBBBs....",
    "...cckBBBBkcc...",
    ".cCcckkSSkkccCc.",
    ".cCcccc2cccccCc.",
    ".sscaaaaaaaacss.",
    ".sssaAAAAAAasss.",
    ".sscaaaaaaaacbb.",
    "...cccccccccc...",
    "...CCCCCCCCCC...",
    "...rrrrRRrrrr...",
    "...ppppPPpppp...",
    "...ppppPPpppp...",
    "...ppppPPpppp...",
    "...pppP..Pppp...",
    "..fffff..fffff..",
    "..FFFFF..FFFFF..",
    "................",
]


def saldanha16():
    pal = dict(
        h=rgb('#8E8E93'), H=rgb('#55555C'), s=rgb('#D3A07B'), S=rgb('#B8835F'),
        g=rgb('#1C1C20'), G=rgb('#6A6A72'), w=rgb('#FFFFFF'), e=rgb('#2A1C14'), m=rgb('#6A3C2C'),
        B=rgb('#D2D0CC'), c=rgb('#1F2B47'), C=rgb('#152036'), k=rgb('#34446D'),
        **{'2': rgb('#4A5A86')},
        a=rgb('#C3C7CF'), A=rgb('#A3A8B2'), b=rgb('#141416'),
        r=rgb('#7B4A2A'), R=rgb('#D4D6DA'),
        p=rgb('#B5B8BD'), P=rgb('#93969C'), f=rgb('#F4F4F2'), F=rgb('#C9CACE'),
    )
    tex = {'h': strand_tex(pal['h'], pal['H'], rgb('#C9C9CD'))}
    ov = {(4, 19): 'A', (11, 19): 'A'}
    return render(SALDANHA, pal, rgb('#1A1620'), tex=tex, overlay=ov)


# ------------------------------------------------------------------ Caio
CAIO = [
    "................",
    "................",
    "....hh.hh.hh....",
    "...hhhhhhhhhh...",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..hhhhhhhhhhhh..",
    "..hHhshhhshhHh..",
    "..HsHHssssHHsH..",
    "..HssssssssssH..",
    "..HssessssessH..",
    "..ssesessesess..",
    "..sssssSSsssss..",
    "...smttttttms...",
    "...sSsuuuusSs...",
    "....SSssssSS....",
    "...ccwSSSSwcc...",
    ".cCcknwwwwnkcCc.",
    ".cCcCwnwwnwCcCc.",
    ".cCcbbbbbbbbcCc.",
    ".cCcbqqqqqvbcCc.",
    ".sscbqqqqvqbcss.",
    ".sssbqvqvqqbsss.",
    "..ssbqqvqqqbss..",
    "...CbbbbbbbbC...",
    "...ppppPPpppp...",
    "...ppppPPpppp...",
    "...ppppPPpppp...",
    "...pppP..Pppp...",
    "..fffff..fffff..",
    "..FFFFF..FFFFF..",
    "................",
]


def caio16():
    pal = dict(
        h=rgb('#2B1D16'), H=rgb('#160F0B'), s=rgb('#D9A47E'), S=rgb('#BE8763'),
        w=rgb('#FFFFFF'), e=rgb('#1C120C'), m=rgb('#5E2A1E'), t=rgb('#FFFFFF'),
        u=rgb('#B4584A'), c=rgb('#6D7C56'), C=rgb('#4E5A3B'), k=rgb('#8A9B70'),
        n=rgb('#1D2A4C'), b=rgb('#1C1C21'), q=rgb('#F5F7F8'), v=rgb('#2FAE45'),
        p=rgb('#27324F'), P=rgb('#18203A'), f=rgb('#F4F4F2'), F=rgb('#C9CACE'),
    )
    tex = {'h': curl_tex(pal['h'], pal['H'], rgb('#55392A'))}
    return render(CAIO, pal, rgb('#161218'), tex=tex)


# ----------------------------------------------------------------- Flora
FLORA = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "....kkkkkkkk....",
    "...kkjjkkkkkk...",
    "..KkkkkkkkkkkK..",
    ".KKkwekkkkewkKK.",
    ".KKkkkkkkkkkkKK.",
    ".KKkkkmmmmkkkKK.",
    ".KKkkmmNNmmkkKK.",
    "..KkkmmmmmmkkK..",
    "..K.kkmmmmkk.K..",
    "....rrryrrrr....",
    "...kkkkkkkkkk...",
    "..kkkkkkkkkkkk..",
    ".kjkKkkkkkkKkkk.",
    ".kjkKkkKKkkKkkk.",
    ".kkkKkkKKkkKkkk.",
    ".kkkKkkKKkkKkkk.",
    ".kkkKkkKKkkKkkk.",
    ".kkkKkkKKkkKkkk.",
    ".KkkkkkKKkkkkkK.",
    "................",
]


def flora16():
    pal = dict(
        k=rgb('#2A2A31'), K=rgb('#15151A'), j=rgb('#4E5060'), m=rgb('#3A3A45'),
        N=rgb('#0A0A0B'), e=rgb('#6A3618'), w=rgb('#FFFFFF'),
        r=rgb('#D7352E'), y=rgb('#F4C04F'),
    )
    return render(FLORA, pal, rgb('#08080A'))


# ----------------------------------------------------------------- Lupin
LUPIN = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "...KK......KK...",
    "..KkKkkkkkkKkK..",
    "..KkkkkkkkkkkK..",
    "...kTkkkkkkTk...",
    "...kkewkkwekk...",
    "...kkkkNNkkkk...",
    "...kktTkkTtkk...",
    "....tTtTTtTt....",
    ".....TtTtTt.....",
    "....kktTtTkk....",
    "...kkkKkkKkkk...",
    "..kkkkKkkKkkkk..",
    "..kkkkKkkKkkkk..",
    "..KkkkKKKKkkkK..",
    "................",
    "................",
]


def lupin16():
    pal = dict(
        k=rgb('#25242A'), K=rgb('#121115'), T=rgb('#94603A'), t=rgb('#5E3A20'),
        N=rgb('#0A0A0B'), e=rgb('#5E3216'), w=rgb('#FFFFFF'),
    )
    im = render(LUPIN, pal, rgb('#070708'))
    # pelo duro: pontinhas soltas no contorno
    for x, y in ((6, 16), (9, 16), (2, 26), (13, 26), (3, 23), (12, 23), (4, 25), (11, 25)):
        if im.getpixel((x, y))[3] == 0:
            im.putpixel((x, y), (7, 7, 8, 255))
    # sombrinha: os cachorros não usam a linha 31; desce o Lupin para o chão
    out = Image.new('RGBA', (W16, H16), (0, 0, 0, 0))
    out.alpha_composite(im, (0, 1))
    return out


ALL16 = [('guilherme', guilherme16), ('gabriel', gabriel16), ('flora', flora16),
         ('lupin', lupin16), ('saldanha', saldanha16), ('caio', caio16)]
