"""Post 2026-11-04 08h: nota clara + 'A pergunta que não cabe na caixa' (duas barras de busca genéricas em HTML:
a curta 'ANTES' e a longa 'AGORA', que quebra em 3 linhas e fura a borda direita do cartão; régua à mão em azul
medindo 1x / 3x, também passando da borda; card cinza de resposta da IA com chip 'Patrocinado' e um vazio onde
caberia um nome, com anotação à mão). Sem logo nem cores de terceiros: lupa em traço, pílula branca e cinza.
Uso: python3 scripts/arte_caixa_busca.py posts/2026-11-04-08h/render.json pasta_saida
Campos do JSON (além de id, modelo, pilar, tema):
  kicker, kicker_dir          mono no topo, fora do cartão (esquerda / direita)
  avatar, nome                foto redonda e nome no cabeçalho do cartão (handle vem do render.py)
  texto                       frase principal ({trecho} = itálico azul serif, | = quebra)
  busca_antes                 {"tag": "ANTES", "texto": "dentista lajeado", "regua": "1x"}
  busca_agora                 {"tag": "AGORA", "texto": "...", "regua": "3x"}  (a pílula estica e passa da borda)
  resposta                    {"chip": "Patrocinado", "nota": "quem aparece|aqui?"}  (nota = Caveat à mão, | = quebra)
  virada                      linha curta em negrito perto do rodapé; ==trecho== = marca-texto amarelo
  rodape                      mono no pé do cartão (fonte do fato; | = quebra)
  fonte_mao                   lista de caminhos .woff2 da Caveat 600 (latin, latin-ext)
  opcionais de ajuste: tam (px do título), topo_miolo (y das barras), antes_w, agora_w (largura das pílulas),
                       busca_fs (px do texto das buscas)"""
import json, sys, html, base64, pathlib, re, importlib.util
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("render", ROOT / "kit" / "render.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
AZ, TI, PAPEL = R.AZUL, R.TINTA, R.PAPEL
BORDA = "#D8D5CC"
CINZA_CARD = "#F3F2EE"
PLACE = "#DEDBD3"

CARD_L, CARD_T, CARD_W, CARD_H = 64, 132, 952, 1066
CARD_R = CARD_L + CARD_W
COL_L = CARD_L + 52

def fonte_mao(paths):
    paths = paths or [str(ROOT / "campanhas" / "fontes" / n) for n in
                      ("caveat-latin-600-normal.woff2", "caveat-latin-ext-600-normal.woff2")]
    out = []
    for p in paths:
        b = base64.b64encode(pathlib.Path(p).read_bytes()).decode()
        rng = ";unicode-range:U+0100-024F" if "ext" in pathlib.Path(p).name else ""
        out.append(f"@font-face{{font-family:Hand;font-weight:600;src:url(data:font/woff2;base64,{b}){rng}}}")
    return "".join(out)

LUPA = (f'<svg class="lupa" viewBox="0 0 40 40"><circle cx="17" cy="17" r="11" fill="none" stroke="{TI}" stroke-width="3.2"/>'
        f'<path d="M25.5 25.5 L35 35" stroke="{TI}" stroke-width="3.6" stroke-linecap="round"/></svg>')

def regua(w, label, lado="centro"):
    """cota desenhada à mão: linha levemente torta com traços nas pontas e o rótulo em Caveat"""
    st = f'fill="none" stroke="{AZ}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"'
    m = w / 2
    d = f"M4,22 C{w*.25:.0f},19 {w*.55:.0f},25 {w-4},21"
    ticks = (f'<path d="M5,8 L3,36" {st}/><path d="M{w-3},7 L{w-5},35" {st}/>'
             # marquinhas de régua a cada ~60px
             + "".join(f'<path d="M{x},{17 if i % 2 else 13} L{x},{27 if i % 2 else 31}" {st} stroke-width="2.2" opacity=".75"/>'
                       for i, x in enumerate(range(64, int(w) - 30, 60))))
    return (f'<div class="rg" style="width:{w}px"><svg width="{w}" height="40" viewBox="0 0 {w} 40" style="overflow:visible">'
            f'<path d="{d}" {st}/>{ticks}</svg><span class="rl rl-{lado}">{html.escape(label)}</span></div>')

def virada_html(s):
    return re.sub(r"==(.+?)==", r'<span class="mk">\1</span>', html.escape(s))

def build(p):
    av = base64.b64encode(pathlib.Path(p["avatar"]).read_bytes()).decode()
    a, g, r = p["busca_antes"], p["busca_agora"], p["resposta"]
    fs = p.get("busca_fs", 30)
    aw, gw = p.get("antes_w", 372), p.get("agora_w", 944)
    css = fonte_mao(p.get("fonte_mao")) + f"""
.k{{position:absolute;left:72px;right:72px;top:72px;display:flex;justify-content:space-between;font-size:18px;opacity:.6}}
.card{{position:absolute;left:{CARD_L}px;top:{CARD_T}px;width:{CARD_W}px;height:{CARD_H}px;background:#fff;border-radius:34px;
  box-shadow:0 30px 80px rgba(0,0,0,.11),0 2px 6px rgba(0,0,0,.04);border:1px solid rgba(0,0,0,.06)}}
.h{{position:absolute;left:{COL_L}px;top:{CARD_T + 46}px;display:flex;align-items:center;gap:20px}}
.h img{{width:84px;height:84px;border-radius:50%;object-fit:cover}}
.h b{{display:block;font-size:31px;font-weight:800;line-height:1.15}} .h span{{font-size:23px;opacity:.55}}
.tx{{position:absolute;left:{COL_L}px;right:{1080 - CARD_R + 40}px;top:{CARD_T + 160}px;font-size:{p.get('tam', 58)}px;line-height:1.1;font-weight:800;letter-spacing:-.03em}}
.tx .it{{color:{AZ};font-size:1.08em;letter-spacing:-.01em}}
.mi{{position:absolute;left:{COL_L}px;top:{p.get('topo_miolo', 512)}px;width:{CARD_W - 104}px}}
.tag{{font-family:Mono;font-size:18px;font-weight:500;letter-spacing:.16em;color:{TI};opacity:.55;margin:0 0 10px 6px}}
.tag.az{{color:{AZ};opacity:1}}
.pl{{position:relative;display:flex;align-items:flex-start;gap:16px;background:#fff;border:2px solid {BORDA};border-radius:40px;
  padding:19px 30px 19px 24px;box-shadow:0 4px 14px rgba(0,0,0,.06);font-size:{fs}px;line-height:1.34;font-weight:500;color:{TI}}}
.pl .lupa{{flex:none;width:30px;height:30px;margin-top:{(fs * 1.34 - 30) / 2:.0f}px;opacity:.7}}
.pl .q{{text-wrap:pretty}}
.pl.a{{width:{aw}px;border-radius:999px;white-space:nowrap}}
.pl.g{{width:{gw}px;border-color:{AZ};box-shadow:0 10px 30px rgba(47,107,255,.14)}}
.cur{{display:inline-block;width:3px;height:1.1em;background:{AZ};vertical-align:-.16em;margin-left:4px}}
.rg{{position:relative;height:40px;margin:5px 0 0}}
.rl{{position:absolute;top:-6px;font-family:Hand;font-weight:600;font-size:50px;line-height:1;color:{AZ};background:#fff;padding:0 10px}}
.rl-dir{{left:calc(100% + 10px);background:none;top:-10px}}
.rl-centro{{left:50%;transform:translateX(-50%) rotate(-3deg);top:-14px}}
.esp{{height:14px}}
.rs{{position:relative;margin-top:18px;width:{p.get('resp_w', 520)}px;background:{CINZA_CARD};border-radius:24px;padding:20px 24px 22px;border:1px solid rgba(0,0,0,.05)}}
.rs .top{{display:flex;align-items:center;gap:14px;margin-bottom:16px}}
.rs .chip{{font-family:Mono;font-size:16px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:{TI};
  border:1.6px solid rgba(11,13,18,.35);border-radius:8px;padding:5px 10px 4px}}
.rs .vaz{{flex:1;height:38px;border:2.4px dashed {AZ};border-radius:10px;background:rgba(47,107,255,.05)}}
.rs .ln{{height:14px;border-radius:7px;background:{PLACE};margin-top:12px}}
.nt{{position:absolute;left:{p.get('nota_x', 610)}px;top:0px;width:260px;font-family:Hand;font-weight:600;font-size:52px;line-height:1;color:{AZ};
  transform:rotate(-4deg);transform-origin:0 50%}}
.nt svg{{position:absolute;left:-122px;top:2px;overflow:visible}}
.vr{{margin-top:24px;font-size:26px;font-weight:700;color:{TI}}}
.vr .mk{{white-space:nowrap;background:linear-gradient(transparent 52%,#FFE14D 52%,#FFE14D 92%,transparent 92%);padding:0 3px;margin:0 -3px}}
.d{{position:absolute;left:{COL_L}px;right:{1080 - CARD_R + 40}px;top:{CARD_T + CARD_H - 72}px;font-size:16px;line-height:1.6;letter-spacing:.08em;opacity:.72}}
"""
    seta = (f'<svg width="110" height="50" viewBox="0 0 110 50"><path d="M106,26 C80,10 44,12 12,30" fill="none" stroke="{AZ}" stroke-width="3.2" stroke-linecap="round"/>'
            f'<path d="M26,18 L10,31 L28,40" fill="none" stroke="{AZ}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    miolo = (f'<div class="mi">'
             f'<div class="tag">{html.escape(a["tag"])}</div>'
             f'<div class="pl a">{LUPA}<span class="q">{html.escape(a["texto"])}<span class="cur"></span></span></div>'
             f'{regua(aw, a.get("regua", "1x"), "dir")}'
             f'<div class="esp"></div>'
             f'<div class="tag az">{html.escape(g["tag"])}</div>'
             f'<div class="pl g">{LUPA}<span class="q">{html.escape(g["texto"])}</span></div>'
             f'{regua(gw, g.get("regua", "3x"), "centro")}'
             f'<div class="rs"><div class="top"><span class="chip">{html.escape(r.get("chip", "Patrocinado"))}</span><span class="vaz"></span></div>'
             f'<div class="ln" style="width:88%"></div>'
             f'<div class="nt">{seta}{html.escape(r.get("nota", "")).replace("|", "<br>")}</div></div>'
             f'<div class="vr">{virada_html(p.get("virada", ""))}</div>'
             f'</div>')
    return ('<!doctype html><html><head><meta charset="utf-8"><style>' + R._base(PAPEL, TI, css) +
            f'</style></head><body><div class="grao"></div>'
            f'<div class="k mono"><span>{html.escape(p.get("kicker", ""))}</span><span>{html.escape(p.get("kicker_dir", ""))}</span></div>'
            f'<div class="card"></div>'
            f'<div class="h"><img src="data:image/jpeg;base64,{av}"><div><b>{html.escape(p.get("nome", "Lucas Jesus"))}</b><span>{R.HANDLE}</span></div></div>'
            f'<div class="tx">{R._ed(p["texto"])}</div>{miolo}'
            f'<div class="d mono">{html.escape(p.get("rodape", "")).replace("|", "<br>")}</div>'
            f'{R._rodape(True)}</body></html>')

def main(spec, outdir):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    posts = json.loads(pathlib.Path(spec).read_text()); out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
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
