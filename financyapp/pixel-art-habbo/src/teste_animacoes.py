"""Testes do manual de animações (§9.2) que valem para o que já existe,
para os 12 humanos.

    python3 src/teste_animacoes.py
"""
import unittest

import anim
import animacoes
import costas
from anim import PE    # a linha do chão, a âncora (o bbox termina aqui)

CACHE = {}
CAMADAS = {n for n in animacoes.ANIMACOES if n.endswith('_tampo')} | set(animacoes.SOBREPOSICOES)


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
            self.assertEqual(list(a), list(animacoes.ANIMACOES), cid)

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
                    self.assertTrue(x0 > 0 and y0 > 0 and x1 <= 40, (cid, nome, i))

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
            for nome in ['sentado_frente', 'andando_frente'] + animacoes.ESCRITORIO:
                marcas = animacoes.campos(cid, nome, len(a[nome]))['rosto']
                for k, (im, (dx, dy)) in enumerate(zip(a[nome], marcas)):
                    if nome == 'olhando_para_o_lado_frente' and k in (1, 2):
                        continue
                    self.assertEqual(im.getpixel((19 + dx, 17 + n + dy)), pupila, (cid, nome, k))


if __name__ == '__main__':
    unittest.main(verbosity=2)
