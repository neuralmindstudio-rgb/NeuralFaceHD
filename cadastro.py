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
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFillRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog

# 🔥 NOVO FIREBASE VIA REST
try:
    from banco_dados import cadastro
    print("Cadastro REST OK")
except Exception as e:
    print(f"Erro banco_dados cadastro: {e}")
    cadastro = None

store = JsonStore('saved_user.json')


class TelaCadastro(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        Window.softinput_mode = "resize"

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect_fundo = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)

        layout_conteudo = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=dp(20),
            spacing=dp(20)
        )
        layout_conteudo.bind(minimum_height=layout_conteudo.setter('height'))

        self.card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(720),
            padding=dp(20),
            spacing=dp(15),
            md_bg_color=(0.07, 0.07, 0.08, 1),
            radius=[dp(15)],
            elevation=2
        )

        self.card.add_widget(Label(
            text="CRIAR NOVA CONTA",
            font_size='22sp',
            bold=True,
            color=(0.6, 0.2, 1, 1),
            size_hint_y=None,
            height=dp(50)
        ))

        self.nome = MDTextField(hint_text="Nome Completo", mode="rectangle")
        self.data_nasc = MDTextField(
            hint_text="Nascimento",
            helper_text="DD/MM/AAAA (Apenas +18)",
            helper_text_mode="persistent",
            mode="rectangle",
            max_text_length=10
        )

        self.email = MDTextField(hint_text="Seu Email", mode="rectangle")
        self.senha = MDTextField(
            hint_text="Senha (mín. 6 dígitos)",
            password=True,
            mode="rectangle",
            icon_right="eye-off"
        )
        self.senha.bind(on_touch_down=self.click_icone_senha)

        self.confirma_senha = MDTextField(
            hint_text="Confirmar Senha",
            password=True,
            mode="rectangle",
            icon_right="eye-off"
        )
        self.confirma_senha.bind(on_touch_down=self.click_icone_senha)

        # 🔥 estabilização de foco no Android
        self.nome.bind(focus=self.on_focus_campo)
        self.data_nasc.bind(focus=self.on_focus_campo)
        self.email.bind(focus=self.on_focus_campo)
        self.senha.bind(focus=self.on_focus_campo)
        self.confirma_senha.bind(focus=self.on_focus_campo)

        self.card.add_widget(self.nome)
        self.card.add_widget(self.data_nasc)
        self.card.add_widget(self.email)
        self.card.add_widget(self.senha)
        self.card.add_widget(self.confirma_senha)

        self.btn_registrar = MDFillRoundFlatButton(
            text="FINALIZAR E GANHAR 5 CRÉDITOS",
            md_bg_color=(0.15, 0.6, 0.15, 1),
            size_hint_x=1,
            height=dp(50)
        )
        self.btn_registrar.bind(on_release=self.iniciar_thread_cadastro)

        self.btn_voltar = MDRectangleFlatButton(
            text="VOLTAR",
            text_color=(1, 1, 1, 1),
            line_color=(0.5, 0.5, 0.5, 1),
            size_hint_x=1
        )
        self.btn_voltar.bind(on_release=self.ir_para_login)

        self.card.add_widget(self.btn_registrar)
        self.card.add_widget(self.btn_voltar)

        layout_conteudo.add_widget(self.card)
        layout_conteudo.add_widget(BoxLayout(size_hint_y=None, height=dp(350)))
        self.scroll.add_widget(layout_conteudo)
        self.add_widget(self.scroll)
        self.dialogo = None

    def on_pre_enter(self, *args):
        Window.softinput_mode = "resize"

    def update_rect(self, instance, value):
        self.rect_fundo.pos = instance.pos
        self.rect_fundo.size = instance.size

    def click_icone_senha(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.pos[0] > instance.right - dp(75):
            instance.password = not instance.password
            instance.icon_right = "eye" if not instance.password else "eye-off"
            return True
        return False

    def on_focus_campo(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self.manter_foco(instance), 0.10)
            Clock.schedule_once(lambda dt: self.manter_foco(instance), 0.30)
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.20)
            Clock.schedule_once(lambda dt: self.rolar_para_campo(instance), 0.45)

    def manter_foco(self, instance):
        try:
            instance.focus = True
        except Exception:
            pass

    def rolar_para_campo(self, campo):
        try:
            y = campo.to_window(campo.x, campo.y)[1]
            altura_janela = Window.height

            # se o campo estiver na metade inferior, sobe a rolagem
            if y < altura_janela * 0.45:
                novo = min(1, self.scroll.scroll_y + 0.18)
                self.scroll.scroll_y = novo
        except Exception as e:
            print(f"Erro ao rolar campo: {e}")

    def ir_para_login(self, *args):
        self.manager.current = 'login'

    def iniciar_thread_cadastro(self, instance):
        if not cadastro:
            MDDialog(
                title="Erro",
                text="Sistema de cadastro indisponível no momento."
            ).open()
            return

        if self.senha.text != self.confirma_senha.text:
            MDDialog(title="Erro", text="As senhas não conferem.").open()
            return

        data_str = self.data_nasc.text.strip()
        try:
            nasc = datetime.strptime(data_str, "%d/%m/%Y")
            idade = (datetime.now() - nasc).days // 365
            if idade < 18:
                MDDialog(title="Acesso Restrito", text="Você precisa ter +18 anos.").open()
                return
        except Exception:
            MDDialog(title="Data Inválida", text="Use o formato DD/MM/AAAA").open()
            return

        self.btn_registrar.text = "PROCESSANDO..."
        self.btn_registrar.disabled = True
        threading.Thread(target=self.processar_firebase, daemon=True).start()

    def processar_firebase(self):
        e_mail = self.email.text.strip()
        pass_w = self.senha.text.strip()
        nome = self.nome.text.strip()

        try:
            sucesso = cadastro(e_mail, pass_w, nome)

            if sucesso:
                Clock.schedule_once(lambda dt: self.sucesso_cadastro(), 0.1)
            else:
                Clock.schedule_once(lambda dt: self.falha_cadastro("E-mail já cadastrado ou erro na conexão."), 0.1)

        except Exception as e:
            print(f"Erro cadastro: {e}")
            Clock.schedule_once(lambda dt: self.falha_cadastro("Erro na conexão."), 0.1)

    def sucesso_cadastro(self):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        self.manager.current = 'login'
        MDDialog(title="Sucesso!", text="Conta criada! Faça seu login.").open()

    def falha_cadastro(self, erro):
        self.btn_registrar.text = "FINALIZAR E GANHAR 5 CRÉDITOS"
        self.btn_registrar.disabled = False
        MDDialog(title="Erro", text=erro).open()
