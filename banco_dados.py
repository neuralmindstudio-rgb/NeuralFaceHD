import pyrebase
import urllib3

# Desativa avisos de certificado para evitar erros no Android
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = {
    "apiKey": "AIzaSyD2WCCt8zsbIvT3h1FgjXkGwmTXwPBTBac",
    "authDomain": "neuralfacehd.firebaseapp.com",
    "databaseURL": "https://neuralfacehd-default-rtdb.firebaseio.com",
    "projectId": "neuralfacehd",
    "storageBucket": "neuralfacehd.firebasestorage.app",
    "messagingSenderId": "624800248243",
    "appId": "1:624800248243:web:400abbea0dd63482cd5bc6"
}

try:
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    db = firebase.database()
    print("CONEXÃO CONFIGURADA COM SUCESSO!")
except Exception as e:
    print(f"Erro ao inicializar: {e}")

# --- NOVA FUNÇÃO PARA RECUPERAÇÃO DE SENHA ---
def recuperar_senha(email):
    """
    Envia um e-mail de redefinição de senha através do Firebase Auth.
    Retorna True se o e-mail foi enviado ou False se houve erro.
    """
    try:
        auth.send_password_reset_email(email)
        return True
    except Exception as e:
        print(f"Erro ao solicitar recuperação: {e}")
        return False
