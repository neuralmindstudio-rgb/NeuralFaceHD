import requests

# 🔑 CONFIG FIREBASE
API_KEY = "AIzaSyD2WCCt8zsbIvT3h1FgjXkGwmTXwPBTBac"
DATABASE_URL = "https://neuralfacehd-default-rtdb.firebaseio.com"

# 🔥 VARIÁVEIS DE SESSÃO
current_user = None
id_token = None
local_id = None

# =========================
# 🔐 LOGIN
# =========================
def login(email, senha):
    global current_user, id_token, local_id

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

    payload = {
        "email": email,
        "password": senha,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            # IMPORTANTE: Preencher as globais antes de retornar True
            id_token = data["idToken"]
            local_id = data["localId"]
            current_user = data
            print(f"LOGIN OK para o UID: {local_id}")
            return True
        else:
            # Caso o Firebase retorne erro (senha errada, user não existe)
            msg_erro = data.get("error", {}).get("message", "ERRO_DESCONHECIDO")
            print(f"Erro login Firebase: {msg_erro}")
            return False

    except Exception as e:
        print(f"Erro conexão login: {e}")
        return False

# =========================
# 📝 CADASTRO
# =========================
def cadastro(email, senha, nome):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"

    payload = {
        "email": email,
        "password": senha,
        "returnSecureToken": True
    }

    try:
        res = requests.post(url, json=payload)
        data = res.json()

        if "localId" in data:
            uid = data["localId"]
            token = data["idToken"] # Pegamos o token gerado no cadastro
            
            # Passamos o token para salvar no banco com permissão
            salvar_usuario(uid, nome, email, token)

            print("CADASTRO OK")
            return True
        else:
            print(f"Erro cadastro: {data}")
            return False

    except Exception as e:
        print(f"Erro conexão cadastro: {e}")
        return False

# =========================
# 💾 SALVAR USUÁRIO
# =========================
def salvar_usuario(uid, nome, email, token=None):
    # Adicionamos o parâmetro ?auth={token} para evitar erro de permissão (Permission Denied)
    auth_url = f"?auth={token}" if token else ""
    url = f"{DATABASE_URL}/usuarios/{uid}.json{auth_url}"

    dados = {
        "nome": nome,
        "email": email,
        "creditos": 5
    }

    try:
        res = requests.put(url, json=dados)
        if res.status_code != 200:
            print(f"Erro ao salvar no Realtime: {res.text}")
    except Exception as e:
        print(f"Erro salvar usuario: {e}")

# =========================
# 💰 PEGAR CRÉDITOS
# =========================
def pegar_creditos():
    global id_token, local_id
    if not local_id or not id_token:
        return 0

    # Sempre use o token para ler dados protegidos
    url = f"{DATABASE_URL}/usuarios/{local_id}/creditos.json?auth={id_token}"

    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json() or 0
        return 0
    except:
        return 0

# =========================
# 💸 ATUALIZAR CRÉDITOS
# =========================
def atualizar_creditos(novo_valor):
    global id_token, local_id
    if not local_id or not id_token:
        return

    url = f"{DATABASE_URL}/usuarios/{local_id}.json?auth={id_token}"

    try:
        requests.patch(url, json={"creditos": novo_valor})
    except Exception as e:
        print(f"Erro atualizar créditos: {e}")

# =========================
# 🔑 RECUPERAR SENHA
# =========================
def recuperar_senha(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"

    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }

    try:
        res = requests.post(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro recuperar senha: {e}")
        return False
    try:
        res = requests.get(url)
        return res.json() or 0
    except:
        return 0


# =========================
# 💸 ATUALIZAR CRÉDITOS
# =========================
def atualizar_creditos(novo_valor):
    if not local_id:
        return

    url = f"{DATABASE_URL}/usuarios/{local_id}.json"

    try:
        requests.patch(url, json={"creditos": novo_valor})
    except Exception as e:
        print(f"Erro atualizar créditos: {e}")


# =========================
# 🔑 RECUPERAR SENHA
# =========================
def recuperar_senha(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"

    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }

    try:
        res = requests.post(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro recuperar senha: {e}")
        return False
