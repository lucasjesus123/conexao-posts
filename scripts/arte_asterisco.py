"""Post 2026-10-28 08h: papel claro + 'o asterisco gigante' (manchete riscada x nota de rodapé com marca-texto), tudo em HTML/SVG.
Uso: python3 scripts/arte_asterisco.py post_render.json pasta_saida
Campos extras do JSON: manchete (lista de linhas), nota ({trecho} = marca-texto amarelo), ast_top/ast_tam (opcional)."""
import json, sys, html, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI = R.AZUL, R.TINTA
CINZA = "#8a867d"

def asterisco(tam, cor, traco):
    """Asterisco de 6 pontas arredondadas: 3 traços com ponta redonda a 0/60/120 graus."""
    r = 50 - traco / 2
    linhas = "".join(f'<line x1="50" y1="{50-r}" x2="50" y2="{50+r}" transform="rotate({a} 50 50)"/>' for a in (0, 60, 120))
    return (f'<svg width="{tam}" height="{tam}" viewBox="0 0 100 100"><g stroke="{cor}" stroke-width="{traco}" '
            f'stroke-linecap="round">{linhas}</g></svg>')

# risco de tinta levemente torto (esticado para a largura da linha)
RISCO = ('<svg class="risco" viewBox="0 0 1000 40" preserveAspectRatio="none"><path d="M-6 25 C 180 19, 420 23, 600 18 S 880 15, 1008 11" '
         f'fill="none" stroke="{CINZA}" stroke-width="3" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>')
# marca-texto: mancha de borda irregular
MT = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 40' preserveAspectRatio='none'>"
      "<path d='M3 9 C 40 4, 90 7, 140 4 S 190 6, 198 8 L 196 17 L 199 27 C 160 33, 110 31, 60 34 S 12 33, 2 31 L 4 21 Z' fill='%23FFE45C' fill-opacity='.72'/></svg>")

def css(p):
    t = p.get("ast_top", 120); s = p.get("ast_tam", 460)
    return f"""
.ast{{position:absolute;right:-{p.get('ast_corte',100)}px;top:{t}px;z-index:0;opacity:1}}
h1{{z-index:2}}
.k,.r,.s,.marca,.handle{{z-index:3}}
.bloco{{position:absolute;left:72px;right:72px;top:{p.get('bloco_top',500)}px;z-index:2}}
.manch{{font-family:Serif;font-weight:500;font-size:46px;line-height:1.18;color:{CINZA};letter-spacing:-.01em}}
.manch span{{position:relative;display:inline-block;white-space:nowrap}}
.risco{{position:absolute;left:-8px;right:-8px;width:calc(100% + 16px);top:4px;height:48px;overflow:visible}}
.manch span:nth-child(3) .risco{{transform:rotate(.6deg)}}
.fonte{{font-family:Mono;font-size:16px;letter-spacing:.14em;text-transform:uppercase;color:{CINZA};margin-top:20px}}
.rod{{margin-top:{p.get('respiro',150)}px}}
.filete{{width:280px;height:2px;background:{TI};margin-bottom:26px}}
.nt{{display:flex;gap:22px;align-items:flex-start}}
.nt svg{{flex:none;margin-top:2px}}
.nt p{{font-family:Mono;font-size:38px;line-height:1.45;color:{TI};letter-spacing:-.01em}}
.mt{{position:relative;white-space:nowrap}}
.mt::before{{content:"";position:absolute;left:-6px;right:-6px;top:2px;bottom:-3px;background:url("{MT}") center/100% 100% no-repeat;transform:rotate(-1.2deg);z-index:-1}}
.mt.b::before{{transform:rotate(.8deg)}}
.nt p{{position:relative;z-index:0}}
.s{{text-wrap:balance}}
"""

def bloco(p):
    linhas = "<br>".join(f"<span>{html.escape(l)}{RISCO}</span>" for l in p["manchete"])
    n = html.escape(p["nota"]); i = 0
    while "{" in n:
        n = n.replace("{", f'<span class="mt{" b" if i else ""}">', 1).replace("}", "</span>", 1); i += 1
    return (f'<div class="ast">{asterisco(p.get("ast_tam",460), AZ, 17)}</div>'
            f'<div class="bloco"><div class="manch">{linhas}</div>'
            f'<div class="rod"><div class="filete"></div><div class="nt">{asterisco(40, AZ, 17)}<p>{n}</p></div></div></div>')

def build(p):
    h = R.build(p)
    h = h.replace("</style>", css(p) + "</style>", 1)
    return h.replace('<h1>', bloco(p) + '<h1>', 1)

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(400)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
