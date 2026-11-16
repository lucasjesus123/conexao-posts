"""Post 2026-11-16 08h: celular3d CLARO + 'a chave com etiqueta' (oficina), em HTML/SVG sobre o celular3d do kit.
Na oficina o carro chega e a CHAVE ganha uma etiqueta de papel com tudo anotado, pra ninguém perguntar de novo.
Por cima do celular3d claro: a chave 3D recortada (campanhas/assets/chave_carro3d.png, espelhada: argola à esquerda) deitada
no papel com sombra de contato, sobrepondo a borda do celular; da argola sai um arame fino até uma ETIQUETA DE CHAVE DE OFICINA
(cartão creme pautado, furo com reforço, 'OS 0417' carimbado em vermelho, escrita à mão em caneta azul). Não é a etiqueta
de preço kraft do arte_etiqueta.py.
Todas as mensagens da conversa viram bolhas (o pop do kit fica escondido: a etiqueta faz o papel do resumo).
A bolha do mecânico ganha estilo próprio (grafite, rótulo 'JORGE · MECÂNICO') e antes dela entra um aviso de sistema de repasse.
"🎤 Áudio · 0:14" vira bolha de áudio com onda desenhada.
Uso: python3 scripts/arte_chave.py render.json pasta_saida   (objeto ou lista; gera ID.jpg, ID.png e ID_story.png)
Campos extras do JSON (além dos do celular3d: tag, titulo, subtitulo, contato, conversa, cta, selo, tam, tema):
  txt_w, txt_top, sb_fs: coluna de texto; msgs_top, msgs_gap, bolha_fs, bolha_w: bolhas
  mecanico: índice da bolha do mecânico (padrão: última); mec_rotulo; aviso: texto do aviso de repasse ('' = sem aviso)
  sim_top, sim_right, sim_left: selo em pílula
  chave: {left, top, w, rot, espelho}; etiqueta: {left, top, w, rot, os, topo, linhas:[..], rodape}
  nota, nota_xy, nota_rot, nota_fs: anotação à mão (caneta azul)"""
import json, sys, html, base64, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI = R.AZUL, R.TINTA
CHAVE = ROOT / "campanhas" / "assets" / "chave_carro3d.png"
CANETA = "#1F3FA8"
VERMELHO = "#C8232B"


def mao():
    out = []
    for n in ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2"):
        f = ROOT / "campanhas" / "fontes" / n
        rng = ";unicode-range:U+0100-024F" if "ext" in n else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(f.read_bytes()).decode()}){rng}}}")
    return "".join(out)


def css(p):
    o = []
    if p.get("titulo_lh"): o.append(f".hd{{line-height:{p['titulo_lh']}}}")
    if p.get("txt_w"): o.append(f".txt{{width:{p['txt_w']}px!important}}")
    if p.get("txt_top"): o.append(f".txt{{top:{p['txt_top']}px!important}}")
    if p.get("sb_fs"): o.append(f".sb{{font-size:{p['sb_fs']}px!important}}")
    if p.get("msgs_top"): o.append(f".msgs{{top:{p['msgs_top']}px!important}}")
    if p.get("msgs_gap"): o.append(f".msgs{{gap:{p['msgs_gap']}px!important}}")
    if p.get("bolha_fs"): o.append(f".b{{font-size:{p['bolha_fs']}px!important}}")
    if p.get("bolha_w"): o.append(f".b{{max-width:{p['bolha_w']}%!important}}")
    if p.get("msgs_lr"): o.append(f".msgs{{left:{p['msgs_lr'][0]}px!important;right:{p['msgs_lr'][1]}px!important}}")
    if p.get("aviso_fs"): o.append(f".aviso{{font-size:{p['aviso_fs']}px!important}}")
    if p.get("cena"): c = p["cena"]; o.append(f".cena{{right:{c.get('right',-40)}px!important;top:{c.get('top',120)}px!important;width:{c.get('w',560)}px!important;height:{c.get('h',1080)}px!important}}")
    sim_pos = f"left:{p['sim_left']}px!important;right:auto!important" if "sim_left" in p else f"right:{p.get('sim_right',64)}px!important"
    ch, et = p.get("chave", {}), p.get("etiqueta", {})
    return "\n".join(o) + f"""
{mao()}
.pop{{display:none!important}}
.input{{padding-left:{p.get("input_pl",170)}px!important}}
.sim{{z-index:30!important;top:{p.get('sim_top',62)}px!important;{sim_pos};font-size:{p.get('sim_tam',19)}px!important;letter-spacing:.18em!important;
  color:{TI}!important;padding:9px 20px 8px;border:2px solid {AZ};border-radius:40px;background:rgba(255,255,255,.85);box-shadow:0 6px 18px rgba(47,107,255,.18)}}
.b.mec{{background:linear-gradient(160deg,#2A2F3A,#15181F)!important;color:#fff;align-self:flex-end;border-bottom-right-radius:6px;border-left:5px solid #F2B705}}
.b.mec i{{display:block;font-style:normal;font-family:Mono;font-size:14px;letter-spacing:.14em;color:#F2B705;margin-bottom:6px}}
.aviso{{align-self:center;font-family:Mono;font-size:13px;letter-spacing:.08em;color:rgba(11,13,18,.62);background:#E7EAF0;border-radius:12px;padding:7px 14px;text-align:center;white-space:nowrap}}
.b.aud{{display:flex;align-items:center;gap:12px;padding:12px 18px!important}}
.b.aud .pl{{width:34px;height:34px;border-radius:50%;background:{AZ};display:grid;place-items:center;flex:none}}
.b.aud small{{font-family:Mono;font-size:15px;color:rgba(11,13,18,.55)}}
.chv{{position:absolute;z-index:16;left:{ch.get('left',430)}px;top:{ch.get('top',900)}px;width:{ch.get('w',300)}px;transform:rotate({ch.get('rot',8)}deg)}}
.chv img{{display:block;width:100%;{'transform:scaleX(-1);' if ch.get('espelho', True) else ''}
  filter:drop-shadow(3px 5px 3px rgba(20,22,30,.45)) drop-shadow(16px 26px 22px rgba(30,40,70,.30))}}
.chv .pt{{position:absolute;width:2px;height:2px}}
.etq{{position:absolute;z-index:18;left:{et.get('left',64)}px;top:{et.get('top',800)}px;width:{et.get('w',360)}px;transform:rotate({et.get('rot',-6)}deg);
  background:#FBF7EA;border-radius:6px 6px 6px 6px;padding:18px 76px 18px 30px;color:{CANETA};
  background-image:linear-gradient(90deg,transparent 18px,rgba(200,35,43,.45) 18px,rgba(200,35,43,.45) 20px,transparent 20px),
    repeating-linear-gradient(180deg,transparent 0,transparent 41px,rgba(47,107,255,.22) 41px,rgba(47,107,255,.22) 43px);
  background-position:0 0,0 {et.get('pauta_y',62)}px;
  box-shadow:0 1px 1px rgba(0,0,0,.12),3px 6px 6px rgba(30,30,40,.16),14px 22px 30px rgba(30,40,70,.20)}}
.etq::before{{content:"";position:absolute;inset:0;border-radius:6px;pointer-events:none;
  background:radial-gradient(120% 80% at 20% 0%,rgba(255,255,255,.55),transparent 55%),linear-gradient(0deg,rgba(180,160,110,.10),transparent 30%)}}
.etq .furo{{position:absolute;right:16px;top:50%;margin-top:-20px;width:40px;height:40px;border-radius:50%;
  background:radial-gradient(circle,#EEECE6 0 8px,#DCCFA8 8.5px 9.5px,#F3E9C8 10px 17px,#D8C99C 17.5px 18.5px,transparent 19px)}}
.etq .et-topo{{font-family:Mono;font-size:13px;letter-spacing:.16em;color:rgba(11,13,18,.55);display:flex;justify-content:space-between;align-items:center;height:36px}}
.etq .os{{font-family:Mono;font-weight:800;font-size:25px;letter-spacing:.06em;color:{VERMELHO};border:3px solid {VERMELHO};border-radius:5px;padding:2px 9px 0;
  transform:rotate(-4deg);opacity:.86;-webkit-mask-image:radial-gradient(circle at 30% 40%,#000 55%,rgba(0,0,0,.55) 75%,#000 90%)}}
.etq .ln{{font-family:Hand;font-weight:600;font-size:{et.get('fs',33)}px;line-height:43px;white-space:nowrap}}
.etq .ln.j{{font-size:{et.get('fs_j',38)}px;color:{CANETA}}}
.etq .ln.j u{{text-decoration-thickness:2px;text-underline-offset:5px}}
.etq .rd{{font-family:Mono;font-size:12px;letter-spacing:.14em;color:rgba(11,13,18,.5);margin-top:6px}}
svg.fio{{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:19;pointer-events:none;overflow:visible}}
svg.fio2{{z-index:19}}
.hd{{white-space:nowrap}}
.nota{{position:absolute;z-index:20;font-family:Hand;font-weight:600;color:{CANETA};white-space:nowrap}}
"""


AUD = ('<div class="b e aud"><span class="pl"><svg width="14" height="16" viewBox="0 0 14 16"><path d="M2 1 L13 8 L2 15Z" fill="#fff"/></svg></span>'
       '<svg width="150" height="30" viewBox="0 0 150 30">{bars}</svg><small>{dur}</small></div>')


def ondas():
    hs = [6, 12, 20, 14, 24, 10, 18, 26, 16, 8, 14, 22, 12, 18, 9, 20, 14, 6, 11, 7, 13, 5]
    return "".join(f'<rect x="{i*7}" y="{15-h/2}" width="4" height="{h}" rx="2" fill="{AZ if i < 8 else "rgba(11,13,18,.28)"}"/>' for i, h in enumerate(hs))


JS = r"""<script>
document.fonts.ready.then(function(){
  const P=__P__, NS='http://www.w3.org/2000/svg';
  const c=e=>{const r=e.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];};
  const f=c(document.querySelector('.etq .furo')), a=c(document.querySelector('.chv .pt'));
  const mk=(cls)=>{const s=document.createElementNS(NS,'svg'); s.setAttribute('class',cls); document.body.appendChild(s); return s;};
  // arame: sai do furo, faz uma curva solta e entra na argola (a parte final passa por cima da etiqueta? não: por baixo da chave)
  const s=mk('fio'); const s2=mk('fio fio2');
  const mx=(f[0]+a[0])/2+(P.fio_dx||0), my=Math.max(f[1],a[1])+(P.fio_dy||60);
  const d=`M${f[0]-9} ${f[1]+2} C ${f[0]+30} ${f[1]+40}, ${mx-30} ${my}, ${mx} ${my} S ${a[0]-20} ${a[1]+20}, ${a[0]} ${a[1]}`;
  const pa=(sv,w,col,op,dd)=>{const e=document.createElementNS(NS,'path'); e.setAttribute('d',dd||d); e.setAttribute('fill','none'); e.setAttribute('stroke',col);
    e.setAttribute('stroke-width',w); e.setAttribute('stroke-opacity',op); e.setAttribute('stroke-linecap','round'); sv.appendChild(e); return e;};
  // sombra do arame no papel + arame (aço) com brilho
  const sh=pa(s,3,'#1a2030',.18); sh.setAttribute('transform','translate(4 7)'); sh.setAttribute('style','filter:blur(2px)');
  pa(s,3.2,'#6F7480',1); pa(s,1.2,'#E9ECF1',.9);
  // pedacinho do arame passando por cima da etiqueta (entra pelo furo)
  const d2=`M${f[0]-9} ${f[1]+2} C ${f[0]-2} ${f[1]+12}, ${f[0]+10} ${f[1]+20}, ${f[0]+24} ${f[1]+24}`; pa(s2,3.2,'#6F7480',1,d2); pa(s2,1.2,'#E9ECF1',.9,d2);
  window.__boxes=['.txt','.hd','.sb','.tag','.sim','.base','.fone','.msgs','.input','.chv','.etq','.nota','.lg'].map(q=>{const el=document.querySelector(q); if(!el) return q+' -'; const r=el.getBoundingClientRect();
    return q+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(',');});
  document.querySelectorAll('.msgs > *').forEach((b,i)=>{const r=b.getBoundingClientRect();
    const rg=document.createRange(); rg.selectNodeContents(b); const ls=[...rg.getClientRects()]; const last=ls.length?ls[ls.length-1]:null;
    window.__boxes.push('b'+i+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(',')+' ult_w '+(last?Math.round(last.width):'-'));});
  window.__boxes.push('furo '+f.map(Math.round)+' argola '+a.map(Math.round));
});
</script>"""


def bolhas(p):
    conv = p.get("conversa", [])
    imec = p.get("mecanico", len(conv) - 1)
    out = ""
    for i, (q, t) in enumerate(conv):
        if t.startswith("🎤"):
            out += AUD.format(bars=ondas(), dur=html.escape(t.split("·")[-1].strip()))
            continue
        tt = html.escape(t).replace("|", "<br>")
        if i == imec:
            if p.get("aviso", "Conversa passada para Jorge · mecânico"):
                out += f'<div class="aviso">{html.escape(p.get("aviso", "Conversa passada para Jorge · mecânico"))}</div>'
            out += f'<div class="b mec"><i>{html.escape(p.get("mec_rotulo", "JORGE · MECÂNICO"))}</i>{tt}</div>'
        else:
            out += f'<div class="b {"e" if q == "cliente" else "d"}">{tt}</div>'
    return out


def build(p):
    base = dict(p, conversa=[["ia", "x"], ["ia", ""]])  # o kit come a última; montamos as bolhas nós mesmos
    h = R.build(base).replace('<div class="msgs"><div class="b d">x</div></div>', f'<div class="msgs">{bolhas(p)}</div>', 1)
    h = h.replace("</style>", css(p) + "</style>", 1)
    if p.get("status"): h = h.replace("<small>● online agora</small>", f"<small>● {html.escape(p['status'])}</small>", 1)
    ch, et = p.get("chave", {}), p.get("etiqueta", {})
    # ponto da argola (em % da imagem já espelhada) onde o arame entra
    ax, ay = ch.get("argola", [11, 30])
    chave = (f'<div class="chv"><img src="{R.b64(CHAVE, "image/png")}"><span class="pt" style="left:{ax}%;top:{ay}%"></span></div>')
    linhas = et.get("linhas", [])
    lh = "".join(f'<div class="ln{" j" if l.startswith("→") else ""}">{html.escape(l) if not l.startswith("→") else "→ <u>" + html.escape(l[1:].strip()) + "</u>"}</div>' for l in linhas)
    etq = (f'<div class="etq"><span class="furo"></span><div class="et-topo"><span>{html.escape(et.get("topo", "OFICINA"))}</span>'
           f'<span class="os">{html.escape(et.get("os", "OS 0417"))}</span></div>{lh}'
           f'<div class="rd">{html.escape(et.get("rodape", ""))}</div></div>')
    nota = ""
    if p.get("nota"):
        x, y = p.get("nota_xy", [80, 1150])
        nota = f'<div class="nota" style="left:{x}px;top:{y}px;font-size:{p.get("nota_fs", 36)}px;transform:rotate({p.get("nota_rot", -4)}deg)">{html.escape(p["nota"])}</div>'
    js = JS.replace("__P__", json.dumps(p, ensure_ascii=False))
    extra = chave + etq + nota + js
    return h.replace("</body>", extra + "</body>", 1) if "</body>" in h else h + extra


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
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(700)
            for l in pg.evaluate("window.__boxes||[]"): print("  ", l)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
