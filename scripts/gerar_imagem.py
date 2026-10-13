"""Gera imagens com a API da OpenAI (modelos GPT Image), usando fotos de referência.

Cada pedido é um arquivo gerar/pedidos/NOME.json:
  {
    "prompt": "descrição completa da cena (sem texto na imagem)",
    "referencias": ["lucas", "robo", "https://..."],   # apelidos de campanhas/referencias.json ou URLs
    "tamanho": "1024x1536",                               # 1024x1536 (vertical), 1536x1024 ou 1024x1024
    "qualidade": "high",
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
    ultimo = None
    for modelo in MODELOS:
        try:
            args = dict(model=modelo, prompt=pedido["prompt"], size=pedido.get("tamanho", "1024x1536"),
                        quality=pedido.get("qualidade", "high"), n=1)
            if imagens:
                r = client.images.edit(image=[open(f, "rb") for f in imagens], **args)
            else:
                r = client.images.generate(**args)
            return modelo, base64.b64decode(r.data[0].b64_json)
        except Exception as e:  # modelo indisponível na conta: tenta o próximo
            ultimo = e
            txt = str(e).lower()
            if "model" in txt and ("not found" in txt or "does not exist" in txt or "invalid" in txt or "access" in txt):
                print(f"Modelo {modelo} indisponível: {str(e)[:200]}")
                continue
            raise
    raise ultimo


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Falta o segredo OPENAI_API_KEY no repositório.")
    client = OpenAI()
    SAIDA.mkdir(parents=True, exist_ok=True)
    erros = 0
    for pj in sorted(pathlib.Path("gerar/pedidos").glob("*.json")):
        pedido = json.loads(pj.read_text(encoding="utf-8"))
        if pedido.get("status") != "pendente":
            continue
        try:
            modelo, png = gerar(client, pedido)
            (SAIDA / f"{pj.stem}.png").write_bytes(png)
            pedido.update(status="pronto", modelo=modelo, saida=f"gerar/saida/{pj.stem}.png")
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
