"""Post 2026-11-11 16h: flutuante escuro + 'Campo de silêncio' — o anel de luz vira campo de força: as notificações
do dia batem na borda do círculo e são cortadas; lá dentro o Lucas guarda o celular no bolso.
Uso: python3 scripts/arte_campo.py post_render.json pasta_saida
Campos extras: campo {"cx","cy","r"}; notificacoes [[remetente, msg, left, top, largura], ...]
Saída: pasta_saida/ID.png, ID.jpg e ID_story.png (igual ao kit/render.py)"""
import json, sys, pathlib, html, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)


def campo(p):
    c = p["campo"]; cx, cy, r = c["cx"], c["cy"], c["r"]
    # banners: vidro escuro, cortados pelo círculo (máscara radial: some dentro do campo)
    mask = f"radial-gradient(circle {r}px at {cx}px {cy}px, transparent {r-2}px, #000 {r+1}px)"
    bn = "".join(
        f'<div class="nt{" dir" if l + w / 2 > cx else ""}" style="left:{l}px;top:{t}px;width:{w}px">'
        f'<i>{R.icone("chat", "#22D3EE", 26)}</i><div><b>{html.escape(a)}</b><span>{html.escape(m)}</span></div>'
        f'<em>agora</em></div>'
        for a, m, l, t, w in p.get("notificacoes", []))
    camada = (f'<div class="nts" style="-webkit-mask-image:{mask};mask-image:{mask}">{bn}</div>')
    # arco do campo + faíscas de impacto onde cada banner encosta
    import math
    hits = ""
    for a, m, l, t, w in p.get("notificacoes", []):
        yc = t + 42
        dy = yc - cy
        if abs(dy) >= r: continue
        dx = math.sqrt(r * r - dy * dy)
        xs = [x for x in (cx - dx, cx + dx) if l < x < l + w]
        for x in xs:
            hits += (f'<ellipse cx="{x:.0f}" cy="{yc}" rx="10" ry="46" fill="url(#hit)" '
                     f'transform="rotate({math.degrees(math.atan2(dy, x - cx)):.0f} {x:.0f} {yc})"/>')
    svg = (f'<svg class="cp" viewBox="0 0 1080 1350"><defs>'
           f'<radialGradient id="hit"><stop offset="0" stop-color="#E6FDFF"/><stop offset=".35" stop-color="#22D3EE" stop-opacity=".9"/>'
           f'<stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>'
           f'<filter id="gl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>'
           f'<radialGradient id="dentro"><stop offset=".6" stop-color="#2F6BFF" stop-opacity="0"/><stop offset=".97" stop-color="#22D3EE" stop-opacity=".16"/>'
           f'<stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient></defs>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#dentro)"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#22D3EE" stroke-width="14" opacity=".55" filter="url(#gl)"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#9FF4FF" stroke-width="3"/>'
           f'{hits}</svg>')
    return camada + svg


def css(p):
    return """
.anel,.aro{display:none}
.tg{background:rgba(6,7,11,.92)}
.rod b{background:#22D3EE;color:#07080B!important;font-weight:800;font-size:34px!important;padding:12px 28px;border-radius:999px;box-shadow:0 10px 40px rgba(34,211,238,.45)}
.nts{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:5}
.nt{position:absolute;height:84px;display:flex;align-items:center;gap:14px;padding:0 20px;border-radius:22px;
  background:linear-gradient(160deg,rgba(40,46,60,.92),rgba(18,20,28,.92));border:1px solid rgba(255,255,255,.14);
  box-shadow:0 18px 40px rgba(0,0,0,.5);white-space:nowrap;overflow:hidden}
.nt i{flex:none;width:46px;height:46px;border-radius:12px;background:rgba(34,211,238,.14);display:flex;align-items:center;justify-content:center}
.nt div{display:flex;flex-direction:column;gap:3px;min-width:0}
.nt b{font-size:22px;font-weight:800;color:#fff} .nt span{font-size:20px;color:rgba(255,255,255,.7)}
.nt.dir{flex-direction:row-reverse;text-align:right}.nt.dir div{align-items:flex-end}.nt.dir em{right:auto;left:18px}
.nt em{position:absolute;right:18px;top:12px;font-style:normal;font-family:Mono;font-size:14px;color:rgba(255,255,255,.4)}
.cp{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:3;pointer-events:none}
"""


JS = """<script>
document.fonts.ready.then(function(){
  const R=s=>[...document.querySelectorAll(s)].map(e=>{const b=e.getBoundingClientRect();return [s,Math.round(b.left),Math.round(b.top),Math.round(b.right),Math.round(b.bottom)];});
  const bx=[].concat(R('.lgt'),R('.tg'),R('.fc'),R('.nt'),R('.txt'),R('.hd'),R('.sb'),R('.rod'));
  window.__boxes=bx.map(b=>b.join(' '));
  const rosto=window.__rosto;
  if(rosto){ bx.forEach(b=>{ if(b[0]!='.nt'&&b[1]<rosto[2]&&b[3]>rosto[0]&&b[2]<rosto[3]&&b[4]>rosto[1]) window.__boxes.push('ALERTA: '+b[0]+' encosta no rosto'); }); }
  const t=document.querySelector('.txt').getBoundingClientRect();
  document.querySelectorAll('.fc,.nt').forEach(e=>{const b=e.getBoundingClientRect(); if(b.bottom>t.top-12) window.__boxes.push('ALERTA: '+e.className+' invade o bloco de texto');});
  document.querySelectorAll('.hd,.sb').forEach(e=>{ if(e.scrollWidth>e.clientWidth+1) window.__boxes.push('ESTOURO '+e.className); });
});
</script>"""


def build(p):
    if not pathlib.Path(p["recorte"]).exists():
        sys.exit(f"Recorte não encontrado: {p['recorte']}")
    c = R.PILARES[p.get("pilar", "imersao")]
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_flutuante(p, c) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    h = h.replace('<img class="pessoa"', campo(p) + '<img class="pessoa"', 1)
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
