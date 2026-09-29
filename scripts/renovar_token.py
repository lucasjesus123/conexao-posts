"""Renova o token do "login com Instagram" (vale 60 dias) e grava o novo no segredo META_TOKEN.

Precisa dos segredos META_TOKEN e GH_PAT (token do GitHub com permissão de escrever segredos deste repositório).
Token de página (graph.facebook.com) não expira e é ignorado aqui.
"""
import base64, json, os, sys, urllib.parse, urllib.request

token = os.environ.get("META_TOKEN", "").strip()
if not token.startswith("IG"):
    print("Token não é de login com Instagram; nada a renovar.")
    sys.exit(0)

url = "https://graph.instagram.com/refresh_access_token?" + urllib.parse.urlencode(
    {"grant_type": "ig_refresh_token", "access_token": token})
with urllib.request.urlopen(url, timeout=60) as r:
    novo = json.loads(r.read())
dias = int(novo.get("expires_in", 0)) // 86400
print(f"Token renovado: vale por mais {dias} dias.")

pat, repo = os.environ.get("GH_PAT", ""), os.environ.get("GITHUB_REPOSITORY", "")
if novo["access_token"] == token:
    print("O token continua o mesmo; nada a gravar.")
    sys.exit(0)
if not pat:
    sys.exit("A Meta devolveu um token novo, mas falta o segredo GH_PAT para gravá-lo. Atualize META_TOKEN à mão.")

from nacl import encoding, public  # pip install pynacl
api = f"https://api.github.com/repos/{repo}/actions/secrets"
h = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
with urllib.request.urlopen(urllib.request.Request(f"{api}/public-key", headers=h)) as r:
    k = json.loads(r.read())
box = public.SealedBox(public.PublicKey(k["key"].encode(), encoding.Base64Encoder()))
enc = base64.b64encode(box.encrypt(novo["access_token"].encode())).decode()
req = urllib.request.Request(f"{api}/META_TOKEN", method="PUT", headers=h,
                             data=json.dumps({"encrypted_value": enc, "key_id": k["key_id"]}).encode())
urllib.request.urlopen(req)
print("Segredo META_TOKEN atualizado com o token novo.")
