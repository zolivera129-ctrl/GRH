"""Baixa do eventface as fotos de cada premiado e organiza em Finais\\CEOs e Finais\\RHs.

Para cada pessoa de pessoas.csv:
  1. acha a foto dela nas pastas de origem (CEOs, RHs...) pelo nome;
  2. abre o evento no eventface, clica em "Enviar selfie" e envia essa foto;
  3. clica em "Baixar todas as fotos" e espera o download;
  4. descompacta em Finais\\<categoria>\\<nome da pessoa>.

Quando o site pede algo que o script não sabe fazer, ele avisa no console e
espera você clicar na janela do navegador. A foto da pessoa é escolhida sozinha
sempre que o site abre a janela de "escolher arquivo".

Uso (de dentro da pasta OneDrive_1_19-10-2026):
    py baixar_fotos.py --conferir             só confere quem tem foto, sem abrir o site
    py baixar_fotos.py --so "Andrea Krewer"   testa com uma pessoa
    py baixar_fotos.py                        roda a lista toda (quem já tem pasta é pulado)
"""

import argparse
import csv
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
import zipfile
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

EVENTO_URL = "https://www.eventface.com.br/evento/WO17616LYTGN"
AQUI = Path(__file__).resolve().parent
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp"}
IGNORAR = {"da", "de", "do", "das", "dos", "e"}

TXT_SELFIE = r"enviar\s*selfie"
TXT_ESCOLHER = (r"(selecionar|escolher|enviar|carregar|upload|buscar).{0,25}(foto|arquivo|imagem)"
                r"|galeria|do computador|meus arquivos")
TXT_BAIXAR = r"baixar\s+todas"
TXT_NENHUMA = (r"nenhuma\s+foto|n[aã]o\s+(encontramos|foram\s+encontradas|h[aá]\s+fotos)"
               r"|\b0\s+fotos?\s+encontrad")
TXT_AVISO = r"^\s*(aceitar(\s+todos)?(\s+os\s+cookies)?|aceito|concordo|entendi|ok)\s*$"


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


# ---------------------------------------------------------------- console

def enter_apertado():
    if os.name == "nt":
        import msvcrt
        apertou = False
        while msvcrt.kbhit():
            apertou |= msvcrt.getwch() in "\r\n"
        return apertou
    import select
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline() != ""
    return False


def perguntar(texto, opcoes="sn"):
    while True:
        r = input(f"{texto} [{'/'.join(opcoes)}] ").strip().lower()[:1]
        if r in opcoes:
            return r


def log(texto=""):
    print(texto, flush=True)


# ---------------------------------------------------------------- navegador

class Navegador:
    def __init__(self, pw, args):
        perfil = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "eventface-perfil"
        opcoes = dict(headless=args.headless, accept_downloads=True, no_viewport=True,
                      args=["--start-maximized"])
        canais = [args.navegador] if args.navegador else ["msedge", "chrome", "chromium"]
        erro = None
        for canal in canais:
            try:
                if args.executavel:
                    opcoes["executable_path"] = args.executavel
                elif canal != "chromium":
                    opcoes["channel"] = canal
                self.ctx = pw.chromium.launch_persistent_context(str(perfil), **opcoes)
                break
            except Exception as e:  # tenta o próximo navegador
                erro = e
                opcoes.pop("channel", None)
        else:
            raise SystemExit(f"Não consegui abrir o navegador: {erro}\n"
                             "Rode:  py -m playwright install chromium   e tente de novo.")
        self.foto = None
        self.envios = 0
        self.downloads = []
        self.ultimo_clique = None
        self.botao_do_topo = None  # o "Baixar todas as fotos" de cima baixa só as fotos da pessoa?
        for p in self.ctx.pages:
            self._ligar(p)
        self.ctx.on("page", self._ligar)
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()

    def _ligar(self, page):
        page.on("download", self._baixou)
        page.on("filechooser", self._escolher_arquivo)

    def _baixou(self, download):
        self.downloads.append(download)

    def _escolher_arquivo(self, chooser):
        if self.foto:
            chooser.set_files(str(self.foto))
            self.envios += 1
            log(f"   enviei a foto {self.foto.name}")

    def esperar(self, condicao, segundos):
        fim = time.time() + segundos
        while time.time() < fim:
            if condicao():
                return True
            self.page.wait_for_timeout(300)
        return condicao()

    def visiveis(self, padrao):
        achados = []
        for frame in self.page.frames:
            for loc in frame.get_by_text(re.compile(padrao, re.I)).all():
                try:
                    if loc.is_visible():
                        achados.append(loc)
                except Exception:
                    pass
        return achados

    def clicar(self, padrao, ultimo=False):
        alvos = self.visiveis(padrao)
        for alvo in (reversed(alvos) if ultimo else alvos):
            try:
                alvo.click(timeout=5000)
                return True
            except Exception:
                continue
        return False

    def fechar_avisos(self):
        for alvo in self.visiveis(TXT_AVISO):
            try:
                alvo.click(timeout=2000)
            except Exception:
                pass

    def abrir_evento(self, url):
        for aba in self.ctx.pages:
            if aba != self.page:
                aba.close()
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        self.fechar_avisos()


def enviar_selfie(nav, foto):
    nav.foto = foto
    antes = nav.envios
    enviou = lambda: nav.envios > antes
    if nav.clicar(TXT_SELFIE) and nav.esperar(enviou, 8):
        return True
    # a selfie pode abrir uma janelinha com outro botão ou com uma caixa de concordância
    janela = ":is([role=dialog], dialog, [aria-modal=true], .modal) input[type=checkbox]:visible"
    for frame in nav.page.frames:
        for caixa in frame.locator(janela).all():
            try:
                if not caixa.is_checked():
                    caixa.check(timeout=2000)
                    log("   marquei a caixa de concordância da janela da selfie")
            except Exception:
                pass
    if nav.clicar(TXT_ESCOLHER) and nav.esperar(enviou, 8):
        return True
    for frame in nav.page.frames:
        campos = frame.locator("input[type=file]")
        if campos.count():
            campos.last.set_input_files(str(foto))
            nav.envios += 1
            log(f"   enviei a foto {foto.name}")
            return True
    log("   >> Não achei onde enviar a selfie. Faça o envio na janela do navegador:")
    log("      a foto é escolhida sozinha quando a janela de arquivos abrir. (Enter pula a pessoa)")
    while not enviou():
        nav.page.wait_for_timeout(300)
        if enter_apertado():
            return False
    return True


def esperar_resultado(nav, botoes_antes, segundos=30):
    """'novo' se apareceu um botão de baixar para o resultado, 'nenhuma' se o site diz
    que não achou fotos, 'mesmo' se a página só filtrou a galeria."""
    try:
        nav.page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    fim = time.time() + segundos
    while time.time() < fim:
        nav.page = nav.ctx.pages[-1]  # o resultado pode abrir em outra aba
        if nav.visiveis(TXT_NENHUMA):
            return "nenhuma"
        if len(nav.visiveis(TXT_BAIXAR)) > botoes_antes:
            return "novo"
        nav.page.wait_for_timeout(500)
    return "mesmo"


def esperar_downloads(nav, aviso_em=25, silencio=6):
    """Espera o primeiro download e junta os que vierem em seguida. Enter desiste."""
    inicio = time.time()
    avisou = False
    while not nav.downloads:
        nav.page.wait_for_timeout(500)
        if not avisou and time.time() - inicio > aviso_em:
            log("   >> Ainda esperando o download. Se o site pedir alguma confirmação,")
            log("      termine na janela do navegador. (Enter pula a pessoa)")
            avisou = True
        if enter_apertado():
            return []
    ultimo = time.time()
    vistos = len(nav.downloads)
    while time.time() - ultimo < silencio:
        nav.page.wait_for_timeout(500)
        if len(nav.downloads) != vistos:
            vistos, ultimo = len(nav.downloads), time.time()
    baixados, nav.downloads = nav.downloads, []
    return baixados


# ---------------------------------------------------------------- arquivos

def eh_imagem(nome):
    return Path(nome).suffix.lower() in EXTENSOES | {".heic", ".tif", ".tiff"}


def contar_fotos(arquivos):
    total = 0
    for arq in arquivos:
        if zipfile.is_zipfile(arq):
            with zipfile.ZipFile(arq) as z:
                total += sum(1 for m in z.infolist() if not m.is_dir() and eh_imagem(m.filename))
        elif eh_imagem(arq.name):
            total += 1
    return total


def extrair(zip_path, destino):
    with zipfile.ZipFile(zip_path) as z:
        membros = [m for m in z.infolist()
                   if not m.is_dir() and not m.filename.startswith("__MACOSX")]
        partes = [Path(m.filename).parts for m in membros]
        # se tudo está dentro de uma pasta só, tira essa pasta do caminho
        corta = 1 if partes and all(len(p) > 1 and p[0] == partes[0][0] for p in partes) else 0
        raiz = destino.resolve()
        for m, p in zip(membros, partes):
            alvo = (destino.joinpath(*p[corta:])).resolve()
            if raiz not in alvo.parents:
                continue
            alvo.parent.mkdir(parents=True, exist_ok=True)
            with z.open(m) as origem, open(alvo, "wb") as saida:
                shutil.copyfileobj(origem, saida)


def guardar(arquivos, destino):
    destino.mkdir(parents=True, exist_ok=True)
    for arq in arquivos:
        if zipfile.is_zipfile(arq):
            extrair(arq, destino)
            arq.unlink()
        else:
            shutil.move(str(arq), str(destino / arq.name))
    return sum(1 for f in destino.rglob("*") if f.is_file())


def escrever_relatorio(caminho, linhas):
    try:
        with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["categoria", "nome", "foto usada", "situacao", "fotos", "pasta"])
            w.writerows(linhas.values())
    except PermissionError:
        log(f"   (não consegui salvar {caminho.name}: ele está aberto no Excel?)")


# ---------------------------------------------------------------- principal

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
    ap.add_argument("--refazer", action="store_true", help="baixa de novo mesmo se a pasta da pessoa já tem fotos")
    ap.add_argument("--pasta", help="pasta que tem Finais (padrão: a pasta do script ou a de cima)")
    ap.add_argument("--lista", default=str(AQUI / "pessoas.csv"), help="lista de pessoas (padrão: pessoas.csv)")
    ap.add_argument("--url", default=EVENTO_URL, help="endereço do evento no eventface")
    ap.add_argument("--limite", type=int, default=400, help="acima disso o zip parece ser do evento inteiro e eu pergunto antes")
    ap.add_argument("--navegador", choices=["msedge", "chrome", "chromium"], help="padrão: Edge, depois Chrome")
    ap.add_argument("--executavel", help=argparse.SUPPRESS)
    ap.add_argument("--headless", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    base = achar_base(args.pasta)
    finais = base / "Finais"
    trabalho = base / "_eventface"
    pessoas = ler_pessoas(Path(args.lista), base)
    if args.categoria:
        pessoas = [p for p in pessoas if p.categoria.lower() == args.categoria.lower()]
    if args.so:
        filtros = [" ".join(tokens(s)) for s in args.so]
        pessoas = [p for p in pessoas if any(f in " ".join(tokens(p.nome)) for f in filtros)]
    if not pessoas:
        raise SystemExit("Nenhuma pessoa da lista bateu com o filtro.")

    fotos = listar_fotos(base, [finais, trabalho] + ([AQUI] if AQUI != base else []))
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

    from playwright.sync_api import sync_playwright

    relatorio = base / "relatorio-eventface.csv"
    linhas = {}
    fila = [p for p in pessoas if p not in sem_foto]
    for p in sem_foto:
        linhas[p.nome] = [p.categoria, p.nome, "", "sem foto de referência", 0, ""]
    input(f"\nVou buscar {len(fila)} pessoas. Aperte Enter para começar (Ctrl+C para parar a qualquer momento)...")

    with sync_playwright() as pw:
        nav = Navegador(pw, args)
        try:
            for i, p in enumerate(fila, 1):
                destino = finais / p.categoria / p.pasta
                linha = [p.categoria, p.nome, p.foto.name, "", 0, str(destino.relative_to(base))]
                linhas[p.nome] = linha
                log(f"\n[{i}/{len(fila)}] {p.nome} ({p.categoria})")
                if destino.is_dir() and any(destino.iterdir()) and not args.refazer:
                    linha[3:5] = ["já tinha fotos", sum(1 for f in destino.rglob('*') if f.is_file())]
                    log("   a pasta já tem fotos, pulei (use --refazer para baixar de novo)")
                    escrever_relatorio(relatorio, linhas)
                    continue
                try:
                    linha[3:5] = buscar(nav, p, destino, trabalho, args)
                except Exception as e:
                    linha[3] = f"erro: {str(e).splitlines()[0][:150]}"
                    log(f"   erro: {e}")
                escrever_relatorio(relatorio, linhas)
                nav.page.wait_for_timeout(1500)
        except KeyboardInterrupt:
            log("\nParado por você.")
        finally:
            escrever_relatorio(relatorio, linhas)
            if trabalho.is_dir() and not any(f.is_file() for f in trabalho.rglob("*")):
                shutil.rmtree(trabalho, ignore_errors=True)
            try:
                nav.ctx.close()
            except Exception:
                pass

    contagem = {}
    for linha in linhas.values():
        situacao = linha[3].split(":")[0] or "não rodou"
        contagem[situacao] = contagem.get(situacao, 0) + 1
    log("\nResumo: " + ", ".join(f"{v} {k}" for k, v in contagem.items()))
    log(f"Relatório: {relatorio}")


def buscar(nav, p, destino, trabalho, args):
    """Faz a busca de uma pessoa. Devolve [situação, nº de fotos]."""
    nav.ultimo_clique = None
    nav.downloads = []
    nav.abrir_evento(args.url)
    botoes_antes = len(nav.visiveis(TXT_BAIXAR))
    if not enviar_selfie(nav, p.foto):
        return ["pulado", 0]
    # se já sei que o site só filtra a galeria, não preciso esperar tanto por um botão novo
    resultado = esperar_resultado(nav, botoes_antes, 10 if nav.botao_do_topo else 30)
    if resultado == "nenhuma":
        log("   o eventface não achou fotos desta pessoa")
        return ["nenhuma foto no evento", 0]

    if resultado == "novo":
        nav.clicar(TXT_BAIXAR, ultimo=True)
        nav.ultimo_clique = "resultado"
    else:
        if nav.botao_do_topo is None:
            log("   A página não ganhou um botão novo de baixar depois da selfie.")
            log("   Se a janela ainda pede para confirmar a selfie, confirme por lá e espere as fotos aparecerem.")
            r = perguntar("   O 'Baixar todas as fotos' agora baixa só as fotos desta pessoa?"
                          " (s = eu clico nele daqui pra frente / n = você clica no botão certo)")
            nav.botao_do_topo = r == "s"
        if nav.botao_do_topo:
            nav.clicar(TXT_BAIXAR, ultimo=True)
            nav.ultimo_clique = "topo"
        else:
            log("   >> Clique na janela no botão que baixa as fotos desta pessoa. (Enter pula a pessoa)")

    baixados = esperar_downloads(nav)
    if not baixados:
        return ["pulado", 0]
    pasta_zip = trabalho / p.categoria / p.pasta
    pasta_zip.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for d in baixados:
        alvo = pasta_zip / (d.suggested_filename or "fotos.zip")
        if alvo.exists() or alvo in arquivos:
            alvo = alvo.with_name(f"{alvo.stem}-{len(arquivos) + 1}{alvo.suffix}")
        d.save_as(str(alvo))
        arquivos.append(alvo)
    total = contar_fotos(arquivos)
    log(f"   baixei {len(arquivos)} arquivo(s) com {total} foto(s)")
    if total > args.limite:
        log(f"   >> {total} fotos é muito para uma pessoa: parece o evento inteiro.")
        if perguntar("   Descompactar mesmo assim?") != "s":
            log(f"   deixei o download em {pasta_zip}")
            if nav.ultimo_clique == "topo":
                nav.botao_do_topo = False
            return ["verificar", total]
    guardadas = guardar(arquivos, destino)
    shutil.rmtree(pasta_zip, ignore_errors=True)
    log(f"   {guardadas} foto(s) em {destino}")
    return ["ok", guardadas]


if __name__ == "__main__":
    main()
