"""Post 2026-11-07 08h: numero claro + 'O número que esfria' (59% com gradiente quente->gelo, régua de termômetro
à mão com dia 1 / dia 3 / dia 7 e cristais de gelo grudados na base do 5 e do 9), tudo em HTML/SVG.
Uso: python3 scripts/arte_esfria.py post_render.json pasta_saida   (o JSON pode ser um objeto ou uma lista)
Campos (além dos do modelo numero: kicker, numero, texto, fonte, topo, tam, tema):
  apoio: linha menor em itálico azul abaixo do texto
  nota_mao: linha à mão (Caveat azul) abaixo do apoio; kicker_tam/kicker_op: tamanho e opacidade do kicker
  grad: lista de cores do gradiente vertical do número, de cima para baixo
  regua: {"marcas": ["dia 1", "dia 3", "dia 7"], "cores": [quente, meio, gelo], "gap": distância do número (px)}
  gelo: {"n5": cristais na base do 5, "n9": cristais na base do 9}
  texto_w: largura do texto (px) · fonte_mao: lista de caminhos .woff2 da Caveat
  kit: pasta do kit (padrão: <repo>/kit ou /home/claude/kit)"""
import json, sys, html, base64, pathlib, importlib.util, random
ROOT = pathlib.Path(__file__).resolve().parent.parent

def _kit(p=None):
    for k in ([p.get("kit")] if p and p.get("kit") else []) + [ROOT / "kit", "/home/claude/kit"]:
        f = pathlib.Path(k) / "render.py"
        if f.exists():
            return f
    raise SystemExit("render.py do kit não encontrado")

spec = importlib.util.spec_from_file_location("render", _kit())
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI = R.AZUL, R.TINTA
GRAD = ["#FF6A2B", "#F2B544", "#8FB8FF", "#5B8DEF"]
MARCAS = ["dia 1", "dia 3", "dia 7"]
CORES = ["#E8452B", "#C98A12", "#3F74E0"]

def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)

def cristal(s, rot, op, cor):
    """asterisco fino de 6 pontas com farpinhas (floco simplificado), traço branco/azul-claro"""
    g = []
    for i in range(6):
        a = i * 60
        g.append(f'<g transform="rotate({a})"><path d="M0 0 V-46"/><path d="M0 -26 L-9 -35 M0 -26 L9 -35"/>'
                 f'<path d="M0 -38 L-5 -43 M0 -38 L5 -43"/></g>')
    return (f'<svg class="cr" viewBox="-50 -50 100 100" width="{s}" height="{s}" style="opacity:{op};transform:rotate({rot}deg)">'
            f'<g fill="none" stroke="{cor}" stroke-width="5" stroke-linecap="round">{"".join(g)}</g>'
            f'<circle r="5" fill="{cor}"/></svg>')

def css(p):
    g = p.get("grad", GRAD)
    stops = ",".join(f"{c} {round(i*100/(len(g)-1))}%" for i, c in enumerate(g))
    return mao(p) + f"""
.n{{white-space:nowrap}}
.n span{{position:relative;display:inline-block;background:linear-gradient(180deg,{stops});
  background-size:100% var(--gh,100%);background-position:0 var(--gy,0);background-repeat:no-repeat;
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 1px 0 rgba(11,13,18,.06))}}
.bl{{display:inline-block;width:0;height:0;vertical-align:baseline}}
.l{{right:auto!important;width:{p.get('texto_w',880)}px;text-wrap:pretty}}
.ap{{position:absolute;left:72px;width:900px;font-family:Serif;font-style:italic;font-weight:500;font-size:{p.get('apoio_tam',36)}px;
  line-height:1.2;color:{AZ};letter-spacing:-.01em}}
.f{{text-wrap:balance;line-height:1.6}}
#gelo{{position:absolute;left:0;top:0;width:1080px;height:1350px;pointer-events:none;z-index:3}}
.cr{{position:absolute;overflow:visible;filter:drop-shadow(0 0 1.5px rgba(40,80,160,.55)) drop-shadow(0 2px 3px rgba(20,40,90,.25))}}
#regua{{position:absolute;left:0;top:0;width:1080px;height:1350px;overflow:visible;pointer-events:none;z-index:2}}
.k{{font-size:{p.get('kicker_tam',19)}px!important;opacity:{p.get('kicker_op',.6)}!important}}
.nm{{position:absolute;left:72px;font-family:Hand;font-weight:600;font-size:{p.get('nota_tam',44)}px;line-height:1.1;color:{AZ};transform:rotate(-1.5deg);transform-origin:left}}
.mk{{position:absolute;font-family:Hand;font-weight:600;font-size:{p.get('regua',{}).get('fs',50)}px;line-height:1;white-space:nowrap}}
"""

def bloco(p):
    r = p.get("regua", {})
    marcas, cores = r.get("marcas", MARCAS), r.get("cores", CORES)
    mk = "".join(f'<div class="mk" id="mk{i}" style="color:{c};transform:rotate({(-3,2,-2)[i%3]}deg)">{html.escape(m)}</div>'
                 for i, (m, c) in enumerate(zip(marcas, cores)))
    gl = p.get("gelo", {})
    rnd = random.Random(7)
    cr = []
    for d, n in (("5", gl.get("n5", 3)), ("9", gl.get("n9", 3))):
        for i in range(n):
            s = rnd.choice([44, 36, 54, 32, 48])
            cor = "#FFFFFF" if i % 2 == 0 else "#DCEBFF"
            cr.append(f'<div class="cw" data-d="{d}" data-i="{i}" data-n="{n}" style="position:absolute">{cristal(s, rnd.randint(0,50), round(rnd.uniform(.75,.92),2), cor)}</div>')
    ap = f'<div class="ap" id="ap">{R._ed(p["apoio"])}</div>' if p.get("apoio") else ""
    if p.get("nota_mao"): ap += f'<div class="nm" id="nm">{html.escape(p["nota_mao"])}</div>'
    return ap + f'<svg id="regua"></svg>{mk}<div id="gelo">{"".join(cr)}</div>'

JS = """<script>
document.fonts.ready.then(function(){
  const N=document.querySelector('.n'), sp=[...N.querySelectorAll('span')];
  // gradiente contínuo: cada dígito usa o mesmo trecho vertical (do topo ao pé da tinta)
  const bl=document.getElementById('bl').getBoundingClientRect().top;     // linha de base
  const fsz=parseFloat(getComputedStyle(N).fontSize), cv=document.createElement('canvas').getContext('2d');
  cv.font=fsz+'px Anton'; const mt=cv.measureText(N.textContent), capH=mt.actualBoundingBoxAscent;
  const topInk=bl-capH;
  sp.forEach(s=>{const r=s.getBoundingClientRect(); s.style.setProperty('--gh',capH+'px'); s.style.setProperty('--gy',(topInk-r.top)+'px');});
  // texto e apoio logo abaixo
  const ap=document.getElementById('ap'), L=document.querySelector('.l');
  if(ap){ap.style.top=(L.getBoundingClientRect().bottom+__APGAP__)+'px';}
  const nm=document.getElementById('nm'); if(nm){nm.style.top=((ap||L).getBoundingClientRect().bottom+(ap?40:__APGAP__))+'px';}
  // régua termômetro à direita do número
  const pc=sp[sp.length-1].getBoundingClientRect();
  const x=pc.right+__GAP__, y1=topInk+6, y2=bl-6, NS='http://www.w3.org/2000/svg', sv=document.getElementById('regua');
  const cores=__CORES__;
  let d=`<defs><linearGradient id="gr" x1="0" y1="${y1}" x2="0" y2="${y2}" gradientUnits="userSpaceOnUse">`+
        `<stop offset="0" stop-color="${cores[0]}"/><stop offset=".5" stop-color="${cores[1]}"/><stop offset="1" stop-color="${cores[2]}"/></linearGradient></defs>`;
  // haste levemente torta (traço à mão) + bulbo
  d+=`<path d="M${x} ${y1} C ${x+1.5} ${y1+(y2-y1)*.3}, ${x-1.5} ${y1+(y2-y1)*.65}, ${x+.5} ${y2}" fill="none" stroke="__TI__" stroke-width="3" stroke-linecap="round"/>`;
  d+=`<circle cx="${x+.5}" cy="${y2+16}" r="13" fill="none" stroke="__TI__" stroke-width="3"/><circle cx="${x+.5}" cy="${y2+16}" r="6" fill="${cores[2]}"/>`;
  const marcasIdx=[0,3,6];
  for(let i=0;i<7;i++){
    const y=y1+(y2-y1)*i/6, big=marcasIdx.includes(i), w=big?26:14;
    d+=`<path d="M${x-w/2} ${y+(i%2?1:-1)} L ${x+w/2+ (big?6:0)} ${y}" stroke="${big?'url(#gr)':'__TI__'}" stroke-width="${big?4:2.6}" stroke-linecap="round" fill="none"/>`;
  }
  sv.innerHTML=d;
  marcasIdx.forEach((t,k)=>{const m=document.getElementById('mk'+k); if(!m) return;
    const y=y1+(y2-y1)*t/6; m.style.left=(x+30)+'px'; m.style.top=(y-m.offsetHeight*.55)+'px';});
  // cristais: grudados na base da tinta do 5 e do 9
  const pos={'5':sp[0].getBoundingClientRect(),'9':sp[1].getBoundingClientRect()};
  const lay={'5':[[.2,.06],[.5,.11],[.8,.05],[.62,-.02]],'9':[[.24,.08],[.56,.03],[.84,.1],[.40,-.02]]};
  document.querySelectorAll('.cw').forEach(c=>{
    const r=pos[c.dataset.d], i=+c.dataset.i, L2=lay[c.dataset.d][i%4], sv2=c.firstChild, s=sv2.width.baseVal.value;
    c.style.left=(r.left+r.width*L2[0]-s/2)+'px'; c.style.top=(bl-capH*L2[1]-s/2-4)+'px';
  });
});
</script>"""

def build(p):
    p = dict(p); p.setdefault("tema", "claro")
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_numero(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    num = "".join(f"<span>{html.escape(ch)}</span>" for ch in p["numero"]) + '<i class="bl" id="bl"></i>'
    h = h.replace(f'<div class="n">{html.escape(p["numero"])}</div>', f'<div class="n">{num}</div>', 1)
    js = (JS.replace("__GAP__", str(p.get("regua", {}).get("gap", 44)))
            .replace("__APGAP__", str(p.get("apoio_gap", 26)))
            .replace("__CORES__", json.dumps(p.get("regua", {}).get("cores", CORES))).replace("__TI__", TI))
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1).replace("</body>", js + "</body>", 1)

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text())
    posts = posts if isinstance(posts, list) else [posts]
    out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(600)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
