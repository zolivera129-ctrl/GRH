"""Prévia das animações: uma página autocontida com os ciclos tocando, para
revisar antes de levar ao jogo, e uma prancha com todos os quadros
ampliados (nearest-neighbor), rótulos fora dos sprites.

    python3 src/previa_animacoes.py

Saída em previa/animacoes/: index.html (a página, com os PNGs embutidos)
e elenco-quadros@3x.png (a prancha).
"""
import base64
import io
import json
import os

from PIL import Image, ImageDraw

import animacoes
import escritorio
import office

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'previa', 'animacoes')
PISO = os.path.join(AQUI, '..', 'assets', 'piso')

FASES = ['Q1 · contato A', 'Q2 · passagem A', 'Q3 · contato B', 'Q4 · passagem B']


def png64(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def prancha(todos, k=3, fundo=(34, 42, 70, 255)):
    """Uma linha por personagem, com as poses e os oito quadros das
    caminhadas; o nome e o rótulo de cada coluna ficam fora dos sprites."""
    colunas = [('parado', 'parado_frente', 0), ('parado', 'parado_costas', 0),
               ('sentado', 'sentado_frente', 0), ('sentado', 'sentado_costas', 0)]
    colunas += [(f'frente {i + 1}', 'andando_frente', i) for i in range(4)]
    colunas += [(f'costas {i + 1}', 'andando_costas', i) for i in range(4)]
    w, h, esq, topo, gap = 40 * k, 70 * k, 110, 26, 6
    W = esq + len(colunas) * (w + gap)
    H = topo + len(todos) * (h + gap)
    out = Image.new('RGBA', (W, H), fundo)
    d = ImageDraw.Draw(out)
    for c, (rot, _, _) in enumerate(colunas):
        d.text((esq + c * (w + gap) + 4, 8), rot, fill=(169, 177, 201, 255))
    for r, (cid, a) in enumerate(todos.items()):
        y = topo + r * (h + gap)
        d.text((8, y + h // 2), office.PERSONAGENS[cid][0], fill=(232, 235, 244, 255))
        for c, (_, nome, i) in enumerate(colunas):
            out.alpha_composite(a[nome][i].resize((w, h), Image.NEAREST), (esq + c * (w + gap), y))
    return out


def estacoes(ids):
    """As estações de trabalho em camadas, uma por móvel (quem não tem
    estação própria usa a flexível), e de quem é cada uma."""
    por_chave, de_quem = {}, {}
    for cid in ids:
        fundo, mesa, teclado, objs, esp = escritorio.camadas_da_estacao(cid)
        chave = png64(fundo) + png64(mesa) + png64(teclado)
        if chave not in por_chave:
            por_chave[chave] = {'fundo': png64(fundo), 'mesa': png64(mesa), 'teclado': png64(teclado),
                                'objetos': png64(objs), 'espelhar': esp, 'ancora': [100, 84]}
        de_quem[cid] = list(por_chave).index(chave)
    return list(por_chave.values()), de_quem


def especiais_dados(todos, man):
    """O que a seção das ações especiais precisa além dos quadros: os
    campos do manifesto, os adereços e as cenas (a estação do Saldanha com o
    tablet no lugar do teclado, a do Caio sem a sineta, que toca à parte)."""
    import especiais
    A = os.path.join(AQUI, '..', 'assets')

    def arq(rel):
        return png64(Image.open(os.path.join(A, rel)).convert('RGBA'))
    campos = {cid: {n: animacoes.campos(cid, n, len(todos[cid][n])) for n in nomes}
              for cid, nomes in especiais.ESPECIAIS.items()}
    tempo = {cid: {n: list(animacoes.tempo(cid, n)) for n in nomes} for cid, nomes in especiais.ESPECIAIS.items()}
    envelope = {cid: {n: animacoes.campos(cid, n, 4)['envelope'] for n in ('andando_frente', 'andando_costas')}
                for cid in especiais.CARREGA_ENVELOPE}
    fundo, mesa, tablet, objs, esp = escritorio.camadas_da_estacao('saldanha', no_teclado='tablet')
    sem_monitor = escritorio.camadas_da_estacao('saldanha', no_teclado='tablet', sem=('monitor',))[3]
    est_saldanha = {'fundo': png64(fundo), 'mesa': png64(mesa), 'teclado': png64(tablet),
                    'objetos': png64(objs), 'sem_monitor': png64(sem_monitor), 'espelhar': esp, 'ancora': [100, 84]}
    pos = {}
    fundo, mesa, teclado, objs, esp = escritorio.camadas_da_estacao('caio', sem=('sineta',), posicoes=pos)
    est_caio = {'fundo': png64(fundo), 'mesa': png64(mesa), 'teclado': png64(teclado),
                'objetos': png64(objs), 'espelhar': esp, 'ancora': [100, 84], 'sineta': list(pos['sineta'])}
    sin = man['sineta']['animacoes']['tocando']
    tira = Image.open(os.path.join(A, sin['folha'])).convert('RGBA')
    w, h = sin['tela']
    return {
        'campos': campos, 'tempo': tempo, 'envelope_andando': envelope,
        'envelope': {'img': arq('objetos/envelope.png'), 'ancora': man['envelope']['ancora']},
        'malote': {'vazio': arq('moveis/malote__vazio.png'), 'com': arq('moveis/malote__com-envelope.png'),
                   'ancora': man['malote']['ancora'], 'abertura': man['malote']['abertura']},
        'selos': {c: arq(f'objetos/selo_tablet__{c}.png') for c in man['selo_tablet']['estados']},
        'selo_ancora': man['selo_tablet']['ancora'],
        'sineta': {'quadros': [png64(tira.crop((w * k, 0, w * (k + 1), h))) for k in range(sin['quadros'])],
                   'ancora': sin['ancora'], 'fps': sin['fps'], 'toque': sin['toque']},
        'quadro': {'img': arq('parede/quadro_branco__limpo.png'), 'ancora': man['quadro_branco']['ancora'],
                   'altura': man['quadro_branco']['altura']},
        'parede': man['parede']['cores'],
        'est_saldanha': est_saldanha, 'est_caio': est_caio,
    }


def caes_dados():
    """Os cachorros (fase 6): os quadros novos e o em pé, na mesma tela,
    com a âncora do em pé, e as camas, como o assets/ tem."""
    import caes
    import office
    A = os.path.join(AQUI, '..', 'assets')
    man = json.load(open(os.path.join(A, 'manifest.json')))
    out = {}
    for cid in caes.ANIMACOES:
        q = caes.quadros(cid)
        em_pe = caes.quadros_em_pe(cid, [{}])[0]
        fn, k = caes.DESENHO[cid]
        sentado = office.dog(fn(k))
        cama = man[caes.CAMA[cid]]
        out[cid] = {
            'nome': office.PERSONAGENS[cid][0],
            'anims': {n: [png64(f) for f in fs] for n, fs in q.items()},
            'em_pe': png64(em_pe), 'ancora': office.paw_anchor(em_pe),
            'sentado': png64(sentado), 'ancora_sentado': office.paw_anchor(sentado),
            'tempo': {n: list(v) for n, v in caes.ANIMACOES[cid].items()},
            'cama': {'img': png64(Image.open(os.path.join(A, 'moveis', caes.CAMA[cid] + '.png')).convert('RGBA')),
                     'ancora': cama['ancora']},
        }
    return out


def pagina(todos):
    dados = {cid: {k: [png64(f) for f in v] for k, v in a.items()} for cid, a in todos.items()}
    lista, de_quem = estacoes(list(todos))
    mesa = {
        'estacoes': lista, 'de_quem': de_quem,
        'rosto': {n: escritorio.rosto(n) for n in animacoes.ESCRITORIO},
        'tempo': {n: list(animacoes.ANIMACOES[n]) for n in animacoes.ANIMACOES},
        'tampo': {cid: escritorio.TAMPO.get(cid, 'mesa') for cid in todos},
    }
    man = json.load(open(os.path.join(AQUI, '..', 'assets', 'manifest.json')))
    import cadeira
    cadeira_ = {'img': png64(Image.open(os.path.join(AQUI, '..', 'assets', 'moveis', 'cadeira__frente-dir.png'))),
                'ancora': man['cadeira']['ancora'], 'desloca': {n: cadeira.desloca(n) for n in cadeira.ROTEIROS}}
    nomes = {cid: office.PERSONAGENS[cid][0] for cid in todos}
    piso = [png64(Image.open(os.path.join(PISO, f'piso_madeira__{i}.png'))) for i in (1, 2, 3)]
    modelo = open(os.path.join(AQUI, 'previa_animacoes.html'), encoding='utf-8').read()
    return (modelo.replace('__DADOS__', json.dumps(dados))
            .replace('__ESPECIAIS__', json.dumps(especiais_dados(todos, man), ensure_ascii=False))
            .replace('__CAES__', json.dumps(caes_dados(), ensure_ascii=False))
            .replace('__MESA__', json.dumps(mesa))
            .replace('__CADEIRA__', json.dumps(cadeira_))
            .replace('__NOMES__', json.dumps(nomes, ensure_ascii=False))
            .replace('__PISO__', json.dumps(piso))
            .replace('__ANCORA__', json.dumps(list(animacoes.ANCORA)))
            .replace('__FASES__', json.dumps(FASES, ensure_ascii=False)))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    todos = {cid: animacoes.quadros(cid) for cid in animacoes.HUMANOS}
    prancha(todos).save(os.path.join(SAIDA, 'elenco-quadros@3x.png'))
    with open(os.path.join(SAIDA, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(pagina(todos))
    print('ok:', os.path.relpath(SAIDA))


if __name__ == '__main__':
    main()
