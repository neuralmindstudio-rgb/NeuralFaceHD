import requests
import os

# 🔒 SSL fix Android
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass

# 🔑 CONFIG FIREBASE
API_KEY = "AIzaSyD2WCCt8zsbIvT3h1FgjXkGwmTXwPBTBac"
DATABASE_URL = "https://neuralfacehd-default-rtdb.firebaseio.com"

# 🔥 VARIÁVEIS DE SESSÃO
current_user = None
id_token = None
local_id = None
ultimo_erro = ""


# =========================
# 🔐 CLASSES (COMPATÍVEL COM SEU APP)
# =========================
class FirebaseAuth:
    def sign_in_with_email_and_password(self, email, senha):
        global id_token, local_id, current_user, ultimo_erro

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

        payload = {
            "email": email,
            "password": senha,
            "returnSecureToken": True
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()

            print("LOGIN RESPONSE:", data)

            if "idToken" in data and "localId" in data:
                id_token = data["idToken"]
                local_id = data["localId"]
                current_user = data
                ultimo_erro = ""
                return data
            else:
                erro = data.get("error", {}).get("message", "LOGIN_FAILED")
                ultimo_erro = erro
                raise Exception(erro)

        except Exception as e:
            ultimo_erro = str(e)
            print("ERRO LOGIN:", e)
            raise


    def create_user_with_email_and_password(self, email, senha):
        global ultimo_erro

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"

        payload = {
            "email": email,
            "password": senha,
            "returnSecureToken": True
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()

            print("CADASTRO RESPONSE:", data)

            if "localId" in data:
                ultimo_erro = ""
                return data
            else:
                erro = data.get("error", {}).get("message", "SIGNUP_FAILED")
                ultimo_erro = erro
                raise Exception(erro)

        except Exception as e:
            ultimo_erro = str(e)
            print("ERRO CADASTRO:", e)
            raise


    def send_password_reset_email(self, email):
        global ultimo_erro

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"

        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            print("RESET RESPONSE:", res.text)

            if res.status_code == 200:
                ultimo_erro = ""
                return True
            else:
                data = res.json()
                ultimo_erro = data.get("error", {}).get("message", "RESET_FAILED")
                raise Exception(ultimo_erro)

        except Exception as e:
            ultimo_erro = str(e)
            print("ERRO RESET:", e)
            raise


class FirebaseDB:
    def child(self, name):
        self.current_child = name
        return self

    def set(self, dados, token=None):
        global local_id

        target_id = local_id if local_id else "temp"
        auth_param = f"?auth={token}" if token else ""
        url = f"{DATABASE_URL}/usuarios/{target_id}.json{auth_param}"

        try:
            res = requests.put(url, json=dados, timeout=15)
            print("SALVAR USER:", res.text)
        except Exception as e:
            print(f"Erro ao salvar: {e}")


# Instâncias
auth = FirebaseAuth()
db = FirebaseDB()


# =========================
# 🚀 FUNÇÕES DIRETAS
# =========================

def login(email, senha):
    try:
        resultado = auth.sign_in_with_email_and_password(email, senha)
        return True if resultado else False
    except:
        return False


def cadastro(email, senha, nome):
    try:
        user = auth.create_user_with_email_and_password(email, senha)

        u_id = user['localId']
        token = user['idToken']

        db.child("usuarios").set({
            "nome": nome,
            "email": email,
            "creditos": 5
        }, token)

        return True
    except:
        return False


def recuperar_senha(email):
    try:
        return auth.send_password_reset_email(email)
    except:
        return False


def pegar_creditos():
    global id_token, local_id

    if not local_id or not id_token:
        print("SEM LOGIN PARA BUSCAR CRÉDITOS")
        return 0

    url = f"{DATABASE_URL}/usuarios/{local_id}/creditos.json?auth={id_token}"

    try:
        res = requests.get(url, timeout=15)
        data = res.json()
        print("CRÉDITOS:", data)
        return data if isinstance(data, int) else 0
    except Exception as e:
        print("ERRO CRÉDITOS:", e)
        return 0


def atualizar_creditos(novo_valor):
    global id_token, local_id

    if not local_id or not id_token:
        return

    url = f"{DATABASE_URL}/usuarios/{local_id}.json?auth={id_token}"

    try:
        res = requests.patch(url, json={"creditos": novo_valor}, timeout=15)
        print("UPDATE CRÉDITOS:", res.text)
    except Exception as e:
        print(f"Erro atualizar créditos: {e}")# =========================

def login(email, senha):
    try:
        resultado = auth.sign_in_with_email_and_password(email, senha)
        return True if resultado else False
    except:
        return False

def cadastro(email, senha, nome):
    try:
        user = auth.create_user_with_email_and_password(email, senha)
        u_id = user['localId']
        token = user['idToken']
        db.child("usuarios").set({
            "nome": nome,
            "email": email,
            "creditos": 5
        }, token)
        return True
    except:
        return False

def recuperar_senha(email):
    try:
        return auth.send_password_reset_email(email)
    except:
        return False

def pegar_creditos():
    global id_token, local_id
    if not local_id or not id_token:
        return 0
    url = f"{DATABASE_URL}/usuarios/{local_id}/creditos.json?auth={id_token}"
    try:
        res = requests.get(url)
        return res.json() or 0
    except:
        return 0

def atualizar_creditos(novo_valor):
    global id_token, local_id
    if not local_id or not id_token:
        return
    url = f"{DATABASE_URL}/usuarios/{local_id}.json?auth={id_token}"
    try:
        requests.patch(url, json={"creditos": novo_valor})
    except:
        pass
