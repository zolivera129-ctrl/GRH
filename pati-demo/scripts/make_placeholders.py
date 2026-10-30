"""Gera imagens PROVISÓRIAS para public/luis-justo-story.png e public/mockup-pausa.png.

Só existem para o vídeo renderizar enquanto as imagens reais não são colocadas na pasta
public/. Não reproduzem o slide real nem a arte real: substitua pelos arquivos originais
(mesmo nome) e renderize de novo.

Uso: python3 scripts/make_placeholders.py   (não sobrescreve arquivos existentes; use --force)
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "public"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FORCE = "--force" in sys.argv


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def story(path):
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), (18, 18, 24))
    d = ImageDraw.Draw(img)
    # plateia (fileiras de cabeças em silhueta)
    rnd = random.Random(4)
    for row in range(7):
        y = 1380 + row * 70
        for i in range(14):
            x = i * 82 + rnd.randint(-20, 20) + (row % 2) * 40
            r = 34 + row * 3
            d.ellipse([x - r, y - r, x + r, y + r], fill=(10 + row, 10 + row, 14 + row))
    # tela projetada
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle([90, 470, 990, 1010], fill=(70, 70, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.blend(img, Image.eval(glow, lambda v: v), 0.0)
    img.paste(Image.composite(glow, img, glow.convert("L")), (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([110, 490, 970, 990], fill=(236, 234, 228))
    d.text((170, 560), "INOVAÇÃO", font=font("DejaVuSans-Bold.ttf", 92), fill=(30, 30, 34))
    for i, w in enumerate([640, 700, 520]):
        d.rounded_rectangle([170, 720 + i * 62, 170 + w, 748 + i * 62], 8, fill=(150, 150, 156))
    d.text((170, 920), "slide do palestrante (provisório)", font=font("DejaVuSans.ttf", 30), fill=(120, 120, 126))
    # interface do story (identificadores que o vídeo oculta)
    for i in range(3):
        x0 = 30 + i * 345
        d.rounded_rectangle([x0, 34, x0 + 330, 40], 3, fill=(255, 255, 255) if i == 0 else (120, 120, 120))
    d.ellipse([34, 70, 114, 150], fill=(200, 160, 120))
    d.text((134, 88), "nome.de.usuario  ·  2 h", font=font("DejaVuSans-Bold.ttf", 34), fill=(255, 255, 255))
    d.rounded_rectangle([34, 1790, 880, 1870], 40, outline=(220, 220, 220), width=3)
    d.text((70, 1810), "Enviar mensagem", font=font("DejaVuSans.ttf", 32), fill=(220, 220, 220))
    img.save(path)


def mockup(path):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    top, bottom = (14, 20, 38), (52, 44, 58)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    rnd = random.Random(7)
    for _ in range(90):
        x, y = rnd.randint(0, W), rnd.randint(0, 560)
        r = rnd.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 230, 240))

    def ridge(base, amp, freq, color, seed):
        r = random.Random(seed)
        pts = [(0, H)]
        ph = r.random() * 6
        for x in range(0, W + 20, 20):
            y = base - amp * (0.6 * math.sin(x * freq + ph) + 0.4 * math.sin(x * freq * 2.7 + ph * 2))
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=color)

    ridge(720, 150, 0.006, (40, 44, 66), 1)
    ridge(820, 110, 0.009, (30, 32, 48), 2)
    ridge(930, 70, 0.013, (20, 22, 32), 3)
    # brilho da fogueira
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([340, 900, 740, 1300], fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.composite(Image.new("RGB", (W, H), (240, 140, 60)), img, glow.point(lambda v: v * 0.55))
    d = ImageDraw.Draw(img)
    d.ellipse([360, 1150, 720, 1230], fill=(24, 18, 16))
    d.polygon([(470, 1170), (540, 990), (610, 1170)], fill=(246, 166, 64))
    d.polygon([(500, 1170), (545, 1050), (585, 1170)], fill=(255, 220, 130))
    d.line([(420, 1200), (660, 1160)], fill=(70, 46, 30), width=22)
    d.line([(420, 1160), (660, 1205)], fill=(84, 54, 34), width=22)
    d.text((90, 150), "Um respiro.", font=font("DejaVuSerif-Bold.ttf", 104), fill=(245, 240, 230))
    d.text((94, 300), "arte provisória", font=font("DejaVuSans.ttf", 30), fill=(190, 186, 200))
    img.save(path)


for name, fn in (("luis-justo-story.png", story), ("mockup-pausa.png", mockup)):
    p = ROOT / name
    if p.exists() and not FORCE:
        print("mantido:", p)
        continue
    fn(p)
    print("gerado:", p)
