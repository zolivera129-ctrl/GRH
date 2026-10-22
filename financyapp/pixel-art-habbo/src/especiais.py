"""Ações especiais (fase 5 do manual, §5): gestos de um personagem só, com
adereço na mão.

- Gabriel: deixando_envelope_no_malote (2 quadros, 6 FPS, uma vez). O
  envelope é um objeto à parte que o jogo cola na mão (marcador
  "envelope" em cada quadro, também na caminhada) e solta no Q2, quando o
  malote passa a mostrar o envelope na abertura. Pela planta, ele deixa o
  envelope de costas para a câmera (a abertura olha para +A e os pontos de
  uso ficam em +A e +B do malote), então além da de frente, que o manual
  pede, há a variante de costas (ver NOTAS_DE_IMPLEMENTACAO.md).
- Saldanha: digitando_sentado (à mesa, com o tablet deitado no lugar do
  teclado), alerta (mão na testa), apresentando_quadro (apontando) e
  comemorando_tablet (tablet erguido acima da cabeça).
- Caio: mostrando_tablet, a pose do desenho original com a tela em branco
  para o jogo colar o selo (verde, amarelo ou vermelho).
- Vivi: tirando_foto, celular nas duas mãos e o flash no Q2.

Tudo sai do desenho original gravado camada por camada (anim.Gravador): o
corpo, a roupa e o rosto são os mesmos pixels; só os braços que fazem o
gesto e o adereço são desenhados aqui, nas cores do próprio personagem.

Coordenadas: as do quadro final (40 × 70, sola na linha anim.PE).

Lado do gesto. O manual põe as mãos do gesto à direita da tela (x de 32 a
38), que é para onde o personagem olha. No nosso desenho de frente, o braço
desse lado é o de trás (o da frente fica à esquerda, perto da câmera);
estender o da frente até lá faria o braço cruzar o peito. Então quem
estende, aponta ou carrega é o braço da direita da tela: o de trás, de
frente, e o da frente, de costas (que é o da direita de costas). Os pontos
do manual valem; os nomes dos braços, não.
"""
import math

from PIL import Image

import anim
import chars
import costas
import escritorio
from px import Layer, mix, mul, rgb


# ------------------------------------------------------------ ferramentas
def _r(v):
    return int(math.floor(v + 0.5))


def banda(p0, p1, w):
    """Uma faixa de largura w de p0 a p1: em pé (mais alta que larga) as
    linhas são horizontais; deitada, as colunas são verticais. Assim o
    braço tem sempre w px de grossura, como o braço solto do desenho."""
    (x0, y0), (x1, y1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    em_pe = abs(y1 - y0) >= abs(x1 - x0)
    pts = set()
    for i in range(n + 1):
        x = _r(x0 + (x1 - x0) * i / n)
        y = _r(y0 + (y1 - y0) * i / n)
        for k in range(w):
            pts.add((x - w // 2 + k, y) if em_pe else (x, y - w // 2 + k))
    return pts


def caminho(pontos, w):
    pts = set()
    for a, b in zip(pontos, pontos[1:]):
        pts |= banda(a, b, w)
    return pts


def camada(pts, base, linha, sombra=None, lado='l'):
    """Uma camada pintada com sombra de 1 px de um lado e contorno."""
    L = Layer(base, linha)
    for p in pts:
        L.set(*p)
    if sombra:
        L.shade_side(lado, 1, sombra)
    L.outline()
    return L.px


def mao(cx, cy, larg=4, alt=4):
    """Bloco da mão centrado em (cx, cy), cantos arredondados."""
    x0, y0 = cx - larg // 2, cy - alt // 2
    pts = {(x, y) for x in range(x0, x0 + larg) for y in range(y0, y0 + alt)}
    for p in ((x0, y0), (x0 + larg - 1, y0 + alt - 1)):
        pts.discard(p)
    return pts


def parado(cid):
    """O parado de frente gravado, agrupado e descido até a âncora, e a pele."""
    ops, n = escritorio._parado(cid)
    return ops, n, escritorio.pele_do_rosto(ops, n, sentado=False)


def info_braco(ops, grupo, pele):
    F = costas.Frente.__new__(costas.Frente)
    F.ops = ops
    return escritorio.braco_de_frente(F, grupo, pele)


def trocar(ops, grupo, novas, depois_de=None):
    """Tira as operações do grupo e põe as novas no lugar da primeira delas
    (ou logo depois da operação de índice depois_de)."""
    out, posto = [], False
    for i, op in enumerate(ops):
        if op[2] == grupo:
            if not posto and depois_de is None:
                out.extend(novas)
                posto = True
            continue
        out.append(op)
        if depois_de is not None and i == depois_de:
            out.extend(novas)
    return out


def ultimo(ops, cond):
    return max(i for i, op in enumerate(ops) if cond(op))


def op(pts, grupo):
    return ['camada', dict(pts), grupo, None]


def _ao_longo(pontos, d):
    """O ponto a d px do começo de uma linha quebrada, e o índice do trecho."""
    for i, (a, b) in enumerate(zip(pontos, pontos[1:])):
        L = math.dist(a, b)
        if d <= L or i == len(pontos) - 2:
            t = min(1.0, d / L) if L else 0.0
            return (_r(a[0] + (b[0] - a[0]) * t), _r(a[1] + (b[1] - a[1]) * t)), i
        d -= L


def braco_estendido(info, pele, ombro, cotovelo, ponta, lado='r', faixa=True, larg_manga=6,
                    ombreira=None, manga_ate=None):
    """Um braço do ombro à mão, em duas camadas (manga e pele), nas cores
    do personagem. A manga cobre a mesma fração do braço que cobre no
    desenho original (no braço solto, do ombro à mão são uns 21 px); a pele
    vai até a mão; as faixas do pulso (relógio, pulseira) ficam no
    antebraço, logo antes da mão. ombreira: pontos da manga original que
    ficam (o alto do ombro), para a silhueta não mudar. manga_ate: até onde
    vai a manga, em px ao longo do braço (o padrão é a fração do original)."""
    sk, sks, skl, luz = pele
    mb, ms, ml = info['manga']
    comp_manga = info['fim_manga'] - info['topo_manga'] + 1
    pontos = [ombro, cotovelo, ponta]
    total = math.dist(ombro, cotovelo) + math.dist(cotovelo, ponta)
    frac = min(0.9, comp_manga / 21)
    fim_manga, i = _ao_longo(pontos, total * frac if manga_ate is None else manga_ate)
    resto = [fim_manga] + pontos[i + 1:]
    pele_pts = caminho(resto, 4) | mao(*ponta)
    P = camada(pele_pts, sk, skl, sks, lado)
    if faixa and info['faixas']:
        # as faixas na pele, 2 px antes da mão, atravessando o antebraço
        vx, vy = ponta[0] - cotovelo[0], ponta[1] - cotovelo[1]
        d = math.hypot(vx, vy) or 1
        ux, uy = vx / d, vy / d
        for k, cor in enumerate(info['faixas'][:2]):
            cx, cy = ponta[0] - ux * (3 + k), ponta[1] - uy * (3 + k)
            for s in (-1, 0, 1):
                q = (_r(cx - uy * s), _r(cy + ux * s))
                if q in P and P[q] != skl:
                    P[q] = cor
    manga_pts = caminho(pontos[:i + 1] + [fim_manga], larg_manga) | set(ombreira or ())
    M = camada(manga_pts, mb, ml, ms, lado)
    return M, P


def manga_original(ops, grupo):
    """A camada de manga do braço, com os pixels soltos que caíram nela
    (vinco, punho dobrado), como está no desenho."""
    camadas = [o for o in ops if o[2] == grupo and o[0] == 'camada']
    manga = min(camadas, key=lambda o: min(y for _, y in o[1]))
    pts = dict(manga[1])
    for o in ops:
        if o[0] == 'pixel' and o[3] == manga[3]:
            pts.update(o[1])
    return pts


def ombreira(ops, grupo, linhas=3):
    """O alto da manga original: as primeiras linhas da camada de manga do
    braço (a silhueta do ombro)."""
    manga = manga_original(ops, grupo)
    topo = min(y for _, y in manga)
    return {p for p in manga if p[1] < topo + linhas}


def antebraco(info, pele, cotovelo, ponta, lado='r', larg_mao=4, alt_mao=4):
    """Só a pele: do cotovelo (escondido embaixo da manga) até a mão, com as
    faixas do pulso antes da mão."""
    sk, sks, skl, luz = pele
    P = camada(banda(cotovelo, ponta, 4) | mao(*ponta, larg_mao, alt_mao), sk, skl, sks, lado)
    if info['faixas']:
        vx, vy = ponta[0] - cotovelo[0], ponta[1] - cotovelo[1]
        d = math.hypot(vx, vy) or 1
        ux, uy = vx / d, vy / d
        em_pe = abs(vy) >= abs(vx)
        for k, cor in enumerate(info['faixas'][:2]):
            cx, cy = ponta[0] - ux * (3 + k), ponta[1] - uy * (3 + k)
            for s in (-2, -1, 0, 1, 2):
                q = (_r(cx) + s, _r(cy)) if em_pe else (_r(cx), _r(cy) + s)
                if q in P and P[q] != skl:
                    P[q] = cor
    return P


# ------------------------------------------------------------ Gabriel
# manual §5.1: a mão do envelope em (36, 36) no Q1 e (38, 42) no Q2
GABRIEL = [
    # Q1: cabeça x+1; o braço da direita dobra e leva a mão à frente, com o
    # envelope; o braço de cima continua caindo do ombro, na manga original
    {'manga': (0, 0), 'cotovelo': (30, 40), 'mao': (36, 37), 'mov': {'cabeca': {'dx': 1}}},
    # Q2: cabeça y+1, tronco inclina 1 px; o braço vai à frente e a mão desce
    # até a abertura, onde solta o envelope
    {'manga': (1, 0), 'cotovelo': (32, 40), 'mao': (37, 42),
     'mov': {'cabeca': {'dx': 1, 'dy': 1}, 'corpo': {'dx': 1, 'acima_de': anim.PE - 21}}},
]
# de costas (olhando -B; espelhado, -A, que é como ele fica no malote da
# planta): o braço da direita, que de costas é o da frente, leva a mão à
# frente e para cima, até a abertura
GABRIEL_COSTAS = [
    {'manga': (0, 0), 'cotovelo': (29, 40), 'mao': (35, 36), 'mov': {'cabeca': {'dx': 1}}},
    {'manga': (1, -1), 'cotovelo': (31, 39), 'mao': (37, 38),
     'mov': {'cabeca': {'dx': 1, 'dy': 1}, 'corpo': {'dx': 1, 'acima_de': anim.PE - 21}}},
]


def _com_cabeca(ops, n):
    """Separa a cabeça (tudo o que começa acima do pescoço) do corpo, para
    ela mexer sozinha."""
    out = []
    for o in ops:
        if o[2] == 'corpo' and anim._caixa(o[1])[1] < 22 + n and o[0] == 'camada':
            out.append([o[0], o[1], 'cabeca', o[3]])
        elif o[0] == 'pixel' and o[2] == 'corpo' and next(iter(o[1]))[1] < 27 + n and o[3] is not None \
                and anim._caixa(ops[o[3]][1])[1] < 22 + n:
            out.append([o[0], o[1], 'cabeca', o[3]])
        else:
            out.append(o)
    return out


def gabriel_envelope():
    ops, n, pele = parado('gabriel')
    info = info_braco(ops, 'braco_tras', pele)
    manga = manga_original(ops, 'braco_tras')
    out = []
    for q in GABRIEL:
        P = antebraco(info, pele, q['cotovelo'], q['mao'])
        M = costas.mover(manga, *q['manga'])
        novo = trocar(ops, 'braco_tras', [op(P, 'braco_tras'), op(M, 'braco_tras')])
        out.append(anim.montar(_com_cabeca(novo, n), q['mov']))
    return out


def gabriel_envelope_costas():
    """A mesma entrega, de costas. De costas cada braço é uma camada só
    (manga e pele juntas, espelhadas do de frente); a manga é a parte de
    cima, até onde ia a manga no desenho de frente."""
    frente, n, pele = parado('gabriel')
    info = info_braco(frente, 'braco_frente', pele)        # o da direita, de costas
    ops = [[k, costas.mover(p, 0, n), g, d] for k, p, g, d in costas.ops('gabriel', 'parado')]
    braco = {}
    for o in ops:
        if o[2] == 'braco_frente':
            braco.update(o[1])
    manga = {p: c for p, c in braco.items() if p[1] <= info['fim_manga']}
    out = []
    for q in GABRIEL_COSTAS:
        P = antebraco(info, pele, q['cotovelo'], q['mao'])
        M = costas.mover(manga, *q['manga'])
        novo = trocar(ops, 'braco_frente', [op(P, 'braco_frente'), op(M, 'braco_frente')])
        out.append(anim.montar(_com_cabeca(novo, n), q['mov']))
    return out


def dedo(ponta, direcao, pele, n=2):
    """O indicador apontando: um traço de 2 px de grossura saindo da mão na
    direção dada, com contorno."""
    sk, sks, skl, _ = pele
    dx, dy = direcao
    d = math.hypot(dx, dy) or 1
    fim = (_r(ponta[0] + dx / d * (2 + n)), _r(ponta[1] + dy / d * (2 + n)))
    return camada(banda(ponta, fim, 3), sk, skl)


# ------------------------------------------------------------ Saldanha
# manual §5.3: a mão vai à testa, perto de (28, 18), no Q1; no Q2 a palma
# está na testa e o cotovelo anda 1 px. O braço da direita sobe com o
# cotovelo para fora; o antebraço e a mão passam na frente do rosto.
ALERTA = [
    {'cotovelo': (33, 30), 'mao': (29, 18),
     'mov': {'cabeca': {'dx': 1}}, 'rosto': 'preocupado'},
    {'cotovelo': (34, 29), 'mao': (28, 15),
     'mov': {'cabeca': {'dy': -1}}, 'rosto': 'alerta'},
]
# manual §5.4: o dedo em (36, 32) no Q1 e 2 px acima, (38, 28), no Q2; a
# cabeça vira 1 px para o quadro no Q1 e volta para o jogador no Q2
APRESENTANDO = [
    {'cotovelo': (30, 40), 'mao': (34, 34), 'dedo': (1, -1), 'mov': {'cabeca': {'dx': 1}}},
    {'cotovelo': (31, 39), 'mao': (36, 30), 'dedo': (1, -1), 'mov': {}},
]
# manual §5.5: os dois braços para cima, o tablet em x 14..30, y 2..9; no Q2
# o tablet sobe 1 px, os braços acompanham, a cabeça volta e o tronco sobe
COMEMORANDO = [
    {'tablet': 2, 'frente': ((10, 33), (8, 24), (15, 9)), 'tras': ((28, 33), (32, 24), (29, 9)),
     'mov': {'cabeca': {'dy': -1}}, 'rosto': None},
    {'tablet': 1, 'frente': ((10, 32), (8, 23), (15, 8)), 'tras': ((28, 32), (32, 23), (29, 8)),
     'mov': {'corpo': {'dy': -1, 'acima_de': anim.PE - 22}, 'cabeca': {'dy': -1}}, 'rosto': 'boca_aberta'},
]
TABLET = {'aro': rgb('#555A64'), 'prata': rgb('#C3C7CF'), 'prata_s': rgb('#A3A8B2'),
          'tela': rgb('#8FD0F4'), 'tela_s': rgb('#5FA8D8'), 'brilho': rgb('#E8F6FD')}


def tablet_erguido(topo, x0=14, x1=30, alt=8):
    """O tablet de pé, de frente para quem olha: aro escuro, borda prateada
    e a tela acesa com um reflexo na diagonal (sem selo: o selo é do Caio)."""
    T = TABLET
    L = Layer(T['prata'], T['aro'])
    L.rect(x0, topo, x1, topo + alt - 1)
    L.outline()
    for x in range(x0 + 2, x1 - 1):
        for y in range(topo + 2, topo + alt - 2):
            L.px[(x, y)] = T['tela']
    for y in range(topo + 2, topo + alt - 2):
        L.px[(x1 - 2, y)] = T['tela_s']
    for k in range(3):
        for x, y in ((x0 + 4 + k, topo + 2 + k), (x0 + 5 + k, topo + 2 + k)):
            if (x, y) in L.px:
                L.px[(x, y)] = T['brilho']
    for x in range(x0 + 1, x1):
        L.px[(x, topo + alt - 2)] = T['prata_s']
    return L.px


def _rosto(cid, ops, n, tipo, dx=0, dy=0):
    """Pixels de expressão, por cima do rosto do parado (já descido n):
    preocupado (sobrancelhas sobem na ponta de dentro), alerta (boca em
    'o') e boca_aberta (sorriso aberto: a boca de 2 px do falar)."""
    if tipo is None:
        return []
    out = {}
    if cid == 'saldanha':
        cinza_e = rgb('#5E5E65')
        if tipo in ('preocupado', 'alerta'):
            for x in (20, 24):
                out[(x, 12 + n - 1)] = cinza_e
        if tipo == 'alerta':
            out[(23, 21 + n)] = rgb('#3A1A12')
            out[(24, 21 + n)] = rgb('#3A1A12')
            out[(23, 22 + n)] = rgb('#6A3C2C')
            out[(24, 22 + n)] = rgb('#6A3C2C')
    if tipo == 'boca_aberta':
        im = escritorio.falando(cid)[2]
        for y in range(im.height):
            for x in range(im.width):
                p = im.getpixel((x, y))
                if p[3]:
                    out[(x, y)] = p[:3]
    return [op(costas.mover(out, dx, dy), 'cabeca')] if out else []


def saldanha_alerta():
    ops, n, pele = parado('saldanha')
    info = info_braco(ops, 'braco_tras', pele)
    ombro = (28, 34)
    out = []
    for q in ALERTA:
        M, P = braco_estendido(info, pele, ombro, q['cotovelo'], q['mao'], larg_manga=5)
        mov = q['mov']
        cab = mov.get('cabeca', {})
        base = _com_cabeca(trocar(ops, 'braco_tras', [op(M, 'braco_tras')]), n)
        base += _rosto('saldanha', ops, n, q['rosto'])
        # o antebraço e a mão passam na frente do rosto: vão por último e
        # acompanham a cabeça, para a palma ficar na testa
        base.append(op(P, 'mao_rosto'))
        mov = dict(mov, mao_rosto=dict(cab))
        out.append(anim.montar(base, mov))
    return out


def saldanha_apresentando():
    ops, n, pele = parado('saldanha')
    info = info_braco(ops, 'braco_tras', pele)
    manga = manga_original(ops, 'braco_tras')
    out = []
    for q in APRESENTANDO:
        P = antebraco(info, pele, q['cotovelo'], q['mao'])
        D = dedo(q['mao'], q['dedo'], pele)
        novo = trocar(ops, 'braco_tras', [op(D, 'braco_tras'), op(P, 'braco_tras'), op(manga, 'braco_tras')])
        out.append(anim.montar(_com_cabeca(novo, n), q['mov']))
    return out


def saldanha_comemorando():
    ops, n, pele = parado('saldanha')
    out = []
    for q in COMEMORANDO:
        novo = ops
        extra = []
        for lado, grupo in (('frente', 'braco_frente'), ('tras', 'braco_tras')):
            info = info_braco(ops, grupo, pele)
            o, c, m = q[lado]
            M, P = braco_estendido(info, pele, o, c, m, lado='l' if lado == 'frente' else 'r', larg_manga=5)
            if lado == 'tras':
                # atrás do tronco e da cabeça
                novo = trocar(novo, grupo, [op(P, grupo), op(M, grupo)])
            else:
                # o braço da frente sobe na frente da orelha e do cabelo
                novo = trocar(novo, grupo, [op(M, grupo)])
                extra.append(op(P, grupo))
        T = tablet_erguido(q['tablet'])
        cab = q['mov'].get('cabeca', {})
        base = _com_cabeca(novo, n) + _rosto('saldanha', ops, n, q['rosto']) + extra
        base.append(op(T, 'tablet'))
        # as mãos seguram o tablet por cima
        for lado in ('frente', 'tras'):
            m = q[lado][2]
            base.append(op(camada(mao(m[0], m[1] - 1), pele[0], pele[2], pele[1]), 'tablet'))
        out.append(anim.montar(base, q['mov']))
    return out


# ------------------------------------------------------------ Vivi
# manual §5.7: os braços sobem até o rosto e as mãos seguram o celular,
# entre (26, 19) e (36, 29); no Q2 a cabeça sobe 1 px e o flash dispara
# perto de (37, 18), por um quadro só
VIVI = [
    {'flash': False, 'mov': {}},
    {'flash': True, 'mov': {'cabeca': {'dy': -1}}},
]
# o braço da frente vai à frente do peito: a manga só até o cotovelo, para
# o antebraço aparecer por cima da blusa, da mesma cor da manga
VIVI_BRACOS = {'frente': ((10, 35), (17, 39), (26, 29)), 'tras': ((28, 35), (31, 41), (35, 28))}
VIVI_MANGA = {'frente': 8, 'tras': None}
CELULAR = {'x0': 27, 'x1': 34, 'y0': 23, 'y1': 28}
FLASH = (36, 21)
COR_CELULAR = {'corpo': rgb('#3A3A44'), 'aro': rgb('#17171C'), 'luz': rgb('#55555F'),
               'lente': rgb('#0E1420'), 'lente_l': rgb('#5A7AA0'), 'led': rgb('#F4E7A1')}


def celular():
    """O celular de lado, nas duas mãos: vemos as costas, com a câmera e o
    LED do flash no canto de cima, do lado da cena."""
    C = COR_CELULAR
    x0, x1, y0, y1 = CELULAR['x0'], CELULAR['x1'], CELULAR['y0'], CELULAR['y1']
    L = Layer(C['corpo'], C['aro'])
    L.rect(x0, y0, x1, y1)
    L.outline()
    for x in range(x0 + 1, x1):
        L.px[(x, y0 + 1)] = C['luz']
    L.px[(x1 - 2, y0 + 2)] = C['lente']
    L.px[(x1 - 3, y0 + 2)] = C['lente_l']
    L.px[(x1 - 1, y0 + 2)] = C['led']
    return L.px


def flash(cx, cy):
    """O clarão: miolo branco e quatro raios amarelados, mais as diagonais
    curtas."""
    branco, amarelo, claro = rgb('#FFFFFF'), rgb('#FFF3B0'), rgb('#FFE27A')
    pts = {(cx, cy): branco}
    for k in (1, 2):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            pts[(cx + dx * k, cy + dy * k)] = branco if k == 1 else amarelo
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        pts[(cx + dx, cy + dy)] = claro
    pts[(cx + 3, cy)] = claro
    pts[(cx, cy - 3)] = claro
    return pts


def vivi_foto():
    ops, n, pele = parado('vivi')
    out = []
    for q in VIVI:
        novo, extra = ops, []
        for lado, grupo in (('tras', 'braco_tras'), ('frente', 'braco_frente')):
            info = info_braco(ops, grupo, pele)
            o, c, m = VIVI_BRACOS[lado]
            M, P = braco_estendido(info, pele, o, c, m, lado='l' if lado == 'frente' else 'r',
                                   larg_manga=7, ombreira=ombreira(ops, grupo), manga_ate=VIVI_MANGA[lado])
            if lado == 'tras':
                novo = trocar(novo, grupo, [op(P, grupo), op(M, grupo)])
            else:
                novo = trocar(novo, grupo, [op(M, grupo)])
                extra.append(op(P, 'maos'))
        base = _com_cabeca(novo, n) + extra
        base.append(op(celular(), 'maos'))
        # os dedos por cima das bordas do celular
        for lado in ('frente', 'tras'):
            m = VIVI_BRACOS[lado][2]
            base.append(op(camada(mao(*m, 3, 3), pele[0], pele[2], pele[1]), 'maos'))
        if q['flash']:
            base.append(op(flash(*FLASH), 'flash'))
        out.append(anim.montar(base, q['mov']))
    return out


# ------------------------------------------------------------ Caio
# manual §5.6: uma pose só, o tablet virado para quem olha, com a tela
# livre para o jogo colar o selo. O desenho original do Caio já é essa pose
# (o "tablet" do chars.py, com o check verde); aqui a tela fica em branco.
VERDES = {rgb('#3DB64B'), rgb('#26863A')}


def caio_tablet():
    fn = chars.caio
    n = anim.folga(fn)
    ops = anim.agrupar(anim.gravar(fn, 'tablet'), anim.regra_humano)
    ops = [o for o in ops if not (o[0] == 'pixel' and next(iter(o[1].values())) in VERDES)]
    ops = [[k, costas.mover(p, 0, n), g, d] for k, p, g, d in ops]
    return [anim.montar(ops, {})], n


def tela_do_tablet():
    """O retângulo útil da tela do Caio (x0, y0, x1, y1, inclusive), no
    quadro final: a parte branca que a mão não cobre."""
    im, _ = caio_tablet()
    im = im[0]
    branco = (0xF5, 0xF7, 0xF8, 255)
    pts = [(x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y)) == branco]
    # as linhas inteiras de tela (sem a mão por cima)
    xs = sorted({x for x, _ in pts})
    linhas = sorted({y for _, y in pts if all((x, y) in set(pts) for x in xs)})
    return xs[0], linhas[0], xs[-1], linhas[-1]


# ------------------------------------------------------------ Saldanha à mesa
# manual §5.2: digitando no tablet, sentado à mesa, com os braços apoiados.
# É a pose da mesa (fase 3) com o tablet deitado no tampo no lugar do
# teclado (um objeto, tablet__frente-esq, que o jogo põe onde iria o
# teclado). Q2: cabeça y+1, mão da frente y-1, a de trás y+1; o tablet fica.
DIGITANDO = [
    {},
    {'cabeca': {'dy': 1}, 'mao_frente': {'dy': -1}, 'mao_tras': {'dy': 1}},
]


def digitando(so_tampo=False):
    ops, _ = escritorio._pose('saldanha')
    return [anim.montar(ops, mov, so_grupos=escritorio.TAMPO_GRUPOS if so_tampo else None) for mov in DIGITANDO]


def digitando_rosto():
    return [[m.get('cabeca', {}).get('dx', 0), chars.SIT_DY + m.get('cabeca', {}).get('dy', 0)] for m in DIGITANDO]


def digitando_maos():
    frente, tras = escritorio.maos('mesa')
    out = []
    for mov in DIGITANDO:
        q = []
        for lado, (x, y) in (('frente', frente), ('tras', tras)):
            m = mov.get(f'mao_{lado}', {})
            q.append([x + m.get('dx', 0), y + m.get('dy', 0)])
        out.append(q)
    return out


# ------------------------------------------------------------ adereços soltos
def envelope():
    """O envelope que o Gabriel carrega: 7 × 5, papel creme com a aba em V.
    A âncora é onde os dedos seguram (a ponta de cima, à esquerda): o jogo
    cola o envelope com a âncora no marcador "envelope" de cada quadro."""
    papel, aba, linha = rgb('#F3EFE2'), rgb('#BDB5A0'), rgb('#7A7466')
    im = Image.new('RGBA', (7, 5), (0, 0, 0, 0))
    for x in range(7):
        for y in range(5):
            borda = x in (0, 6) or y in (0, 4)
            im.putpixel((x, y), (linha if borda else papel) + (255,))
    for x, y in ((1, 1), (2, 2), (3, 3), (4, 2), (5, 1)):
        im.putpixel((x, y), aba + (255,))
    return im, [1, 1]


SELOS = {
    # cor: (fundo, contorno, desenho, cor do desenho)
    'verde': (rgb('#3DB64B'), rgb('#1F7A2E'), 'check', rgb('#FFFFFF')),
    'amarelo': (rgb('#F2C230'), rgb('#A87C10'), 'exclamacao', rgb('#5A3A08')),
    'vermelho': (rgb('#E04A3F'), rgb('#9A2A22'), 'x', rgb('#FFFFFF')),
}
DESENHOS = {
    'check': [(1, 3), (2, 4), (3, 3), (4, 2), (5, 1)],
    'exclamacao': [(3, 1), (3, 2), (3, 3), (3, 5)],
    'x': [(2, 2), (4, 2), (3, 3), (2, 4), (4, 4)],
}


def selo(cor):
    """O selo redondo que o jogo cola na tela do tablet do Caio, 7 × 7, com
    um desenho além da cor (check, exclamação, x) para não depender só da
    cor. A âncora é o centro."""
    fundo, contorno, desenho, tinta = SELOS[cor]
    linhas = {0: (2, 4), 1: (1, 5), 2: (0, 6), 3: (0, 6), 4: (0, 6), 5: (1, 5), 6: (2, 4)}
    pts = {(x, y) for y, (a, b) in linhas.items() for x in range(a, b + 1)}
    im = Image.new('RGBA', (7, 7), (0, 0, 0, 0))
    for (x, y) in pts:
        borda = any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        im.putpixel((x, y), (contorno if borda else fundo) + (255,))
    for p in DESENHOS[desenho]:
        im.putpixel(p, tinta + (255,))
    return im, [3, 3]


# ------------------------------------------------------------ o registro
# por personagem, na ordem das linhas da folha (depois das animações de
# todo humano): nome -> (quadros por segundo, repete?, direção)
ESPECIAIS = {
    'gabriel': {
        'deixando_envelope_no_malote': (6, False, 'frente'),
        'deixando_envelope_no_malote_costas': (6, False, 'costas'),
    },
    'saldanha': {
        'digitando_sentado': (6, True, 'frente'),
        'digitando_sentado_tampo': (6, True, 'frente'),
        'alerta': (5, False, 'frente'),
        'apresentando_quadro': (5, True, 'frente'),
        'comemorando_tablet': (5, False, 'frente'),
    },
    'caio': {'mostrando_tablet': (0, False, 'frente')},
    'vivi': {'tirando_foto': (6, False, 'frente')},
}
# quem leva o envelope na mão andando (lista do corte 2 nos assets): o
# Gabriel traz, o Saldanha busca no malote
CARREGA_ENVELOPE = ('gabriel', 'saldanha')
# o quadro em que o envelope sai da mão e vai para o malote; o do flash
SOLTA, FLASH_NO_QUADRO = 1, 1


def quadros(cid):
    """{animação: [quadros]} das ações especiais de cid (vazio para quem
    não tem)."""
    fazer = {
        'deixando_envelope_no_malote': gabriel_envelope,
        'deixando_envelope_no_malote_costas': gabriel_envelope_costas,
        'digitando_sentado': digitando,
        'digitando_sentado_tampo': lambda: digitando(so_tampo=True),
        'alerta': saldanha_alerta,
        'apresentando_quadro': saldanha_apresentando,
        'comemorando_tablet': saldanha_comemorando,
        'mostrando_tablet': lambda: caio_tablet()[0],
        'tirando_foto': vivi_foto,
    }
    return {nome: fazer[nome]() for nome in ESPECIAIS.get(cid, {})}


def _pega(mx, my):
    """Onde vai a âncora do envelope com a mão em (mx, my): os dedos
    seguram a ponta de cima, à esquerda."""
    return [mx, my]


def mao_no_quadro(ops, mov, grupo):
    """O centro da mão de um braço solto num quadro: o meio das três
    últimas linhas do que aparece do braço."""
    im = anim.montar(ops, mov, so_grupos=(grupo,))
    pts = [(x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3]]
    fundo = max(y for _, y in pts)
    xs = [x for x, y in pts if y >= fundo - 2]
    return _r((min(xs) + max(xs)) / 2), fundo - 1


def envelope_na_caminhada(cid, nome):
    """Os pontos do envelope nos 4 quadros da caminhada: na mão da direita
    da tela (de frente, a de trás; de costas, a da frente), como no manual
    §5.1 (de frente perto de (32, 43); de costas, de (31, 43))."""
    if nome == 'andando_frente':
        ops, n = escritorio._parado(cid)
        grupo = 'braco_tras'
    else:
        n = anim.folga(costas.HUMANOS[cid][0])
        ops = [[k, costas.mover(p, 0, n), g, d] for k, p, g, d in costas.ops(cid, 'parado')]
        grupo = 'braco_frente'
    return [_pega(*mao_no_quadro(ops, q, grupo)) for q in anim.ANDANDO]


def campos(cid, nome, nquadros):
    """Os campos do manifesto de uma ação especial (além de linha, quadros,
    fps e loop): direcao e os marcadores de cada uma."""
    fps, loop, direcao = ESPECIAIS[cid][nome]
    e = {'direcao': direcao}
    if nome == 'deixando_envelope_no_malote':
        e['rosto'] = [[q['mov'].get('cabeca', {}).get('dx', 0), q['mov'].get('cabeca', {}).get('dy', 0)]
                      for q in GABRIEL]
        e['envelope'] = [_pega(*q['mao']) for q in GABRIEL]
        e['solta'] = SOLTA
    elif nome == 'deixando_envelope_no_malote_costas':
        e['envelope'] = [_pega(*q['mao']) for q in GABRIEL_COSTAS]
        e['solta'] = SOLTA
    elif nome == 'digitando_sentado':
        e['rosto'] = digitando_rosto()
        e['tampo'] = 'digitando_sentado_tampo'
        e['maos'] = digitando_maos()
        e['mesa'] = 'mesa'
        e['no_lugar_do_teclado'] = 'tablet'
    elif nome == 'digitando_sentado_tampo':
        e['camada_de'] = 'digitando_sentado'
    elif nome == 'apresentando_quadro':
        e['rosto'] = [[q['mov'].get('cabeca', {}).get('dx', 0), 0] for q in APRESENTANDO]
        e['dedo'] = [list(ponta_do_dedo(q)) for q in APRESENTANDO]
    elif nome == 'mostrando_tablet':
        e['rosto'] = [[0, 0]]
        x0, y0, x1, y1 = tela_do_tablet()
        e['tela'] = [x0, y0, x1, y1]
        e['selo'] = [(x0 + x1) // 2, (y0 + y1) // 2]
    elif nome == 'tirando_foto':
        e['rosto'] = [[0, q['mov'].get('cabeca', {}).get('dy', 0)] for q in VIVI]
        e['flash'] = list(FLASH)
        e['flash_no_quadro'] = FLASH_NO_QUADRO
    return e


def ponta_do_dedo(q):
    dx, dy = q['dedo']
    d = math.hypot(dx, dy)
    return _r(q['mao'][0] + dx / d * 4), _r(q['mao'][1] + dy / d * 4)
