"""Post 2026-11-14 08h: celular3d escuro ESPELHADO (celular à esquerda, título à direita) + 'a pergunta fantasma', em HTML/SVG.
Por cima do celular3d do kit: a pergunta que o cliente pensou e não digitou sai da tela como bolha FANTASMA (contorno tracejado
ciano, fundo quase transparente com desfoque e brilho, letra manuscrita Serif itálica, indicador '…digitando' apagado), quebrando
a moldura do celular em direção à coluna do título. Bolinhas de pensamento ligam a 1ª mensagem do cliente à bolha, e uma seta
de caneta ciano (traço à mão, PRNG fixo) sai da anotação "o que ele pensou e não escreveu" até a bolha.
Todas as mensagens da conversa viram bolhas (o pop é só o pop_html, não come a última mensagem).
Uso: python3 scripts/arte_fantasma.py render.json pasta_saida   (objeto ou lista; gera ID.jpg, ID.png e ID_story.png)
Campos extras do JSON (além dos do celular3d: tag, titulo, subtitulo, contato, conversa, pop_html, pop_rodape, cta, selo, tam):
  espelho: true = celular à esquerda e texto à direita (padrão true); txt_left, txt_top, txt_w: coluna de texto
  cena_left, cena_top, cena_w, cena_h: posição/tamanho do celular; msgs_top, bolha_fs, msgs_gap, bolha_w, msgs_lr: bolhas
  pop_top, pop_left, pop_w, pop_rot, pop_fs: pop (no espelho fica à esquerda, sobre a base do celular)
  sim_top, sim_left, sim_tam: selo SIMULAÇÃO em pílula
  fantasma: {left, top, w, rot, fs, linhas: [..], digitando}: a bolha fantasma (linhas = perguntas não escritas)
  trilha: [[x,y,r],...] bolinhas de pensamento (se vazio, liga a 1ª bolha do cliente à fantasma automaticamente)
  nota, nota_xy, nota_fs, nota_rot: anotação à mão; seta: [[x,y],...] pontos intermediários; seta_ini, seta_fim_dx/dy
  | nos balões da conversa = quebra de linha"""
import json, sys, html, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
CI = R.CIANO


def css(p):
    top = p.get("pop_top", 940)
    f = p.get("fantasma", {})
    o = []
    if p.get("titulo_lh"): o.append(f".hd{{line-height:{p['titulo_lh']}}}")
    if p.get("msgs_top"): o.append(f".msgs{{top:{p['msgs_top']}px!important}}")
    if p.get("msgs_gap"): o.append(f".msgs{{gap:{p['msgs_gap']}px!important}}")
    if p.get("bolha_fs"): o.append(f".b{{font-size:{p['bolha_fs']}px!important}}")
    if p.get("bolha_w"): o.append(f".b{{max-width:{p['bolha_w']}%!important}}")
    if p.get("msgs_lr"): o.append(f".msgs{{left:{p['msgs_lr'][0]}px!important;right:{p['msgs_lr'][1]}px!important}}")
    if p.get("pop_fs"): o.append(f".pop{{font-size:{p['pop_fs']}px!important}}")
    if p.get("espelho", True):
        o.append(f""".txt{{left:{p.get('txt_left',560)}px!important;top:{p.get('txt_top',104)}px!important;width:{p.get('txt_w',470)}px!important;gap:24px!important}}
.sb{{font-size:{p.get('sb_fs',30)}px!important}}
.tag{{font-size:{p.get('tag_fs',16)}px!important;letter-spacing:.14em!important;white-space:nowrap;padding:13px 22px!important}}
.cena{{right:auto!important;left:{p.get('cena_left',-30)}px!important;top:{p.get('cena_top',110)}px!important;width:{p.get('cena_w',540)}px!important;height:{p.get('cena_h',1060)}px!important}}
.fone{{transform:rotateY(22deg) rotateX(7deg) rotateZ(-2deg)!important;transform-origin:40% 50%!important;
  box-shadow:40px 60px 120px rgba(0,0,0,.7),0 0 0 2px rgba(255,255,255,.08),0 0 80px rgba(47,107,255,.25)!important}}
.pop{{right:auto!important;left:{p.get('pop_left',40)}px!important}}
.base{{left:auto!important;right:64px!important}}
.lg{{right:auto!important;left:64px!important}}
.luz{{transform:scaleX(-1)}}""")
    return "\n".join(o) + f"""
.pop{{z-index:8!important;top:{top}px!important;width:{p.get('pop_w',500)}px!important;transform:rotate({p.get('pop_rot',2)}deg)!important}}
.sim{{z-index:9!important;top:{p.get('sim_top', top - 62)}px!important;right:auto!important;left:{p.get('sim_left', 64)}px!important;font-size:{p.get('sim_tam', 22)}px!important;
  letter-spacing:.16em!important;color:#fff!important;padding:9px 20px 8px;border:2px solid {CI};border-radius:40px;background:rgba(6,7,11,.85);
  box-shadow:0 0 18px rgba(34,211,238,.30)}}
svg.mao{{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:20;pointer-events:none;overflow:visible}}
svg.mao text{{font-family:Serif;font-style:italic}}
.fant{{position:absolute;z-index:14;left:{f.get('left',420)}px;top:{f.get('top',720)}px;width:{f.get('w',560)}px;transform:rotate({f.get('rot',-5)}deg);
  display:flex;flex-direction:column;gap:14px;align-items:flex-start}}
.fb{{position:relative;font-family:Serif;font-style:italic;font-weight:500;font-size:{f.get('fs',38)}px;line-height:1.1;color:#EFFFFF;
  padding:16px 28px 18px;border:3px dashed rgba(125,243,255,.95);border-radius:30px 30px 30px 8px;
  background:linear-gradient(160deg,rgba(34,211,238,.16),rgba(6,7,11,.35));backdrop-filter:blur(7px);
  box-shadow:0 0 44px rgba(34,211,238,.50),0 0 120px rgba(34,211,238,.18),inset 0 0 30px rgba(34,211,238,.18);
  text-shadow:0 0 14px rgba(34,211,238,.75),0 0 2px rgba(255,255,255,.6);white-space:nowrap}}
.fb:nth-child(2){{margin-left:{f.get('recuo2',34)}px;opacity:.9}}
.dig{{margin-left:12px;font-family:Mono;font-size:19px;letter-spacing:.14em;color:rgba(125,243,255,.45);display:flex;align-items:center;gap:7px}}
.dig i{{width:8px;height:8px;border-radius:50%;background:rgba(125,243,255,.42)}}
.dig i:nth-child(2){{opacity:.7}} .dig i:nth-child(3){{opacity:.4}}
.bol{{position:absolute;z-index:13;border-radius:50%;border:2.5px dashed rgba(125,243,255,.85);background:rgba(34,211,238,.08);
  box-shadow:0 0 16px rgba(34,211,238,.45)}}
.pop .mk{{color:#fff;background:linear-gradient(transparent 74%,rgba(34,211,238,.6) 74%)!important;padding:0 2px 4px!important}}
"""


JS = r"""<script>
document.fonts.ready.then(function(){
  const P=__P__, CI='__CI__', NS='http://www.w3.org/2000/svg';
  let s=14; const rnd=()=>{s=(s*16807)%2147483647; return s/2147483647;};
  const sv=document.createElementNS(NS,'svg'); sv.setAttribute('class','mao'); document.body.appendChild(sv);
  const suave=(v,k)=>{ const out=[]; for(let i=0;i<v.length-1;i++){ const a=v[Math.max(i-1,0)], b=v[i], c=v[i+1], e=v[Math.min(i+2,v.length-1)];
      for(let j=0;j<k;j++){ const t=j/k, t2=t*t, t3=t2*t;
        out.push([0,1].map(q=>.5*((2*b[q])+(-a[q]+c[q])*t+(2*a[q]-5*b[q]+4*c[q]-e[q])*t2+(-a[q]+3*b[q]-3*c[q]+e[q])*t3))); } }
    out.push(v[v.length-1]); return out; };
  const path=(pts,w,op)=>{ const pa=document.createElementNS(NS,'path'); pa.setAttribute('d','M'+pts.map(p=>p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L'));
    pa.setAttribute('fill','none'); pa.setAttribute('stroke',CI); pa.setAttribute('stroke-width',w); pa.setAttribute('stroke-opacity',op||1);
    pa.setAttribute('stroke-linecap','round'); pa.setAttribute('stroke-linejoin','round');
    pa.setAttribute('style','filter:drop-shadow(0 0 6px rgba(34,211,238,.55)) drop-shadow(0 2px 3px rgba(0,0,0,.7))'); sv.appendChild(pa); };
  const traco=(pts,w)=>{ path(pts,w,1); path(pts.map(([x,y])=>[x+1.6,y-1]),w*.38,.55); };
  const box=r=>[r.left,r.top,r.right,r.bottom].map(Math.round).join(',');

  // bolinhas de pensamento: da 1ª bolha do cliente até a bolha fantasma (saem da tela, atravessam a moldura)
  const bs=[...document.querySelectorAll('.msgs .b')], cli=bs.find(b=>b.classList.contains('e'));
  const fa=document.querySelector('.fant'), fb=document.querySelector('.fb'), fr=fb.getBoundingClientRect();
  let tr=P.trilha;
  if(!tr || !tr.length){ const cr=cli.getBoundingClientRect(), a=[cr.right-10, cr.bottom+4], b=[fr.left+30, fr.bottom+18];
    tr=[[.22,9],[.5,13],[.8,18]].map(([t,r])=>[a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, r]); }
  tr.forEach(([x,y,r])=>{ const d=document.createElement('div'); d.className='bol';
    d.style.cssText=`left:${x-r}px;top:${y-r}px;width:${2*r}px;height:${2*r}px`; document.body.appendChild(d); });

  // anotação à mão + seta curva até a bolha fantasma
  if(P.nota){ const e=document.createElementNS(NS,'text'); const [x,y]=P.nota_xy; e.setAttribute('x',x); e.setAttribute('y',y); e.setAttribute('font-size',P.nota_fs||36);
    e.setAttribute('fill',P.nota_cor||'#fff'); e.setAttribute('text-anchor',P.nota_anc||'start');
    e.setAttribute('transform',`rotate(${P.nota_rot||-4} ${x} ${y})`); e.setAttribute('style','paint-order:stroke;stroke:#06070B;stroke-width:7px;stroke-linejoin:round');
    const ls=String(P.nota).split('|'); ls.forEach((l,i)=>{ const t=document.createElementNS(NS,'tspan'); t.setAttribute('x',x); t.setAttribute('dy',i?(P.nota_fs||36)*1.08:0); t.textContent=l; e.appendChild(t); });
    sv.appendChild(e); window.__nota=e; }
  const alvo=[...document.querySelectorAll('.fb')][P.seta_alvo??1].getBoundingClientRect();
  const nr=window.__nota?window.__nota.getBoundingClientRect():null;
  const ini=P.seta_ini||(nr?[nr.left+40, nr.top-8]:[alvo.left, alvo.bottom+80]);
  const fim=[alvo.left+alvo.width*.5+(P.seta_fim_dx||0), alvo.bottom+14+(P.seta_fim_dy||0)];
  const via=[ini,...(P.seta||[]),fim];
  const sm=suave(via,10).map(([x,y],i)=>[x+Math.sin(i*.7)*1.2+(rnd()-.5), y+Math.cos(i*.5)*1.2+(rnd()-.5)]);
  traco(sm,4.2);
  const A=sm[sm.length-4], B=sm[sm.length-1], ang=Math.atan2(B[1]-A[1],B[0]-A[0]), L=22;
  traco([[B[0]-L*Math.cos(ang-.5),B[1]-L*Math.sin(ang-.5)],[B[0],B[1]],[B[0]-L*Math.cos(ang+.5),B[1]-L*Math.sin(ang+.5)]],4.2);

  window.__boxes=['.txt','.hd','.sb','.tag','.fone','.pop','.sim','.base','.lg','.fant','.dig'].map(q=>{const el=document.querySelector(q); return el? q+' '+box(el.getBoundingClientRect()) : q+' -';});
  document.querySelectorAll('.fb').forEach((b,i)=>window.__boxes.push('fb'+i+' '+box(b.getBoundingClientRect())));
  bs.forEach((b,i)=>window.__boxes.push('b'+i+' '+box(b.getBoundingClientRect())));
  if(nr) window.__boxes.push('nota '+box(nr));
  window.__boxes.push('seta '+JSON.stringify(via.map(v=>v.map(Math.round))));
  document.querySelectorAll('.hd').forEach(h=>window.__boxes.push('hd scrollW '+h.scrollWidth+' clientW '+h.clientWidth));
});
</script>"""


def build(p):
    # "|" nos balões vira quebra de linha; todas as mensagens viram bolhas (o kit usa a última como pop, então soma uma muda)
    conv = [[q, t.replace("|", " ")] for q, t in p.get("conversa", [])]
    p = dict(p, conversa=conv + [["ia", "x"]])
    # pilar editorial (ex.: "atendimento") pode não existir na tabela de cores do kit; o celular3d não usa essas cores
    k = dict(p, pilar=p.get("pilar") if p.get("pilar") in R.PILARES else "ia")
    h = R.build(k).replace(" ", "<br>")
    h = h.replace("</style>", css(p) + "</style>", 1)
    if p.get("espelho", True):  # rastros de luz espelhados
        h = h.replace('<svg style="position:absolute;inset:0" width="1080"', '<svg class="luz" style="position:absolute;inset:0" width="1080"', 1)
    f = p.get("fantasma", {})
    linhas = "".join(f'<div class="fb">{html.escape(l)}</div>' for l in f.get("linhas", []))
    dig = (f'<div class="dig"><i></i><i></i><i></i>{html.escape(f["digitando"])}</div>' if f.get("digitando") else "")
    fant = f'<div class="fant">{linhas}{dig}</div>'
    js = JS.replace("__CI__", CI).replace("__P__", json.dumps(p, ensure_ascii=False))
    return h.replace("</body>", fant + js + "</body>", 1) if "</body>" in h else h + fant + js


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
