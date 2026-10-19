"""Arte de tráfego pago 'Atenção, Lajeado' — cena do GPT sem texto + textos por código."""
import base64, pathlib, sys
from playwright.sync_api import sync_playwright

S = pathlib.Path("/tmp/claude-0/-home-claude/2f9aa9cf-efcd-5930-acf1-b1be0c7a3bb7/scratchpad")
R = pathlib.Path("/home/claude/conexao-posts")
OUT = pathlib.Path(sys.argv[1])

def b64(p, mime):
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

F = S / "fonts"
MONO = b64(F / "fontsource-jetbrains-mono-5.3.0/files/jetbrains-mono-latin-700-normal.woff2", "font/woff2")
CENA = b64(R / "gerar/saida/2026-10-19-lajeado-sem-texto.png", "image/png")

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family:'Mono'; src:url({MONO}) format('woff2'); font-weight:700; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1350px; overflow:hidden; background:#05070D; font-family:'Inter Display','Inter',sans-serif; color:#fff; position:relative; }}
.wrap {{ position:absolute; left:0; top:0; width:1080px; height:1350px; -webkit-mask-image: linear-gradient(to right, transparent 0, #000 90px, #000 990px, transparent 1080px); }}
.cena {{ position:absolute; left:90px; top:118px; width:900px;
  -webkit-mask-image: linear-gradient(to bottom, transparent 0, #000 90px, #000 46%, transparent 55%); }}
.tag {{ position:absolute; top:92px; left:50%; transform:translateX(-50%); display:flex; align-items:center; gap:16px;
  background:#E11D2A; padding:16px 34px; border-radius:14px; font-weight:900; font-size:42px; letter-spacing:.5px;
  box-shadow:0 0 36px rgba(255,40,40,.55); white-space:nowrap; }}
.tag svg {{ width:38px; height:38px; }}
.bloco {{ position:absolute; left:96px; right:96px; bottom:226px; text-align:center; }}
.k {{ font-family:'Mono'; color:#22D3EE; font-size:22px; letter-spacing:5px; margin-bottom:18px; }}
h1 {{ font-weight:900; line-height:1.0; letter-spacing:-2.5px; }}
h1 .g {{ display:block; font-size:86px; background:linear-gradient(90deg,#22D3EE,#2F6BFF 75%,#7C5CFF); -webkit-background-clip:text; color:transparent; padding-bottom:6px; }}
h1 .w {{ display:block; font-size:72px; }}
.sub {{ font-size:31px; line-height:1.38; color:rgba(255,255,255,.86); margin:26px auto 0; max-width:820px; }}
.sub b {{ color:#fff; }}
.chips {{ display:flex; justify-content:center; gap:16px; margin-top:32px; }}
.chips span {{ font-size:25px; font-weight:600; padding:13px 24px; border-radius:40px; border:1.5px solid rgba(34,211,238,.7); background:rgba(5,7,13,.55); white-space:nowrap; }}
.chips span.p {{ border-color:#8B7CFF; font-weight:800; }}
.cta {{ position:absolute; bottom:96px; left:50%; transform:translateX(-50%); background:#22D3EE; color:#05070D; font-weight:800; font-size:32px;
  letter-spacing:.5px; padding:20px 46px; border-radius:50px; box-shadow:0 0 40px rgba(34,211,238,.45); white-space:nowrap; }}
</style></head><body>
<div class="wrap"><img class="cena" src="{CENA}"></div>
<div class="tag"><svg viewBox="0 0 24 24"><path d="M12 2 1 21h22L12 2z" fill="#fff"/><rect x="11" y="8" width="2" height="7" fill="#E11D2A"/><rect x="11" y="16.5" width="2" height="2" fill="#E11D2A"/></svg>ATENÇÃO, LAJEADO</div>
<div class="bloco">
  <div class="k">IMERSÃO PRESENCIAL</div>
  <h1><span class="g">Inteligência Artificial</span><span class="w">para Negócios</span></h1>
  <p class="sub">Aprenda a <b>implantar ferramentas de I.A.</b> que trabalham no seu negócio <b>todos os dias.</b></p>
  <div class="chips"><span>25/11 · 19h às 22h</span><span>Tri Hotel · Lajeado</span><span class="p">R$ 198,90</span></div>
</div>
<div class="cta">INSCRIÇÕES ABERTAS</div>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
    pg.set_content(html); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUT)); b.close()
print("ok")
