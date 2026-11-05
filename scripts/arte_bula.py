"""Post 2026-11-05 08h: 'Tarja vermelha: só com conferência humana' — a arte é a face de uma caixa de remédio
(papel cartão branco-gelo, vinco de lombada à direita, tarja vermelha sangrando de ponta a ponta, texto de embalagem,
código de barras e lote circulado à caneta), tudo em HTML/CSS/SVG sobre kit/render.py.
Uso: python3 scripts/arte_bula.py post_render.json pasta_saida
Campos do JSON:
  kicker (mono, topo direito), produto (nome do 'remédio'), dosagem (mono), apoio ({itálico azul}, | quebra),
  tarja (texto branco da tarja vermelha),
  indicado: {"titulo", "itens": [...]}, posologia: {"titulo", "itens": [...]} (numerados),
  advertencia: {"titulo", "itens": [...], "reacao": [rótulo, texto]},
  lote: [rótulo, valor circulado à caneta], validade: [rótulo, valor],
  estudo: {"num", "texto", "fonte"}, aviso (letra miúda na lombada),
  tam_produto, tam_tarja (opcionais)."""
import json, sys, html, base64, pathlib, importlib.util, random
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
FON = ROOT / "campanhas" / "fontes"
def ff(n): return base64.b64encode((FON / n).read_bytes()).decode()
HAND = (f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{ff('caveat-latin-600-normal.woff2')})}}"
        f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{ff('caveat-latin-ext-600-normal.woff2')});unicode-range:U+0100-024F}}")
AZ, TI = R.AZUL, R.TINTA
TARJA = "#D93A35"
CARTAO = "#F8F7F3"      # papel cartão branco-gelo
CANETA = "#1F4FD8"
DOBRA = 1004            # x do vinco da lombada
M = 72                  # margem esquerda

def css(p):
    return HAND + f"""
body{{background:{CARTAO}}}
.face{{position:absolute;inset:0;background:
  radial-gradient(120% 90% at 30% 25%,rgba(255,255,255,.9) 0,rgba(255,255,255,0) 60%),
  linear-gradient(180deg,#FBFAF7 0,{CARTAO} 55%,#F1EFE9 100%)}}
.fibra{{position:absolute;inset:0;pointer-events:none;opacity:.09;mix-blend-mode:multiply;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.012 .5' numOctaves='3' seed='4'/><feColorMatrix values='0 0 0 0 .45 0 0 0 0 .42 0 0 0 0 .36 0 0 0 .9 0'/></filter><rect width='100%' height='100%' filter='url(%23f)'/></svg>")}}
.grao{{opacity:.075;z-index:30}}
.z{{position:relative;z-index:5}}
.k{{position:absolute;right:{1080-DOBRA+40}px;top:66px;font-size:19px;padding:9px 14px 8px 16px;border:1.5px solid rgba(11,13,18,.55);border-radius:4px;opacity:.75;z-index:5}}
.reg{{position:absolute;left:{M}px;top:76px;font-size:19px;opacity:.55;z-index:5}}
.prod{{position:absolute;left:{M-6}px;top:98px;font-weight:900;font-size:{p.get('tam_produto',118)}px;line-height:1;letter-spacing:-.05em;z-index:5}}
.prod sup{{font-size:.26em;font-weight:800;vertical-align:top;position:relative;top:.32em;margin-left:6px;letter-spacing:0;opacity:.8}}
.dose{{position:absolute;left:{M}px;top:{p.get('dose_top',238)}px;font-family:Mono;font-size:29px;letter-spacing:.02em;opacity:.8;z-index:5}}
.dose b{{font-weight:500;color:{AZ}}}
.apoio{{position:absolute;left:{M}px;top:{p.get('apoio_top',300)}px;font-weight:600;font-size:{p.get('tam_apoio',43)}px;line-height:1.14;letter-spacing:-.025em;z-index:5}}
.apoio .it{{color:{AZ};font-size:1.1em;letter-spacing:-.01em}}
.tarja{{position:absolute;left:-10px;right:-10px;top:{p.get('tarja_top',446)}px;height:146px;background:{TARJA};z-index:4;
  display:flex;align-items:center;padding-left:{M+10}px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.18), inset 0 -2px 0 rgba(0,0,0,.08)}}
.tarja:after{{content:"";position:absolute;inset:0;opacity:.18;mix-blend-mode:multiply;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.tarja span{{position:relative;color:#fff;font-weight:800;font-size:{p.get('tam_tarja',46)}px;letter-spacing:.01em;text-transform:uppercase;white-space:nowrap;line-height:1}}
.tarja small{{display:block;font-family:Mono;font-weight:500;font-size:19px;letter-spacing:.16em;margin-top:14px;opacity:.85}}
.cols{{position:absolute;left:{M}px;right:{1080-DOBRA+40}px;top:{p.get('cols_top',630)}px;display:grid;grid-template-columns:1fr 1fr;column-gap:48px;z-index:5}}
.sec h3{{font-family:Mono;font-weight:500;font-size:24px;letter-spacing:.14em;text-transform:uppercase;padding-bottom:11px;margin-bottom:12px;border-bottom:2px solid {TI}}}
.sec li{{list-style:none;font-size:29px;font-weight:600;line-height:1.36;letter-spacing:-.015em;white-space:nowrap}}
.ind li:before{{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:{TI};opacity:.4;margin:0 14px 5px 2px;vertical-align:middle}}
.pos ol{{counter-reset:n}}
.pos li{{counter-increment:n}}
.pos li:before{{content:counter(n);display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;
  border:2px solid {AZ};color:{AZ};font-family:Mono;font-size:17px;font-weight:500;margin:0 13px 0 0;vertical-align:4px;letter-spacing:0}}
.adv{{position:absolute;left:{M}px;right:{1080-DOBRA+40}px;top:{p.get('adv_top',868)}px;z-index:5}}
.adv h3{{color:{TARJA};border-color:{TARJA};display:flex;align-items:center;gap:12px}}
.adv h3 i{{display:inline-flex;width:28px;height:28px;border-radius:50%;background:{TARJA};color:#fff;font-style:normal;font-family:M;font-weight:900;font-size:19px;align-items:center;justify-content:center;letter-spacing:0}}
.adv ul{{display:grid;grid-template-columns:1fr 1fr;column-gap:48px}}
.adv li:before{{content:"";display:inline-block;width:14px;height:3px;background:{TARJA};margin:0 14px 7px 2px;vertical-align:middle}}
.reac{{margin-top:14px;padding:12px 16px 13px 20px;background:linear-gradient(90deg,rgba(217,58,53,.10),rgba(217,58,53,.03));border-left:5px solid {TARJA};font-size:28px;line-height:1.25;font-weight:600;letter-spacing:-.012em;white-space:nowrap}}
.reac b{{display:block;font-family:Mono;font-weight:500;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:{TARJA};margin-bottom:5px}}
.pe{{position:absolute;left:{M}px;right:{1080-DOBRA+40}px;top:{p.get('pe_top',1118)}px;display:flex;gap:30px;align-items:flex-start;z-index:5}}
.cb{{flex:none}}
.cb small{{display:block;font-family:Mono;font-size:15px;letter-spacing:.32em;margin-top:4px;opacity:.75}}
.lote{{font-family:Mono;font-size:23px;line-height:2.0;letter-spacing:.03em;padding-top:0;flex:none;color:#2A2E38}}
.lote .c{{position:relative;display:inline-block;margin-left:34px;color:{CANETA};font-weight:500}}
.lote .c svg{{position:absolute;left:-37px;top:50%;overflow:visible;transform:translateY(-50%) rotate(-3deg)}}
.est{{position:absolute;right:{1080-DOBRA+40}px;top:{p.get('est_top',288)}px;width:{p.get('est_w',372)}px;z-index:5;border:1.5px solid rgba(11,13,18,.45);border-radius:8px;padding:14px 16px 9px 16px;background:rgba(255,255,255,.4)}}
.est .lab{{position:absolute;top:-11px;left:12px;background:{CARTAO};padding:0 7px;font-family:Mono;font-size:16px;letter-spacing:.2em;opacity:.8}}
.est p{{display:grid;grid-template-columns:auto 1fr;column-gap:12px;align-items:center;font-size:19px;line-height:1.26;font-weight:600;letter-spacing:-.01em}}
.est p b{{font-weight:900;font-size:40px;line-height:1;letter-spacing:-.045em;color:{AZ}}}
.est p span{{grid-column:1/3;font-family:Mono;font-weight:500;font-size:18px;letter-spacing:.04em;opacity:.75;margin-top:8px;padding-top:6px;border-top:1px dashed rgba(11,13,18,.3)}}
.lomb{{position:absolute;left:{DOBRA}px;top:0;bottom:0;right:0;z-index:20;pointer-events:none;
  background:linear-gradient(90deg,rgba(255,255,255,.75) 0,rgba(255,255,255,0) 3px,rgba(70,62,50,.16) 5px,rgba(70,62,50,.26) 35%,rgba(40,34,26,.50) 100%);mix-blend-mode:multiply}}
.lomb2{{position:absolute;left:{DOBRA-46}px;width:46px;top:0;bottom:0;z-index:20;pointer-events:none;
  background:linear-gradient(90deg,rgba(0,0,0,0),rgba(70,62,50,.09))}}
.vinco{{position:absolute;left:{DOBRA-1}px;width:2px;top:0;bottom:0;z-index:21;background:linear-gradient(90deg,rgba(255,255,255,.95),rgba(120,110,95,.35))}}
.aviso{{position:absolute;left:{DOBRA+38}px;top:{p.get('aviso_y',960)}px;transform:translate(-50%,-50%) rotate(90deg);white-space:nowrap;font-family:Mono;font-size:17px;letter-spacing:.2em;color:rgba(11,13,18,.62);z-index:19}}
.canto{{position:absolute;left:0;top:0;width:96px;height:96px;z-index:22;pointer-events:none;
  background:linear-gradient(135deg,rgba(120,110,95,.07) 0,rgba(0,0,0,0) 44%,rgba(90,80,65,.12) 49.4%,rgba(255,255,255,.85) 50.4%,rgba(0,0,0,0) 56%)}}
.marca{{z-index:6}}
.handle{{z-index:6;right:{1080-DOBRA+40}px}}
"""

def barras(seed=11, n=46, h=66):
    rnd = random.Random(seed); x = 0; s = []
    for i in range(n):
        w = rnd.choice([2, 2, 3, 4, 2, 5]) if i not in (0, 2, n // 2, n // 2 + 2, n - 3, n - 1) else 2
        hh = h + (10 if i in (0, 2, n // 2, n // 2 + 2, n - 3, n - 1) else 0)
        s.append(f'<rect x="{x}" y="0" width="{w}" height="{hh}" fill="{TI}"/>')
        x += w + rnd.choice([2, 2, 3, 4])
    return f'<svg width="{x}" height="{h+10}" viewBox="0 0 {x} {h+10}">{"".join(s)}</svg>', x

def circulo(w, h):
    """Volta de caneta à mão em torno do trecho: elipse com leve tremor, que passa do ponto de partida."""
    import math
    W, H = w + 74, h + 30
    cx, cy, rx, ry = W / 2, H / 2, W / 2 - 4, H / 2 - 3
    pts = []
    for k in range(0, 58):
        a = math.radians(-100 + k * 6.4)
        r = 1 + 0.03 * math.sin(k * 0.5) + (0.025 * (k - 52) / 5 if k > 52 else 0)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a) + (k / 58) * 1))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<path d="{d}" fill="none" stroke="{CANETA}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" opacity=".92"/></svg>')

# encolhe a linha da tarja só se ela não couber antes do vinco (nunca quebra)
FIT = f"""<script>document.fonts.ready.then(()=>{{const s=document.querySelector('.tarja span');const max={DOBRA-M-10-36};
let f=parseFloat(getComputedStyle(s).fontSize);while(s.getBoundingClientRect().width>max&&f>30){{f-=.5;s.style.fontSize=f+'px'}}
document.body.dataset.ok=1}});</script>"""

def build(p):
    e = html.escape
    ind = "".join(f"<li>{e(t)}</li>" for t in p["indicado"]["itens"])
    pos = "".join(f"<li>{e(t)}</li>" for t in p["posologia"]["itens"])
    adv = p["advertencia"]
    advl = "".join(f"<li>{e(t)}</li>" for t in adv["itens"])
    rot, txt = adv["reacao"]
    cb, cbw = barras()
    digitos = p.get("ean", "7 891234 560528")
    lr, lv = p["lote"]; vr, vv = p["validade"]
    est = p["estudo"]
    nome = e(p["produto"])
    corpo = (
        f'<div class="face"></div><div class="fibra"></div>'
        f'<div class="reg mono">{e(p.get("registro",""))}</div>' +
        (f'<div class="k mono">{e(p["kicker"])}</div>' if p.get("kicker") else '')+
        f'<div class="prod">{nome}</div>'
        f'<div class="dose">{R._ed(p["dosagem"]).replace("<em class=\"it\">","<b>").replace("</em>","</b>")}</div>'
        f'<div class="apoio">{R._ed(p["apoio"])}</div>'
        f'<div class="tarja"><span>{e(p["tarja"])}'
        + (f'<small>{e(p["tarja_sub"])}</small>' if p.get("tarja_sub") else '') + '</span></div>'
        f'<div class="cols"><div class="sec ind"><h3>{e(p["indicado"]["titulo"])}</h3><ul>{ind}</ul></div>'
        f'<div class="sec pos"><h3>{e(p["posologia"]["titulo"])}</h3><ol>{pos}</ol></div></div>'
        f'<div class="adv sec"><h3><i>!</i>{e(adv["titulo"])}</h3><ul>{advl}</ul>'
        f'<div class="reac"><b>{e(rot)}</b> {e(txt)}</div></div>'
        f'<div class="pe"><div class="cb">{cb}<small>{e(digitos)}</small></div>'
        f'<div class="lote">{e(lr)} <span class="c">{e(lv)}{circulo(len(lv)*14.5, 30)}</span><br>{e(vr)} {e(vv)}</div>'
        f'</div><div class="est"><span class="lab">{e(est.get("rotulo","ESTUDO"))}</span><p><b>{e(est["num"])}</b><em style="font-style:normal;white-space:nowrap">{e(est["texto"]).replace("|", "<br>")}</em><span>{e(est["fonte"])}</span></p></div>'
        f'<div class="lomb2"></div><div class="lomb"></div><div class="vinco"></div>'
        f'<div class="aviso">{e(p.get("aviso",""))}</div><div class="canto"></div>'
    )
    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + R._base(CARTAO, TI, css(p)) +
            f'</style></head><body>{corpo}<div class="grao"></div>{R._rodape(True)}{FIT}</body></html>')

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_selector("body[data-ok]", state="attached"); pg.wait_for_timeout(300)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
