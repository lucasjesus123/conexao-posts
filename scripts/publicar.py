"""Publica no Instagram os posts agendados deste repositório, via API oficial da Meta.

Cada post fica em posts/AAAA-MM-DD/ com:
  feed.jpg    arte do feed (1080x1350)
  story.jpg   arte do story (1080x1920), opcional
  post.json   {"publicar_em": "2026-09-28T18:00:00-03:00", "legenda": "...", "story": true, "status": "agendado"}

Publica todo post com status "agendado" cujo horário já chegou e grava o resultado no próprio post.json.
Segredos necessários: META_TOKEN e IG_USER_ID. Só usa a biblioteca padrão do Python.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN = os.environ.get("META_TOKEN", "").strip()
# Token do "login com Instagram" começa com IG e usa graph.instagram.com; token de página usa graph.facebook.com
LOGIN_INSTAGRAM = TOKEN.startswith("IG")
HOST = "graph.instagram.com" if LOGIN_INSTAGRAM else "graph.facebook.com"
GRAPH = f"https://{HOST}/{os.environ.get('GRAPH_VERSION', 'v26.0')}"
IG = "me" if LOGIN_INSTAGRAM else os.environ.get("IG_USER_ID", "").strip()
REPO = os.environ.get("GITHUB_REPOSITORY", "lucasjesus123/conexao-posts")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"


def api(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{GRAPH}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Meta API {e.code}: {e.read().decode()[:500]}") from None


def _nao_encontrado(e):
    """Erro "Media Not Found" da Meta: o container ainda não propagou. Passa sozinho em alguns segundos."""
    return "2207006" in str(e) or "Media Not Found" in str(e)


def _com_espera(chamada, tentativas=4, pausa=10):
    for i in range(tentativas):
        try:
            return chamada()
        except RuntimeError as e:
            if not _nao_encontrado(e) or i == tentativas - 1:
                raise
            time.sleep(pausa)


def esperar_container(cid, tentativas=30):
    for _ in range(tentativas):
        st = _com_espera(lambda: api("GET", cid, fields="status_code,status")).get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {cid} falhou: {st}")
        time.sleep(5)
    raise RuntimeError(f"Container {cid} não ficou pronto a tempo")


def publicar(image_url, legenda=None, story=False):
    params = {"image_url": image_url}
    if story:
        params["media_type"] = "STORIES"
    elif legenda:
        params["caption"] = legenda
    cid = api("POST", f"{IG}/media", **params)["id"]
    esperar_container(cid)
    return _com_espera(lambda: api("POST", f"{IG}/media_publish", creation_id=cid))["id"]


def verificar():
    info = api("GET", IG, fields="username,followers_count")
    print(f"Conectado: @{info.get('username')} ({info.get('followers_count')} seguidores)")


def descobrir():
    if LOGIN_INSTAGRAM:
        info = api("GET", "me", fields="user_id,username")
        print(f"Token de login com Instagram: @{info.get('username')} IG_USER_ID = {info.get('user_id')}")
        return
    _descobrir_pagina()


def _descobrir_pagina():
    """Mostra o ID do Instagram ligado ao token (funciona com token de página ou de usuário)."""
    try:
        me = api("GET", "me", fields="name,instagram_business_account{id,username},connected_instagram_account{id,username}")
        ig = me.get("instagram_business_account") or me.get("connected_instagram_account")
        if ig:
            print(f"Página: {me.get('name')} -> Instagram @{ig.get('username')} IG_USER_ID = {ig.get('id')}")
            return
    except Exception as e:
        print(f"Aviso ao ler o token como página: {e}")
    try:
        for pg in api("GET", "me/accounts", fields="name,instagram_business_account{id,username}").get("data", []):
            ig = pg.get("instagram_business_account") or {}
            print(f"Página: {pg.get('name')} -> Instagram @{ig.get('username', '(nenhum ligado)')} IG_USER_ID = {ig.get('id', '-')}")
    except Exception as e:
        print(f"Aviso ao listar páginas: {e}")


def main():
    if not TOKEN:
        if len(sys.argv) > 1:
            sys.exit("Falta o segredo META_TOKEN no repositório.")
        print("META_TOKEN ainda não configurado; nada a publicar.")
        return
    if "--descobrir" in sys.argv:
        descobrir()
        return
    if not IG:
        if "--verificar" not in sys.argv:
            print("IG_USER_ID ainda não configurado; nada a publicar.")
            return
        sys.exit("Falta o segredo IG_USER_ID. Rode o workflow com 'Testar conexão' marcado para descobrir o ID.")
    if "--verificar" in sys.argv:
        verificar()
        return
    agora = dt.datetime.now(dt.timezone.utc)
    erros = 0
    for pj in sorted(pathlib.Path("posts").glob("*/post.json")):
        post = json.loads(pj.read_text(encoding="utf-8"))
        status = post.get("status")
        quando = dt.datetime.fromisoformat(post["publicar_em"])
        pasta, nome = pj.parent.as_posix(), pj.parent.name
        tem_story = bool(post.get("story")) and (pj.parent / "story.jpg").exists()
        # Story que falhou: tenta de novo nas próximas rodadas (até 3 vezes, nas 6 horas seguintes)
        refazer_story = (status == "publicado_sem_story" and tem_story and post.get("story_tentativas", 0) < 3
                         and agora - quando < dt.timedelta(hours=6))
        if status == "agendado" and quando > agora:
            print(f"{nome}: agendado para {post['publicar_em']}")
            continue
        if status != "agendado" and not refazer_story:
            continue
        try:
            if status == "agendado":
                post["feed_id"] = publicar(f"{RAW}/{pasta}/feed.jpg", post.get("legenda", ""))
                post["publicado_em"] = agora.isoformat(timespec="seconds")
                print(f"{nome}: feed publicado ({post['feed_id']})")
            if tem_story:
                post["story_id"] = publicar(f"{RAW}/{pasta}/story.jpg", story=True)
                print(f"{nome}: story publicado ({post['story_id']})")
            post["status"] = "publicado"
            post.pop("erro", None)
        except Exception as e:  # registra e segue para o próximo
            erros += 1
            if "feed_id" in post:
                post["status"] = "publicado_sem_story"
                post["story_tentativas"] = post.get("story_tentativas", 0) + (1 if refazer_story else 0)
            else:
                post["status"] = "erro"
            post["erro"] = str(e)
            print(f"{nome}: ERRO {e}")
        pj.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
