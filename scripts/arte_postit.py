"""Post 2026-11-03 08h: papel claro + 'O post-it de férias' (post-it amarelo colado com fita, letra à mão), tudo em HTML/SVG.
Uso: python3 scripts/arte_postit.py post_render.json pasta_saida
Campos extras do JSON (além dos do modelo papel: kicker, num, titulo, tam, topo, subtitulo):
  postit: {"linhas": [...]  texto em caneta grafite/azul (| = quebra dentro da linha),
           "destaque": frase sublinhada à mão em azul,
           "volta": linha em vermelho; {trecho} = circulado à mão em vermelho,
           "w": largura (px), "right": distância da borda direita, "bottom": distância do pé da arte,
           "rot": rotação (graus), "fs": corpo da letra}
  sub_w: largura do subtítulo (px)
  fonte_mao: lista de caminhos .woff2 da Caveat"""
import json, sys, html, base64, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI = R.AZUL, R.TINTA
AMARELO = "#FFE680"
GRAFITE = "#2B3140"   # caneta grafite
CANETA = "#1F4FD8"    # caneta azul (sublinhado)
VERMELHO = "#D62F2F"  # caneta vermelha

def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)

# fita adesiva: borda serrilhada nas pontas (rasgada à mão)
FITA_CLIP = ("polygon(0% 8%,3% 0%,6% 10%,9% 2%,12% 6%,88% 4%,91% 0%,94% 9%,97% 1%,100% 7%,"
             "98% 22%,100% 38%,97% 52%,100% 68%,98% 84%,100% 96%,96% 100%,93% 91%,90% 100%,87% 94%,"
             "13% 96%,10% 100%,7% 92%,4% 100%,1% 93%,2% 78%,0% 62%,3% 47%,0% 31%,2% 18%)")

def css(p):
    q = p["postit"]
    w, fs = q.get("w", 372), q.get("fs", 44)
    return mao(p) + f"""
.s{{display:none}}
.sub{{text-wrap:balance;position:absolute;left:72px;width:{p.get('sub_w',470)}px;bottom:{q.get('bottom',170)}px;font-size:25px;line-height:1.42;color:{TI};opacity:.72}}
.sub .fnt{{display:block;margin-top:12px;font-family:Mono;font-size:19px;letter-spacing:.06em;opacity:.75}}
.pi{{position:absolute;right:{q.get('right',84)}px;bottom:{q.get('bottom',170)}px;width:{w}px;z-index:2;
  transform:rotate({q.get('rot',-4)}deg);transform-origin:50% 60%}}
.pi .papel{{position:relative;background:{AMARELO};
  background-image:linear-gradient(176deg,rgba(255,255,255,.28) 0%,rgba(255,255,255,0) 26%),
                   linear-gradient(0deg,rgba(150,110,0,.07) 0%,rgba(150,110,0,0) 22%);
  padding:64px 26px 46px 34px;
  clip-path:polygon(0 0,100% 0,100% calc(100% - 46px),calc(100% - 46px) 100%,0 100%)}}
.pi .somb{{filter:drop-shadow(0 1px 1px rgba(40,30,0,.14)) drop-shadow(0 5px 7px rgba(40,30,0,.09)) drop-shadow(0 18px 22px rgba(40,30,0,.12))}}
.pi .dobra{{position:absolute;right:0;bottom:0;width:46px;height:46px;
  background:linear-gradient(135deg,#F2D560 0%,#E9C94A 48%,#FFF0A8 52%,#FFE680 100%);
  clip-path:polygon(0 0,100% 0,0 100%);
  filter:drop-shadow(-2px -2px 3px rgba(60,40,0,.18))}}
.pi .fita{{position:absolute;left:50%;top:-24px;width:150px;height:48px;margin-left:-75px;transform:rotate(3deg);
  background:linear-gradient(180deg,rgba(255,255,255,.70),rgba(232,230,218,.62));
  clip-path:{FITA_CLIP};box-shadow:inset 0 0 0 1px rgba(255,255,255,.3);z-index:3}}
.pi .fsomb{{position:absolute;left:50%;top:-22px;width:150px;height:48px;margin-left:-73px;transform:rotate(3deg);
  background:rgba(60,50,0,.10);clip-path:{FITA_CLIP};filter:blur(1.5px);z-index:2}}
.pi .tx{{font-family:Hand;font-weight:600;font-size:{fs}px;line-height:1.08;color:{GRAFITE};letter-spacing:.002em}}
.pi .tx p{{margin:0}}
.pi .dest{{position:relative;display:inline-block;color:{CANETA};margin-top:6px}}
.pi .dest svg{{position:absolute;left:-6px;bottom:-12px;width:calc(100% + 14px);height:20px;overflow:visible}}
.pi .tx .volta{{color:{VERMELHO};font-size:1em;margin-top:{q.get('gap',34)}px;white-space:nowrap}}
.pi .circ{{position:relative;display:inline-block;padding:0 6px;margin:0 12px 0 14px}}
.pi .circ svg{{position:absolute;left:-15px;top:-13px;width:calc(100% + 30px);height:calc(100% + 26px);overflow:visible}}
"""

SUBL = (f'<svg viewBox="0 0 200 20" preserveAspectRatio="none"><path d="M2 9 C 40 5, 90 12, 140 7 S 186 6, 198 9" '
        f'fill="none" stroke="{CANETA}" stroke-width="3.4" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
        f'<path d="M30 15 C 80 11, 130 15, 176 12" fill="none" stroke="{CANETA}" stroke-width="2.4" stroke-linecap="round" '
        f'opacity=".85" vector-effect="non-scaling-stroke"/></svg>')
# elipse imperfeita: começa embaixo à esquerda, dá a volta e passa do ponto de partida
CIRC = (f'<svg viewBox="0 0 120 60" preserveAspectRatio="none"><path d="M18 48 C 4 40, 2 20, 22 10 C 44 0, 92 1, 110 14 '
        f'C 122 24, 116 44, 94 52 C 70 60, 34 58, 14 46 C 8 41, 9 33, 16 27" fill="none" stroke="{VERMELHO}" '
        f'stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')

def bloco(p):
    q = p["postit"]
    linhas = "".join(f"<p>{html.escape(l).replace('|', '<br>')}</p>" for l in q["linhas"])
    dest = f'<span class="dest">{html.escape(q["destaque"])}{SUBL}</span>'
    v = html.escape(q["volta"]).replace("{", '<span class="circ">').replace("}", CIRC + "</span>")
    s = p.get("subtitulo", "")
    corpo, _, fonte = s.partition(" Fonte:")   # a fonte vai numa linha própria, em mono discreto
    sub = html.escape(corpo)
    if fonte:
        sub += f'<span class="fnt">Fonte:{html.escape(fonte)}</span>'
    return (f'<p class="sub">{sub}</p>'
            f'<div class="pi"><div class="fsomb"></div><div class="fita"></div>'
            f'<div class="somb"><div class="papel"><div class="tx">{linhas}{dest}<p class="volta">{v}</p></div><div class="dobra"></div></div></div></div>')

def build(p):
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_papel(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + (f"h1{{right:{p['h1_right']}px}}" if p.get('h1_right') else '') + "</style>", 1)
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1)

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
