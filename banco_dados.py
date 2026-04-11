import requests

# 🔑 CONFIG FIREBASE
API_KEY = "AIzaSyD2WCCt8zsbIvT3h1FgjXkGwmTXwPBTBac"
DATABASE_URL = "https://neuralfacehd-default-rtdb.firebaseio.com"

# 🔥 VARIÁVEIS DE SESSÃO (Essenciais para manter o usuário logado)
current_user = None
id_token = None
local_id = None

# =========================
# 🔐 CLASSE PARA SIMULAR O PYREBASE (Para o seu código não quebrar)
# =========================
class FirebaseAuth:
    def sign_in_with_email_and_password(self, email, senha):
        global id_token, local_id, current_user
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": email, "password": senha, "returnSecureToken": True}
        
        res = requests.post(url, json=payload)
        data = res.json()
        
        if "idToken" in data:
            id_token = data["idToken"]
            local_id = data["localId"]
            current_user = data
            return data
        else:
            raise Exception(data.get("error", {}).get("message", "LOGIN_FAILED"))

    def create_user_with_email_and_password(self, email, senha):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {"email": email, "password": senha, "returnSecureToken": True}
        
        res = requests.post(url, json=payload)
        data = res.json()
        
        if "localId" in data:
            return data
        else:
            raise Exception(data.get("error", {}).get("message", "SIGNUP_FAILED"))

    def send_password_reset_email(self, email):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            raise Exception("RESET_FAILED")
        return True

class FirebaseDB:
    def child(self, name):
        self.current_child = name
        return self

    def set(self, dados, token=None):
        # Aqui simulamos a gravação no Realtime Database
        global local_id
        target_id = local_id if local_id else "temp"
        auth_param = f"?auth={token}" if token else ""
        url = f"{DATABASE_URL}/usuarios/{target_id}.json{auth_param}"
        requests.put(url, json=dados)

# Criamos as instâncias para o seu código importar
auth = FirebaseAuth()
db = FirebaseDB()
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
