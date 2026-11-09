"""Post 2026-11-09 08h: celular3d CLARO + 'A folha que entra no celular', tudo em HTML/SVG (sem imagem gerada).
Por cima do celular3d do kit: a folha de caderno do pedreiro (pauta azul, margem vermelha, picote da espiral rasgado,
letra a lápis com leve tremor, digital cinza de cimento, lápis de carpinteiro vermelho atravessado) girada ~-8°,
entre a coluna de texto e o celular, com a ponta direita enfiada por baixo da borda do aparelho (o rabisco entra,
o orçamento sai pelo pop). Dentro da tela, a 1ª bolha vira a FOTO (miniatura da mesma folha) e a 2ª vira o ÁUDIO
(play + forma de onda + duração).

Uso: python3 scripts/arte_caderno.py render.json pasta_saida   (objeto ou lista; gera ID.jpg, ID.png e ID_story.png)

Campos extras do JSON (além dos do celular3d: tag, titulo, subtitulo, contato, conversa, pop_html, pop_rodape, cta,
selo, tam, pop_top, tema):
  conversa: a bolha cujo texto contém "Foto" vira a miniatura da folha (o texto depois de ":" vira a legenda);
            a que contém "Áudio" vira a forma de onda (a duração é o último pedaço do texto, ex. "0:48").
  folha: {"x","y","w","h": caixa da folha antes do giro (px da arte), "rot": giro (padrão -8),
          "titulo": linha de cima (ex. "Tião · laje garagem"), "linhas": itens a lápis, "fs": corpo da letra,
          "pauta": espaço entre as linhas, "topo": y da 1ª linha, "tremor": força do tremor (padrão 2.2),
          "digital": [x, y, giro] da digital de cimento dentro da folha}
  lapis: {"x","y","w","rot"}: lápis de carpinteiro (caixa antes do giro; padrão atravessado na parte de baixo da folha)
  folha_z: z-index da folha (padrão 2 = por baixo do celular, parece entrando na tela; 7 = por cima)
  thumb_w, thumb_h: tamanho da miniatura na bolha da foto (px dentro da tela)
  txt_w, titulo_lh, msgs_top, msgs_gap, bolha_fs, bolha_w, pop_w, pop_right, pop_rot, input_txt: ajustes de layout
  sim_top, sim_right, sim_tam: selo SIMULAÇÃO em pílula (padrão logo acima do pop)
  hora: lista de horários pequenos por bolha (ex. ["21:14", ...]); "" pula
  fonte_mao: lista de .woff2 da letra à mão (padrão Caveat em campanhas/fontes)"""
import json, sys, html, base64, pathlib, importlib.util, math, random
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, CI = R.AZUL, R.TINTA, R.CIANO
GRAFITE = "#2C3038"
PAUTA = "#8FB3E3"
MARGEM = "#E0525A"
LAPIS = "#C8202B"


def mao(p):
    fs = p.get("fonte_mao") or [str(ROOT / "campanhas" / "fontes" / n) for n in
                                ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for f in fs:
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(f).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(pathlib.Path(f).read_bytes()).decode()}){rng}}}")
    return "".join(out)


def folha_cfg(p):
    f = dict(x=40, y=660, w=500, h=520, rot=-8, fs=58, pauta=66, topo=150, tremor=2.2,
             titulo="Tião · laje garagem", linhas=["10 saco cimento", "3 barra de 3/8", "cano 100 6m", "cola pvc"],
             digital=[400, 430, 24])
    f.update(p.get("folha", {}))
    return f


def simbolo_folha(f):
    """<symbol id="folha"> no tamanho w x h: papel com borda rasgada da espiral, pauta, margem, texto, digital."""
    W, H = f["w"], f["h"]
    rnd = random.Random(11)
    # borda de cima: picote rasgado da espiral (dentes irregulares + furinhos)
    top = 34
    pts = [(0, top + 4)]
    x = 0
    while x < W:
        x += rnd.uniform(7, 13)
        pts.append((min(x, W), top + rnd.uniform(-3.5, 4.5)))
    borda = " ".join(f"L{a:.1f} {b:.1f}" for a, b in pts)
    papel = f"M0 {H} {borda} L{W} {H} Z".replace("M0 %d L" % H, "M0 %d L" % H)
    papel = f"M0 {H} L0 {top+4} {borda} L{W} {H} Z"
    furos = ""
    for i, cx in enumerate(range(26, W - 10, 31)):
        # meia-lua rasgada do furo da espiral, mordendo a borda
        r = 6.5 + rnd.uniform(-.6, .8)
        furos += f'<ellipse cx="{cx + rnd.uniform(-1.5,1.5):.1f}" cy="{top+3:.1f}" rx="{r:.1f}" ry="{r*1.25:.1f}" fill="#000"/>'
    linhas_pauta = "".join(
        f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{PAUTA}" stroke-width="1.6" opacity=".75"/>'
        for y in range(f["topo"] - f["pauta"] + 0, H, f["pauta"]) if y > top + 26)
    mx = 78
    margem = (f'<line x1="{mx}" y1="{top}" x2="{mx}" y2="{H}" stroke="{MARGEM}" stroke-width="2" opacity=".8"/>'
              f'<line x1="{mx+5}" y1="{top}" x2="{mx+5}" y2="{H}" stroke="{MARGEM}" stroke-width="1" opacity=".45"/>')
    # texto a lápis: cada linha com giro, deslocamento e tamanho levemente diferentes (mão de obra, não de designer)
    txt = ""
    tit_y = f["topo"] - f["pauta"] - 8
    txt += (f'<text x="{mx+22}" y="{tit_y}" font-size="{f["fs"]*.72:.0f}" transform="rotate(-1.6 {mx+22} {tit_y})" '
            f'fill="{GRAFITE}" opacity=".78">{html.escape(f["titulo"])}</text>'
            f'<path d="M{mx+20} {tit_y+9} q {W*.25:.0f} -5 {W*.48:.0f} -2" stroke="{GRAFITE}" stroke-width="2.2" fill="none" opacity=".55" stroke-linecap="round"/>')
    for i, l in enumerate(f["linhas"]):
        y = f["topo"] + i * f["pauta"] - 10
        x = mx + 24 + rnd.uniform(-6, 10)
        rot = rnd.uniform(-3.2, 1.2)
        fs = f["fs"] * rnd.uniform(.95, 1.05)
        txt += (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs:.1f}" transform="rotate({rot:.2f} {x:.1f} {y:.1f})" '
                f'fill="{GRAFITE}" opacity="{rnd.uniform(.86,.96):.2f}">{html.escape(l)}</text>')
        # risquinho de conferência à esquerda, na margem
        cy = y - fs * .28
        txt += (f'<path d="M{mx-46} {cy:.1f} l 9 9 l 17 -21" stroke="{GRAFITE}" stroke-width="2.6" fill="none" '
                f'stroke-linecap="round" stroke-linejoin="round" opacity=".5"/>' if i < 2 else "")
    dx, dy, drot = f["digital"]
    # digital de cimento: cristas concêntricas + turbulência + mancha
    cristas = "".join(
        f'<ellipse cx="0" cy="{k*1.6:.1f}" rx="{8 + k*5.2:.1f}" ry="{11 + k*6.8:.1f}" fill="none" stroke="#5E5A53" '
        f'stroke-width="3" opacity="{.9 - k*.05:.2f}"/>' for k in range(9))
    digital = (f'<g transform="translate({dx} {dy}) rotate({drot})" filter="url(#cimento)">'
               f'<ellipse cx="0" cy="6" rx="58" ry="74" fill="#7D786F" opacity=".22"/>{cristas}</g>')
    return f"""<symbol id="folha" viewBox="0 0 {W} {H}" overflow="visible">
<defs><clipPath id="clipPapel"><path d="{papel}"/></clipPath>
<mask id="maskFuros"><rect x="-10" y="-10" width="{W+20}" height="{H+20}" fill="#fff"/>{furos}</mask>
<linearGradient id="papelG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFEFA"/><stop offset=".55" stop-color="#FBF9F2"/><stop offset="1" stop-color="#EFEBDF"/></linearGradient></defs>
<g mask="url(#maskFuros)"><path d="{papel}" fill="url(#papelG)"/>
<g clip-path="url(#clipPapel)"><rect width="{W}" height="{H}" filter="url(#fibra)" opacity=".5"/>
{linhas_pauta}{margem}{digital}
<g font-family="Hand" font-weight="600" filter="url(#tremor)">{txt}</g>
<path d="M{W*.62:.0f} {H} Q {W*.7:.0f} {H*.6:.0f} {W} {H*.42:.0f}" stroke="rgba(0,0,0,.035)" stroke-width="40" fill="none"/>
</g></g></symbol>"""


def defs(f):
    return f"""<svg width="0" height="0" style="position:absolute"><defs>
<filter id="tremor" x="-5%" y="-20%" width="110%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="4" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="{f['tremor']}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="1.2" numOctaves="1" seed="9" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.1 1.2" result="ga"/>
<feComposite in="d" in2="ga" operator="in"/></filter>
<filter id="cimento" x="-40%" y="-40%" width="180%" height="180%"><feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="3" seed="2" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="9" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="5" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2 1.25" result="ga"/>
<feComposite in="d" in2="ga" operator="in"/></filter>
<filter id="fibra"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" seed="3"/>
<feColorMatrix type="matrix" values="0 0 0 0 .55  0 0 0 0 .5  0 0 0 0 .42  0 0 0 .18 0"/></filter>
</defs>{simbolo_folha(f)}</svg>"""


def lapis_svg(L):
    w, h = L["w"], 40
    corpo = w - 92
    return f"""<svg width="{w}" height="{h+16}" viewBox="0 -6 {w} {h+16}" style="overflow:visible">
<defs><linearGradient id="lpG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8414A"/><stop offset=".18" stop-color="{LAPIS}"/>
<stop offset=".5" stop-color="#B51A24"/><stop offset=".52" stop-color="#9E141D"/><stop offset="1" stop-color="#7D0F16"/></linearGradient>
<linearGradient id="mdG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1D7A8"/><stop offset=".5" stop-color="#D9B57C"/><stop offset="1" stop-color="#B98E55"/></linearGradient></defs>
<ellipse cx="{w*.48:.0f}" cy="{h+4}" rx="{w*.5:.0f}" ry="8" fill="rgba(40,30,20,.22)" filter="blur(4px)" style="filter:blur(5px)"/>
<rect x="0" y="0" width="{corpo}" height="{h}" rx="3" fill="url(#lpG)"/>
<rect x="0" y="0" width="{corpo}" height="5" rx="2" fill="rgba(255,255,255,.28)"/>
<rect x="0" y="0" width="7" height="{h}" rx="2" fill="#E7CC9C"/><rect x="2" y="{h*.35:.0f}" width="3" height="{h*.3:.0f}" fill="#4A4A4A"/>
<text x="{corpo*.18:.0f}" y="{h*.64:.0f}" font-family="Mono" font-size="13" letter-spacing="3" fill="rgba(255,236,200,.75)">CARPINTEIRO · 2B</text>
<path d="M{corpo} 0 L{corpo+70} {h*.33:.0f} L{corpo+70} {h*.67:.0f} L{corpo} {h} Z" fill="url(#mdG)"/>
<path d="M{corpo} 0 L{corpo+70} {h*.33:.0f} L{corpo+38} {h*.2:.0f} Z" fill="rgba(255,255,255,.25)"/>
<path d="M{corpo+66} {h*.31:.0f} L{w} {h*.43:.0f} L{w} {h*.57:.0f} L{corpo+66} {h*.69:.0f} Z" fill="#3B3B3E"/>
</svg>"""


def thumb(p, legenda):
    f = folha_cfg(p)
    tw, th = p.get("thumb_w", 230), p.get("thumb_h", 150)
    # recorte da foto: a folha girada, "fotografada" de perto em cima de uma bancada
    return (f'<div class="foto"><svg width="{tw}" height="{th}" viewBox="0 0 {tw} {th}">'
            f'<rect width="{tw}" height="{th}" fill="#9C8B73"/><rect width="{tw}" height="{th}" filter="url(#fibra)" opacity=".9"/>'
            f'<g transform="translate({tw*.04:.0f} {-th*.12:.0f}) rotate(-6) scale({tw*1.15/f["w"]:.3f})">'
            f'<use href="#folha" width="{f["w"]}" height="{f["h"]}" style="filter:drop-shadow(0 6px 8px rgba(0,0,0,.35))"/></g>'
            f'<rect width="{tw}" height="{th}" fill="url(#vinheta)"/></svg>'
            f'<span class="leg">{html.escape(legenda)}</span></div>')


def audio(dur):
    rnd = random.Random(5)
    barras = "".join(f'<i style="height:{max(5, int(30*abs(math.sin(k*.55))*rnd.uniform(.45,1)+4))}px"></i>' for k in range(30))
    return (f'<div class="aud"><span class="play"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M7 4.5v15l12-7.5z" fill="{TI}"/></svg></span>'
            f'<span class="onda">{barras}</span><span class="dur">{html.escape(dur)}</span>'
            f'<span class="mic"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round">'
            f'<rect x="9" y="3" width="6" height="11" rx="3" fill="#fff"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg></span></div>')


def css(p):
    f = folha_cfg(p)
    L = dict(x=f["x"] + f["w"] * .10, y=f["y"] + f["h"] - 40, w=430, rot=-24)
    L.update(p.get("lapis", {}))
    top = p.get("pop_top", 760)
    o = [mao(p)]
    if p.get("titulo_lh"): o.append(f".hd{{line-height:{p['titulo_lh']}}}")
    if p.get("txt_w"): o.append(f".txt{{width:{p['txt_w']}px}}")
    if p.get("msgs_top"): o.append(f".msgs{{top:{p['msgs_top']}px!important}}")
    if p.get("msgs_gap"): o.append(f".msgs{{gap:{p['msgs_gap']}px!important}}")
    if p.get("bolha_fs"): o.append(f".b{{font-size:{p['bolha_fs']}px!important}}")
    if p.get("bolha_w"): o.append(f".b{{max-width:{p['bolha_w']}%!important}}")
    if p.get("pop_w"): o.append(f".pop{{width:{p['pop_w']}px!important}}")
    if p.get("pop_right"): o.append(f".pop{{right:{p['pop_right']}px!important}}")
    if "pop_rot" in p: o.append(f".pop{{transform:rotate({p['pop_rot']}deg)!important}}")
    return "\n".join(o) + f"""
.sb{{text-wrap:pretty}}
.pop{{z-index:8!important}}
.sim{{z-index:9!important;top:{p.get('sim_top', top - 58)}px!important;right:{p.get('sim_right', 64)}px!important;font-size:{p.get('sim_tam', 20)}px!important;
  letter-spacing:.18em!important;color:{TI}!important;padding:8px 18px 7px;border:2px solid {AZ};border-radius:40px;background:#fff;
  box-shadow:0 6px 18px rgba(30,45,90,.16)}}
.folha{{position:absolute;left:{f['x']}px;top:{f['y']}px;width:{f['w']}px;height:{f['h']}px;z-index:{p.get('folha_z', 2)};
  transform:rotate({f['rot']}deg);transform-origin:40% 50%;
  filter:drop-shadow(0 1px 1px rgba(40,30,10,.18)) drop-shadow(0 10px 14px rgba(40,30,10,.12)) drop-shadow(0 30px 40px rgba(30,45,90,.16))}}
.folha svg{{width:100%;height:100%;overflow:visible}}
.folha .scan{{position:absolute;top:34px;bottom:0;right:0;width:{p.get('scan_w', 150)}px;pointer-events:none;
  background:repeating-linear-gradient(0deg,rgba(47,107,255,.0) 0 5px,rgba(34,211,238,.32) 5px 7px),
             linear-gradient(90deg,rgba(34,211,238,0),rgba(34,211,238,.34) 65%,rgba(47,107,255,.55));
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 60%)}}
.lapis{{position:absolute;left:{L['x']}px;top:{L['y']}px;width:{L['w']}px;z-index:{p.get('folha_z', 2)};transform:rotate({L['rot']}deg);transform-origin:50% 50%;
  filter:drop-shadow(0 8px 6px rgba(40,30,10,.22))}}
.b{{position:relative}}
.b .h{{display:inline-block;margin-left:10px;font-size:.62em;opacity:.5;vertical-align:-2px}}
.b.d .h{{opacity:.75}}
.b.foto{{padding:8px!important;max-width:none!important}}
.foto svg{{display:block;border-radius:16px}}
.foto .leg{{display:flex;justify-content:space-between;padding:8px 8px 2px;font-size:.82em;color:rgba(11,13,18,.62)}}
.b.audio{{padding:12px 16px!important;max-width:none!important}}
.aud{{display:flex;align-items:center;gap:12px}}
.aud .play{{display:grid;place-items:center;width:30px}}
.aud .onda{{display:flex;align-items:center;gap:3px;height:34px}}
.aud .onda i{{display:block;width:3.5px;border-radius:3px;background:rgba(11,13,18,.45)}}
.aud .onda i:nth-child(-n+9){{background:{AZ}}}
.aud .dur{{font-size:.78em;color:rgba(11,13,18,.55);font-variant-numeric:tabular-nums}}
.aud .mic{{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,{CI},{AZ})}}
"""


def build(p):
    conv = []
    especiais = {}
    for i, (q, t) in enumerate(p.get("conversa", [])):
        if i < len(p["conversa"]) - 1 and ("Foto" in t or "Áudio" in t):
            tok = f"@@ESP{i}@@"
            if "Foto" in t:
                leg = t.split(":", 1)[1].strip() if ":" in t else "Foto"
                especiais[tok] = ("foto", thumb(p, leg))
            else:
                especiais[tok] = ("audio", audio(t.split()[-1]))
            conv.append([q, tok])
        else:
            conv.append([q, t.replace("|", " ")])
    pp = dict(p, conversa=conv)
    h = R.build(pp)
    horas = p.get("hora", [])
    # bolhas especiais + horário pequeno
    for i, (q, t) in enumerate(conv[:-1]):
        lado = "e" if q == "cliente" else "d"
        hr = horas[i] if i < len(horas) else ""
        hs = f'<span class="h">{html.escape(hr)}</span>' if hr else ""
        if t in especiais:
            kind, inner = especiais[t]
            if kind == "foto":
                inner = inner.replace('</span></div>', f'{hs}</span></div>', 1)
                h = h.replace(f'<div class="b {lado}">{t}</div>', f'<div class="b {lado} foto">{inner}</div>', 1)
            else:
                h = h.replace(f'<div class="b {lado}">{t}</div>', f'<div class="b {lado} audio">{inner}</div>', 1)
        elif hs:
            esc = html.escape(t)
            h = h.replace(f'<div class="b {lado}">{esc}</div>', f'<div class="b {lado}">{esc}{hs}</div>', 1)
    h = h.replace("</style>", css(p) + "</style>", 1)
    if p.get("status_contato"):
        h = h.replace("<small>● online agora</small>", f'<small>{html.escape(p["status_contato"])}</small>', 1)
    if "input_txt" in p:
        h = h.replace('<div class="input">Mensagem…</div>', f'<div class="input">{html.escape(p["input_txt"])}</div>', 1)
    f = folha_cfg(p)
    L = dict(w=430); L.update(p.get("lapis", {}))
    vinheta = ('<svg width="0" height="0" style="position:absolute"><defs><radialGradient id="vinheta" cx=".5" cy=".45" r=".75">'
               '<stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></radialGradient></defs></svg>')
    camada = (defs(f) + vinheta +
              f'<div class="folha"><svg viewBox="0 0 {f["w"]} {f["h"]}"><use href="#folha" width="{f["w"]}" height="{f["h"]}"/></svg><i class="scan"></i></div>'
              f'<div class="lapis">{lapis_svg(L)}</div>')
    h = h.replace('<div class="cena">', camada + '<div class="cena">', 1)
    js = """<script>document.fonts.ready.then(()=>{window.__boxes=['.txt','.tag','.hd','.sb','.cena','.tela','.msgs','.pop','.sim','.base','.lg','.folha','.lapis','.input']
.map(q=>{const e=document.querySelector(q); if(!e) return q+' -'; const r=e.getBoundingClientRect(); return q+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(',');});
document.querySelectorAll('.msgs .b').forEach((b,i)=>{const r=b.getBoundingClientRect(); window.__boxes.push('b'+i+' '+[r.left,r.top,r.right,r.bottom].map(Math.round).join(','));});
const hd=document.querySelector('.hd'); window.__boxes.push('hd scrollW '+hd.scrollWidth+' clientW '+hd.clientWidth);});</script>"""
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
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(700)
            for l in pg.evaluate("window.__boxes||[]"): print("  ", l)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
