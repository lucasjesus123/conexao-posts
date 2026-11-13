"""Post 2026-11-13 16h: retrato P&B + 'A copiadora'. Lucas segura uma folha A4 (foto Kairogen, P&B em código);
em overlay SVG, sobre a folha, um orçamento manuscrito (Caveat) com UM erro circulado em vermelho e 'tabela velha?'
a lápis; da folha sai um leque de cópias idênticas (mesmo círculo) voando para a esquerda/cima, menores, inclinadas,
com blur crescente, as últimas saindo do quadro. Contador mono ciano + SIMULAÇÃO junto da folha.
Uso: python3 scripts/arte_copiadora.py posts/2026-11-13-16h/render.json out
Campos do JSON (além dos do m_retrato: id, modelo, pilar, imagem, frase, kicker, nome, x, y, w, tam, q_bottom):
  folha            [x0, y0, x1, y1] da folha em pixels da foto ORIGINAL (1176 x 1568)
  foto_w           largura da foto original (padrão 1176)
  fonte_mao        lista de .woff2 da Caveat 600 (latin, latin-ext)
  itens            [["Areia média (m³)", "R$ 140,00"], ...]  (o item com erro = indice 'erro')
  erro             índice do item circulado em vermelho
  nota_lapis       texto a lápis junto do círculo
  total            linha de total
  n_copias         quantas cópias no leque (30-40)
  semente          semente do leque (muda a distribuição)
  leque            {"ox","oy" (origem, px do feed), "ang0","ang1" (graus, 180 = esquerda, 270 = cima),
                    "d0","d1" (distância inicial/final), "k0","k1" (escala inicial/final), "zona_rosto": [x0,y0,x1,y1]}
  contador         texto mono ciano junto da folha original
"""
import json, sys, html, base64, pathlib, math, random, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CIANO, TINTA = R.CIANO, R.TINTA
VERMELHO = "#E0262B"
CANETA = "#1C2230"
LAPIS = "#6E6E6E"


def fonte_mao(paths):
    out = []
    for p in paths:
        p = pathlib.Path(p if pathlib.Path(p).is_absolute() else ROOT / p)
        b = base64.b64encode(p.read_bytes()).decode()
        rng = ";unicode-range:U+0100-024F" if "ext" in p.name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{b}){rng}}}")
    return "".join(out)


def tinta(p, W, H):
    """Conteúdo manuscrito da folha em coordenadas locais (0..W x 0..H, px da foto original).
    As mãos cobrem as bordas da folha na faixa y ~230-460 (x < 30 e x > 370): nada de tinta ali."""
    e = html.escape
    hand = f'font-family="Hand" font-weight="600" fill="{CANETA}"'
    g = []
    g.append(f'<text x="44" y="80" {hand} font-size="60">Orçamento</text>')
    g.append(f'<path d="M44,96 C120,90 200,100 272,92" fill="none" stroke="{CANETA}" stroke-width="3.2" stroke-linecap="round"/>')
    g.append(f'<text x="{W - 44}" y="78" text-anchor="end" {hand} font-size="30" opacity=".7">nº 0412</text>')
    passo = p.get("passo", [0, 128, 0])
    y = 170
    erro = p.get("erro", 1)
    cy_erro = None
    for i, (nome, preco) in enumerate(p["itens"]):
        y += passo[i] if i < len(passo) else 0
        g.append(f'<text x="58" y="{y}" {hand} font-size="42">{e(nome)}</text>')
        g.append(f'<text x="{W - 74}" y="{y + 46}" text-anchor="end" {hand} font-size="46">{e(preco)}</text>')
        g.append(f'<path d="M66,{y + 34} L{W - 210},{y + 34}" stroke="{CANETA}" stroke-width="2.4" stroke-dasharray="2 9" stroke-linecap="round" opacity=".55"/>')
        if i == erro:
            cy_erro = y + 14
    if cy_erro is not None:
        cx, cy, rx, ry = W / 2 + 4, cy_erro, W / 2 - 40, 64
        def volta(dr, a0, a1, rot):
            pts = []
            for k in range(41):
                a = math.radians(a0 + (a1 - a0) * k / 40)
                pts.append((cx + (rx + dr) * math.cos(a), cy + (ry + dr * .6) * math.sin(a)))
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            return f'<path d="{d}" transform="rotate({rot} {cx} {cy})" fill="none" stroke="{VERMELHO}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
        g.append(volta(0, 200, 545, -3))
        g.append(volta(5, 530, 596, -5))
        # nota a lápis logo abaixo do círculo, setinha subindo até ele
        ny = cy + ry + 62
        g.append(f'<text x="70" y="{ny}" font-family="Hand" font-weight="600" font-size="44" fill="{LAPIS}" transform="rotate(-4 70 {ny})">{e(p.get("nota_lapis", ""))}</text>')
        ax = 300
        g.append(f'<path d="M{ax - 8},{ny - 16} C{ax + 4},{ny - 30} {ax + 12},{ny - 42} {ax + 14},{ny - 58}" fill="none" stroke="{LAPIS}" stroke-width="3" stroke-linecap="round"/>')
        g.append(f'<path d="M{ax + 3},{ny - 50} L{ax + 14},{ny - 60} L{ax + 22},{ny - 47}" fill="none" stroke="{LAPIS}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        y = ny + 30
    yt = max(y + 50, H - 70)
    g.append(f'<path d="M44,{yt - 52} L{W - 44},{yt - 56}" stroke="{CANETA}" stroke-width="2.6" stroke-linecap="round"/>')
    g.append(f'<text x="44" y="{yt}" {hand} font-size="46">{e(p.get("total", ""))}</text>')
    return "".join(g)


def _caixa(cx, cy, w, h, rot):
    a = math.radians(rot); c, s = abs(math.cos(a)), abs(math.sin(a))
    hw, hh = (w * c + h * s) / 2, (w * s + h * c) / 2
    return cx - hw, cy - hh, cx + hw, cy + hh


def _bate(b, r):
    return b[0] < r[2] and b[2] > r[0] and b[1] < r[3] and b[3] > r[1]


def leque(p, fx, fy, fw, fh, k_folha):
    """Cópias voando: lista de grupos já ordenados (as mais distantes por baixo).
    Rejeita qualquer cópia cuja caixa encoste no rosto, no kicker, na mão esquerda ou no miolo da folha."""
    L = p.get("leque", {})
    rnd = random.Random(p.get("semente", 7))
    n = p.get("n_copias", 36)
    ox, oy = L.get("ox", fx + fw * .3), L.get("oy", fy + fh * .25)
    a0, a1 = L.get("ang0", 195), L.get("ang1", 262)
    d0, d1 = L.get("d0", 150), L.get("d1", 820)
    k0, k1 = L.get("k0", .62), L.get("k1", .2)
    proibido = [r for r in L.get("proibido", [])]
    proibido.append([fx + fw * .22, fy + fh * .16, fx + fw + 20, fy + fh + 20])  # miolo da folha original
    copias, tent = [], 0
    while len(copias) < n and tent < 20000:
        tent += 1
        i = len(copias)
        t = (i + rnd.random()) / n
        ang = rnd.uniform(a0, a1)
        d = d0 + (d1 - d0) * t + rnd.uniform(-40, 40)
        cx, cy = ox + d * math.cos(math.radians(ang)), oy + d * math.sin(math.radians(ang))
        k = (k0 + (k1 - k0) * t ** .7) * rnd.uniform(.85, 1.12)
        rot = rnd.choice((-1, 1)) * rnd.uniform(8, 18 + 42 * t)
        if any(_bate(_caixa(cx, cy, fw * k, fh * k, rot), r) for r in proibido):
            continue
        copias.append((t, cx, cy, k * k_folha, rot))
    out = []
    for t, cx, cy, k, rot in sorted(copias, key=lambda c: -c[0]):
        blur = round(min(7, t * 7.5) * 2) / 2
        filt = f' filter="url(#b{int(blur * 2)})"' if blur >= .5 else ""
        op = 1 - .4 * t
        out.append(f'<g opacity="{op:.2f}"{filt}><g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({k:.4f}) translate({-p["_W"] / 2:.1f},{-p["_H"] / 2:.1f})">'
                   f'<use href="#copia"/></g></g>')
    print(f'  {len(copias)} cópias ({tent} tentativas)')
    return out


def build(p):
    x, y, w = p.get("x", 0), p.get("y", -60), p.get("w", 1350)
    s = w / p.get("foto_w", 1176)
    X0, Y0, X1, Y1 = p["folha"]
    W, H = X1 - X0, Y1 - Y0
    p["_W"], p["_H"] = W, H
    fx, fy, fw, fh = x + X0 * s, y + Y0 * s, W * s, H * s
    ink = tinta(p, W, H)
    filtros = "".join(f'<filter id="b{i}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{i / 2:.1f}"/></filter>' for i in range(1, 16))
    defs = (f'<defs>{filtros}'
            f'<filter id="sombra" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#000" flood-opacity=".75"/></filter>'
            f'<linearGradient id="luz" x1="0" x2="1" y1="0" y2=".3"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D9D9D6"/></linearGradient>'
            f'<g id="tinta">{ink}</g>'
            f'<g id="copia"><rect width="{W}" height="{H}" fill="url(#luz)" filter="url(#sombra)"/><use href="#tinta"/></g></defs>')
    copias = leque(p, fx, fy, fw, fh, s)
    original = (f'<g transform="translate({fx:.1f},{fy:.1f}) scale({s:.4f})" style="mix-blend-mode:multiply"><use href="#tinta"/></g>')
    svg = (f'<svg class="ov" width="1080" height="1350" viewBox="0 0 1080 1350">{defs}'
           + "".join(copias) + original + "</svg>")
    cont = (f'<div class="ct mono" style="left:{fx:.0f}px;top:{fy + fh + 14:.0f}px"><i></i>{html.escape(p.get("contador", ""))}</div>')
    if p.get("selo"):  # selo próprio colado no canto superior esquerdo da folha original
        cont += f'<div class="selo mono" style="left:{fx - 18:.0f}px;top:{fy - 24:.0f}px">{html.escape(p["selo"])}</div>'
    if p.get("oferta") or p.get("preco"):  # linha de oferta no lugar da assinatura
        cont += (f'<div class="of"><span class="mono">{html.escape(p.get("oferta", ""))}</span>'
                 f'<b>{html.escape(p.get("preco", ""))}</b></div>')
    css = fonte_mao(p.get("fonte_mao", [])) + f"""
body>img:first-of-type{{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 7%,#000 93%,transparent 100%),linear-gradient(180deg,transparent 0,#000 5%);
  -webkit-mask-composite:source-in;mask-composite:intersect}}
.ov{{position:absolute;left:0;top:0;overflow:visible}}
.k{{text-shadow:0 0 14px #000,0 0 4px #000;opacity:.85!important}}
.ct{{position:absolute;font-size:15px;letter-spacing:.16em;color:{CIANO};display:flex;align-items:center;gap:10px;white-space:nowrap}}
.selo{{position:absolute;z-index:4;font-size:24px;letter-spacing:.16em;color:{TINTA};background:{CIANO};padding:9px 18px 8px;border-radius:8px;
  transform:rotate(-4deg);box-shadow:0 8px 22px rgba(0,0,0,.55);font-weight:500}}
.of{{position:absolute;left:72px;right:72px;bottom:142px;display:flex;align-items:center;gap:22px}}
.of span{{font-size:19px;letter-spacing:.12em;color:#fff;opacity:.85}}
.of b{{font-family:M;font-weight:800;font-size:34px;letter-spacing:-.01em;color:{TINTA};background:{CIANO};padding:8px 22px 9px;border-radius:40px;
  box-shadow:0 0 28px rgba(34,211,238,.45);white-space:nowrap}}
.n{{display:none}}
.q{{right:60px!important;-webkit-text-stroke:.9px #fff;text-shadow:0 2px 18px rgba(0,0,0,.9)}}
.q .it{{-webkit-text-stroke:.9px {CIANO}}}
.ct i{{width:9px;height:9px;border-radius:50%;background:{CIANO};box-shadow:0 0 10px {CIANO}}}
"""
    doc = R.build(p)
    doc = doc.replace("</style>", css + "</style>", 1)
    doc = doc.replace('<div class="grao"></div>', '<div class="grao"></div>' + svg + cont, 1)
    # kicker por cima das cópias
    doc = doc.replace('<div class="k mono">', '<div class="k mono" style="z-index:3">', 1)
    return doc


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(700)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
