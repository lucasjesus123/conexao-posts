"""Post 2026-11-10 16h: painel3d escuro + 'a telefonista de 2026' (sistemas sob medida).
Objeto 3D (campanhas/assets/mesa_telefonica3d.png): mesa telefônica de 1950 em miniatura, jacks ciano, cabos azuis.
Painel 'Fechamento do ano' com 3 cards de VALOR (ícone | rótulo | valor grande em ciano), gráfico 'Horas de redigitação'
quase plano o ano todo e disparando em novembro/dezembro. Por cima de tudo, uma camada de anotação à mão em px da página:
laço tracejado ciano que liga os 3 cards (como um cabo de telefonista) e desce até a mesa, nota manuscrita e setas curvas.
Baseado em scripts/arte_caminho.py; as anotações aqui ficam na PÁGINA (1080x1350), não dentro do objeto, porque ligam painel e objeto.
Uso: python3 scripts/arte_telefonista.py post_render.json pasta_saida   (gera ID.png, ID.jpg, ID_story.png)
Campos extras:
  obj_x, obj_y, obj_w, obj_rot   posição do objeto (tamanho real lido do PNG)
  palco_top, palco_h, palco_w, palco_right   painel de vidro
  txt_top, txt_w, hd_w, sb_tam, chip_tam      coluna de texto (hd_w deixa o título mais largo que a coluna)
  laco: "auto" (liga o meio-esquerdo de cada card e desce até laco_fim) ou [[x,y]...] manual; laco_fim [x,y] (padrão: jacks do objeto)
  notas [[texto, x, y, rot, cor]]  setas [[x0,y0,cx,cy,x1,y1,cor]]  (px da página)  nt_tam, css_extra
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
        return 900, 760


def chips(p):
    return "".join(f'<div class="vidro chip">{R.icone(ic, CI, 28)}<span>{html.escape(t)}</span></div>' for ic, t in p.get("chips", [])[:4])


def cards(p):
    out = ""
    for ic, v, rot in p.get("cards", [])[:3]:
        out += (f'<div class="vidro kv"><div class="ki">{R.icone(ic, CI, 26)}</div>'
                f'<div class="kt">{html.escape(rot)}</div><b>{html.escape(v)}</b></div>')
    return out


def graf():
    # 12 meses: quase plano, sobe em novembro e dispara em dezembro
    ys = [112, 108, 110, 104, 108, 102, 106, 100, 98, 92, 70, 18]
    xs = [round(i * 440 / 11) for i in range(12)]
    pts = list(zip(xs, ys))
    d = f"M{pts[0][0]} {pts[0][1]}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cx = (x0 + x1) / 2
        d += f" C{cx} {y0}, {cx} {y1}, {x1} {y1}"
    barras = "".join(f'<rect x="{x - 7}" y="{y + 8}" width="14" height="{130 - y - 8}" rx="4" fill="rgba(255,255,255,{.10 if i < 10 else .22})"/>'
                     for i, (x, y) in enumerate(pts))
    return f"""<svg width="100%" height="160" viewBox="0 0 440 160" style="overflow:visible">
<defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CI}" stop-opacity=".40"/><stop offset="1" stop-color="{CI}" stop-opacity="0"/></linearGradient></defs>
<g stroke="rgba(255,255,255,.07)" stroke-width="1.5"><path d="M0 30H440M0 80H440M0 130H440"/></g>
{barras}
<path d="{d} L440 130 L0 130Z" fill="url(#rg)"/>
<path d="{d}" fill="none" stroke="{CI}" stroke-width="5" stroke-linecap="round"/>
<circle cx="440" cy="18" r="9" fill="{CI}" style="filter:drop-shadow(0 0 10px {CI})"/>
<g font-family="Mono" font-size="17" fill="rgba(255,255,255,.7)"><text x="0" y="156">jan</text><text x="440" y="156" text-anchor="end" fill="{CI}" font-weight="700">dez</text></g>
</svg>"""


def anot(p):
    s = ['<svg class="anot" width="1080" height="1350" viewBox="0 0 1080 1350">',
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
         '<path d="M1 1L8 5L1 9" fill="none" stroke="context-stroke" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>',
         f'<path id="laco" d="" fill="none" stroke="{CI}" stroke-width="6" stroke-dasharray="3 16" stroke-linecap="round" style="filter:drop-shadow(0 0 7px {CI})"/>',
         '<g id="jacks"></g>']
    for x0, y0, cx, cy, x1, y1, cor in p.get("setas", []):
        s.append(f'<path d="M{x0} {y0} Q{cx} {cy} {x1} {y1}" fill="none" stroke="{cor}" stroke-width="5" stroke-linecap="round" marker-end="url(#ah)"/>')
    s.append("</svg>")
    for t, x, y, rot, cor in p.get("notas", []):
        s.append(f'<div class="nt" style="left:{x}px;top:{y}px;transform:rotate({rot}deg);color:{cor}">{html.escape(t)}</div>')
    return "".join(s)


def css(p, ow, oh):
    x, y, w, rot = p.get("obj_x", 500), p.get("obj_y", 880), p.get("obj_w", 560), p.get("obj_rot", 0)
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
.linha{{padding:18px 20px!important}} .linha small{{font-size:21px!important;color:#fff!important;font-weight:600}}
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


def js(p):
    laco = p.get("laco", "auto")
    fim = p.get("laco_fim")
    return """<script>
document.fonts.ready.then(function(){
  const LACO=%s, FIM=%s, CI='%s';
  const NS='http://www.w3.org/2000/svg';
  let pts=[];
  if(LACO==='auto'){
    document.querySelectorAll('.kv').forEach(e=>{const b=e.getBoundingClientRect(); pts.push([b.left-4,b.top+b.height/2]);});
    const o=document.querySelector('.objw').getBoundingClientRect();
    const f=FIM||[o.left+o.width*.42,o.top+o.height*.30];
    let d='M'+pts[0][0]+' '+pts[0][1];
    for(let i=1;i<pts.length;i++){const a=pts[i-1],b=pts[i];
      d+=` C${a[0]-20} ${a[1]+8}, ${b[0]-20} ${b[1]-8}, ${b[0]} ${b[1]}`;}
    const l=pts[pts.length-1];
    // sai do último card, faz um laço (cabo enrolado) e desce até a mesa
    const lx=l[0]-120, ly=l[1]+150;
    d+=` C${l[0]-80} ${l[1]+10}, ${lx-70} ${ly-40}, ${lx} ${ly}`;
    d+=` C${lx+60} ${ly+45}, ${lx+40} ${ly-55}, ${lx-10} ${ly-20}`;
    d+=` C${lx-60} ${ly+20}, ${f[0]-60} ${f[1]-90}, ${f[0]} ${f[1]}`;
    pts.push(f);
    document.getElementById('laco').setAttribute('d',d);
  } else {
    pts=LACO; let d='M'+pts.map(q=>q.join(' ')).join(' L');
    document.getElementById('laco').setAttribute('d',d); pts=[pts[0],pts[pts.length-1]];
  }
  const g=document.getElementById('jacks');
  pts.forEach(q=>{const c=document.createElementNS(NS,'circle'); c.setAttribute('cx',q[0]); c.setAttribute('cy',q[1]); c.setAttribute('r',8);
    c.setAttribute('fill',CI); c.setAttribute('style','filter:drop-shadow(0 0 8px '+CI+')'); g.appendChild(c);});
  window.__boxes=['.lgt','.sel','.txt','.hd','.sb','.chips','.cta3','.palco','.kv','.objw','.nota','.nt'].map(s=>{const e=document.querySelector(s); if(!e) return s+' -'; const b=e.getBoundingClientRect();
    return s+' '+[b.left,b.top,b.right,b.bottom].map(Math.round).join(',');});
  document.querySelectorAll('.chip,.kv .kt,.kv b,.hd,.ph').forEach(e=>{ if(e.scrollWidth>e.clientWidth+1) window.__boxes.push('ESTOURO '+e.className+' '+e.textContent); });
});
</script>""" % (json.dumps(laco), json.dumps(fim), CI)


def build(p):
    ow, oh = tam_obj(p["objeto"])
    base = dict(p, chips=[], cards=[])
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_painel3d(base, R.PILARES[p.get("pilar", "sistemas")]) + "</body></html>"
    h = h.replace("</style>", css(p, ow, oh) + "</style>", 1)
    h = h.replace('<div class="chips"></div>', f'<div class="chips">{chips(p)}</div>', 1)
    h = h.replace('<div class="kps"></div>', f'<div class="kps">{cards(p)}</div>', 1)
    h = re.sub(r'<svg width="100%" height="150".*?</svg>', lambda m: graf(), h, count=1, flags=re.S)
    if p.get('cta_seta') is False: h = h.replace(' →</div>', '</div>', 1)
    obj = f'<div class="objw"><img src="{R.b64(p["objeto"], "image/png")}"></div>'
    h = h.replace('<div class="txt">', obj + '<div class="txt">', 1)
    return h.replace("</body>", anot(p) + js(p) + "</body>", 1)


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
