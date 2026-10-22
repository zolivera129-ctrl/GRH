"""Testes do manual de animações (§9.2) que valem para o que já existe,
para os 12 humanos, e os das ações especiais (itens 9 a 11).

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
