"""As animações de cada humano, prontas para a folha de sprites.

A ordem das linhas mantém o que o jogo já usa (parado e sentado de frente
nas linhas 0 e 1) e acrescenta as do manual (§3 e §8.1, fase 2): parado e
sentado de costas e as duas caminhadas. Todos os quadros ficam na tela de
40 × 70 com a sola na linha anim.PE, então a âncora é a mesma em todos:
(20, anim.PE).
"""
import anim
import costas

ANCORA = (20, anim.PE)

# nome: (quadros por segundo, repete?)
ANIMACOES = {
    'parado_frente': (0, False),
    'sentado_frente': (0, False),
    'parado_costas': (0, False),
    'sentado_costas': (0, False),
    'andando_frente': (8, True),
    'andando_costas': (8, True),
}


def quadros(cid):
    """{animação: [quadros]} de um humano, pelo id do assets/."""
    frente, _ = costas.HUMANOS[cid]
    n = anim.folga(frente)
    ops_costas = costas.ops(cid, 'parado')
    return {
        'parado_frente': [anim.descer(frente('parado'), n)],
        'sentado_frente': [anim.descer(frente('sentado'), n)],
        'parado_costas': [costas.imagem(cid, 'parado')],
        'sentado_costas': [costas.imagem(cid, 'sentado')],
        'andando_frente': anim.andando(frente),
        'andando_costas': [anim.montar(ops_costas, q, n) for q in anim.ANDANDO],
    }


HUMANOS = list(costas.HUMANOS)
