"""Os personagens, desenhados pixel a pixel em vista 3/4 (olhando
para a direita, como os avatares do Habbo na direção 2)."""
import math

from px import Layer, Sprite, rgb, mul, mix


def curls(base, dark, light):
    """Textura de cachos: anéis pequenos com brilho em cima e sombra embaixo."""
    tile = ["LLBD",
            "LBDD",
            "BDDB",
            "BBBL"]

    def fn(x, y, c):
        off = 2 if (y // 4) % 2 else 0
        t = tile[y % 4][(x + off) % 4]
        return {'L': light, 'B': base, 'D': dark}[t]
    return fn


# ---------------------------------------------------------------- humanos
def _legs_shoes(S, P, top=46):
    # pernas
    fl = Layer(P['pant'], P['pantline'])
    fl.rect(19, top, 26, 58)
    fl.shade_side('r', 2, P['pants'])
    fl.outline()
    S.add(fl)
    nl = Layer(P['pant'], P['pantline'])
    nl.rect(12, top, 19, 59)
    nl.shade_side('r', 1, P['pants'])
    nl.outline()
    S.add(nl)
    if P.get('cuff'):
        for y in (56, 57):
            for x in range(13, 19):
                S.set(x, y, P['pants'])
            for x in range(20, 26):
                S.set(x, y - 1, mul(P['pants'], 0.92))

    # tênis (o de trás fica mais alto, o da frente mais baixo)
    for (x0, y0) in ((19, 57), (11, 58)):
        up = Layer(P['shoe'], P['shoeline'])
        up.rows({y0: (x0, x0 + 6), y0 + 1: (x0, x0 + 8), y0 + 2: (x0, x0 + 9)})
        up.outline()
        S.add(up)
        so = Layer(P['sole'], P['soleline'])
        so.rows({y0 + 3: (x0, x0 + 9), y0 + 4: (x0 + 1, x0 + 9)})
        so.outline(skip='t')
        S.add(so)
        if P.get('stripe'):
            # a faixa lateral do Vans Old Skool
            for x, y in ((x0 + 2, y0 + 2), (x0 + 3, y0 + 1), (x0 + 4, y0 + 1),
                         (x0 + 5, y0 + 2), (x0 + 6, y0 + 2), (x0 + 7, y0 + 2)):
                S.set(x, y, P['sole'])
        else:
            S.set(x0 + 6, y0 + 1, P['shoehl'])
            S.set(x0 + 7, y0 + 1, P['shoehl'])


def _arms_body_legs(S, P):
    """Corpo-base compartilhado pelos dois humanos (camiseta larga, braços
    caindo ao lado do corpo, calça e tênis). P traz a paleta."""
    # braço de trás (o da direita da tela), atrás do corpo
    fa = Layer(P['sk'], P['skline'])
    fa.rows({y: (27, 30) for y in range(37, 46)})
    fa.rows({46: (27, 30), 47: (27, 30), 48: (28, 30)})
    fa.shade_side('r', 1, P['sks'])
    fa.outline()
    S.add(fa)

    fsl = Layer(P['tee'], P['teeline'])
    fsl.rows({29: (25, 28), 30: (25, 29), 31: (25, 30)})
    fsl.rows({y: (25, 31) for y in range(32, 38)})
    fsl.rows({38: (26, 31)})
    fsl.shade_side('r', 2, P['tees'])
    fsl.outline()
    S.add(fsl)

    _legs_shoes(S, P)

    # tronco (camiseta larga)
    bd = Layer(P['tee'], P['teeline'])
    bd.rows({27: (14, 24), 28: (12, 26)})
    bd.rows({y: (11, 27) for y in range(29, 48)})
    bd.shade_side('r', 2, P['tees'])
    bd.outline()
    # dobra da barra
    for x in range(13, 26):
        bd.set(x, 46, P['tees'])
    S.add(bd)
    return S


def _near_arm(S, P, band=None):
    nsl = Layer(P['tee'], P['teeline'])
    nsl.rows({29: (9, 13), 30: (8, 14)})
    nsl.rows({y: (7, 14) for y in range(31, 39)})
    nsl.rows({39: (7, 13)})
    nsl.shade_side('l', 1, P['tees'])
    nsl.outline()
    # vinco da manga
    for y in range(32, 38):
        nsl.set(12, y, P['tees'])
    S.add(nsl)

    na = Layer(P['sk'], P['skline'])
    na.rows({y: (8, 11) for y in range(40, 47)})
    na.rows({47: (8, 11), 48: (8, 11), 49: (9, 11)})
    na.shade_side('l', 1, P['sks'])
    na.outline()
    if band:
        for x in range(8, 12):
            na.set(x, 45, band)
            na.set(x, 46, mul(band, 0.8))
    S.add(na)


def _neck_head(S, P, chin_y=25):
    nk = Layer(P['sk'], P['skline'])
    nk.rect(15, 22, 21, 28)
    nk.outline(skip='t')
    for x in range(16, 21):
        nk.set(x, 24, P['sks'])
        nk.set(x, 25, P['sks'])
    S.add(nk)
    # gola
    for x in range(15, 22):
        S.set(x, 29, P['teeline'])
    S.set(14, 28, P['teeline'])
    S.set(22, 28, P['teeline'])

    hd = Layer(P['sk'], P['skline'])
    hd.rows({9: (14, 24), 10: (12, 25), 11: (11, 26), 12: (10, 26)})
    hd.rows({y: (10, 27) for y in range(13, 17)})
    hd.rows({17: (10, 28), 18: (10, 28), 19: (10, 27), 20: (11, 27),
             21: (11, 27), 22: (12, 26), 23: (13, 26), 24: (15, 25), 25: (17, 24)})
    # luz no rosto (lado de frente) e sombra na nuca
    hd.shade_side('l', 2, P['sks'])
    hd.paint([(x, y) for y in range(12, 15) for x in range(21, 26)], P['skl'])
    hd.outline()
    S.add(hd)


def _ear(S, P):
    ear = Layer(P['sk'], P['skline'])
    ear.rows({15: (13, 14), 16: (12, 15), 17: (12, 15), 18: (12, 15), 19: (13, 14)})
    ear.outline()
    ear.set(13, 17, P['sks'])
    ear.set(14, 17, P['sks'])
    ear.set(14, 16, P['sks'])
    S.add(ear)


def guilherme():
    S = Sprite(40, 70)
    P = dict(
        sk=rgb('#C98D5F'), sks=rgb('#AD7249'), skl=rgb('#DCA67B'), skline=rgb('#7A4A2C'),
        tee=rgb('#F7F7F3'), tees=rgb('#DCDDE3'), teeline=rgb('#9A9CA9'),
        pant=rgb('#96BCE0'), pants=rgb('#769FCA'), pantline=rgb('#4E709A'),
        shoe=rgb('#27272E'), shoehl=rgb('#50505C'), shoeline=rgb('#111114'),
        sole=rgb('#F0F0EE'), soleline=rgb('#A3A3A8'),
    )
    hair, haird, hairl = rgb('#33231A'), rgb('#1B120D'), rgb('#62432F')
    blk, blkl = rgb('#1E1E23'), rgb('#44444E')
    blu, blud, pink = rgb('#3EA8E6'), rgb('#1C5FA8'), rgb('#F59CC6')

    _arms_body_legs(S, P)

    # estampa: o boneco azul voando com o raio rosa
    art = {
        30: [(15, 18, pink)],
        31: [(18, 20, pink), (21, 21, blu)],
        32: [(17, 18, blud), (19, 23, blu)],
        33: [(13, 15, blu), (16, 24, blu)],
        34: [(14, 15, blud), (16, 23, blu), (24, 25, blu)],
        35: [(17, 22, blu)],
        36: [(16, 18, blu), (21, 23, blu)],
        37: [(15, 16, blud), (22, 23, blud)],
    }
    for y, segs in art.items():
        for x0, x1, c in segs:
            for x in range(x0, x1 + 1):
                S.set(x, y, c)
    for x, y in ((19, 33), (21, 34), (20, 35), (19, 35)):
        S.set(x, y, blud)

    # alça transversal: do ombro de trás até o quadril da frente
    strap = Layer(blk, rgb('#0E0E10'))
    strap.line_(25, 28, 15, 40, w=2)
    S.add(strap)
    for i in range(0, 11, 3):
        S.set(25 - i, 28 + i, blkl)

    # bolsa preta transversal no quadril
    bag = Layer(blk, rgb('#0B0B0D'))
    bag.rows({40: (10, 16), 41: (9, 17)})
    bag.rows({y: (9, 17) for y in range(42, 47)})
    bag.rows({47: (10, 16)})
    bag.outline()
    for x in range(10, 17):
        bag.set(x, 42, blkl)
    bag.set(16, 43, rgb('#8A8A95'))
    bag.set(11, 41, blkl)
    S.add(bag)

    _near_arm(S, P, band=rgb('#5AC9F0'))

    _neck_head(S, P)

    # rosto
    eye = rgb('#1A1210')
    gl = rgb('#26262B')
    for x, y in ((19, 16), (19, 17), (24, 16), (24, 17)):
        S.set(x, y, eye)
    for x, y in ((18, 16), (23, 16)):
        S.set(x, y, rgb('#FFFFFF'))
    # óculos redondos de aro fino
    ring_a = [(18, 14), (19, 14), (20, 14), (17, 15), (21, 15), (17, 16), (21, 16),
              (17, 17), (21, 17), (18, 18), (19, 18), (20, 18)]
    ring_b = [(24, 14), (25, 14), (23, 15), (26, 15), (23, 16), (26, 16),
              (23, 17), (26, 17), (24, 18), (25, 18)]
    for p in ring_a + ring_b:
        S.set(*p, gl)
    S.set(22, 15, gl)
    for x in (14, 15, 16):
        S.set(x, 15, gl)
    # sobrancelhas
    for x in (18, 19, 20):
        S.set(x, 12, haird)
    for x in (24, 25):
        S.set(x, 12, haird)
    # nariz
    S.set(28, 18, P['sk'])
    S.set(27, 19, P['sks'])
    S.set(26, 19, P['sks'])
    # bigode fino + sorriso + cavanhaque
    mouth = rgb('#5E2A1E')
    for x in range(23, 26):
        S.set(x, 20, mix(P['sks'], haird, 0.4))
    S.set(21, 20, mouth)
    S.set(26, 20, mouth)
    S.set(21, 21, mouth)
    for x in range(22, 26):
        S.set(x, 21, rgb('#FFFFFF'))
    S.set(26, 21, mouth)
    for x in range(22, 26):
        S.set(x, 22, mouth if x in (22, 25) else rgb('#B4584A'))
    for x, y in ((21, 23), (22, 23), (23, 23), (24, 23), (25, 23),
                 (21, 24), (22, 24), (23, 24), (24, 24), (22, 25), (23, 25)):
        S.set(x, y, haird if (x + y) % 3 else hair)
    S.set(20, 22, P['sks'])

    # cabelo: volume cacheado em cima, laterais na régua (degradê)
    fade = Layer(mix(P['sks'], haird, 0.62))
    fade.rows({10: (11, 15), 11: (10, 14), 12: (10, 13)})
    fade.rows({y: (10, 13) for y in range(13, 16)})
    fade.rows({16: (10, 12), 17: (10, 11), 18: (10, 11)}, mix(P['sks'], haird, 0.35))
    S.add(fade)
    _ear(S, P)

    hr = Layer(hair, haird)
    hr.rows({0: [(13, 15), (18, 21), (24, 26)],
             1: (11, 27), 2: (10, 29), 3: (9, 30), 4: (8, 30)})
    hr.rows({y: (8, 31) for y in range(5, 9)})
    hr.rows({9: (8, 30), 10: [(9, 14), (16, 29)], 11: [(17, 19), (22, 28)],
             12: [(23, 25)]})
    hr.recolor(curls(hair, haird, hairl))
    hr.outline()
    # bordinha de baixo irregular (cachos caindo na testa)
    for p in ((15, 10), (20, 11), (21, 11), (26, 12), (16, 11)):
        hr.px.pop(p, None)
    S.add(hr)
    return S.image()


def gabriel():
    S = Sprite(40, 70)
    P = dict(
        sk=rgb('#F1C9A8'), sks=rgb('#D9A684'), skl=rgb('#FADCC4'), skline=rgb('#A06C4C'),
        tee=rgb('#4B4346'), tees=rgb('#3A3336'), teeline=rgb('#221E20'),
        pant=rgb('#76653C'), pants=rgb('#5E5030'), pantline=rgb('#3A311C'),
        shoe=rgb('#1D1D20'), shoehl=rgb('#3E3E44'), shoeline=rgb('#0B0B0C'),
        sole=rgb('#F2F2F0'), soleline=rgb('#A5A5AA'),
        cuff=True, stripe=True,
    )
    beard, beardd, beardl = rgb('#3E2819'), rgb('#26170E'), rgb('#5C3D2A')
    cap, capd, capl = rgb('#202024'), rgb('#0E0E10'), rgb('#3C3C45')

    _arms_body_legs(S, P)

    # estampa TONE DEATH: o encapuzado roxo, os toca-discos e o letreiro azul
    purple, blue, yellow = rgb('#7563D6'), rgb('#7FA9F0'), rgb('#F4C04F')
    logo = {
        31: [(18, 20, purple)],
        32: [(17, 21, purple)],
        33: [(14, 15, yellow), (16, 22, purple), (23, 24, yellow)],
        34: [(15, 23, rgb('#E7E3EE'))],
        35: [(14, 24, blue)],
        36: [(14, 24, blue)],
        37: [(17, 21, yellow)],
    }
    for y, segs in logo.items():
        for x0, x1, c in segs:
            for x in range(x0, x1 + 1):
                S.set(x, y, c)
    S.set(19, 32, rgb('#2A2350'))
    S.set(18, 33, rgb('#F4C04F'))
    S.set(20, 33, rgb('#F4C04F'))
    for x in (15, 17, 19, 21, 23):
        S.set(x, 36, rgb('#4B6FB8'))

    _near_arm(S, P, band=rgb('#F4F4F4'))
    # relógio no pulso de trás
    for x in range(27, 31):
        S.set(x, 45, rgb('#151517'))

    _neck_head(S, P)
    _ear(S, P)

    # barba cheia: costeleta, maxilar, queixo e bigode
    bd = Layer(beard, beardd)
    bd.rows({14: (15, 16), 15: (15, 16), 16: (15, 16), 17: (15, 17),
             18: (15, 18), 19: (15, 27), 20: (15, 27), 21: (15, 27),
             22: (15, 26), 23: (15, 26), 24: (16, 25), 25: (17, 24), 26: (18, 23)})
    bd.recolor(lambda x, y, c: beardl if (x * 3 + y) % 5 == 0 else (beardd if (x + y * 2) % 7 == 0 else None))
    bd.outline()
    # bochecha aparecendo acima da barba
    for p in ((19, 19), (20, 19), (21, 19), (19, 20), (20, 20)):
        bd.px.pop(p, None)
    S.add(bd)
    # boca no meio da barba
    for x in range(22, 26):
        S.set(x, 22, rgb('#B4655A'))
    S.set(23, 21, rgb('#FFFFFF'))
    S.set(24, 21, rgb('#FFFFFF'))
    S.set(22, 21, beardd)
    S.set(25, 21, beardd)
    # nariz
    S.set(28, 17, P['sk'])
    S.set(28, 18, P['sk'])
    S.set(27, 18, P['sks'])
    S.set(26, 18, P['sks'])

    # olhos e óculos meio-aro (aro grosso em cima, fio fino embaixo)
    eye = rgb('#2A1A12')
    for x, y in ((19, 16), (19, 17), (24, 16), (24, 17)):
        S.set(x, y, eye)
    for x, y in ((18, 16), (23, 16)):
        S.set(x, y, rgb('#FFFFFF'))
    gl, glt = rgb('#141416'), rgb('#7C7C86')
    for x in list(range(17, 22)) + list(range(23, 27)):
        S.set(x, 14, gl)
    for x in (17, 21, 23, 26, 22):
        S.set(x, 15, gl)
    for x in range(14, 17):
        S.set(x, 15, gl)
    for x, y in ((17, 16), (21, 16), (23, 16), (26, 16), (18, 17), (20, 17),
                 (19, 17), (24, 17), (25, 17)):
        S.set(x, y, glt)
    S.set(19, 17, eye)
    S.set(24, 17, eye)
    # sobrancelhas
    for x in (18, 19, 20, 24, 25):
        S.set(x, 12, beardd)

    # alargador no lóbulo da orelha
    for x, y in ((13, 19), (14, 19), (13, 20), (14, 20)):
        S.set(x, y, rgb('#1A1214'))
    S.set(13, 19, rgb('#8A2A30'))

    # boné preto de seis gomos, aba para a frente
    cp = Layer(cap, capd)
    cp.rows({3: (14, 23), 4: (12, 25), 5: (11, 26), 6: (10, 27), 7: (10, 27),
             8: (9, 27), 9: (9, 27), 10: (9, 27), 11: (9, 26)})
    cp.recolor(lambda x, y, c: capl if (y in (4, 5) and 14 <= x <= 21) or x == 20 and 5 < y < 11 else None)
    cp.outline()
    cp.set(19, 2, capd)  # botão
    S.add(cp)
    brim = Layer(cap, capd)
    brim.rows({10: (24, 31), 11: (23, 33), 12: (24, 33)})
    brim.outline()
    for x in range(26, 32):
        brim.set(x, 11, capl)
    S.add(brim)
    # bordado branco na frente do boné (duas linhas de letrinhas)
    for x, y in ((21, 6), (22, 6), (24, 6), (25, 6), (26, 6),
                 (22, 8), (23, 8), (25, 8), (26, 8)):
        S.set(x, y, rgb('#EDEDED'))
    S.set(23, 6, rgb('#9A9AA0'))
    S.set(24, 8, rgb('#9A9AA0'))
    # cabelo curto aparecendo na nuca
    for x, y in ((10, 12), (11, 12), (10, 13), (11, 13), (12, 12), (10, 14)):
        S.set(x, y, beardd)
    return S.image()


def _white_sneakers(P):
    P.update(shoe=rgb('#F4F4F2'), shoehl=rgb('#FFFFFF'), shoeline=rgb('#A6A8AE'),
             sole=rgb('#E2E2E0'), soleline=rgb('#9A9CA2'))
    return P


def saldanha(pose='tablet'):
    """Contador: grisalho, óculos, barba curta branca, polo marinho para
    dentro da calça, cinto marrom, chino cinza-claro e tênis branco.
    pose='tablet': segura o tablet com as duas mãos, conferindo os números.
    pose='parado': em pé, braços soltos (o parado do jogo)."""
    S = Sprite(40, 70)
    P = _white_sneakers(dict(
        sk=rgb('#D3A07B'), sks=rgb('#B8835F'), skl=rgb('#E4B794'), skline=rgb('#83533A'),
        tee=rgb('#1F2B47'), tees=rgb('#18223A'), teeline=rgb('#0A0F1E'),
        pant=rgb('#B5B8BD'), pants=rgb('#9A9DA3'), pantline=rgb('#62666D'),
    ))
    P['shoeline'] = rgb('#878A92')
    navy_l = rgb('#34446D')

    if pose == 'parado':
        # braço de trás solto, com o relógio no pulso
        fa = Layer(P['sk'], P['skline'])
        fa.rows({y: (27, 30) for y in range(35, 46)})
        fa.rows({46: (27, 30), 47: (27, 30), 48: (28, 30)})
        fa.shade_side('r', 1, P['sks'])
        fa.outline()
        for x in range(27, 31):
            fa.set(x, 44, rgb('#141416'))
        fa.set(29, 44, rgb('#3E4A5E'))
        S.add(fa)

    # manga de trás (polo justa)
    fsl = Layer(P['tee'], P['teeline'])
    fsl.rows({29: (25, 28), 30: (25, 29)})
    fsl.rows({y: (25, 30) for y in range(31, 36)})
    fsl.shade_side('r', 1, P['tees'])
    fsl.outline()
    S.add(fsl)

    _legs_shoes(S, P, top=44)

    # polo por dentro da calça
    bd = Layer(P['tee'], P['teeline'])
    bd.rows({27: (14, 24), 28: (12, 26)})
    bd.rows({y: (11, 27) for y in range(29, 45)})
    bd.shade_side('r', 2, P['tees'])
    bd.outline()
    for x in range(13, 19):
        bd.set(x, 29, navy_l)
    for x in range(14, 25, 3):
        bd.set(x, 43, P['tees'])
    S.add(bd)
    # cinto marrom com fivela prateada
    for x in range(11, 28):
        S.set(x, 44, rgb('#8A5533'))
        S.set(x, 45, rgb('#5E3820'))
    for x, y in ((18, 44), (19, 44), (20, 44), (18, 45), (20, 45)):
        S.set(x, y, rgb('#D4D6DA'))
    S.set(19, 45, rgb('#6B6E74'))
    for x in (13, 24):
        S.set(x, 44, rgb('#A5A8AD'))

    if pose == 'parado':
        nsl = Layer(P['tee'], P['teeline'])
        nsl.rows({29: (9, 13), 30: (8, 14)})
        nsl.rows({y: (7, 14) for y in range(31, 35)})
        nsl.rows({35: (7, 13)})
        nsl.shade_side('l', 1, P['tees'])
        nsl.outline()
        for x in range(8, 13):
            nsl.set(x, 34, navy_l)
        S.add(nsl)
        na = Layer(P['sk'], P['skline'])
        na.rows({y: (8, 11) for y in range(36, 47)})
        na.rows({47: (8, 11), 48: (8, 11), 49: (9, 11)})
        na.shade_side('l', 1, P['sks'])
        na.outline()
        S.add(na)
    else:
        # tablet (costas prateadas), inclinado na frente do peito
        tb = Layer(rgb('#C3C7CF'), rgb('#555A64'))
        for x in range(17, 31):
            top = 38 - (x - 17) // 2
            for y in range(top, top + 8):
                tb.set(x, y)
        tb.outline()
        for x in range(18, 30):
            top = 38 - (x - 17) // 2
            tb.set(x, top, rgb('#8FD0F4'))       # brilho da tela virada para ele
            tb.set(x, top + 1, rgb('#E8EAEE'))
            tb.set(x, top + 6, rgb('#A3A8B2'))
        tb.set(26, 37, rgb('#8A8F99'))
        S.add(tb)

        # mão de trás segurando a borda do tablet, com relógio no pulso
        fh = Layer(P['sk'], P['skline'])
        fh.rows({33: (28, 30), 34: (27, 30), 35: (27, 30), 36: (28, 30)})
        fh.outline()
        S.add(fh)
        for x in (29, 30, 31):
            S.set(x, 37, rgb('#141416'))
        S.set(30, 37, rgb('#3E4A5E'))

        # braço da frente dobrado, a mão tocando a tela
        nsl = Layer(P['tee'], P['teeline'])
        nsl.rows({29: (9, 13), 30: (8, 14)})
        nsl.rows({y: (7, 14) for y in range(31, 35)})
        nsl.rows({35: (7, 13)})
        nsl.shade_side('l', 1, P['tees'])
        nsl.outline()
        for x in range(8, 13):
            nsl.set(x, 34, navy_l)
        S.add(nsl)
        na = Layer(P['sk'], P['skline'])
        na.rows({36: (8, 11), 37: (8, 11), 38: (8, 13), 39: (8, 19), 40: (9, 20),
                 41: (11, 20), 42: (17, 19)})
        na.shade_side('l', 1, P['sks'])
        na.outline()
        na.set(21, 38, P['sk'])
        S.add(na)
        S.set(21, 38, P['skline'])

    _neck_head(S, P)
    # gola da polo e a carcela com botões
    for x in range(15, 22):
        S.set(x, 29, P['tee'])
    for x, y in ((14, 27), (15, 27), (15, 28), (16, 28), (16, 29), (17, 29),
                 (22, 27), (21, 27), (21, 28), (20, 28), (20, 29), (19, 29)):
        S.set(x, y, navy_l)
    for x, y in ((14, 28), (15, 29), (22, 28), (21, 29)):
        S.set(x, y, P['teeline'])
    S.set(18, 29, P['sks'])
    for y in (30, 31, 32, 33):
        S.set(18, y, P['teeline'])
    S.set(19, 31, rgb('#4A5A86'))
    S.set(19, 33, rgb('#4A5A86'))
    _ear(S, P)

    # rosto: óculos retangulares, barba curta branca, olhar no tablet
    eye, gl = rgb('#2A1C14'), rgb('#1C1C20')
    for x, y in ((19, 17), (24, 17)):
        S.set(x, y, eye)
    for x, y in ((18, 17), (23, 17)):
        S.set(x, y, mix(P['sk'], eye, 0.35))
    for x in range(17, 22):
        S.set(x, 14, gl)
        S.set(x, 18, gl)
    for x in range(23, 27):
        S.set(x, 14, gl)
        S.set(x, 18, gl)
    for y in range(14, 19):
        for x in (17, 21, 23, 26):
            S.set(x, y, gl)
    S.set(22, 15, gl)
    for x in range(14, 17):
        S.set(x, 15, gl)
    grey, greyd, greyl = rgb('#8E8E93'), rgb('#5E5E65'), rgb('#C9C9CD')
    for x in (18, 19, 20, 24, 25):
        S.set(x, 12, greyd)
    S.set(28, 18, P['sk'])
    S.set(27, 19, P['sks'])
    S.set(26, 19, P['sks'])
    # barba: bigode mais escuro, cavanhaque branco e sombra no maxilar
    for x, y in ((15, 21), (16, 22), (17, 23), (18, 24), (16, 20), (17, 22), (19, 25)):
        S.set(x, y, mix(P['sks'], greyl, 0.5))
    for x in range(22, 27):
        S.set(x, 20, rgb('#7C7975'))
    for x in range(23, 26):
        S.set(x, 21, rgb('#6A3C2C'))
    for x, y in ((21, 21), (22, 21), (26, 21), (21, 22), (22, 22), (23, 22), (24, 22),
                 (25, 22), (26, 22), (20, 23), (21, 23), (22, 23), (23, 23), (24, 23),
                 (25, 23), (21, 24), (22, 24), (23, 24), (24, 24), (22, 25), (23, 25)):
        S.set(x, y, greyl if (x + y) % 3 else rgb('#A6A39F'))

    # cabelo grisalho curto, penteado para trás
    hr = Layer(grey, greyd)
    hr.rows({6: (15, 23), 7: (13, 25), 8: (11, 26), 9: (10, 27), 10: (10, 26),
             11: (10, 21), 12: (10, 17), 13: (10, 14), 14: (10, 13)})
    hr.rows({15: (10, 11), 16: (10, 11), 17: (10, 11), 18: (10, 11)}, mix(grey, greyl, 0.4))

    def strands(x, y, c):
        if y <= 8:
            return greyd if (x + y * 2) % 5 == 0 else (rgb('#76767C') if (x + y) % 3 else None)
        if (x * 2 + y) % 7 == 0:
            return greyl
        if (x + y * 3) % 6 == 0:
            return greyd
        return None
    hr.recolor(strands)
    hr.outline()
    for x, y in ((15, 13), (16, 13), (12, 15), (13, 15)):
        hr.px.pop((x, y), None)
    S.add(hr)
    return S.image()


def caio(pose='tablet'):
    """Consultor: cabelo cacheado curto, sorrisão, camisa de linho verde-oliva
    aberta sobre camiseta branca, crachá no cordão, chino marinho e tênis
    branco. pose='tablet': mostra o tablet com o check verde.
    pose='parado': em pé, braços soltos (o parado do jogo)."""
    S = Sprite(40, 70)
    P = _white_sneakers(dict(
        sk=rgb('#D9A47E'), sks=rgb('#BE8763'), skl=rgb('#E9BC99'), skline=rgb('#86553A'),
        tee=rgb('#6D7C56'), tees=rgb('#5A6845'), teeline=rgb('#333C25'),
        pant=rgb('#27324F'), pants=rgb('#1E2740'), pantline=rgb('#0F1528'),
    ))
    olive_l, olive_ll = rgb('#82936A'), rgb('#98A980')
    hair, haird, hairl = rgb('#2B1D16'), rgb('#160F0B'), rgb('#55392A')

    # braço de trás, camisa com a manga dobrada no antebraço
    fa = Layer(P['sk'], P['skline'])
    fa.rows({y: (27, 30) for y in range(40, 46)})
    fa.rows({46: (27, 30), 47: (27, 30), 48: (28, 30)})
    fa.shade_side('r', 1, P['sks'])
    fa.outline()
    S.add(fa)
    fsl = Layer(P['tee'], P['teeline'])
    fsl.rows({29: (25, 28), 30: (25, 29)})
    fsl.rows({y: (25, 30) for y in range(31, 41)})
    fsl.shade_side('r', 1, P['tees'])
    fsl.outline()
    for x in range(26, 30):
        fsl.set(x, 39, olive_l)
    S.add(fsl)

    _legs_shoes(S, P)

    # camisa aberta por cima da camiseta branca
    bd = Layer(P['tee'], P['teeline'])
    bd.rows({27: (14, 24), 28: (12, 26)})
    bd.rows({y: (11, 27) for y in range(29, 48)})
    bd.shade_side('r', 2, P['tees'])
    bd.outline()
    S.add(bd)
    wt, wts = rgb('#F6F6F2'), rgb('#DADBE0')
    for y in range(28, 47):
        for x in range(17, 22):
            S.set(x, y, wts if x == 21 else wt)
    for y in range(29, 47):
        S.set(16, y, P['teeline'])
        S.set(22, y, P['teeline'])
        S.set(15, y, olive_l)
    for y in (32, 36, 40, 44):
        S.set(23, y, rgb('#E6E1CC'))
    # bolso no peito
    for x in range(23, 27):
        S.set(x, 32, P['teeline'])
    for y in range(32, 36):
        S.set(23, y, P['teeline'])
        S.set(26, y, P['teeline'])
    for x in range(24, 26):
        S.set(x, 33, olive_l)

    if pose == 'parado':
        # braço da frente solto, manga dobrada no antebraço
        nsl = Layer(P['tee'], P['teeline'])
        nsl.rows({29: (9, 13), 30: (8, 14)})
        nsl.rows({y: (7, 14) for y in range(31, 40)})
        nsl.rows({40: (7, 13)})
        nsl.shade_side('l', 1, P['tees'])
        nsl.outline()
        for x in range(8, 13):
            nsl.set(x, 38, olive_ll)
            nsl.set(x, 39, olive_l)
        S.add(nsl)
        na = Layer(P['sk'], P['skline'])
        na.rows({y: (8, 11) for y in range(41, 47)})
        na.rows({47: (8, 11), 48: (8, 11), 49: (9, 11)})
        na.shade_side('l', 1, P['sks'])
        na.outline()
        S.add(na)
    else:
        # braço da frente erguido segurando o tablet
        nsl = Layer(P['tee'], P['teeline'])
        nsl.rows({29: (9, 13), 30: (8, 14), 31: (7, 14), 32: (6, 13), 33: (5, 12),
                  34: (4, 11), 35: (4, 10), 36: (4, 9), 37: (4, 8), 38: (5, 8)})
        nsl.shade_side('l', 1, P['tees'])
        nsl.outline()
        for x in range(5, 9):
            nsl.set(x, 36, olive_ll)
            nsl.set(x, 37, olive_l)
        S.add(nsl)
        na = Layer(P['sk'], P['skline'])
        na.rows({y: (3, 6) for y in range(28, 36)})
        na.shade_side('l', 1, P['sks'])
        na.outline()
        S.add(na)
        # tablet com a tela virada para quem olha
        tb = Layer(rgb('#1C1C21'), rgb('#08080A'))
        tb.rect(0, 14, 10, 28)
        tb.outline()
        tb.rect(1, 15, 9, 27, rgb('#F5F7F8'))
        S.add(tb)
        green, greend = rgb('#3DB64B'), rgb('#26863A')
        for x, y in ((2, 21), (3, 22), (4, 23), (5, 22), (6, 21), (7, 20), (8, 19)):
            S.set(x, y, green)
            S.set(x, y + 1, greend)
        hand = Layer(P['sk'], P['skline'])
        hand.rows({25: (2, 6), 26: (1, 7), 27: (1, 7), 28: (2, 7), 29: (3, 6)})
        hand.outline()
        S.add(hand)

    _neck_head(S, P)
    # gola da camiseta e gola da camisa
    for x in range(16, 21):
        S.set(x, 29, wts)
    for x, y in ((14, 27), (15, 27), (15, 28), (16, 28), (22, 27), (21, 27), (21, 28), (22, 28)):
        S.set(x, y, olive_l)
    S.set(14, 28, P['teeline'])
    S.set(23, 28, P['teeline'])
    # cordão do crachá
    navy = rgb('#1D2A4C')
    for x, y in ((16, 30), (16, 31), (17, 32), (17, 33), (18, 34), (18, 35),
                 (21, 30), (21, 31), (20, 32), (20, 33), (19, 34), (19, 35)):
        S.set(x, y, navy)
    cr = Layer(rgb('#F7F7F5'), rgb('#9EA1A8'))
    cr.rect(17, 37, 21, 42)
    cr.outline()
    S.add(cr)
    S.set(18, 36, rgb('#B9BCC2'))
    S.set(19, 36, rgb('#B9BCC2'))
    for x in (18, 19, 20):
        S.set(x, 39, rgb('#C7CAD0'))
    _ear(S, P)

    # rosto: sorrisão, barba por fazer
    eye = rgb('#1C120C')
    for x, y in ((19, 16), (19, 17), (24, 16), (24, 17)):
        S.set(x, y, eye)
    for x, y in ((18, 16), (23, 16)):
        S.set(x, y, rgb('#FFFFFF'))
    for x in (18, 19, 20, 24, 25):
        S.set(x, 13, haird)
    S.set(17, 14, haird)
    S.set(28, 18, P['sk'])
    S.set(27, 19, P['sks'])
    S.set(26, 19, P['sks'])
    stub = mix(P['sks'], haird, 0.28)
    for x, y in ((15, 21), (16, 22), (17, 23), (18, 24), (19, 24), (20, 25), (21, 25),
                 (22, 24), (25, 24), (26, 23), (20, 20), (21, 20), (26, 20)):
        S.set(x, y, stub)
    mouth = rgb('#5E2A1E')
    S.set(20, 21, mouth)
    S.set(27, 21, mouth)
    for x in range(21, 27):
        S.set(x, 21, rgb('#FFFFFF'))
    for x in range(21, 27):
        S.set(x, 22, mouth if x in (21, 26) else rgb('#B4584A'))
    S.set(20, 19, P['skl'])
    S.set(26, 18, P['skl'])

    # cachos curtos
    hr = Layer(hair, haird)
    hr.rows({4: [(14, 16), (18, 21), (23, 25)], 5: (12, 26), 6: (11, 27), 7: (10, 28),
             8: (10, 28), 9: (10, 28), 10: [(10, 14), (16, 27)],
             11: [(10, 12), (18, 19), (22, 24)], 12: (10, 12), 13: (10, 12), 14: (10, 11)})
    hr.recolor(curls(hair, haird, hairl))
    hr.outline()
    for p in ((15, 10), (26, 10), (13, 11)):
        hr.px.pop(p, None)
    S.add(hr)
    return S.image()


# ----------------------------------------------------------------- cachorros
# ------------------------------------------------- partes reaproveitáveis
def _far_arm_sl(S, P, sl, end, cuff=None, watch=None):
    """Braço de trás solto, com manga (sl = base, sombra, contorno) até a
    linha end; cuff pinta a barra dobrada, watch = (pulseira, mostrador)."""
    fa = Layer(P['sk'], P['skline'])
    fa.rows({y: (27, 30) for y in range(end - 1, 46)})
    fa.rows({46: (27, 30), 47: (27, 30), 48: (28, 30)})
    fa.shade_side('r', 1, P['sks'])
    fa.outline()
    if watch:
        for x in range(27, 31):
            fa.set(x, 44, watch[0])
        fa.set(29, 44, watch[1])
    S.add(fa)
    fsl = Layer(sl[0], sl[2])
    fsl.rows({29: (25, 28), 30: (25, 29)})
    fsl.rows({y: (25, 30) for y in range(31, end + 1)})
    fsl.shade_side('r', 1, sl[1])
    fsl.outline()
    if cuff:
        for x in range(26, 30):
            fsl.set(x, end - 1, cuff)
    S.add(fsl)


def _near_arm_sl(S, P, sl, end, cuff=None, watch=None):
    nsl = Layer(sl[0], sl[2])
    nsl.rows({29: (9, 13), 30: (8, 14)})
    nsl.rows({y: (7, 14) for y in range(31, end + 1)})
    nsl.rows({end + 1: (7, 13)})
    nsl.shade_side('l', 1, sl[1])
    nsl.outline()
    if cuff:
        for x in range(8, 13):
            nsl.set(x, end, cuff)
    S.add(nsl)
    na = Layer(P['sk'], P['skline'])
    na.rows({y: (8, 11) for y in range(end + 2, 47)})
    na.rows({47: (8, 11), 48: (8, 11), 49: (9, 11)})
    na.shade_side('l', 1, P['sks'])
    na.outline()
    if watch:
        for x in range(8, 12):
            na.set(x, 45, watch[0])
        na.set(10, 45, watch[1])
    S.add(na)


def _torso(S, c, bottom, waist=False, tex=None):
    """Tronco do corpo-base; waist=True afina a cintura (y 36 a 41)."""
    bd = Layer(c[0], c[2])
    bd.rows({27: (14, 24), 28: (12, 26)})
    for y in range(29, bottom + 1):
        bd.rows({y: (12, 26) if waist and 36 <= y <= 41 else (11, 27)})
    if tex:
        bd.recolor(tex)
    bd.shade_side('r', 2, c[1])
    bd.outline()
    S.add(bd)
    return bd


def _hoop(S, x, y, gold=rgb('#E2B648'), dark=rgb('#A87C22')):
    for dx, dy in ((0, 0), (-1, 1), (-1, 2), (0, 3), (1, 2), (1, 1)):
        S.set(x + dx, y + dy, gold if dy < 2 else dark)


def _face(S, P, brow, lash=None, smile='teeth', lip=None):
    eye = rgb('#1C120C')
    for x, y in ((19, 16), (19, 17), (24, 16), (24, 17)):
        S.set(x, y, eye)
    for x, y in ((18, 16), (23, 16)):
        S.set(x, y, rgb('#FFFFFF'))
    if lash:
        for x, y in ((18, 15), (19, 15), (20, 15), (24, 15), (25, 15), (26, 15)):
            S.set(x, y, lash)
    for x in (18, 19, 20, 24, 25):
        S.set(x, 13, brow)
    S.set(28, 18, P['sk'])
    S.set(27, 19, P['sks'])
    S.set(26, 19, P['sks'])
    mouth = rgb('#5E2A1E')
    if smile == 'teeth':
        S.set(21, 20, mouth)
        S.set(26, 20, mouth)
        for x in range(22, 26):
            S.set(x, 21, rgb('#FFFFFF'))
            S.set(x, 20, lip or mix(P['sks'], mouth, 0.35))
        S.set(21, 21, mouth)
        S.set(26, 21, mouth)
        for x in range(22, 26):
            S.set(x, 22, lip or rgb('#B4584A'))
        S.set(22, 22, mouth)
        S.set(25, 22, mouth)
    else:
        for x, y in ((21, 21), (22, 22), (23, 22), (24, 22), (25, 21)):
            S.set(x, y, mouth)


def vivi():
    """Vivi: cachos volumosos castanhos com luzes caramelo, argolas e
    colar dourados, blusa laranja canelada de decote quadrado e manga 3/4,
    calça pantalona creme de cintura alta e scarpin caramelo."""
    S = Sprite(40, 70)
    P = dict(sk=rgb('#B07148'), sks=rgb('#93583A'), skl=rgb('#C4875C'), skline=rgb('#5E3420'),
             tee=rgb('#D9623A'), tees=rgb('#B84D2C'), teeline=rgb('#7A2E18'))
    top = (P['tee'], P['tees'], P['teeline'])
    cream = (rgb('#F0E8D9'), rgb('#D6CBB8'), rgb('#A0957F'))
    hair, haird, hairl, hairll = rgb('#3B2417'), rgb('#21130B'), rgb('#7E5130'), rgb('#B07A42')
    gold, goldd = rgb('#E2B648'), rgb('#A87C22')

    # cabelo de trás: o volume de cachos que cai pelas costas
    hb = Layer(hair, haird)
    hb.rows({1: (12, 24), 2: (9, 27), 3: (7, 29), 4: (6, 30)})
    hb.rows({y: (5, 31) for y in range(5, 9)})
    hb.rows({y: (4, 31) for y in range(9, 15)})
    hb.rows({y: (3, 30) for y in range(15, 23)})
    hb.rows({y: (3, 29) for y in range(23, 29)})
    hb.rows({y: [(3, 14), (24, 29)] for y in range(29, 35)})
    hb.rows({y: (4, 13) for y in range(35, 41)})
    hb.rows({41: (5, 11), 42: [(6, 7), (9, 10)]})
    tex = curls(hair, haird, hairl)
    hb.recolor(lambda x, y, c: hairll if (x * 5 + y * 3) % 17 == 0 else tex(x, y, c))
    hb.outline()
    for p in ((3, 16), (3, 21), (4, 27), (29, 33), (4, 38), (30, 19), (31, 12)):
        hb.px.pop(p, None)
    S.add(hb)

    _far_arm_sl(S, P, top, 40, watch=(gold, rgb('#F7EFD0')))

    # pantalona creme e scarpin
    for legs in (((19, 26), (19, 27), 57), ((12, 19), (11, 19), 58)):
        (a0, a1), (b0, b1), y1 = legs
        lg = Layer(cream[0], cream[2])
        lg.rows({y: (a0, a1) if y < 49 else (b0, b1) for y in range(41, y1 + 1)})
        lg.shade_side('r', 2, cream[1])
        lg.outline()
        S.add(lg)
    # vinco da pantalona
    for y in range(45, 58):
        S.set(15, y, mix(cream[0], cream[1], 0.6))
    for y in range(46, 57):
        S.set(23, y, mix(cream[0], cream[1], 0.5))
    tan, tand, tanl = rgb('#C88A57'), rgb('#6E4424'), rgb('#E6B585')
    for rows, hl in (({58: (20, 27), 59: (19, 29), 60: [(19, 20), (24, 29)]}, (26, 59)),
                     ({59: (13, 21), 60: (12, 23), 61: [(12, 13), (17, 23)]}, (20, 60))):
        sh = Layer(tan, tand)
        sh.rows(rows)
        sh.outline()
        sh.set(*hl, tanl)
        S.add(sh)

    # blusa canelada por dentro da calça
    ribs = lambda x, y, c: mul(c, 0.92) if x % 2 == 0 else None
    _torso(S, top, 41, waist=True, tex=ribs)
    for x in range(12, 27):
        S.set(x, 41, cream[0])
        S.set(x, 42, cream[1])

    _near_arm_sl(S, P, top, 40)

    _neck_head(S, P)
    # decote quadrado e colar
    for y in range(28, 32):
        for x in range(15, 22):
            S.set(x, y, P['sk'] if y < 31 else P['sks'])
    for y in range(28, 32):
        S.set(14, y, P['tees'])
        S.set(22, y, P['tees'])
    for x in range(14, 23):
        S.set(x, 32, P['teeline'])
    for x, y in ((15, 29), (16, 30), (17, 30), (18, 30), (19, 30), (20, 29)):
        S.set(x, y, gold)
    S.set(18, 31, goldd)

    _face(S, P, brow=haird, lash=rgb('#1A0E08'), lip=rgb('#8E4434'))
    S.set(25, 18, P['skl'])

    # cachos da frente e do alto, por cima da testa e da orelha
    hf = Layer(hair, haird)
    hf.rows({y: (8, 30) for y in range(3, 9)})
    hf.rows({9: (8, 29), 10: [(8, 22), (25, 29)], 11: [(8, 18), (26, 29)], 12: [(8, 16), (27, 29)]})
    hf.rows({y: (8, 14) for y in range(13, 24)})
    hf.rows({24: (9, 13), 25: (10, 12)})
    hf.recolor(lambda x, y, c: hairll if (x * 5 + y * 3) % 17 == 0 else tex(x, y, c))
    hf.outline()
    for p in ((8, 4), (30, 5), (22, 10), (18, 11), (8, 15), (8, 20), (14, 23), (29, 12)):
        hf.px.pop(p, None)
    S.add(hf)
    _hoop(S, 15, 21)
    return S.image()


def nina():
    """Nina: coque alto bagunçado com mechas soltas, argolas, blazer verde
    oliva com a manga puxada, regata creme, cinto marrom, calça creme e
    mocassim marrom."""
    S = Sprite(40, 70)
    P = dict(sk=rgb('#E6B791'), sks=rgb('#CB9873'), skl=rgb('#F3CBA8'), skline=rgb('#8E5A3C'),
             pant=rgb('#E6DCC9'), pants=rgb('#CDBFA8'), pantline=rgb('#978A73'),
             shoe=rgb('#7A4A2A'), shoehl=rgb('#A06A40'), shoeline=rgb('#3E2414'),
             sole=rgb('#4A2C18'), soleline=rgb('#2A180C'))
    olive = (rgb('#5E6838'), rgb('#4B532C'), rgb('#2A3018'))
    olive_l = rgb('#76824A')
    P['teeline'] = olive[2]
    hair, haird, hairl = rgb('#3A2418'), rgb('#21140C'), rgb('#6A4430')
    gold, goldd = rgb('#E2B648'), rgb('#A87C22')

    _far_arm_sl(S, P, olive, 39, cuff=olive_l, watch=(rgb('#7A4A2A'), rgb('#E2B648')))
    _legs_shoes(S, P, top=44)

    _torso(S, olive, 47)
    # regata creme, cinto e calça aparecendo na frente aberta do blazer
    tank, tanks = rgb('#F1EADC'), rgb('#D8CFBE')
    for y in range(28, 42):
        for x in range(17, 22):
            S.set(x, y, tanks if x == 21 or x % 2 == 0 else tank)
    for x in range(17, 22):
        S.set(x, 42, rgb('#7A4A2A'))
        S.set(x, 43, rgb('#5C3620'))
    S.set(18, 42, gold)
    S.set(19, 42, gold)
    S.set(18, 43, goldd)
    for y in range(44, 48):
        for x in range(17, 22):
            S.set(x, y, P['pant'] if x < 21 else P['pants'])
    # lapelas
    for y in range(28, 47):
        S.set(16, y, olive[2])
        S.set(22, y, olive[2])
    for x, y in ((15, 28), (15, 29), (15, 30), (16, 31), (15, 31), (16, 32), (16, 33),
                 (23, 28), (23, 29), (23, 30), (22, 31), (23, 31), (22, 32), (22, 33)):
        S.set(x, y, olive_l)
    S.set(23, 40, olive[2])
    for x in range(24, 27):
        S.set(x, 42, olive[1])

    _near_arm_sl(S, P, olive, 39, cuff=olive_l)

    _neck_head(S, P)
    for x in range(16, 22):
        S.set(x, 29, P['sks'])
    for x, y in ((16, 30), (17, 31), (18, 31), (19, 31), (20, 30)):
        S.set(x, y, gold)
    S.set(18, 32, gold)
    S.set(18, 33, goldd)
    _ear(S, P)
    _face(S, P, brow=haird, lash=rgb('#1A0E08'), smile='closed')
    S.set(25, 18, P['skl'])
    for x in range(22, 26):
        S.set(x, 21, rgb('#B4655A'))

    # cabelo preso, com o coque no alto e mechas soltas
    hr = Layer(hair, haird)
    hr.rows({0: (14, 19), 1: (12, 21), 2: (11, 22), 3: (11, 23), 4: (11, 23), 5: (12, 23),
             6: (12, 24), 7: (11, 26), 8: (10, 27), 9: (10, 27), 10: (10, 26), 11: (10, 22),
             12: (10, 18), 13: (10, 15), 14: (10, 13)})
    hr.rows({y: (10, 12) for y in range(15, 22)})
    hr.recolor(strands(hair, haird, hairl))
    hr.outline()
    for x, y in ((13, 2), (16, 1), (19, 3), (14, 4), (20, 5)):
        hr.set(x, y, hairl)
    S.add(hr)
    for x, y in ((26, 11), (27, 12), (27, 13), (26, 14), (27, 15), (27, 16), (26, 17), (27, 18),
                 (13, 14), (14, 15), (13, 16), (14, 17), (13, 18),
                 (11, 22), (12, 23), (11, 24), (10, 4), (24, 2), (25, 3)):
        S.set(x, y, haird)
    _hoop(S, 14, 20)
    return S.image()


def strands(base, dark, light):
    def fn(x, y, c):
        if (x * 2 + y) % 7 == 0:
            return light
        if (x + y * 3) % 6 == 0:
            return dark
        return None
    return fn


def otto():
    """Otto: cabelo grisalho ondulado, barba branca aparada, óculos redondos
    de tartaruga, camisa branca com a manga dobrada, colete de tricô verde
    oliva, gravata listrada, calça de lã e sapato de couro."""
    S = Sprite(40, 70)
    P = dict(sk=rgb('#D6A27C'), sks=rgb('#BA8562'), skl=rgb('#E6B894'), skline=rgb('#7E5038'),
             pant=rgb('#5E4E42'), pants=rgb('#4A3D33'), pantline=rgb('#2A221C'),
             shoe=rgb('#5C3A22'), shoehl=rgb('#8A5C38'), shoeline=rgb('#2A1A0E'),
             sole=rgb('#3A2414'), soleline=rgb('#1E120A'))
    shirt = (rgb('#F6F5F0'), rgb('#DADBDE'), rgb('#9C9EA6'))
    vest = (rgb('#4E5838'), rgb('#3E462C'), rgb('#23281A'))
    P['teeline'] = vest[2]
    grey, greyd, greyl = rgb('#A9A9AE'), rgb('#6E6E75'), rgb('#DADADE')

    _far_arm_sl(S, P, shirt, 40, cuff=rgb('#C9CBD0'), watch=(rgb('#5C3A22'), rgb('#E9DFC6')))
    _legs_shoes(S, P, top=45)

    knit = lambda x, y, c: (mul(c, 1.08) if (x + y * 2) % 4 == 0 else
                            (mul(c, 0.94) if (x * 3 + y) % 5 == 0 else None))
    _torso(S, vest, 45, tex=knit)
    for x in range(12, 27):
        S.set(x, 44, vest[1])
    # gola V com a camisa e a gravata
    for y, (x0, x1) in {28: (15, 22), 29: (15, 21), 30: (16, 21), 31: (16, 20), 32: (17, 20),
                        33: (17, 19), 34: (18, 19), 35: (18, 18)}.items():
        for x in range(x0, x1 + 1):
            S.set(x, y, shirt[0] if x < x1 else shirt[1])
        S.set(x0 - 1, y, vest[2])
        S.set(x1 + 1, y, vest[2])
    tie, tiel = rgb('#3E5A3A'), rgb('#8FA36A')
    for y in range(29, 36):
        for x in (18, 19):
            if y < 35 or x == 18:
                S.set(x, y, tiel if (y + x) % 3 == 0 else tie)

    _near_arm_sl(S, P, shirt, 40, cuff=rgb('#C9CBD0'))

    _neck_head(S, P)
    # gola da camisa e o nó da gravata
    for x, y in ((15, 27), (16, 27), (16, 28), (17, 28), (22, 27), (21, 27), (21, 28), (20, 28)):
        S.set(x, y, shirt[0])
    for x, y in ((15, 28), (22, 28), (16, 29), (21, 29)):
        S.set(x, y, shirt[2])
    for x in (18, 19):
        S.set(x, 28, tie)
        S.set(x, 29, tie)
    _ear(S, P)

    # barba branca aparada, bigode um pouco mais escuro
    bd = Layer(rgb('#D4D1CC'), rgb('#9C9893'))
    bd.rows({15: (15, 16), 16: (15, 16), 17: (15, 16), 18: (15, 17), 19: (15, 18),
             20: (15, 27), 21: (15, 27), 22: (15, 26), 23: (16, 26), 24: (17, 25), 25: (18, 24)})
    bd.recolor(lambda x, y, c: rgb('#EDEBE7') if (x * 3 + y) % 5 == 0 else
               (rgb('#B5B1AB') if (x + y * 2) % 6 == 0 else None))
    bd.outline()
    S.add(bd)
    for x in range(21, 28):
        S.set(x, 20, rgb('#8E8A85'))
    for x in range(22, 26):
        S.set(x, 21, rgb('#8A4A3E'))
    S.set(21, 21, rgb('#6E3A2E'))
    S.set(26, 21, rgb('#6E3A2E'))
    S.set(28, 18, P['sk'])
    S.set(27, 19, P['sks'])
    # olhos e óculos redondos de tartaruga
    eye = rgb('#2A1C14')
    for x, y in ((19, 16), (19, 17), (24, 16), (24, 17)):
        S.set(x, y, eye)
    tort, tortl = rgb('#5A3418'), rgb('#9A6232')
    ring_a = [(18, 14), (19, 14), (20, 14), (17, 15), (21, 15), (17, 16), (21, 16),
              (17, 17), (21, 17), (18, 18), (19, 18), (20, 18)]
    ring_b = [(24, 14), (25, 14), (23, 15), (26, 15), (23, 16), (26, 16),
              (23, 17), (26, 17), (24, 18), (25, 18)]
    for i, p in enumerate(ring_a + ring_b):
        S.set(*p, tortl if i % 4 == 0 else tort)
    S.set(22, 15, tort)
    for x in (14, 15, 16):
        S.set(x, 15, tort)
    for x in (18, 19, 20, 24, 25):
        S.set(x, 12, greyd)

    # cabelo grisalho ondulado, cheio, penteado para trás
    hr = Layer(grey, greyd)
    hr.rows({4: (15, 23), 5: (13, 25), 6: (11, 27), 7: (10, 28), 8: (9, 28), 9: (9, 28),
             10: (9, 27), 11: (9, 23), 12: (9, 19), 13: (9, 16), 14: (9, 14)})
    hr.rows({y: (9, 12) for y in range(15, 21)})
    hr.rows({21: (10, 12), 22: (10, 11)})

    def waves(x, y, c):
        k = (x + (y // 2) * 2) % 5
        if k == 0:
            return greyl
        if k == 3:
            return greyd
        return None
    hr.recolor(waves)
    hr.outline()
    for p in ((28, 7), (9, 9), (9, 18)):
        hr.px.pop(p, None)
    S.add(hr)
    return S.image()


class _SLayer(Layer):
    """Camada que desenha numa escala k: as coordenadas do desenho original
    são convertidas na hora e o contorno sai já no tamanho final."""
    def __init__(self, k, base, line=None):
        super().__init__(base, line)
        self.k = k

    def _m(self, v):
        return int(math.floor(v * self.k + 0.5))

    def set(self, x, y, c=None):
        super().set(self._m(x), self._m(y), c)

    def rows(self, spec, c=None):
        out = {}
        for y, segs in spec.items():
            if isinstance(segs[0], int):
                segs = [segs]
            out.setdefault(self._m(y), []).extend((self._m(a), self._m(b)) for a, b in segs)
        super().rows(out, c)

    def rect(self, x0, y0, x1, y1, c=None):
        super().rect(self._m(x0), self._m(y0), self._m(x1), self._m(y1), c)


class _SSprite(Sprite):
    def __init__(self, k, w, h):
        self.k = k
        dim = (lambda v: v) if k == 1 else (lambda v: int(math.ceil(v * k)) + 1)
        super().__init__(dim(w), dim(h))

    def set(self, x, y, c):
        m = lambda v: int(math.floor(v * self.k + 0.5))
        super().set(m(x), m(y), c)


def _tufts(layer, seed, c, every=4):
    """Pelo duro: pontinhas soltas para fora do contorno."""
    for (x, y) in layer.edges():
        if (x * 7 + y * 13 + seed) % every:
            continue
        for dx, dy in ((0, -1), (-1, 0), (1, 0)):
            q = (x + dx, y + dy)
            if q not in layer.px:
                layer.px[q] = c
                break


def flora(k=1.0):
    """Labrador preta, sentada, pelo brilhante e coleira vermelha."""
    L = lambda base, line=None: _SLayer(k, base, line)
    S = _SSprite(k, 48, 46)
    fur, furd, furl, furll = rgb('#2A2A31'), rgb('#141418'), rgb('#434552'), rgb('#666A7D')
    line = rgb('#09090B')

    # rabo no chão
    tl = L(fur, line)
    tl.rows({38: (4, 9), 39: (3, 11), 40: (3, 12), 41: (5, 12)})
    tl.outline()
    S.add(tl)

    # corpo sentado (anca grande atrás, peito na frente)
    bd = L(fur, line)
    bd.rows({18: (19, 30), 19: (17, 32), 20: (15, 33), 21: (13, 33), 22: (12, 33),
             23: (11, 33), 24: (10, 33), 25: (9, 33), 26: (9, 33)})
    bd.rows({y: (8, 33) for y in range(27, 37)})
    bd.rows({37: (9, 33), 38: (9, 33), 39: (10, 33), 40: (11, 33), 41: (12, 33)})
    bd.shade_side('l', 2, furd)
    bd.outline()
    for x, y in ((14, 24), (15, 23), (16, 22), (17, 22), (13, 25), (12, 27), (12, 28),
                 (13, 26), (18, 21), (19, 20)):
        bd.set(x, y, furl)
    for x, y in ((15, 24), (14, 25), (16, 23)):
        bd.set(x, y, furll)
    for x, y in ((14, 32), (15, 31), (16, 31), (17, 31), (18, 32), (19, 33), (19, 34),
                 (19, 35), (19, 36), (19, 37)):
        bd.set(x, y, furd)
    S.add(bd)

    hp = L(fur, line)
    hp.rows({40: (10, 19), 41: (9, 20), 42: (9, 21), 43: (10, 21)})
    hp.outline()
    hp.set(13, 41, furl)
    S.add(hp)

    for x0, y1 in ((25, 43), (30, 44)):
        lg = L(fur, line)
        lg.rect(x0, 30, x0 + 4, y1 - 2)
        lg.rows({y1 - 1: (x0, x0 + 5), y1: (x0, x0 + 5)})
        lg.shade_side('l', 1, furd)
        lg.outline()
        lg.set(x0 + 2, 31, furl)
        lg.set(x0 + 2, 32, furl)
        lg.set(x0 + 2, y1, furd)
        lg.set(x0 + 4, y1, furd)
        S.add(lg)

    ch = L(fur, line)
    ch.rows({18: (26, 33), 19: (25, 34), 20: (24, 35), 21: (24, 35), 22: (24, 35),
             23: (24, 35), 24: (24, 35), 25: (24, 34), 26: (25, 34), 27: (25, 34),
             28: (26, 34), 29: (26, 33), 30: (27, 33), 31: (28, 32)})
    ch.outline(skip='t')
    for x, y in ((31, 23), (32, 24), (32, 25), (33, 26), (31, 24)):
        ch.set(x, y, furl)
    S.add(ch)

    # coleira vermelha com plaquinha dourada
    col = L(rgb('#D7352E'), rgb('#8E1C18'))
    col.rows({19: (23, 35), 20: (23, 35)})
    col.outline()
    for x in range(25, 34):
        col.set(x, 19, rgb('#EF5A50'))
    S.add(col)
    for x, y, c in ((33, 21, rgb('#F4C04F')), (34, 21, rgb('#F4C04F')),
                    (33, 22, rgb('#C99A2E')), (34, 22, rgb('#F7D57E'))):
        S.set(x, y, c)

    # cabeça grande (proporção de pet do Habbo): crânio largo e focinho
    # largo de labrador apontando para a frente-direita
    hd = L(fur, line)
    hd.rows({0: (22, 30), 1: (20, 32), 2: (19, 34), 3: (18, 35), 4: (17, 36),
             5: (17, 37), 6: (17, 39), 7: (17, 41), 8: (17, 43), 9: (17, 44),
             10: (17, 45), 11: (17, 45), 12: (18, 45), 13: (18, 44), 14: (19, 43),
             15: (20, 42), 16: (22, 40), 17: (25, 37)})
    hd.shade_side('l', 1, furd)
    hd.outline()
    # brilho no topo da cabeça
    for x in range(22, 29):
        hd.set(x, 1, furl)
    for x in range(21, 30):
        hd.set(x, 2, furl if x in (21, 22, 28, 29) else furll)
    for x in range(23, 27):
        hd.set(x, 3, furl)
    # brilho no dorso do focinho
    for x in range(36, 43):
        hd.set(x, 8, furl)
    for x in range(38, 42):
        hd.set(x, 9, furll)
    # bochecha e linha da boca (separa o focinho do crânio)
    for x, y in ((31, 11), (31, 12), (32, 13), (33, 14)):
        hd.set(x, y, furd)
    for x in range(34, 42):
        hd.set(x, 14, line)
    hd.set(42, 13, line)
    for x in range(26, 37):
        hd.set(x, 16, furd)
    S.add(hd)

    # nariz grande
    nose = {7: (41, 43), 8: (41, 45), 9: (41, 46), 10: (42, 46), 11: (43, 45)}
    for y, (x0, x1) in nose.items():
        for x in range(x0, x1 + 1):
            S.set(x, y, rgb('#0B0B0D'))
    S.set(42, 8, rgb('#6A6A78'))
    S.set(43, 8, rgb('#3A3A44'))
    S.set(44, 10, rgb('#2A2A30'))

    # olhos castanhos com brilho (o de perto maior, o de longe menor)
    dk, ir, irl, hi = rgb('#120A06'), rgb('#5A2E14'), rgb('#8C4E24'), rgb('#FFFFFF')
    for x, y, c in ((27, 6, dk), (28, 6, dk), (29, 6, dk), (27, 7, ir), (28, 7, hi),
                    (29, 7, ir), (27, 8, irl), (28, 8, irl), (29, 8, ir)):
        S.set(x, y, c)
    for x, y, c in ((34, 6, dk), (35, 6, dk), (34, 7, ir), (35, 7, hi), (34, 8, irl), (35, 8, ir)):
        S.set(x, y, c)
    for x in (27, 28, 29):
        S.set(x, 5, furl)
    S.set(34, 5, furl)
    S.set(35, 5, furl)

    # orelha caída do lado de perto
    ear = L(fur, line)
    ear.rows({3: (18, 22), 4: (16, 23), 5: (15, 24), 6: (14, 24), 7: (14, 24),
              8: (14, 24), 9: (14, 24), 10: (14, 23), 11: (14, 23), 12: (15, 23),
              13: (15, 22), 14: (16, 22), 15: (17, 21), 16: (18, 20)})
    ear.outline()
    for y in range(6, 13):
        ear.set(17, y, furd)
    for x, y in ((19, 4), (20, 4), (21, 4), (22, 5), (18, 5)):
        ear.set(x, y, furl)
    S.add(ear)
    return S.image()


def lupin(k=1.0):
    """Vira-lata pequeno: preto, pelo duro, barba e bochechas caramelo,
    sobrancelhas de velhinho e orelhas com a pontinha dobrada."""
    L = lambda base, line=None: _SLayer(k, base, line)
    S = _SSprite(k, 38, 34)
    fur, furd, furl = rgb('#25242A'), rgb('#121115'), rgb('#403E4A')
    tan, tand, tanl = rgb('#7C4B2A'), rgb('#55321B'), rgb('#A66C40')
    line = rgb('#070708')

    tl = L(fur, line)
    tl.rows({17: (5, 6), 18: (4, 7), 19: (4, 7), 20: (5, 8), 21: (5, 9), 22: (6, 10)})
    _tufts(tl, 1, line, 3)
    tl.outline()
    S.add(tl)

    bd = L(fur, line)
    bd.rows({16: (13, 21), 17: (11, 23), 18: (10, 24), 19: (9, 24), 20: (8, 24)})
    bd.rows({y: (7, 24) for y in range(21, 27)})
    bd.rows({27: (8, 24), 28: (8, 24)})
    bd.shade_side('l', 1, furd)
    bd.outline()
    _tufts(bd, 2, line)
    for x, y in ((11, 18), (12, 18), (10, 19), (9, 21), (13, 17), (14, 17)):
        bd.set(x, y, furl)
    for x, y in ((11, 24), (12, 23), (13, 23), (14, 24), (14, 25), (14, 26)):
        bd.set(x, y, furd)
    S.add(bd)

    hp = L(fur, line)
    hp.rows({27: (8, 14), 28: (7, 15), 29: (7, 15)})
    hp.outline()
    S.add(hp)

    for x0, y1 in ((17, 30), (21, 31)):
        lg = L(fur, line)
        lg.rect(x0, 22, x0 + 2, y1 - 2)
        lg.rows({y1 - 1: (x0, x0 + 3), y1: (x0, x0 + 3)})
        lg.outline()
        lg.set(x0 + 1, 24, furl)
        S.add(lg)

    ch = L(fur, line)
    ch.rows({15: (19, 25), 16: (18, 26), 17: (18, 26), 18: (18, 26), 19: (18, 26),
             20: (19, 26), 21: (19, 25), 22: (20, 25)})
    ch.outline(skip='t')
    _tufts(ch, 3, line)
    for x, y in ((23, 18), (24, 19), (22, 20), (23, 21)):
        ch.set(x, y, furl)
    S.add(ch)

    # cabeça quadradinha de terrier
    hd = L(fur, line)
    hd.rows({3: (16, 23), 4: (14, 25), 5: (13, 26), 6: (13, 27), 7: (13, 28),
             8: (13, 30), 9: (13, 32), 10: (13, 33), 11: (13, 33), 12: (13, 33),
             13: (14, 33), 14: (14, 32), 15: (15, 31), 16: (16, 30)})
    hd.shade_side('l', 1, furd)
    hd.outline()
    _tufts(hd, 5, line)
    for x in range(17, 22):
        hd.set(x, 4, furl)
    hd.set(16, 5, furl)
    S.add(hd)

    # bochecha e barba: pelo duro preto mesclado com caramelo, mais
    # comprido embaixo do queixo
    tan, tand, tanl = rgb('#70462A'), rgb('#4A2D1A'), rgb('#94603A')
    for x, y in ((22, 10), (23, 11), (21, 11), (22, 12)):
        S.set(x, y, tand)
    S.set(23, 10, tan)
    mz = L(fur, line)
    mz.rows({8: (27, 31), 9: (25, 33), 10: (24, 34), 11: (24, 34), 12: (23, 33)})
    mz.outline(skip='lt')
    S.add(mz)
    br = L(tan, line)
    br.rows({12: (24, 32), 13: (23, 33), 14: (23, 32), 15: (23, 32), 16: (24, 31),
             17: [(24, 26), (28, 30)], 18: [(25, 25), (29, 29)]})

    def mixfur(x, y, c):
        k = (x * 5 + y * 3) % 6
        return {0: tanl, 1: tan, 2: fur, 3: tand, 4: tan, 5: furd}[k]
    br.recolor(mixfur)
    br.outline(c=line)
    S.add(br)
    for x, y in ((26, 10), (28, 11), (30, 10), (25, 11), (29, 9)):
        S.set(x, y, tand)
    # boquinha
    for x in range(28, 33):
        S.set(x, 12, rgb('#1A0E07'))

    # nariz
    for x, y in ((31, 7), (32, 7), (33, 7), (31, 8), (32, 8), (33, 8), (34, 8),
                 (32, 9), (33, 9), (34, 9)):
        S.set(x, y, rgb('#0A0A0B'))
    S.set(32, 7, rgb('#62626E'))

    # olhos redondinhos e sobrancelhas peludas
    dk, ir, hi = rgb('#140B06'), rgb('#5E3216'), rgb('#FFFFFF')
    for x, y, c in ((20, 7, dk), (21, 7, hi), (20, 8, ir), (21, 8, dk),
                    (26, 7, dk), (27, 7, hi), (26, 8, ir), (27, 8, dk)):
        S.set(x, y, c)
    for x, y in ((19, 5), (20, 5), (21, 5), (22, 5), (25, 5), (26, 5), (27, 5)):
        S.set(x, y, tanl if (x + y) % 2 else tan)

    # orelhas semi-erguidas com a pontinha dobrada para a frente
    near = L(fur, line)
    near.rows({1: (15, 17), 2: (14, 18), 3: (12, 18), 4: (11, 17), 5: (10, 15), 6: (10, 13)})
    near.outline()
    near.set(14, 3, furl)
    near.set(13, 4, furd)
    S.add(near)
    far = L(fur, line)
    far.rows({0: (22, 25), 1: (22, 27), 2: (23, 28), 3: (25, 29), 4: (27, 29)})
    far.outline()
    far.set(24, 1, furl)
    far.set(26, 2, furd)
    S.add(far)
    return S.image()
