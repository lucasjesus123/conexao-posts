"""Post 2026-10-31 16h: celular3d escuro + 'decalque do vendedor da casa' (pop em papel vegetal sobre a mensagem original do histórico), em HTML/SVG.
Uso: python3 scripts/arte_decalque.py post_render.json pasta_saida
Campos extras do JSON (além dos do celular3d):
  original: texto da mensagem original do vendedor; {trecho} = palavra que ganha fio até o .mk de mesma ordem no pop_html; | = quebra
  fios: âncoras de cada fio (ver comentário do JS)
  carimbo: texto mono do carimbo da camada de trás ("✓" vira um check desenhado em SVG)
  orig_dx, orig_dy: deslocamento da camada de trás em relação ao pop (px, padrão -46/-150)
  orig_rot: giro da camada de trás (graus, padrão 3), orig_w: largura (padrão 500)
  pop_rot: giro do pop (padrão -1.5), pop_w: largura do pop, titulo_lh: line-height do título (opcional)
  sim_tam, sim_right, sim_gap: selo em pílula ciano logo abaixo do pop
  | nos balões da conversa = quebra de linha"""
import json, sys, html, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI = R.CIANO

CHECK = ('<svg width="17" height="13" viewBox="0 0 17 13" style="vertical-align:-1px;margin-right:6px"><path d="M1.5 7 L6 11 L15.5 1.5" '
         'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def css(p):
    top = p.get("pop_top", 760)
    dx, dy, rot, w = p.get("orig_dx", -46), p.get("orig_dy", -150), p.get("orig_rot", 3), p.get("orig_w", 500)
    lh = f".hd{{line-height:{p['titulo_lh']}}}" if p.get("titulo_lh") else ""
    return f"""
{lh}
.orig{{position:absolute;right:{50 - dx}px;top:{top + dy}px;width:{w}px;z-index:6;padding:24px 30px 20px;border-radius:26px;
  background:rgba(38,42,52,.78);border:2px dashed rgba(255,255,255,.30);transform:rotate({rot}deg);transform-origin:70% 60%;
  box-shadow:0 30px 60px rgba(0,0,0,.45)}}
.orig .ot{{font-size:25px;line-height:1.4;font-weight:500;color:rgba(232,236,244,.62);letter-spacing:-.005em}}
.orig .ow{{color:rgba(240,244,250,.80);border-bottom:1.5px dotted rgba(34,211,238,.55)}}
.orig .car{{display:inline-flex;align-items:center;margin-bottom:14px;font-family:Mono;font-size:14px;letter-spacing:.16em;color:rgba(255,255,255,.55);
  padding:6px 12px;border:1.5px solid rgba(255,255,255,.28);border-radius:8px}}
.orig .car .ok{{color:#5BE38C;display:inline-flex;align-items:center}}
.pop{{z-index:8!important;transform:rotate({p.get('pop_rot', -1.5)}deg)!important;
  background:linear-gradient(160deg,rgba(150,225,245,.13),rgba(14,19,28,.58) 55%,rgba(14,19,28,.66))!important;
  backdrop-filter:blur(2.2px) saturate(.8);-webkit-backdrop-filter:blur(2.2px) saturate(.8)}}
.pop small{{color:{CI}}}
.sim{{z-index:9!important;right:{p.get('sim_right',64)}px!important;font-size:{p.get('sim_tam',26)}px!important;letter-spacing:.16em!important;color:#fff!important;
  padding:9px 20px 8px;border:2px solid {CI};border-radius:40px;background:rgba(6,7,11,.82);box-shadow:0 0 18px rgba(34,211,238,.30)}}
{f".pop{{width:{p['pop_w']}px!important}}" if p.get('pop_w') else ""}
svg.fios{{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:9;pointer-events:none;overflow:visible}}
"""


def bloco(p):
    o = html.escape(p["original"])
    o = o.replace("{", '<span class="ow">').replace("}", "</span>").replace("|", "<br>")
    car = html.escape(p.get("carimbo", "HISTÓRICO · VENDEDOR DA CASA · ✓ VENDEU"))
    car = car.replace("✓", f'<span class="ok">{CHECK}') + ("</span>" if "✓" in p.get("carimbo", "✓") else "")
    return f'<div class="orig"><div class="car">{car}</div><div class="ot">{o}</div></div>'


# fios ciano pontilhados: de cada palavra da camada de trás até o marca-texto de mesma ordem no pop.
# Cada fio pode ter âncoras próprias em "fios" (lista na ordem das palavras):
#   a: fração ao longo da base da palavra de trás (0..1, padrão .5)
#   de: "r" = fio sai do lado direito da palavra de trás (em vez de sair por baixo)
#   r: qual pedaço (linha) do marca-texto (padrão 0); lado: "t" (chega por cima), "l" (pela esquerda) ou "r" (pela direita, contornando o pop; folga = px além da borda)
#   f: fração ao longo do topo do marca-texto quando lado = "t" (padrão .5); dy: desce a ponta pra dentro da palavra
#   via: [x, y] ponto de controle opcional (curva quadrática por ele)
JS = """<script>
document.fonts.ready.then(function(){
  const NS='http://www.w3.org/2000/svg', sv=document.createElementNS(NS,'svg'); sv.setAttribute('class','fios'); document.body.appendChild(sv);
  const ow=[...document.querySelectorAll('.orig .ow')], mk=[...document.querySelectorAll('.pop .mk')], F=__FIOS__;
  ow.forEach((a,i)=>{ const b=mk[i]; if(!b) return; const o=F[i]||{};
    const ras=[...a.getClientRects()], ra=ras[ras.length-1], rbs=[...b.getClientRects()], rb=rbs[Math.min(o.r||0,rbs.length-1)];
    let x1=ra.left+ra.width*(o.a??.5), y1=ra.bottom+4;
    if(o.de==='r'){ x1=ra.right+6; y1=ra.top+ra.height*.55; }
    let x2,y2,d;
    if(o.lado==='l'){ x2=rb.left-6; y2=rb.top+rb.height*.55; }
    else if(o.lado==='r'){ x2=rb.right+6; y2=rb.top+rb.height*.55; }
    else { x2=rb.left+rb.width*(o.f??.5); y2=rb.top-2+(o.dy||0); }
    if(o.via) d=`M${x1} ${y1} Q ${o.via[0]} ${o.via[1]}, ${x2} ${y2}`;
    else if(o.lado==='r'){ const X=document.querySelector('.pop').getBoundingClientRect().right+(o.folga??22);
      d=`M${x1} ${y1} C ${X} ${y1}, ${X} ${y2}, ${x2} ${y2}`; }
    else if(o.lado==='l') d=`M${x1} ${y1} C ${x1} ${y2}, ${x2-70} ${y2}, ${x2} ${y2}`;
    else d=`M${x1} ${y1} C ${x1} ${(y1+y2)/2}, ${x2} ${(y1+y2)/2}, ${x2} ${y2}`;
    const pa=document.createElementNS(NS,'path');
    pa.setAttribute('d',d); pa.setAttribute('fill','none'); pa.setAttribute('stroke','__CI__'); pa.setAttribute('stroke-width','2.2');
    pa.setAttribute('stroke-dasharray','1 6.5'); pa.setAttribute('stroke-linecap','round'); sv.appendChild(pa);
    [[x1,y1],[x2,y2]].forEach(([x,y])=>{ const c=document.createElementNS(NS,'circle'); c.setAttribute('cx',x); c.setAttribute('cy',y);
      c.setAttribute('r','3.8'); c.setAttribute('fill','__CI__'); sv.appendChild(c); });
  });
  const pr=document.querySelector('.pop').getBoundingClientRect(), si=document.querySelector('.sim');
  si.style.top=(pr.bottom+__SG__)+'px';
  window.__boxes = ['.txt','.hd','.sb','.orig','.pop','.sim','.base','.lg','.msgs'].map(s=>{const r=document.querySelector(s).getBoundingClientRect();
    return s+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(',');});
  [...document.querySelectorAll('.hd')].forEach(h=>window.__boxes.push('hd scrollW '+h.scrollWidth));
});
</script>""".replace("__CI__", CI)


def build(p):
    # "|" no texto dos balões do chat vira quebra de linha (o render.py escapa o texto)
    p = dict(p, conversa=[[q, t.replace("|", "\u2029")] for q, t in p.get("conversa", [])])
    h = R.build(p).replace("\u2029", "<br>")
    h = h.replace("</style>", css(p) + "</style>", 1)
    h = h.replace('<div class="pop">', bloco(p) + '<div class="pop">', 1)
    js = JS.replace("__SG__", str(p.get("sim_gap", 20))).replace("__FIOS__", json.dumps(p.get("fios", [])))
    return h.replace("</body>", js + "</body>", 1) if "</body>" in h else h + js


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(500)
            for l in pg.evaluate("window.__boxes||[]"): print("  ", l)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
