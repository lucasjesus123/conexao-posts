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
Do not invent prices, dates, numbers or logos that are not in the list. No watermark."""
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
                ajustar(png, pedido.get("formato", "feed")).save(SAIDA / f"{pj.stem}.jpg", quality=92)
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
