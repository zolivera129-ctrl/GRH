"""Vida no escritório (fase 3 do manual): a pose-base à mesa, com os
antebraços para a frente e as mãos no tampo, e o que se anima em cima dela.

Onde ficam as mãos. Pela planta, quem senta olhando +B (Guilherme, Saldanha,
Caio e a estação flexível) tem a mesa no tile seguinte, em +B. No sprite sem
espelhar, a borda do tampo mais perto do personagem passa por (20, 58) e
sobe meio pixel a cada pixel para a direita (a mesa tem 24 px e está 16 px
mais perto da câmera). No balcão da recepção, com 34 px, a borda passa por
(20, 48). As mãos pousam logo depois dessa borda. As coordenadas do manual
(§4, mãos em (28, 44) e (19, 43)) eram ponto de partida e só batem com o
balcão.

Por que os antebraços também saem numa camada à parte. A mesa fica mais
perto da câmera que a cadeira, então o jogo desenha a mesa depois do
personagem, e ela cobriria as mãos. A camada "tampo" traz só antebraços e
mãos, nos mesmos pixels do quadro, para o jogo colar depois da mesa (manual
§1.1: braços e mãos que passam sobre o tampo).

Coordenadas: as do quadro final (40 × 70, âncora em (20, anim.PE)).
"""
import math
from collections import Counter

import anim
import chars
import costas
from px import Layer, mix

# a borda do tampo: y da borda em x = 20, para cada móvel
BORDA = {'mesa': 58, 'balcao': 48}
# quem senta em quê: só a Vivi trabalha no balcão
TAMPO = {'vivi': 'balcao'}


def borda(x, tampo):
    return BORDA[tampo] - (x - 20) / 2


# ------------------------------------------------------------ grupos
def regra_sentado(caixa):
    """Grupos de um humano sentado, de frente: pernas (quadril, coxas,
    canelas e sapatos), os dois braços, a cabeça (tudo o que começa acima
    do pescoço: cabeça, cabelo, rosto, barba, argolas) e o corpo."""
    x0, y0, x1, y1 = caixa
    d = chars.SIT_DY
    if y1 >= 55 or (y1 == 51 and x1 - x0 >= 15):
        return 'pernas'
    g = anim.regra_humano(caixa)
    if g.startswith('braco'):
        return g
    if y0 < 22 + d:
        return 'cabeca'
    return 'corpo'


def gravar_sentado(fn):
    return anim.agrupar(anim.gravar(fn, 'sentado'), regra_sentado)


# ------------------------------------------------------------ paleta do braço
def _cores(pts):
    """base, sombra e contorno de uma camada com sombra de 1 px e contorno."""
    base = Counter(pts.values()).most_common(1)[0][0]
    topo = min(y for _, y in pts)
    linha = pts[min((p for p in pts if p[1] == topo), key=lambda p: p[0])]
    meio = sorted({y for _, y in pts})[len({y for _, y in pts}) // 2]
    xs = sorted(x for x, y in pts if y == meio)
    sombra_e = pts[(xs[1], meio)]
    sombra_d = pts[(xs[-2], meio)]
    sombra = sombra_e if sombra_e != base else sombra_d
    return base, sombra, linha


def braco_de_frente(F, grupo):
    """Lê o braço do desenho de frente: a manga (cores, onde termina, a cor
    do punho, se houver) e a pele (cores e as faixas do pulso: relógio,
    pulseira, munhequeira)."""
    ops = [op for op in F.ops if op[2] == grupo]
    camadas = [op for op in ops if op[0] == 'camada']
    camadas.sort(key=lambda op: min(y for _, y in op[1]))
    manga, pele = camadas[0], camadas[-1]
    i_manga, i_pele = manga[3], pele[3]
    pts_manga, pts_pele = dict(manga[1]), dict(pele[1])
    for op in ops:                      # pixels soltos em cima de cada camada
        if op[0] == 'pixel':
            (p, c), = op[1].items()
            if op[3] == i_manga:
                pts_manga[p] = c
            elif op[3] == i_pele:
                pts_pele[p] = c
    mb, ms, ml = _cores(manga[1])
    pb, ps, pl = _cores(pele[1])
    fim = max(y for _, y in manga[1])
    # punho: a cor que não é da manga nas linhas de baixo
    # (só faixa de verdade: os botões dourados de punho, 1 ou 2 px, ficam de fora)
    punho = Counter(c for (x, y), c in pts_manga.items() if y >= fim - 2 and c not in (mb, ms, ml))
    punho = punho.most_common(1)[0] if punho else None
    punho = punho[0] if punho and punho[1] >= 3 else None
    # faixas do pulso: linhas da pele com cor que não é de pele
    faixas = {}
    topo_pele = min(y for _, y in pele[1])
    for (x, y), c in pts_pele.items():
        if c not in (pb, ps, pl):
            faixas.setdefault(y - topo_pele, Counter())[c] += 1
    faixas = {k: v.most_common(1)[0][0] for k, v in faixas.items()}
    return {'manga': (mb, ms, ml), 'pele': (pb, ps, pl), 'fim_manga': fim,
            'topo_manga': min(y for _, y in manga[1]), 'fundo_pele': max(y for _, y in pele[1]),
            'punho': punho, 'faixas': faixas,
            'largura_pele': len({x for x, _ in pele[1]})}


# ------------------------------------------------------------ desenho
def capsula(p0, p1, r):
    """Pontos inteiros a até r do segmento p0-p1 (centro do pixel)."""
    (x0, y0), (x1, y1) = p0, p1
    pts = set()
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy or 1e-9
    for y in range(math.floor(min(y0, y1) - r) - 1, math.ceil(max(y0, y1) + r) + 2):
        for x in range(math.floor(min(x0, x1) - r) - 1, math.ceil(max(x0, x1) + r) + 2):
            t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
            px_, py_ = x0 + t * dx, y0 + t * dy
            if (x - px_) ** 2 + (y - py_) ** 2 <= r * r:
                pts.add((x, y))
    return pts


def _caminho(pontos):
    """Comprimento de cada trecho de uma linha poligonal."""
    return [math.dist(a, b) for a, b in zip(pontos, pontos[1:])]


def _ponto(pontos, s):
    """O ponto a s px do começo da linha poligonal."""
    for a, b in zip(pontos, pontos[1:]):
        L = math.dist(a, b)
        if s <= L:
            t = s / L if L else 0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        s -= L
    return pontos[-1]


def _trecho(pontos, s0, s1):
    """Os pontos da linha poligonal entre s0 e s1 px do começo."""
    out = [_ponto(pontos, s0)]
    acc = 0
    for a, b in zip(pontos, pontos[1:]):
        acc += math.dist(a, b)
        if s0 < acc < s1:
            out.append(b)
    out.append(_ponto(pontos, s1))
    return out


def _engrossar(pontos, r):
    pts = set()
    for a, b in zip(pontos, pontos[1:]):
        pts |= capsula(a, b, r)
    return pts


def braco_dobrado(info, ombro, cotovelo, pulso, mao, lado_sombra):
    """O braço da pose da mesa, em camadas (manga de cima, antebraço, mão),
    cada uma com o seu grupo. A manga cobre o mesmo comprimento que cobre no
    braço solto do desenho de frente; o resto é pele. ombro, cotovelo,
    pulso e mao são pontos do quadro final; devolve [(pts, parte)]."""
    caminho = [ombro, cotovelo, pulso]
    total = sum(_caminho(caminho))
    # no braço solto, a manga vai do ombro até fim_manga e a pele até a
    # ponta da mão; aqui a manga cobre a mesma fração do braço
    braco_solto = info['fundo_pele'] - info['topo_manga']
    frac_manga = (info['fim_manga'] - info['topo_manga'] + 1) / braco_solto
    s_manga = min(total, frac_manga * (total + 3))
    mb, ms, ml = info['manga']
    pb, ps, pl = info['pele']
    s_cot = math.dist(ombro, cotovelo)

    out = []
    # manga: em cima até o cotovelo (ou onde ela termina) e, se for comprida,
    # um pedaço do antebraço
    manga_cima = _engrossar(_trecho(caminho, 0, min(s_manga, s_cot)), 3.4)
    L = Layer(mb, ml)
    for p in manga_cima:
        L.set(*p)
    if s_manga > s_cot:
        manga_baixo = _engrossar(_trecho(caminho, s_cot, s_manga), 2.6)
        Lb = Layer(mb, ml)
        for p in manga_baixo:
            Lb.set(*p)
    else:
        Lb = None
    # pele: do fim da manga até o pulso
    r_pele = 2.05
    pele = _engrossar(_trecho(caminho, min(s_manga, total), total), r_pele)
    P = Layer(pb, pl)
    for p in pele:
        P.set(*p)
    # a mão pousada no tampo: dorso claro em cima (a luz vem de cima e da
    # esquerda), dedos para a frente, contorno só nos lados e embaixo
    hx, hy = round(mao[0]), round(mao[1])
    H = Layer(pb, pl)
    H.rows({hy - 1: (hx - 2, hx + 1), hy: (hx - 2, hx + 2), hy + 1: (hx - 2, hx + 3), hy + 2: (hx - 1, hx + 3)})

    # faixas do pulso (relógio, pulseira, munhequeira) logo antes da mão,
    # com o mesmo espaçamento que têm no braço solto
    if info['faixas']:
        ux, uy = pulso[0] - cotovelo[0], pulso[1] - cotovelo[1]
        Lu = math.hypot(ux, uy)
        ux, uy = ux / Lu, uy / Lu
        ultima = max(info['faixas'])
        for r, cor in info['faixas'].items():
            alvo = Lu - 3.0 - (ultima - r)
            for p in P.px:
                s = (p[0] - cotovelo[0]) * ux + (p[1] - cotovelo[1]) * uy
                if abs(s - alvo) <= 0.55:
                    P.px[p] = cor

    # a pele vem antes das mangas, que cobrem a ponta redonda dela
    for camada, parte, sombra in ((P, 'antebraco', ps), (L, 'cima', ms), (Lb, 'antebraco', ms), (H, 'mao', ps)):
        if camada is None:
            continue
        cor_det = {p: c for p, c in camada.px.items() if c not in (camada.base,)}
        camada.px = {p: camada.base for p in camada.px}
        camada.shade_side(lado_sombra, 1, sombra)
        camada.px.update(cor_det)
        if parte == 'mao':
            camada.outline(skip='t')
            luz = mix(pb, (255, 255, 255), 0.18)
            for x in range(hx - 1, hx + 2):
                if (x, hy - 1) in camada.px:
                    camada.px[(x, hy - 1)] = luz
            for x in range(hx, hx + 3):
                if (x, hy + 2) in camada.px and camada.px[(x, hy + 2)] != pl:
                    camada.px[(x, hy + 2)] = ps
        else:
            camada.outline()
        out.append((camada.px, parte))
    # o punho, na ponta da manga
    if info['punho'] and s_manga < total:
        fim = _ponto(caminho, s_manga)
        cor = info['punho']
        for camada_px, parte in out:
            if parte in ('antebraco', 'cima'):
                for p in list(camada_px):
                    if math.dist(p, fim) <= 2.2 and camada_px[p] not in (ml, pl):
                        camada_px[p] = cor
    return out


# ------------------------------------------------------------ a pose da mesa
def maos(tampo):
    """Os pontos da pose da mesa (quadro final): ombros, cotovelos, pulsos e
    mãos dos dois braços, para a mesa ou para o balcão."""
    sobe = BORDA['mesa'] - BORDA[tampo]
    frente = {'ombro': (10.5, 37.5), 'cotovelo': (11.5, 46.0 - sobe * 0.2),
              'pulso': (24.0, 54.0 - sobe), 'mao': (27.0, 55.5 - sobe)}
    tras = {'ombro': (28.5, 37.5), 'cotovelo': (29.5, 44.5 - sobe * 0.2),
            'pulso': (31.5, 50.5 - sobe), 'mao': (34.0, 52.0 - sobe)}
    return frente, tras


def pose_mesa(cid, tampo=None):
    """O sentado de frente com as mãos no tampo, como lista de operações
    agrupadas no formato do anim.montar, já com a folga da âncora aplicada
    (montar com desce=0). Grupos: pernas, corpo, cabeca, braco_frente,
    antebraco_frente, mao_frente e os três de trás."""
    tampo = tampo or TAMPO.get(cid, 'mesa')
    fn = costas.HUMANOS[cid][0]
    n = anim.folga(fn)
    ops = [[k, costas.mover(pts, 0, n), g, d] for k, pts, g, d in gravar_sentado(fn)]
    F2 = costas.Frente.__new__(costas.Frente)
    F2.ops = ops
    frente, tras = maos(tampo)
    novos = {}
    for grupo, pontos, sombra in (('braco_frente', frente, 'l'), ('braco_tras', tras, 'r')):
        info = braco_de_frente(F2, grupo)
        lado = grupo.split('_')[1]
        partes = braco_dobrado(info, pontos['ombro'], pontos['cotovelo'], pontos['pulso'], pontos['mao'], sombra)
        novos[grupo] = [['camada', pts, {'cima': f'braco_{lado}', 'antebraco': f'antebraco_{lado}',
                                         'mao': f'mao_{lado}'}[parte], None] for pts, parte in partes]
    # a parte de cima de cada braço entra onde estava o braço solto; o
    # antebraço e a mão de trás vão logo depois das pernas (as mãos estão no
    # tampo, acima do colo), e o tronco, desenhado depois, esconde o cotovelo
    out = []
    feitos = set()
    ult_perna = max(i for i, op in enumerate(ops) if op[2] == 'pernas')
    for i, op in enumerate(ops):
        g = op[2]
        if g in novos:
            if g not in feitos:
                if g == 'braco_tras':
                    out.extend(o for o in novos[g] if o[2] == 'braco_tras')
                else:
                    out.extend(novos[g])
                feitos.add(g)
            continue
        out.append(op)
        if i == ult_perna:
            out.extend(o for o in novos['braco_tras'] if o[2] != 'braco_tras')
    return out


# ------------------------------------------------------------ conferência
TAMPO_GRUPOS = ('antebraco_frente', 'antebraco_tras', 'mao_frente', 'mao_tras')


def so_tampo(ops, mov=None):
    """Só antebraços e mãos, como aparecem no quadro: a camada que o jogo
    cola depois da mesa."""
    return anim.montar(ops, mov or {}, so_grupos=TAMPO_GRUPOS)


def camadas_da_estacao(cid, W=200, H=130, ax=100, ay=84):
    """A estação de trabalho de cid em camadas, como o jogo monta, lidas do
    layout e do manifesto: fundo (piso e cadeira), mesa e objetos sobre ela.
    O personagem vai entre o fundo e a mesa, com o pé em (ax, ay); a camada
    do tampo vai entre a mesa e os objetos. Quem não tem estação própria usa
    a estação flexível; a Vivi, o balcão da recepção.
    Devolve (fundo, mesa, teclado, objetos, espelhar); o teclado vai entre
    a mesa e a camada do tampo."""
    import json
    import os
    from PIL import Image
    raiz = os.path.join(os.path.dirname(__file__), '..')
    man = json.load(open(os.path.join(raiz, 'assets', 'manifest.json')))
    lay = json.load(open(os.path.join(raiz, '..', 'docs', 'FinancyApp_Layout_12x10_v1.json')))
    nome = {'sr_pra_ontem': 'sr. pra ontem'}.get(cid, cid)
    cadeiras = [p for p in lay['pecas_piso'] if p['modelo'] == 'cadeira' and p.get('zona') != 'reuniao']
    cad = next((p for p in cadeiras if (p.get('ocupante_padrao') or '').lower() == nome), None)
    cad = cad or next(p for p in cadeiras if p.get('zona') == 'flex')
    olha = cad['olha_para']
    espelhar = olha in ('+B', '-A')
    a, b = cad['tile']
    da, db = {'+A': (1, 0), '+B': (0, 1)}[olha]
    mesa = next(p for p in lay['pecas_piso'] if p['modelo'] in ('mesa_trabalho', 'mesa_fundador', 'balcao_recepcao')
                and p['tile'][0] <= a + da < p['tile'][0] + p['base'][0]
                and p['tile'][1] <= b + db < p['tile'][1] + p['base'][1])
    fundo, frente, teclado, objs = (Image.new('RGBA', (W, H), (0, 0, 0, 0)) for _ in range(4))

    def P(s, t, z=0):
        return ax + 32 * (s - t) - 32 * (a + 0.5 - b - 0.5), ay + 16 * (s + t) - 16 * (a + b + 1) - z

    def colar(tela, img, anc, x, y):
        tela.alpha_composite(img, (round(x - anc[0]), round(y - anc[1])))

    def arq(rel):
        return Image.open(os.path.join(raiz, 'assets', rel)).convert('RGBA')
    piso = [arq(f'piso/piso_madeira__{i}.png') for i in (1, 2, 3)]
    for s in range(a - 3, a + 4):
        for t in range(b - 3, b + 4):
            colar(fundo, piso[(s * 7 + t * 3) % 3], (32, 32), *P(s + 1, t + 1))
    direcao = {'+A': 'frente-dir', '+B': 'frente-esq'}[olha]
    colar(fundo, arq(f'moveis/cadeira__{direcao}.png'), man['cadeira']['ancora'], *P(a + 1, b + 1))
    e = man[mesa['modelo']]
    (ma, mb), (mda, mdb) = mesa['tile'], mesa['base']
    mx, my = P(ma + mda, mb + mdb)
    colar(frente, arq(f"moveis/{mesa['modelo']}.png"), e['ancora'], mx, my)
    for obj in mesa.get('objetos', []):
        o = man[obj]
        nomeobj = f"objetos/{obj}__{o['estados'][0]}.png" if o.get('estados') else f'objetos/{obj}.png'
        colar(objs, arq(nomeobj), o['ancora'], mx + e['encaixes'][obj][0], my + e['encaixes'][obj][1])
    t = man['teclado']
    dx, dy = t['no_personagem'][TAMPO.get(cid, 'mesa')]
    colar(teclado, arq(f'objetos/teclado__{direcao}.png'), t['ancora'], ax + dx, ay + dy)
    return fundo, frente, teclado, objs, espelhar


def estacao(cid, quadro=None, tampo_por_cima=True, k=1):
    """A estação montada (conferência): fundo, personagem, mesa, camada do
    tampo e objetos."""
    from PIL import Image
    fundo, mesa, teclado, objs, esp = camadas_da_estacao(cid)
    ops = pose_mesa(cid)
    corpo = quadro or anim.montar(ops, {})
    cima = so_tampo(ops)
    tela = Image.new('RGBA', fundo.size, (24, 30, 52, 255))
    tela.alpha_composite(fundo)
    for img, depois_da_mesa in ((corpo, False), (cima, True)):
        if depois_da_mesa:
            tela.alpha_composite(mesa)
            tela.alpha_composite(teclado)
            if not tampo_por_cima:
                break
        if esp:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        tela.alpha_composite(img, (100 - (40 - 20 if esp else 20), 84 - anim.PE))
    tela.alpha_composite(objs)
    if k > 1:
        tela = tela.resize((tela.width * k, tela.height * k), Image.NEAREST)
    return tela


def anim_ancora():
    return (20, anim.PE)


# ------------------------------------------------------------ as animações
# Tabelas 4.1 a 4.5 do manual, sobre a pose da mesa. Grupos que mexem:
# cabeca, corpo (tronco e pescoço), braco_* (a parte de cima do braço),
# antebraco_* e mao_*. As pernas e o quadril nunca mexem.
OMBROS = ('corpo', 'braco_frente', 'braco_tras')
# os ombros mexem, a barra da roupa e o quadril não: o tronco encolhe ou
# inclina acima desta linha
CINTURA = anim.PE - 18


def _junto(grupos, **m):
    return {g: dict(m, **({'acima_de': CINTURA} if g == 'corpo' else {})) for g in grupos}


CICLOS = {
    # 4.1: respiração. No Q2 a cabeça e os ombros descem 1 px; as mãos
    # ficam apoiadas no tampo (a mesa segura).
    'sentado_frente_idle': [
        {},
        _junto(('cabeca',) + OMBROS, dy=1),
    ],
    # 4.2: teclando. Só os punhos alternam 1 px; cabeça, ombros e tronco
    # ficam parados (com a cabeça e os ombros mexendo, como no manual,
    # parecia que a pessoa dançava). Q4 volta ao apoio.
    'teclando_frente': [
        {},
        {'mao_frente': {'dy': -1}, 'mao_tras': {'dy': 1}},
        {'mao_frente': {'dy': 1}, 'mao_tras': {'dy': -1}},
        {},
    ],
    # 4.3: assentindo para a tela (uma vez).
    'assentindo_para_tela_frente': [
        {},
        {'cabeca': {'dx': 1, 'dy': 1}},
        {'cabeca': {'dx': 1, 'dy': 2}, **_junto(OMBROS, dy=1)},
        {},
    ],
    # 4.5: olhando para o lado (uma vez). As pupilas andam 1 px no Q2 e no
    # Q3 (ver olhos_de_lado).
    'olhando_para_o_lado_frente': [
        {},
        {'cabeca': {'dx': 1}},
        {'cabeca': {'dx': 2}, **_junto(OMBROS, dx=1)},
        {},
    ],
}
# quadros com as pupilas de lado
PUPILAS = {'olhando_para_o_lado_frente': (1, 2)}
# quadros por segundo e se repete (manual §8.1)
TEMPO = {'sentado_frente_idle': (2, True), 'teclando_frente': (8, True),
         'assentindo_para_tela_frente': (6, False), 'olhando_para_o_lado_frente': (5, False)}


def _olhos(cid):
    """As posições das pupilas no quadro final da pose sentada (o desenho
    de frente põe as pupilas em x 19 e 24, linhas 16 e 17)."""
    n = anim.folga(costas.HUMANOS[cid][0]) + chars.SIT_DY
    return [(x, y + n) for x in (19, 24) for y in (16, 17)], n


def olhos_de_lado(cid, ops):
    """As mesmas operações com as pupilas 1 px para a frente: cada pupila
    anda para a direita, o branco que estava atrás dela vai para onde ela
    estava e o branco da frente (quem tem) some. Óculos e cílios desenhados
    depois continuam por cima."""
    pupilas, n = _olhos(cid)
    idx = [i for i, op in enumerate(ops) if op[0] == 'pixel' and op[2] == 'cabeca'
           and next(iter(op[1])) in pupilas]
    perto = {j for i in idx for j in range(i - 4, i + 5)}
    out = []
    for i, op in enumerate(ops):
        if op[0] == 'pixel' and op[2] == 'cabeca':
            (p, c), = op[1].items()
            if i in idx:
                out.append([op[0], {(p[0] + 1, p[1]): c}, op[2], op[3]])
                continue
            if i in perto:
                atras = (p[0] + 1, p[1]) in pupilas
                frente = (p[0] - 1, p[1]) in pupilas
                if atras:
                    out.append([op[0], {(p[0] + 1, p[1]): c}, op[2], op[3]])
                    continue
                if frente:
                    continue
        out.append(op)
    return out


_POSE = {}


def _pose(cid):
    """pose_mesa e a versão com as pupilas de lado, guardadas por cid (as
    listas não são alteradas por quem lê)."""
    if cid not in _POSE:
        ops = pose_mesa(cid)
        _POSE[cid] = (ops, olhos_de_lado(cid, ops))
    return _POSE[cid]


def quadros(cid, nome, so_tampo_=False):
    ops, lado = _pose(cid)
    out = []
    for k, mov in enumerate(CICLOS[nome]):
        base = lado if k in PUPILAS.get(nome, ()) else ops
        out.append(anim.montar(base, mov, so_grupos=TAMPO_GRUPOS if so_tampo_ else None))
    return out


def rosto(nome):
    """Onde o rosto está em cada quadro, em relação ao parado de frente:
    a sobreposição de olhos e boca vai nesse deslocamento."""
    out = []
    for mov in CICLOS[nome]:
        m = mov.get('cabeca', {})
        out.append([m.get('dx', 0), chars.SIT_DY + m.get('dy', 0)])
    return out


def maos_marcadas(cid, nome):
    """Os pontos das duas mãos em cada quadro (frente, trás), para o jogo
    colar objetos na mão."""
    frente, tras = maos(TAMPO.get(cid, 'mesa'))
    out = []
    for mov in CICLOS[nome]:
        q = []
        for lado, pts in (('frente', frente), ('tras', tras)):
            m = mov.get(f'mao_{lado}', {})
            q.append([round(pts['mao'][0]) + m.get('dx', 0), round(pts['mao'][1]) + m.get('dy', 0)])
        out.append(q)
    return out


# ------------------------------------------------------------ rosto
# Piscar e falar são sobreposições (manual §1.1 e §4.4, §4.6): só os pixels
# que mudam, na tela do parado de frente. O jogo cola a sobreposição em cima
# do quadro do corpo, deslocada pelo "rosto" daquele quadro.
ESCURO = rgb_ = None
BOCA_ESCURA = (0x3A, 0x1A, 0x12)
# boca de cada um: (x0, x1, linha, cor do lábio de baixo), em coordenadas
# do desenho de frente. A boca abre para baixo a partir da linha: no Q2 a
# linha vira boca aberta e o lábio desce 1 px; no Q3, 2 px.
BOCA = {
    'guilherme': (23, 24, 22, '#B4584A'), 'gabriel': (23, 24, 22, '#B4655A'),
    'saldanha': (23, 25, 22, '#8A5A48'), 'caio': (22, 25, 22, '#B4584A'),
    'vivi': (23, 24, 22, '#8E4434'), 'nina': (23, 24, 22, '#B4655A'),
    'otto': (23, 24, 22, '#8A4A3E'), 'sr_pra_ontem': (23, 25, 23, '#8A3A2E'),
    'iris': (23, 24, 22, '#9C4E48'), 'joana': (23, 24, 22, '#7A2430'),
    'malu': (23, 24, 22, '#B5605A'), 'duda': (23, 24, 22, '#8A4A3E'),
}
CILIOS = {(0x1A, 0x0E, 0x08), (0x14, 0x0A, 0x06), (0x0E, 0x08, 0x05)}


def _parado(cid):
    fn = costas.HUMANOS[cid][0]
    n = anim.folga(fn)
    ops = anim.agrupar(anim.gravar(fn, 'parado'), anim.regra_humano)
    return [[k, costas.mover(p, 0, n), g, d] for k, p, g, d in ops], n


def _diferenca(base, nova):
    from PIL import Image
    out = Image.new('RGBA', base.size, (0, 0, 0, 0))
    for y in range(base.height):
        for x in range(base.width):
            a, b = base.getpixel((x, y)), nova.getpixel((x, y))
            if a != b:
                out.putpixel((x, y), b)
    return out


def piscando(cid):
    """3 quadros: aberto, fechado, aberto (12 FPS, uma vez). Fechado: o olho
    (pupila, branco e cílio) some e fica um traço de 1 px na linha de baixo
    do olho; a armação dos óculos, desenhada depois, continua por cima."""
    from PIL import Image
    ops, n = _parado(cid)
    pupilas = {(x, y + n) for x in (19, 24) for y in (16, 17)}
    cor_pupila = Counter(next(iter(op[1].values())) for op in ops
                         if op[0] == 'pixel' and next(iter(op[1])) in pupilas).most_common(1)[0][0]
    olho = {cor_pupila, (255, 255, 255)} | CILIOS
    linhas_olho = range(15 + n, 18 + n)
    fechado, posto = [], False
    for op in ops:
        if op[0] == 'pixel':
            (p, c), = op[1].items()
            perto = any(abs(p[0] - x) <= 2 for x in (19, 24))
            if p[1] in linhas_olho and perto and (c in olho or p in pupilas or
                                                   (p[0] + 1, p[1]) in pupilas):
                if not posto:
                    for x0 in (18, 23):
                        fechado.append(['pixel', {(x0, 17 + n): cor_pupila, (x0 + 1, 17 + n): cor_pupila},
                                        op[2], op[3]])
                    posto = True
                continue
        fechado.append(op)
    aberto = anim.montar(ops, {})
    vazio = Image.new('RGBA', aberto.size, (0, 0, 0, 0))
    return [vazio, _diferenca(aberto, anim.montar(fechado, {})), vazio.copy()]


def _dentes(img, cid, n):
    """Os dentes da boca de repouso: pixels quase brancos na área da boca."""
    x0, x1, L, _ = BOCA[cid]
    pts = []
    for y in range(L - 2 + n, L + 1 + n):
        for x in range(x0 - 2, x1 + 3):
            r, g, b, a = img.getpixel((x, y))
            if a and min(r, g, b) >= 235:
                pts.append((x, y))
    return pts


def falando(cid):
    """4 quadros: boca de repouso, abertura de 1 px, de 2 px (com o fundo
    escuro) e de 1 px de novo (8 FPS, em loop enquanto fala). Quem mostra os
    dentes na boca de repouso: no Q2 eles diminuem (fica a metade do meio) e
    no Q3 somem, para a boca abrir de verdade."""
    from PIL import Image
    from px import rgb
    ops, n = _parado(cid)
    x0, x1, L, labio = BOCA[cid]
    labio = rgb(labio)
    aberto = anim.montar(ops, {})
    dentes = _dentes(aberto, cid, n)

    def abre(px_, sobra_dentes):
        pts = {}
        if dentes:
            xs = sorted({x for x, _ in dentes})
            meio = len(xs) / 2
            fica = set(xs[int(meio - sobra_dentes / 2):int(meio + sobra_dentes / 2)]) if sobra_dentes else set()
            for (x, y) in dentes:
                if x not in fica:
                    pts[(x, y)] = BOCA_ESCURA
        for x in range(x0, x1 + 1):
            for k in range(px_):
                pts[(x, L + k + n)] = BOCA_ESCURA
            pts[(x, L + px_ + n)] = labio
        return _diferenca(aberto, anim.montar(ops + [['camada', pts, 'corpo', None]], {}))
    vazio = Image.new('RGBA', aberto.size, (0, 0, 0, 0))
    largura = len({x for x, _ in dentes})
    um = abre(1, max(1, largura // 2))
    return [vazio, um, abre(2, 0), um.copy()]
