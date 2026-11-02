"""Post 2026-11-02 08h: nota clara + 'A escada que ninguém filma' (escada de 5 degraus em SVG, robô humanoide
em traço de linha no 5º degrau furando a moldura do cartão pela borda direita, anotações à mão em Caveat).
Uso: python3 scripts/arte_escada.py posts/2026-11-02-08h/render.json pasta_saida
Campos do JSON (além de id, modelo, pilar, tema):
  kicker, kicker_dir          mono no topo (esquerda / direita)
  avatar, nome                foto redonda e nome no cabeçalho do cartão (handle vem do render.py)
  texto                       frase principal ({trecho} = itálico azul serif, | = quebra)
  sub                         sublinha; ==trecho== = marca-texto amarelo
  degraus                     ["01|PROCESSO", ...] número | uma palavra (o último sai em azul)
  notas                       {"aqui": "tu está aqui?", "piloto": "2023 · piloto", "robo": "2027 · +2 armazéns",
                               "leitura": "a escada, na minha leitura"}  (leitura = linha à mão embaixo da escada)
  rodape                      mono no pé do cartão
  fonte_mao                   lista de caminhos .woff2 da Caveat 600 (latin, latin-ext)
  opcionais de ajuste: tam (px do texto), sub_tam, sub_w, chao (y da base da escada), degrau_h, robo_x, robo_s"""
import json, sys, html, base64, pathlib, re, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PAPEL = R.AZUL, R.TINTA, R.PAPEL
TOPO, FRENTE, LATERAL = "#E2DFD6", "#FFFFFF", "#D6D2C7"
AZ_CLARO = "#EAF0FF"
SW = 2.6
ST = f'stroke="{TI}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round"'

CARD_L, CARD_T, CARD_W, CARD_H = 64, 150, 952, 1010
CARD_R = CARD_L + CARD_W

def fonte_mao(paths):
    out = []
    for i, p in enumerate(paths):
        b = base64.b64encode(pathlib.Path(p).read_bytes()).decode()
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(p).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{b}){rng}}}")
    return "".join(out)

# ---------- caixinha isométrica (mesma geometria de arte_caixas.py, viewBox 210 x 230) ----------
def caixa(x, y, s):
    st = f'stroke="{TI}" stroke-width="{SW / s:.2f}" stroke-linejoin="round"'
    sf = f'stroke="{TI}" stroke-width="{1.6 / s:.2f}" stroke-linejoin="round"'
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<polygon points="10,65 105,20 200,65 105,110" fill="{TOPO}" {st}/>'
            f'<polygon points="10,65 105,110 105,200 10,155" fill="{FRENTE}" {st}/>'
            f'<polygon points="105,110 200,65 200,155 105,200" fill="{LATERAL}" {st}/>'
            f'<polygon points="48,83 67,92 162,47 143,38" fill="{AZ}" {sf}/>'
            f'<polygon points="48,83 67,92 67,182 48,173" fill="{AZ}" {sf}/></g>')

def tubo(d, w):
    """membro com contorno: traço grosso escuro + traço branco por dentro"""
    return (f'<path d="{d}" fill="none" stroke="{TI}" stroke-width="{w + 2 * SW}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{FRENTE}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

# ---------- robô humanoide em traço de linha (origem = ponto entre os pés, y para cima negativo) ----------
def robo(x, y, s=1.0):
    g = []
    # sombra no degrau
    g.append(f'<ellipse cx="0" cy="2" rx="52" ry="7" fill="{TI}" opacity=".14" filter="url(#bl)"/>')
    # pernas (coxa + canela) e pés
    for sx in (-1, 1):
        g.append(tubo(f"M{sx*17},-94 L{sx*20},-52 L{sx*20},-16", 21))
        g.append(f'<circle cx="{sx*20}" cy="-52" r="7" fill="{TOPO}" {ST}/>')
        g.append(f'<path d="M{sx*6},-1 L{sx*6},-11 Q{sx*6},-18 {sx*13},-18 L{sx*28},-18 Q{sx*38},-18 {sx*40},-8 L{sx*41},-1 Z" fill="{LATERAL}" {ST}/>')
    # quadril
    g.append(f'<rect x="-29" y="-108" width="58" height="22" rx="10" fill="{TOPO}" {ST}/>')
    # tronco
    g.append(f'<path d="M-38,-186 Q-38,-196 -28,-196 L28,-196 Q38,-196 38,-186 L33,-114 Q32,-104 22,-104 L-22,-104 Q-32,-104 -33,-114 Z" fill="{FRENTE}" {ST}/>')
    g.append(f'<path d="M-24,-180 L24,-180" {ST} opacity=".35"/>')
    g.append(f'<circle cx="0" cy="-165" r="5" fill="{AZ}" stroke="{TI}" stroke-width="2"/>')
    # pescoço
    g.append(f'<rect x="-8" y="-210" width="16" height="16" rx="4" fill="{LATERAL}" {ST}/>')
    # cabeça oval com visor azul
    g.append(f'<ellipse cx="0" cy="-236" rx="27" ry="31" fill="{FRENTE}" {ST}/>')
    g.append(f'<rect x="-21" y="-248" width="42" height="17" rx="8.5" fill="{AZ}" stroke="{TI}" stroke-width="2.2"/>')
    g.append(f'<ellipse cx="-8" cy="-243" rx="6" ry="2.2" fill="#fff" opacity=".75"/>')
    g.append(f'<path d="M-27,-238 L-31,-238 M27,-238 L31,-238" {ST}/>')
    # braços (ombro -> cotovelo -> mão na lateral da caixa)
    for sx in (-1, 1):
        g.append(f'<circle cx="{sx*40}" cy="-184" r="10" fill="{TOPO}" {ST}/>')
        g.append(tubo(f"M{sx*42},-180 L{sx*47},-146 L{sx*34},-128", 14))
    # caixinha segurada à frente do tronco
    g.append(caixa(-38, -158, 0.36))
    # mãos por cima da caixa
    for sx in (-1, 1):
        g.append(f'<rect x="{sx*36 - 7}" y="-136" width="14" height="18" rx="6" fill="{TOPO}" {ST}/>')
    return f'<g transform="translate({x},{y}) scale({s})">{"".join(g)}</g>'

# ---------- escada ----------
def escada(p):
    chao = p.get("chao", 1072)
    H = p.get("degrau_h", 78)
    xs = [116, 280, 444, 608, 772, 1040]   # bordas das colunas; a 5ª passa da moldura (CARD_R = 1016)
    dx, dy = 28, 18
    degs = p["degraus"]
    tops = [chao - (i + 1) * H for i in range(5)]
    # laje da escada: perfil em degraus por cima, base diagonal por baixo (o 1º degrau apoia no chão)
    fundo5 = tops[4] + H + 8
    def base_y(x):  # y da face de baixo na posição x
        return chao if x <= xs[1] else chao - (x - xs[1]) * (chao - fundo5) / (xs[5] - xs[1])
    g = [f'<path d="M{xs[0] + 10},{chao + 4} L{xs[1]},{chao + 4} L{xs[5] + dx},{fundo5 - dy + 6}" fill="none" stroke="{TI}" stroke-width="14" opacity=".08" filter="url(#bl)"/>']
    # lateral da escada (profundidade) no fim
    perfil = [(xs[0], chao)]
    for i in range(5):
        perfil += [(xs[i], tops[i]), (xs[i + 1], tops[i])]
    perfil += [(xs[5], fundo5), (xs[1], chao)]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in perfil)
    # pisos (atrás do perfil)
    for i in range(5):
        x0, x1, top = xs[i], xs[i + 1], tops[i]
        g.append(f'<polygon points="{x0},{top} {x1},{top} {x1 + dx},{top - dy} {x0 + dx},{top - dy}" fill="{TOPO}" {ST}/>')
    g.append(f'<polygon points="{xs[5]},{tops[4]} {xs[5] + dx},{tops[4] - dy} {xs[5] + dx},{fundo5 - dy} {xs[5]},{fundo5}" fill="{LATERAL}" {ST}/>')
    g.append(f'<polygon points="{pts}" fill="{FRENTE}"/>')
    # 5º degrau tingido de azul claro
    g.append(f'<polygon points="{xs[4]},{tops[4]} {xs[5]},{tops[4]} {xs[5]},{fundo5} {xs[4]},{base_y(xs[4]):.1f}" fill="{AZ_CLARO}"/>')
    # divisões leves entre os espelhos
    for i in range(1, 5):
        g.append(f'<line x1="{xs[i]}" y1="{tops[i - 1]}" x2="{xs[i]}" y2="{base_y(xs[i]):.1f}" stroke="{TI}" stroke-width="1.4" opacity=".18"/>')
    g.append(f'<polygon points="{pts}" fill="none" {ST}/>')
    for i in range(5):
        x0, top = xs[i], tops[i]
        ult = i == 4
        n, nome = (degs[i].split("|") + [""])[:2]
        cor = AZ if ult else TI
        # número em cima, uma palavra embaixo, ~28px e cor cheia (legível no celular)
        g.append(f'<text x="{x0 + 16}" y="{top + 33}" font-family="Mono" font-weight="500" font-size="28" fill="{cor}">{html.escape(n)}</text>')
        g.append(f'<text x="{x0 + 16}" y="{top + 65}" font-family="Mono" font-weight="500" font-size="28" fill="{cor}">{html.escape(nome)}</text>')
    topo5 = chao - 5 * H
    # robô em pé no meio do piso do 5º degrau, atravessando a borda do cartão
    g.append(robo(p.get("robo_x", 1000), topo5 - dy / 2 + 2, p.get("robo_s", 1.0)))
    return g, chao, H, xs, dx, dy

def anotacoes(p, chao, H, xs, dx, dy):
    n = p.get("notas", {})
    hand = f'font-family="Hand" font-weight="600" fill="{AZ}"'
    seta = f'fill="none" stroke="{AZ}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'
    g = []
    t1 = chao - H                      # piso do degrau 1
    t2 = chao - 2 * H
    t5 = chao - 5 * H
    # "tu está aqui?" + seta curva até o degrau 1
    ay = t1 - 250
    g.append(f'<text x="124" y="{ay}" {hand} font-size="52" transform="rotate(-5 124 {ay})">{html.escape(n.get("aqui", ""))}</text>')
    g.append(f'<path d="M160,{ay + 26} C126,{ay + 100} 140,{t1 - 70} 192,{t1 - 26}" {seta}/>')
    g.append(f'<path d="M174,{t1 - 32} L194,{t1 - 24} L193,{t1 - 46}" {seta}/>')
    # "2023 · piloto" junto ao degrau 2
    py = t2 - 92
    g.append(f'<text x="{xs[1] + 20}" y="{py}" {hand} font-size="42" transform="rotate(-4 {xs[1] + 20} {py})">{html.escape(n.get("piloto", ""))}</text>')
    g.append(f'<path d="M{xs[1] + 74},{py + 16} C{xs[1] + 84},{py + 40} {xs[1] + 80},{py + 58} {xs[1] + 70},{t2 - 26}" {seta}/>')
    g.append(f'<path d="M{xs[1] + 62},{t2 - 38} L{xs[1] + 69},{t2 - 24} L{xs[1] + 82},{t2 - 34}" {seta}/>')
    # "2027 · +2 armazéns" junto ao robô (expansão, não a chegada)
    rx = p.get("robo_x", 1000)
    s = p.get("robo_s", 1.0)
    ry = t5 - dy / 2
    tx, ty = rx - 60 * s - 18, ry - 52 * s
    g.append(f'<text x="{tx}" y="{ty}" text-anchor="end" {hand} font-size="40" transform="rotate(-4 {tx} {ty})">{html.escape(n.get("robo", ""))}</text>')
    g.append(f'<path d="M{tx + 10},{ty - 20} C{tx + 18},{ty - 26} {tx + 26},{ty - 28} {tx + 36},{ty - 27}" {seta}/>')
    g.append(f'<path d="M{tx + 25},{ty - 36} L{tx + 37},{ty - 27} L{tx + 25},{ty - 18}" {seta}/>')
    # autoria da leitura, embaixo da laje
    if n.get("leitura"):
        g.append(f'<text x="{CARD_R - 44}" y="{chao - 16}" text-anchor="end" font-family="Hand" font-weight="600" font-size="34" fill="{TI}" opacity=".62">{html.escape(n["leitura"])}</text>')
    return g

def sub_html(s):
    t = html.escape(s)
    return re.sub(r"==(.+?)==", r'<span class="mk">\1</span>', t)

def build(p):
    av = base64.b64encode(pathlib.Path(p["avatar"]).read_bytes()).decode()
    g, chao, H, xs, dx, dy = escada(p)
    g += anotacoes(p, chao, H, xs, dx, dy)
    svg = (f'<svg class="sv" width="1080" height="1350" viewBox="0 0 1080 1350">'
           f'<defs><filter id="bl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="5"/></filter></defs>'
           + "".join(g) + "</svg>")
    css = fonte_mao(p.get("fonte_mao", [])) + f"""
.k{{position:absolute;left:72px;right:72px;top:84px;display:flex;justify-content:space-between;font-size:18px;opacity:.6}}
.card{{position:absolute;left:{CARD_L}px;top:{CARD_T}px;width:{CARD_W}px;height:{CARD_H}px;background:#fff;border-radius:34px;
  box-shadow:0 30px 80px rgba(0,0,0,.11),0 2px 6px rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.06)}}
.h{{position:absolute;left:{CARD_L + 52}px;top:{CARD_T + 48}px;display:flex;align-items:center;gap:20px}}
.h img{{width:84px;height:84px;border-radius:50%;object-fit:cover}}
.h b{{display:block;font-size:31px;font-weight:800;line-height:1.15}} .h span{{font-size:23px;opacity:.55}}
.tx{{position:absolute;left:{CARD_L + 52}px;right:{1080 - CARD_R + 40}px;top:{CARD_T + 172}px;font-size:{p.get('tam', 62)}px;line-height:1.1;font-weight:800;letter-spacing:-.03em}}
.tx .it{{color:{AZ};font-size:1.08em;letter-spacing:-.01em}}
.sb{{position:absolute;left:{CARD_L + 52}px;width:{p.get('sub_w', 660)}px;top:{CARD_T + 352}px;font-size:{p.get('sub_tam', 27)}px;line-height:1.42;font-weight:600;color:rgba(11,13,18,.72)}}
.sb .mk{{white-space:nowrap;color:{TI};background:linear-gradient(transparent 52%,#FFE14D 52%,#FFE14D 92%,transparent 92%);padding:0 3px;margin:0 -3px}}
.d{{position:absolute;left:{CARD_L + 52}px;right:{1080 - CARD_R + 52}px;top:{CARD_T + CARD_H - 62}px;font-size:16px;opacity:.5}}
.sv{{position:absolute;left:0;top:0;overflow:visible}}
"""
    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + R._base(PAPEL, TI, css) +
            f'</style></head><body><div class="grao"></div>'
            f'<div class="k mono"><span>{html.escape(p.get("kicker", ""))}</span><span>{html.escape(p.get("kicker_dir", ""))}</span></div>'
            f'<div class="card"></div>'
            f'<div class="h"><img src="data:image/jpeg;base64,{av}"><div><b>{html.escape(p.get("nome", "Lucas Jesus"))}</b><span>{R.HANDLE}</span></div></div>'
            f'<div class="tx">{R._ed(p["texto"])}</div><div class="sb">{sub_html(p.get("sub", ""))}</div>'
            f'<div class="d mono">{html.escape(p.get("rodape", ""))}</div>'
            f'{svg}{R._rodape(True)}</body></html>')

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(600)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
