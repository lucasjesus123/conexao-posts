import base64, pathlib
from playwright.sync_api import sync_playwright
F = pathlib.Path('/home/claude/kit/fonts')
def ff(n): return base64.b64encode((F/n).read_bytes()).decode()
fonts = f"@font-face{{font-family:M;font-weight:800;src:url(data:font/woff2;base64,{ff('montserrat-latin-800-normal.woff2')})}}@font-face{{font-family:Mono;src:url(data:font/woff2;base64,{ff('jetbrains-mono-latin-500-normal.woff2')})}}"
def row(word, n=8, cls=""):
    word = word.ljust(n)
    return '<div class="row"><i class="led"></i>' + "".join(f'<div class="t {cls}"><span>{c if c!=" " else "&nbsp;"}</span></div>' for c in word) + '</div>'
rows = '<div class="lbl"><span>DESTINO</span><span>STATUS</span></div>' if False else ''
html = f"""<!doctype html><html><head><meta charset=utf-8><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:transparent;width:1200px;height:900px;overflow:hidden}}
.scene{{position:absolute;inset:0;perspective:1600px}}
.board{{position:absolute;left:150px;top:150px;width:900px;padding:34px 38px 40px;border-radius:44px;
 transform:rotateY(-20deg) rotateX(10deg) rotateZ(-3deg);transform-style:preserve-3d;
 background:linear-gradient(150deg,#FBFCFE 0%,#E3E8F0 38%,#C7CEDA 70%,#EEF1F6 100%);
 box-shadow:0 0 0 3px rgba(255,255,255,.9) inset,0 0 0 2px #AEB6C4,0 50px 80px rgba(20,30,60,.35),0 0 60px rgba(34,211,238,.35)}}
.board:before{{content:"";position:absolute;left:60px;right:60px;top:12px;height:6px;border-radius:6px;background:#22D3EE;box-shadow:0 0 18px #22D3EE,0 0 40px #22D3EE}}
.head{{display:flex;justify-content:space-between;font-family:Mono;font-size:22px;letter-spacing:.25em;color:#5A6475;margin:8px 6px 18px}}
.head b{{color:#0E7490;font-weight:500}}
.glass{{background:#0B0E14;border-radius:24px;padding:22px 22px 26px;display:flex;flex-direction:column;gap:16px;box-shadow:inset 0 4px 20px rgba(0,0,0,.8)}}
.row{{display:flex;gap:10px;align-items:center}}
.led{{width:16px;height:16px;border-radius:50%;background:#22D3EE;box-shadow:0 0 12px #22D3EE,0 0 26px #22D3EE;margin-right:10px;flex:none}}
.t{{position:relative;width:86px;height:112px;border-radius:10px;background:linear-gradient(180deg,#22252D 0,#15171D 49%,#0A0B0F 51%,#1A1C22 100%);
 display:grid;place-items:center;font-family:M;font-weight:800;font-size:78px;color:#F4F6FA;box-shadow:0 3px 0 #000,inset 0 1px 0 rgba(255,255,255,.08)}}
.t:after{{content:"";position:absolute;left:0;right:0;top:50%;height:3px;background:#000;transform:translateY(-1px)}}
.t.c span{{color:#5BE7F5;text-shadow:0 0 18px rgba(34,211,238,.8)}}
.t.b{{filter:blur(2.2px);transform:rotateX(35deg)}} .t.b span{{opacity:.35}}
.fly{{position:absolute;left:820px;top:560px;width:120px;height:156px;border-radius:12px;font-size:110px;
 transform:rotate(18deg) translateZ(120px);box-shadow:0 30px 50px rgba(0,0,0,.45),0 0 40px rgba(34,211,238,.6)}}
.trail{{position:absolute;left:700px;top:600px;width:160px;height:90px;background:linear-gradient(90deg,transparent,rgba(34,211,238,.35));filter:blur(14px);transform:rotate(18deg)}}
.wire{{position:absolute;left:0;top:0}}
</style></head><body><div class="scene">
<svg class="wire" width="1200" height="900"><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#22D3EE" stop-opacity="0"/><stop offset=".4" stop-color="#22D3EE"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient><filter id="bl"><feGaussianBlur stdDeviation="8"/></filter></defs>
<path d="M60 820 C 300 760, 520 860, 760 740" stroke="url(#g)" stroke-width="14" fill="none" filter="url(#bl)" opacity=".8"/>
<path d="M60 820 C 300 760, 520 860, 760 740" stroke="url(#g)" stroke-width="3" fill="none"/></svg>
<div class="board"><div class="head"><span>CHEGADAS · IA</span><b>VALE DO TAQUARI</b></div><div class="glass">
{row("LAJEADO")}{row("EM ROTA", cls="c")}{row("", cls="b")}</div></div>
<div class="trail"></div><div class="t fly"><span>?</span></div>
</div></body></html>"""
pathlib.Path('board.html').write_text(html)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width":1200,"height":900})
    pg.set_content(html, wait_until="load"); pg.wait_for_timeout(300)
    pg.screenshot(path='painel_embarque3d.png', omit_background=True); b.close()
