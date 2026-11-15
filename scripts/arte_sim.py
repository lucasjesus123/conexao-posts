"""Post 2026-11-15 16h: painel3d escuro + 'portabilidade da empresa' (institucional).
Objeto 3D (campanhas/assets/sim_bandeja3d.png, 900x1200 RGBA): bandeja de chip SIM de vidro com chip dourado, inclinada.
Metáfora: o painel de vidro é o celular (o fornecedor); a bandeja sai por um slot na borda de baixo do painel, quebrando a
moldura, e fica no canto inferior direito da página: troca o aparelho, o chip (a tua empresa) vai contigo.
O painel 'As chaves da tua empresa' tem só os 3 cards de VALOR (ícone | rótulo | valor em ciano). O gráfico do painel3d
foi retirado (não inventamos dados): no lugar entra um slot de SIM (barra escura + furinho de ejetar), sem texto.
Detalhe surpresa: anotação à mão em ciano 'sai contigo' com seta curva apontando para o chip (px da página).
Baseado em scripts/arte_telefonista.py (sem o laço tracejado; 'laco' fica desligado por padrão).
Uso: python3 scripts/arte_sim.py post_render.json pasta_saida   (gera ID.png, ID.jpg, ID_story.png)
Campos extras:
  obj_x, obj_y, obj_w, obj_rot   posição do objeto (tamanho real lido do PNG; px da página, canto sup. esq. do PNG inteiro)
  palco_top, palco_h, palco_w, palco_right   painel de vidro
  slot: true/false   slot de SIM no fim do painel (no lugar do gráfico)
  txt_top, txt_w, hd_w, sb_tam, chip_tam      coluna de texto (hd_w deixa o título mais largo que a coluna)
  notas [[texto, x, y, rot, cor]]  setas [[x0,y0,cx,cy,x1,y1,cor]]  (px da página)  nt_tam, css_extra
  pilar sem cores próprias no kit (ex.: 'institucional') usa as cores de 'sistemas'.
"""
import json, sys, html, re, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI = R.CIANO


def tam_obj(f):
    try:
        from PIL import Image
        return Image.open(f).size
    except Exception:
        return 900, 1200


def chips(p):
    return "".join(f'<div class="vidro chip">{R.icone(ic, CI, 28)}<span>{html.escape(t)}</span></div>' for ic, t in p.get("chips", [])[:4])


def cards(p):
    out = ""
    for ic, v, rot in p.get("cards", [])[:3]:
        out += (f'<div class="vidro kv"><div class="ki">{R.icone(ic, CI, 26)}</div>'
                f'<div class="kt">{html.escape(rot)}</div><b>{html.escape(v)}</b></div>')
    return out


def slot():
    # slot de SIM: barra escura com brilho ciano na boca + furinho de ejetar. Sem texto, sem dado.
    return ('<div class="slot"><div class="boca"></div><div class="furo"></div></div>')


def anot(p):
    s = ['<svg class="anot" width="1080" height="1350" viewBox="0 0 1080 1350">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
         '<path d="M1 1L8 5L1 9" fill="none" stroke="context-stroke" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>']
    for x0, y0, cx, cy, x1, y1, cor in p.get("setas", []):
        s.append(f'<path d="M{x0} {y0} Q{cx} {cy} {x1} {y1}" fill="none" stroke="{cor}" stroke-width="5" stroke-linecap="round" marker-end="url(#ah)"'
                 f' style="filter:drop-shadow(0 0 6px rgba(0,0,0,.9))"/>')
    s.append("</svg>")
    for t, x, y, rot, cor in p.get("notas", []):
        s.append(f'<div class="nt" style="left:{x}px;top:{y}px;transform:rotate({rot}deg);color:{cor}">{html.escape(t)}</div>')
    return "".join(s)


def css(p, ow, oh):
    x, y, w, rot = p.get("obj_x", 560), p.get("obj_y", 700), p.get("obj_w", 520), p.get("obj_rot", 0)
    return f"""
.txt{{top:{p.get('txt_top', 180)}px!important;width:{p.get('txt_w', 560)}px!important;gap:26px!important}}
.hd{{width:{p.get('hd_w', 960)}px}}
.sb{{font-size:{p.get('sb_tam', 30)}px!important;line-height:1.36;text-wrap:balance}}
.chips{{width:auto!important;grid-template-columns:auto auto!important;justify-content:start;column-gap:12px!important;row-gap:12px!important}}
.chip{{font-size:{p.get('chip_tam', 21)}px!important;padding:15px 16px!important;gap:10px!important;white-space:nowrap}}
.palco{{top:{p.get('palco_top', 420)}px!important;height:{p.get('palco_h', 600)}px!important;width:{p.get('palco_w', 520)}px!important;right:{p.get('palco_right', -80)}px!important}}
.painel{{padding:26px 100px 26px 26px!important;gap:16px!important}}
.ph{{white-space:nowrap}}
.kps{{display:flex!important;flex-direction:column;gap:10px}}
.kv{{display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:20px}}
.kv .ki{{flex:none;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:rgba(34,211,238,.10)}}
.kv .kt{{flex:1;min-width:0;font-size:18px;line-height:1.22;color:rgba(255,255,255,.88);font-weight:600}}
.kv b{{flex:none;font-size:32px;font-weight:900;letter-spacing:-.03em;color:{CI};text-shadow:0 0 22px rgba(34,211,238,.45)}}
.slot{{position:relative;margin-top:auto;height:34px;border-radius:17px;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.14);
  box-shadow:inset 0 4px 10px rgba(0,0,0,.8)}}
.slot .boca{{position:absolute;left:22px;right:70px;top:13px;height:8px;border-radius:4px;background:#020306;
  box-shadow:0 0 16px rgba(34,211,238,.55),inset 0 0 4px rgba(34,211,238,.9)}}
.slot .furo{{position:absolute;right:26px;top:10px;width:14px;height:14px;border-radius:50%;background:#020306;border:2px solid rgba(255,255,255,.35)}}
.cta3{{white-space:nowrap;font-size:{p.get('cta_tam', 28)}px!important;padding:22px 34px!important}}
.obj{{display:none!important}}
.objw{{position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w * oh / ow:.0f}px;transform:rotate({rot}deg);z-index:4;
  filter:drop-shadow(0 30px 50px rgba(0,0,0,.55)) drop-shadow(0 0 40px rgba(34,211,238,.22))}}
.objw img{{width:100%;height:100%;display:block}}
.anot{{position:absolute;left:0;top:0;z-index:8;overflow:visible;pointer-events:none}}
.nt{{position:absolute;z-index:9;font-family:Serif;font-style:italic;font-weight:500;font-size:{p.get('nt_tam', 54)}px;white-space:nowrap;line-height:1;
  text-shadow:0 2px 14px rgba(0,0,0,.95),0 0 4px rgba(0,0,0,.9);transform-origin:0 50%}}
.sel{{font-size:20px!important;color:rgba(255,255,255,.85)!important;padding:10px 18px;border:1.5px solid rgba(34,211,238,.6);border-radius:40px;background:rgba(6,7,11,.55);top:74px!important}}
.nota{{font-size:23px!important;font-weight:600;color:rgba(255,255,255,.85)!important;bottom:62px!important;z-index:6!important}}
{p.get('css_extra', '')}
"""


def js():
    return """<script>
document.fonts.ready.then(function(){
  window.__boxes=['.lgt','.sel','.txt','.hd','.sb','.chips','.cta3','.palco','.kv','.slot','.objw','.nota','.nt'].map(s=>{const e=document.querySelector(s); if(!e) return s+' -'; const b=e.getBoundingClientRect();
    return s+' '+[b.left,b.top,b.right,b.bottom].map(Math.round).join(',');});
  document.querySelectorAll('.kv').forEach((e,i)=>{const b=e.getBoundingClientRect(); window.__boxes.push('kv'+i+' '+[b.left,b.top,b.right,b.bottom].map(Math.round).join(','));});
  document.querySelectorAll('.chip,.kv .kt,.kv b,.hd,.ph').forEach(e=>{ if(e.scrollWidth>e.clientWidth+1) window.__boxes.push('ESTOURO '+e.className+' '+e.textContent); });
});
</script>"""


def build(p):
    ow, oh = tam_obj(p["objeto"])
    pil = p.get("pilar", "sistemas")
    if pil not in R.PILARES:
        R.PILARES[pil] = R.PILARES["sistemas"]
    base = dict(p, chips=[], cards=[])
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_painel3d(base, R.PILARES[pil]) + "</body></html>"
    h = h.replace("</style>", css(p, ow, oh) + "</style>", 1)
    h = h.replace('<div class="chips"></div>', f'<div class="chips">{chips(p)}</div>', 1)
    h = h.replace('<div class="kps"></div>', f'<div class="kps">{cards(p)}</div>', 1)
    # tira o bloco do gráfico inteiro (título + svg); no lugar, o slot do SIM (ou nada)
    h = re.sub(r'<div class="vidro linha">.*?</svg></div>', lambda m: slot() if p.get("slot", True) else "", h, count=1, flags=re.S)
    if p.get('cta_seta') is False: h = h.replace(' →</div>', '</div>', 1)
    obj = f'<div class="objw"><img src="{R.b64(p["objeto"], "image/png")}"></div>'
    h = h.replace('<div class="txt">', obj + '<div class="txt">', 1)
    return h.replace("</body>", anot(p) + js() + "</body>", 1)


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(700)
            for l in pg.evaluate("window.__boxes||[]"): print("  ", l)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
