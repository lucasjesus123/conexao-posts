"""Post 2026-10-27 08h: nota clara + 'telefone sem fio do pedido' (4 telas, 12 cx vira 21 cx) em HTML/SVG.
Uso: python3 scripts/arte_redigitacao.py post_render.json pasta_saida"""
import json, sys, base64, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
FON = ROOT / "campanhas" / "fontes"
def ff(n): return base64.b64encode((FON / n).read_bytes()).decode()
CAVEAT = (f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{ff('caveat-latin-600-normal.woff2')})}}"
          f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{ff('caveat-latin-ext-600-normal.woff2')});unicode-range:U+0100-024F}}")
AZ = R.AZUL
CSS = CAVEAT + f"""
.trilha{{position:relative;height:560px;margin-top:34px}}
.trilha svg.fio{{position:absolute;left:0;top:0;overflow:visible}}
.st{{position:absolute;width:560px;height:104px;border-radius:18px;background:#F7F6F2;border:1.5px solid rgba(11,13,18,.10);
  box-shadow:0 14px 30px rgba(0,0,0,.08);padding:14px 22px;display:flex;flex-direction:column;justify-content:center}}
.st .lb{{font-family:Mono;font-size:15px;letter-spacing:.16em;opacity:.5;margin-bottom:8px;text-transform:uppercase}}
.st .v{{font-size:27px;font-weight:600;letter-spacing:-.01em;white-space:nowrap}}
.bolha{{display:inline-block;background:#DCF8C6;border-radius:14px 14px 14px 4px;padding:6px 14px;font-size:25px;font-weight:600}}
.cel{{display:flex;gap:0}} .cel span{{border:1.5px solid rgba(11,13,18,.18);padding:4px 12px;font-size:24px;font-weight:600;background:#fff}}
.cel span+span{{border-left:none}}
.q{{position:relative;display:inline-block}}
.circ{{position:absolute;left:-6px;top:-14px;overflow:visible}}
.nota21{{position:absolute;font-family:Hand;font-weight:600;color:{AZ};font-size:40px;line-height:1;transform:rotate(-4deg);white-space:nowrap}}
.card .d{{opacity:.9;color:{AZ};font-size:24px;font-weight:500}}
.selo{{position:absolute;right:0;top:-6px;font-family:Mono;font-size:14px;letter-spacing:.16em;padding:7px 12px;border:1.5px solid rgba(11,13,18,.25);border-radius:30px;opacity:.6}}
"""
def trilha():
    xs = [0, 90, 180, 270]; ys = [0, 128, 256, 384]
    st = [
        ("WhatsApp · 07:52", '<span class="bolha">Me manda 12 cx de óleo 900ml</span>'),
        ("Planilha", '<div class="cel"><span>Óleo soja 900ml</span><span>12</span><span>R$ 7,49</span></div>'),
        ("Nota fiscal", '<div class="v">Qtd.: 12 cx</div>'),
        ("Financeiro", '<div class="v">Óleo soja 900ml · <span class="q">21 cx'
                       f'<svg class="circ" width="130" height="66" viewBox="0 0 130 66"><path d="M18 8 C 60 -6, 124 6, 120 34 C 116 62, 30 66, 10 46 C -4 30, 14 12, 44 9" fill="none" stroke="{AZ}" stroke-width="4" stroke-linecap="round"/></svg></span></div>'),
    ]
    out = ['<div class="trilha"><div class="selo">SIMULAÇÃO</div>']
    # fio tracejado ligando as telas
    pts = " ".join(f"{x+40},{y+104}" if i < 3 else "" for i, (x, y) in enumerate(zip(xs, ys)))
    path = ""
    for i in range(3):
        x0, y0 = xs[i] + 40, ys[i] + 104; x1, y1 = xs[i+1] + 40, ys[i+1]
        path += f'<path d="M{x0} {y0} C {x0} {y0+14}, {x1} {y1-14}, {x1} {y1}" fill="none" stroke="{AZ}" stroke-width="2.5" stroke-dasharray="6 7"/>'
    out.append(f'<svg class="fio" width="900" height="560">{path}</svg>')
    for (lb, v), x, y in zip(st, xs, ys):
        out.append(f'<div class="st" style="left:{x}px;top:{y}px"><div class="lb">{lb}</div>{v}</div>')
    # anotação à mão + seta
    out.append(f'<svg class="fio" width="900" height="560"><path d="M738 530 C 756 500, 722 468, 674 462" fill="none" stroke="{AZ}" stroke-width="3.5" stroke-linecap="round"/>'
               f'<path d="M688 452 L 673 462 L 686 474" fill="none" stroke="{AZ}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    out.append('<div class="nota21" style="left:250px;top:508px">ninguém errou… só digitou de novo</div>')
    out.append('</div>')
    return "".join(out)

def build(p):
    h = R.build(p)
    h = h.replace("</style>", CSS + "</style>", 1)
    return h.replace('<div class="d mono">', trilha() + '<div class="d mono">', 1)

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
