"""Pede ao GPT a arte de um post no estilo de uma referência e já coloca o resultado na pasta do post.

Uso (o squad roda isto no passo de Execução):
  python3 scripts/pedir_arte.py --post posts/2026-10-15-16h --estilo revista-lucas-robo \
      --textos "VOCÊ, LOJISTA DE LAJEADO | Aprenda I.A. | com quem atua. | Garanta sua vaga | R$ 198,90" \
      [--lucas] [--cena "robô atendendo no balcão"] [--sem-story]

O que faz:
  1. cria gerar/pedidos/<post>-feed.json (e -story.json), faz commit e push;
  2. o GitHub (workflow "Gerar arte no estilo (GPT)") gera com a chave OPENAI_API_KEY;
  3. espera até 10 min, puxa o resultado e copia para <post>/feed.jpg e <post>/story.jpg.
Sai com código 1 se der erro ou passar do tempo (aí o squad usa o render.py como plano B).
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import time


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", required=True)
    ap.add_argument("--estilo", required=True)
    ap.add_argument("--textos", required=True, help="textos separados por |, título primeiro")
    ap.add_argument("--lucas", action="store_true")
    ap.add_argument("--cena", default="")
    ap.add_argument("--sem-story", action="store_true")
    ap.add_argument("--espera", type=int, default=600)
    a = ap.parse_args()

    estilos = json.loads(pathlib.Path("estilos/estilos.json").read_text(encoding="utf-8"))
    if a.estilo not in estilos and not pathlib.Path(a.estilo).exists():
        sys.exit(f"Estilo '{a.estilo}' não existe. Disponíveis: {', '.join(k for k in estilos if not k.startswith('_'))}")

    post = pathlib.Path(a.post)
    post.mkdir(parents=True, exist_ok=True)
    textos = [t.strip() for t in a.textos.split("|") if t.strip()]
    formatos = ["feed"] + ([] if a.sem_story else ["story"])
    nomes = {}
    for f in formatos:
        nome = f"{post.name}-{f}"
        pedido = {"estilo": a.estilo, "textos": textos, "com_lucas": a.lucas, "cena": a.cena,
                  "formato": f, "post": post.as_posix(), "status": "pendente"}
        pj = pathlib.Path(f"gerar/pedidos/{nome}.json")
        pj.parent.mkdir(parents=True, exist_ok=True)
        pj.write_text(json.dumps(pedido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        nomes[f] = pj
    git("add", "gerar/pedidos")
    git("commit", "-q", "-m", f"Pedido de arte GPT: {post.name} ({a.estilo})")
    for _ in range(5):
        git("pull", "--rebase", "-q", "origin", "main")
        if git("push", "-q", "origin", "HEAD:main").returncode == 0:
            break
        time.sleep(5)
    else:
        sys.exit("Não consegui enviar o pedido ao GitHub.")
    print(f"Pedido enviado ({', '.join(formatos)}). Esperando o GPT…")

    fim = time.time() + a.espera
    while time.time() < fim:
        time.sleep(30)
        git("pull", "--rebase", "-q", "origin", "main")
        estados = {f: json.loads(pj.read_text(encoding="utf-8")) for f, pj in nomes.items()}
        if any(e["status"] == "erro" for e in estados.values()):
            for f, e in estados.items():
                if e["status"] == "erro":
                    print(f"ERRO no {f}: {e.get('erro', '')[:500]}")
            sys.exit(1)
        if all(e["status"] == "pronto" for e in estados.values()):
            for f, e in estados.items():
                shutil.copy(e["arte_final"], post / f"{f}.jpg")
                print(f"{f}: {post / (f + '.jpg')} ({e.get('modelo')})")
            print("Textos pedidos (o Revisor confere letra por letra):")
            for t in textos:
                print(f"  - {t}")
            return
    sys.exit("O GPT não respondeu a tempo. Use o render.py como plano B.")


if __name__ == "__main__":
    main()
