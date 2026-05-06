import requests
import os

# SSL fix Android
try:
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()
except ImportError:
    pass

# CONFIG FIREBASE
API_KEY = "AIzaSyD2WCCt8zsbIvT3h1FgjXkGwmTXwPBTBac"
DATABASE_URL = "https://neuralfacehd-default-rtdb.firebaseio.com"

# VARIAVEIS DE SESSAO
current_user = None
id_token = None
local_id = None
ultimo_erro = ""


def traduzir_erro_firebase(codigo):
    mapa = {
        "EMAIL_NOT_FOUND": "E-mail nao encontrado.",
        "INVALID_PASSWORD": "Senha incorreta.",
        "USER_DISABLED": "Conta desativada.",
        "INVALID_EMAIL": "E-mail invalido.",
        "EMAIL_EXISTS": "Este e-mail ja esta cadastrado.",
        "WEAK_PASSWORD": "Senha fraca. Use pelo menos 6 caracteres.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Muitas tentativas. Tente novamente mais tarde.",
        "OPERATION_NOT_ALLOWED": "Operacao nao permitida.",
        "MISSING_EMAIL": "Informe o e-mail.",
        "MISSING_PASSWORD": "Informe a senha.",
        "NETWORK_REQUEST_FAILED": "Falha de conexao com a internet.",
        "LOGIN_FAILED": "Falha no login.",
        "SIGNUP_FAILED": "Falha no cadastro.",
        "RESET_FAILED": "Falha ao enviar recuperacao de senha.",
    }
    return mapa.get(codigo, f"Erro no Firebase: {codigo}")


def extrair_codigo_erro(data, fallback):
    return data.get("error", {}).get("message", fallback)


class FirebaseAuth:
    def sign_in_with_email_and_password(self, email, senha):
        global id_token, local_id, current_user, ultimo_erro

        url = (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithPassword?key={API_KEY}"
        )
        payload = {
            "email": email,
            "password": senha,
            "returnSecureToken": True,
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

            erro = extrair_codigo_erro(data, "LOGIN_FAILED")
            ultimo_erro = traduzir_erro_firebase(erro)
            raise Exception(ultimo_erro)

        except Exception as e:
            if not ultimo_erro:
                ultimo_erro = str(e)
            print("ERRO LOGIN:", e)
            raise

    def create_user_with_email_and_password(self, email, senha):
        global id_token, local_id, current_user, ultimo_erro

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
        payload = {
            "email": email,
            "password": senha,
            "returnSecureToken": True,
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()
            print("CADASTRO RESPONSE:", data)

            if "idToken" in data and "localId" in data:
                # Mantem sessao global consistente logo apos cadastro.
                id_token = data["idToken"]
                local_id = data["localId"]
                current_user = data
                ultimo_erro = ""
                return data

            erro = extrair_codigo_erro(data, "SIGNUP_FAILED")
            ultimo_erro = traduzir_erro_firebase(erro)
            raise Exception(ultimo_erro)

        except Exception as e:
            if not ultimo_erro:
                ultimo_erro = str(e)
            print("ERRO CADASTRO:", e)
            raise

    def send_password_reset_email(self, email):
        global ultimo_erro

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email,
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            print("RESET RESPONSE:", res.text)

            if res.status_code == 200:
                ultimo_erro = ""
                return True

            data = res.json()
            erro = extrair_codigo_erro(data, "RESET_FAILED")
            ultimo_erro = traduzir_erro_firebase(erro)
            raise Exception(ultimo_erro)

        except Exception as e:
            if not ultimo_erro:
                ultimo_erro = str(e)
            print("ERRO RESET:", e)
            raise


class FirebaseDB:
    def __init__(self):
        self._path_parts = []

    def child(self, name):
        # Permite encadeamento: db.child("usuarios").child(uid).set(...)
        self._path_parts.append(str(name).strip("/"))
        return self

    def _build_url(self, token=None):
        caminho = "/".join([p for p in self._path_parts if p]) if self._path_parts else ""
        auth_param = f"?auth={token}" if token else ""
        if caminho:
            return f"{DATABASE_URL}/{caminho}.json{auth_param}"
        return f"{DATABASE_URL}.json{auth_param}"

    def set(self, dados, token=None):
        try:
            url = self._build_url(token=token)
            res = requests.put(url, json=dados, timeout=15)
            print("SALVAR USER:", res.text)
            return res
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            raise
        finally:
            self._path_parts = []


# Instancias
auth = FirebaseAuth()
db = FirebaseDB()


def login(email, senha):
    try:
        resultado = auth.sign_in_with_email_and_password(email, senha)
        return True if resultado else False
    except Exception:
        return False


def cadastro(email, senha, nome):
    try:
        user = auth.create_user_with_email_and_password(email, senha)
        u_id = user["localId"]
        token = user["idToken"]

        db.child("usuarios").child(u_id).set(
            {
                "nome": nome,
                "email": email,
                "creditos": 5,
            },
            token,
        )
        return True
    except Exception:
        return False


def recuperar_senha(email):
    try:
        return auth.send_password_reset_email(email)
    except Exception:
        return False


def pegar_creditos():
    global id_token, local_id

    if not local_id or not id_token:
        print("SEM LOGIN PARA BUSCAR CREDITOS")
        return 0

    url = f"{DATABASE_URL}/usuarios/{local_id}/creditos.json?auth={id_token}"

    try:
        res = requests.get(url, timeout=15)
        data = res.json()
        print("CREDITOS:", data)
        return data if isinstance(data, int) else 0
    except Exception as e:
        print("ERRO CREDITOS:", e)
        return 0


def atualizar_creditos(novo_valor):
    global id_token, local_id

    if not local_id or not id_token:
        return

    url = f"{DATABASE_URL}/usuarios/{local_id}.json?auth={id_token}"

    try:
        res = requests.patch(url, json={"creditos": novo_valor}, timeout=15)
        print("UPDATE CREDITOS:", res.text)
    except Exception as e:
        print(f"Erro atualizar creditos: {e}")
