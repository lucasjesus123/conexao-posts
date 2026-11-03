"""Post 2026-11-03 16h: painel3d escuro + 'Não mexer' (sistemas).
Painel 'Inventário de gambiarras' com 2 cards de check verde e 1 card com '?' (custo nunca calculado), gráfico plano
'O custo que ninguém vê' (linha reta visível + curva fantasma tracejada subindo, sem números). Engrenagem de vidro rachada
presa com silver tape (objeto) embaixo à direita, quebrando a moldura do painel, com 'NÃO MEXER' escrito a canetão
sobre a tira de fita mais clara e um arco fino ciano com seta sugerindo que ela gira.
Uso: python3 scripts/arte_naomexer.py post_render.json pasta_saida
Campos do JSON (além dos do painel3d: titulo, tam, chips, cards, painel_titulo, grafico_titulo, cta, nota, selo, objeto):
  apoio: linha de apoio; {trecho} = marca-texto ciano, | = quebra
  chips: [[icone, texto]] x4; o 4º chip sai em vermelho tracejado (o custo)
  cards: [[icone, "✓" ou "?", "Rótulo: descrição"]] x3 (o ":" separa negrito e descrição)
  obj_x, obj_y, obj_w, obj_rot: posição do objeto 3D (px no feed 1080x1350; o PNG é 900x1200)
  fita_txt, fita_x, fita_y, fita_rot, fita_tam: texto a canetão e sua posição em px DO PNG do objeto (centro), rotação, tamanho
  arco: true/false; arco_r, arco_de, arco_ate: raio (px do PNG) e ângulos (graus, sentido horário a partir das 3h)
  chips_w, sb_tam, chip_tam, txt_top, painel_pr, cta_seta (false tira a seta), css_extra"""
import json, sys, html, re, math, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI, AZ = R.CIANO, R.AZUL
VERDE = "#5BE38C"
ALERTA = "#FF6B6B"
ENG_C = (470, 610)  # centro da engrenagem no PNG 900x1200

def check(t=22, cor="#06120B", w=3):
    return (f'<svg width="{t}" height="{t}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>')

def apoio(t):
    s = html.escape(t).replace("|", "<br>")
    return s.replace("{", '<span class="mk">').replace("}", "</span>")

def chips(p):
    out = []
    for n, (ic, t) in enumerate(p.get("chips", [])[:4]):
        ult = n == 3
        out.append(f'<div class="vidro chip{" vao" if ult else ""}">{R.icone(ic, ALERTA if ult else CI, 28)}<span>{html.escape(t)}</span></div>')
    return "".join(out)

def cards(p):
    out = ""
    for ic, v, rot in p.get("cards", [])[:3]:
        a, _, b = rot.partition(":")
        duvida = v.strip() != "✓"
        badge = f'<div class="okb q">{html.escape(v.strip())}</div>' if duvida else f'<div class="okb">{check(26)}</div>'
        out += (f'<div class="vidro kp2{" dv" if duvida else ""}"><div class="ki">{R.icone(ic, ALERTA if duvida else CI, 26)}</div>'
                f'<div class="kt"><b>{html.escape(a.strip())}</b><small>{html.escape(b.strip())}</small></div>{badge}</div>')
    return out

# custo: linha plana (o que se vê) + curva fantasma tracejada que sobe por baixo (o que ninguém vê); sem eixo, sem número
GRAF = f"""<svg width="100%" height="150" viewBox="0 0 440 150" style="overflow:visible">
<defs><linearGradient id="fa" x1="0" x2="1"><stop offset="0" stop-color="{ALERTA}" stop-opacity=".05"/><stop offset="1" stop-color="{ALERTA}" stop-opacity=".75"/></linearGradient>
<linearGradient id="fb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ALERTA}" stop-opacity=".16"/><stop offset="1" stop-color="{ALERTA}" stop-opacity="0"/></linearGradient></defs>
<g stroke="rgba(255,255,255,.07)" stroke-width="1.5"><path d="M0 35H440M0 80H440M0 125H440"/></g>
<path d="M0 118 C 120 116, 220 104, 300 74 S 400 20, 440 8 L440 150 L0 150Z" fill="url(#fb)"/>
<path d="M0 118 C 120 116, 220 104, 300 74 S 400 20, 440 8" fill="none" stroke="url(#fa)" stroke-width="3.5" stroke-dasharray="2 9" stroke-linecap="round"/>
<path d="M0 118 L440 118" stroke="{CI}" stroke-width="5" stroke-linecap="round"/>
<circle cx="440" cy="118" r="7" fill="#06070B" stroke="{CI}" stroke-width="4"/>
</svg>"""

def arco(p):
    if p.get("arco") is False: return ""
    cx, cy = ENG_C; r = p.get("arco_r", 430)
    a0, a1 = math.radians(p.get("arco_de", 150)), math.radians(p.get("arco_ate", 215))
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    # seta na ponta (direção tangente, sentido horário)
    tx, ty = -math.sin(a1), math.cos(a1)
    nx, ny = math.cos(a1), math.sin(a1)
    L, W = 34, 20
    pa = (x1 - tx * L + nx * W, y1 - ty * L + ny * W); pb = (x1 - tx * L - nx * W, y1 - ty * L - ny * W)
    return (f'<svg class="arco" width="900" height="1200" viewBox="0 0 900 1200"><defs><linearGradient id="ag" gradientUnits="userSpaceOnUse" '
            f'x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}"><stop offset="0" stop-color="{CI}" stop-opacity="0"/><stop offset="1" stop-color="{CI}"/></linearGradient></defs>'
            f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="url(#ag)" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{pa[0]:.1f} {pa[1]:.1f} L{x1:.1f} {y1:.1f} L{pb[0]:.1f} {pb[1]:.1f}" fill="none" stroke="{CI}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def objeto(p):
    w = p.get("obj_w", 520); s = w / 900
    fx, fy = p.get("fita_x", 420), p.get("fita_y", 617)
    txt = html.escape(p.get("fita_txt", "NÃO MEXER"))
    return (f'<div class="objw"><div class="esc" style="transform:scale({s:.4f})">{arco(p)}'
            f'<img src="{R.b64(p["objeto"], "image/png")}">'
            f'<div class="fita" style="left:{fx}px;top:{fy}px">{txt}</div></div></div>')

def css(p):
    x, y, w, rot = p.get("obj_x", 560), p.get("obj_y", 720), p.get("obj_w", 520), p.get("obj_rot", 0)
    return f"""
.txt{{top:{p.get('txt_top', 190)}px!important}}
.sb{{font-size:{p.get('sb_tam', 30)}px!important;line-height:1.38}}
.sb .mk{{color:#fff;font-weight:800;background:linear-gradient(transparent 58%,rgba(34,211,238,.55) 58%);padding:0 4px;margin:0 -2px}}
.chips{{grid-template-columns:1fr 1fr!important;column-gap:16px!important;row-gap:16px!important;width:{p.get('chips_w', 600)}px!important}}
.chip{{font-size:{p.get('chip_tam', 22)}px!important;padding:18px 18px!important;gap:12px!important;white-space:nowrap}}
.chip.vao{{background:rgba(255,107,107,.05)!important;border:2px dashed rgba(255,107,107,.55)!important;box-shadow:none!important;color:rgba(255,255,255,.88)}}
.painel{{padding-right:{p.get('painel_pr', 110)}px!important}}
.ph{{white-space:nowrap}}
.kps{{display:flex!important;flex-direction:column;gap:12px}}
.kp2{{display:flex;align-items:center;gap:16px;padding:16px 18px;border-radius:20px}}
.kp2 .ki{{flex:none;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:rgba(34,211,238,.10)}}
.kp2.dv{{border:2px dashed rgba(255,107,107,.5)!important;background:rgba(255,107,107,.05)!important}}
.kp2.dv .ki{{background:rgba(255,107,107,.12)}}
.kp2 .kt{{flex:1;min-width:0}} .kp2 b{{display:block;font-size:23px;font-weight:800;line-height:1.1}}
.kp2 small{{display:block;font-size:17px;color:rgba(255,255,255,.8);margin-top:3px;line-height:1.25}}
.kp2 .okb{{flex:none;width:52px;height:52px;border-radius:50%;display:grid;place-items:center;background:{VERDE};box-shadow:0 0 22px rgba(91,227,140,.45)}}
.kp2 .okb.q{{background:{ALERTA};box-shadow:0 0 22px rgba(255,107,107,.45);color:#1A0606;font-weight:900;font-size:30px}}
.linha small{{font-size:19px!important;color:rgba(255,255,255,.75)!important;font-weight:600}}
.obj{{display:none!important}}
.objw{{position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w*4/3:.0f}px;transform:rotate({rot}deg);z-index:4;
  filter:drop-shadow(0 30px 50px rgba(0,0,0,.55)) drop-shadow(0 0 40px rgba(34,211,238,.30))}}
.esc{{position:absolute;left:0;top:0;width:900px;height:1200px;transform-origin:0 0}}
.esc img{{position:absolute;left:0;top:0;width:900px;height:1200px}}
.esc .arco{{position:absolute;left:0;top:0;overflow:visible}}
.fita{{position:absolute;transform:translate(-50%,-50%) rotate({p.get('fita_rot', 31)}deg);font-family:{p.get("fita_fonte", "M")};font-weight:900;font-size:{p.get("fita_tam", 80)}px;
  line-height:1.2;padding-top:.06em;letter-spacing:-.01em;color:#111;white-space:nowrap;opacity:.9;mix-blend-mode:multiply;
  text-shadow:1px 0 0 rgba(17,17,17,.6),-1px 1px 0 rgba(17,17,17,.35)}}
.sel{{font-size:22px!important;color:rgba(255,255,255,.85)!important;padding:10px 18px;border:1.5px solid rgba(34,211,238,.6);border-radius:40px;background:rgba(6,7,11,.55);top:74px!important}}
{p.get('css_extra', '')}
"""

JS = """<script>
document.fonts.ready.then(function(){
  window.__boxes=['.lgt','.sel','.txt','.hd','.sb','.chips','.cta3','.palco','.objw','.fita','.nota'].map(s=>{const e=document.querySelector(s); if(!e) return s+' -'; const b=e.getBoundingClientRect();
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
