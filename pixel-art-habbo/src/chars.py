"""Os quatro personagens, desenhados pixel a pixel em vista 3/4 (olhando
para a direita, como os avatares do Habbo na direção 2)."""
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

    # pernas
    fl = Layer(P['pant'], P['pantline'])
    fl.rect(19, 46, 26, 58)
    fl.shade_side('r', 2, P['pants'])
    fl.outline()
    S.add(fl)
    nl = Layer(P['pant'], P['pantline'])
    nl.rect(12, 46, 19, 59)
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


# ----------------------------------------------------------------- cachorros
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


def flora():
    """Labrador preta, sentada, pelo brilhante e coleira vermelha."""
    S = Sprite(48, 46)
    fur, furd, furl, furll = rgb('#2A2A31'), rgb('#141418'), rgb('#434552'), rgb('#666A7D')
    line = rgb('#09090B')

    # rabo no chão
    tl = Layer(fur, line)
    tl.rows({38: (4, 9), 39: (3, 11), 40: (3, 12), 41: (5, 12)})
    tl.outline()
    S.add(tl)

    # corpo sentado (anca grande atrás, peito na frente)
    bd = Layer(fur, line)
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

    hp = Layer(fur, line)
    hp.rows({40: (10, 19), 41: (9, 20), 42: (9, 21), 43: (10, 21)})
    hp.outline()
    hp.set(13, 41, furl)
    S.add(hp)

    for x0, y1 in ((25, 43), (30, 44)):
        lg = Layer(fur, line)
        lg.rect(x0, 30, x0 + 4, y1 - 2)
        lg.rows({y1 - 1: (x0, x0 + 5), y1: (x0, x0 + 5)})
        lg.shade_side('l', 1, furd)
        lg.outline()
        lg.set(x0 + 2, 31, furl)
        lg.set(x0 + 2, 32, furl)
        lg.set(x0 + 2, y1, furd)
        lg.set(x0 + 4, y1, furd)
        S.add(lg)

    ch = Layer(fur, line)
    ch.rows({18: (26, 33), 19: (25, 34), 20: (24, 35), 21: (24, 35), 22: (24, 35),
             23: (24, 35), 24: (24, 35), 25: (24, 34), 26: (25, 34), 27: (25, 34),
             28: (26, 34), 29: (26, 33), 30: (27, 33), 31: (28, 32)})
    ch.outline(skip='t')
    for x, y in ((31, 23), (32, 24), (32, 25), (33, 26), (31, 24)):
        ch.set(x, y, furl)
    S.add(ch)

    # coleira vermelha com plaquinha dourada
    col = Layer(rgb('#D7352E'), rgb('#8E1C18'))
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
    hd = Layer(fur, line)
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
    ear = Layer(fur, line)
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


def lupin():
    """Vira-lata pequeno: preto, pelo duro, barba e bochechas caramelo,
    sobrancelhas de velhinho e orelhas com a pontinha dobrada."""
    S = Sprite(38, 34)
    fur, furd, furl = rgb('#25242A'), rgb('#121115'), rgb('#403E4A')
    tan, tand, tanl = rgb('#7C4B2A'), rgb('#55321B'), rgb('#A66C40')
    line = rgb('#070708')

    tl = Layer(fur, line)
    tl.rows({17: (5, 6), 18: (4, 7), 19: (4, 7), 20: (5, 8), 21: (5, 9), 22: (6, 10)})
    _tufts(tl, 1, line, 3)
    tl.outline()
    S.add(tl)

    bd = Layer(fur, line)
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

    hp = Layer(fur, line)
    hp.rows({27: (8, 14), 28: (7, 15), 29: (7, 15)})
    hp.outline()
    S.add(hp)

    for x0, y1 in ((17, 30), (21, 31)):
        lg = Layer(fur, line)
        lg.rect(x0, 22, x0 + 2, y1 - 2)
        lg.rows({y1 - 1: (x0, x0 + 3), y1: (x0, x0 + 3)})
        lg.outline()
        lg.set(x0 + 1, 24, furl)
        S.add(lg)

    ch = Layer(fur, line)
    ch.rows({15: (19, 25), 16: (18, 26), 17: (18, 26), 18: (18, 26), 19: (18, 26),
             20: (19, 26), 21: (19, 25), 22: (20, 25)})
    ch.outline(skip='t')
    _tufts(ch, 3, line)
    for x, y in ((23, 18), (24, 19), (22, 20), (23, 21)):
        ch.set(x, y, furl)
    S.add(ch)

    # cabeça quadradinha de terrier
    hd = Layer(fur, line)
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
    mz = Layer(fur, line)
    mz.rows({8: (27, 31), 9: (25, 33), 10: (24, 34), 11: (24, 34), 12: (23, 33)})
    mz.outline(skip='lt')
    S.add(mz)
    br = Layer(tan, line)
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
    near = Layer(fur, line)
    near.rows({1: (15, 17), 2: (14, 18), 3: (12, 18), 4: (11, 17), 5: (10, 15), 6: (10, 13)})
    near.outline()
    near.set(14, 3, furl)
    near.set(13, 4, furd)
    S.add(near)
    far = Layer(fur, line)
    far.rows({0: (22, 25), 1: (22, 27), 2: (23, 28), 3: (25, 29), 4: (27, 29)})
    far.outline()
    far.set(24, 1, furl)
    far.set(26, 2, furd)
    S.add(far)
    return S.image()
