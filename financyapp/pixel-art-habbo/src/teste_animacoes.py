"""Testes do manual de animações (§9.2) que valem para o que já existe.

    python3 src/teste_animacoes.py
"""
import unittest

import previa_animacoes

from anim import PE    # a linha do chão, a âncora (o bbox termina aqui)


def opacos(im):
    return {(x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3]}


class Guilherme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = previa_animacoes.quadros_guilherme()

    def test_tela_40x70_sem_meio_tom(self):
        # 1. 40 × 70, pixels inteiros e transparência sem meio-termo
        for nome, quadros in self.a.items():
            for im in quadros:
                self.assertEqual(im.size, (40, 70), nome)
                alfas = {im.getpixel((x, y))[3] for x in range(40) for y in range(70)}
                self.assertLessEqual(alfas, {0, 255}, nome)

    def test_ancora_no_chao(self):
        # 2. a âncora não mexe: nas poses e nos contatos, o pé da frente
        # pisa na linha da âncora. No Q2 o pé da frente está no ar e o de
        # trás, plantado, fica 1 px acima (é a profundidade); no Q4 o da
        # frente volta a pisar.
        for nome, quadros in self.a.items():
            for i, im in enumerate(quadros):
                esperado = PE - 1 if nome.startswith('andando') and i == 1 else PE
                self.assertEqual(im.getbbox()[3], esperado, (nome, i))

    def test_pe_plantado_nao_mexe(self):
        # o pé que fica no chão na passagem é o mesmo do parado, pixel por
        # pixel (de frente o pé de trás é o da direita; de costas, o da esquerda)
        dir_, esq = (22, PE - 6, 30, PE), (11, PE - 5, 19, PE)
        casos = (('parado_frente', 'andando_frente', 1, dir_), ('parado_frente', 'andando_frente', 3, esq),
                 ('parado_costas', 'andando_costas', 1, esq), ('parado_costas', 'andando_costas', 3, dir_))
        for parado, ciclo, i, caixa in casos:
            self.assertEqual(self.a[ciclo][i].crop(caixa).tobytes(),
                             self.a[parado][0].crop(caixa).tobytes(), (ciclo, i))

    def test_nada_vaza_da_tela(self):
        for nome, quadros in self.a.items():
            for i, im in enumerate(quadros):
                x0, y0, x1, y1 = im.getbbox()
                self.assertTrue(x0 > 0 and y0 > 0 and x1 < 40, (nome, i))

    def test_caminhada_quatro_poses_distintas(self):
        # 6. quatro poses visualmente distintas
        for nome in ('andando_frente', 'andando_costas'):
            self.assertEqual(len(self.a[nome]), 4)
            self.assertEqual(len({im.tobytes() for im in self.a[nome]}), 4, nome)

    def test_caminhada_corpo_sobe_so_nas_passagens(self):
        # o topo da cabeça sobe 1 px em Q2 e Q4 e volta em Q1 e Q3 (loop sem salto)
        for nome in ('andando_frente', 'andando_costas'):
            topo = [im.getbbox()[1] for im in self.a[nome]]
            self.assertEqual(topo[0], topo[2], nome)
            self.assertEqual(topo[1], topo[3], nome)
            self.assertEqual(topo[0] - topo[1], 1, nome)

    def test_parado_e_contato_tem_a_mesma_cabeca(self):
        # a cabeça do contato é a do parado: só pernas e braços mexem
        for parado, ciclo in (('parado_frente', 'andando_frente'), ('parado_costas', 'andando_costas')):
            p = self.a[parado][0].crop((0, 0, 40, 29)).tobytes()
            for i in (0, 2):
                self.assertEqual(self.a[ciclo][i].crop((0, 0, 40, 29)).tobytes(), p, (ciclo, i))

    def test_sentado_de_costas_no_mesmo_assento(self):
        # 3. sentado de costas com o mesmo quadril e os mesmos pés do de frente
        f, c = self.a['sentado_frente'][0], self.a['sentado_costas'][0]
        self.assertEqual(f.getbbox()[3], c.getbbox()[3])
        self.assertEqual(f.crop((0, 56, 40, 70)).tobytes(), c.crop((0, 56, 40, 70)).tobytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
