"""Post 2026-11-08 16h: painel3d escuro + 'caminho de desejo' (institucional).
Diorama 3D (campanhas/assets/caminho_desejo3d.png, 1176x978): calçada de vidro ciano (o sistema) e, cortando o gramado,
uma trilha de terra gasta (o caminho que a equipe faz). Anotações à mão em SVG por cima do objeto:
'o sistema' apontando a calçada vazia, 'a equipe' apontando a trilha, e um pontilhado ciano sobre a trilha
com 'a gente pavimenta aqui ✓'. Painel: 'O caminho real', 3 cards com check, gráfico 'previsto' (reto, cinza tracejado)
x 'real' (ciano, torto mas contínuo). Sem números.
Uso: python3 scripts/arte_caminho.py post_render.json pasta_saida
Campos extras: apoio ({trecho} = marca-texto, | = quebra), obj_x, obj_y, obj_w, obj_rot, notas [[texto, x, y, rot, cor]] em px do PNG,
setas [[x0,y0,cx,cy,x1,y1,cor]] (curva quadrática em px do PNG), trilha [[x,y]...] (pontilhado ciano), txt_top, sb_tam, chip_tam, css_extra"""
import json, sys, html, re, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI = R.CIANO
VERDE = "#5BE38C"
PW, PH = 1176, 978


def check(t=22, cor="#06120B", w=3):
    return (f'<svg width="{t}" height="{t}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>')


def apoio(t):
    s = html.escape(t).replace("|", "<br>")
    return s.replace("{", '<span class="mk">').replace("}", "</span>")


def chips(p):
    return "".join(f'<div class="vidro chip">{R.icone(ic, CI, 28)}<span>{html.escape(t)}</span></div>' for ic, t in p.get("chips", [])[:4])


def cards(p):
    out = ""
    for ic, v, rot in p.get("cards", [])[:3]:
        a, _, b = rot.partition(":")
        out += (f'<div class="vidro kp2"><div class="ki">{R.icone(ic, CI, 26)}</div>'
                f'<div class="kt"><b>{html.escape(a.strip())}</b><small>{html.escape(b.strip())}</small></div>'
                f'<div class="okb">{check(26)}</div></div>')
    return out


GRAF = f"""<svg width="100%" height="150" viewBox="0 0 440 150" style="overflow:visible">
<defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CI}" stop-opacity=".35"/><stop offset="1" stop-color="{CI}" stop-opacity="0"/></linearGradient></defs>
<g stroke="rgba(255,255,255,.07)" stroke-width="1.5"><path d="M0 35H440M0 80H440M0 125H440"/></g>
<path d="M0 120 L440 40" stroke="rgba(255,255,255,.45)" stroke-width="4" stroke-dasharray="10 10" stroke-linecap="round"/>
<path d="M0 120 C 30 95, 60 130, 95 100 S 150 60, 185 95 S 250 120, 280 70 S 350 30, 380 60 S 420 30, 440 22 L440 150 L0 150Z" fill="url(#rg)"/>
<path d="M0 120 C 30 95, 60 130, 95 100 S 150 60, 185 95 S 250 120, 280 70 S 350 30, 380 60 S 420 30, 440 22" fill="none" stroke="{CI}" stroke-width="5" stroke-linecap="round"/>


</svg>"""


def anot(p):
    s = [f'<svg class="anot" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" style="overflow:visible">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
         '<path d="M1 1L8 5L1 9" fill="none" stroke="context-stroke" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>']
    tr = p.get("trilha")
    if tr:
        d = "M" + " L".join(f"{x} {y}" for x, y in tr)
        s.append(f'<path d="{d}" fill="none" stroke="{CI}" stroke-width="9" stroke-dasharray="2 20" stroke-linecap="round" '
                 f'style="filter:drop-shadow(0 0 8px {CI})"/>')
    for x0, y0, cx, cy, x1, y1, cor in p.get("setas", []):
        s.append(f'<path d="M{x0} {y0} Q{cx} {cy} {x1} {y1}" fill="none" stroke="{cor}" stroke-width="6" stroke-linecap="round" marker-end="url(#ah)"/>')
    s.append("</svg>")
    for t, x, y, rot, cor in p.get("notas", []):
        s.append(f'<div class="nt" style="left:{x}px;top:{y}px;transform:rotate({rot}deg);color:{cor}">{html.escape(t)}</div>')
    return "".join(s)


def objeto(p):
    w = p.get("obj_w", 640); sc = w / PW
    return (f'<div class="objw"><div class="esc" style="transform:scale({sc:.4f})">'
            f'<img src="{R.b64(p["objeto"], "image/png")}">{anot(p)}</div></div>')


def css(p):
    x, y, w, rot = p.get("obj_x", 440), p.get("obj_y", 800), p.get("obj_w", 640), p.get("obj_rot", 0)
    return f"""
.txt{{top:{p.get('txt_top', 190)}px!important}}
.sb{{font-size:{p.get('sb_tam', 30)}px!important;line-height:1.38}}
.sb .mk{{color:#fff;font-weight:800;background:linear-gradient(transparent 58%,rgba(34,211,238,.55) 58%);padding:0 4px;margin:0 -2px}}
.chips{{grid-template-columns:auto auto!important;justify-content:start;column-gap:14px!important;row-gap:14px!important}}
.chip{{font-size:{p.get('chip_tam', 21)}px!important;padding:16px 16px!important;gap:10px!important;white-space:nowrap}}
.ph{{white-space:nowrap}}
.kps{{display:flex!important;flex-direction:column;gap:12px}}
.kp2{{display:flex;align-items:center;gap:16px;padding:16px 18px;border-radius:20px}}
.kp2 .ki{{flex:none;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:rgba(34,211,238,.10)}}
.kp2 .kt{{flex:1;min-width:0}} .kp2 b{{display:block;font-size:23px;font-weight:800;line-height:1.1}}
.kp2 small{{display:block;font-size:18px;color:rgba(255,255,255,.8);margin-top:3px;line-height:1.25}}
.kp2 .okb{{flex:none;width:48px;height:48px;border-radius:50%;display:grid;place-items:center;background:{VERDE};box-shadow:0 0 22px rgba(91,227,140,.45)}}
.linha small{{font-size:19px!important;color:rgba(255,255,255,.75)!important;font-weight:600}}
.obj{{display:none!important}}
.objw{{position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w*PH/PW:.0f}px;transform:rotate({rot}deg);z-index:4;
  filter:drop-shadow(0 30px 50px rgba(0,0,0,.55)) drop-shadow(0 0 40px rgba(34,211,238,.25))}}
.esc{{position:absolute;left:0;top:0;width:{PW}px;height:{PH}px;transform-origin:0 0}}
.esc img{{position:absolute;left:0;top:0;width:{PW}px;height:{PH}px}}
.esc .anot{{position:absolute;left:0;top:0}}
.nt{{position:absolute;font-family:Serif;font-style:italic;font-weight:500;font-size:{p.get('nt_tam', 56)}px;white-space:nowrap;line-height:1;
  text-shadow:0 2px 14px rgba(0,0,0,.95),0 0 4px rgba(0,0,0,.9);transform-origin:0 50%}}
.sel{{font-size:20px!important;color:rgba(255,255,255,.85)!important;padding:10px 18px;border:1.5px solid rgba(34,211,238,.6);border-radius:40px;background:rgba(6,7,11,.55);top:74px!important}}
.nota{{display:none!important}}
{p.get('css_extra', '')}
"""


JS = """<script>
document.fonts.ready.then(function(){
  window.__boxes=['.lgt','.sel','.txt','.hd','.sb','.chips','.cta3','.palco','.objw'].map(s=>{const e=document.querySelector(s); if(!e) return s+' -'; const b=e.getBoundingClientRect();
    return s+' '+[b.left,b.top,b.right,b.bottom].map(Math.round).join(',');});
  document.querySelectorAll('.chip,.kp2 b,.kp2 small,.hd,.ph').forEach(e=>{ if(e.scrollWidth>e.clientWidth+1) window.__boxes.push('ESTOURO '+e.className+' '+e.textContent); });
});
</script>"""


def build(p):
    base = dict(p, subtitulo="__SB__", chips=[], cards=[])
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_painel3d(base, R.PILARES[p.get("pilar", "sistemas")]) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    h = h.replace("__SB__", apoio(p.get("apoio", "")), 1)
    h = h.replace('<div class="chips"></div>', f'<div class="chips">{chips(p)}</div>', 1)
    h = h.replace('<div class="kps"></div>', f'<div class="kps">{cards(p)}</div>', 1)
    h = re.sub(r'<svg width="100%" height="150".*?</svg>', lambda m: GRAF, h, count=1, flags=re.S)
    if p.get('cta_seta') is False: h = h.replace(' →</div>', '</div>', 1)
    h = h.replace('<div class="txt">', objeto(p) + '<div class="txt">', 1)
    return h.replace("</body>", JS + "</body>", 1)


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(600)
            for l in pg.evaluate("window.__boxes||[]"): print("  ", l)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
