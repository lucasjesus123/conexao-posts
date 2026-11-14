"""Post 2026-11-14 16h: nota clara + 'A ficha da primeira reunião' — cartão branco do modelo nota (símbolo da Conexão no
lugar do avatar) com uma ficha A5 de bloco pautado presa na borda de baixo por um prendedor binder clip preto (alças de
arame metálicas dobradas sobre a ficha). Na ficha: pergunta impressa, resposta a lápis cinza riscada à mão em caneta
vermelha e, embaixo, em vermelho torto, a anotação do Lucas. A ficha gira levemente e sangra pela borda de baixo,
sem tocar o rodapé: logo e @ ficam empilhados à esquerda, sobre o fundo.
Tudo em HTML/CSS/SVG sobre o modelo nota de kit/render.py (sem imagem gerada).
Uso: python3 scripts/arte_ficha.py post_render.json pasta_saida
Campos extras do JSON (além dos do modelo nota: texto, rodape, nome, avatar, tam, tema):
  marca_bottom, handle_bottom: distância do pé da logo e do @ (empilhados à esquerda)
  card_top: topo do cartão (px; o modelo centraliza, aqui o cartão sobe para a metade de cima)
  avatar_fundo: cor do círculo atrás do símbolo; avatar_pad: respiro do símbolo dentro do círculo (px)
  ficha: {"cabecalho": texto mono do topo, "selo": selo discreto (ex.: "EXEMPLO"),
          "pergunta": pergunta impressa (1ª), "resposta": resposta a lápis (será riscada),
          "nota": anotação em vermelho, "proxima": começo da 2ª pergunta (opcional; vazio = só pautas em branco),
          "left", "top", "w", "h": caixa da ficha antes de girar (px), "rot": rotação (graus),
          "passo": distância entre as linhas pautadas (px), "fs_perg", "fs_lapis", "fs_nota": tamanhos,
          "nota_dx": recuo da anotação, "nota_rot": giro da anotação, "clip_x": centro do prendedor na ficha (px)}
  fonte_mao: lista de caminhos .woff2 da Caveat"""
import json, sys, html, base64, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PA = R.AZUL, R.TINTA, R.PAPEL
FOLHA = "#FCFBF7"
IMPRESSO = "#22252C"
LAPIS = "#53565D"
VERMELHO = "#D62F2F"
PAUTA = "rgba(47,107,255,.20)"


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


def geo(p):
    e = p["ficha"]
    return e.get("left", 300), e.get("top", 600), e.get("w", 690), e.get("h", 820), e.get("rot", 3)


def css(p):
    L, T, W, H, rot = geo(p); e = p["ficha"]
    passo = e.get("passo", 64); topo_pauta = e.get("topo_pauta", 214)
    return mao(p) + f"""
.card{{top:{p.get('card_top', 92)}px;transform:none;z-index:4}}
.h img{{background:{p.get('avatar_fundo', '#0E1220')};object-fit:contain;padding:{p.get('avatar_pad', 19)}px;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.06)}}
.tx{{text-wrap:balance}}
.marca{{z-index:6;bottom:{p.get('marca_bottom', 98)}px}}
.handle{{z-index:6;left:72px;right:auto;bottom:{p.get('handle_bottom', 62)}px;font-size:17px}}
.fc{{position:absolute;left:{L}px;top:{T}px;width:{W}px;height:{H}px;z-index:3;transform:rotate({rot}deg);transform-origin:50% 0;
  filter:drop-shadow(0 1px 1px rgba(30,25,15,.16)) drop-shadow(0 10px 12px rgba(30,25,15,.10)) drop-shadow(-12px 30px 36px rgba(30,25,15,.16))}}
.pp{{position:absolute;inset:0;overflow:hidden;color:{IMPRESSO};
  background:
    repeating-linear-gradient(180deg,transparent 0,transparent {passo-2}px,{PAUTA} {passo-2}px,{PAUTA} {passo}px) 0 {topo_pauta}px/100% calc(100% - {topo_pauta}px) no-repeat,
    radial-gradient(120% 60% at 20% 0,#FFFFFF 0,rgba(255,255,255,0) 60%),
    linear-gradient(178deg,{FOLHA} 0%,#F5F3EC 100%)}}
.pp:before{{content:"";position:absolute;inset:0;opacity:.4;mix-blend-mode:multiply;pointer-events:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='f'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' seed='5'/><feColorMatrix values='0 0 0 0 .55 0 0 0 0 .52 0 0 0 0 .46 0 0 0 .30 0'/></filter><rect width='100%' height='100%' filter='url(%23f)'/></svg>")}}
.pp:after{{content:"";position:absolute;left:0;right:0;top:0;height:40px;pointer-events:none;
  background:linear-gradient(180deg,rgba(90,80,60,.10),rgba(90,80,60,0))}}
.cab{{position:absolute;left:52px;right:52px;top:{e.get('cab_top', 118)}px;display:flex;justify-content:space-between;align-items:center;
  font-family:Mono;font-weight:500;font-size:18px;letter-spacing:.2em;white-space:nowrap;padding-bottom:14px;border-bottom:2px solid {IMPRESSO}}}
.selo{{font-size:14px;font-weight:700;letter-spacing:.2em;padding:6px 10px 5px;border:2px solid rgba(34,37,44,.75);border-radius:4px;color:rgba(34,37,44,.85)}}
.pg{{position:absolute;left:52px;right:52px;font-weight:700;font-size:{e.get('fs_perg', 33)}px;line-height:1.24;letter-spacing:-.01em;text-wrap:balance}}
.pg b{{font-family:Mono;font-weight:600;margin-right:12px;letter-spacing:0}}
.hd{{position:absolute;font-family:Hand;font-weight:600;line-height:1;white-space:nowrap}}
.lp{{color:{LAPIS};font-size:{e.get('fs_lapis', 52)}px;opacity:.95}}
.lp span{{position:relative;display:inline-block}}
.lp svg{{position:absolute;left:-14px;top:0;width:calc(100% + 28px);height:100%;overflow:visible}}
.nt{{color:{VERMELHO};font-size:{e.get('fs_nota', 60)}px;transform:rotate({e.get('nota_rot', -4)}deg);transform-origin:0 70%}}
.prox{{position:absolute;left:52px;font-weight:700;font-size:{e.get('fs_perg', 33)}px;white-space:nowrap}}
.prox b{{font-family:Mono;font-weight:600;margin-right:12px}}
.clip{{position:absolute;z-index:5;pointer-events:none;overflow:visible}}
"""


def risco():
    """risco de caneta vermelha à mão: duas passadas quase horizontais, a segunda voltando um pouco torta"""
    return (f'<svg viewBox="0 0 400 100" preserveAspectRatio="none">'
            f'<path d="M2 60 C 90 55, 200 59, 300 52 S 380 47, 398 49" fill="none" stroke="{VERMELHO}" stroke-width="3.6" '
            f'stroke-linecap="round" vector-effect="non-scaling-stroke" opacity=".95"/>'
            f'<path d="M392 55 C 300 61, 190 54, 90 63 S 20 67, 10 66" fill="none" stroke="{VERMELHO}" stroke-width="2.4" '
            f'stroke-linecap="round" vector-effect="non-scaling-stroke" opacity=".7"/></svg>')


def prendedor(cx, cy, rot, larg=176):
    """binder clip preto visto de frente, com a alça da frente dobrada para baixo (arame com brilho metálico).
    (cx, cy) = centro da lombada na arte; o corpo desce a partir daí."""
    w = larg; h = 220
    x0 = -w / 2
    # corpo: lombada arredondada (faixa de brilho) + face preta levemente trapezoidal
    corpo = f"M {x0+6} 10 Q {x0} 10 {x0} 18 L {x0+8} 74 Q {x0+9} 80 {x0+16} 80 L {-x0-16} 80 Q {-x0-9} 80 {-x0-8} 74 L {-x0} 18 Q {-x0} 10 {-x0-6} 10 Z"
    # alça de arame: pernas saem das pontas do corpo e se fecham num laço mais estreito embaixo
    ax = -x0 - 14; bx = 30
    alca = (f"M {-ax} 74 C {-ax+2} 110, {-bx-8} 160, {-bx} 180 Q {-bx+2} 190 {-bx+14} 190 L {bx-14} 190 Q {bx-2} 190 {bx} 180 "
            f"C {bx+8} 160, {ax-2} 110, {ax} 74")
    alca_tras = alca.replace("180", "186").replace("190", "180")
    return f"""<svg class="clip" style="left:{cx - w/2 - 20}px;top:{cy - 20}px;transform:rotate({rot}deg);transform-origin:{w/2+20}px 20px"
 width="{w+40}" height="{h+40}" viewBox="{x0-20} -20 {w+40} {h+40}">
<defs>
 <linearGradient id="cf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A5E68"/><stop offset=".10" stop-color="#2A2C32"/>
  <stop offset=".22" stop-color="#121317"/><stop offset=".75" stop-color="#0A0B0D"/><stop offset="1" stop-color="#1B1C21"/></linearGradient>
 <linearGradient id="cs" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".28" stop-color="#fff" stop-opacity=".16"/>
  <stop offset=".36" stop-color="#fff" stop-opacity="0"/><stop offset=".78" stop-color="#fff" stop-opacity="0"/><stop offset=".86" stop-color="#fff" stop-opacity=".07"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <linearGradient id="ar" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6F8"/><stop offset=".3" stop-color="#A9AFB8"/>
  <stop offset=".55" stop-color="#E9ECEF"/><stop offset=".8" stop-color="#7E848D"/><stop offset="1" stop-color="#C9CDD3"/></linearGradient>
 <filter id="sb" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="-3" dy="7" stdDeviation="5" flood-color="#1E1910" flood-opacity=".32"/></filter>
 <filter id="sa" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="-2" dy="5" stdDeviation="2.6" flood-color="#1E1910" flood-opacity=".30"/></filter>
</defs>
<g filter="url(#sa)" opacity=".55"><path d="{alca_tras}" fill="none" stroke="#6F757E" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>
<g filter="url(#sb)"><path d="{corpo}" fill="url(#cf)"/></g>
<path d="{corpo}" fill="url(#cs)"/>
<path d="M {x0+6} 12.5 L {-x0-6} 12.5" stroke="#9AA0AA" stroke-width="2" stroke-linecap="round" opacity=".7"/>
<path d="M {x0+10} 76.5 L {-x0-10} 76.5" stroke="#3A3D45" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="{-ax}" cy="73" r="8" fill="#0C0D10" stroke="#3B3E46" stroke-width="1.5"/><circle cx="{ax}" cy="73" r="8" fill="#0C0D10" stroke="#3B3E46" stroke-width="1.5"/>
<g filter="url(#sa)">
 <path d="{alca}" fill="none" stroke="#5E646D" stroke-width="8.5" stroke-linecap="round" stroke-linejoin="round"/>
 <path d="{alca}" fill="none" stroke="url(#ar)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
 <path d="{alca}" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity=".75" transform="translate(-1.2,-1.2)"/>
</g>
</svg>"""


def ficha(p):
    e = p["ficha"]; L, T, W, H, rot = geo(p)
    passo = e.get("passo", 64); tp = e.get("topo_pauta", 214)
    linha = lambda n: tp + n * passo   # y (local) da linha pautada n
    pg_top = e.get("pg_top", 190)
    n_resp = e.get("linha_resp", 3)    # linha onde a resposta a lápis se apoia
    n_nota = n_resp + 1
    fl, fn = e.get("fs_lapis", 52), e.get("fs_nota", 60)
    perg = html.escape(e["pergunta"])
    num, _, resto = perg.partition(" ")
    prox = html.escape(e.get("proxima", ""))
    pn, _, pr = prox.partition(" ")
    corpo = (f'<div class="pp">'
             f'<div class="cab"><span>{html.escape(e.get("cabecalho", "FICHA · 1ª REUNIÃO"))}</span>'
             f'<span class="selo">{html.escape(e.get("selo", "EXEMPLO"))}</span></div>'
             f'<div class="pg" style="top:{pg_top}px"><b>{num}</b>{resto}</div>'
             f'<div class="hd lp" style="left:{e.get("lapis_dx", 62)}px;top:{linha(n_resp) - fl*0.80:.0f}px"><span>{html.escape(e["resposta"])}{risco()}</span></div>'
             f'<div class="hd nt" style="left:{e.get("nota_dx", 150)}px;top:{linha(n_nota) - fn*0.80 + e.get("nota_dy", 0):.0f}px">{html.escape(e["nota"])}</div>' +
             (f'<div class="prox" style="top:{e.get("prox_top", H - 40)}px"><b>{pn}</b>{pr}</div>' if prox else '') +
             f'</div>')
    return f'<div class="fc">{corpo}</div>'


def prendedor_na_arte(p):
    import math
    e = p["ficha"]; L, T, W, H, rot = geo(p)
    lx = e.get("clip_x", W / 2); ly = e.get("clip_y", -34)
    a = math.radians(rot)
    # a ficha gira em torno do meio da borda de cima
    ox, oy = L + W / 2, T
    dx, dy = lx - W / 2, ly
    return prendedor(ox + dx * math.cos(a) - dy * math.sin(a), oy + dx * math.sin(a) + dy * math.cos(a), rot + e.get("clip_rot", -1.5),
                     e.get("clip_w", 176))


def build(p):
    p = dict(p); p.setdefault("nome", "Grupo Conexão")
    h = '<!doctype html><html><head><meta charset="utf-8"><style>' + R.m_nota(p, None) + "</body></html>"
    h = h.replace("</style>", css(p) + "</style>", 1)
    return h.replace('<img class="marca"', ficha(p) + prendedor_na_arte(p) + '<img class="marca"', 1)


def checa(pg):
    return pg.evaluate("""() => {const r = s => [...document.querySelectorAll(s)].map(e => {const b = e.getBoundingClientRect();
      return [s, Math.round(b.left), Math.round(b.top), Math.round(b.right), Math.round(b.bottom)]});
      return ['.card','.tx','.d','.marca','.handle','.fc','.pg','.lp','.nt','.prox','.clip'].flatMap(r)}""")


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
            Image.open(out / f"{p['id']}_story.png").convert("RGB").save(out / f"{p['id']}_story.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
