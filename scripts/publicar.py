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

GRAPH = f"https://graph.facebook.com/{os.environ.get('GRAPH_VERSION', 'v26.0')}"
TOKEN = os.environ.get("META_TOKEN", "")
IG = os.environ.get("IG_USER_ID", "")
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


def esperar_container(cid, tentativas=30):
    for _ in range(tentativas):
        st = api("GET", cid, fields="status_code,status").get("status_code")
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
    return api("POST", f"{IG}/media_publish", creation_id=cid)["id"]


def verificar():
    info = api("GET", IG, fields="username,name,followers_count")
    print(f"Conectado: @{info.get('username')} ({info.get('followers_count')} seguidores)")


def descobrir():
    """Lista as páginas e o ID da conta do Instagram ligada a cada uma (para preencher IG_USER_ID)."""
    for pg in api("GET", "me/accounts", fields="name,instagram_business_account{id,username}").get("data", []):
        ig = pg.get("instagram_business_account") or {}
        print(f"Página: {pg.get('name')} -> Instagram @{ig.get('username', '(nenhum ligado)')} IG_USER_ID = {ig.get('id', '-')}")


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
        if post.get("status") != "agendado":
            continue
        quando = dt.datetime.fromisoformat(post["publicar_em"])
        if quando > agora:
            print(f"{pj.parent.name}: agendado para {post['publicar_em']}")
            continue
        pasta = pj.parent.as_posix()
        try:
            post["feed_id"] = publicar(f"{RAW}/{pasta}/feed.jpg", post.get("legenda", ""))
            print(f"{pj.parent.name}: feed publicado ({post['feed_id']})")
            if post.get("story") and (pj.parent / "story.jpg").exists():
                post["story_id"] = publicar(f"{RAW}/{pasta}/story.jpg", story=True)
                print(f"{pj.parent.name}: story publicado ({post['story_id']})")
            post["status"] = "publicado"
            post["publicado_em"] = agora.isoformat(timespec="seconds")
        except Exception as e:  # registra e segue para o próximo
            erros += 1
            post["status"] = "erro" if "feed_id" not in post else "publicado_sem_story"
            post["erro"] = str(e)
            print(f"{pj.parent.name}: ERRO {e}")
        pj.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
