"""Post 2026-11-04 16h: flutuante + 'A linha que atravessa o Lucas' (imersão, reembolso até 18/11).
Lucas (recorte) aponta com o dedo para o card 18/11. Uma linha do tempo de luz ciano cruza a arte na diagonal
(alto à esquerda -> embaixo à direita): nó HOJE (card atrás, alto), 14 tiques acesos até o nó 18/11 (na altura do dedo)
com a anotação '14 dias pra mudar de ideia', e segue até o nó 25/11 (card à frente). A linha passa ATRÁS do braço dele e
volta À FRENTE do tronco (o trecho final é desenhado de novo numa camada acima do recorte).
Uso: python3 scripts/arte_linha_tempo.py post_render.json pasta_saida   (JSON = um objeto ou uma lista de objetos)
Saída: pasta_saida/ID.png, ID.jpg e ID_story.png (igual ao kit/render.py)
Campos (além dos do flutuante: recorte, x, y, w, anel_x, anel_y, cards_atras, cards_frente, titulo, subtitulo, tam,
txt_bottom, tag, info, preco):
  linha: {
    hoje:   [x, y]  nó do HOJE (px do feed 1080x1350)
    prazo:  [x, y]  nó do 18/11 (logo além da ponta do dedo)
    evento: [x, y]  nó do 25/11
    tiques: 14      tiques acesos, distribuídos por igual ENTRE hoje e prazo
    frente_de: 0.35 fração do trecho prazo->evento a partir da qual a linha passa à frente do Lucas
    nota: "14 dias pra mudar de ideia", nota_t: 0.5 (posição ao longo de hoje->prazo), nota_off: 42 (px acima da linha), nota_tam: 19
  }
  rosto: [l, t, r, b]  opcional: caixa do rosto no feed; o script avisa se texto, card ou linha encostar nela
  sb_tam, info_tam, preco_tam, css_extra"""
import json, sys, html, math, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI, AZ = R.CIANO, R.AZUL

LINHA_PADRAO = {"hoje": [90, 330], "prazo": [445, 540], "evento": [720, 703], "tiques": 14, "frente_de": 0.35,
                "nota": "14 dias pra mudar de ideia", "nota_t": 0.5, "nota_off": 42, "nota_tam": 19}

def _L(p):
    return {**LINHA_PADRAO, **p.get("linha", {})}

def _lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def _defs(uid):
    return (f'<defs><filter id="bl{uid}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="7"/></filter>'
            f'<filter id="bt{uid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter></defs>')

def _traco(a, b, uid, op0=1, op1=1, w=4):
    """Traço com halo: camada borrada larga + núcleo fino claro."""
    gid = f"lg{uid}"
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}">'
            f'<stop offset="0" stop-color="{CI}" stop-opacity="{op0}"/><stop offset="1" stop-color="{CI}" stop-opacity="{op1}"/></linearGradient>'
            f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="url(#{gid})" stroke-width="{w * 4}" stroke-linecap="round" filter="url(#bl{uid[0]})" opacity=".55"/>'
            f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="url(#{gid})" stroke-width="{w}" stroke-linecap="round"/>')

def _no(c, r, cheio=False):
    x, y = c
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.2:.1f}" fill="{CI}" opacity=".18"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{CI if cheio else "#06070B"}" stroke="{CI}" stroke-width="4"/>'
            + ("" if cheio else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .38:.1f}" fill="#fff"/>'))

def linha_atras(p):
    """Linha inteira (camada sob o recorte): cauda que surge do nada antes do HOJE, 14 tiques, nós e o fim após o 25/11."""
    L = _L(p); h, z, e = L["hoje"], L["prazo"], L["evento"]
    dx, dy = z[0] - h[0], z[1] - h[1]; n = math.hypot(dx, dy); ux, uy = dx / n, dy / n; nx, ny = -uy, ux
    ini = (h[0] - ux * 260, h[1] - uy * 260)
    fim = (e[0] + (e[0] - z[0]) * .25, e[1] + (e[1] - z[1]) * .25)
    s = _defs("a")
    s += _traco(ini, h, "a0", 0, .55, 3)            # passado: surge apagado
    s += _traco(h, z, "a1", 1, 1, 4)                # os 14 dias
    s += _traco(z, e, "a2", 1, 1, 4)                # até a imersão
    s += _traco(e, fim, "a3", 1, 0, 3)
    tq = ""
    k = int(L["tiques"])
    for i in range(1, k + 1):
        cx, cy = _lerp(h, z, i / (k + 1))
        a, b = (cx - nx * 13, cy - ny * 13), (cx + nx * 13, cy + ny * 13)
        tq += (f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="{CI}" stroke-width="9" stroke-linecap="round" filter="url(#bta)" opacity=".8"/>'
               f'<path d="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f}" stroke="#E9FDFF" stroke-width="3.2" stroke-linecap="round"/>')
    s += tq + _no(h, 11, True) + _no(z, 15) + _no(e, 13)
    return f'<svg class="lt atras" width="1080" height="1350" viewBox="0 0 1080 1350">{s}</svg>'

def linha_frente(p):
    """Trecho prazo->evento redesenhado acima do recorte: a linha 'sai' de dentro do Lucas e chega ao 25/11."""
    L = _L(p); z, e = L["prazo"], L["evento"]
    a = _lerp(z, e, float(L["frente_de"]))
    s = _defs("f") + _traco(a, e, "f1", .15, 1, 4) + _no(e, 13)
    return f'<svg class="lt frente" width="1080" height="1350" viewBox="0 0 1080 1350">{s}</svg>'

def nota(p):
    L = _L(p); h, z = L["hoje"], L["prazo"]
    if not L.get("nota"): return ""
    dx, dy = z[0] - h[0], z[1] - h[1]; n = math.hypot(dx, dy); ang = math.degrees(math.atan2(dy, dx))
    nx, ny = dy / n, -dx / n   # normal para cima/direita da linha
    cx, cy = _lerp(h, z, float(L["nota_t"]))
    off = float(L["nota_off"]); cx, cy = cx + nx * off, cy + ny * off
    return (f'<div class="ltn" style="left:{cx:.1f}px;top:{cy:.1f}px;transform:translate(-50%,-50%) rotate({ang:.2f}deg);'
            f'font-size:{L["nota_tam"]}px">{html.escape(L["nota"])}</div>')

def css(p):
    return f"""
.lt{{position:absolute;left:0;top:0;overflow:visible;pointer-events:none}}
.lt.atras{{z-index:3}} .lt.frente{{z-index:7}}
.ltn{{position:absolute;z-index:6;white-space:nowrap;font-family:Mono;font-weight:500;letter-spacing:.06em;color:#BFF6FF;
  text-shadow:0 0 14px rgba(34,211,238,.75),0 0 2px rgba(34,211,238,.9)}}
.fc small{{text-transform:none}}
.sb{{font-size:{p.get('sb_tam', 32)}px!important}}
.rod{{font-size:{p.get('info_tam', 21)}px!important}} .rod b{{font-size:{p.get('preco_tam', 44)}px!important;font-weight:900}}
{p.get('css_extra', '')}
"""

JS = """<script>
document.fonts.ready.then(function(){
  const R=s=>[...document.querySelectorAll(s)].map(e=>{const b=e.getBoundingClientRect();return [s,Math.round(b.left),Math.round(b.top),Math.round(b.right),Math.round(b.bottom)];});
  const bx=[].concat(R('.lgt'),R('.tg'),R('.fc'),R('.ltn'),R('.txt'),R('.hd'),R('.sb'),R('.rod'));
  window.__boxes=bx.map(b=>b.join(' '));
  const rosto=window.__rosto;
  if(rosto){ bx.forEach(b=>{ if(b[1]<rosto[2]&&b[3]>rosto[0]&&b[2]<rosto[3]&&b[4]>rosto[1]) window.__boxes.push('ALERTA: '+b[0]+' encosta no rosto'); }); }
  const t=document.querySelector('.txt').getBoundingClientRect();
  document.querySelectorAll('.fc,.ltn').forEach(e=>{const b=e.getBoundingClientRect(); if(b.bottom>t.top-12) window.__boxes.push('ALERTA: '+e.className+' invade o bloco de texto');});
  document.querySelectorAll('.fc').forEach(e=>{const b=e.getBoundingClientRect(); if(b.left<0||b.right>1080) window.__boxes.push('ALERTA: card fora da arte '+e.textContent);});
  document.querySelectorAll('.hd,.sb').forEach(e=>{ if(e.scrollWidth>e.clientWidth+1) window.__boxes.push('ESTOURO '+e.className); });
});
</script>"""

def build(p):
    if not pathlib.Path(p["recorte"]).exists():
        sys.exit(f"Recorte não encontrado: {p['recorte']} (gere a foto no Kairogen e recorte com rembg antes)")
    c = R.PILARES[p.get("pilar", "imersao")]
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_flutuante(p, c) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    h = h.replace('<img class="pessoa"', linha_atras(p) + '<img class="pessoa"', 1)
    h = h.replace('<div class="sombra"></div>', '<div class="sombra"></div>' + linha_frente(p) + nota(p), 1)
    r = p.get("rosto")
    js = (f"<script>window.__rosto={json.dumps(r)};</script>" if r else "") + JS
    return h.replace("</body>", js + "</body>", 1)

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    dados = json.loads(pathlib.Path(spec).read_text())
    posts = dados if isinstance(dados, list) else [dados]
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
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
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(*sys.argv[1:])
