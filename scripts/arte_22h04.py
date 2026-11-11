"""Post 2026-11-11 08h: numero claro + '22h04' (a hora em que o cliente perguntou). Número gigante em Anton com o "04" em
azul e anéis concêntricos finos ao redor (relógio marcando a hora); sobre a base do número, girada, uma conversa NEUTRA
de mensageiro em HTML (sem layout de app): pergunta do cliente às 22:04 e resposta da loja às 08:47, com "Amanhã cedo"
sublinhado à mão em vermelho e a nota em Caveat "antes: educado → agora: demora" com seta curva. Selo SIMULAÇÃO.
Tudo em HTML/CSS/SVG sobre o modelo numero de kit/render.py (sem imagem gerada).
Uso: python3 scripts/arte_22h04.py post_render.json pasta_saida   (o JSON pode ser um objeto ou uma lista)
Campos (além dos do modelo numero: kicker, numero, texto, fonte, topo, tam, tema):
  destaque: trecho final do número que fica azul e ganha os anéis (ex.: "04")
  conversa: [[quem ("cliente"|"loja"), texto, hora], ...]   na resposta da loja, {trecho} = sublinhado à mão em vermelho
  nota_mao: ["linha", ...] em Caveat vermelha, logo abaixo da resposta, com seta curva subindo até o {trecho}
  nota_xy: [dx a partir do {trecho}, dy abaixo da resposta] · selo_x: distância do selo à direita da resposta
  selo: selo discreto junto da conversa (padrão "SIMULAÇÃO")
  chat_left, chat_w, chat_rot, chat_sobe (px que a conversa sobe sobre a base do número), fs_chat
  aneis: [raio1, raio2] em px (padrão automático), texto_w, apoio, apoio_tam, gap_bar
  fonte_mao: lista de caminhos .woff2 da Caveat · kit: pasta do kit"""
import json, sys, html, base64, pathlib, importlib.util
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
VERMELHO = "#D42A2A"
VERDE = "#E7F6E9"


def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)


def ticks(cor="#9AA0A8", h=20):
    return (f'<svg class="tk" width="{h*1.5:.0f}" height="{h}" viewBox="0 0 30 20"><g fill="none" stroke="{cor}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="M2 11 L7 16 L17 4"/><path d="M12 15.5 L13 16 L23 4"/></g></svg>')


def css(p):
    return mao(p) + f"""
.n{{white-space:nowrap;z-index:1}}
.n .az{{color:{AZ}}}
.bl{{display:inline-block;width:0;height:0;vertical-align:baseline}}
#aneis{{position:absolute;left:0;top:0;width:1080px;height:1350px;pointer-events:none;z-index:0;overflow:visible}}
.k{{font-size:{p.get('kicker_tam',21)}px!important;opacity:{p.get('kicker_op',.7)}!important}}
.l{{right:auto!important;width:{p.get('texto_w',900)}px;text-wrap:pretty}}
.ap{{position:absolute;left:72px;width:900px;font-size:{p.get('apoio_tam',32)}px;font-weight:600;line-height:1.3;opacity:.62;letter-spacing:-.01em}}
.f{{text-wrap:balance;line-height:1.6}}
.chat{{position:absolute;left:{p.get('chat_left',92)}px;width:{p.get('chat_w',640)}px;z-index:4;transform:rotate({p.get('chat_rot',-2)}deg);
  transform-origin:30% 50%;display:flex;flex-direction:column;gap:18px}}
.b{{position:relative;max-width:560px;padding:20px 26px 14px;border-radius:26px;font-size:{p.get('fs_chat',34)}px;line-height:1.28;font-weight:600;
  letter-spacing:-.012em;color:{TI}}}
.b .h{{display:flex;justify-content:flex-end;align-items:center;gap:8px;font-family:Mono;font-size:18px;letter-spacing:.04em;color:rgba(11,13,18,.5);margin-top:6px}}
.cli{{align-self:flex-start;background:#FFFFFF;border-top-left-radius:6px;
  box-shadow:0 1px 1px rgba(11,13,18,.08),0 14px 30px rgba(30,30,20,.12),0 2px 6px rgba(30,30,20,.06)}}
.loj{{align-self:flex-end;background:{VERDE};border-top-right-radius:6px;
  box-shadow:0 1px 1px rgba(11,13,18,.08),0 14px 30px rgba(30,60,20,.12),0 2px 6px rgba(30,60,20,.06)}}
.em{{font-family:"Noto Color Emoji";font-weight:400;font-size:.9em}}
.rs{{position:relative;white-space:nowrap}}
.rs svg{{position:absolute;left:-6px;width:calc(100% + 12px);top:84%;height:20px;overflow:visible}}
.selo{{position:absolute;font-family:Mono;font-size:15px;font-weight:500;letter-spacing:.2em;padding:7px 12px 6px;border:1.5px solid rgba(11,13,18,.32);
  border-radius:30px;color:rgba(11,13,18,.6);background:rgba(238,236,230,.85);white-space:nowrap}}
.nm{{position:absolute;font-family:Hand;font-weight:600;font-size:{p.get('nota_tam',46)}px;line-height:1.02;color:{VERMELHO};
  transform:rotate(-3deg);transform-origin:left center;white-space:nowrap;z-index:5}}
#seta{{position:absolute;left:0;top:0;width:1080px;height:1350px;pointer-events:none;z-index:6;overflow:visible}}
"""


def sublinhado():
    """dois traços de caneta vermelha, levemente tortos (sublinhado à mão)"""
    return (f'<svg viewBox="0 0 200 22" preserveAspectRatio="none">'
            f'<path d="M2 8 C 40 4, 90 9, 140 5 S 190 6, 198 4" fill="none" stroke="{VERMELHO}" stroke-width="4.2" '
            f'stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
            f'<path d="M10 17 C 60 12, 120 16, 194 11" fill="none" stroke="{VERMELHO}" stroke-width="3" stroke-linecap="round" '
            f'vector-effect="non-scaling-stroke" opacity=".8"/></svg>')


def _txt(s):
    t = html.escape(s)
    t = t.replace("{", '<span class="rs" id="alvo">').replace("}", sublinhado() + "</span>")
    return t.replace("🙂", '<span class="em">🙂</span>')


def bloco(p):
    bolhas = []
    for quem, txt, hora in p["conversa"]:
        cls = "cli" if quem == "cliente" else "loj"
        tk = ticks() if quem == "cliente" else ""
        bolhas.append(f'<div class="b {cls}">{_txt(txt)}<span class="h">{html.escape(hora)}{tk}</span></div>')
    nota = p.get("nota_mao", ["antes: educado", "→ agora: demora"])
    ap = f'<div class="ap" id="ap">{html.escape(p["apoio"])}</div>' if p.get("apoio") else ""
    return (f'<svg id="aneis"></svg><div class="chat" id="chat">{"".join(bolhas)}</div>'
            f'<div class="selo" id="selo">{html.escape(p.get("selo", "SIMULAÇÃO"))}</div>'
            f'<div class="nm" id="nm">{"<br>".join(html.escape(x) for x in nota)}</div><svg id="seta"></svg>{ap}')


JS = """<script>
document.fonts.ready.then(function(){
  const N=document.querySelector('.n'), az=N.querySelector('.az');
  const bl=document.getElementById('bl').getBoundingClientRect().top;
  const fsz=parseFloat(getComputedStyle(N).fontSize), cv=document.createElement('canvas').getContext('2d');
  cv.font=fsz+'px Anton'; const capH=cv.measureText('0').actualBoundingBoxAscent, topInk=bl-capH;
  // anéis concêntricos em volta do destaque (relógio marcando a hora)
  const a=az.getBoundingClientRect(), cx=(a.left+a.right)/2, cy=topInk+capH/2, NS='http://www.w3.org/2000/svg';
  const R0=__ANEIS__ || [Math.max(a.width,capH)*0.72, Math.max(a.width,capH)*0.82];
  let s='';
  R0.forEach((r,i)=>{ s+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="__AZ__" stroke-width="${i?1.6:2.2}" opacity="${i?.16:.26}"/>`; });
  // marquinhas de minuto no anel externo (sutis)
  const ro=R0[R0.length-1];
  for(let k=0;k<12;k++){const t=k*Math.PI/6, x1=cx+Math.cos(t)*(ro-10), y1=cy+Math.sin(t)*(ro-10), x2=cx+Math.cos(t)*ro, y2=cy+Math.sin(t)*ro;
    s+=`<path d="M${x1} ${y1} L${x2} ${y2}" stroke="__AZ__" stroke-width="2" opacity=".22" stroke-linecap="round"/>`;}
  document.getElementById('aneis').innerHTML=s;
  // conversa sobe sobre a base do número
  const ch=document.getElementById('chat'); ch.style.top=(bl-__SOBE__)+'px';
  const cr=ch.getBoundingClientRect();
  // selo: à direita da resposta da loja, centrado na altura dela
  const se=document.getElementById('selo'), lj=ch.querySelector('.loj').getBoundingClientRect();
  se.style.left=(lj.right+__SELOX__)+'px'; se.style.top=(lj.top+(lj.height-se.offsetHeight)/2)+'px';
  // nota à mão logo abaixo da resposta, com seta curva subindo até o sublinhado
  const nm=document.getElementById('nm'), al=document.getElementById('alvo').getBoundingClientRect();
  nm.style.left=(al.left+__NMX__)+'px'; nm.style.top=(lj.bottom+__NMY__)+'px';
  const nr=nm.getBoundingClientRect();
  const x1=nr.left-14, y1=nr.top+nr.height*0.55, x2=al.left+34, y2=al.bottom+16;
  const mx=x2-26, my=y1+6;
  const sv=document.getElementById('seta');
  sv.innerHTML=`<path d="M${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}" fill="none" stroke="__VM__" stroke-width="3.6" stroke-linecap="round"/>`+
    `<path d="M${x2-11} ${y2+15} L ${x2} ${y2} L ${x2+13} ${y2+13}" fill="none" stroke="__VM__" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>`;
  // barra, texto e apoio abaixo de tudo
  const base=Math.max(cr.bottom, se.getBoundingClientRect().bottom, nr.bottom);
  const bar=document.querySelector('.bar'), L=document.querySelector('.l');
  bar.style.top=(base+__GAPBAR__)+'px'; L.style.top=(base+__GAPBAR__+14+44)+'px';
  const ap=document.getElementById('ap'); if(ap){ap.style.top=(L.getBoundingClientRect().bottom+__APGAP__)+'px';}
  window.__caixas={chat:[cr.left,cr.top,cr.right,cr.bottom],nota:[nr.left,nr.top,nr.right,nr.bottom],
    l:L.getBoundingClientRect().bottom, ap:ap?ap.getBoundingClientRect().bottom:0, f:document.querySelector('.f').getBoundingClientRect().top};
});
</script>"""


def build(p):
    p = dict(p); p.setdefault("tema", "claro")
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_numero(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    n, d = p["numero"], p.get("destaque", "04")
    pre = n[:-len(d)] if d and n.endswith(d) else n
    num = html.escape(pre) + (f'<span class="az">{html.escape(d)}</span>' if pre != n else "") + '<i class="bl" id="bl"></i>'
    h = h.replace(f'<div class="n">{html.escape(n)}</div>', f'<div class="n">{num}</div>', 1)
    nx, ny = p.get("nota_xy", [70, 14])
    js = (JS.replace("__ANEIS__", json.dumps(p.get("aneis")) if p.get("aneis") else "null")
            .replace("__SOBE__", str(p.get("chat_sobe", 60))).replace("__GAPBAR__", str(p.get("gap_bar", 70)))
            .replace("__APGAP__", str(p.get("apoio_gap", 26))).replace("__NMX__", str(nx)).replace("__SELOX__", str(p.get("selo_x", 26))).replace("__NMY__", str(ny))
            .replace("__AZ__", AZ).replace("__VM__", VERMELHO))
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
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(700)
            print("  caixas", pg.evaluate("window.__caixas"))
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
