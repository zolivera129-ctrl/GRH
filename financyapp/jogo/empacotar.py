"""Monta o pacote da página para publicar como Artifact no claude.ai.

Uso: python3 empacotar.py  (gera ./pacote/, que fica fora do git)

O Artifact serve só os arquivos publicados junto com a página, então o
pacote leva a página, o estilo, os scripts, os assets, o roteiro de falas e o
layout da planta,
com os caminhos dos dados trocados para dentro do pacote. A página publicada
não leva doctype, head nem body: o Artifact põe esse esqueleto na hora.
"""
import re
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
PACOTE = AQUI / 'pacote'
LAYOUT = RAIZ / 'docs' / 'FinancyApp_Layout_12x10_v1.json'
ASSETS = RAIZ / 'pixel-art-habbo' / 'assets'


def pagina():
    html = (AQUI / 'index.html').read_text(encoding='utf-8')
    head = re.search(r'<head>(.*)</head>', html, re.S).group(1)
    body = re.search(r'<body>(.*)</body>', html, re.S).group(1)
    # o esqueleto do Artifact já traz o charset e o viewport
    head = re.sub(r'\s*<meta (charset|name="viewport")[^>]*>', '', head)
    body = body.replace('data-assets="../pixel-art-habbo/assets/"', 'data-assets="assets/"')
    body = body.replace('data-layout="../docs/FinancyApp_Layout_12x10_v1.json"',
                        f'data-layout="dados/{LAYOUT.name}"')
    assert 'data-assets="assets/"' in body and 'data-layout="dados/' in body
    assert 'data-roteiro="dados/financyapp_roteiro_falas_v03.json"' in body
    return head.strip() + '\n' + body.strip() + '\n'


def main():
    shutil.rmtree(PACOTE, ignore_errors=True)
    PACOTE.mkdir()
    (PACOTE / 'index.html').write_text(pagina(), encoding='utf-8')
    shutil.copy(AQUI / 'estilo.css', PACOTE / 'estilo.css')
    shutil.copytree(AQUI / 'src', PACOTE / 'src')
    shutil.copytree(ASSETS, PACOTE / 'assets')
    # o roteiro de falas (dados/) e o layout da planta
    shutil.copytree(AQUI / 'dados', PACOTE / 'dados')
    shutil.copy(LAYOUT, PACOTE / 'dados' / LAYOUT.name)
    arquivos = sorted(p.relative_to(PACOTE).as_posix() for p in PACOTE.rglob('*')
                      if p.is_file() and p.name != 'index.html')
    print(f'{len(arquivos)} arquivos além da página em {PACOTE}')


if __name__ == '__main__':
    main()
