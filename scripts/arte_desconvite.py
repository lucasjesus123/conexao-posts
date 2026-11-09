"""Post 2026-11-09 16h: revista escura + 'Convite rasgado' — o Lucas rasga o convite e a palavra gigante atrás
da cabeça leva um risco de caneta vermelha (passa ATRÁS do recorte), mais pílula de preço em CSS.
Uso: python3 scripts/arte_desconvite.py post_render.json pasta_saida
Campos extras: risco {"y": centro vertical do traço, "x1", "x2"}, preco_pilula {"texto", "top", "right"}"""
import json, sys, pathlib, importlib.util
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)

def risco(p):
    r = p.get("risco", {})
    y, x1, x2 = r.get("y", 300), r.get("x1", 40), r.get("x2", 1040)
    d = (f"M{x1},{y+18} C{x1+180},{y-6} {x1+330},{y+22} {(x1+x2)//2},{y+4} "
         f"S{x2-160},{y-20} {x2},{y-8}")
    d2 = f"M{x1+60},{y+44} C{x1+300},{y+20} {x2-300},{y+34} {x2-40},{y+12}"
    return (f'<svg style="position:absolute;left:0;top:0;width:1080px;height:1350px" viewBox="0 0 1080 1350">'
            f'<path d="{d}" fill="none" stroke="#FF3B3B" stroke-width="30" stroke-linecap="round" opacity=".95"/>'
            f'<path d="{d2}" fill="none" stroke="#FF3B3B" stroke-width="16" stroke-linecap="round" opacity=".8"/></svg>')

def pilula(p):
    q = p.get("preco_pilula")
    if not q: return ""
    return (f'<div style="position:absolute;right:{q.get("right",72)}px;top:{q.get("top",900)}px;z-index:7;'
            f'background:#22D3EE;color:#07080B;font-family:M;font-weight:800;font-size:{q.get("tam",34)}px;'
            f'padding:14px 28px;border-radius:999px;box-shadow:0 10px 40px rgba(34,211,238,.45)">{q["texto"]}</div>')

def build(p):
    h = R.build(p)
    css = ".i{font-size:26px!important;color:#fff!important;bottom:52px!important}.i span:last-child{font-size:20px;opacity:.6}"
    h = h.replace("</style>", css + "</style>", 1)
    return h.replace('<div class="faixa"></div>', risco(p) + '<div class="faixa"></div>', 1).replace("</body>", pilula(p) + "</body>")

def story_cta(pw_browser, story_png, texto_topo, texto_cta):
    """Escreve no story (abaixo do card) a contagem e o CTA do link na bio."""
    import base64
    b64 = base64.b64encode(pathlib.Path(story_png).read_bytes()).decode()
    fonts = R.fonts()
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts}*{{margin:0}}body{{width:1080px;height:1920px;position:relative;font-family:M}}'
            f'.t{{position:absolute;left:0;right:0;top:230px;text-align:center;font-family:Mono;letter-spacing:.14em;font-size:30px;color:#22D3EE}}'
            f'.c{{position:absolute;left:50%;transform:translateX(-50%);top:1610px;background:#22D3EE;color:#07080B;font-weight:800;font-size:40px;padding:22px 46px;border-radius:999px;white-space:nowrap;box-shadow:0 10px 50px rgba(34,211,238,.5)}}</style></head>'
            f'<body><img src="data:image/png;base64,{b64}" style="position:absolute;left:0;top:0;width:1080px"><div class="t">{texto_topo}</div><div class="c">{texto_cta}</div></body></html>')
    pg = pw_browser.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(html, wait_until="load"); pg.wait_for_timeout(300); pg.screenshot(path=str(story_png)); pg.close()

def main(spec, outdir):
    posts = json.loads(pathlib.Path(spec).read_text())
    out = pathlib.Path(outdir); out.mkdir(exist_ok=True, parents=True)
    from PIL import Image
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(300)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            if p.get("story_cta"):
                story_cta(b, out / f"{p['id']}_story.png", p["story_cta"][0], p["story_cta"][1])
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
