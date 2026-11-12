"""Post 2026-11-12 08h: papel claro + 'Senha 001' — rolo de senha de padaria/açougue do interior.
Um dispensador vermelho de plástico (cortado pela borda direita) solta a tira de senhas amarelo-manteiga, picotada.
A senha 001 já foi puxada: RASGADA no picote (borda irregular com fibras), solta, inclinada e à frente, com o número
gigante em tinta de bilhete falhada. As senhas 002–005 seguem presas na tira, cada uma com um critério; a 099
("projeto bonito") aparece pequena e desfocada, no fim da fila. Tudo em HTML/CSS/SVG sobre kit/render.py (sem imagem gerada).
Uso: python3 scripts/arte_senha.py post_render.json pasta_saida
Campos do JSON (lista de posts; o modelo base é o papel de kit/render.py):
  kicker (mono, topo), num (mono, topo direito, opcional), titulo ({itálico azul}, | quebra), tam, topo,
  apoio (linha de apoio abaixo do título), tam_apoio, apoio_top,
  senha: {"numero": "001", "vez": "SUA VEZ", "texto": "...", "left", "top", "w", "rot"},
  fila: [["002", "Repete toda|semana?"], ...] (presas na tira, da ponta rasgada até o dispensador; | = quebra),
  fim: ["099", "projeto bonito"] (pequena e desfocada), fim_pos: [x, y, rot, escala],
  tira: {"left", "top", "w", "h_tk", "rot"} (tira e dispensador), disp: {"left", "top"},
  dado: {"num", "texto", "fonte", "left", "top", "w"} (box fino)."""
import json, sys, html, pathlib, importlib.util, random, math
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PA = R.AZUL, R.TINTA, R.PAPEL
MANTEIGA = "#F4DE97"     # papel de senha
MANTEIGA2 = "#EBCF7E"
IMPRESSO = "#2B2622"     # tinta do bilhete
VERM = "#D7262B"         # plástico do dispensador
e = html.escape


def rasgo(w, seed, amp=7, base=0, lado="baixo"):
    """pontos de uma borda rasgada no picote (irregular, com dentes e fiapos), da esquerda para a direita"""
    rnd = random.Random(seed); pts = []; x = 0.0
    while x < w:
        y = base + rnd.uniform(0, amp) + (amp * .9 if rnd.random() < .12 else 0)
        pts.append((x, y)); x += rnd.uniform(3, 9)
    pts.append((w, base + rnd.uniform(0, amp)))
    return pts


def clip_rasgado(w, h, seed, topo=False, base_amp=8):
    """clip-path: retângulo com a borda de baixo (ou de cima) rasgada"""
    b = rasgo(w, seed, base_amp)
    if topo:
        borda = ",".join(f"{x:.1f}px {y:.1f}px" for x, y in b)
        return f"polygon({borda},{w}px {h}px,0px {h}px)"
    borda = ",".join(f"{x:.1f}px {h - base_amp - 2 + y:.1f}px" for x, y in reversed(b))
    return f"polygon(0px 0px,{w}px 0px,{borda})"


def fibras(w, seed, topo, h):
    """faixa clara de fibras expostas acompanhando o rasgo"""
    b = rasgo(w, seed, 8)
    rnd = random.Random(seed + 7)
    if topo:
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in b)
        d += " L" + " L".join(f"{x:.1f} {y + 3 + rnd.uniform(0, 5):.1f}" for x, y in reversed(b)) + " Z"
        y0 = 0
    else:
        d = "M" + " L".join(f"{x:.1f} {h - 10 + y:.1f}" for x, y in b)
        d += " L" + " L".join(f"{x:.1f} {h - 10 + y - 3 - rnd.uniform(0, 5):.1f}" for x, y in reversed(b)) + " Z"
        y0 = 0
    fios = []
    for _ in range(int(w / 14)):
        x = rnd.uniform(0, w); L = rnd.uniform(2, 7)
        if topo:
            fios.append(f'<path d="M{x:.1f} {rnd.uniform(0,6):.1f} l{rnd.uniform(-2,2):.1f} {-L:.1f}"/>')
        else:
            fios.append(f'<path d="M{x:.1f} {h - rnd.uniform(0,6):.1f} l{rnd.uniform(-2,2):.1f} {L:.1f}"/>')
    return (f'<svg class="fib" width="{w}" height="{h}" viewBox="0 {y0} {w} {h}" style="overflow:visible">'
            f'<path d="{d}" fill="rgba(255,252,238,.75)"/>'
            f'<g stroke="rgba(250,240,205,.9)" stroke-width="1" stroke-linecap="round">{"".join(fios)}</g></svg>')


FILTROS = """<svg width="0" height="0" style="position:absolute"><defs>
 <filter id="falha" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency=".38" numOctaves="3" seed="4" result="fino"/>
  <feTurbulence type="fractalNoise" baseFrequency=".022 .06" numOctaves="2" seed="8" result="largo"/>
  <feColorMatrix in="fino" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -16 0 0 0 13" result="a"/>
  <feColorMatrix in="largo" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -2 0 0 0 2.25" result="b"/>
  <feComposite in="a" in2="b" operator="arithmetic" k1="1" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in"/>
 </filter>
 <filter id="falha2" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency=".45" numOctaves="3" seed="11" result="fino"/>
  <feColorMatrix in="fino" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -16 0 0 0 12.6" result="a"/>
  <feComposite in="SourceGraphic" in2="a" operator="in"/>
 </filter>
</defs></svg>"""

NOISE_PAPEL = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'>"
               "<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.9 .35' numOctaves='3' seed='6'/>"
               "<feColorMatrix values='0 0 0 0 .5 0 0 0 0 .42 0 0 0 0 .25 0 0 0 .55 0'/></filter>"
               "<rect width='100%' height='100%' filter='url(%23f)'/></svg>\")")


def css(p):
    t = p["tira"]; s = p["senha"]; d = p["dado"]; ds = p.get("disp", {})
    TW, HT = t.get("w", 330), t.get("h_tk", 170)
    return f"""
.s{{display:none}}
h1{{z-index:6}}
.ap{{position:absolute;left:72px;right:72px;top:{p.get('apoio_top',420)}px;font-size:{p.get('tam_apoio',34)}px;font-weight:600;
  line-height:1.3;letter-spacing:-.012em;color:{TI};opacity:.78;z-index:6}}
.ap b{{font-weight:800;opacity:1;color:{TI}}}
/* papel de senha */
.tk{{position:relative;background:
  radial-gradient(130% 90% at 20% 0%,rgba(255,250,225,.75) 0,rgba(255,250,225,0) 55%),
  linear-gradient(175deg,{MANTEIGA} 0%,{MANTEIGA2} 100%);color:{IMPRESSO};overflow:hidden}}
.tk:before{{content:"";position:absolute;inset:0;opacity:.42;mix-blend-mode:multiply;pointer-events:none;background-image:{NOISE_PAPEL}}}
.tk .nm{{font-family:Anton;line-height:.9;letter-spacing:.01em;filter:url(#falha2)}}
.tk .q{{font-weight:800;letter-spacing:-.02em;line-height:1.12;text-wrap:balance}}
/* tira presa */
.tira{{position:absolute;left:{t.get('left',690)}px;top:{t.get('top',590)}px;width:{TW}px;z-index:3;transform:rotate({t.get('rot',3)}deg);transform-origin:50% 0;
  filter:drop-shadow(0 1px 1px rgba(60,45,20,.28)) drop-shadow(0 6px 6px rgba(60,45,20,.12)) drop-shadow(-16px 26px 30px rgba(50,38,20,.20))}}
.tira .tk,.fim .tk{{height:{HT}px;padding:0 22px 0 26px;display:flex;align-items:center;gap:20px}}
.tira .tk .nm,.fim .nm{{font-size:{t.get('tam_nm',66)}px;flex:none;padding-right:20px;border-right:2px dotted rgba(43,38,34,.35)}}
.tira .tk .q,.fim .q{{font-size:{t.get('tam_q',27)}px}}
.pic{{position:absolute;left:0;right:0;height:8px;top:-4px;z-index:2;
  background:radial-gradient(circle at 4px 4px,rgba(120,95,40,.55) 2.2px,rgba(120,95,40,.0) 2.9px) 2px 0/11px 8px repeat-x}}
.pic:after{{content:"";position:absolute;left:0;right:0;top:3px;height:2px;background:linear-gradient(180deg,rgba(255,250,230,.6),rgba(140,110,50,.18))}}
.tira .tk:after{{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(90deg,rgba(120,90,30,.10) 0,rgba(255,255,255,0) 18%,rgba(255,252,235,.22) 58%,rgba(120,90,30,.12) 100%)}}
.tira .tk.prim:after{{background:linear-gradient(180deg,rgba(60,10,10,.38) 0,rgba(60,10,10,.10) 14px,rgba(0,0,0,0) 34px),
  linear-gradient(90deg,rgba(120,90,30,.10) 0,rgba(255,255,255,0) 18%,rgba(255,252,235,.22) 58%,rgba(120,90,30,.12) 100%)}}
.tira .tk.ult{{clip-path:{clip_rasgado(TW, HT, 21)}}}
.tira .fib{{position:absolute;left:0;top:0;pointer-events:none}}
/* dispensador */
.disp{{position:absolute;left:{ds.get('left', t.get('left',690)-70)}px;top:{ds.get('top', t.get('top',590)-150)}px;width:560px;height:190px;z-index:4}}
.corpo{{position:absolute;inset:0;border-radius:95px 0 0 95px;
  background:
   radial-gradient(60% 40% at 30% 18%,rgba(255,255,255,.55) 0,rgba(255,255,255,0) 70%),
   linear-gradient(180deg,#F04A47 0%,{VERM} 30%,#B4141B 72%,#7E0B11 100%);
  box-shadow:inset 0 3px 2px rgba(255,190,180,.55),inset 0 -10px 18px rgba(70,0,5,.45),inset 18px 0 30px rgba(255,120,110,.25),
   0 2px 2px rgba(60,10,10,.25),0 18px 26px -6px rgba(70,15,15,.35),-20px 40px 50px -10px rgba(60,30,20,.25)}}
.corpo:before{{content:"";position:absolute;left:58px;right:40px;top:16px;height:22px;border-radius:20px;
  background:linear-gradient(180deg,rgba(255,255,255,.85),rgba(255,255,255,0));filter:blur(1.5px);opacity:.85}}
.corpo:after{{content:"";position:absolute;left:24px;top:58px;width:26px;height:70px;border-radius:20px;
  background:linear-gradient(90deg,rgba(255,255,255,.55),rgba(255,255,255,0));filter:blur(2px)}}
.frente{{position:absolute;left:30px;right:0;bottom:0;height:52px;border-radius:0 0 0 40px;
  background:linear-gradient(180deg,#A80F16 0%,#8E0C12 55%,#6E080D 100%);box-shadow:inset 0 2px 0 rgba(255,120,110,.45),inset 0 -3px 4px rgba(40,0,3,.5)}}
.emenda{{position:absolute;left:44px;right:0;bottom:52px;height:2px;background:rgba(80,0,6,.35);box-shadow:0 1px 0 rgba(255,150,140,.35)}}
.aro{{position:absolute;left:44px;right:-10px;top:24px;bottom:72px;border-radius:70px 0 0 70px;
  box-shadow:inset 0 2px 3px rgba(90,0,8,.45),inset 0 -2px 2px rgba(255,170,160,.4);background:linear-gradient(180deg,rgba(0,0,0,.06),rgba(255,255,255,.05))}}
.boca{{position:absolute;left:{70-6}px;width:{TW+12}px;bottom:-6px;height:30px;border-radius:6px 6px 10px 10px;
  background:linear-gradient(180deg,#1A0507,#3B0A0E 60%,#6A1016);box-shadow:inset 0 3px 5px rgba(0,0,0,.6),0 2px 0 rgba(255,140,130,.35)}}
.lam{{position:absolute;left:{70-12}px;width:{TW+24}px;bottom:-14px;height:13px;border-radius:2px;
  background:linear-gradient(180deg,#F4F6F8 0%,#B9C0C8 40%,#7D858F 70%,#D6DBE0 100%);
  box-shadow:0 2px 3px rgba(0,0,0,.35);clip-path:polygon(0 0,100% 0,100% 55%,{''.join(f'{100-(i+.5)*100/40:.2f}% 100%,{100-(i+1)*100/40:.2f}% 55%,' for i in range(40))}0 55%)}}
.parafuso{{position:absolute;width:16px;height:16px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff,#9aa1a8 45%,#4b5157 100%);
  box-shadow:0 1px 1px rgba(0,0,0,.4)}}
/* senha 001 rasgada */
.s1{{position:absolute;left:{s.get('left',70)}px;top:{s.get('top',560)}px;width:{s.get('w',560)}px;z-index:7;transform:rotate({s.get('rot',-8)}deg);
  filter:drop-shadow(0 1px 1px rgba(60,45,20,.35)) drop-shadow(0 4px 4px rgba(60,45,20,.10)) drop-shadow(-22px 34px 36px rgba(50,38,20,.26))}}
.s1 .tk{{height:{s.get('h',330)}px;padding:30px 36px 0 40px;clip-path:{clip_rasgado(s.get('w',560), s.get('h',330), 21, topo=True)}}}
.s1 .tk:after{{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(105deg,rgba(255,255,255,0) 55%,rgba(255,255,255,.22) 72%,rgba(120,90,30,.10) 100%)}}
.s1 .fib{{position:absolute;left:0;top:0;pointer-events:none}}
.s1 .vez{{font-family:Mono;font-weight:500;font-size:24px;letter-spacing:.24em;display:flex;align-items:center;gap:14px}}
.s1 .vez i{{width:12px;height:12px;border-radius:50%;background:{VERM}}}
.s1 .nm{{font-size:{s.get('tam',232)}px;margin-top:6px;letter-spacing:.005em;filter:url(#falha)}}
.s1 .tx{{font-weight:800;font-size:{s.get('tam_tx',31)}px;line-height:1.16;letter-spacing:-.02em;margin-top:4px;text-wrap:balance}}
.s1 .pic{{top:auto;bottom:6px;opacity:.0}}
/* 099 */
.fim{{position:absolute;left:{p.get('fim_pos',[900,1040,9,.5])[0]}px;top:{p.get('fim_pos',[900,1040,9,.5])[1]}px;width:{TW}px;z-index:1;
  transform:rotate({p.get('fim_pos',[0,0,9,.5])[2]}deg) scale({p.get('fim_pos',[0,0,9,.5])[3]});transform-origin:0 0;
  filter:blur(1.7px) drop-shadow(-6px 10px 10px rgba(50,38,20,.18));opacity:.78}}
/* dado */
.dd{{position:absolute;left:{d.get('left',72)}px;top:{d.get('top',1030)}px;width:{d.get('w',540)}px;z-index:6;
  border:1.5px solid rgba(11,13,18,.42);border-radius:8px;padding:16px 20px 12px 20px;display:grid;grid-template-columns:auto 1fr;column-gap:16px;align-items:center;
  background:rgba(255,255,255,.35)}}
.dd b{{font-family:M;font-weight:900;font-size:{d.get('tam',50)}px;line-height:1;letter-spacing:-.045em;color:{AZ}}}
.dd p{{font-size:{d.get('tam_tx',19)}px;line-height:1.28;font-weight:600;letter-spacing:-.01em;text-wrap:balance}}
.dd span{{grid-column:1/3;font-family:Mono;font-weight:500;font-size:16px;letter-spacing:.06em;opacity:.7;margin-top:9px;padding-top:7px;border-top:1px dashed rgba(11,13,18,.3)}}
.sombra-mesa{{position:absolute;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(70% 50% at 70% 70%,rgba(255,255,255,.35),rgba(255,255,255,0) 70%),radial-gradient(90% 60% at 100% 30%,rgba(60,45,25,.06),rgba(0,0,0,0) 60%)}}
"""


def ticket(num, txt, cls="", extra=""):
    q = "<br>".join(f'<span style="white-space:nowrap">{e(l)}</span>' for l in txt.split("|"))
    return f'<div class="tk {cls}">{extra}<div class="nm">{e(num)}</div><div class="q">{q}</div></div>'


def tira(p):
    t = p["tira"]; TW, HT = t.get("w", 330), t.get("h_tk", 170)
    fila = p["fila"]           # [002, 003, 004, 005]: a 002 é a ponta rasgada (embaixo), a 005 encosta no dispensador
    blocos = []
    for i, (n, q) in enumerate(reversed(fila)):
        ult = i == len(fila) - 1
        pic = '<div class="pic"></div>' if i > 0 else ''
        fib = fibras(TW, 21, False, HT) if ult else ''
        blocos.append(f'<div style="position:relative">{pic}{ticket(n, q, ("ult" if ult else "") + (" prim" if i == 0 else ""))}{fib}</div>')
    return f'<div class="tira">{"".join(blocos)}</div>'


def dispensador(p):
    return ('<div class="disp"><div class="corpo"><div class="aro"></div><div class="emenda"></div><div class="frente"></div></div><div class="boca"></div><div class="lam"></div>'
            '<div class="parafuso" style="left:96px;top:86px"></div></div>')


def senha1(p):
    s = p["senha"]; w = s.get("w", 560); h = s.get("h", 330)
    return (f'<div class="s1"><div class="tk"><div class="vez"><i></i>{e(s["vez"])}</div>'
            f'<div class="nm">{e(s["numero"])}</div><div class="tx">{"<br>".join(e(l) for l in s["texto"].split("|"))}</div></div>{fibras(w, 21, True, h)}</div>')


def fim(p):
    n, q = p["fim"]
    return f'<div class="fim">{ticket(n, q)}</div>'


def dado(p):
    d = p["dado"]
    return f'<div class="dd"><b>{e(d["num"])}</b><p>{e(d["texto"])}</p><span>{e(d["fonte"])}</span></div>'


def build(p):
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_papel(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    corpo = (FILTROS + '<div class="sombra-mesa"></div>' + f'<p class="ap">{R._ed(p["apoio"])}</p>'
             + fim(p) + tira(p) + dispensador(p) + senha1(p) + dado(p))
    return h.replace('<img class="marca"', corpo + '<img class="marca"', 1)


def checa(pg):
    return pg.evaluate("""() => {const r = s => {const e = document.querySelector(s); if(!e) return null;
      const b = e.getBoundingClientRect(); return [s, Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]};
      return ['h1','.ap','.s1','.tira','.disp','.fim','.dd','.marca','.handle'].map(r)}""")


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
            for c in checa(pg): print("  caixa", c)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
