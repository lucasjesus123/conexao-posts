"""Recorta um objeto 3D gerado em fundo escuro mantendo o brilho (glow) como transparência.
Uso: python3 scripts/recorte_brilho.py entrada.jpg saida.png
Precisa: pip install "rembg[cpu]" pillow numpy --break-system-packages
"""
import sys
import numpy as np
from PIL import Image
from rembg import remove, new_session

src = Image.open(sys.argv[1]).convert("RGB")
m = np.array(remove(src, session=new_session("isnet-general-use")))[:, :, 3].astype(float) / 255
a = np.array(src).astype(float)
borda = np.concatenate([a[:20].reshape(-1, 3), a[-20:].reshape(-1, 3), a[:, :20].reshape(-1, 3), a[:, -20:].reshape(-1, 3)])
bg = np.median(borda, 0)
glow = np.clip(np.clip((a - bg).max(2), 0, None) / 90, 0, 1) ** 1.2
alpha = np.maximum(m, glow)
rgb = np.clip((a - bg * (1 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-3), 0, 255)
im = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
bb = im.getbbox()
im = im.crop(bb)
im.resize((900, int(900 * im.height / im.width))).save(sys.argv[2], optimize=True)
print("ok", sys.argv[2])
