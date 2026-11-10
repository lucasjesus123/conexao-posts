"""Post 2026-11-10 08h: papel claro + 'O holerite do fantasma' — recibo de pagamento (contracheque) de papel branco-gelo,
picote no topo, fonte mono, levemente girado, com "Último acesso: março" circulado à mão em vermelho (com setinha) e
carimbo vermelho "DEMITIDO EM DEZEMBRO" batido no campo de observações, com tinta falhada.
Tudo em HTML/CSS/SVG sobre o modelo papel de kit/render.py (sem imagem gerada).
Uso: python3 scripts/arte_holerite.py post_render.json pasta_saida
Campos extras do JSON (além dos do modelo papel: kicker, num, titulo, tam, topo, subtitulo):
  sub_w, sub_bottom, tam_sub: largura, distância do pé e tamanho do subtítulo
  holerite: {"cabecalho": texto mono do topo,
             "linhas": [[rótulo, valor] ou [[rótulo, valor], [rótulo, valor]] (linha com 2 células)],
             "circulo": valor a circular em vermelho (ex.: "março"),
             "carimbo": ["DEMITIDO", "EM DEZEMBRO"], "rot_carimbo": graus,
             "obs": rótulo do campo de observações, "selo": selo discreto (ex.: "ILUSTRATIVO"),
             "left", "top", "w": caixa do papel antes de girar (px), "rot": rotação (graus), "h_obs": altura do campo}
  fonte_mao: lista de caminhos .woff2 da Caveat"""
import json, sys, html, base64, pathlib, importlib.util, random
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PA = R.AZUL, R.TINTA, R.PAPEL
GELO = "#FBF9F4"
TINTA_REC = "#23262D"      # impressão do recibo
VERMELHO = "#D42A2A"       # caneta
CARIMBO = "#C8242B"        # tinta de carimbo


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
    e = p["holerite"]
    return e.get("left", 480), e.get("top", 560), e.get("w", 620), e.get("rot", -5)


def borda_rasgada(w, dente=7, passo=9, seed=11):
    """clip-path com a borda de cima serrilhada (destacado do bloco no picote)"""
    rnd = random.Random(seed); pts = []; x = 0
    while x < w:
        pts.append(f"{x}px {rnd.uniform(0, 2):.1f}px"); x += passo / 2
        pts.append(f"{min(x, w)}px {dente + rnd.uniform(-1.5, 1.5):.1f}px"); x += passo / 2
    pts.append(f"{w}px 0px")
    return "polygon(" + ",".join(pts) + ",100% 100%,0 100%)"


def css(p):
    L, T, W, rot = geo(p); e = p["holerite"]
    return mao(p) + f"""
.s{{display:none}}
h1{{z-index:6}}
.sub{{text-wrap:pretty;position:absolute;left:72px;width:{p.get('sub_w',400)}px;bottom:{p.get('sub_bottom',170)}px;
  font-size:{p.get('tam_sub',34)}px;font-weight:600;line-height:1.3;letter-spacing:-.01em;color:{TI};opacity:.8;z-index:6}}
.sub .nw{{white-space:nowrap}}
.hl{{position:absolute;left:{L}px;top:{T}px;width:{W}px;z-index:3;transform:rotate({rot}deg);transform-origin:50% 50%;
  filter:drop-shadow(0 1px 1px rgba(30,25,15,.18)) drop-shadow(0 8px 10px rgba(30,25,15,.10)) drop-shadow(-14px 30px 34px rgba(30,25,15,.18))}}
.pp{{position:relative;clip-path:{borda_rasgada(W)};padding:38px 44px 12px 44px;color:{TINTA_REC};font-family:Mono;
  background:radial-gradient(120% 70% at 25% 10%,#FFFFFF 0,rgba(255,255,255,0) 60%),linear-gradient(176deg,{GELO} 0%,#F4F1EA 100%)}}
.pp:before{{content:"";position:absolute;inset:0;opacity:.45;mix-blend-mode:multiply;pointer-events:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='f'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' seed='5'/><feColorMatrix values='0 0 0 0 .55 0 0 0 0 .52 0 0 0 0 .46 0 0 0 .32 0'/></filter><rect width='100%' height='100%' filter='url(%23f)'/></svg>")}}
.pp:after{{content:"";position:absolute;left:0;right:0;top:0;height:22px;pointer-events:none;
  background:linear-gradient(180deg,rgba(120,110,90,.10),rgba(120,110,90,0))}}
.pic{{position:absolute;left:18px;right:18px;top:22px;height:6px;
  background:radial-gradient(circle at 3px 3px,rgba(70,64,52,.42) 2.3px,transparent 2.8px) 0 0/14px 6px repeat-x}}
.cab{{display:flex;justify-content:space-between;align-items:center;font-size:17px;letter-spacing:.1em;white-space:nowrap;padding-bottom:14px;
  border-bottom:2px solid {TINTA_REC}}}
.selo{{font-size:14px;font-weight:700;letter-spacing:.18em;padding:6px 10px 5px;border:2px solid rgba(35,38,45,.8);border-radius:4px;color:rgba(35,38,45,.9)}}
.ln{{display:flex;border-bottom:1.5px dashed rgba(35,38,45,.28)}}
.cel{{flex:1;padding:11px 0 10px}}
.cel+.cel{{border-left:1.5px dashed rgba(35,38,45,.28);padding-left:22px}}
.rot{{display:block;font-size:15px;letter-spacing:.18em;text-transform:uppercase;opacity:.55;margin-bottom:5px}}
.val{{display:block;font-size:{e.get('fs_val',23)}px;letter-spacing:-.01em;line-height:1.2;white-space:nowrap}}
.circ{{position:relative;display:inline-block}}
.circ svg.el{{position:absolute;left:-26px;top:-9px;width:calc(100% + 52px);height:calc(100% + 18px);overflow:visible}}
.seta{{position:absolute;overflow:visible;pointer-events:none}}
.obs{{position:relative;height:{e.get('h_obs',196)}px;padding-top:12px}}
.obs .rot{{margin:0}}
.car{{position:absolute;left:{e.get('car_x',30)}px;top:{e.get('car_y',36)}px;width:{e.get('car_w',470)}px;
  transform:rotate({e.get('rot_carimbo',-14)}deg);transform-origin:50% 50%;mix-blend-mode:multiply;opacity:.9}}
.pp{{overflow:hidden}}
.car svg{{display:block;width:100%;height:auto;overflow:visible}}
"""


def circulo():
    """elipse à mão: volta não fechada, com sobreposição no fim (caneta vermelha)"""
    return (f'<svg class="el" viewBox="0 0 200 100" preserveAspectRatio="none">'
            f'<path d="M150 9 C 110 -2, 40 2, 14 30 C -6 54, 22 92, 92 95 C 160 98, 200 76, 192 44 C 186 20, 150 6, 104 8" '
            f'fill="none" stroke="{VERMELHO}" stroke-width="4.6" stroke-linecap="round" vector-effect="non-scaling-stroke" opacity=".93"/>'
            f'<path d="M140 12 C 100 4, 46 8, 22 32" fill="none" stroke="{VERMELHO}" stroke-width="2.2" stroke-linecap="round" '
            f'vector-effect="non-scaling-stroke" opacity=".55"/></svg>')


def seta(x, y):
    """setinha à mão chegando no círculo pela direita, dentro da própria linha"""
    return (f'<svg class="seta" style="left:{x}px;top:{y}px" width="84" height="40" viewBox="0 0 84 40">'
            f'<path d="M80 30 C 60 35, 34 32, 8 20" fill="none" stroke="{VERMELHO}" stroke-width="4.4" stroke-linecap="round"/>'
            f'<path d="M23 7 C 17 12, 12 16, 7 20 C 13 24, 18 27, 25 32" fill="none" stroke="{VERMELHO}" stroke-width="4.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def carimbo(p):
    e = p["holerite"]; l1, l2 = e.get("carimbo", ["DEMITIDO", "EM DEZEMBRO"])
    # tinta falhada: máscara de ruído fino (pontos sem tinta) + ruído largo (pressão desigual do carimbo)
    return f"""<div class="car"><svg viewBox="0 0 470 196">
<defs>
 <filter id="tx" x="0" y="0" width="100%" height="100%" filterUnits="userSpaceOnUse">
  <feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="2" seed="9" result="fino"/>
  <feTurbulence type="fractalNoise" baseFrequency=".018 .03" numOctaves="2" seed="3" result="largo"/>
  <feColorMatrix in="fino" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -7 5.0" result="a"/>
  <feColorMatrix in="largo" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -5 3.75" result="b"/>
  <feComposite in="a" in2="b" operator="arithmetic" k1="1" result="m"/>
 </filter>
 <mask id="falha" maskUnits="userSpaceOnUse" x="0" y="0" width="470" height="196"><rect width="470" height="196" fill="#fff" filter="url(#tx)"/></mask>
</defs>
<g mask="url(#falha)" fill="{CARIMBO}" stroke="{CARIMBO}">
 <rect x="6" y="6" width="458" height="184" rx="14" fill="none" stroke-width="7"/>
 <rect x="20" y="20" width="430" height="156" rx="7" fill="none" stroke-width="2.6"/>
 <text x="235" y="104" text-anchor="middle" stroke="none" font-family="Anton" font-size="88" letter-spacing="5" textLength="384" lengthAdjust="spacingAndGlyphs">{html.escape(l1)}</text>
 <line x1="50" y1="120" x2="420" y2="120" stroke-width="2.6"/>
 <text x="235" y="163" text-anchor="middle" stroke="none" font-family="Anton" font-size="39" letter-spacing="8" textLength="370" lengthAdjust="spacingAndGlyphs">{html.escape(l2)}</text>
</g></svg></div>"""


def celula(rotulo, valor, alvo):
    v = html.escape(valor)
    if alvo and valor == alvo:
        v = f'<span class="circ">{v}{circulo()}{seta(*SETA)}</span>'
    return f'<div class="cel"><span class="rot">{html.escape(rotulo)}</span><span class="val">{v}</span></div>'


SETA = (96, 4)   # posição da setinha em relação ao valor circulado


def holerite(p):
    global SETA
    e = p["holerite"]; alvo = e.get("circulo"); SETA = tuple(e.get("seta", SETA))
    linhas = []
    for ln in e["linhas"]:
        cels = ln if isinstance(ln[0], list) else [ln]
        linhas.append('<div class="ln">' + "".join(celula(r, v, alvo) for r, v in cels) + '</div>')
    selo = f'<span class="selo">{html.escape(e["selo"])}</span>' if e.get("selo") else ""
    obs = (f'<div class="obs"><span class="rot">{html.escape(e.get("obs", "Observações"))}</span>{carimbo(p)}</div>')
    return (f'<div class="hl"><div class="pp"><div class="pic"></div>'
            f'<div class="cab"><span>{html.escape(e["cabecalho"])}</span>{selo}</div>'
            + "".join(linhas) + obs + '</div></div>')


def bloco(p):
    return f'<p class="sub">{html.escape(p.get("subtitulo", ""))}</p>' + holerite(p)


def build(p):
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_papel(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + (f"h1{{right:{p['h1_right']}px}}" if p.get('h1_right') else '') + "</style>", 1)
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1)


def checa(pg):
    """caixas (px) do que não pode colidir com o holerite"""
    return pg.evaluate("""() => {const r = s => {const e = document.querySelector(s); if(!e) return null;
      const b = e.getBoundingClientRect(); return [s, Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]};
      return ['h1','.sub','.marca','.handle','.k','.hl','.car','.circ'].map(r)}""")


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
