"""Baixa do eventface as fotos de cada premiado e organiza em Finais\\CEOs e Finais\\RHs.

Para cada pessoa de pessoas.csv:
  1. acha a foto dela nas pastas de origem (CEOs, RHs...) pelo nome;
  2. manda essa foto para a busca por selfie do evento (a mesma do botão "Enviar selfie");
  3. baixa cada foto encontrada para Finais\\<categoria>\\<nome da pessoa>.

É o que o "Baixar todas as fotos" faz depois da selfie, só que direto na pasta, sem zip.

Uso (de dentro da pasta OneDrive_1_19-10-2026):
    py baixar_fotos.py --conferir             só confere a foto de cada pessoa, sem ir ao site
    py baixar_fotos.py --so "Andrea Krewer"   testa com uma pessoa
    py baixar_fotos.py                        roda a lista toda (quem já tem pasta é pulado)
"""

import argparse
import csv
import io
import json
import mimetypes
import re
import time
import unicodedata
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

EVENTO = "https://www.eventface.com.br/evento-v3/WO17616LYTGN"
AQUI = Path(__file__).resolve().parent
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}
IGNORAR = {"da", "de", "do", "das", "dos", "e"}
NAVEGADOR = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) fotos-eventface"


# ---------------------------------------------------------------- pessoas e fotos

@dataclass
class Pessoa:
    categoria: str
    nome: str
    premio: str = ""
    foto: Path | None = None
    conferir: bool = False

    @property
    def pasta(self):
        return re.sub(r'[<>:"/\\|?*]', "", self.nome).strip(" .")


def tokens(texto):
    texto = re.sub(r"\(.*?\)", " ", texto)
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return [t for t in re.split(r"[^a-z0-9]+", texto) if t and t not in IGNORAR]


def apelidos(nome):
    return [t for trecho in re.findall(r"\((.*?)\)", nome) for t in tokens(trecho)]


def parecido(a, b):
    if a == b:
        return True
    return min(len(a), len(b)) > 3 and SequenceMatcher(None, a, b).ratio() >= 0.85


def pontuar(nome, arquivo):
    """Quanto o nome do arquivo bate com o nome da pessoa: (pontos, certeza) ou None."""
    pessoa, arq = tokens(nome), tokens(arquivo)
    if not pessoa or not arq:
        return None
    tem = lambda t: any(parecido(t, x) for x in arq)
    primeiro = tem(pessoa[0]) or any(tem(a) for a in apelidos(nome))
    achados = sum(tem(t) for t in pessoa)
    if len(pessoa) == 1:
        return (1.0, True) if primeiro else None
    if primeiro and tem(pessoa[-1]):
        return achados / len(pessoa), True
    # sem o sobrenome final: só serve se o resto bater bem, e fica marcado para conferir
    if (primeiro and achados >= 2) or (not primeiro and achados == len(pessoa) - 1 >= 2):
        return achados / len(pessoa) - 0.5, False
    return None


def listar_fotos(base, excluir):
    fotos = []
    for p in base.rglob("*"):
        if p.suffix.lower() in EXTENSOES and p.is_file():
            if not any(e == p or e in p.parents for e in excluir):
                fotos.append(p)
    return fotos


def achar_foto(pessoa, fotos):
    melhor = None
    for f in fotos:
        r = pontuar(pessoa.nome, f.stem)
        if r is None:
            continue
        chave = (r[1], r[0], f.stat().st_size)
        if melhor is None or chave > melhor[0]:
            melhor = (chave, f)
    if melhor:
        pessoa.foto, pessoa.conferir = melhor[1], not melhor[0][0]


def ler_pessoas(caminho, base):
    for codificacao in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texto = caminho.read_text(encoding=codificacao)
            break
        except UnicodeDecodeError:
            continue
    separador = ";" if texto.splitlines()[0].count(";") >= texto.splitlines()[0].count(",") else ","
    pessoas = []
    for linha in csv.DictReader(texto.splitlines(), delimiter=separador):
        linha = {(k or "").strip().lower(): (v or "").strip() for k, v in linha.items()}
        if not linha.get("nome"):
            continue
        p = Pessoa(linha.get("categoria") or "Outros", linha["nome"], linha.get("premio", ""))
        if linha.get("foto"):
            foto = Path(linha["foto"])
            p.foto = foto if foto.is_absolute() else base / foto
        pessoas.append(p)
    return pessoas


# ---------------------------------------------------------------- eventface

class ErroBusca(Exception):
    pass


def pedir(url, dados=None, cabecalhos=None, tentativas=5):
    """GET ou POST com novas tentativas quando a conexão cai."""
    req = urllib.request.Request(url, data=dados, headers={"User-Agent": NAVEGADOR, **(cabecalhos or {})})
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500:
                corpo = e.read()
                try:
                    raise ErroBusca(json.loads(corpo).get("error") or f"HTTP {e.code}")
                except ValueError:
                    raise ErroBusca(f"HTTP {e.code}")
            erro = e
        except (urllib.error.URLError, OSError) as e:
            erro = e
        time.sleep(2 ** tentativa)
    raise ErroBusca(f"sem conexão com o eventface ({erro})")


def preparar_selfie(foto):
    """Como o site: JPEG de até 1280 px. Fundo transparente vira branco."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return foto.read_bytes(), mimetypes.guess_type(foto.name)[0] or "image/jpeg"
    with Image.open(foto) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            fundo = Image.new("RGB", img.size, "white")
            fundo.paste(img, mask=img.getchannel("A"))
            img = fundo
        img = img.convert("RGB")
        img.thumbnail((1280, 1280))
        saida = io.BytesIO()
        img.save(saida, "JPEG", quality=85)
        return saida.getvalue(), "image/jpeg"


def buscar_fotos(evento, foto):
    """Manda a selfie e devolve a lista de fotos do evento em que a pessoa aparece."""
    conteudo, tipo = preparar_selfie(foto)
    limite = uuid.uuid4().hex
    corpo = (f'--{limite}\r\nContent-Disposition: form-data; name="selfie"; filename="selfie.jpg"\r\n'
             f"Content-Type: {tipo}\r\n\r\n").encode() + conteudo + f"\r\n--{limite}--\r\n".encode()
    d = json.loads(pedir(f"{evento}/search", corpo,
                         {"Content-Type": f"multipart/form-data; boundary={limite}"}))
    # a busca roda em segundo plano: consulta até terminar, como a página faz
    for tentativa in range(90):
        if d.get("status") == "completed":
            return d.get("photos") or []
        if d.get("status") == "failed":
            raise ErroBusca(d.get("error") or "falha na busca")
        if not d.get("task_id"):
            raise ErroBusca(f"resposta inesperada do eventface: {d}")
        time.sleep(0.6 if tentativa < 6 else 1 if tentativa < 12 else 2)
        tarefa = d["task_id"]
        d = json.loads(pedir(f"{evento}/search/{tarefa}"))
        d.setdefault("task_id", tarefa)
    raise ErroBusca("a busca demorou demais")


def nome_arquivo(foto, repetidos):
    nome = re.sub(r'[<>:"/\\|?*]', "_", foto.get("filename") or "").strip(" .")
    if not nome:
        nome = f"foto_{foto['id']}.jpg"
    if nome.lower() in repetidos:
        nome = f"{foto['id']}_{nome}"
    return nome


def baixar_fotos(evento, fotos, pasta):
    """Baixa para `pasta` o que ainda não está lá. Devolve quantas falharam."""
    raiz = evento.split("/evento-v3/")[0]
    nomes = [f.get("filename", "").lower() for f in fotos]
    repetidos = {n for n in nomes if nomes.count(n) > 1}
    pasta.mkdir(parents=True, exist_ok=True)

    def uma(foto):
        alvo = pasta / nome_arquivo(foto, repetidos)
        if alvo.exists():
            return True
        try:
            dados = pedir(raiz + foto["url"])
        except ErroBusca:
            return False
        parcial = alvo.with_name(alvo.name + ".part")
        parcial.write_bytes(dados)
        parcial.replace(alvo)
        return True

    falhas = 0
    with ThreadPoolExecutor(4) as pool:
        for i, ok in enumerate(pool.map(uma, fotos), 1):
            falhas += not ok
            print(f"\r   baixando {i}/{len(fotos)}", end="", flush=True)
    print()
    return falhas


def guardar(provisoria, destino):
    """Só põe a pasta no lugar definitivo quando todas as fotos chegaram."""
    if destino.is_dir():
        for f in provisoria.iterdir():
            f.replace(destino / f.name)
        provisoria.rmdir()
    else:
        provisoria.rename(destino)


def processar(p, destino, args):
    """Busca e baixa as fotos de uma pessoa. Devolve [situação, nº de fotos]."""
    fotos = buscar_fotos(args.evento, p.foto)
    log(f"   {len(fotos)} foto(s) encontrada(s)")
    if not fotos:
        return ["nenhuma foto no evento", 0]
    if len(fotos) > args.limite:
        log(f"   >> {len(fotos)} fotos é muito para uma pessoa; não baixei (use --limite para liberar)")
        return ["verificar", len(fotos)]
    provisoria = destino.with_name(destino.name + " (baixando)")
    falhas = baixar_fotos(args.evento, fotos, provisoria)
    if falhas:
        log(f"   >> {falhas} foto(s) não baixaram; rode de novo para completar")
        return ["incompleto", len(fotos) - falhas]
    guardar(provisoria, destino)
    log(f"   ok: {destino}")
    return ["ok", len(fotos)]


# ---------------------------------------------------------------- principal

def log(texto=""):
    print(texto, flush=True)


def escrever_relatorio(caminho, linhas):
    try:
        with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["categoria", "nome", "foto usada", "situacao", "fotos", "pasta"])
            w.writerows(linhas.values())
    except PermissionError:
        log(f"   (não consegui salvar {caminho.name}: ele está aberto no Excel?)")


def achar_base(pedida):
    if pedida:
        return Path(pedida).expanduser().resolve()
    for candidata in (AQUI, AQUI.parent, Path.cwd()):
        if (candidata / "Finais").is_dir():
            return candidata
    log("Não achei a pasta Finais aqui do lado.")
    caminho = input("Arraste a pasta OneDrive_1_19-10-2026 para esta janela e aperte Enter: ")
    return Path(caminho.strip().strip('"')).expanduser().resolve()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conferir", action="store_true", help="só mostra a foto achada para cada pessoa")
    ap.add_argument("--so", action="append", default=[], metavar="NOME", help="roda só quem tem esse nome (pode repetir)")
    ap.add_argument("--categoria", help="roda só CEOs ou só RHs")
    ap.add_argument("--refazer", action="store_true", help="busca de novo mesmo se a pasta da pessoa já tem fotos")
    ap.add_argument("--pasta", help="pasta que tem Finais (padrão: a pasta do script ou a de cima)")
    ap.add_argument("--lista", default=str(AQUI / "pessoas.csv"), help="lista de pessoas (padrão: pessoas.csv)")
    ap.add_argument("--evento", default=EVENTO, help="endereço do evento no eventface")
    ap.add_argument("--limite", type=int, default=400, help="acima disso de fotos para uma pessoa, não baixa")
    ap.add_argument("--sem-pausa", action="store_true", help="não espera Enter para começar")
    args = ap.parse_args()
    args.evento = args.evento.rstrip("/").replace("/evento/", "/evento-v3/")

    base = achar_base(args.pasta)
    finais = base / "Finais"
    pessoas = ler_pessoas(Path(args.lista), base)
    if args.categoria:
        pessoas = [p for p in pessoas if p.categoria.lower() == args.categoria.lower()]
    if args.so:
        filtros = [" ".join(tokens(s)) for s in args.so]
        pessoas = [p for p in pessoas if any(f in " ".join(tokens(p.nome)) for f in filtros)]
    if not pessoas:
        raise SystemExit("Nenhuma pessoa da lista bateu com o filtro.")

    fotos = listar_fotos(base, [finais] + ([AQUI] if AQUI != base else []))
    for p in pessoas:
        if not p.foto:
            achar_foto(p, fotos)

    log(f"Pasta: {base}")
    log(f"{len(fotos)} fotos de referência encontradas, {len(pessoas)} pessoas na lista.\n")
    for p in pessoas:
        if p.foto and p.foto.exists():
            marca = "  <- confira" if p.conferir else ""
            log(f"  {p.categoria:5} {p.nome:38} {p.foto.relative_to(base) if base in p.foto.parents else p.foto}{marca}")
        else:
            log(f"  {p.categoria:5} {p.nome:38} SEM FOTO")
    sem_foto = [p for p in pessoas if not (p.foto and p.foto.exists())]
    if sem_foto:
        log(f"\n{len(sem_foto)} sem foto: renomeie a foto com o nome da pessoa ou preencha a coluna 'foto' do pessoas.csv.")
    if args.conferir:
        return

    relatorio = base / "relatorio-eventface.csv"
    linhas = {}
    fila = [p for p in pessoas if p not in sem_foto]
    for p in sem_foto:
        linhas[p.nome] = [p.categoria, p.nome, "", "sem foto de referência", 0, ""]
    if not args.sem_pausa:
        input(f"\nVou buscar {len(fila)} pessoas. Aperte Enter para começar (Ctrl+C para parar a qualquer momento)...")

    try:
        for i, p in enumerate(fila, 1):
            destino = finais / p.categoria / p.pasta
            linha = [p.categoria, p.nome, p.foto.name, "", 0, str(destino.relative_to(base))]
            linhas[p.nome] = linha
            log(f"\n[{i}/{len(fila)}] {p.nome} ({p.categoria})")
            if destino.is_dir() and any(destino.iterdir()) and not args.refazer:
                linha[3:5] = ["já tinha fotos", sum(1 for f in destino.iterdir() if f.is_file())]
                log("   a pasta já tem fotos, pulei (use --refazer para buscar de novo)")
            else:
                try:
                    linha[3:5] = processar(p, destino, args)
                except Exception as e:  # uma pessoa com problema não para a lista
                    linha[3] = f"erro: {e}"
                    log(f"   erro: {e}")
                time.sleep(1)
            escrever_relatorio(relatorio, linhas)
    except KeyboardInterrupt:
        log("\nParado por você. Rode de novo para continuar de onde parou.")
    finally:
        escrever_relatorio(relatorio, linhas)

    contagem = {}
    for linha in linhas.values():
        situacao = linha[3].split(":")[0] or "não rodou"
        contagem[situacao] = contagem.get(situacao, 0) + 1
    log("\nResumo: " + ", ".join(f"{v} {k}" for k, v in contagem.items()))
    log(f"Relatório: {relatorio}")


if __name__ == "__main__":
    main()
