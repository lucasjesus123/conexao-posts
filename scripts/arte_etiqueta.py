"""Post 2026-11-08 08h: papel claro + 'Etiqueta do pânico' — etiqueta de preço de papel kraft (furo, ilhó, barbante
saindo pela borda do quadro) com descontos remarcados à mão: -10% e -20% riscados, -40% em vermelho, torto.
Tudo em HTML/CSS/SVG sobre o modelo papel de kit/render.py.
Uso: python3 scripts/arte_etiqueta.py post_render.json pasta_saida
Campos extras do JSON (além dos do modelo papel: kicker, num, titulo, tam, topo, subtitulo):
  fonte_sub: linha mono menor abaixo do subtítulo
  sub_w: largura do subtítulo (px), sub_bottom: distância do pé da arte
  etiqueta: {"topo": texto mono no alto da etiqueta (opcional),
             "riscados": ["-10%", "-20%"]  (tinta preta, riscados à mão),
             "final": "-40%" (vermelho, maior, torto),
             "left", "top", "w", "h": caixa da etiqueta antes de girar (px),
             "rot": rotação (graus), "fio_y": altura em que o barbante sai pela borda direita}
  fonte_mao: lista de caminhos .woff2 da Caveat"""
import json, sys, html, base64, math, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PA = R.AZUL, R.TINTA, R.PAPEL
KRAFT = "#C99A62"
KRAFT_ESC = "#A97A45"
VERMELHO = "#D62F2F"
CANETA_PRETA = "#16181D"
FIO = "#E8DFCF"        # barbante cru
FIO_ESC = "#B9AB92"

def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)

def geo(p):
    e = p["etiqueta"]
    L, T, W, H = e.get("left", 560), e.get("top", 520), e.get("w", 410), e.get("h", 640)
    return L, T, W, H, e.get("rot", 12)

def gira(p, x, y):
    """ponto local da etiqueta (x, y a partir do canto sup. esq.) -> ponto na arte, já girado em torno do centro"""
    L, T, W, H, rot = geo(p)
    a = math.radians(rot); dx, dy = x - W / 2, y - H / 2
    return L + W / 2 + dx * math.cos(a) - dy * math.sin(a), T + H / 2 + dx * math.sin(a) + dy * math.cos(a)

FURO_Y = 84    # centro do furo, no sistema local da etiqueta
CHANF = 92     # tamanho do chanfro dos cantos de cima

def css(p):
    L, T, W, H, rot = geo(p)
    return mao(p) + f"""
.s{{display:none}}
h1{{z-index:6}}
.sub{{text-wrap:balance;position:absolute;left:72px;width:{p.get('sub_w',440)}px;bottom:{p.get('sub_bottom',170)}px;
  font-size:{p.get('tam_sub',34)}px;font-weight:600;line-height:1.32;letter-spacing:-.01em;color:{TI};opacity:.8;z-index:6}}
.sub .fnt{{display:block;margin-top:18px;font-family:Mono;font-weight:500;font-size:19px;line-height:1.5;letter-spacing:.02em;opacity:.95}}
.sub .nw{{white-space:nowrap}}
.fio{{position:absolute;left:0;top:0;width:1080px;height:1350px;pointer-events:none}}
.fio.atras{{z-index:2}} .fio.frente{{z-index:4}}
.et{{position:absolute;left:{L}px;top:{T}px;width:{W}px;height:{H}px;z-index:3;transform:rotate({rot}deg);transform-origin:50% 50%;
  filter:drop-shadow(0 1px 1px rgba(60,35,5,.22)) drop-shadow(0 6px 8px rgba(60,35,5,.14)) drop-shadow(10px 26px 30px rgba(60,35,5,.20))}}
.et .kr{{position:absolute;inset:0;
  clip-path:polygon({CHANF}px 0,{W-CHANF}px 0,100% {CHANF}px,100% 100%,0 100%,0 {CHANF}px);
  background:
    radial-gradient(120% 80% at 30% 20%,rgba(255,240,215,.34) 0,rgba(255,240,215,0) 55%),
    linear-gradient(172deg,#D2A56D 0%,{KRAFT} 46%,#BE8E57 100%)}}
.et .kr:before{{content:"";position:absolute;inset:0;opacity:.55;mix-blend-mode:multiply;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.9 .06' numOctaves='3' seed='7'/><feColorMatrix values='0 0 0 0 .55 0 0 0 0 .38 0 0 0 0 .2 0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23f)'/></svg>")}}
.et .kr:after{{content:"";position:absolute;inset:0;opacity:.35;mix-blend-mode:multiply;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='1.4' numOctaves='2' seed='3'/><feColorMatrix values='0 0 0 0 .4 0 0 0 0 .27 0 0 0 0 .12 0 0 0 .6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.et .borda{{position:absolute;inset:0;pointer-events:none}}
.et .topo{{position:absolute;left:0;right:0;top:{FURO_Y+46}px;text-align:center;font-family:Mono;font-weight:500;font-size:19px;letter-spacing:.24em;color:#3A2810;opacity:.78}}
.et .topo:after{{content:"";display:block;margin:14px auto 0;width:{W-110}px;border-top:2px dashed rgba(58,40,16,.45)}}
.et .hd{{position:absolute;left:0;right:0;font-family:Hand;font-weight:600;line-height:1;white-space:nowrap;text-align:center}}
.et .rs{{color:{CANETA_PRETA};font-size:118px;opacity:.9}}
.et .rs .dg{{position:relative;display:inline-block}}
.et .rs .sg,.et .rs .um{{display:inline-block;height:1em;vertical-align:top}}
.et .rs .sg{{width:.44em;margin-right:.16em}}
.et .rs .um{{width:.4em}}
.et .rs .sg svg,.et .rs .um svg{{width:100%;height:100%;overflow:visible}}
.et .rs .dg>svg.rk{{position:absolute;left:-10px;top:0;width:calc(100% + 20px);height:100%;overflow:visible}}
.et .fin{{color:{VERMELHO};font-size:{p['etiqueta'].get('fs_final',214)}px;transform:rotate({p['etiqueta'].get('rot_final',-12)}deg);transform-origin:50% 60%}}
.et .fin span{{display:inline-block;position:relative}}
"""

# Métrica da Caveat com line-height:1 (em % da altura da linha): algarismos vão de ~29% a ~83% (linha de base).
# risco à mão: só sobre os algarismos (começa depois do sinal), em diagonal subindo forte (a etiqueta já gira 12° no sentido
# horário, então o risco precisa subir ~35° para não parecer paralelo ao sinal), cruzando o meio da altura (~56%)
def risco(seed):
    a = (3, -3)[seed % 2]
    tr = (f'<path d="M4 {92+a} C 60 {80+a}, 130 {44-a}, 196 {20+a}" fill="none" stroke="{CANETA_PRETA}" stroke-width="7" '
          f'stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
          f'<path d="M18 {98-a} C 80 {84}, 140 {52}, 188 {30-a}" fill="none" stroke="{CANETA_PRETA}" stroke-width="4.5" '
          f'stroke-linecap="round" opacity=".85" vector-effect="non-scaling-stroke"/>')
    return f'<svg class="rk" viewBox="0 0 200 100" preserveAspectRatio="none">{tr}</svg>'

# sinal de menos à mão: traço longo e reto na altura do meio dos algarismos, separado dos números
SINAL = (f'<span class="sg"><svg viewBox="0 0 44 100" preserveAspectRatio="none"><path d="M3 58 C 15 57, 30 56.5, 42 55.5" '
         f'fill="none" stroke="{CANETA_PRETA}" stroke-width="8.5" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg></span>')
# "1" à mão: traço reto vertical, com perninha curtíssima no alto (a perna longa da Caveat lia como 4)
UM = (f'<span class="um"><svg viewBox="0 0 40 100" preserveAspectRatio="none"><path d="M13 35 L 22 28.5 L 20 83.5" '
      f'fill="none" stroke="{CANETA_PRETA}" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg></span>')

def riscado(t, i):
    neg = t.startswith("-")
    corpo = html.escape(t[1:] if neg else t).replace("1", UM)
    return (SINAL if neg else "") + f'<span class="dg">{corpo}{risco(i)}</span>'

def borda_svg(W, H):
    # contorno vincado + furo com ilhó metálico
    c, fy = CHANF, FURO_Y
    poly = f"{c},1 {W-c},1 {W-1},{c} {W-1},{H-1} 1,{H-1} 1,{c}"
    cx = W / 2
    return f"""<svg class="borda" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
 <radialGradient id="ilho" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#F4EEDF"/><stop offset=".45" stop-color="#C9BFA6"/>
  <stop offset=".8" stop-color="#8E8470"/><stop offset="1" stop-color="#6E6553"/></radialGradient>
 <linearGradient id="aro" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity="0"/>
  <stop offset="1" stop-color="#3B3428" stop-opacity=".5"/></linearGradient>
</defs>
<polygon points="{poly}" fill="none" stroke="rgba(90,58,20,.35)" stroke-width="2"/>
<polygon points="{c+16},16 {W-c-16},16 {W-16},{c+16} {W-16},{H-16} 16,{H-16} 16,{c+16}" fill="none" stroke="rgba(255,240,215,.28)" stroke-width="1.5"/>
<circle cx="{cx+1.5}" cy="{fy+3}" r="31" fill="rgba(60,35,5,.28)"/>
<circle cx="{cx}" cy="{fy}" r="30" fill="url(#ilho)"/>
<circle cx="{cx}" cy="{fy}" r="30" fill="none" stroke="url(#aro)" stroke-width="3"/>
<circle cx="{cx}" cy="{fy}" r="16.5" fill="#5B5243"/>
<circle cx="{cx}" cy="{fy}" r="14" fill="{PA}"/>
<path d="M {cx-14} {fy} A 14 14 0 0 1 {cx+14} {fy}" fill="rgba(40,25,5,.30)"/>
</svg>"""

def fio(p, frente):
    """barbante: laçada pelo furo (fio da frente sobre a etiqueta, fio de trás por baixo dela) e saída pela borda direita."""
    e = p["etiqueta"]; L, T, W, H, rot = geo(p)
    hx, hy = gira(p, W / 2, FURO_Y)
    # pontos onde os dois fios cruzam a borda de cima da etiqueta
    ax, ay = gira(p, W / 2 - 9, -6)
    bx, by = gira(p, W / 2 + 12, -4)
    ex, ey = 1100, e.get("fio_y", 470)
    mx, my = (hx + ex) / 2, max(hy, ey) + e.get("fio_curva", 60)
    if frente:
        # sai do furo, passa por cima da borda de cima e segue
        d1 = f"M {hx-3:.1f} {hy+4:.1f} C {hx-10:.1f} {hy-20:.1f}, {ax-6:.1f} {ay+10:.1f}, {ax:.1f} {ay:.1f}"
        d2 = (f"M {ax:.1f} {ay:.1f} C {ax+30:.1f} {ay-46:.1f}, {mx-40:.1f} {my:.1f}, {mx:.1f} {my-6:.1f} "
              f"S {ex-70:.1f} {ey+6:.1f}, {ex:.1f} {ey:.1f}")
        paths = [d1, d2]
    else:
        d3 = (f"M {hx+6:.1f} {hy:.1f} C {hx+10:.1f} {hy-20:.1f}, {bx+4:.1f} {by+10:.1f}, {bx:.1f} {by:.1f} "
              f"C {bx+40:.1f} {by-40:.1f}, {mx-30:.1f} {my+8:.1f}, {mx+8:.1f} {my-2:.1f} S {ex-60:.1f} {ey+16:.1f}, {ex:.1f} {ey+12:.1f}")
        paths = [d3]
    cls = "frente" if frente else "atras"
    out = [f'<svg class="fio {cls}" viewBox="0 0 1080 1350"><defs><filter id="fs{cls}" x="-10%" y="-10%" width="120%" height="120%">'
           f'<feDropShadow dx="3" dy="8" stdDeviation="5" flood-color="#3C2305" flood-opacity=".22"/></filter></defs><g filter="url(#fs{cls})">']
    for d in paths:
        out.append(f'<path d="{d}" fill="none" stroke="{FIO_ESC}" stroke-width="7.5" stroke-linecap="round"/>'
                   f'<path d="{d}" fill="none" stroke="{FIO}" stroke-width="5" stroke-linecap="round"/>'
                   f'<path d="{d}" fill="none" stroke="#9C8D72" stroke-width="5" stroke-linecap="round" stroke-dasharray="3 6" opacity=".55"/>')
    out.append("</g></svg>")
    return "".join(out)

def etiqueta(p):
    e = p["etiqueta"]; L, T, W, H, rot = geo(p)
    topo = f'<div class="topo">{html.escape(e["topo"])}</div>' if e.get("topo") else ""
    ys = e.get("ys", [190, 300, 420])
    rs = "".join(f'<div class="hd rs" style="top:{ys[i]}px;margin-left:{(-18, 26)[i % 2]}px">{riscado(t, i)}</div>'
                 for i, t in enumerate(e["riscados"]))
    fin = (f'<div class="hd fin" style="top:{ys[-1]}px;margin-left:{e.get("final_dx",60)}px"><span>{html.escape(e["final"])}</span></div>')
    return (fio(p, False) +
            f'<div class="et"><div class="kr"></div>{borda_svg(W, H)}{topo}{rs}{fin}</div>' +
            fio(p, True))

def bloco(p):
    sub = html.escape(p.get("subtitulo", ""))
    if p.get("fonte_sub"):
        # | = quebra explícita; cada linha fica inteira (sem quebra no meio)
        partes = "<br>".join(f'<span class="nw">{html.escape(t.strip())}</span>' for t in p["fonte_sub"].split("|"))
        sub += f'<span class="fnt">{partes}</span>'
    return f'<p class="sub">{sub}</p>' + etiqueta(p)

def build(p):
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_papel(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + (f"h1{{right:{p['h1_right']}px}}" if p.get('h1_right') else '') + "</style>", 1)
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1)

def checa(pg):
    """caixas (px) do que não pode ser tocado pela etiqueta nem pelo barbante"""
    return pg.evaluate("""() => {const r = s => {const e = document.querySelector(s); if(!e) return null;
      const b = e.getBoundingClientRect(); return [s, Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]};
      return ['h1','.sub','.marca','.handle','.k','.et'].map(r)}""")

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
            for c in checa(pg): print("  caixa", c)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            Image.open(out / f"{p['id']}_story.png").convert("RGB").save(out / f"{p['id']}_story.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
