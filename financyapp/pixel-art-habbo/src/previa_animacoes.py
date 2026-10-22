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
