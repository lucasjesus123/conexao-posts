"""Post 2026-10-31 08h: papel claro + 'Visualizou.' (conversa que morre na tela x resposta que continua), tudo em HTML/SVG.
Uso: python3 scripts/arte_visualizou.py post_render.json pasta_saida
Campos extras do JSON:
  conversa: [[quem ("cliente"|"loja"), texto, hora], ...]   thread que morre
  visto: texto do "Visualizado" (cor de alerta, com ✓✓ desenhado em SVG)
  vazio_nota: anotação à mão no vazio
  resposta: bolha final; {trecho} = marca-texto azul
  resposta_hora, setas: [rótulo da 1ª marca, rótulo da 2ª marca] (| = quebra)
  selo, thread_top, vazio_alt, fonte_mao (lista de caminhos .woff2 da Caveat)"""
import json, sys, html, base64, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI = R.AZUL, R.TINTA
ALERTA = "#E5484D"
CINZA = "#55524b"
VERDE = "#D9FDD3"

def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for i, f in enumerate(fs):
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)

def ticks(cor, h=22):
    return (f'<svg class="tk" width="{h*1.5:.0f}" height="{h}" viewBox="0 0 30 20"><g fill="none" stroke="{cor}" stroke-width="2.6" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="M2 11 L7 16 L17 4"/><path d="M12 15.5 L13 16 L23 4"/></g></svg>')

# marca-texto azul: mancha de borda irregular (cada fragmento de linha ganha a sua)
MT = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 40' preserveAspectRatio='none'>"
      "<path d='M3 9 C 40 4, 90 7, 140 4 S 190 6, 198 8 L 196 17 L 199 27 C 160 33, 110 31, 60 34 S 12 33, 2 31 L 4 21 Z' "
      "fill='%235B95FF' fill-opacity='.46'/></svg>")

def css(p):
    t = p.get("thread_top", 452)
    return mao(p) + f"""
.palco{{position:absolute;left:72px;right:72px;top:{t}px;z-index:2}}
.col{{width:640px;display:flex;flex-direction:column;gap:18px}}
.b{{position:relative;max-width:500px;padding:20px 26px 16px;border-radius:26px;font-size:33px;line-height:1.3;font-weight:500;letter-spacing:-.01em;color:{TI}}}
.b .h{{display:block;text-align:right;font-family:Mono;font-size:17px;letter-spacing:.04em;opacity:.45;margin-top:4px}}
.cli{{align-self:flex-start;background:#FFFFFF;border-top-left-radius:6px;box-shadow:0 1px 0 rgba(11,13,18,.06),0 10px 26px rgba(30,30,20,.06)}}
.loj{{align-self:flex-end;background:{VERDE};border-top-right-radius:6px;box-shadow:0 1px 0 rgba(11,13,18,.06),0 10px 26px rgba(30,60,20,.07)}}
.num{{font-weight:800;font-size:44px;letter-spacing:-.02em;line-height:1.1}}
.visto{{align-self:flex-end;display:flex;align-items:center;gap:10px;font-family:Mono;font-weight:500;font-size:26px;letter-spacing:.02em;color:{ALERTA};margin-top:-6px;padding-right:6px}}
.selo{{position:absolute;right:0;top:6px;font-family:Mono;font-size:15px;letter-spacing:.18em;padding:8px 14px;border:1.5px solid rgba(11,13,18,.28);border-radius:30px;opacity:.6}}
.vazio{{position:relative;height:{p.get('vazio_alt',268)}px;width:640px}}
.pont{{position:absolute;left:46px;top:18px;bottom:18px;width:0;border-left:2.5px dotted rgba(11,13,18,.22)}}
.vnota{{position:absolute;left:84px;top:{p.get('vnota_top',92)}px;font-family:Hand;font-weight:600;font-size:54px;line-height:1;color:{CINZA};transform:rotate(-2.5deg);white-space:nowrap}}
.fim{{position:relative;width:640px;display:flex;flex-direction:column}}
.fim{{align-items:flex-start}}
.fim .b{{max-width:640px;font-size:34px;line-height:1.42;padding:24px 34px 24px 28px}}
.fim .b .h{{display:inline-block;float:right;margin:22px 0 0 28px}}
.mt{{position:relative;-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 4px;margin:0 -4px;
  background:url("{MT}") center/100% 100% no-repeat}}
.lbl{{position:absolute;font-family:Hand;font-weight:600;font-size:40px;line-height:.95;color:{AZ};white-space:nowrap}}
svg.setas{{position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:3;pointer-events:none;overflow:visible}}
"""

def _mt(s):
    t = html.escape(s).replace("|", "<br>")
    return t.replace("{", '<span class="mt">').replace("}", "</span>")

def bloco(p):
    bolhas = []
    for quem, txt, hora in p["conversa"]:
        cls = "cli" if quem == "cliente" else "loj"
        corpo = f'<span class="num">{html.escape(txt)}</span>' if quem != "cliente" and len(txt) < 14 else html.escape(txt).replace("|", "<br>")
        bolhas.append(f'<div class="b {cls}">{corpo}<span class="h">{html.escape(hora)}</span></div>')
    visto = f'<div class="visto">{html.escape(p.get("visto","Visualizado 14:02"))}{ticks(ALERTA)}</div>'
    hora_fim = f'<span class="h">{html.escape(p["resposta_hora"])}</span>' if p.get("resposta_hora") else ""
    a, b = p.get("setas", ["o que vem|junto", "a pergunta|de volta"])
    lb = lambda s, i: f'<div class="lbl" id="l{i}">{html.escape(s).replace("|", "<br>")}</div>'
    return (f'<div class="palco"><div class="selo">{html.escape(p.get("selo","EXEMPLO"))}</div>'
            f'<div class="col">{"".join(bolhas)}{visto}</div>'
            f'<div class="vazio"><div class="pont"></div><div class="vnota">{html.escape(p["vazio_nota"])}</div></div>'
            f'<div class="fim"><div class="b loj">{_mt(p["resposta"])}{hora_fim}</div></div>'
            f'</div>{lb(a,0)}{lb(b,1)}<svg class="setas" id="setas"></svg>')

# posiciona os rótulos à direita da bolha final, cada um na altura da sua marca, e desenha a seta à mão
JS = """<script>
document.fonts.ready.then(function(){
  const mts=[...document.querySelectorAll('.mt')], sv=document.getElementById('setas'), NS='http://www.w3.org/2000/svg';
  const fim=document.querySelector('.fim .b').getBoundingClientRect();
  sv.innerHTML='<defs><marker id="pt" viewBox="0 0 12 12" refX="9" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">'+
    '<path d="M1 1.5 L10 6 L1 10.5" fill="none" stroke="__AZ__" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>';
  const lx=fim.right+56;
  mts.forEach((m,i)=>{
    const rs=[...m.getClientRects()], alvo=rs[rs.length-1], L=document.getElementById('l'+i); if(!L) return;
    const cyAlvo=alvo.top+alvo.height*0.5;
    L.style.left=lx+'px'; L.style.top=(cyAlvo-L.offsetHeight*(i?0.30:0.5)+(i?6:-10))+'px'; L.style.transform='rotate('+(i?-3:-2)+'deg)';
    const lr=L.getBoundingClientRect();
    const x1=lr.left-10, y1=lr.top+(i?24:lr.height*0.55), x2=alvo.right+10, y2=cyAlvo;
    const cx=(x1+x2)/2, cy=(y1+y2)/2+(i?18:-18);
    const pa=document.createElementNS(NS,'path');
    pa.setAttribute('d',`M${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`);
    pa.setAttribute('fill','none'); pa.setAttribute('stroke','__AZ__'); pa.setAttribute('stroke-width','2.6');
    pa.setAttribute('stroke-linecap','round'); pa.setAttribute('marker-end','url(#pt)'); sv.appendChild(pa);
  });
});
</script>""".replace("__AZ__", AZ)

def build(p):
    h = R.build(p)
    h = h.replace("</style>", css(p) + "</style>", 1)
    h = h.replace('<p class="s"></p>', "", 1)
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1).replace("</body>", JS + "</body>", 1)

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(500)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
