"""Testes do manual de animações (§9.2) que valem para o que já existe,
para os 12 humanos, os das ações especiais (itens 9 a 11) e os dos
cachorros (item 12).

    python3 src/teste_animacoes.py
"""
import unittest
from collections import Counter

import anim
import animacoes
import costas
import especiais
from anim import PE    # a linha do chão, a âncora (o bbox termina aqui)

CACHE = {}
CAMADAS = ({n for n in animacoes.ANIMACOES if n.endswith('_tampo')} | set(animacoes.SOBREPOSICOES)
           | {n for e in especiais.ESPECIAIS.values() for n in e if n.endswith('_tampo')})


def todos():
    if not CACHE:
        for cid in animacoes.HUMANOS:
            CACHE[cid] = animacoes.quadros(cid)
    return CACHE


class Humanos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = todos()

    def test_lista_de_animacoes(self):
        for cid, a in self.t.items():
            self.assertEqual(list(a), animacoes.nomes(cid), cid)

    def test_tela_40x70_sem_meio_tom(self):
        # 1. 40 × 70, pixels inteiros e transparência sem meio-termo
        for cid, a in self.t.items():
            for nome, quadros in a.items():
                for im in quadros:
                    self.assertEqual(im.size, (40, 70), (cid, nome))
                    alfas = set(im.getchannel('A').getdata())
                    self.assertLessEqual(alfas, {0, 255}, (cid, nome))

    def test_ancora_no_chao(self):
        # 2. a âncora não mexe: nas poses e nos contatos, o pé da frente
        # pisa na linha da âncora. No Q2 o pé da frente está no ar e o de
        # trás, plantado, fica 1 px acima (é a profundidade).
        for cid, a in self.t.items():
            for nome, quadros in a.items():
                if nome in CAMADAS:
                    continue
                for i, im in enumerate(quadros):
                    esperado = PE - 1 if nome.startswith('andando') and i == 1 else PE
                    self.assertEqual(im.getbbox()[3], esperado, (cid, nome, i))

    def test_pe_plantado_nao_mexe(self):
        # no Q2 o pé de trás e no Q4 o da frente ficam onde estavam no parado
        # (de frente o pé de trás é o da direita; de costas, o da esquerda)
        dir_, esq = (25, PE - 6, 31, PE), (11, PE - 5, 18, PE)
        casos = (('parado_frente', 'andando_frente', 1, dir_), ('parado_frente', 'andando_frente', 3, esq),
                 ('parado_costas', 'andando_costas', 1, esq), ('parado_costas', 'andando_costas', 3, dir_))
        for cid, a in self.t.items():
            for parado, ciclo, i, caixa in casos:
                self.assertEqual(a[ciclo][i].crop(caixa).tobytes(), a[parado][0].crop(caixa).tobytes(),
                                 (cid, ciclo, i))

    def test_nada_vaza_da_tela(self):
        for cid, a in self.t.items():
            for nome, quadros in a.items():
                for i, im in enumerate(quadros):
                    if im.getbbox() is None:
                        continue            # quadro vazio de sobreposição
                    x0, y0, x1, y1 = im.getbbox()
                    # o tablet do desenho original do Caio encosta na
                    # coluna 0 (encosta, não corta)
                    esq = 0 if (cid, nome) == ('caio', 'mostrando_tablet') else 1
                    self.assertTrue(x0 >= esq and y0 > 0 and x1 <= 40, (cid, nome, i))

    def test_caminhada_quatro_poses_distintas(self):
        # 6. quatro poses visualmente distintas
        for cid, a in self.t.items():
            for nome in ('andando_frente', 'andando_costas'):
                self.assertEqual(len(a[nome]), 4)
                self.assertEqual(len({im.tobytes() for im in a[nome]}), 4, (cid, nome))

    def test_caminhada_corpo_sobe_so_nas_passagens(self):
        # o topo da cabeça sobe 1 px em Q2 e Q4 e volta em Q1 e Q3 (loop sem salto)
        for cid, a in self.t.items():
            for nome in ('andando_frente', 'andando_costas'):
                topo = [im.getbbox()[1] for im in a[nome]]
                self.assertEqual(topo[0], topo[2], (cid, nome))
                self.assertEqual(topo[1], topo[3], (cid, nome))
                self.assertEqual(topo[0] - topo[1], 1, (cid, nome))

    def test_contato_tem_a_cabeca_do_parado(self):
        # só pernas e braços mexem nos contatos
        for cid, a in self.t.items():
            for parado, ciclo in (('parado_frente', 'andando_frente'), ('parado_costas', 'andando_costas')):
                p = a[parado][0].crop((0, 0, 40, 30)).tobytes()
                for i in (0, 2):
                    self.assertEqual(a[ciclo][i].crop((0, 0, 40, 30)).tobytes(), p, (cid, ciclo, i))

    def test_sentado_de_costas_no_mesmo_assento(self):
        # 3. sentado de costas com o quadril e os pés do sentado de frente
        for cid, a in self.t.items():
            f, c = a['sentado_frente'][0], a['sentado_costas'][0]
            self.assertEqual(f.getbbox()[3], c.getbbox()[3], cid)
            self.assertEqual(f.crop((0, PE - 7, 40, 70)).tobytes(), c.crop((0, PE - 7, 40, 70)).tobytes(), cid)

    def test_de_costas_nao_tem_rosto(self):
        # 4. de costas, os olhos de frente somem (viram cabelo, nuca ou pele)
        for cid, a in self.t.items():
            n = anim.folga(costas.HUMANOS[cid][0])
            f, c = a['parado_frente'][0], a['parado_costas'][0]
            for x, y in ((19, 16), (24, 16), (19, 17), (24, 17)):
                self.assertNotEqual(c.getpixel((x, y + n)), f.getpixel((x, y + n)), (cid, x, y))


    # ------------------------------------------------------------ fase 3
    def test_mesa_parada_quadril_e_pernas_nao_mexem(self):
        # 7. na vida à mesa, do quadril para baixo nada mexe, a não ser as
        # mãos e os antebraços (que estão na camada do tampo)
        for cid, a in self.t.items():
            for nome in animacoes.ESCRITORIO:
                tampo = set()
                for im in a[f'{nome}_tampo']:
                    tampo |= {(x, y) for y in range(70) for x in range(40) if im.getpixel((x, y))[3]}
                base = a[nome][0]
                for k, im in enumerate(a[nome]):
                    for y in range(PE - 12, 70):
                        for x in range(40):
                            if (x, y) not in tampo:
                                self.assertEqual(im.getpixel((x, y)), base.getpixel((x, y)), (cid, nome, k, x, y))

    def test_tampo_e_parte_do_quadro(self):
        # a camada do tampo repete os pixels do quadro: colada por cima, não muda nada
        for cid, a in self.t.items():
            for nome in animacoes.ESCRITORIO:
                for k, (corpo, tampo) in enumerate(zip(a[nome], a[f'{nome}_tampo'])):
                    self.assertIsNotNone(tampo.getbbox(), (cid, nome, k))
                    for y in range(70):
                        for x in range(40):
                            p = tampo.getpixel((x, y))
                            if p[3]:
                                self.assertEqual(p, corpo.getpixel((x, y)), (cid, nome, k, x, y))

    def test_teclando_so_mexe_as_maos(self):
        # pedido do Guilherme: teclando não balança o corpo; fora da camada
        # do tampo, os quadros são iguais ao primeiro
        for cid, a in self.t.items():
            tampo = set()
            for im in a['teclando_frente_tampo']:
                tampo |= {(x, y) for y in range(70) for x in range(40) if im.getpixel((x, y))[3]}
            base = a['teclando_frente'][0]
            for k, im in enumerate(a['teclando_frente']):
                for y in range(70):
                    for x in range(40):
                        if (x, y) not in tampo:
                            self.assertEqual(im.getpixel((x, y)), base.getpixel((x, y)), (cid, k, x, y))

    def test_dentes_somem_ao_falar(self):
        # pedido do Guilherme: quem tem dente na boca de repouso perde metade
        # dos dentes no Q2 e todos no Q3
        import escritorio
        for cid, a in self.t.items():
            n = anim.folga(costas.HUMANOS[cid][0])
            base = a['parado_frente'][0]
            dentes = escritorio._dentes(base, cid, n)
            for k, esperado in ((1, len({x for x, _ in dentes}) // 2 or (1 if dentes else 0)), (2, 0)):
                im = base.copy()
                im.alpha_composite(a['falando_frente'][k])
                ficaram = [p for p in dentes if min(im.getpixel(p)[:3]) >= 235]
                if dentes:
                    self.assertEqual(len(ficaram), esperado, (cid, k))

    def test_braco_a_mesa_tem_a_pele_do_rosto(self):
        # pedido do Guilherme: o braço sentado à mesa tem a mesma pele do
        # rosto (antes saía na cor do contorno em quem tem braço de 4 px)
        import escritorio
        from px import mix
        for cid, a in self.t.items():
            P = costas.Costas(costas.HUMANOS[cid][0]).P
            sk, sks = P['sk'], P['sks']
            luz = mix(sk, (255, 255, 255), 0.16)
            frente, _ = escritorio.maos(escritorio.TAMPO.get(cid, 'mesa'))
            cores = Counter(c for c in a['teclando_frente_tampo'][0].getdata() if c[3])
            self.assertIn(a['teclando_frente'][0].getpixel(frente)[:3], (sk, sks, luz), cid)
            self.assertIn(sk + (255,), cores, cid)

    def test_teclando_alterna_os_punhos(self):
        # 4.2: as mãos sobem e descem 1 px em oposição; a mesa (o tampo) não
        # existe no sprite, e o quadril fica onde estava
        for cid, a in self.t.items():
            q = a['teclando_frente_tampo']
            self.assertNotEqual(q[1].tobytes(), q[0].tobytes(), cid)
            self.assertNotEqual(q[2].tobytes(), q[0].tobytes(), cid)
            self.assertNotEqual(q[1].tobytes(), q[2].tobytes(), cid)

    def test_sobreposicoes_so_no_rosto(self):
        # 4.4 e 4.6: piscar e falar mexem só nos olhos e na boca, e o quadro
        # de repouso é vazio
        for cid, a in self.t.items():
            n = anim.folga(costas.HUMANOS[cid][0])
            pisca, fala = a['piscando_frente'], a['falando_frente']
            self.assertIsNone(pisca[0].getbbox(), cid)
            self.assertIsNone(pisca[2].getbbox(), cid)
            self.assertIsNone(fala[0].getbbox(), cid)
            x0, y0, x1, y1 = pisca[1].getbbox()
            self.assertTrue(16 <= x0 and x1 <= 28 and 15 + n <= y0 and y1 <= 18 + n, (cid, pisca[1].getbbox()))
            for k in (1, 2):
                x0, y0, x1, y1 = fala[k].getbbox()
                self.assertTrue(21 <= x0 and x1 <= 27 and 21 + n <= y0 and y1 <= 27 + n, (cid, k, fala[k].getbbox()))
            self.assertEqual(fala[1].tobytes(), fala[3].tobytes(), cid)

    def test_rosto_marca_onde_esta_o_olho(self):
        # o deslocamento "rosto" de cada quadro leva a pupila do parado de
        # frente até a pupila daquele quadro (menos quando ela olha de lado)
        for cid, a in self.t.items():
            n = anim.folga(costas.HUMANOS[cid][0])
            pupila = a['parado_frente'][0].getpixel((19, 17 + n))
            for nome in ['sentado_frente', 'andando_frente'] + animacoes.ESCRITORIO + animacoes.CADEIRA:
                marcas = animacoes.campos(cid, nome, len(a[nome]))['rosto']
                for k, (im, (dx, dy)) in enumerate(zip(a[nome], marcas)):
                    if nome == 'olhando_para_o_lado_frente' and k in (1, 2):
                        continue
                    self.assertEqual(im.getpixel((19 + dx, 17 + n + dy)), pupila, (cid, nome, k))


    def test_quadril_sentado(self):
        # 3. sentado, o quadril (o alto das pernas, por baixo do tronco) fica
        # a uns 14 px da âncora, na altura do assento da cadeira; a cintura
        # alta das pantalonas e calças de cintura alta sobe até 18
        import escritorio
        for cid in self.t:
            fn = costas.HUMANOS[cid][0]
            n = anim.folga(fn)
            ops = [[k, costas.mover(p, 0, n), g, d] for k, p, g, d in escritorio.gravar_sentado(fn)]
            topo = anim.montar(ops, {}, so_grupos=('pernas',)).getbbox()[1]
            self.assertTrue(14 <= PE - topo <= 18, (cid, PE - topo))

    def test_paleta_e_a_do_desenho(self):
        # 5 e 14. nenhuma cor nova na roupa, no cabelo ou na pele: todo
        # quadro usa as cores das quatro poses-base (e do desenho original
        # com o tablet, no Saldanha e no Caio), mais só estas, que são novas
        # de propósito: a luz no dorso da mão à mesa, a boca aberta ao falar e
        # os adereços (tablet erguido, celular e flash). Também garante que
        # não há rótulo nem texto nas texturas.
        import chars
        import escritorio
        from px import rgb
        props = set(especiais.TABLET.values()) | set(especiais.COR_CELULAR.values()) \
            | set(especiais.flash(0, 0).values())
        for cid, a in self.t.items():
            base = set()
            for nome in ('parado_frente', 'sentado_frente', 'parado_costas', 'sentado_costas'):
                base |= {c[:3] for c in a[nome][0].getdata() if c[3]}
            if cid in ('saldanha', 'caio'):
                base |= {c[:3] for c in getattr(chars, cid)('tablet').getdata() if c[3]}
            ops, n = escritorio._parado(cid)
            luz = escritorio.pele_do_rosto(ops, n, sentado=False)[3]
            permitidas = base | props | {luz, escritorio.BOCA_ESCURA, rgb(escritorio.BOCA[cid][3])}
            for nome, quadros in a.items():
                for k, im in enumerate(quadros):
                    novas = {c[:3] for c in im.getdata() if c[3]} - permitidas
                    self.assertFalse(novas, (cid, nome, k, sorted(novas)[:4]))


    # ------------------------------------------------------------ fase 4
    def test_cadeira_comeca_e_termina_nas_poses(self):
        # 8. sentando termina exatamente na pose sentada; levantando, na pose
        # em pé; e cada um começa na outra
        for cid, a in self.t.items():
            sob, sen = a['levantando_da_cadeira_frente'], a['sentando_na_cadeira_frente']
            self.assertEqual(len(sob), 6, cid)
            self.assertEqual(len(sen), 6, cid)
            self.assertEqual(sob[0].tobytes(), a['sentado_frente'][0].tobytes(), cid)
            self.assertEqual(sob[-1].tobytes(), a['parado_frente'][0].tobytes(), cid)
            self.assertEqual(sen[0].tobytes(), a['parado_frente'][0].tobytes(), cid)
            self.assertEqual(sen[-1].tobytes(), a['sentado_frente'][0].tobytes(), cid)

    def test_cadeira_sai_para_o_chao(self):
        # pedido do Guilherme: em pé, fora da cadeira; levantar anda até meio
        # tile à frente e sentar volta para o centro do tile, sempre para a
        # frente e sem pulo maior que 4 px por quadro
        import cadeira
        for nome, (ini, fim) in (('levantando_da_cadeira_frente', ((0, 0), (16, 8))),
                                 ('sentando_na_cadeira_frente', ((16, 8), (0, 0)))):
            d = [tuple(p) for p in animacoes.campos('guilherme', nome, 6)['desloca']]
            self.assertEqual((d[0], d[-1]), (ini, fim), nome)
            for a_, b_ in zip(d, d[1:]):
                self.assertLessEqual(abs(b_[0] - a_[0]), 4, nome)
                self.assertEqual(b_[1] - a_[1], (b_[0] - a_[0]) // 2, nome)   # na direção do iso, 2:1

    def test_cadeira_sem_quadro_congelado(self):
        # 8. nenhum quadro repete o anterior
        for cid, a in self.t.items():
            for nome in animacoes.CADEIRA:
                q = a[nome]
                for k in range(1, len(q)):
                    self.assertNotEqual(q[k].tobytes(), q[k - 1].tobytes(), (cid, nome, k))



# ------------------------------------------------------------ fase 5
def pixels(im, cor=None):
    return {(x, y) for y in range(im.height) for x in range(im.width)
            if im.getpixel((x, y))[3] and (cor is None or im.getpixel((x, y))[:3] == cor)}


def da_mao(cid, im):
    """Os pixels de pele (base, sombra e contorno) de um quadro."""
    P = costas.Costas(costas.HUMANOS[cid][0]).P
    return set().union(*(pixels(im, P[k]) for k in ('sk', 'sks', 'skline')))


def perto(p, pts, r=2):
    return any(abs(p[0] - q[0]) <= r and abs(p[1] - q[1]) <= r for q in pts)


class Especiais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = todos()

    def test_listagem_bate_com_o_resumo(self):
        # 13. a listagem de tudo o que o manifesto tem confere com as
        # tabelas 8.1 e 8.2; o que não está no manual tem motivo registrado
        import json
        import os
        import qa
        man = json.load(open(os.path.join(qa.ASSETS, 'manifest.json'), encoding='utf-8'))
        linhas = qa.listagem(man)
        self.assertEqual(qa.conferir(linhas), [])
        self.assertTrue(all(l['confere'] for l in linhas))

    def test_resumo_8_2(self):
        # 13. id, quadros, FPS e modo de cada ação, como no resumo 8.2
        esperado = {
            ('gabriel', 'deixando_envelope_no_malote'): (2, 6, False),
            ('saldanha', 'digitando_sentado'): (2, 6, True),
            ('saldanha', 'alerta'): (2, 5, False),
            ('saldanha', 'apresentando_quadro'): (2, 5, True),
            ('saldanha', 'comemorando_tablet'): (2, 5, False),
            ('caio', 'mostrando_tablet'): (1, 0, False),
            ('vivi', 'tirando_foto'): (2, 6, False),
        }
        for (cid, nome), (n, fps, loop) in esperado.items():
            self.assertEqual(len(self.t[cid][nome]), n, (cid, nome))
            self.assertEqual(animacoes.tempo(cid, nome), (fps, loop), (cid, nome))
            self.assertEqual(especiais.ESPECIAIS[cid][nome][2], 'frente', (cid, nome))

    def test_so_quem_tem(self):
        # as ações especiais ficam só na folha de quem faz
        for cid, a in self.t.items():
            extras = set(a) - set(animacoes.ANIMACOES)
            self.assertEqual(extras, set(especiais.ESPECIAIS.get(cid, {})), cid)

    def test_envelope_na_mao_andando(self):
        # 9. o envelope fica na mão nos quatro passos: o ponto de cada quadro
        # encosta na mão daquele quadro (pele a até 2 px)
        for cid in especiais.CARREGA_ENVELOPE:
            for nome in ('andando_frente', 'andando_costas'):
                marcas = animacoes.campos(cid, nome, 4)['envelope']
                self.assertEqual(len(marcas), 4, (cid, nome))
                for k, (im, p) in enumerate(zip(self.t[cid][nome], marcas)):
                    self.assertTrue(perto(tuple(p), da_mao(cid, im)), (cid, nome, k, p))
                # acompanha a mão: o ponto muda entre os quadros
                self.assertGreater(len({tuple(p) for p in marcas}), 1, (cid, nome))

    def test_envelope_sai_no_q2(self):
        # 9. a entrega: envelope na mão no Q1, solto no Q2, com a mão perto
        # do ponto em cada quadro
        for nome in ('deixando_envelope_no_malote', 'deixando_envelope_no_malote_costas'):
            c = animacoes.campos('gabriel', nome, 2)
            self.assertEqual(c['solta'], 1, nome)
            for k, (im, p) in enumerate(zip(self.t['gabriel'][nome], c['envelope'])):
                self.assertTrue(perto(tuple(p), da_mao('gabriel', im), 1), (nome, k, p))
        # de frente, a mão vai para onde o manual diz, com até 2 px de ajuste
        c = animacoes.campos('gabriel', 'deixando_envelope_no_malote', 2)
        for (x, y), (mx, my) in zip(c['envelope'], ((36, 36), (38, 42))):
            self.assertLessEqual(max(abs(x - mx), abs(y - my)), 2)

    def test_selo_dentro_da_tela_do_caio(self):
        # 10. o selo cabe na tela, sem cobrir moldura nem mão; um selo por cor
        from PIL import Image
        c = animacoes.campos('caio', 'mostrando_tablet', 1)
        x0, y0, x1, y1 = c['tela']
        im = self.t['caio']['mostrando_tablet'][0]
        branco = (0xF5, 0xF7, 0xF8)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.assertEqual(im.getpixel((x, y))[:3], branco, (x, y))
        for cor in especiais.SELOS:
            s, (ax, ay) = especiais.selo(cor)
            sx, sy = c['selo'][0] - ax, c['selo'][1] - ay
            self.assertTrue(x0 <= sx and sx + s.width - 1 <= x1 and y0 <= sy and sy + s.height - 1 <= y1, cor)
        # e a tela do Saldanha não tem selo: nenhum dos verdes do check
        for nome in especiais.ESPECIAIS['saldanha']:
            for im in self.t['saldanha'][nome]:
                for cor in especiais.VERDES:
                    self.assertFalse(pixels(im, cor), nome)

    def test_flash_so_no_q2(self):
        # 11. o flash aparece no Q2 e não fica resíduo no Q1
        q = self.t['vivi']['tirando_foto']
        clarao = especiais.flash(*especiais.FLASH)
        self.assertTrue(all(q[1].getpixel(p)[:3] == c for p, c in clarao.items()))
        self.assertFalse(any(q[0].getpixel(p)[:3] == c for p, c in clarao.items()))
        self.assertEqual(animacoes.campos('vivi', 'tirando_foto', 2)['flash_no_quadro'], 1)

    def test_sineta_vibra_no_q2(self):
        # 11. a sineta vibra no Q2 e volta ao normal: o Q1 é a parada, a base
        # não mexe e o tamanho não muda
        import office
        quadros, (ax, ay) = office.bell_ringing()
        parada, (px_, py) = office.bell()
        m = office.SINETA_MARGEM
        self.assertEqual((ax, ay), (px_ + m, py))
        q1 = quadros[0].crop((m, 0, m + parada.width, parada.height))
        self.assertEqual(q1.tobytes(), parada.tobytes())
        self.assertNotEqual(quadros[1].tobytes(), quadros[0].tobytes())
        base = (0, parada.height - 1, quadros[0].width, parada.height)
        self.assertEqual(quadros[1].crop(base).tobytes(), quadros[0].crop(base).tobytes())

    def test_relogio_do_saldanha_fica_no_braco(self):
        # 5. o smartwatch não some nem troca de braço nos gestos: fica no
        # braço da direita da tela (o de trás, de frente)
        preto = (20, 20, 22)
        for nome in ('alerta', 'apresentando_quadro', 'comemorando_tablet', 'digitando_sentado'):
            for k, im in enumerate(self.t['saldanha'][nome]):
                rel = pixels(im, preto)
                self.assertTrue(rel, (nome, k))
                self.assertTrue(all(x >= 20 for x, _ in rel), (nome, k, rel))

    def test_digitando_so_mexe_cabeca_e_maos(self):
        # 5.2: tronco e pernas parados, o tablet (objeto) não trepida
        a = self.t['saldanha']
        tampo = set()
        for im in a['digitando_sentado_tampo']:
            tampo |= pixels(im)
        q0, q1 = a['digitando_sentado']
        for y in range(PE - 12, 70):
            for x in range(40):
                if (x, y) not in tampo:
                    self.assertEqual(q0.getpixel((x, y)), q1.getpixel((x, y)), (x, y))

    def test_comemorando_tablet_no_alto(self):
        # 5.5: o tablet acima da cabeça, sem cortar: topo em y 2 no Q1 e 1 no Q2
        for k, topo in enumerate((2, 1)):
            im = self.t['saldanha']['comemorando_tablet'][k]
            self.assertEqual(im.getbbox()[1], topo, k)

    def test_rosto_das_acoes(self):
        # o "rosto" leva a pupila do parado até a pupila do quadro, para
        # piscar e falar irem no lugar certo
        for cid, nomes in especiais.ESPECIAIS.items():
            n = anim.folga(costas.HUMANOS[cid][0])
            pupila = self.t[cid]['parado_frente'][0].getpixel((19, 17 + n))
            for nome in nomes:
                marcas = animacoes.campos(cid, nome, len(self.t[cid][nome])).get('rosto')
                if not marcas:
                    continue
                for k, (im, (dx, dy)) in enumerate(zip(self.t[cid][nome], marcas)):
                    self.assertEqual(im.getpixel((19 + dx, 17 + n + dy)), pupila, (cid, nome, k))



# ------------------------------------------------------------ fase 6
class Caes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import caes
        cls.caes = caes
        cls.t = {cid: caes.quadros(cid) for cid in caes.ANIMACOES}
        cls.em_pe = {cid: caes.quadros_em_pe(cid, [{}])[0] for cid in caes.ANIMACOES}

    def test_resumo_8_2(self):
        # 13. quadros, FPS e loop como no resumo 8.2
        esperado = {('flora', 'andando'): (4, 8), ('flora', 'dormindo_na_cama'): (2, 1), ('flora', 'inquieto'): (2, 3),
                    ('lupin', 'andando'): (4, 9), ('lupin', 'dormindo_na_cama'): (2, 1), ('lupin', 'inquieto'): (2, 4)}
        for (cid, nome), (n, fps) in esperado.items():
            self.assertEqual(len(self.t[cid][nome]), n, (cid, nome))
            self.assertEqual(self.caes.ANIMACOES[cid][nome], (fps, True), (cid, nome))

    def test_em_pe_e_o_desenho_original(self):
        # gravado e remontado sem mexer, é o em pé do assets/, pixel a pixel
        import office
        for cid, (fn, k) in self.caes.DESENHO.items():
            self.assertEqual(self.em_pe[cid].tobytes(), office.dog(fn(k, 'em_pe')).tobytes(), cid)

    def test_mesma_tela_e_mesmo_chao(self):
        # 2. todos na tela do em pé, pisando na linha dele
        for cid, a in self.t.items():
            ref = self.em_pe[cid]
            for nome, qs in a.items():
                for k, im in enumerate(qs):
                    self.assertEqual(im.size, ref.size, (cid, nome, k))
                    self.assertEqual(im.getbbox()[3], ref.getbbox()[3], (cid, nome, k))
                    alfas = set(im.getchannel('A').getdata())
                    self.assertLessEqual(alfas, {0, 255}, (cid, nome, k))

    def test_paleta_dos_caes(self):
        # 12. andar, dormir e ficar inquieto usam só as cores do em pé e do
        # sentado de cada um
        import office
        for cid, a in self.t.items():
            fn, k = self.caes.DESENHO[cid]
            base = {c[:3] for im in (self.em_pe[cid], office.dog(fn(k))) for c in im.getdata() if c[3]}
            for nome, qs in a.items():
                for q, im in enumerate(qs):
                    self.assertFalse({c[:3] for c in im.getdata() if c[3]} - base, (cid, nome, q))

    def test_tamanho_relativo(self):
        # 12. a Flora continua maior que o Lupin, em pé, andando e deitada
        for nome in ('andando', 'dormindo_na_cama', 'inquieto'):
            for k in range(len(self.t['flora'][nome])):
                f, l = self.t['flora'][nome][k].getbbox(), self.t['lupin'][nome][k].getbbox()
                self.assertGreater(f[2] - f[0], l[2] - l[0], (nome, k))
                self.assertGreater(f[3] - f[1], l[3] - l[1], (nome, k))
        # andando, a altura muda no máximo 1 px (o corpo sobe na passagem)
        for cid, a in self.t.items():
            h0 = self.em_pe[cid].getbbox()
            for im in a['andando']:
                self.assertLessEqual(abs((im.getbbox()[3] - im.getbbox()[1]) - (h0[3] - h0[1])), 1, cid)

    def test_caracteristicas(self):
        # 12. a coleira vermelha da Flora e a barba caramelo do Lupin em
        # todos os quadros, inclusive deitados
        vermelho = {(0xD7, 0x35, 0x2E), (0xEF, 0x5A, 0x50)}
        caramelo = {(0x70, 0x46, 0x2A), (0x94, 0x60, 0x3A)}
        for cid, cores in (('flora', vermelho), ('lupin', caramelo)):
            for nome, qs in self.t[cid].items():
                for k, im in enumerate(qs):
                    self.assertTrue(any(pixels(im, c) for c in cores), (cid, nome, k))

    def test_andando_quatro_poses(self):
        # 6. quatro poses distintas; nos contatos o corpo está no lugar do em pé
        for cid, a in self.t.items():
            q = a['andando']
            self.assertEqual(len({im.tobytes() for im in q}), 4, cid)
            topo = [im.getbbox()[1] for im in q]
            self.assertEqual(topo[0], self.em_pe[cid].getbbox()[1], cid)
            self.assertEqual(topo[0], topo[2], cid)

    def test_dormindo_de_olhos_fechados(self):
        # 12. deitado, nada dos olhos abertos (íris e brilho) aparece
        olhos = {'flora': {(0x5A, 0x2E, 0x14), (0x8C, 0x4E, 0x24), (255, 255, 255)},
                 'lupin': {(0x5E, 0x32, 0x16), (255, 255, 255)}}
        for cid, a in self.t.items():
            for k, im in enumerate(a['dormindo_na_cama']):
                cores = {im.getpixel(p)[:3] for p in pixels(im)}
                self.assertFalse(cores & olhos[cid], (cid, k))
            # e em pé eles estavam lá
            cores = {self.em_pe[cid].getpixel(p)[:3] for p in pixels(self.em_pe[cid])}
            self.assertTrue(cores & olhos[cid], cid)

    def test_dormindo_so_respira(self):
        # 6.2 e 6.5: no Q2 só as costas sobem 1 px; o que muda fica na
        # metade de cima do corpo, e a cabeça não mexe
        for cid, a in self.t.items():
            q1, q2 = a['dormindo_na_cama']
            dif = [(x, y) for y in range(q1.height) for x in range(q1.width) if q1.getpixel((x, y)) != q2.getpixel((x, y))]
            self.assertTrue(dif, cid)
            ops, _ = self.caes.gravar_deitado(cid)
            cab = set()
            for o in ops:
                if o[2] == 'cabeca':
                    cab |= set(o[1])
            self.assertFalse(set(dif) & cab - {p for p in cab if q1.getpixel(p) == q2.getpixel(p)}, cid)
            self.assertEqual(q2.getbbox()[1], q1.getbbox()[1] - (1 if q1.getbbox()[1] > q2.getbbox()[1] else 0), cid)

    def test_inquieto_comeca_no_em_pe(self):
        # 6.3 e 6.6: Q1 é o em pé; no Q2 a cabeça sobe
        for cid, a in self.t.items():
            q1, q2 = a['inquieto']
            self.assertEqual(q1.tobytes(), self.em_pe[cid].tobytes(), cid)
            self.assertLess(q2.getbbox()[1], q1.getbbox()[1], cid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
