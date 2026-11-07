"""Post 2026-11-07 16h: celular3d escuro + 'contagem regressiva' (a conversa lida de baixo pra cima), em HTML/SVG.
Por cima do celular3d do kit, traço de caneta ciano feito à mão (SVG com leve tremor): um "1" grande circulado no pop
com a anotação "começa aqui", números 2..N circulados ao lado das bolhas (a mais baixa = 2, a primeira = N) e uma seta
que sai do pop, sobe pela lateral do celular e chega na primeira bolha, anotada "por último".
Uso: python3 scripts/arte_contagem.py render.json pasta_saida   (objeto ou lista; gera ID.jpg, ID.png e ID_story.png)
Campos extras do JSON (além dos do celular3d: tag, titulo, subtitulo, contato, conversa, pop_html, pop_rodape, cta, selo, tam, pop_top):
  pop_w, pop_right, pop_rot: largura, distância da direita e giro do pop (padrões 520 / 50 / -2)
  msgs_top, bolha_fs, msgs_gap, bolha_w, msgs_lr: topo da lista de bolhas, fonte, espaço entre bolhas, largura máx. (%), [margem esq, dir]
  txt_w: largura da coluna de texto; titulo_lh: line-height do título; input_txt: texto da caixa "Mensagem…"
  num_r: raio dos círculos pequenos (padrão 25); num_dx: lista de deslocamentos x de cada número (ordem das bolhas, px)
  num_dy: idem em y; um_r: raio do "1" do pop; um_dx, um_dy: posição do "1" em relação ao canto sup. esq. do pop
  nota1: texto da anotação do pop (padrão "começa aqui"), nota1_dx/nota1_dy/nota1_rot
  notaN: anotação da primeira bolha (padrão "por último"), notaN_dx/notaN_dy/notaN_rot
  seta: [[x,y],...] pontos intermediários da seta (coordenadas da página); seta_fim_dx/dy: ajuste da ponta
  sim_top, sim_right, sim_tam: selo SIMULAÇÃO em pílula (sim_top absoluto; padrão logo acima do pop)
  | nos balões da conversa = quebra de linha"""
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
"""


# Traço "de caneta": pontos com tremor suave (PRNG com semente fixa -> mesma arte a cada render), curva Catmull-Rom,
# desenhado duas vezes (traço cheio + rastro fino deslocado) pra parecer pincel.
JS = r"""<script>
document.fonts.ready.then(function(){
  const P=__P__, CI='__CI__', NS='http://www.w3.org/2000/svg';
  let s=7; const rnd=()=>{s=(s*16807)%2147483647; return s/2147483647;};
  const sv=document.createElementNS(NS,'svg'); sv.setAttribute('class','mao'); document.body.appendChild(sv);
  const cr=pts=>{ let d=`M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
    for(let i=0;i<pts.length-1;i++){ const a=pts[Math.max(i-1,0)], b=pts[i], c=pts[i+1], e=pts[Math.min(i+2,pts.length-1)];
      d+=` C${(b[0]+(c[0]-a[0])/6).toFixed(1)} ${(b[1]+(c[1]-a[1])/6).toFixed(1)},${(c[0]-(e[0]-b[0])/6).toFixed(1)} ${(c[1]-(e[1]-b[1])/6).toFixed(1)},${c[0].toFixed(1)} ${c[1].toFixed(1)}`; }
    return d; };
  const traco=(pts,w)=>{ [[w,1,0],[w*.38,.55,1.6]].forEach(([sw,op,off])=>{ const pa=document.createElementNS(NS,'path');
      pa.setAttribute('d',cr(pts.map(([x,y])=>[x+off,y-off*.6]))); pa.setAttribute('fill','none'); pa.setAttribute('stroke',CI);
      pa.setAttribute('stroke-width',sw); pa.setAttribute('stroke-opacity',op); pa.setAttribute('stroke-linecap','round'); pa.setAttribute('stroke-linejoin','round');
      if(!off) pa.setAttribute('style','filter:drop-shadow(0 0 6px rgba(34,211,238,.55)) drop-shadow(0 2px 3px rgba(0,0,0,.7))');
      sv.appendChild(pa); }); };
  // círculo à mão: começa em cima-direita, passa um pouco do ponto inicial (sobra de caneta), raio oscila
  const circulo=(cx,cy,r,w)=>{ const n=26, a0=-1.1+rnd()*.3, ph=rnd()*6, pts=[];
    for(let i=0;i<=n;i++){ const t=i/n, a=a0-t*(2*Math.PI+.55), k=1+.07*Math.sin(3*a+ph)+.04*(rnd()-.5)-.05*t;
      pts.push([cx+Math.cos(a)*r*1.08*k, cy+Math.sin(a)*r*.94*k]); }
    traco(pts,w); };
  const texto=(x,y,t,fs,rot,anc,peso)=>{ const e=document.createElementNS(NS,'text'); e.setAttribute('x',x); e.setAttribute('y',y);
    e.setAttribute('font-size',fs); e.setAttribute('text-anchor',anc||'middle'); if(peso) e.setAttribute('font-weight',peso);
    e.setAttribute('transform',`rotate(${rot||0} ${x} ${y})`); e.setAttribute('style','paint-order:stroke;stroke:#06070B;stroke-width:5px;stroke-linejoin:round');
    e.textContent=t; sv.appendChild(e); return e; };
  // linha à mão entre pontos de passagem: amostra a curva e soma um tremor baixo
  const linha=(via,w)=>traco(suave(via,8).map(([x,y],i)=>[x+Math.sin(i*.8)*1.5+(rnd()-.5)*1.2, y+Math.cos(i*.6)*1.5+(rnd()-.5)*1.2]),w);
  const suave=(v,k)=>{ const out=[]; for(let i=0;i<v.length-1;i++){ const a=v[Math.max(i-1,0)], b=v[i], c=v[i+1], e=v[Math.min(i+2,v.length-1)];
      for(let j=0;j<k;j++){ const t=j/k, t2=t*t, t3=t2*t;
        out.push([0,1].map(q=>.5*((2*b[q])+(-a[q]+c[q])*t+(2*a[q]-5*b[q]+4*c[q]-e[q])*t2+(-a[q]+3*b[q]-3*c[q]+e[q])*t3))); } }
    out.push(v[v.length-1]); return out; };

  const bs=[...document.querySelectorAll('.msgs .b')], pop=document.querySelector('.pop'), pr=pop.getBoundingClientRect();
  const N=bs.length+1, nr=P.num_r||25, dx=P.num_dx||[], dy=P.num_dy||[];
  window.__boxes=['.txt','.hd','.sb','.pop','.sim','.base','.lg','.fone'].map(q=>{const r=document.querySelector(q).getBoundingClientRect();
    return q+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(',');});
  // números ao lado de cada bolha (lado livre: à direita da bolha do cliente, à esquerda da bolha da IA)
  bs.forEach((b,i)=>{ const r=b.getBoundingClientRect(), n=N-i, cli=b.classList.contains('e');
    let cx=cli? r.right+nr+14 : r.left-nr-14, cy=r.top+r.height/2;
    cx+=dx[i]||0; cy+=dy[i]||0;
    circulo(cx,cy,nr,3.6); texto(cx-1,cy+nr*.42,String(n),nr*1.25,-4,'middle','500');
    window.__boxes.push(`b${i} ${[r.left,r.top,r.right,r.bottom].map(Math.round).join(',')} n${n}@${Math.round(cx)},${Math.round(cy)}`);
    if(i===0) window.__b0=r; });
  // "1" grande no pop
  const ur=P.um_r||44, ux=pr.left+(P.um_dx??-6), uy=pr.top+(P.um_dy??-8);
  circulo(ux,uy,ur,5); texto(ux-2,uy+ur*.45,'1',ur*1.35,-6,'middle','500');
  texto(ux+(P.nota1_dx??-10), uy+(P.nota1_dy??ur+44), P.nota1||'começa aqui', P.nota1_fs||34, P.nota1_rot??-6, P.nota1_anc||'middle');
  // seta: sai do pop e sobe até a primeira bolha
  const b0=window.__b0, fim=[b0.left-12+(P.seta_fim_dx||0), b0.top+b0.height*.5+(P.seta_fim_dy||0)];
  const ini=P.seta_ini||[pr.left-10, pr.top+60];
  const via=[ini, ...(P.seta||[]), fim];
  linha(via,4.2);
  // ponta: direção do último trecho
  const sm=suave(via,8), A=sm[sm.length-3], B=sm[sm.length-1], ang=Math.atan2(B[1]-A[1],B[0]-A[0]), L=22;
  traco([[B[0]-L*Math.cos(ang-.5),B[1]-L*Math.sin(ang-.5)],[B[0]+.5,B[1]+.3],[B[0]-L*Math.cos(ang+.48)+1,B[1]-L*Math.sin(ang+.48)]],4.2);
  texto(b0.left+(P.notaN_dx??-20), b0.top+(P.notaN_dy??-18), P.notaN||'por último', P.notaN_fs||30, P.notaN_rot??-5, P.notaN_anc||'end');
  window.__boxes.push('pop1 '+Math.round(ux)+','+Math.round(uy)+' seta '+JSON.stringify(via.map(v=>v.map(Math.round))));
  [...sv.querySelectorAll('text')].forEach(t=>{const r=t.getBoundingClientRect(); window.__boxes.push('txt "'+t.textContent+'" '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(','));});
  document.querySelectorAll('.hd').forEach(h=>window.__boxes.push('hd scrollW '+h.scrollWidth+' clientW '+h.clientWidth));
});
</script>"""


def build(p):
    # "|" no texto dos balões do chat vira quebra de linha (o render.py escapa o texto)
    p = dict(p, conversa=[[q, t.replace("|", " ")] for q, t in p.get("conversa", [])])
    h = R.build(p).replace(" ", "<br>")
    h = h.replace("</style>", css(p) + "</style>", 1)
    if "input_txt" in p:
        h = h.replace('<div class="input">Mensagem…</div>', f'<div class="input">{html.escape(p["input_txt"])}</div>', 1)
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
