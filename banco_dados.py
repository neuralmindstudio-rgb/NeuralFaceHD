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
            id_token = data["idToken"]
            local_id = data["localId"]
            current_user = data
            print("LOGIN OK")
            return True
        else:
            print(f"Erro login: {data}")
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

            # cria usuário no banco
            salvar_usuario(uid, nome, email)

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
def salvar_usuario(uid, nome, email):
    url = f"{DATABASE_URL}/usuarios/{uid}.json"

    dados = {
        "nome": nome,
        "email": email,
        "creditos": 5
    }

    try:
        requests.put(url, json=dados)
    except Exception as e:
        print(f"Erro salvar usuario: {e}")


# =========================
# 💰 PEGAR CRÉDITOS
# =========================
def pegar_creditos():
    if not local_id:
        return 0

    url = f"{DATABASE_URL}/usuarios/{local_id}/creditos.json"

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
