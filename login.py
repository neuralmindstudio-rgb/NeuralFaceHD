import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.storage.jsonstore import JsonStore 
from kivy.core.window import Window

from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog

# Importa a conexão com Firebase do seu arquivo banco_dados.py
from banco_dados import auth 

store = JsonStore('saved_user.json')

class TelaLogin(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        
        # --- AJUSTE 1: Captura o botão 'Voltar' do Android ---
        Window.bind(on_keyboard=self.voltar_ao_login)
        
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        root = AnchorLayout(anchor_x='center', anchor_y='center')

        layout_principal = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15), size_hint=(1, None))
        layout_principal.bind(minimum_height=layout_principal.setter('height'))
        
        layout_principal.add_widget(Label(
            text="NEURAL FACE HD", 
            font_size='32sp', bold=True, color=(0.6, 0.2, 1, 1),
            halign="center", size_hint_y=None, height=dp(50)
        ))
        
        layout_principal.add_widget(Label(
            text="by Neural Mind Studio", 
            font_size='12sp', color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=dp(20), halign="center"
        ))

        # Inputs
        self.input_email = MDTextField(hint_text="E-mail", mode="rectangle")
        
        # --- AJUSTE 2: Campo de Senha com Toque Detectável ---
        self.input_senha = MDTextField(
            hint_text="Senha", 
            mode="rectangle", 
            password=True,
            icon_right="eye-off"
        )
        # Bind de toque direto no widget para capturar o clique no olho
        self.input_senha.bind(on_touch_down=self.checar_clique_no_olho)
        
        layout_principal.add_widget(self.input_email)
        layout_principal.add_widget(self.input_senha)

        # Opções (Lembrar/Esqueci)
        layout_opcoes = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        box_check = BoxLayout(orientation='horizontal', size_hint_x=0.5)
        self.check_lembrar = MDCheckbox(size_hint=(None, None), size=(dp(38), dp(38)), selected_color=(0.6, 0.2, 1, 1))
        box_check.add_widget(self.check_lembrar)
        box_check.add_widget(Label(text="Lembrar", font_size='13sp', color=(0.7, 0.7, 0.7, 1)))
        
        btn_esqueci = MDFlatButton(text="Esqueci a senha?", font_size='12sp', on_release=self.resetar_senha)
        layout_opcoes.add_widget(box_check)
        layout_opcoes.add_widget(btn_esqueci)
        layout_principal.add_widget(layout_opcoes)

        # Botão Entrar
        layout_principal.add_widget(MDFillRoundFlatButton(
            text="ENTRAR NO SISTEMA", size_hint_x=1,
            md_bg_color=(0.4, 0, 0.8, 1), on_release=self.fazer_login
        ))
        
        # Botão Criar Conta
        layout_principal.add_widget(MDRectangleFlatButton(
            text="CRIAR NOVA CONTA", size_hint_x=1,
            text_color=(1, 1, 1, 1), line_color=(0.6, 0.2, 1, 1),
            on_release=lambda x: setattr(self.manager, 'current', 'registro')
        ))

        # Botão Sair
        layout_principal.add_widget(MDRectangleFlatButton(
            text="SAIR", size_hint_x=1,
            text_color=(1, 0, 0, 1), line_color=(0.4, 0.4, 0.4, 1),
            on_release=lambda x: os._exit(0)
        ))

        root.add_widget(layout_principal)
        self.add_widget(root)
        Clock.schedule_once(self.carregar_dados_salvos)

    # --- LÓGICA DE CLIQUE NO OLHO POR COORDENADA ---
    def checar_clique_no_olho(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Se o toque for nos últimos 45 pixels da direita do campo
            if touch.x > (instance.right - dp(45)):
                instance.password = not instance.password
                instance.icon_right = "eye" if not instance.password else "eye-off"
                return True # Interrompe o evento para não focar o texto ao clicar no olho
        return False

    # --- FUNÇÃO BOTÃO VOLTAR ANDROID ---
    def voltar_ao_login(self, window, key, *args):
        if key == 27: # Código do botão 'Voltar'
            if self.manager.current != 'login':
                self.manager.current = 'login'
                return True 
        return False 

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
        except: 
            MDDialog(title="Erro", text="Credenciais inválidas.").open()

    def resetar_senha(self, instance):
        if self.input_email.text:
            try:
                auth.send_password_reset_email(self.input_email.text)
                MDDialog(title="Sucesso", text="Link enviado ao seu e-mail.").open()
            except: MDDialog(title="Erro", text="E-mail inválido.").open()
