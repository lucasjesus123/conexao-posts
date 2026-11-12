"""Post 2026-11-12 16h: celular3d escuro + placa de saída de emergência 'REMARCAR' (a saída pronta no lembrete), em HTML/SVG.
Por cima do celular3d do kit: placa ciano luminosa com o bonequinho correndo pela porta (pictograma em SVG), escrita REMARCAR,
na coluna da esquerda; a palavra REMARCAR nas bolhas ganha destaque e uma seta de caneta ciano sai da placa até a resposta do paciente.
Uso: python3 scripts/arte_saida.py render.json pasta_saida   (gera ID.jpg, ID.png e ID_story.png)
Campos extras: os do arte_contagem.py (pop_top, msgs_top, bolha_fs, msgs_gap, bolha_w, pop_w, sim_top...) +
  placa: {left, top, w, rot, texto, sub}; seta: [[x,y],...] pontos intermediários; seta_alvo: índice da bolha (padrão 1)
  seta_fim_dx/dy; nota: anotação à mão perto da seta, nota_xy, nota_rot"""
import json, sys, html, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI = R.CIANO


def css(p):
    top = p.get("pop_top", 760)
    o = []
    if p.get("titulo_lh"): o.append(f".hd{{line-height:{p['titulo_lh']}}}")
    if p.get("txt_w"): o.append(f".txt{{width:{p['txt_w']}px}}")
    if p.get("msgs_top"): o.append(f".msgs{{top:{p['msgs_top']}px!important}}")
    if p.get("msgs_gap"): o.append(f".msgs{{gap:{p['msgs_gap']}px!important}}")
    if p.get("bolha_fs"): o.append(f".b{{font-size:{p['bolha_fs']}px!important}}")
    if p.get("bolha_w"): o.append(f".b{{max-width:{p['bolha_w']}%!important}}")
    if p.get("msgs_lr"): o.append(f".msgs{{left:{p['msgs_lr'][0]}px!important;right:{p['msgs_lr'][1]}px!important}}")
    if p.get("pop_w"): o.append(f".pop{{width:{p['pop_w']}px!important}}")
    if p.get("pop_right"): o.append(f".pop{{right:{p['pop_right']}px!important}}")
    if "pop_rot" in p: o.append(f".pop{{transform:rotate({p['pop_rot']}deg)!important}}")
    return "\n".join(o) + f"""
.pop{{z-index:8!important}}
.sim{{z-index:9!important;top:{p.get('sim_top', top - 62)}px!important;right:{p.get('sim_right', 64)}px!important;font-size:{p.get('sim_tam', 22)}px!important;
  letter-spacing:.16em!important;color:#fff!important;padding:9px 20px 8px;border:2px solid {CI};border-radius:40px;background:rgba(6,7,11,.82);
  box-shadow:0 0 18px rgba(34,211,238,.30)}}
svg.mao{{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:20;pointer-events:none;overflow:visible}}
svg.mao text{{font-family:Serif;font-style:italic;fill:{CI}}}

.placa{{position:absolute;z-index:15;display:flex;align-items:center;gap:22px;padding:18px 30px 18px 20px;border-radius:18px;
  background:linear-gradient(160deg,#7DF3FF,{CI} 55%,#14B8D4);color:#04121A;
  box-shadow:0 0 0 5px rgba(6,7,11,.9),0 0 0 7px rgba(34,211,238,.55),0 0 70px rgba(34,211,238,.55),0 30px 60px rgba(0,0,0,.6)}}
.placa svg{{flex:none}}
.placa b{{display:block;font-weight:900;font-size:{p.get('placa',{}).get('fs',58)}px;letter-spacing:.04em;line-height:1}}
.placa small{{display:block;font-family:Mono;font-size:17px;letter-spacing:.12em;margin-top:8px;opacity:.8}}
.rm{{font-weight:800;color:#fff;background:linear-gradient(transparent 58%,rgba(34,211,238,.55) 58%);padding:0 2px}}
.b.e .rm{{color:#7DF3FF;background:none;text-decoration:underline;text-decoration-color:{CI};text-underline-offset:5px;text-decoration-thickness:3px}}
"""


# Traço "de caneta": pontos com tremor suave (PRNG com semente fixa -> mesma arte a cada render), curva Catmull-Rom,
# desenhado duas vezes (traço cheio + rastro fino deslocado) pra parecer pincel.
PICT = '''<svg width="{pw}" height="{pw}" viewBox="0 0 100 100"><rect x="4" y="4" width="92" height="92" rx="12" fill="#04121A"/>
<g fill="none" stroke="#7DF3FF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
<path d="M62 20 H84 V84 H62"/><path d="M84 52 H74"/></g>
<g fill="#7DF3FF"><circle cx="44" cy="22" r="8"/></g>
<g fill="none" stroke="#7DF3FF" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
<path d="M40 34 L34 58"/><path d="M38 40 L52 48 L60 42"/><path d="M38 40 L24 46 L18 40"/><path d="M34 58 L48 66 L46 84"/><path d="M34 58 L26 74 L12 76"/></g></svg>'''

JS = r"""<script>
document.fonts.ready.then(function(){
  const P=__P__, CI='__CI__', NS='http://www.w3.org/2000/svg';
  let s=11; const rnd=()=>{s=(s*16807)%2147483647; return s/2147483647;};
  document.querySelectorAll('.msgs .b').forEach(b=>{ b.innerHTML=b.innerHTML.replace(/REMARCAR/g,'<span class="rm">REMARCAR</span>'); });
  const sv=document.createElementNS(NS,'svg'); sv.setAttribute('class','mao'); document.body.appendChild(sv);
  const suave=(v,k)=>{ const out=[]; for(let i=0;i<v.length-1;i++){ const a=v[Math.max(i-1,0)], b=v[i], c=v[i+1], e=v[Math.min(i+2,v.length-1)];
      for(let j=0;j<k;j++){ const t=j/k, t2=t*t, t3=t2*t;
        out.push([0,1].map(q=>.5*((2*b[q])+(-a[q]+c[q])*t+(2*a[q]-5*b[q]+4*c[q]-e[q])*t2+(-a[q]+3*b[q]-3*c[q]+e[q])*t3))); } }
    out.push(v[v.length-1]); return out; };
  const path=(pts,w,op)=>{ const pa=document.createElementNS(NS,'path'); let d='M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L');
    pa.setAttribute('d',d); pa.setAttribute('fill','none'); pa.setAttribute('stroke',CI); pa.setAttribute('stroke-width',w); pa.setAttribute('stroke-opacity',op||1);
    pa.setAttribute('stroke-linecap','round'); pa.setAttribute('stroke-linejoin','round');
    pa.setAttribute('style','filter:drop-shadow(0 0 6px rgba(34,211,238,.55)) drop-shadow(0 2px 3px rgba(0,0,0,.7))'); sv.appendChild(pa); };
  const traco=(pts,w)=>{ path(pts,w,1); path(pts.map(([x,y])=>[x+1.6,y-1]),w*.38,.55); };
  const pl=document.querySelector('.placa').getBoundingClientRect();
  const bs=[...document.querySelectorAll('.msgs .b')], alvo=bs[P.seta_alvo??1], rm=alvo.querySelector('.rm')||alvo;
  const ar=rm.getBoundingClientRect();
  const ini=P.seta_ini||[pl.right-30, pl.top-14];
  const fim=[ar.left+ar.width*.5+(P.seta_fim_dx||0), ar.bottom+14+(P.seta_fim_dy||0)];
  const via=[ini,...(P.seta||[]),fim];
  const sm=suave(via,10).map(([x,y],i)=>[x+Math.sin(i*.7)*1.3+(rnd()-.5), y+Math.cos(i*.5)*1.3+(rnd()-.5)]);
  traco(sm,4.4);
  const A=sm[sm.length-4], B=sm[sm.length-1], ang=Math.atan2(B[1]-A[1],B[0]-A[0]), L=24;
  traco([[B[0]-L*Math.cos(ang-.5),B[1]-L*Math.sin(ang-.5)],[B[0],B[1]],[B[0]-L*Math.cos(ang+.5),B[1]-L*Math.sin(ang+.5)]],4.4);
  if(P.nota){ const e=document.createElementNS(NS,'text'); const [x,y]=P.nota_xy; e.setAttribute('x',x); e.setAttribute('y',y); e.setAttribute('font-size',P.nota_fs||36);
    e.setAttribute('transform',`rotate(${P.nota_rot||-5} ${x} ${y})`); e.setAttribute('style','paint-order:stroke;stroke:#06070B;stroke-width:6px;stroke-linejoin:round');
    e.textContent=P.nota; sv.appendChild(e); }
  window.__boxes=['.txt','.sb','.pop','.sim','.base','.placa','.fone','.cta2'].map(q=>{const el=document.querySelector(q); if(!el) return q+' -'; const r=el.getBoundingClientRect();
    return q+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(',');});
  bs.forEach((b,i)=>{const r=b.getBoundingClientRect(); window.__boxes.push('b'+i+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(','));});
  window.__boxes.push('seta '+JSON.stringify(via.map(v=>v.map(Math.round))));
});
</script>"""


def build(p):
    # "|" no texto dos balões do chat vira quebra de linha (o render.py escapa o texto)
    p = dict(p, conversa=[[q, t.replace("|", " ")] for q, t in p.get("conversa", [])])
    h = R.build(p).replace(" ", "<br>")
    h = h.replace("</style>", css(p) + "</style>", 1)
    if "input_txt" in p:
        h = h.replace('<div class="input">Mensagem…</div>', f'<div class="input">{html.escape(p["input_txt"])}</div>', 1)
    pc = p.get("placa", {})
    placa = (f'<div class="placa" style="left:{pc.get('left',64)}px;top:{pc.get('top',840)}px;transform:rotate({pc.get('rot',-4)}deg)">'
             f'{PICT.replace("{pw}", str(pc.get("pict",96)))}<div><b>{html.escape(pc.get('texto','REMARCAR'))}</b><small>{html.escape(pc.get('sub','SAÍDA SEM CONSTRANGIMENTO'))}</small></div></div>')
    h = h.replace("</body>", placa + "</body>", 1) if "</body>" in h else h + placa
    js = JS.replace("__CI__", CI).replace("__P__", json.dumps(p, ensure_ascii=False))
    return h.replace("</body>", js + "</body>", 1) if "</body>" in h else h + js


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text())
    if isinstance(posts, dict): posts = [posts]
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
    main(*sys.argv[1:])
