"""Prévia das animações: faixas ampliadas (nearest-neighbor) e uma página
autocontida com os ciclos tocando, para revisar antes de levar ao jogo.

    python3 src/previa_animacoes.py

Saída em previa/animacoes/: <id>-faixas@6x.png (os quadros lado a lado,
rótulos fora dos sprites) e <id>.html (a página, com os PNGs embutidos).
"""
import base64
import io
import json
import os

from PIL import Image, ImageDraw

import anim
import chars
import costas

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'previa', 'animacoes')
PISO = os.path.join(AQUI, '..', 'assets', 'piso')

FASES = ['Q1 · contato A', 'Q2 · passagem A', 'Q3 · contato B', 'Q4 · passagem B']


def quadros_guilherme():
    """Tudo o que o piloto entrega, por nome de animação (manual §3)."""
    n = anim.folga(chars.guilherme)
    frente = anim.andando(chars.guilherme)
    ops_costas = costas.guilherme_ops('parado')
    tras = [anim.montar(ops_costas, q, n) for q in anim.ANDANDO]
    return {
        'parado_frente': [anim.descer(chars.guilherme('parado'), n)],
        'parado_costas': [costas.guilherme('parado')],
        'andando_frente': frente,
        'andando_costas': tras,
        'sentado_frente': [anim.descer(chars.guilherme('sentado'), n)],
        'sentado_costas': [costas.guilherme('sentado')],
    }


def png64(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def faixas(anims, k=6, fundo=(34, 42, 70, 255)):
    """Uma linha por animação, quadros da esquerda para a direita, com o
    nome e o número de cada quadro escritos fora do sprite."""
    pad, rot = 8, 14
    w, h = 40, 70
    n = max(len(v) for v in anims.values())
    W = 150 + n * (w * k + pad)
    H = len(anims) * (h * k + rot + pad) + pad
    out = Image.new('RGBA', (W, H), fundo)
    d = ImageDraw.Draw(out)
    y = pad
    for nome, frames in anims.items():
        d.text((8, y + h * k // 2), nome, fill=(232, 235, 244, 255))
        for i, f in enumerate(frames):
            x = 150 + i * (w * k + pad)
            out.alpha_composite(f.resize((w * k, h * k), Image.NEAREST), (x, y))
            d.text((x, y + h * k + 2), f'{i + 1}', fill=(169, 177, 201, 255))
        y += h * k + rot + pad
    return out


def pagina(cid, nome, anims):
    dados = {k: [png64(f) for f in v] for k, v in anims.items()}
    piso = [png64(Image.open(os.path.join(PISO, f'piso_madeira__{i}.png'))) for i in (1, 2, 3)]
    modelo = open(os.path.join(AQUI, 'previa_animacoes.html'), encoding='utf-8').read()
    return (modelo.replace('__NOME__', nome)
            .replace('__DADOS__', json.dumps(dados))
            .replace('__PISO__', json.dumps(piso))
            .replace('__FASES__', json.dumps(FASES, ensure_ascii=False)))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    anims = quadros_guilherme()
    faixas(anims).save(os.path.join(SAIDA, 'guilherme-faixas@6x.png'))
    with open(os.path.join(SAIDA, 'guilherme.html'), 'w', encoding='utf-8') as f:
        f.write(pagina('guilherme', 'Guilherme', anims))
    print('ok:', os.path.relpath(SAIDA))


if __name__ == '__main__':
    main()
