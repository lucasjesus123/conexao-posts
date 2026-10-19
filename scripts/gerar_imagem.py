"""Gera imagens com a API da OpenAI (modelos GPT Image), usando fotos de referência.

Cada pedido é um arquivo gerar/pedidos/NOME.json:
  {
    "prompt": "descrição completa da cena (sem texto na imagem)",
    "referencias": ["lucas", "robo", "https://..."],   # apelidos de campanhas/referencias.json ou URLs
    "tamanho": "1024x1536",                               # 1024x1536 (vertical), 1536x1024 ou 1024x1024
    "qualidade": "high",
    "status": "pendente"
  }

Ou, no modo "estilo" (reproduzir uma referência guardada em estilos/ só trocando os textos):
  {
    "estilo": "anuncio-hud",                 # nome em estilos/estilos.json (ou caminho de uma imagem)
    "textos": ["VOCÊ, LOJISTA DE LAJEADO", "Imersão de I.A. em Lajeado", "..."],
    "com_lucas": true,                       # coloca o Lucas (fotos de referência) no lugar da pessoa
    "cena": "opcional: o que muda na imagem",
    "formato": "feed",                       # feed (1080x1350) ou story (1080x1920)
    "status": "pendente"
  }

A imagem sai em gerar/saida/NOME.png e o pedido vira "pronto" (ou "erro", com a mensagem da OpenAI).
Segredo necessário: OPENAI_API_KEY. Modelo: variável OPENAI_IMAGE_MODEL ou o primeiro da lista que a conta aceitar.
"""
import base64
import json
import os
import pathlib
import sys
import urllib.request

from openai import OpenAI

MODELOS = [m for m in [os.environ.get("OPENAI_IMAGE_MODEL", "").strip()] if m] + [
    "gpt-image-2", "gpt-image-1.5", "gpt-image-1",
]
REFS = json.loads(pathlib.Path("campanhas/referencias.json").read_text(encoding="utf-8"))
CACHE = pathlib.Path("campanhas/referencias")
SAIDA = pathlib.Path("gerar/saida")
ESTILOS = pathlib.Path("estilos/estilos.json")
FINAL = {"feed": (1080, 1350), "story": (1080, 1920)}
# A API aceita tamanhos múltiplos de 16 nos modelos novos; se recusar, cai para os tamanhos clássicos.
TAMANHOS = {"feed": ["1088x1360", "1024x1536"], "story": ["1088x1936", "1024x1536"]}


def montar_estilo(pedido):
    """Transforma um pedido de estilo em prompt + referências."""
    estilos = json.loads(ESTILOS.read_text(encoding="utf-8")) if ESTILOS.exists() else {}
    e = estilos.get(pedido["estilo"], {"arquivo": pedido["estilo"], "descricao": ""})
    textos = pedido.get("textos", [])
    if isinstance(textos, str):
        textos = [t.strip() for t in textos.split("|") if t.strip()]
    lista = "\n".join(f'{i + 1}. "{t}"' for i, t in enumerate(textos))
    refs = [e["arquivo"]]
    pessoa = ""
    if pedido.get("com_lucas"):
        refs.append("lucas")
        pessoa = ("The other reference images show the real man Lucas: wherever a person appears in the layout, "
                  "it must be exactly this man (same face, beard, hair and clear transparent-frame eyeglasses). ")
    else:
        pessoa = ("If the reference shows a person, replace them with a NEW generic person (never copy the real person of the reference). ")
    paleta = ""
    if pedido.get("paleta") == "marca":
        paleta = "Recolor the whole piece to this brand palette: deep blue-black #05070D, cyan #22D3EE, electric blue #2F6BFF, touches of violet. "
    obs = e.get("obs", "")
    formato = pedido.get("formato", "feed")
    prompt = f"""Recreate the FIRST reference image as a new Instagram {formato} ad in exactly the same visual style:
same layout, composition, color palette, typography style, light effects, buttons and overall quality. {e.get('descricao', '')}
{pessoa}{paleta}{pedido.get('cena', '')} {obs}
Remove EVERY logo, brand name, watermark, social media icon and website of the reference; the only brand allowed is the text in the list below.

Replace ALL the text of the reference with ONLY these texts, in this order of importance (headline first), written exactly as below,
in Brazilian Portuguese, keeping every accent and punctuation mark, perfectly spelled, with no extra words, no other text, no translations:
{lista}

Put each text in the equivalent place of the reference (headline where the headline is, button text in the button, etc.).
Do not invent prices, dates, numbers or logos that are not in the list. No watermark.
Do NOT write any phone number, website, @handle or social icons: leave the bottom 11% of the image (and, in a story, the bottom 20%) clean and dark — a footer is added later."""
    return prompt, refs, formato


def ajustar(png_bytes, formato):
    """Deixa a imagem no tamanho exato do Instagram (corta o excesso pelo centro)."""
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    w, h = FINAL[formato]
    esc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def rodape(im, formato, destaque=""):
    """Logo + WhatsApp + site aplicados por código (o GPT erra site e telefone). No story, acima dos 20% da base.
    destaque: pílula ciano opcional acima do contato (ex.: "INSCRIÇÕES ABERTAS")."""
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    im = im.convert("RGBA")
    W, H = im.size
    base = H if formato == "feed" else int(H * 0.80)
    a = np.asarray(im).astype(float)
    cor = np.median(a[base - 160:base - 140, W // 3:2 * W // 3, :3].reshape(-1, 3), 0)
    h = 150
    g = np.zeros((h, W, 4), dtype=np.uint8)
    g[..., :3] = cor
    g[..., 3] = (np.clip(np.linspace(0, 1, h) * 3, 0, 1)[:, None] * 240).astype(np.uint8)
    im.alpha_composite(Image.fromarray(g, "RGBA"), (0, base - h))
    if formato == "story":
        fundo = np.zeros((H - base, W, 4), dtype=np.uint8); fundo[..., :3] = cor; fundo[..., 3] = 240
        im.alpha_composite(Image.fromarray(fundo, "RGBA"), (0, base))
    logo = Image.open("campanhas/assets/logo_conexao.png").convert("RGBA")
    lh = 54
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    im.alpha_composite(logo, (56, base - lh - 34))
    d = ImageDraw.Draw(im)
    t = "(51) 99266-8095  ·  conexaomkt.com.br"
    if destaque:
        fb = ImageFont.truetype("campanhas/fontes/Inter-SemiBold.otf", 26)
        f = ImageFont.truetype("campanhas/fontes/Inter-SemiBold.otf", 24)
        w1 = d.textlength(destaque, font=fb)
        x1, y1 = W - 56 - w1 - 44, base - 118
        d.rounded_rectangle([x1, y1, W - 56, y1 + 48], radius=30, fill=(34, 211, 238, 255))
        d.text((x1 + 22, y1 + 9), destaque, font=fb, fill=(5, 7, 13, 255))
        d.text((W - 56 - d.textlength(t, font=f), base - 52), t, font=f, fill=(255, 255, 255, 230))
    else:
        f = ImageFont.truetype("campanhas/fontes/Inter-SemiBold.otf", 27)
        d.text((W - 56 - d.textlength(t, font=f), base - 34 - lh / 2 - 17), t, font=f, fill=(255, 255, 255, 235))
    return im.convert("RGB")


def respiro(im, escala=0.93):
    """Encolhe a arte e completa as bordas com o próprio fundo desfocado: dá margem de respiro
    quando o GPT encosta o texto nas laterais."""
    from PIL import Image, ImageFilter
    import numpy as np
    im = im.convert("RGB")
    W, H = im.size
    bg = im.resize((W, H)).filter(ImageFilter.GaussianBlur(50))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (5, 7, 13)), 0.55)
    w, h = int(W * escala), int(H * escala)
    peq = im.resize((w, h), Image.LANCZOS)
    m = np.ones((h, w))
    f = 40
    r = np.linspace(0, 1, f)
    m[:, :f] *= r[None, :]; m[:, -f:] *= r[::-1][None, :]; m[:f, :] *= r[:, None]; m[-f:, :] *= r[::-1][:, None]
    bg.paste(peq, ((W - w) // 2, (H - h) // 2), Image.fromarray((m * 255).astype("uint8")))
    return bg


def selo_centro(im, texto="INSCRIÇÕES ABERTAS", margem=58):
    """Rodapé mínimo: só uma pílula ciano centralizada, com margem de respiro da base."""
    from PIL import ImageDraw, ImageFont
    im = im.convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("campanhas/fontes/Inter-SemiBold.otf", 30)
    w = d.textlength(texto, font=f)
    pw, ph = w + 72, 64
    x, y = (W - pw) / 2, H - margem - ph
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=ph / 2, fill=(34, 211, 238))
    d.text(((W - w) / 2, y + 14), texto, font=f, fill=(5, 7, 13))
    return im


def story_de_feed(feed):
    """Story 1080x1920 montado a partir da arte do feed: a arte inteira na área segura
    (14% do topo e 20% da base livres), sobre o próprio fundo desfocado e escurecido."""
    from PIL import Image, ImageFilter
    W, H = 1080, 1920
    feed = feed.convert("RGB")
    bg = feed.resize((int(feed.width * H / feed.height), H)).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (5, 7, 13)), 0.6)
    area = int(H * 0.80) - int(H * 0.14) - 20
    f2 = feed.resize((int(feed.width * area / feed.height), area), Image.LANCZOS)
    bg.paste(f2, ((W - f2.width) // 2, int(H * 0.14) + 10))
    return bg


def baixar(ref):
    """Aceita apelido (lucas, robo, hibrido…), URL ou caminho do repositório; devolve lista de arquivos locais."""
    urls = REFS.get(ref, ref)
    urls = urls if isinstance(urls, list) else [urls]
    arquivos = []
    for u in urls:
        if not u.startswith("http"):
            arquivos.append(pathlib.Path(u))
            continue
        destino = CACHE / u.rsplit("/", 1)[-1]
        if not destino.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                destino.write_bytes(r.read())
        arquivos.append(destino)
    return arquivos


def gerar(client, pedido):
    imagens = [f for ref in pedido.get("referencias", []) for f in baixar(ref)][:16]
    tamanhos = [pedido["tamanho"]] if pedido.get("tamanho") else TAMANHOS.get(pedido.get("formato", "feed"))
    ultimo = None
    for modelo in MODELOS:
      for tam in tamanhos:
        try:
            args = dict(model=modelo, prompt=pedido["prompt"], size=tam,
                        quality=pedido.get("qualidade", "high"), n=1)
            if imagens:
                r = client.images.edit(image=[open(f, "rb") for f in imagens], **args)
            else:
                r = client.images.generate(**args)
            return modelo, base64.b64decode(r.data[0].b64_json)
        except Exception as e:
            ultimo = e
            txt = str(e).lower()
            if "size" in txt and tam != tamanhos[-1]:
                print(f"Tamanho {tam} recusado; tentando o próximo.")
                continue
            if "model" in txt and ("not found" in txt or "does not exist" in txt or "invalid" in txt or "access" in txt):
                print(f"Modelo {modelo} indisponível: {str(e)[:200]}")
                break  # próximo modelo
            raise
    raise ultimo


def pedido_do_formulario():
    """Run workflow pelo GitHub: transforma os campos do formulário num pedido."""
    estilo = os.environ.get("IN_ESTILO", "").strip()
    if not estilo:
        return
    import datetime as dt
    nome = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime("%Y-%m-%d-%Hh%M") + f"-{estilo}"
    pedido = {
        "estilo": estilo,
        "textos": os.environ.get("IN_TEXTOS", ""),
        "com_lucas": os.environ.get("IN_LUCAS", "true") == "true",
        "cena": os.environ.get("IN_CENA", ""),
        "formato": os.environ.get("IN_FORMATO", "feed"),
        "status": "pendente",
    }
    pathlib.Path("gerar/pedidos").mkdir(parents=True, exist_ok=True)
    pathlib.Path(f"gerar/pedidos/{nome}.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Falta o segredo OPENAI_API_KEY no repositório.")
    pedido_do_formulario()
    client = OpenAI()
    SAIDA.mkdir(parents=True, exist_ok=True)
    erros = 0
    for pj in sorted(pathlib.Path("gerar/pedidos").glob("*.json")):
        pedido = json.loads(pj.read_text(encoding="utf-8"))
        if pedido.get("status") != "pendente":
            continue
        try:
            if pedido.get("estilo"):
                prompt, refs, formato = montar_estilo(pedido)
                pedido.update(prompt=prompt, referencias=refs)
            modelo, png = gerar(client, pedido)
            (SAIDA / f"{pj.stem}.png").write_bytes(png)
            pedido.update(status="pronto", modelo=modelo, saida=f"gerar/saida/{pj.stem}.png")
            if pedido.get("estilo"):
                arte = ajustar(png, pedido.get("formato", "feed"))
                if pedido.get("rodape", True):
                    arte = rodape(arte, pedido.get("formato", "feed"), pedido.get("destaque", ""))
                arte.save(SAIDA / f"{pj.stem}.jpg", quality=92)
                pedido["arte_final"] = f"gerar/saida/{pj.stem}.jpg"
            pedido.pop("erro", None)
            print(f"{pj.stem}: pronto com {modelo}")
        except Exception as e:
            erros += 1
            pedido.update(status="erro", erro=str(e)[:1500])
            print(f"{pj.stem}: ERRO {e}")
        pj.write_text(json.dumps(pedido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
