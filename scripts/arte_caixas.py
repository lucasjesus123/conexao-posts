"""Post 2026-11-01 08h: numero claro + 'A caixa que não chegou' (3 caixas entregues e 1 que não veio), tudo em HTML/SVG.
Uso: python3 scripts/arte_caixas.py post_render.json pasta_saida
Campos do JSON (além de id, modelo, pilar):
  kicker, numero ("1 em 4": a palavra do meio sai menor), texto ({trecho} = itálico azul), fonte (| = quebra)
  regua: ["01 entregue", "02 entregue", "03 entregue", "04 —"]  (o último sai em alerta)
  opcionais de ajuste: topo (número), tam (px do número), caixas_top, texto_top"""
import json, sys, html, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PAPEL = R.AZUL, R.TINTA, R.PAPEL
ALERTA = "#E5484D"
TOPO, FRENTE, LATERAL = "#E2DFD6", "#FFFFFF", "#D6D2C7"

# caixa isométrica num viewBox de 210 x 230 (frente = face esquerda, lateral = face direita)
T = "10,65 105,20 200,65 105,110"
F = "10,65 105,110 105,200 10,155"
L = "105,110 200,65 200,155 105,200"
FITA_T = "48,83 67,92 162,47 143,38"
FITA_F = "48,83 67,92 67,182 48,173"

def caixa(x):
    s = f'stroke="{TI}" stroke-width="2.6" stroke-linejoin="round"'
    return (f'<g transform="translate({x},0)">'
            f'<ellipse cx="108" cy="208" rx="98" ry="13" fill="{TI}" opacity=".10" filter="url(#bl)"/>'
            f'<polygon points="{T}" fill="{TOPO}" {s}/><polygon points="{F}" fill="{FRENTE}" {s}/>'
            f'<polygon points="{L}" fill="{LATERAL}" {s}/>'
            f'<polygon points="{FITA_T}" fill="{AZ}" stroke="{TI}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<polygon points="{FITA_F}" fill="{AZ}" stroke="{TI}" stroke-width="1.6" stroke-linejoin="round"/></g>')

def fantasma(x):
    s = f'fill="none" stroke="{ALERTA}" stroke-width="2.6" stroke-dasharray="10 8" stroke-linejoin="round" stroke-linecap="round"'
    return (f'<g transform="translate({x},0)">'
            f'<polygon points="10,65 105,20 200,65 200,155 105,200 10,155" {s}/>'
            f'<polyline points="10,65 105,110 200,65" {s}/><line x1="105" y1="110" x2="105" y2="200" {s}/>'
            f'<text x="58" y="137" text-anchor="middle" dominant-baseline="middle" font-family="Mono" font-weight="500" '
            f'font-size="64" fill="{ALERTA}">?</text></g>')

def fileira():
    passo = 242  # 4 caixas de 210 + 3 vãos de 32 = 936
    g = "".join(caixa(i * passo) for i in range(3)) + fantasma(3 * passo)
    return (f'<svg class="cx" width="936" height="230" viewBox="0 0 936 230">'
            f'<defs><filter id="bl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="5"/></filter></defs>{g}</svg>')

def numero(n):
    p = html.escape(n).split(" ")
    if len(p) == 3:
        return f'{p[0]}<span class="em">{p[1]}</span>{p[2]}'
    return html.escape(n)

def build(p):
    topo, tam = p.get("topo", 170), p.get("tam", 320)
    cx = p.get("caixas_top", 500)
    tx = p.get("texto_top", 830)
    regua = p.get("regua", ["01 entregue", "02 entregue", "03 entregue", "04 —"])
    celulas = "".join(f'<span class="{"x" if i == len(regua) - 1 else ""}">{html.escape(r)}</span>' for i, r in enumerate(regua))
    css = f"""
.k{{position:absolute;left:72px;top:80px;right:72px;font-size:19px;opacity:.6}}
.n{{position:absolute;left:60px;top:{topo}px;font-family:Anton;font-size:{tam}px;line-height:.9;letter-spacing:-.01em;white-space:nowrap}}
.n .em{{font-size:.45em;opacity:.5;margin:0 .32em 0 .28em;letter-spacing:0}}
.cx{{position:absolute;left:72px;top:{cx}px;overflow:visible}}
.rg{{position:absolute;left:72px;top:{cx + 238}px;width:936px;display:grid;grid-template-columns:repeat(4,210px);column-gap:32px;font-size:20px;letter-spacing:.08em}}
.rg span{{position:relative;text-align:center;opacity:.6}}
.rg span:not(:last-child)::after{{content:"·";position:absolute;right:-21px;top:0;opacity:.8}}
.rg span.x{{color:{ALERTA};opacity:1}}
.bar{{position:absolute;left:72px;top:{tx}px;width:180px;height:14px;background:{AZ}}}
.l{{position:absolute;left:72px;right:140px;top:{tx + 52}px;font-size:46px;font-weight:800;line-height:1.15;letter-spacing:-.02em}}
.l .it{{color:{AZ};font-size:1.04em}}
.f{{position:absolute;left:72px;right:72px;bottom:146px;font-size:17px;line-height:1.6;opacity:.55}}
"""
    fonte = html.escape(p.get("fonte", "")).replace("|", "<br>")
    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + R._base(PAPEL, TI, css) +
            f'</style></head><body><div class="grao"></div><div class="k mono">{html.escape(p.get("kicker", "Número da semana"))}</div>'
            f'<div class="n">{numero(p["numero"])}</div>{fileira()}<div class="rg mono">{celulas}</div>'
            f'<div class="bar"></div><div class="l">{R._ed(p["texto"])}</div>'
            f'<div class="f mono">{fonte}</div>{R._rodape(True)}</body></html>')

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(500)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
