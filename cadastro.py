import os
import threading
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore 
from kivy.core.window import Window

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog

# Importa a conexão com Firebase do seu arquivo banco_dados.py
from banco_dados import auth, db 

# Faz a tela subir quando o teclado abre no Android
Window.softinput_mode = "below_target"

store = JsonStore('saved_user.json')

# ==========================================
# 1. TELA DE LOGIN
# ==========================================
class TelaLogin(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        layout_principal = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        layout_principal.add_widget(BoxLayout(size_hint_y=0.2)) # Espaço topo
        
        layout_principal.add_widget(Label(
            text="NEURAL FACE HD", 
            font_size='36sp', bold=True, color=(0.6, 0.2, 1, 1),
            halign="center", size_hint_y=None, height=dp(60)
        ))
        
        layout_principal.add_widget(Label(
            text="by Neural Mind Studio", 
            font_size='12sp', color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=dp(20), halign="center"
        ))

        self.input_email = MDTextField(hint_text="E-mail", mode="rectangle")
        self.input_senha = MDTextField(hint_text="Senha", mode="rectangle", password=True)
        layout_principal.add_widget(self.input_email)
        layout_principal.add_widget(self.input_senha)

        # Lembrar + Esqueci
        layout_opcoes = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        box_check = BoxLayout(orientation='horizontal', size_hint_x=0.5)
        self.check_lembrar = MDCheckbox(size_hint=(None, None), size=(dp(38), dp(38)), selected_color=(0.6, 0.2, 1, 1))
        box_check.add_widget(self.check_lembrar)
        box_check.add_widget(Label(text="Lembrar", font_size='13sp', color=(0.7, 0.7, 0.7, 1)))
        
        btn_esqueci = MDFlatButton(text="Esqueci a senha?", font_size='13sp', on_release=self.resetar_senha)
        layout_opcoes.add_widget(box_check)
        layout_opcoes.add_widget(btn_esqueci)
        layout_principal.add_widget(layout_opcoes)

        layout_principal.add_widget(MDFillRoundFlatButton(
            text="ENTRAR NO SISTEMA", size_hint_x=0.9, pos_hint={'center_x': .5},
            md_bg_color=(0.4, 0, 0.8, 1), on_release=self.fazer_login
        ))
        
        layout_principal.add_widget(MDRectangleFlatButton(
            text="CRIAR NOVA CONTA", size_hint_x=0.9, pos_hint={'center_x': .5},
            text_color=(1, 1, 1, 1), line_color=(0.6, 0.2, 1, 1),
            on_release=lambda x: setattr(self.manager, 'current', 'registro')
        ))

        self.add_widget(layout_principal)
        Clock.schedule_once(self.carregar_dados_salvos)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos; self.rect.size = instance.size

    def carregar_dados_salvos(self, dt):
        try:
            if store.exists('user_creds'):
                dados = store.get('user_creds')
                self.input_email.text = dados['email']; self.input_senha.text = dados['password']
                self.check_lembrar.active = True
        except: pass

    def fazer_login(self, instance):
        try:
            auth.sign_in_with_email_and_password(self.input_email.text, self.input_senha.text)
            if self.check_lembrar.active:
                store.put('user_creds', email=self.input_email.text, password=self.input_senha.text)
            self.manager.current = 'principal'
        except: MDDialog(title="Erro", text="Credenciais inválidas.").open()

    def resetar_senha(self, instance):
        if self.input_email.text:
            try:
                auth.send_password_reset_email(self.input_email.text)
                MDDialog(title="Sucesso", text="Link enviado ao seu e-mail.").open()
            except: MDDialog(title="Erro", text="E-mail inválido.").open()

# ==========================================
# 2. TELA DE CADASTRO
# ==========================================
class TelaCadastro(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect_fundo = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        layout_conteudo = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(20), spacing=dp(20))
        layout_conteudo.bind(minimum_height=layout_conteudo.setter('height'))
        
        self.card = MDCard(
            orientation='vertical', size_hint=(1, None), height=dp(720),
            padding=dp(20), spacing=dp(15), md_bg_color=(0.07, 0.07, 0.08, 1), 
            radius=[dp(15)], elevation=2
        )
        
        self.card.add_widget(Label(text="CRIAR NOVA CONTA", font_size='22sp', bold=True, color=(0.6, 0.2, 1, 1), size_hint_y=None, height=dp(50)))

        self.nome = MDTextField(hint_text="Nome Completo", mode="rectangle", line_color_focus=(0.6, 0.2, 1, 1))
        self.data_nasc = MDTextField(
            hint_text="Nascimento",
            helper_text="Use barras: DD/MM/AAAA (Apenas +18)",
            helper_text_mode="persistent",
            mode="rectangle", 
            line_color_focus=(0.6, 0.2, 1, 1),
            max_text_length=10
        )
        
        self.email = MDTextField(hint_text="Seu Email", mode="rectangle", line_color_focus=(0.6, 0.2, 1, 1))
        self.senha = MDTextField(hint_text="Senha (mín. 6 dígitos)", password=True, mode="rectangle", line_color_focus=(0.6, 0.2, 1, 1), icon_right="eye-off")
        self.senha.bind(on_touch_down=self.click_icone_senha)
        
        self.confirma_senha = MDTextField(hint_text="Confirmar Senha", password=True, mode="rectangle", line_color_focus=(0.6, 0.2, 1, 1), icon_right="eye-off")
        self.confirma_senha.bind(on_touch_down=self.click_icone_senha)
        
        self.card.add_widget(self.nome); self.card.add_widget(self.data_nasc)
        self.card.add_widget(self.email); self.card.add_widget(self.senha)
        self.card.add_widget(self.confirma_senha)
        
        self.btn_registrar = MDFillRoundFlatButton(
            text="FINALIZAR E GANHAR 5 CRÉDITOS", 
            md_bg_color=(0.15, 0.6, 0.15, 1), 
            size_hint_x=1, height=dp(50)
        )
        self.btn_registrar.bind(on_release=self.iniciar_thread_cadastro)
        
        self.btn_voltar = MDRectangleFlatButton(text="VOLTAR", text_color=(1, 1, 1, 1), line_color=(0.5, 0.5, 0.5, 1), size_hint_x=1)
        self.btn_voltar.bind(on_release=self.ir_para_login)
        
        self.card.add_widget(self.btn_registrar); self.card.add_widget(self.btn_voltar)
        layout_conteudo.add_widget(self.card)
        layout_conteudo.add_widget(BoxLayout(size_hint_y=None, height=dp(350))) 
        scroll.add_widget(layout_conteudo)
        self.add_widget(scroll)
        self.dialogo_erro = None

    def mostrar_popup_erro(self, titulo, mensagem):
        self.dialogo_erro = MDDialog(
            title=titulo, text=mensagem,
            buttons=[MDRectangleFlatButton(text="OK", on_release=lambda x: self.dialogo_erro.dismiss())]
        )
        self.dialogo_erro.open()

    def update_rect(self, instance, value):
        self.rect_fundo.pos = instance.pos; self.rect_fundo.size = instance.size

    def click_icone_senha(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.pos[0] > instance.right - dp(50):
            instance.password = not instance.password
            instance.icon_right = "eye" if not instance.password else "eye-off"
            return True

    def iniciar_thread_cadastro(self, instance):
        data_str = self.data_nasc.text.strip()
        try:
            nascimento = datetime.strptime(data_str, "%d/%m/%Y")
            idade = (datetime.now() - nascimento).days // 365
            if idade < 18:
                self.mostrar_popup_erro("Acesso Restrito", "Apenas para maiores de 18 anos.")
                return
        except ValueError:
            self.mostrar_popup_erro("Data Inválida", "Use o formato DD/MM/AAAA")
            return

        self.btn_registrar.text = "A PROCESSAR..."; self.btn_registrar.disabled = True
        threading.Thread(target=self.processar_firebase, daemon=True).start()

    def processar_firebase(self):
        email_u = self.email.text.strip(); senha_u = self.senha.text.strip()
        if len(senha_u) < 6:
            Clock.schedule_once(lambda dt: self.reset_interface("SENHA CURTA"), 0.1); return
        try:
            # 1. Cria o usuário no Firebase Auth
            user = auth.create_user_with_email_and_password(email_u, senha_u)
            u_id = user['localId']
            
            # 2. LOGIN AUTOMÁTICO IMEDIATO para capturar o ID Token (Necessário para o Database)
            login = auth.sign_in_with_email_and_password(email_u, senha_u)
            id_token = login['idToken']
            
            # 3. Salva no banco de dados com os 5 créditos iniciais usando o token de acesso
            db.child("usuarios").child(u_id).set({
                "nome": self.nome.text.strip(), 
                "creditos": 5, 
                "data_nascimento": self.data_nasc.text,
                "email": email_u,
                "aceitou_termos": False,
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
            }, id_token)
            
            # 4. Retorna para o login após o sucesso
            Clock.schedule_once(self.ir_para_login, 0.2)
        except Exception as e:
            print(f"Erro Firebase: {e}")
            msg = "EMAIL JÁ EXISTE" if "EMAIL_EXISTS" in str(e) else "ERRO CONEXÃO"
            Clock.schedule_once(lambda dt: self.reset_interface(msg), 0.1)

    def reset_interface(self, mensagem):
        self.btn_registrar.text = mensagem; self.btn_registrar.disabled = False
        Clock.schedule_once(lambda dt: setattr(self.btn_registrar, 'text', "FINALIZAR E GANHAR 5 CRÉDITOS"), 2)

    def ir_para_login(self, *args):
        self.manager.current = 'login'
