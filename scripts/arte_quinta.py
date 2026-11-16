"""Post 2026-11-16 16h: revista escura + 'QUINTA, 8h' — o Lucas na manhã seguinte à imersão, caneca preta na mão,
QUINTA gigante atrás da cabeça. Em HTML/SVG: bilhete à mão em ciano "quarta 22h" com seta riscada apontando
para a palavra (passa ATRÁS do recorte), post-it amarelo "DIA 1/30" colado na caneca (na frente da foto),
pílula de preço e CTA do story.
Uso: python3 scripts/arte_quinta.py quinta_render.json pasta_saida
Campos extras (além dos do modelo revista):
  mao     {"texto": "quarta 22h", "x", "y" (canto sup. esq. do texto), "tam" (px), "rot" (graus), "cor"}
  seta    {"x1","y1" (início, perto do fim do texto), "x2","y2" (ponta, na palavra), "curva" (px, + = barriga p/ baixo)}
  postit  {"texto": "DIA 1/30", "x","y" (canto sup. esq.), "w" (lado, px), "rot" (graus), "tam" (px da letra)}
  preco_pilula {"texto","top","right","tam"}
  story_cta ["texto do topo", "texto do botão"]
  fonte_mao  lista de .woff2 da letra à mão (padrão: Caveat em campanhas/fontes/)"""
import json, sys, html, math, base64, pathlib, importlib.util
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "kit" if (ROOT / "kit" / "render.py").exists() else ROOT.parent / "kit"   # kit/ é gitignored
spec = importlib.util.spec_from_file_location("render", KIT / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CIANO, AMARELO, GRAFITE = "#22D3EE", "#FFE680", "#2B3140"

def fonte_mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                               ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        if not pathlib.Path(f).exists():
            continue
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)   # sem Caveat cai no Serif itálico do kit (fallback no font-family)

def nota(p):
    """Letra à mão em ciano + seta riscada (traço de giz). Entra logo depois da palavra -> fica atrás do recorte."""
    m, s = p.get("mao"), p.get("seta")
    out = ""
    if m:
        cor = m.get("cor", CIANO)
        out += (f'<div style="position:absolute;left:{m.get("x",72)}px;top:{m.get("y",128)}px;font-family:Hand,Serif;'
                f'font-style:{"normal"};font-weight:600;font-size:{m.get("tam",48)}px;line-height:1;color:{cor};'
                f'transform:rotate({m.get("rot",-4)}deg);transform-origin:0 50%;white-space:nowrap;'
                f'text-shadow:0 0 18px rgba(34,211,238,.35)">{html.escape(m.get("texto","quarta 22h"))}</div>')
    if s:
        cor = (m or {}).get("cor", CIANO)
        x1, y1, x2, y2 = s["x1"], s["y1"], s["x2"], s["y2"]
        cv = s.get("curva", 40)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        L = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L          # normal do segmento
        cx, cy = mx + nx * cv, my + ny * cv
        # direção final (tangente na ponta) para a cabeça da seta
        tx, ty = x2 - cx, y2 - cy; tl = math.hypot(tx, ty) or 1; tx, ty = tx / tl, ty / tl
        a = 26
        def rot(ang):
            c_, s_ = math.cos(ang), math.sin(ang)
            return x2 - a * (tx * c_ - ty * s_), y2 - a * (tx * s_ + ty * c_)
        (hx1, hy1), (hx2, hy2) = rot(0.5), rot(-0.5)
        out += (f'<svg style="position:absolute;left:0;top:0;width:1080px;height:1350px" viewBox="0 0 1080 1350">'
                f'<g fill="none" stroke="{cor}" stroke-linecap="round" stroke-linejoin="round" '
                f'style="filter:drop-shadow(0 0 10px rgba(34,211,238,.45))">'
                f'<path d="M{x1},{y1} Q{cx:.0f},{cy:.0f} {x2},{y2}" stroke-width="5.5"/>'
                f'<path d="M{x1+3},{y1+4} Q{cx+4:.0f},{cy+2:.0f} {x2-2},{y2+2}" stroke-width="2.2" opacity=".55"/>'
                f'<path d="M{hx1:.0f},{hy1:.0f} L{x2},{y2} L{hx2:.0f},{hy2:.0f}" stroke-width="5.5"/></g></svg>')
    return out

def postit(p):
    q = p.get("postit")
    if not q: return ""
    w = q.get("w", 132)
    return (f'<div style="position:absolute;left:{q.get("x",340)}px;top:{q.get("y",800)}px;width:{w}px;height:{w}px;z-index:4;'
            f'transform:rotate({q.get("rot",-7)}deg);filter:drop-shadow(0 2px 2px rgba(0,0,0,.35)) drop-shadow(0 10px 14px rgba(0,0,0,.35))">'
            f'<div style="position:absolute;inset:0;background:{AMARELO};'
            f'background-image:linear-gradient(176deg,rgba(255,255,255,.30) 0%,rgba(255,255,255,0) 30%),'
            f'linear-gradient(0deg,rgba(150,110,0,.10) 0%,rgba(150,110,0,0) 25%);'
            f'clip-path:polygon(0 0,100% 0,100% 100%,14% 100%,0 88%)"></div>'
            f'<div style="position:absolute;left:0;right:0;top:0;height:22%;background:rgba(150,110,0,.06)"></div>'
            f'<div style="position:absolute;inset:0;display:grid;place-items:center;text-align:center;font-family:Hand,Serif;'
            f'font-weight:600;font-size:{q.get("tam",42)}px;line-height:.95;color:{GRAFITE};padding:8px">'
            f'{html.escape(q.get("texto","DIA 1/30")).replace("|","<br>")}</div></div>')

def pilula(p):
    q = p.get("preco_pilula")
    if not q: return ""
    return (f'<div style="position:absolute;right:{q.get("right",72)}px;top:{q.get("top",900)}px;z-index:7;'
            f'background:{CIANO};color:#07080B;font-family:M;font-weight:800;font-size:{q.get("tam",34)}px;'
            f'padding:14px 28px;border-radius:999px;box-shadow:0 10px 40px rgba(34,211,238,.45)">{html.escape(q["texto"])}</div>')

def build(p):
    h = R.build(p)
    css = fonte_mao(p) + ".i{font-size:26px!important;color:#fff!important;bottom:52px!important}.i span:last-child{font-size:20px;opacity:.6}"
    h = h.replace("</style>", css + "</style>", 1)
    h = h.replace('<div class="faixa"></div>', nota(p) + '<div class="faixa"></div>', 1)
    return h.replace("</body>", postit(p) + pilula(p) + "</body>")

def story_compacto(feed, dest):
    """Story 1080x1920 com o card menor (800x1000, topo 360) para o texto e o CTA caberem na área segura."""
    from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
    art = Image.open(feed).convert("RGB")
    bg = art.resize((1536, 1920)).crop((228, 0, 1308, 1920)).filter(ImageFilter.GaussianBlur(48))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    card = art.resize((800, 1000))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, *card.size), 32, fill=255)
    bg.paste(card, (140, 360), m)
    bg.save(dest)

def story_cta(pw_browser, story_png, texto_topo, texto_cta):
    """Escreve no story (fora do card) a contagem no topo e o CTA do link na bio embaixo."""
    b64 = base64.b64encode(pathlib.Path(story_png).read_bytes()).decode()
    html_ = (f'<!doctype html><html><head><meta charset="utf-8"><style>{R.fonts()}*{{margin:0}}body{{width:1080px;height:1920px;position:relative;font-family:M}}'
             f'.t{{position:absolute;left:0;right:0;top:300px;text-align:center;font-family:Mono;letter-spacing:.14em;font-size:30px;color:{CIANO}}}'
             f'.c{{position:absolute;left:50%;transform:translateX(-50%);top:1400px;background:{CIANO};color:#07080B;font-weight:800;font-size:40px;padding:22px 46px;border-radius:999px;white-space:nowrap;box-shadow:0 10px 50px rgba(34,211,238,.5)}}</style></head>'
             f'<body><img src="data:image/png;base64,{b64}" style="position:absolute;left:0;top:0;width:1080px"><div class="t">{html.escape(texto_topo)}</div><div class="c">{html.escape(texto_cta)}</div></body></html>')
    pg = pw_browser.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(html_, wait_until="load"); pg.wait_for_timeout(300); pg.screenshot(path=str(story_png)); pg.close()

def main(spec, outdir):
    posts = json.loads(pathlib.Path(spec).read_text())
    out = pathlib.Path(outdir); out.mkdir(exist_ok=True, parents=True)
    from PIL import Image
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            story_compacto(f, out / f"{p['id']}_story.png")
            if p.get("story_cta"):
                story_cta(b, out / f"{p['id']}_story.png", p["story_cta"][0], p["story_cta"][1])
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
