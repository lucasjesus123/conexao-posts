"""Post 2026-11-17 08h: papel claro + 'O HD desplugado' — HD externo preto fosco (recorte de campanhas/assets/hd_externo.png)
grande na metade de cima, com sombra de contato no papel; na face de cima, uma tira de fita crepe com escrita à mão em
caneta preta ("BACKUP – NÃO MEXER" / "mar/2023", a data sublinhada a lápis), deitada na perspectiva do HD. O cabo desce
em S até a ponta USB solta, desconectada; ao lado dela, a lápis, "alguém já testou?" com uma seta à mão. O olho entra
pela etiqueta, desce pelo cabo até a ponta solta e cai no título.
Tudo em HTML/CSS/SVG sobre o modelo papel de kit/render.py (a única imagem é o recorte do HD).
Uso: python3 scripts/arte_hd.py posts/2026-11-17-08h/render.json out
Campos extras do JSON (além dos do modelo papel: kicker, num, titulo, tam, topo, subtitulo):
  k_top: topo do kicker (px; desce para logo acima do título)
  fonte: linha mono da fonte do dado (abaixo do subtítulo; "|" quebra a linha); tam_sub, sub_top
  hd: {"img": caminho do recorte PNG, "left", "top": posição do canto do recorte (px), "w": largura (px),
       "rot": giro (graus, em torno do canto de cima à esquerda)}
  fita: {"cx", "cy": centro da fita em px NATURAIS do recorte, "w", "h": tamanho da fita (px naturais),
         "u": [x, y] direção do texto na face do HD, "v": [x, y] direção 'para baixo' na face (perspectiva),
         "rot": giro extra da fita no plano da face (graus), "linhas": [texto caneta, data], "tam": tamanho da letra,
         "tam_data": tamanho da data}
  nota: {"texto", "left", "top", "rot", "tam", "seta": path SVG (coordenadas da caixa da nota), "seta_box": [x, y, w, h]}
  fonte_mao: lista de caminhos .woff2 da Caveat"""
import json, sys, html, base64, pathlib, importlib.util, random
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PA = R.AZUL, R.TINTA, R.PAPEL
CANETA = "#16171A"     # caneta preta (marcador fino)
LAPIS = "#5E5E5C"      # grafite


def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        f = pathlib.Path(f)
        if not f.is_absolute():
            f = ROOT / f
        rng = ";unicode-range:U+0100-024F" if "ext" in f.name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(f.read_bytes()).decode()}){rng}}}")
    return "".join(out)


def serrilha(W, H, seed):
    """clip-path da fita crepe: lados compridos retos, pontas rasgadas em zigue-zague irregular"""
    rnd = random.Random(seed)
    y = 0.0                                          # ponta esquerda, de baixo para cima
    esq = []
    while y < H:
        esq.append((rnd.uniform(0, 7), y)); y += rnd.uniform(3, 7)
    esq.append((rnd.uniform(0, 5), H))
    y = 0.0; dir_ = []
    while y < H:
        dir_.append((W - rnd.uniform(0, 7), y)); y += rnd.uniform(3, 7)
    dir_.append((W - rnd.uniform(0, 5), H))
    pts = dir_ + list(reversed(esq))
    return "polygon(" + ",".join(f"{a:.1f}px {b:.1f}px" for a, b in pts) + ")"


def fita(p):
    f = p["fita"]
    W, H = f.get("w", 300), f.get("h", 118)
    ux, uy = f.get("u", [1, 0]); vx, vy = f.get("v", [0, 1])
    l1, l2 = (f.get("linhas") or ["", ""]) + [""] * (2 - len(f.get("linhas") or []))
    sub = (f'<svg class="sb" viewBox="0 0 120 12" preserveAspectRatio="none"><path d="M2 7 C 30 3, 70 10, 118 5" '
           f'fill="none" stroke="{LAPIS}" stroke-width="2.4" stroke-linecap="round" opacity=".9" '
           f'vector-effect="non-scaling-stroke"/><path d="M8 9 C 40 7, 80 11, 112 8" fill="none" stroke="{LAPIS}" '
           f'stroke-width="1.4" stroke-linecap="round" opacity=".55" vector-effect="non-scaling-stroke"/></svg>')
    return (f'<div class="ft" style="left:{f["cx"] - W / 2}px;top:{f["cy"] - H / 2}px;width:{W}px;height:{H}px;'
            f'transform:matrix({ux},{uy},{vx},{vy},0,0) rotate({f.get("rot", 0)}deg)">'
            f'<div class="fs" style="clip-path:{serrilha(W, H, 7)}"></div>'
            f'<div class="fc" style="clip-path:{serrilha(W, H, 7)}"></div>'
            f'<div class="tx"><b style="font-size:{f.get("tam", 38)}px">{html.escape(l1)}</b>'
            f'<span style="font-size:{f.get("tam_data", 34)}px">{html.escape(l2)}{sub}</span></div></div>')


def nota(p):
    n = p["nota"]
    bx, by, bw, bh = n.get("seta_box", [0, 0, 200, 120])
    seta = n.get("seta", "")
    return (f'<div class="nt" style="left:{n["left"]}px;top:{n["top"]}px;transform:rotate({n.get("rot", 0)}deg)">'
            f'<span style="font-size:{n.get("tam", 40)}px">{html.escape(n["texto"])}</span>'
            f'<svg style="left:{bx}px;top:{by}px" width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}">'
            f'<path d="{seta}" fill="none" stroke="{LAPIS}" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity=".88"/></svg></div>')


def css(p):
    hd = p["hd"]; s = hd["w"] / 763
    ruido = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='f'>"
             "<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' seed='3'/>"
             "<feColorMatrix values='0 0 0 0 .55 0 0 0 0 .45 0 0 0 0 .28 0 0 0 .7 0'/></filter>"
             "<rect width='100%' height='100%' filter='url(%23f)'/></svg>\")")
    fibra = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='120'><filter id='g'>"
             "<feTurbulence type='fractalNoise' baseFrequency='.006 .18' numOctaves='2' seed='9'/>"
             "<feColorMatrix values='0 0 0 0 .5 0 0 0 0 .42 0 0 0 0 .26 0 0 -1.2 0 .7'/></filter>"
             "<rect width='100%' height='100%' filter='url(%23g)'/></svg>\")")
    return mao(p) + f"""
.r{{display:none}}
.k{{top:{p.get('k_top', 760)}px;justify-content:flex-start;gap:0;opacity:.62;z-index:20}}
h1{{z-index:20;right:{p.get("h1_right", 60)}px}}
.s{{display:none}}
.dd{{position:absolute;left:72px;right:72px;top:{p.get('sub_top', 1110)}px;z-index:20}}
.dd p{{font-size:{p.get('tam_sub', 28)}px;font-weight:600;line-height:1.3;letter-spacing:-.01em;color:{TI};opacity:.78}}
.dd .fn{{margin-top:16px;font-size:{p.get('tam_fn', 15)}px;line-height:1.55;letter-spacing:.08em;opacity:{p.get('op_fn', .5)}}}
.hd{{position:absolute;left:0;top:0;width:763px;height:1024px;transform-origin:0 0;
  transform:translate({hd['left']}px,{hd['top']}px) rotate({hd.get('rot', 0)}deg) scale({s:.4f});z-index:5}}
.hd img{{position:absolute;left:0;top:0;width:763px;height:1024px;
  filter:drop-shadow(0 2px 1.5px rgba(30,24,14,.55)) drop-shadow(4px 10px 8px rgba(30,24,14,.22)) drop-shadow(16px 34px 34px rgba(30,24,14,.20))}}
.ft{{position:absolute;transform-origin:50% 50%;z-index:2}}
.ft .fs{{position:absolute;inset:0 -4px;transform:translate(3px,6px);background:rgba(0,0,0,.55);filter:blur(5px)}}
.ft .fc{{position:absolute;inset:0;
  background:{ruido},{fibra},linear-gradient(100deg,rgba(255,255,255,.18) 0,rgba(255,255,255,0) 18%,rgba(255,255,255,0) 82%,rgba(255,255,255,.16) 100%),
    linear-gradient(180deg,rgba(232,214,168,.95) 0,rgba(222,202,152,.93) 100%);
  background-blend-mode:multiply,soft-light,normal,normal;
  box-shadow:inset 0 0 14px rgba(150,115,50,.30)}}
.ft .fc:after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,250,235,.30) 0,rgba(255,250,235,0) 7%,rgba(0,0,0,.06) 9%,rgba(0,0,0,0) 14%,rgba(0,0,0,0) 86%,rgba(0,0,0,.06) 91%,rgba(255,250,235,0) 93%,rgba(255,250,235,.28) 100%)}}
.ft .tx{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
  font-family:Hand;font-weight:600;color:{CANETA};line-height:1;mix-blend-mode:multiply;white-space:nowrap}}
.ft .tx b{{font-weight:600;letter-spacing:.01em;transform:rotate(-1.2deg)}}
.ft .tx span{{position:relative;margin-top:6px;transform:rotate(1deg) translateX(8px)}}
.ft .sb{{position:absolute;left:-4px;right:-6px;bottom:-6px;height:12px;width:calc(100% + 10px);overflow:visible}}
.nt{{position:absolute;z-index:8;transform-origin:0 0;mix-blend-mode:multiply}}
.nt span{{font-family:Hand;font-weight:600;line-height:1;color:{LAPIS};white-space:nowrap;opacity:.95}}
.nt svg{{position:absolute;overflow:visible}}
"""


def bloco(p):
    hd = p["hd"]
    img = R.b64(hd["img"], "image/png")
    linhas = str(p.get("fonte", "")).split("|")
    dd = (f'<div class="dd"><p>{R._ed(p.get("subtitulo", "")).replace("<em class=\"it\">", "<b>").replace("</em>", "</b>")}</p>'
          f'<p class="fn mono">{"<br>".join(html.escape(l) for l in linhas)}</p></div>')
    return f'<div class="hd"><img src="{img}">{fita(p)}</div>{nota(p)}{dd}'


def build(p):
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_papel(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    return h.replace('<img class="marca"', bloco(p) + '<img class="marca"', 1)


def checa(pg):
    return pg.evaluate("""() => {const r = e => {const b = e.getBoundingClientRect();
      return [e.className || e.tagName, Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]};
      return [...document.querySelectorAll('h1,.k,.dd p,.marca,.handle,.hd,.ft,.nt')].map(r)}""")


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
