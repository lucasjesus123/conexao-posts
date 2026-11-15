"""Post 2026-11-15 08h: papel claro + 'Doze folhinhas do mesmo dia' — leque de 12 folhas de folhinha de destacar
(calendário de brinde de loja do interior, papel jornal, número vermelho enorme), todas do mesmo dia: 25 DEZ, uma por
ano de 2015 a 2026. As de baixo amareladas, com o furo do grampo rasgado e canto dobrado, cortadas pelas bordas de
cima/esquerda (quebra de moldura); a de cima, 2026, nova, com o "25" gigante e a anotação a caneta azul. Em algumas
folhas velhas, "surpresa?" a lápis, riscado. O olho entra no "25" de 2026, desce e sai no título.
Tudo em HTML/CSS/SVG sobre o modelo papel de kit/render.py (sem imagem gerada).
Uso: python3 scripts/arte_folhinha.py posts/2026-11-15-08h/render.json out
Campos extras do JSON (além dos do modelo papel: kicker, num, titulo, tam, topo, subtitulo):
  k_top: topo do kicker (px; o kicker desce para logo acima do título, fora do leque)
  fonte: linha mono da fonte do dado (abaixo do subtítulo); tam_sub: tamanho do subtítulo; sub_gap: respiro título→dado
  folha_w, folha_h: tamanho de cada folhinha (px)
  folhas: lista em ordem de empilhamento (a primeira fica por baixo), cada uma
          {"ano", "left", "top", "rot" (graus), "idade" (0 = nova .. 1 = amarelada),
           "dobra": "be"|"bd"|"" (canto dobrado embaixo à esquerda/direita), "tam_dobra": px,
           "surpresa": [x, y, rot] (posição local do 'surpresa?' a lápis riscado; omitir = sem),
           "nota": true (só na de cima: anotação a caneta azul)}
  nota: linhas da anotação a caneta azul; nota_xy: [x, y, rot] local na folha; tam_nota
  loja: linha miúda do brinde no pé da folhinha
  fonte_mao: lista de caminhos .woff2 da Caveat"""
import json, sys, html, base64, pathlib, importlib.util, random, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PA = R.AZUL, R.TINTA, R.PAPEL
CANETA = "#1D44B8"     # esferográfica azul
LAPIS = "#5E5E5C"      # grafite
GRAMPOS = (.27, .73)  # posição dos 2 grampos do bloco (fração da largura)
DIAS = ["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO", "DOMINGO"]


def mix(a, b, t):
    a, b = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)


def contorno(W, H, seed, rasgado, dobra, fd):
    """clip-path: borda de cima picotada (destacada do bloco); nas velhas, o furo do grampo arrancado (mordida
    irregular no meio do topo); canto dobrado = canto cortado (a aba é desenhada por cima)."""
    rnd = random.Random(seed); pts = []; x = 0.0
    furos = [(W * c - 30 + rnd.uniform(-6, 6), W * c + 30 + rnd.uniform(-6, 6), rnd.uniform(18, 30)) for c in GRAMPOS]
    while x < W:
        fu = next((f for f in furos if f[0] <= x <= f[1]), None) if rasgado else None
        if fu:                                # furo do grampo arrancado: mordida torta no papel
            fx0, fx1, fundo = fu
            for k in range(9):
                t = k / 8; xx = fx0 + (fx1 - fx0) * t
                pts.append((xx, 3 + fundo * (1 - (2 * t - 1) ** 2) ** .8 + rnd.uniform(-3, 3)))
            x = fx1 + 4; continue
        pts.append((x, rnd.uniform(0, 2.4) if not rasgado else rnd.uniform(0, 4.5)))
        x += rnd.uniform(5, 9)
    pts.append((W, rnd.uniform(0, 2)))
    if dobra == "bd":
        pts += [(W, H - fd), (W - fd, H), (0, H)]
    elif dobra == "be":
        pts += [(W, H), (fd, H), (0, H - fd)]
    else:
        pts += [(W, H), (0, H)]
    return "polygon(" + ",".join(f"{a:.1f}px {b:.1f}px" for a, b in pts) + ")"


def aba(W, H, dobra, fd, idade):
    """aba do canto dobrado: reflexo do triângulo cortado, verso do papel um pouco mais escuro"""
    if not dobra:
        return ""
    cor0, cor1 = mix("#EFE7D2", "#D9C291", idade), mix("#E2D7BC", "#C7AC74", idade)
    if dobra == "be":
        pol, ang, sx = f"0 {H - fd}px,{fd}px {H}px,{fd}px {H - fd}px", 225, "-3px 3px"
    else:
        pol, ang, sx = f"{W}px {H - fd}px,{W - fd}px {H}px,{W - fd}px {H - fd}px", 135, "3px 3px"
    return (f'<div class="aba" style="filter:drop-shadow({sx} 4px rgba(60,40,10,.30))"><div style="position:absolute;inset:0;'
            f'clip-path:polygon({pol});background:linear-gradient({ang}deg,{cor1} 0,{cor0} 55%,{mix(cor0, "#FFFFFF", .25)} 100%)"></div></div>')


def lapis(x, y, rot, seed):
    rnd = random.Random(seed)
    y1 = 30 + rnd.uniform(-2, 2)
    risco = (f'M-6 {y1 - 6:.1f} C 36 {y1 - 11:.1f}, 80 {y1:.1f}, 132 {y1 - 9:.1f} '
             f'M2 {y1:.1f} C 44 {y1 - 5:.1f}, 90 {y1 + 4:.1f}, 128 {y1 - 3:.1f}')
    return (f'<div class="lp" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)"><span>surpresa?</span>'
            f'<svg viewBox="-10 0 170 60" width="170" height="60"><path d="{risco}" fill="none" stroke="{LAPIS}" '
            f'stroke-width="2.6" stroke-linecap="round" opacity=".85"/></svg></div>')


def nota(p):
    x, y, rot = p.get("nota_xy", [56, 474, -4])
    linhas = p.get("nota", [])
    corpo = "<br>".join(html.escape(l) for l in linhas)
    return (f'<div class="nt" style="left:{x}px;top:{y}px;transform:rotate({rot}deg);font-size:{p.get("tam_nota", 36)}px">'
            f'{corpo}<svg class="sub-nt" viewBox="0 0 200 14" preserveAspectRatio="none"><path d="M2 9 C 50 4, 120 12, 198 5" '
            f'fill="none" stroke="{CANETA}" stroke-width="3" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg></div>')


def folha(p, f, i):
    W, H = p.get("folha_w", 470), p.get("folha_h", 650)
    ano = int(f["ano"]); idade = f.get("idade", 0)
    dobra, fd = f.get("dobra", ""), f.get("tam_dobra", 64)
    papel0 = mix("#F7F4EA", "#E8D6A6", idade)        # papel jornal novo → amarelado
    papel1 = mix("#EFEADC", "#DCC48A", idade)
    verm = mix("#D6231C", "#B44A3B", idade * .9)      # vermelho desbota
    tinta = mix("#1B1A18", "#4A4136", idade)
    dia = DIAS[datetime.date(ano, 12, 25).weekday()]
    rasgado = idade > 0
    # manchas de umidade/oxidação só nas velhas
    rnd = random.Random(ano)
    manchas = ",".join(
        f"radial-gradient({rnd.randint(60, 160)}px {rnd.randint(40, 120)}px at {rnd.randint(5, 95)}% {rnd.randint(10, 95)}%,"
        f"rgba(170,120,40,{.10 * idade:.3f}),rgba(170,120,40,0) 70%)" for _ in range(3)) + "," if idade > .3 else ""
    fundo = (f"{manchas}radial-gradient(130% 80% at 30% 15%,rgba(255,255,255,{.55 - .4 * idade:.2f}) 0,rgba(255,255,255,0) 60%),"
             f"linear-gradient(172deg,{papel0} 0%,{papel1} 100%)")
    furos = "" if rasgado else "".join(f'<i class="fu" style="left:{W * c - 5:.0f}px"></i>' for c in GRAMPOS)
    extra = ""
    if f.get("surpresa"):
        extra += lapis(*f["surpresa"], seed=ano)
    if f.get("nota"):
        extra += nota(p)
    corpo = (f'<div class="pp" style="clip-path:{contorno(W, H, ano, rasgado, dobra, fd)};background:{fundo};color:{tinta};'
             f'box-shadow:inset 0 0 {30 + 50 * idade:.0f}px rgba(150,105,30,{.06 + .30 * idade:.2f})">'
             f'{furos}<div class="cb"><b>{ano}</b><span>DEZEMBRO</span></div><div class="fio" style="background:{tinta}"></div>'
             f'<div class="n" style="color:{verm}">25</div><div class="na" style="color:{verm}">NATAL</div>'
             f'<div class="pe"><div class="fio2" style="background:{tinta}"></div><b>{dia}</b>'
             f'<span>{html.escape(p.get("loja", ""))}</span></div>{extra}</div>')
    sombra = ("drop-shadow(0 1px 1px rgba(40,30,15,.22)) drop-shadow(0 6px 8px rgba(40,30,15,.12)) "
              "drop-shadow(-10px 22px 26px rgba(40,30,15,.16))")
    return (f'<div class="fl" data-ano="{ano}" style="left:{f["left"]}px;top:{f["top"]}px;width:{W}px;height:{H}px;'
            f'transform:rotate({f["rot"]}deg);z-index:{2 + i};filter:{sombra}">{corpo}{aba(W, H, dobra, fd, idade)}</div>')


def css(p):
    W, H = p.get("folha_w", 470), p.get("folha_h", 650)
    ruido = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><filter id='f'>"
             "<feTurbulence type='fractalNoise' baseFrequency='.95' numOctaves='3' seed='4'/>"
             "<feColorMatrix values='0 0 0 0 .45 0 0 0 0 .40 0 0 0 0 .30 0 0 0 .55 0'/></filter>"
             "<rect width='100%' height='100%' filter='url(%23f)'/></svg>\")")
    fibra = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='g'>"
             "<feTurbulence type='fractalNoise' baseFrequency='.012 .09' numOctaves='2' seed='8'/>"
             "<feColorMatrix values='0 0 0 0 .5 0 0 0 0 .44 0 0 0 0 .32 0 0 -1.1 0 .62'/></filter>"
             "<rect width='100%' height='100%' filter='url(%23g)'/></svg>\")")
    return mao(p) + f"""
.r{{display:none}}
.k{{top:{p.get('k_top', 712)}px;justify-content:flex-start;gap:0;opacity:.62;z-index:20}}
h1{{z-index:20;right:60px}}
.s{{display:none}}
.dd{{position:absolute;left:72px;right:72px;top:{p.get('sub_top', 1000)}px;z-index:20}}
.dd p{{font-size:{p.get('tam_sub', 27)}px;font-weight:600;line-height:1.3;letter-spacing:-.01em;color:{TI};opacity:.78;white-space:nowrap}}
.dd p b{{font-weight:800;opacity:1}}
.dd .fn{{margin-top:12px;font-size:16px;opacity:.5}}
.fl{{position:absolute;transform-origin:50% 50%}}
.pp{{position:absolute;inset:0;overflow:hidden;font-family:M}}
.pp:before{{content:"";position:absolute;inset:0;mix-blend-mode:multiply;opacity:.55;pointer-events:none;background-image:{ruido}}}
.pp:after{{content:"";position:absolute;inset:0;mix-blend-mode:multiply;opacity:.18;pointer-events:none;background-image:{fibra}}}
.fu{{position:absolute;top:14px;width:9px;height:9px;border-radius:50%;background:#8C8370;box-shadow:inset 0 2px 2px rgba(0,0,0,.45)}}
.cb{{position:absolute;left:30px;right:30px;top:40px;display:flex;justify-content:space-between;align-items:baseline}}
.cb b{{font-weight:900;font-size:36px;letter-spacing:-.01em}}
.cb span{{font-weight:800;font-size:27px;letter-spacing:.16em}}
.fio{{position:absolute;left:30px;right:30px;top:92px;height:3px;opacity:.85}}
.fio:after{{content:"";position:absolute;left:0;right:0;top:6px;height:1px;background:inherit}}
.n{{position:absolute;left:0;right:0;top:{p.get('n_top', 70)}px;text-align:center;font-family:Anton;font-size:{p.get('tam_25', 380)}px;
  line-height:1;letter-spacing:-.01em}}
.na{{position:absolute;left:0;right:0;top:{p.get('na_top', 478)}px;text-align:center;font-weight:900;font-size:42px;letter-spacing:.42em;
  text-indent:.42em}}
.pe{{position:absolute;left:30px;right:30px;bottom:24px;text-align:center}}
.fio2{{height:2px;opacity:.7;margin-bottom:12px}}
.pe b{{display:block;font-weight:800;font-size:25px;letter-spacing:.2em}}
.pe span{{display:block;margin-top:4px;font-family:Mono;font-size:12px;letter-spacing:.14em;text-transform:uppercase;opacity:.6}}
.aba{{position:absolute;inset:0;pointer-events:none}}
.lp{{position:absolute;transform-origin:0 50%;width:170px;height:60px;mix-blend-mode:multiply}}
.lp span{{position:absolute;left:0;top:0;font-family:Hand;font-weight:600;font-size:35px;line-height:1;color:{LAPIS};opacity:.8}}
.lp svg{{position:absolute;left:-10px;top:0}}
.nt{{position:absolute;z-index:3;transform-origin:0 0;font-family:Hand;font-weight:600;line-height:1.02;color:{CANETA};
  mix-blend-mode:multiply;white-space:nowrap}}
.sub-nt{{position:absolute;left:{p.get('sub_nt_x', 160)}px;width:{p.get('sub_nt_w', 140)}px;bottom:-6px;height:14px;overflow:visible}}
"""


def bloco(p):
    W, H = p.get("folha_w", 470), p.get("folha_h", 650)
    folhas = "".join(folha(p, f, i) for i, f in enumerate(p["folhas"]))
    dd = (f'<div class="dd"><p>{R._ed(p.get("subtitulo", "")).replace("<em class=\"it\">", "<b>").replace("</em>", "</b>")}</p>'
          f'<p class="fn mono">{html.escape(p.get("fonte", ""))}</p></div>')
    return f'<div class="leque">{folhas}</div>{dd}'


def build(p):
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_papel(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1)


def checa(pg):
    return pg.evaluate("""() => {const r = e => {const b = e.getBoundingClientRect();
      return [e.className || e.tagName, e.dataset.ano || '', Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]};
      return [...document.querySelectorAll('h1,.k,.dd p,.marca,.handle,.fl,.n,.nt,.lp')].map(r)}""")


def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(600)
            for c in checa(pg): print("  caixa", c)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=82, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
