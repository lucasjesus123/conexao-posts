"""Post 2026-11-01 16h: painel3d escuro + 'O elo que ninguém assina' (institucional).
Painel 'Reunião de fim de mês' com 3 cards de check verde (sem número), gráfico da venda que sobe até a metade
e termina num '?' branco; a linha cai do painel até o elo aberto da corrente 3D (objeto) no canto inferior direito.
Uso: python3 scripts/arte_elo.py post_render.json pasta_saida
Campos do JSON (além dos do painel3d: titulo, tam, chips, cards, painel_titulo, grafico_titulo, cta, nota, selo, objeto):
  apoio: linha de apoio; {trecho} = marca-texto ciano, | = quebra
  chips: [[icone, texto]] x4; "✓" sai verde; o 4º chip sai tracejado (o vão) e há um traço tracejado entre o 3º e o 4º
  cards: [[icone, "✓", "Rótulo: descrição"]] x3 (o ":" separa negrito e descrição)
  obj_x, obj_y, obj_w, obj_rot: posição do objeto 3D (px no feed 1080x1350)
  elo_x, elo_y: ponto (no feed) onde fica o buraco do elo aberto; a linha da venda cai até ali
  chips_w: largura da grade de chips; cta_seta: false tira a seta do botão; css_extra: CSS livre
  sb_tam, chip_tam: tamanhos opcionais do apoio e dos chips; txt_top: topo da coluna de texto; painel_pr: folga à direita do painel (px)"""
import json, sys, html, re, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI, AZ = R.CIANO, R.AZUL
VERDE = "#5BE38C"
ALERTA = "#FF6B6B"

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
        txt = html.escape(t).replace("✓", f'<em class="ok">{check(20, VERDE, 3.2)}</em>')
        out.append(f'<div class="vidro chip{" vao" if ult else ""}">{R.icone(ic, ALERTA if ult else CI, 28)}<span>{txt}</span></div>')
    if len(out) == 4:  # traço tracejado no vão entre o 3º e o 4º
        out.insert(3, '<i class="gap"></i>')
    return "".join(out)

def cards(p):
    out = ""
    for ic, _v, rot in p.get("cards", [])[:3]:
        a, _, b = rot.partition(":")
        out += (f'<div class="vidro kp2"><div class="ki">{R.icone(ic, CI, 26)}</div>'
                f'<div class="kt"><b>{html.escape(a.strip())}</b><small>{html.escape(b.strip())}</small></div>'
                f'<div class="okb">{check(26)}</div></div>')
    return out

# venda: sobe da esquerda até a metade e para; ponto oco no fim + "?" grande; sem eixo de valor
GRAF = f"""<svg width="100%" height="190" viewBox="0 0 440 190" style="overflow:visible">
<defs><linearGradient id="ar2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CI}" stop-opacity=".45"/><stop offset="1" stop-color="{CI}" stop-opacity="0"/></linearGradient>
<linearGradient id="ln2" x1="0" x2="1"><stop offset="0" stop-color="{AZ}"/><stop offset="1" stop-color="{CI}"/></linearGradient></defs>
<g stroke="rgba(255,255,255,.08)" stroke-width="1.5"><path d="M0 40H440M0 90H440M0 140H440"/></g>
<path d="M0 170 C 40 165, 70 140, 105 142 S 165 110, 200 96 L200 190 L0 190Z" fill="url(#ar2)"/>
<path d="M0 170 C 40 165, 70 140, 105 142 S 165 110, 200 96" fill="none" stroke="url(#ln2)" stroke-width="5" stroke-linecap="round"/>
<path d="M210 92 L440 92" stroke="rgba(255,255,255,.16)" stroke-width="2.5" stroke-dasharray="3 10" stroke-linecap="round"/>
<circle id="fim" cx="200" cy="96" r="9" fill="#06070B" stroke="{CI}" stroke-width="4"/>
<text x="236" y="150" font-family="M" font-weight="900" font-size="150" fill="#fff" style="filter:drop-shadow(0 0 18px rgba(34,211,238,.45))">?</text>
</svg>"""

def css(p):
    x, y, w, rot = p.get("obj_x", 560), p.get("obj_y", 820), p.get("obj_w", 560), p.get("obj_rot", 0)
    return f"""
.txt{{top:{p.get('txt_top', 190)}px!important}}
.sb{{font-size:{p.get('sb_tam', 30)}px!important;line-height:1.38}}
.sb .mk{{color:#fff;font-weight:800;background:linear-gradient(transparent 58%,rgba(34,211,238,.55) 58%);padding:0 4px;margin:0 -2px}}
.chips{{grid-template-columns:1fr 1fr!important;column-gap:40px!important;row-gap:16px!important;position:relative}}
.chip{{font-size:{p.get('chip_tam', 23)}px!important;padding:18px 18px!important;gap:12px!important;white-space:nowrap}}
.chip .ok{{display:inline-flex;vertical-align:-2px;margin-left:6px}}
.chip.vao{{background:rgba(255,107,107,.05)!important;border:2px dashed rgba(255,107,107,.55)!important;box-shadow:none!important;color:rgba(255,255,255,.82)}}
.chips .gap{{position:absolute;left:calc(50% - 20px);width:40px;bottom:35px;height:0;border-top:3px dashed rgba(255,107,107,.75)}}
.painel{{padding-right:{p.get('painel_pr', 110)}px!important}}
.ph{{white-space:nowrap}}
.kps{{display:flex!important;flex-direction:column;gap:12px}}
.kp2{{display:flex;align-items:center;gap:16px;padding:16px 18px;border-radius:20px}}
.kp2 .ki{{flex:none;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:rgba(34,211,238,.10)}}
.kp2 .kt{{flex:1;min-width:0}} .kp2 b{{display:block;font-size:23px;font-weight:800;line-height:1.1}}
.kp2 small{{display:block;font-size:17px;color:rgba(255,255,255,.62);margin-top:3px}}
.kp2 .okb{{flex:none;width:52px;height:52px;border-radius:50%;display:grid;place-items:center;background:{VERDE};box-shadow:0 0 22px rgba(91,227,140,.45)}}
.linha small{{font-size:19px!important;color:rgba(255,255,255,.75)!important;font-weight:600}}
.obj{{left:{x}px!important;top:{y}px!important;right:auto!important;bottom:auto!important;width:{w}px!important;transform:rotate({rot}deg);z-index:4!important}}
svg.queda{{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:3;pointer-events:none;overflow:visible}}
.sel{{font-size:22px!important;color:rgba(255,255,255,.85)!important;padding:10px 18px;border:1.5px solid rgba(34,211,238,.6);border-radius:40px;background:rgba(6,7,11,.55);top:74px!important}}
.kp2 small{{color:rgba(255,255,255,.8)!important}}
.chips{{width:{p.get('chips_w', 600)}px!important}}
{p.get('css_extra', '')}
"""

JS = """<script>
document.fonts.ready.then(function(){
  const NS='http://www.w3.org/2000/svg', sv=document.createElementNS(NS,'svg'); sv.setAttribute('class','queda'); document.body.appendChild(sv);
  const r=document.getElementById('fim').getBoundingClientRect(), x1=r.left+r.width/2, y1=r.bottom, x2=__EX__, y2=__EY__;
  sv.innerHTML=`<defs><linearGradient id="qd" gradientUnits="userSpaceOnUse" x1="0" y1="${y1}" x2="0" y2="${y2}">
    <stop offset="0" stop-color="__CI__"/><stop offset="1" stop-color="__CI__" stop-opacity=".25"/></linearGradient></defs>
    <path d="M${x1} ${y1} C ${x1} ${y1+(y2-y1)*.45}, ${x2} ${y2-(y2-y1)*.5}, ${x2} ${y2}" fill="none" stroke="url(#qd)" stroke-width="3.2" stroke-dasharray="2 9" stroke-linecap="round"/>`;
  window.__boxes=['.lgt','.sel','.txt','.hd','.sb','.chips','.cta3','.palco','.obj','.nota','#fim'].map(s=>{const e=document.querySelector(s); if(!e) return s+' -'; const b=e.getBoundingClientRect();
    return s+' '+[b.left,b.top,b.right,b.bottom].map(Math.round).join(',');});
  document.querySelectorAll('.chip,.kp2 b,.kp2 small,.hd').forEach(e=>{ if(e.scrollWidth>e.clientWidth+1) window.__boxes.push('ESTOURO '+e.className+' '+e.textContent); });
});
</script>""".replace("__CI__", CI)

def build(p):
    base = dict(p, subtitulo="__SB__", chips=[], cards=[])
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_painel3d(base, R.PILARES["sistemas"]) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    h = h.replace("__SB__", apoio(p.get("apoio", "")), 1)
    h = h.replace('<div class="chips"></div>', f'<div class="chips">{chips(p)}</div>', 1)
    h = h.replace('<div class="kps"></div>', f'<div class="kps">{cards(p)}</div>', 1)
    h = re.sub(r'<svg width="100%" height="150".*?</svg>', lambda m: GRAF, h, count=1, flags=re.S)
    if p.get('cta_seta') is False: h = h.replace(' →</div>', '</div>', 1)
    js = JS.replace("__EX__", str(p.get("elo_x", 840))).replace("__EY__", str(p.get("elo_y", 1010)))
    return h.replace("</body>", js + "</body>", 1)

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
