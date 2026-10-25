"""Objeto 3D 'Protocolo cancelado': tirinha de papel térmico riscada em ciano + etiqueta de vidro.
Gera campanhas/assets/protocolo_riscado3d.png (PNG transparente) via Playwright."""
import base64, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / 'kit' / 'fonts'
OUT = ROOT / 'campanhas' / 'assets' / 'protocolo_riscado3d.png'
def ff(n): return base64.b64encode((F/n).read_bytes()).decode()
fonts = (f"@font-face{{font-family:Mono;font-weight:500;src:url(data:font/woff2;base64,{ff('jetbrains-mono-latin-500-normal.woff2')})}}"
         f"@font-face{{font-family:Mono;font-weight:500;src:url(data:font/woff2;base64,{ff('jetbrains-mono-latin-ext-500-normal.woff2')});unicode-range:U+0100-024F}}"
         f"@font-face{{font-family:M;font-weight:800;src:url(data:font/woff2;base64,{ff('montserrat-latin-800-normal.woff2')})}}"
         f"@font-face{{font-family:M;font-weight:600;src:url(data:font/woff2;base64,{ff('montserrat-latin-600-normal.woff2')})}}")
# serrilhado (zigue-zague) em cima e embaixo
def zig(n=18, d=14):
    top = [f"{i*100/n:.3f}% {0 if i%2==0 else d}px" for i in range(n+1)]
    bot = [f"{(n-i)*100/n:.3f}% calc(100% - {0 if i%2==0 else d}px)" for i in range(n+1)]
    return "polygon(" + ",".join(top + bot) + ")"
import random
random.seed(7)
bars, x = "", 0
while x < 270:
    w = random.choice([2, 3, 3, 5, 6, 8]); bars += f'<rect x="{x}" y="0" width="{w}" height="64" fill="#2E2E2E"/>'; x += w + random.choice([2, 3, 4, 6])
PIN = '<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#22D3EE" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.6"/></svg>'
html = f"""<!doctype html><html><head><meta charset=utf-8><style>{fonts}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:transparent;width:760px;height:900px;overflow:hidden}}
.scene{{position:absolute;inset:0;perspective:1500px}}
.wrap{{position:absolute;left:170px;top:60px;width:360px;height:620px;transform:rotateX(10deg) rotateY(-8deg) rotateZ(-8deg);transform-style:preserve-3d}}
.shadow{{position:absolute;inset:20px 10px -10px 30px;background:rgba(0,0,0,.55);filter:blur(30px);transform:translate(10px,40px)}}
.glow{{position:absolute;inset:-6px;clip-path:{zig()};background:rgba(34,211,238,.28);filter:blur(12px)}}
.paper{{position:absolute;inset:0;clip-path:{zig()};background:#F2F0EA;padding:40px 30px 34px;color:#3A3A3A;font-family:Mono;font-weight:500;font-size:19px;line-height:1.5;letter-spacing:.02em;
  background-image:linear-gradient(180deg,rgba(0,0,0,.06),rgba(0,0,0,0) 18%,rgba(0,0,0,0) 80%,rgba(0,0,0,.08)),url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .14 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.c{{text-align:center}} .b{{font-size:21px;letter-spacing:.08em}}
.dash{{border-top:2px dashed #6A6A6A;margin:12px 0}}
.sp{{height:12px}}
.bc{{display:block;margin:14px auto 6px}}
.strike{{position:absolute;left:0;top:0;overflow:visible}}
.tag{{position:absolute;left:345px;top:560px;width:300px;height:120px;border-radius:18px;transform:rotate(6deg);
  background:rgba(10,20,35,.82);border:2px solid rgba(255,255,255,.45);backdrop-filter:blur(10px);
  box-shadow:0 30px 50px rgba(0,0,0,.5),0 0 30px rgba(34,211,238,.35),inset 0 1px 0 rgba(255,255,255,.3);
  display:flex;align-items:center;gap:14px;padding:0 20px;color:#fff}}
.tag b{{display:block;font-family:M;font-weight:800;font-size:22px;line-height:1.15;letter-spacing:-.01em}}
.tag small{{display:block;font-family:M;font-weight:600;font-size:19px;color:#7DF3FF;margin-top:4px}}
</style></head><body><div class="scene"><div class="wrap">
<div class="shadow"></div><div class="glow"></div>
<div class="paper">
<div class="c b">CENTRAL DE SUPORTE</div><div class="dash"></div>
<div class="sp"></div>
<div id="l1">SUA SOLICITAÇÃO FOI</div><div id="l2">ENCAMINHADA</div>
<div class="sp"></div>
<div>PROTOCOLO Nº ••••••••</div>
<div id="l3">STATUS: EM ANÁLISE</div>
<div>PRAZO: ATÉ __ DIAS ÚTEIS</div>
<div class="dash"></div>
<div style="font-size:16px">NÃO RESPONDA ESTA MENSAGEM</div>
<svg class="bc" width="270" height="64">{bars}</svg>
<div class="c b">AGUARDE RETORNO</div>
</div>
<svg class="strike" width="360" height="620" viewBox="0 0 360 620"><defs><filter id="gl" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7"/></filter></defs>
<g stroke="#22D3EE" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M16 150 C 60 136, 100 156, 150 136 S 240 112, 290 108 S 330 96, 344 92" stroke-width="18" opacity=".55" filter="url(#gl)"/>
<path d="M16 150 C 60 136, 100 156, 150 136 S 240 112, 290 108 S 330 96, 344 92" stroke-width="10"/>
<path d="M20 226 C 55 214, 90 230, 130 212 S 200 196, 240 198 S 270 190, 286 186" stroke-width="18" opacity=".55" filter="url(#gl)"/>
<path d="M20 226 C 55 214, 90 230, 130 212 S 200 196, 240 198 S 270 190, 286 186" stroke-width="10"/>
</g></svg>
</div>
<div class="tag">{PIN}<div><b>QUEM MONTOU<br>ATENDE</b><small>Lajeado/RS</small></div></div>
</div></body></html>"""
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 760, "height": 900})
    pg.set_content(html, wait_until="load"); pg.wait_for_timeout(300)
    # posição das linhas a riscar (para conferir)
    print(pg.evaluate("['l1','l2','l3'].map(i=>{const r=document.getElementById(i).getBoundingClientRect();return [i,Math.round(r.x),Math.round(r.y),Math.round(r.width)]})"))
    pg.screenshot(path=str(OUT), omit_background=True); b.close()
print(OUT)
