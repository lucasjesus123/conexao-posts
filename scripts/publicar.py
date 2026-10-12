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


def esperar_container(cid, tentativas=30, pausa=5):
    for _ in range(tentativas):
        r = _com_espera(lambda: api("GET", cid, fields="status_code,status"))
        st = r.get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {cid} falhou: {st} {r.get('status', '')}")
        time.sleep(pausa)
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


def publicar_video(video_url, legenda=None, story=False, capa_ms=None):
    """Reels no feed (com legenda) ou vídeo no story. Vídeo demora mais para processar na Meta."""
    params = {"video_url": video_url, "media_type": "STORIES" if story else "REELS"}
    if not story:
        params["caption"] = legenda or ""
        params["share_to_feed"] = "true"
        if capa_ms is not None:
            params["thumb_offset"] = str(capa_ms)
    cid = api("POST", f"{IG}/media", **params)["id"]
    esperar_container(cid, tentativas=60, pausa=10)
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


def _proximo_agendado():
    """Horário do próximo post 'agendado' (o mais cedo), ou None."""
    datas = [dt.datetime.fromisoformat(json.loads(pj.read_text(encoding="utf-8"))["publicar_em"])
             for pj in pathlib.Path("posts").glob("*/post.json")
             if json.loads(pj.read_text(encoding="utf-8")).get("status") == "agendado"]
    return min(datas) if datas else None


def _prazo():
    """Até quando este run pode ficar acordado (o job do GitHub tem limite de 6h)."""
    ini = float(os.environ.get("INICIO_RUN") or time.time())
    return dt.datetime.fromtimestamp(ini, dt.timezone.utc) + dt.timedelta(minutes=340)


def esperar_proximo():
    """O agendador do GitHub atrasa (às vezes horas). Se um post vence antes do prazo deste run,
    o run fica esperando acordado até o horário exato e só então segue para publicar.
    Sai com código 0 se há algo para publicar agora, 3 se não há nada dentro do prazo."""
    agora = dt.datetime.now(dt.timezone.utc)
    alvo = _proximo_agendado()
    if alvo is None or alvo > _prazo():
        print("Nenhum post vencendo dentro do prazo deste run.")
        sys.exit(3)
    if alvo <= agora:
        print("Há post no horário ou atrasado; publica já.")
        return
    print(f"Esperando até {alvo.isoformat()} para publicar na hora certa.")
    # Dorme em blocos de 1 min e relê o repositório: se alguém antecipar ou trocar um post, o run percebe.
    import subprocess
    while True:
        agora = dt.datetime.now(dt.timezone.utc)
        if alvo <= agora:
            return
        time.sleep(min(60, (alvo - agora).total_seconds() + 5))
        subprocess.run(["git", "pull", "--rebase", "-q", "origin", "main"], check=False)
        novo = _proximo_agendado()
        if novo is None or novo > _prazo():
            print("O post que eu esperava foi tirado ou adiado; encerrando a espera.")
            sys.exit(3)
        alvo = novo


def _git(*args):
    import subprocess
    return subprocess.run(["git", *args], capture_output=True, text=True).returncode == 0


def reivindicar(pj):
    """Trava o post antes de publicar: marca "publicando" e faz push. Se dois runs tentarem ao
    mesmo tempo, só o push de um passa; o outro desiste. Fora do GitHub Actions, não trava."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return True
    _git("add", "posts")
    _git("commit", "-q", "-m", "Status de publicação [skip ci]")  # salva o que já foi publicado neste run
    _git("pull", "--rebase", "-q", "origin", "main")
    post = json.loads(pj.read_text(encoding="utf-8"))
    if post.get("status") != "agendado":
        return False
    post["status"] = "publicando"
    pj.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _git("add", str(pj))
    _git("commit", "-q", "-m", f"Publicando {pj.parent.name} [skip ci]")
    if _git("push", "-q", "origin", "HEAD:main"):
        return True
    # Push recusado: alguém mexeu no repositório. Tenta de novo uma vez com a versão nova.
    _git("reset", "-q", "HEAD~1")
    _git("checkout", "--", str(pj))
    _git("pull", "--rebase", "-q", "origin", "main")
    post = json.loads(pj.read_text(encoding="utf-8"))
    if post.get("status") != "agendado":
        return False
    post["status"] = "publicando"
    pj.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _git("add", str(pj))
    _git("commit", "-q", "-m", f"Publicando {pj.parent.name} [skip ci]")
    if _git("push", "-q", "origin", "HEAD:main"):
        return True
    _git("reset", "-q", "HEAD~1")
    _git("checkout", "--", str(pj))
    return False


def main():
    if "--esperar" in sys.argv:
        esperar_proximo()
        return
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
        video = post.get("video")  # ex.: "reel.mp4" na pasta do post -> publica como Reels (+ story em vídeo)
        tem_story = bool(post.get("story")) and ((pj.parent / "story.jpg").exists() or bool(video))
        # Story que falhou: tenta de novo nas próximas rodadas (até 3 vezes, nas 6 horas seguintes)
        refazer_story = (status == "publicado_sem_story" and tem_story and post.get("story_tentativas", 0) < 3
                         and agora - quando < dt.timedelta(hours=6))
        if status == "agendado" and quando > agora:
            print(f"{nome}: agendado para {post['publicar_em']}")
            continue
        if status != "agendado" and not refazer_story:
            continue
        if status == "agendado":
            if not reivindicar(pj):
                print(f"{nome}: outro run já está publicando; pulando.")
                continue
            post = json.loads(pj.read_text(encoding="utf-8"))
        try:
            if status == "agendado":
                if video:
                    post["feed_id"] = publicar_video(f"{RAW}/{pasta}/{video}", post.get("legenda", ""), capa_ms=post.get("capa_ms"))
                else:
                    post["feed_id"] = publicar(f"{RAW}/{pasta}/feed.jpg", post.get("legenda", ""))
                post["publicado_em"] = agora.isoformat(timespec="seconds")
                print(f"{nome}: feed publicado ({post['feed_id']})")
            if tem_story:
                if video and not (pj.parent / "story.jpg").exists():
                    post["story_id"] = publicar_video(f"{RAW}/{pasta}/{video}", story=True)
                else:
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
