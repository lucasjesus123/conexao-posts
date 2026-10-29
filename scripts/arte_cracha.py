"""Post 2026-10-29 08h: papel claro + 'crachá da equipe' (cordão azul entrando pelo topo, crachá plastificado com o semáforo da IA).
Uso: python3 scripts/arte_cracha.py post_render.json pasta_saida
Campos do JSON: kicker, titulo ({itálico azul}, | quebra), tam, cracha_cab, cracha_apoio,
blocos [[cor, rótulo, [itens]]...], rodape_cracha, cta. Cores dos blocos: verde | amarelo | vermelho."""
import json, sys, html, base64, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
FON = ROOT / "campanhas" / "fontes"
def ff(n): return base64.b64encode((FON / n).read_bytes()).decode()
CAVEAT = (f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{ff('caveat-latin-600-normal.woff2')})}}"
          f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{ff('caveat-latin-ext-600-normal.woff2')});unicode-range:U+0100-024F}}")
AZ, TI = R.AZUL, R.TINTA
CORES = {"verde": "#22A559", "amarelo": "#F2B705", "vermelho": "#E5484D"}

# geometria do crachá (antes da rotação)
CX, CY, CW = 540, 236, 500   # left, top, width

def css(p):
    return CAVEAT + f"""
.k{{position:absolute;left:72px;top:80px;font-size:19px;opacity:.6;z-index:4}}
h1{{position:absolute;left:72px;top:128px;width:480px;font-weight:900;font-size:{p.get('tam',78)}px;line-height:1.02;letter-spacing:-.045em;z-index:4}}
h1 .it{{color:{AZ};font-size:1.08em;letter-spacing:-.02em;font-weight:500}}
.cordao{{position:absolute;left:0;top:0;z-index:2;overflow:visible}}
.wrap{{position:absolute;left:{CX}px;top:{CY}px;width:{CW}px;transform:rotate(2deg);transform-origin:50% 0;z-index:3}}
.sombra{{position:absolute;inset:18px -6px -26px 22px;border-radius:34px;background:rgba(11,13,18,.30);filter:blur(26px)}}
.sombra2{{position:absolute;inset:4px 0 -6px 6px;border-radius:30px;background:rgba(11,13,18,.16);filter:blur(5px)}}
.cr{{position:relative;border-radius:30px;background:#FFFFFF;padding:64px 34px 28px 34px;
  box-shadow:inset 0 0 0 1.5px rgba(11,13,18,.07), inset 0 0 0 9px #fff, inset 0 0 0 10px rgba(11,13,18,.05)}}
.brilho{{position:absolute;inset:0;border-radius:30px;pointer-events:none;
  background:linear-gradient(118deg,rgba(255,255,255,0) 22%,rgba(255,255,255,.38) 30%,rgba(255,255,255,0) 40%),
             linear-gradient(160deg,rgba(225,232,245,.35) 0%,rgba(255,255,255,0) 35%,rgba(236,238,244,.0) 70%,rgba(214,220,232,.35) 100%);
  mix-blend-mode:normal}}
.furo{{position:absolute;left:50%;top:22px;width:92px;height:22px;margin-left:-46px;border-radius:12px;background:{R.PAPEL};
  box-shadow:inset 0 3px 5px rgba(0,0,0,.28), 0 1px 0 rgba(255,255,255,.9)}}
.cab{{display:flex;justify-content:space-between;align-items:center;font-size:17px;padding-bottom:14px;border-bottom:2px solid {TI}}}
.cab b{{font-weight:500;color:{AZ}}}
.apoio{{font-size:25px;font-weight:600;margin:16px 0 20px;letter-spacing:-.01em;line-height:1.25}}
.apoio .it{{color:{AZ};font-size:1.08em}}
.bl{{position:relative;padding:14px 0 14px 26px;margin-bottom:12px;border-radius:4px 14px 14px 4px}}
.bl:before{{content:"";position:absolute;left:0;top:0;bottom:0;width:8px;border-radius:6px;background:var(--c)}}
.bl{{background:linear-gradient(90deg,var(--t) 0,rgba(255,255,255,0) 85%)}}
.rot{{display:flex;align-items:center;gap:11px;font-weight:800;font-size:20px;letter-spacing:.03em;margin-bottom:8px;white-space:nowrap}}
.rot i{{width:16px;height:16px;border-radius:50%;background:var(--c);box-shadow:0 0 0 4px var(--t);flex:none}}
.it-l{{list-style:none}}
.it-l li{{font-size:25px;font-weight:600;line-height:1.36;letter-spacing:-.012em;white-space:nowrap}}
.it-l li:before{{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:{TI};opacity:.35;margin:0 12px 4px 0;vertical-align:middle}}
.pe{{display:flex;gap:18px;align-items:center;margin-top:16px;padding-top:16px;border-top:1.5px dashed rgba(11,13,18,.25)}}
.barras{{display:flex;gap:2px;align-items:stretch;height:70px;flex:none;opacity:.85}}
.barras i{{background:{TI};display:block}}
.fato{{text-wrap:balance;font-size:19.5px;line-height:1.32;font-weight:600;opacity:.78}}
.fato span{{display:block;font-family:Mono;font-weight:500;font-size:15px;letter-spacing:.06em;opacity:.8;margin-top:5px;font-size:16px}}
.sub{{position:absolute;left:72px;width:440px;top:{p.get('sub_top',486)}px;font-size:30px;line-height:1.36;font-weight:400;opacity:.78;z-index:4}}
.barra{{position:absolute;left:72px;top:{p.get('sub_top',486)-44}px;width:120px;height:10px;background:{AZ};z-index:4}}
.sub b{{font-weight:800;opacity:1}}
.cta{{position:absolute;left:72px;top:1060px;font-family:Hand;font-weight:600;color:{AZ};font-size:50px;line-height:1.02;transform:rotate(-4deg);z-index:4}}
.seta{{position:absolute;left:0;top:0;z-index:4;overflow:visible}}
.handle,.marca{{z-index:5}}
"""

def barras():
    larg = [3, 1, 2, 1, 4, 1, 2, 3, 1, 1, 3, 2, 1, 4, 1, 2]
    return '<div class="barras">' + "".join(f'<i style="width:{w}px;margin-right:{1+(i%3)}px"></i>' for i, w in enumerate(larg)) + "</div>"

def cordao():
    """Duas fitas azuis vindas de fora do quadro, em V, até a presilha metálica sobre o furo do crachá."""
    px, py = CX + CW / 2 + 4, CY + 6          # ponto da argola (já considerando a leve rotação)
    L1 = (px - 230, -60); L2 = (px + 170, -60)
    def fita(a, b, w, sombra=False):
        cor = "rgba(11,13,18,.22)" if sombra else AZ
        return (f'<path d="M{a[0]} {a[1]} C {a[0]+20} {a[1]+90}, {b[0]-(b[0]-a[0])*.25} {b[1]-60}, {b[0]} {b[1]}" '
                f'fill="none" stroke="{cor}" stroke-width="{w}" stroke-linecap="butt" {"filter=\"url(#bl)\"" if sombra else ""}/>')
    jx, jy = px, py - 96   # junção das fitas
    s = [f'<svg class="cordao" width="1080" height="1350" viewBox="0 0 1080 1350">',
         '<defs><filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>',
         '<linearGradient id="met" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6FA"/><stop offset=".45" stop-color="#9AA1AD"/>'
         '<stop offset=".6" stop-color="#D9DDE4"/><stop offset="1" stop-color="#6E7480"/></linearGradient>',
         f'<linearGradient id="fg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2459E0"/><stop offset=".5" stop-color="{AZ}"/><stop offset="1" stop-color="#2150CC"/></linearGradient></defs>']
    # sombras no papel
    s.append(fita((L1[0] + 18, L1[1]), (jx + 18, jy + 14), 34, True))
    s.append(fita((L2[0] + 18, L2[1]), (jx + 18, jy + 14), 34, True))
    for a in (L1, L2):
        s.append(f'<path d="M{a[0]} {a[1]} C {a[0]+20} {a[1]+90}, {jx-(jx-a[0])*.25} {jy-60}, {jx} {jy}" fill="none" stroke="url(#fg)" stroke-width="34"/>')
        # costura/brilho da fita
        s.append(f'<path d="M{a[0]} {a[1]} C {a[0]+20} {a[1]+90}, {jx-(jx-a[0])*.25} {jy-60}, {jx} {jy}" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="2" stroke-dasharray="7 6" transform="translate(0,0)"/>')
    # ponteira (dobra) da fita
    s.append(f'<rect x="{jx-24}" y="{jy-14}" width="48" height="40" rx="6" fill="#2150CC"/>')
    s.append(f'<rect x="{jx-24}" y="{jy-14}" width="48" height="8" rx="4" fill="rgba(255,255,255,.18)"/>')
    # presilha metálica: tampa + haste + mosquetão
    s.append(f'<rect x="{jx-20}" y="{jy+20}" width="40" height="22" rx="5" fill="url(#met)" stroke="#5B616C" stroke-width="1"/>')
    s.append(f'<rect x="{jx-5}" y="{jy+40}" width="10" height="16" fill="url(#met)" stroke="#5B616C" stroke-width="1"/>')
    s.append(f'<path d="M{jx} {jy+54} C {jx+30} {jy+56}, {jx+30} {py+20}, {jx} {py+22} C {jx-30} {py+20}, {jx-30} {jy+56}, {jx} {jy+54} Z" '
             f'fill="none" stroke="url(#met)" stroke-width="7"/>')
    s.append(f'<path d="M{jx} {jy+54} C {jx+30} {jy+56}, {jx+30} {py+20}, {jx} {py+22} C {jx-30} {py+20}, {jx-30} {jy+56}, {jx} {jy+54} Z" '
             f'fill="none" stroke="rgba(60,64,72,.55)" stroke-width="1"/>')
    s.append('</svg>')
    return "".join(s)

def cracha(p):
    tint = {"verde": "rgba(34,165,89,.10)", "amarelo": "rgba(242,183,5,.13)", "vermelho": "rgba(229,72,77,.10)"}
    bls = []
    for cor, rot, itens in p["blocos"]:
        li = "".join(f"<li>{html.escape(t)}</li>" for t in itens)
        bls.append(f'<div class="bl" style="--c:{CORES[cor]};--t:{tint[cor]}"><div class="rot"><i></i>{html.escape(rot)}</div><ul class="it-l">{li}</ul></div>')
    fato, fonte = p["rodape_cracha"]
    return (f'<div class="wrap"><div class="sombra"></div><div class="sombra2"></div><div class="cr"><div class="furo"></div>'
            f'<div class="cab mono"><span>{html.escape(p["cracha_cab"])}</span></div>'
            f'<div class="apoio">{R._ed(p["cracha_apoio"])}</div>{"".join(bls)}'
            f'<div class="pe">{barras()}<div class="fato">{html.escape(fato)}<span>{html.escape(fonte)}</span></div></div>'
            f'<div class="brilho"></div></div></div>')

def seta():
    a = AZ
    return (f'<svg class="seta" width="1080" height="1350"><path d="M330 1150 C 400 1166, 470 1150, 520 1110" fill="none" stroke="{a}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M500 1108 L 522 1108 L 520 1130" fill="none" stroke="{a}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def build(p):
    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + R._base(R.PAPEL, TI, css(p)) +
            f'</style></head><body><div class="grao"></div><div class="k mono">{html.escape(p["kicker"])}</div>'
            f'<h1>{R._ed(p["titulo"])}</h1>' + (f'<div class="barra"></div><p class="sub">{R._ed(p["subtitulo"])}</p>' if p.get('subtitulo') else '') + f'{cordao()}{cracha(p)}'
            f'<div class="cta">{R._ed(p["cta"])}</div>{seta()}{R._rodape(True)}</body></html>')

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in posts:
            pg = b.new_page(viewport={"width": 1080, "height": 1350})
            pg.set_content(build(p), wait_until="load"); pg.wait_for_timeout(400)
            f = out / f"{p['id']}.png"; pg.screenshot(path=str(f)); pg.close()
            R.story(f, out / f"{p['id']}_story.png")
            Image.open(f).convert("RGB").save(out / f"{p['id']}.jpg", quality=80, optimize=True, progressive=True)
            print(f)
        b.close()

if __name__ == "__main__":
    main(*sys.argv[1:])
